"""HyperFrames が使えないときの代わり：ブラウザでコマを1枚ずつ撮り、ffmpeg で MP4 にする。

    pip install playwright && python -m playwright install chromium
    python capture.py number/index.html number/examples/sample.json out/number.mp4
    python capture.py list/index.html list/examples/sample.json out/list.mp4 --bgm bgm.mp3
    python capture.py number/index.html - out/preview.mp4 --fps 2      # 既定値のまま・粗いコマで下見

テンプレートは window.__VARS（ここで入れる）を変数として読み、window.__timelines.main（GSAP）を時刻で止めて撮る。
HyperFrames より遅い（15秒・30fps で数分）。音は --bgm の曲を尺に合わせて切り、最後1.5秒でフェードする。
"""
import argparse, json, pathlib, re, shutil, subprocess, tempfile

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("html")
ap.add_argument("vars", help="話の JSON（- なら既定値のまま）")
ap.add_argument("out")
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--bgm")
a = ap.parse_args()

html = pathlib.Path(a.html).resolve()
root = re.search(r'data-composition-id="main"[^>]*', html.read_text(encoding="utf-8")).group(0)
W, H, DUR = (float(re.search(r'data-%s="([\d.]+)"' % k, root).group(1)) for k in ("width", "height", "duration"))
V = {} if a.vars == "-" else json.loads(pathlib.Path(a.vars).read_text(encoding="utf-8"))
tmp = pathlib.Path(tempfile.mkdtemp(prefix="cap_"))
out = pathlib.Path(a.out).resolve()
out.parent.mkdir(parents=True, exist_ok=True)
out.unlink(missing_ok=True)          # 成否は出力ファイルで見る（前回の mp4 を残さない）

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": int(W), "height": int(H)})
    pg.add_init_script("window.__VARS = %s;" % json.dumps(V, ensure_ascii=False))
    pg.goto(html.as_uri(), wait_until="networkidle")
    pg.evaluate("document.fonts.ready.then(() => true)")
    if not pg.evaluate("!!(window.__timelines && window.__timelines.main)"):
        raise SystemExit("window.__timelines.main が無い（GSAP の読み込み失敗か、テンプレートのスクリプトの誤り）")
    for i in range(int(round(DUR * a.fps))):
        # false＝コールバックも走らせる。戻り値（タイムライン本体）を返すと直列化で止まるので返さない
        pg.evaluate("t => { window.__timelines.main.seek(t, false); }", i / a.fps)
        pg.screenshot(path=str(tmp / ("%05d.png" % i)))
    b.close()

cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(a.fps), "-i", str(tmp / "%05d.png")]
if a.bgm:
    cmd += ["-i", a.bgm, "-map", "0:v", "-map", "1:a", "-af", "apad,afade=t=out:st=%.2f:d=1.5" % (DUR - 1.5),
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
cmd += ["-t", "%.3f" % DUR, "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", str(out)]
subprocess.run(cmd, check=True)
shutil.rmtree(tmp, ignore_errors=True)
print("OK", out)
