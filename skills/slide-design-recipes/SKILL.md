---
name: slide-design-recipes
description: 提案書・説明資料のスライドを、7つの意匠（クリーム＋白カード／左レール／ダーク交互／ホワイト・エディトリアル／エビデンス・アトラス／フェーズ・ゲージ／ブルー読了バー）から選んで、原稿 JSON から編集できる PPTX に書き出す雛形と規範。PowerPoint もローカルの素材も要らない（python-pptx だけ）。下端に生成画像の風景の帯を敷く作り方、意匠の選び方、日本語・タイ語・ベトナム語の書体の罠、納品前の自己検査つき。「提案資料を作って」「スライドのテンプレート」「同じ原稿を別デザインで」「PPTX を自動生成」「官公庁向けの資料」 / slide template, pptx generation, design system, proposal deck で使う。
---

# slide-design-recipes — 原稿を書けば、意匠を選んで PPTX になる

実務で十数種の意匠を試して、使い続けた7種だけを雛形にした。
**原稿（JSON）と見た目（意匠）を分けて持つ**ので、同じ原稿を `--design` だけ替えて別の意匠で出し直せる。

## 1. 意匠を選ぶ

| 意匠 | 名前 | 向いている相手・場面 | 骨格 |
|---|---|---|---|
| **B**（既定） | 左レール＋罫線カード | 官公庁・研究機関。いちばん汎用 | 左に濃色のレールと章番号 |
| D | ホワイト・エディトリアル | 印刷して配る提案書 | 白地、左端に細い帯、金の差し色 |
| E | エビデンス・アトラス | 図やデータが主役の技術説明 | 上端に太罫、項目ごとに5色を順に |
| C | ダーク交互 | 投影して見せる場、動画に載せる | 濃い面と淡い面が交互 |
| F | フェーズ・ゲージ | 段階的な計画が主題 | 全ページ上端に Phase 1〜5 のゲージ |
| A | クリーム＋白カード | 民間・一般向け。やわらかい調子 | 白い角丸カード |
| G | ブルー・読了バー | 企業の会社説明・Web と色を合わせたいとき | 白地、上端に読了バー |

選び方：相手（官公庁→B／政府要人→D・F／民間・一般→A）→ 主役（図→E／段階→F）→ 出口（印刷→D／投影・動画→C）。迷ったら B。
色は `scripts/designs.json` の16進を替えるだけで自社の色にできる。意匠を足すなら1件足す。

## 2. 原稿を書く

`examples/example_ja.json` を写して、文言だけ替える。

- 面の種類：`cover` 表紙／`section` 章扉／`bullets` 箇条／`cards` カード2〜4枚／`stats` 大きな数字2〜4つ／`flow` 横一列の流れ／`compare` 左右くらべ／`image` 図1枚＋説明／`video` 動画／`full` 全面画像／`closing` 結び。
- `/` は改行。単位などに `/` を使いたいときは「冊（月）」のように書く。
- `notes` は話す原稿（発表者ノートに入る）。`chapter` は「03 PLAN」のような章番号。
- **決まっていない数字は `◯◯` のまま**にして「（要確認）」を添える。それらしい数字を埋めない。
- 書体：`"font"`（既定 BIZ UDPGothic）。タイ語は `"font_cs": "Leelawadee UI"`、ベトナム語は `"font": "Segoe UI"` など、その言語の字がある書体にする。

## 3. 書き出す

```bash
pip install python-pptx pillow
python scripts/deck.py examples/example_ja.json -o out/proposal.pptx
python scripts/deck.py examples/example_ja.json --design D -o out/proposal_D.pptx
```

保存後に自己検査して `OK` か `NG` を出す（effectLst の二重付与＝PowerPoint で開けなくなる／本文が帯にかかる）。

## 4. 下端の帯（任意）

本文の面の下端に、薄い風景の帯を敷くと資料全体に統一感が出る。表紙・章扉・結びには敷かない。

1. `image-prompt-recipes` の画風 S6（水彩）か S7（リソグラフ）で、3:1 の横長パノラマを生成する（背景色はスライドの地の色に合わせる）。
2. `python scripts/make_band.py panorama.png -o scripts/bands/<帯の名前>_town.webp` で 12:1 に切り出し、上端をぼかして透過にする。
3. 帯の名前は `designs.json` の `band`。`town`・`fields`・`river` の3場面を作ると面ごとに順に回る（1つだけでもよい）。

見本として `scripts/bands/watercolor_town.webp`（意匠 A〜C 用）を同梱している。

## 5. 確かめて渡す

- 画像にして目で見る：PowerPoint、または `soffice --headless --convert-to pdf out/proposal.pptx`。
- 図は `image` の面に差し込む。図がまだ無ければ差し替え用の枠が出る。図の作り方は `image-prompt-recipes`。
- `◯◯` のまま残した箇所は一覧にして相手に確認する。
- 罠と規範は `references/design-guide.md`。
