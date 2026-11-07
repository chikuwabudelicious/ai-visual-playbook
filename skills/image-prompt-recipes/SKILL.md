---
name: image-prompt-recipes
description: 文字入りインフォグラフィック・図解・挿絵・アイコン・スライド用の帯画像・写真風の背景を、画像生成AI（gpt-image 系ほか）で「一から試行錯誤するより確実に」作るためのプロンプト集と手順。画風の頭文（12種）＋図の種類別の中身テンプレ（循環・工程・物質収支・比較・数字・年表・断面図など）＋言語別の文字指定＋余計な文字を足させない決まり文句＋生成後の点検。既存の図を文字のレシピに書き起こして別環境で作り直す方法、文字だけ別言語に差し替える方法も含む。「インフォグラフィックを作って」「図解を画像で」「日本語の文字が崩れない画像」「スライドの挿絵」「アイコンを透過で」「同じ画風で何枚も」「この図を英語版に」 / infographic, diagram with text, gpt-image prompt, consistent style, transparent icons, multilingual labels で使う。
---

# image-prompt-recipes — 画像生成で「外さない」ための型

実務で数千枚を生成して残った、効いた書き方だけをまとめた。
ゼロから書くより、**近い型をなぞって中身だけ差し替える**ほうが品位が安定する。

## 1. まず方式を決める

| 方式 | 中身 | 向いている場面 |
|---|---|---|
| **A. 文字は自分で置く** | 画像には絵・アイコン・背景だけを描かせ、文字はスライドや HTML の上に置く | 数字が後で変わる図、相手が直す資料、法的に正確さが要る表記 |
| **B. 文字ごと描かせる** | ラベルも画像に焼き込む（gpt-image 系は日本語・ベトナム語も正確に描ける） | 見た目優先の図解、SNS、多言語の量産 |

迷ったら A。B は生成のたびに文字を目で照合する手間がかかる。

## 2. プロンプトは4段で組む

```
[画風の頭文]  references/styles.md から1つ（色を5色以内に固定するのが肝）
[文字の指定]  references/text-and-languages.md の言語別の1文
[中身]        references/kinds.md の図の種類別テンプレに、ラベルを '…' で引用して入れる
[決まり文句]  「引用した文字以外は描かない・看板や題を足さない・特定の国に見せない・数字はこのとおり」
```

決まり文句（毎回末尾に付ける。英語のまま使う）：

```
Keep each label SHORT exactly as given. The ONLY text in the image is the quoted labels, spelled exactly as given;
do NOT add any other words, signs, shop signs, banners, captions or titles. Numbers must be exactly: <数字を列挙>.
The setting is neutral and not identifiable as any particular country (no landmarks, no flags).
No watermark, no logo.
```

- **ラベルは短く**：1つ12字（欧文なら4語）程度まで。長い説明は画像の外に置く。
- **数字を列挙する**：AI は数字を「それらしく」書き換える。`Numbers must be exactly: 10, 24, 2, 500` で止まる。
- **タイトルを描かせない**：スライド側に題があるなら `no overall title at the top` を入れる。入れないと勝手に大見出しが付く。
- **「キャンバスを埋める」**：`The diagram must FILL the canvas … keep a clean 4% margin` を入れないと、小さな図の周りに大きな余白が出る。

## 3. 生成する

- 文字入りの図は **gpt-image 系**（2026-11 時点：`gpt-image-2`、`gpt-image-2.5-sunburst`、`gpt-image-2.6-sunburst`）。旧 `gpt-image-1` 系や汎用の画像モデルは日本語が崩れやすい。モデル名は変わるので、使う前に API のモデル一覧で確かめる。
- 速い下書き用の軽いモデル（例 `*-flare`）は、線が途切れる・道がつながらないことがある。本番は細密なほうで。
- 透過 PNG（アイコン・帯）は `background="transparent"` が効くモデルを使う。効かないモデルでは白地で描いてから抜く。
- 道具：`scripts/gen_image.py`（OpenAI の Python SDK。モデルの逃げ先・透過・余白トリム・送る指示の確認つき）。

```bash
pip install openai pillow
export OPENAI_API_KEY=...
python scripts/gen_image.py --prompt-file prompt.txt --size 1536x1024 -o out/fig.png --trim
python scripts/gen_image.py --prompt-file prompt.txt --dry          # 送る指示と費用の目安だけ
python scripts/gen_image.py --prompt "flat vector icon ..." --transparent --size 1024x1024 -o out/icon.png
python scripts/gen_image.py --edit out/fig.png --prompt-file relang_th.txt -o out/fig_th.png   # 文字だけ差し替え
```

費用の目安（2026-11 時点）：高品質1枚 約0.2〜0.3 USD、30〜70秒。量産の前に1枚だけ試す。

## 4. 点検する（省かない）

1. **数字と固有名詞を原稿と1つずつ照合**する。生成は焼き込みの字を間違える。
2. 頼んでいない文字（看板・題・透かし風の字）が足されていないか。
3. 画風がそろっているか（同じ資料の中で線の太さ・色数が違うと安っぽく見える）。
4. 人の顔・ロゴ・実在の建物が写っていないか。
5. 直すときは**プロンプトの該当箇所だけ**を直して作り直す。全文を書き換えると別の絵になる。

詳しい失敗例と対処は `references/pitfalls.md`。

## 5. 多言語にする

- **作り直さず、文字だけ差し替える**のが速く安く、構図もそろう（画像編集 API に元画像を渡す）。指示文は `references/text-and-languages.md` の「差し替え」。
- 作り直すなら、プロンプトの骨格は共通にして**ラベルだけ言語辞書で差し替える**。写真風の背景など文字の無い画像は1枚を全言語で使い回す。
- タイ語・アラビア語・ゾンカ語など文字体系が違う言語は、1枚出して字形を確かめてから残りを回す。

## 6. 別の環境で同じ図を作り直す（レシピ化）

元の画像ファイルを持ち歩けないとき（クラウド・別PC・共有先）は、**画像を文字の「レシピ」に書き起こして**持ち歩き、行った先で生成し直す。
書き起こしの指示文とレシピの形式は `references/recipes.md`。Claude や Codex に画像を見せてこの指示を渡せば、APIキーなしでもレシピを作れる。

- 作り直しは「同じ中身・同じ画風の新しい1枚」で、元と1画素まで同じにはならない。
- レシピの画風は、書き起こしたメモ（`style_notes`）をそのまま使うのがいちばん元に近かった。辞書の画風に寄せると、見立てが外れて離れることがある。

## ファイル

| ファイル | 中身 |
|---|---|
| `references/styles.md` | 画風の頭文12種（そのまま貼れる英文） |
| `references/kinds.md` | 図の種類別の中身テンプレ12種と作例 |
| `references/text-and-languages.md` | 言語別の文字指定、文字の差し替え指示 |
| `references/recipes.md` | 書き起こしの指示文とレシピの形式 |
| `references/pitfalls.md` | 実際に起きた失敗と対処 |
| `scripts/gen_image.py` | 生成・編集・透過・トリム |
