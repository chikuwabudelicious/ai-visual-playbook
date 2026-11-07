# 画像を「レシピ」に書き起こして、別の環境で作り直す

画像ファイルは重く、共有先・クラウド・別PCへ持ち歩けないことが多い。
そこで、**作り方を文字で持ち歩き、行った先で生成し直す**。レシピは JSON の文字だけなので、Git やチャットにそのまま載る。

## 1. 書き起こす（画像を AI に見せて、次の指示を渡す）

Claude・Codex・Gemini など、画像を読める AI ならどれでもよい。複数枚なら1枚ずつ。

```
You are cataloguing an existing infographic / illustration so that it can be RE-GENERATED later with
an image model in an environment where the original file is missing.
Look at the image and return ONE JSON object with these keys:
- "kind": one of cycle, process_flow, mass_balance, hub_spoke, compare, hero_stat, timeline, columns,
  cutaway, map, table_chart, illustration, photo, icon_set, landscape_band, diagram_other
- "style_notes": 1-2 sentences in English on rendering, palette (with hex if obvious), line weight, background
- "aspect": like "16:9", "3:2", "1:1", "2:3", "12:1"
- "title": the main heading text exactly as printed ("" if none)
- "texts": every other visible text label EXACTLY as printed, in reading order, original language and
  script (keep line breaks as " / ")
- "numbers": every number/unit as printed
- "layout": English, 3-6 sentences: composition, number and placement of elements, arrows, icons,
  what each element depicts
- "prompt": a complete English prompt that would reproduce this image: start with the style/rendering,
  then the layout, then quote every text exactly in double quotes with its position.
  End with "No watermark, no logo unless shown."
- "caution": anything that should not be reproduced as-is (logos, real company names, faces of
  identifiable people, unreadable text) or ""
Return JSON only.
```

映像の1カットなら、始め・中ほど・終わりの3コマを見せて次を渡す：

```
You are cataloguing an existing short video clip (frames shown in order: start, middle, end) so that a
similar clip can be RE-GENERATED later: first a still image, then motion with an image-to-video model.
Return ONE JSON object:
- "source_type": "generated" | "live" (real camera footage) | "3d" | "screen"
- "subject": English, one sentence
- "first_frame_prompt": complete English prompt for the FIRST frame: shot type, lens feel, lighting,
  palette, every visible object and its position. No text, no logos, no captions.
- "motion_prompt": English prompt for the video model: camera move (dolly/pan/static/orbit), subject
  motion, pace, mood, what must NOT happen (morphing, text appearing)
- "aspect": "16:9" | "9:16" | "1:1"
- "visible_text": any text/logo visible in the frames (to avoid) or ""
- "caution": e.g. identifiable people, real place that should not be presented as a field record, or ""
Return JSON only.
```

## 2. レシピの形

```json
{
  "collection": "town-guide-2026",
  "recipes": {
    "town-guide-2026/recycle_cycle": {
      "type": "image",
      "described_from": "recycle_cycle_ja.png",
      "langs": ["ja", "en"],
      "kind": "cycle",
      "style_notes": "Flat editorial infographic, off-white #F4F6F1, forest green and amber, thin two-tone line icons.",
      "aspect": "1:1",
      "title": "",
      "texts": ["町の / 資源循環", "家庭の生ごみ", "地域で処理"],
      "numbers": [],
      "layout": "Five nodes around a dark green center circle, clockwise amber arrows ...",
      "prompt": "Modern flat infographic ... 'Node 1' ...",
      "caution": ""
    }
  }
}
```

- 同じ図の言語違いは1件にまとめ、代表（いちばん文字の少ない言語）だけを見せて書き起こす。
- 実写（`source_type: live`）は作り直せない。似た情景の代わりを作るときは、記録映像や実績として出さない。

## 3. 作り直す

1. `style_notes` を先頭に、`prompt` を続け、`text-and-languages.md` の言語別の1文と、SKILL.md の決まり文句を足す。
2. 縦横比は書き起こした `aspect` に合わせる。
3. 別の言語で作るなら、`texts` の訳を `{"原文": "訳"}` で用意して、`prompt` の引用部分だけを置き換える。
4. できたものを `texts`・`numbers` と1つずつ照合する。

試してわかったこと：
- 画風は**書き起こしの `style_notes` をそのまま使う**のがいちばん元に近い。手持ちの画風辞書に「近いもの」を当てると、見立てが外れて元から離れることがある。辞書の画風は、人が確かめて「これで合っている」と印を付けたレシピにだけ当てる。
- 作り直しでは、元に無い看板の字や、特定の国風の家並みが足されやすい。決まり文句で毎回止める。
- 古い図の言い回しも、そのままレシピに写る。今は使わない表現が混じっていないか、作る前に `texts` を見る。
