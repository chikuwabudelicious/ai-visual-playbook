# -*- coding: utf-8 -*-
r"""原稿（JSON）から、意匠 A〜F の編集できる PPTX を作る。python-pptx だけで動く（PowerPoint は要らない）。

    pip install python-pptx pillow
    python deck.py ../examples/example_ja.json -o out/deck.pptx            # 意匠は JSON の "design"（無ければ B）
    python deck.py ../examples/example_ja.json --design D -o out/deck_D.pptx  # 同じ原稿を別の意匠で

判型：横A4（297×210mm）。書体は原稿の "font"（既定 BIZ UDPGothic＝無償の UD ゴシック）、タイ語などは "font_cs" も。
本文の面の下端に風景の帯を敷ける（bands/<帯>_{town,fields,river}.webp。無ければ敷かない。作り方は make_band.py）。
面の種類（"type"）：cover 表紙／section 章扉／bullets 箇条／cards カード2〜4枚／stats 大きな数字2〜4つ／flow 横一列の流れ
（段階・ロードマップ）／compare 左右くらべ／image 図1枚＋説明／video 動画の面（PowerPoint で再生できる）／full 全面画像／closing 結び。
項目は examples/example_ja.json を見る。各面に "notes"（話す原稿）と "chapter"（"03 TECHNOLOGY" など）を付けられる。
保存後に2点を自己検査する：effectLst の二重付与（PowerPoint で開けなくなる）／本文が帯にかかっていないか。
"""
import argparse, io, json, os, re, subprocess, sys, tempfile, urllib.request

from PIL import Image, ImageFilter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "BIZ UDPGothic"                  # 原稿の "font" で替えられる（main で入れる）
FONT_CS = None                          # complex script（タイ語など）の書体。None なら FONT と同じ
SW, SH = Inches(11.69), Inches(8.27)
BAND_H = SW // 12                       # 帯の高さ＝幅/12（1920px の面なら160px）
BODY_BOTTOM = SH - BAND_H - Inches(0.05)  # 本文はここより上で終える
FOOT_Y = SH - Inches(0.73) - Inches(0.26)  # フッター・面番号は下端から約0.73in より上まで下げてよい
MX = Inches(0.75)                       # 左右の余白
SCENES = ("town", "fields", "river")    # 帯の3場面を面ごとに順に回す


def rgb(h):
    return RGBColor.from_string(h.lstrip("#"))


# ---------- 文字 ----------
def est_w(text, pt):
    """1行の幅（インチ）の見積り。全角＝1em、半角＝0.55em。"""
    return sum((1.0 if ord(c) > 0x2E7F else 0.55) for c in text) * pt / 72


def fit_pt(text, w_in, h_in, max_pt, min_pt=10, lh=1.35):
    """枠に収まる最大の大きさ（pt）。"/" は改行。"""
    for pt in range(int(max_pt), int(min_pt) - 1, -1):
        lines = sum(max(1, -(-est_w(s, pt) // (w_in * 0.96))) for s in text.split("/"))
        if lines * pt * lh / 72 <= h_in:
            return pt
    return min_pt


def text(slide, x, y, w, h, s, pt, color, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, fit=True, lh=1.25):
    s = str(s or "")
    if fit:
        pt = fit_pt(s, w / 914400, h / 914400, pt, min(pt, 11), lh + 0.1)
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    for i, line in enumerate(s.split("/")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = lh
        r = p.add_run()
        r.text = line
        f = r.font
        f.size, f.bold, f.color.rgb = Pt(pt), bold, rgb(color)
        f.name = FONT
        rpr = r._r.get_or_add_rPr()
        for tag in ("a:ea", "a:cs"):         # 和文・その他の書体も指定する（latin だけだと和文が既定の書体に、タイ語が化ける）
            el = rpr.find(qn(tag))
            if el is None:
                el = rpr.makeelement(qn(tag), {})
                rpr.append(el)
            el.set("typeface", (FONT_CS or FONT) if tag == "a:cs" else FONT)
    return tb


def box(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    s.shadow.inherit = False                 # 影を付けない（effectLst は足さない＝二重付与の罠を避ける）
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(1)
    else:
        s.line.fill.background()
    return s


def picture(slide, src, x, y, w=None, h=None):
    if re.match(r"https?://", str(src)):
        data = urllib.request.urlopen(src, timeout=30).read()
        src = io.BytesIO(data)
    return slide.shapes.add_picture(src, x, y, w, h)


def fit_picture(slide, src, x, y, w, h):
    """縦横比を保って枠の中央に置く。"""
    if re.match(r"https?://", str(src)):
        src = io.BytesIO(urllib.request.urlopen(src, timeout=30).read())
    im = Image.open(src)
    iw, ih = im.size
    s = min(w / iw, h / ih)
    pw, ph = int(iw * s), int(ih * s)
    if hasattr(src, "seek"):
        src.seek(0)
    return slide.shapes.add_picture(src, x + (w - pw) // 2, y + (h - ph) // 2, pw, ph)


# ---------- 帯 ----------
_band_cache = {}


def band_png(name):
    """bands/<name>.webp（2400×200・上はぼかしで透過）を PNG にして返す。python-pptx は webp を読めない。"""
    if name not in _band_cache:
        p = os.path.join(HERE, "bands", name + ".webp")
        if not os.path.exists(p):
            return None
        buf = io.BytesIO()
        Image.open(p).convert("RGBA").save(buf, "PNG", optimize=True)
        _band_cache[name] = buf.getvalue()
    return io.BytesIO(_band_cache[name])


def add_band(slide, prefix, i):
    png = next((p for p in (band_png("%s_%s" % (prefix, SCENES[(i + k) % 3])) for k in range(3)) if p), None)  # 無い場面は有る場面で代用
    if png:
        slide.shapes.add_picture(png, 0, SH - BAND_H, SW, BAND_H)


# ---------- 意匠ごとの骨格 ----------
class Deck:
    def __init__(self, spec, design):
        all_d = json.load(open(os.path.join(HERE, "designs.json"), encoding="utf-8"))
        if design not in all_d:
            sys.exit("意匠は %s のどれか（designs.json に1件足せば増やせる）" % " ".join(k for k in all_d if not k.startswith("_")))
        self.d, self.key, self.spec = all_d[design], design, spec
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = SW, SH
        self.body_i = 0
        self.n = 0
        cp = self.prs.core_properties
        cp.author = cp.last_modified_by = spec.get("author", "")   # python-pptx の既定の作成者を残さない
        cp.title = spec.get("title", "")

    # 面の土台：地・骨格・帯・フッター。返り値は本文を置ける (x, y, w, h) と文字色
    def base(self, kind, chapter=None):
        d = self.d
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self.n += 1
        dark = kind in ("cover", "section", "closing") or (d["skeleton"] == "alt" and kind not in ("full",) and self.body_i % 2 == 1)
        bg = d["dark"] if dark else d["bg"]
        box(s, 0, 0, SW, SH, bg)
        ink = d["on_dark"] if dark else d["ink"]
        mute = d.get("on_dark_mute", d["on_dark"]) if dark else d["mute"]
        x, y, w = MX, Inches(0.55), SW - 2 * MX
        sk = d["skeleton"]
        if kind in ("cover", "section", "closing", "full"):
            if sk == "gauge" and kind == "section":
                self.gauge(s, chapter, dark=True)
            return s, (x, y, w, SH - y - Inches(0.6)), ink, mute, dark
        body = True
        if sk == "rail":                            # B：左に深緑のレールと章番号
            rw = Inches(0.80)
            box(s, 0, 0, rw, SH, d["dark"])
            if chapter:
                text(s, 0, Inches(0.5), rw, Inches(0.6), chapter.split()[0], 22, d["on_dark"], True, PP_ALIGN.CENTER, fit=False)
            x, w = rw + Inches(0.55), SW - rw - Inches(0.55) - MX
        elif sk == "stripe":                        # D：左端の細い濃緑の帯＋金の短い罫
            box(s, 0, 0, Inches(0.14), SH, d["dark"])
        elif sk == "topbar":                        # E：上端のサフランの太罫
            box(s, 0, 0, SW, Inches(0.12), d["accent2"])
            y = Inches(0.6)
        elif sk == "gauge":                         # F：上端に Phase の進行ゲージ
            self.gauge(s, chapter, dark=dark)
            y = Inches(0.8)
        elif sk == "readbar":                       # G：上端の読了バー
            box(s, 0, 0, SW, Inches(0.07), d["line"])
            box(s, 0, 0, int(SW * min(1, self.n / max(1, len(self.spec["slides"])))), Inches(0.07), d["accent"])
        if chapter and sk != "rail":
            text(s, x, y, w, Inches(0.3), chapter, 11, d["accent2"] if sk in ("stripe", "topbar", "gauge") else (mute if dark else d["accent"]), True, fit=False)
        if self.spec.get("band", True):
            add_band(s, d.get("band_dark") if dark and d.get("band_dark") else d["band"], self.body_i)
        foot = self.spec.get("footer", "")
        text(s, x, FOOT_Y, w * 0.8, Inches(0.25), foot, 9, mute, fit=False)
        text(s, x + w - Inches(1), FOOT_Y, Inches(1), Inches(0.25), str(self.n), 9, mute, align=PP_ALIGN.RIGHT, fit=False)
        self.body_i += 1
        return s, (x, y + Inches(0.35), w, FOOT_Y - y - Inches(0.45)), ink, mute, dark

    def gauge(self, s, chapter, dark):
        d = self.d
        ph = int(self.spec.get("phase", 0) or 0)
        m = re.search(r"phase\s*(\d)", chapter or "", re.I)
        ph = int(m.group(1)) if m else ph
        gx, gw = MX, SW - 2 * MX
        seg = gw / 5
        for i in range(5):
            on = i < ph
            box(s, int(gx + seg * i + Inches(0.03)), Inches(0.22), int(seg - Inches(0.06)), Inches(0.08),
                d["accent2"] if on else (d["line"] if not dark else "#2A3B38"))
            text(s, int(gx + seg * i), Inches(0.32), int(seg), Inches(0.22), "Phase %d" % (i + 1), 8,
                 d["accent2"] if on else d["mute"], align=PP_ALIGN.CENTER, fit=False)

    def title(self, s, area, t, ink, sub=None):
        x, y, w, h = area
        text(s, x, y, w, Inches(0.8), t, 30, ink, True)
        yy = y + Inches(0.85)
        if sub:
            text(s, x, yy, w, Inches(0.5), sub, 15, self.d["mute"] if ink == self.d["ink"] else self.d["on_dark"])
            yy += Inches(0.55)
        box(s, x, yy, Inches(0.9), Pt(3), self.d["accent2"])
        yy += Inches(0.25)
        return x, yy, w, BODY_BOTTOM - yy

    def notes(self, s, sl):
        if sl.get("notes"):
            s.notes_slide.notes_text_frame.text = sl["notes"].replace("/", "\n")

    # ---------- 面の種類 ----------
    def cover(self, sl):
        d = self.d
        s, (x, y, w, h), ink, mute, _ = self.base("cover")
        if sl.get("image"):
            fit_picture(s, sl["image"], int(SW * 0.55), 0, int(SW * 0.45), SH)
            w = int(SW * 0.55) - x - Inches(0.3)
        box(s, x, Inches(2.3), Inches(1.2), Pt(4), d["accent2"])
        text(s, x, Inches(2.55), w, Inches(1.9), sl.get("title", self.spec.get("title", "")), 40, ink, True)
        text(s, x, Inches(4.55), w, Inches(1.0), sl.get("subtitle", ""), 18, mute)
        text(s, x, SH - Inches(1.5), w, Inches(0.9), "/".join(v for v in (sl.get("org"), sl.get("date")) if v), 14, ink)
        return s

    def section(self, sl):
        d = self.d
        s, (x, y, w, h), ink, mute, _ = self.base("section", sl.get("chapter"))
        no = (sl.get("chapter") or "").split()[0] if sl.get("chapter") else ""
        text(s, x, Inches(2.2), w, Inches(1.6), no, 72, d["accent2"], True, fit=False)
        text(s, x, Inches(3.8), w, Inches(1.2), sl.get("title", ""), 36, ink, True)
        text(s, x, Inches(5.0), w, Inches(1.0), sl.get("subtitle", ""), 16, mute)
        return s

    def bullets(self, sl):
        s, area, ink, mute, dark = self.base("body", sl.get("chapter"))
        x, y, w, h = self.title(s, area, sl.get("title", ""), ink, sl.get("lead"))
        items = sl.get("items", [])
        rh = min(Inches(0.9), h / max(1, len(items)))
        for i, it in enumerate(items):
            yy = y + rh * i
            box(s, x, int(yy + Inches(0.12)), Inches(0.12), Inches(0.12), self.d["accent"] if not dark else self.d["accent2"])
            text(s, x + Inches(0.3), int(yy), w - Inches(0.3), int(rh - Inches(0.08)), it, 18, ink)
        return s

    def _cell(self, s, x, y, w, h, head, body, ink, mute, dark, i):
        d = self.d
        sk = d["skeleton"]
        col = d.get("cycle", [d["accent"]])[i % len(d.get("cycle", [d["accent"]]))]
        if sk == "cards":
            box(s, x, y, w, h, d["card"], d["line"], MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.04
        elif dark:
            box(s, x, y, w, h, None, "#3A4A3F")
        else:
            box(s, x, y, w, h, d["card"], d["line"])
        box(s, x, y, w, Inches(0.06), col if sk == "topbar" else d["accent"])
        pad = Inches(0.22)
        text(s, x + pad, y + pad, w - 2 * pad, Inches(0.8), head, 18, ink, True)
        text(s, x + pad, y + pad + Inches(0.85), w - 2 * pad, h - 2 * pad - Inches(0.85), body, 14, mute)

    def cards(self, sl):
        s, area, ink, mute, dark = self.base("body", sl.get("chapter"))
        x, y, w, h = self.title(s, area, sl.get("title", ""), ink, sl.get("lead"))
        cs = sl.get("cards", [])[:4]
        g = Inches(0.25)
        cw = (w - g * (len(cs) - 1)) / max(1, len(cs))
        for i, c in enumerate(cs):
            self._cell(s, int(x + (cw + g) * i), y, int(cw), int(min(h, Inches(3.0))), c.get("h", ""), c.get("t", ""),
                       ink, mute, dark, i)
        return s

    def stats(self, sl):
        d = self.d
        s, area, ink, mute, dark = self.base("body", sl.get("chapter"))
        x, y, w, h = self.title(s, area, sl.get("title", ""), ink, sl.get("lead"))
        st = sl.get("stats", [])[:4]
        g = Inches(0.3)
        cw = (w - g * (len(st) - 1)) / max(1, len(st))
        for i, v in enumerate(st):
            xx = int(x + (cw + g) * i)
            col = d.get("cycle", [d["accent"]])[i % len(d.get("cycle", [d["accent"]]))] if not dark else d["accent2"]
            bh = int(min(h * 0.8, Inches(2.9)))
            box(s, xx, y, Pt(3), bh, col)
            text(s, xx + Inches(0.2), y, int(cw - Inches(0.2)), Inches(1.3), v.get("v", "◯◯"), 54, col, True)
            text(s, xx + Inches(0.2), y + Inches(1.3), int(cw - Inches(0.2)), Inches(0.5), v.get("unit", ""), 16, ink, True)
            text(s, xx + Inches(0.2), y + Inches(1.85), int(cw - Inches(0.2)), int(bh - Inches(1.9)), v.get("label", ""), 14, mute)
        if sl.get("note"):
            text(s, x, BODY_BOTTOM - Inches(0.3), w, Inches(0.3), sl["note"], 10, mute)
        return s

    def flow(self, sl):
        d = self.d
        s, area, ink, mute, dark = self.base("body", sl.get("chapter"))
        x, y, w, h = self.title(s, area, sl.get("title", ""), ink, sl.get("lead"))
        steps = sl.get("steps", [])[:6]
        g = Inches(0.35)
        cw = (w - g * (len(steps) - 1)) / max(1, len(steps))
        for i, st in enumerate(steps):
            xx = int(x + (cw + g) * i)
            dot = box(s, xx, y, Inches(0.55), Inches(0.55), d["accent"] if not dark else d["accent2"], shape=MSO_SHAPE.OVAL)
            text(s, xx, y, Inches(0.55), Inches(0.55), str(i + 1), 16, d["on_dark"] if not dark else d["dark"], True,
                 PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, fit=False)
            if i < len(steps) - 1:
                box(s, xx + Inches(0.65), int(y + Inches(0.26)), int(cw + g - Inches(0.75)), Pt(2), d["line"] if not dark else "#3A4A3F")
            text(s, xx, y + Inches(0.75), int(cw), Inches(0.8), st.get("h", ""), 17, ink, True)
            text(s, xx, y + Inches(1.6), int(cw), int(h - Inches(1.6)), st.get("t", ""), 13, mute)
        return s

    def compare(self, sl):
        d = self.d
        s, area, ink, mute, dark = self.base("body", sl.get("chapter"))
        x, y, w, h = self.title(s, area, sl.get("title", ""), ink, sl.get("lead"))
        g = Inches(0.4)
        cw = (w - g) / 2
        for i, side in enumerate((sl.get("left", {}), sl.get("right", {}))):
            xx = int(x + (cw + g) * i)
            head_bg = d["mute"] if i == 0 else d["accent"]
            box(s, xx, y, int(cw), Inches(0.6), head_bg)
            text(s, xx + Inches(0.2), y, int(cw - Inches(0.4)), Inches(0.6), side.get("h", ""), 17, "#FFFFFF", True,
                 anchor=MSO_ANCHOR.MIDDLE)
            items = side.get("items", [])
            rh = min(Inches(0.75), (h - Inches(0.75)) / max(1, len(items)))
            for j, it in enumerate(items):
                yy = int(y + Inches(0.75) + rh * j)
                box(s, xx, int(yy + rh - Pt(1)), int(cw), Pt(0.75), d["line"])
                text(s, xx + Inches(0.15), yy, int(cw - Inches(0.3)), int(rh - Inches(0.08)), it, 14, ink if i else mute,
                     anchor=MSO_ANCHOR.MIDDLE)
        return s

    def image(self, sl):
        s, area, ink, mute, dark = self.base("body", sl.get("chapter"))
        x, y, w, h = self.title(s, area, sl.get("title", ""), ink, sl.get("lead"))
        side = sl.get("text")
        iw = int(w * 0.62) if side else w
        if sl.get("image"):
            fit_picture(s, sl["image"], x, y, iw, int(h))
        else:                                           # 図が未定なら枠だけ（あとで差し替える）
            box(s, x, y, iw, int(h), self.d["tint"], self.d["line"])
            text(s, x, y, iw, int(h), "図（差し替え）", 16, mute, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, fit=False)
        if side:
            text(s, x + iw + Inches(0.35), y, w - iw - Inches(0.35), int(h), side, 15, ink)
        if sl.get("caption"):
            text(s, x, BODY_BOTTOM - Inches(0.28), w, Inches(0.28), sl["caption"], 10, mute)
        return s

    def video(self, sl):
        s, area, ink, mute, dark = self.base("body", sl.get("chapter"))
        x, y, w, h = self.title(s, area, sl.get("title", ""), ink, sl.get("lead"))
        mp4 = sl["video"]
        vh = int(h)
        vw = int(vh * 16 / 9) if vh * 16 / 9 <= w else int(w)
        vh = int(vw * 9 / 16)
        poster = None
        tmp = os.path.join(tempfile.gettempdir(), "tk_poster.png")
        if _has("ffmpeg") and subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(sl.get("poster_at", 1)), "-i", mp4,
                                              "-frames:v", "1", tmp], capture_output=True).returncode == 0:
            poster = tmp                                # 表紙のコマ（無ければ python-pptx の既定の絵）
        s.shapes.add_movie(mp4, int(x + (w - vw) / 2), y, vw, vh, poster_frame_image=poster, mime_type="video/mp4")
        return s

    def full(self, sl):
        s, *_ = self.base("full")
        fit_picture(s, sl["image"], 0, 0, SW, SH)
        return s

    def closing(self, sl):
        d = self.d
        s, (x, y, w, h), ink, mute, _ = self.base("closing")
        text(s, x, Inches(2.4), w, Inches(1.6), sl.get("title", "ありがとうございました"), 36, ink, True)
        box(s, x, Inches(4.1), Inches(1.2), Pt(4), d["accent2"])
        text(s, x, Inches(4.4), w, Inches(1.8), sl.get("contact", ""), 15, mute)
        return s

    def build(self):
        for sl in self.spec["slides"]:
            t = sl.get("type", "bullets")
            fn = getattr(self, t, None)
            if not fn or t.startswith("_") or t in ("base", "title", "notes", "build", "gauge"):
                sys.exit("面の種類 %r は無い（cover section bullets cards stats flow compare image video full closing）" % t)
            self.notes(fn(sl), sl)
        return self.prs


def _has(cmd):
    from shutil import which
    return which(cmd) is not None


def check(path):
    """effectLst の二重付与（PowerPoint で開けなくなる）と、帯にかかる本文を検査する。"""
    import zipfile
    bad = []
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.startswith("ppt/slides/slide") and n.endswith(".xml"):
                x = z.read(n).decode("utf-8")
                for sp in re.findall(r"<p:spPr>.*?</p:spPr>", x, re.S):
                    if sp.count("<a:effectLst") > 1:
                        bad.append("%s：effectLst が二重" % n)
    prs = Presentation(path)
    for i, s in enumerate(prs.slides, 1):
        if not any(sh.shape_type == 13 and sh.top >= SH - BAND_H - 2 and sh.width == SW for sh in s.shapes):
            continue                                    # 帯の無い面（表紙・章扉・結び）は見ない
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip() and sh.top + sh.height > BODY_BOTTOM + Inches(0.02) \
                    and sh.top < FOOT_Y - Inches(0.05):
                bad.append("%d面：本文が帯にかかる（%s）" % (i, sh.text_frame.text[:20]))
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("content", help="原稿の JSON")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--design", help="A〜F（原稿の design より優先）")
    a = ap.parse_args()
    spec = json.load(open(a.content, encoding="utf-8"))
    global FONT, FONT_CS
    FONT, FONT_CS = spec.get("font", FONT), spec.get("font_cs")
    base = os.path.dirname(os.path.abspath(a.content))
    for sl in spec["slides"]:                     # 原稿の中の相対パスは原稿の場所から
        for k in ("image", "video"):
            if sl.get(k) and not re.match(r"https?://", sl[k]) and not os.path.isabs(sl[k]):
                sl[k] = os.path.join(base, sl[k])
    design = (a.design or spec.get("design") or "B").upper()
    prs = Deck(spec, design).build()
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    prs.save(a.out)
    bad = check(a.out)
    print(("NG\n  " + "\n  ".join(bad)) if bad else "OK", a.out, "（意匠 %s・%d面）" % (design, len(prs.slides)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
