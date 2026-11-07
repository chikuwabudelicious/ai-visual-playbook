# 文字の指定と多言語

## 言語別の1文（画風の頭文のすぐ後に置く）

| 言語 | 指定 |
|---|---|
| 日本語 | `All text is Japanese, rendered ACCURATELY and legibly in a clean gothic sans (UD gothic style). Use exactly the Japanese strings given — do not add, translate or paraphrase any text.` |
| 英語 | `All text is English, rendered accurately and legibly in a clean sans-serif. Use exactly the English strings given — do not add or paraphrase any text.` |
| ベトナム語 | `All text is Vietnamese, rendered ACCURATELY with correct diacritics (tone marks stacked correctly) in a clean sans-serif.` |
| タイ語 | `All text is Thai, rendered ACCURATELY with correct vowel and tone marks above and below the consonants, in a clean Thai sans (Loopless style).` |
| 中国語（簡体） | `All text is Simplified Chinese, rendered accurately in a clean sans (Hei style). Do not use Traditional characters.` |
| 韓国語 | `All text is Korean, rendered accurately in a clean sans (Gothic/Dotum style).` |
| インドネシア語・タガログ語ほか | `All text is <Language>, rendered accurately and legibly in a clean sans-serif.` |
| アラビア語 | `All text is Arabic, written right-to-left with correctly joined letters. Do NOT mirror the layout; only the text runs right-to-left.` |

ポイント：
- 書体は「〜 style」と**系統で言う**（具体的なフォント名で指定しても、その書体にはならない）。
- 日本語の図に英語を混ぜたくないときは `No English unless specified.` を足す。
- 日本語は「ゴシック体」の指定が安定する。明朝で描かせると細い線がかすれやすい。

## 文字を崩さないための書き方

1. ラベルは `'…'` で囲み、**引用した文字以外は描かない**と言う。
2. 1ラベル12字（欧文4語）まで。長い文は画像の外へ。
3. 数字は末尾で列挙する：`Numbers must be exactly: …`。
4. 化学式・下付き文字は Unicode の文字で渡す（`CO₂` `CH₄`）。`CO2` と書くと、そのまま描かれる。
5. 改行させたい箇所は `two lines: '…' / '…'` と言う。

## 文字だけ別の言語に差し替える（画像編集）

元画像を画像編集 API に渡し、次の指示を送る。構図・色・アイコンは元のまま残る。

```
Translate every piece of text in this infographic into <TARGET LANGUAGE>, and change NOTHING else:
keep the exact layout, icons, colors, arrows, badge positions, bar lengths and margins.
Numbers, units, symbols and these terms stay exactly as they are: <固定する語をカンマ区切り>.
Render the <TARGET LANGUAGE> text accurately and legibly in a clean sans-serif, at a similar size to
the original, fitting inside the same boxes. Do not add any new text.
```

- 社名・製品名・型番・単位は「固定する語」に必ず入れる。モデルは単位まで訳しにかかる。
- 文字数が大きく増える言語（ドイツ語・タイ語など）は、元を短い言語（英語）にすると収まりやすい。
- 解像度を上げる目的で編集にかけない。編集のたびに少しずつ画質が落ちる。
- モデルによっては編集で画風が写実寄りに変わる。差し替え用には、画風を保つモデルを1つ決めて固定する。

## 作り直す場合（骨格は共通、ラベルだけ辞書）

```python
LABELS = {
  "ja": {"step1": "回収", "step2": "洗浄"},
  "en": {"step1": "Collect", "step2": "Wash"},
}
def prompt(lang):
    L = LABELS[lang]
    return STYLE + TYPO[lang] + f"Card 1 heading '{L['step1']}' … Card 2 heading '{L['step2']}' …" + GUARD
```

文字の無い画像（写真風の背景・挿絵）は1言語ぶんだけ作り、他の言語へ使い回す。
