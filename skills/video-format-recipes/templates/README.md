# templates — JSON を書き換えるだけで書き出せる見本3型

| フォルダ | 型 | 比率・尺 | 中身 |
|---|---|---|---|
| `number/` | F05 数字1つ | 9:16（1080×1920）・15秒 | 前振り → 特大の数字がカウントアップ → 比べる棒（任意）→ 意味づけ2つ → 発信者名 |
| `list/` | F17 数えて分かる | 9:16・24秒 | 問いかけ＋特大の数 → 項目を3〜5個、1つずつ積む → まとめ → 発信者名 |
| `compare/` | F04 くらべて見る | 1:1（1080×1080）・24秒 | 左＝これまで、右＝新しいやり方。観点ごとに2〜4行 → まとめ → 発信者名 |

- 各フォルダの `index.html` がテンプレート、`examples/sample.json` が話のデータの見本（中身はすべて架空）
- 変数の一覧は `index.html` 冒頭の `data-composition-variables`。JSON に無い項目はそこの既定値になる
- 文言の `/` は改行位置。文字の大きさは枠に収まるよう自動で縮む
- 時刻はすべて拍（`bpm`・`beat_offset`）から決まる。文言・数字・時刻を HTML に直書きしない
- ロゴ・BGM・書体ファイルは同梱していない。書体は Google Fonts の Noto Sans JP、GSAP は cdnjs（3.12.5 に固定）から読む。**書き出しにはネット接続が要る**

## 必要なもの

- Node.js 18 以上（`npx`）、ffmpeg
- 代わりの書き出し（`capture.py`）を使うなら Python 3.9 以上と Playwright

## 書き出し（HyperFrames）

```bash
cd templates
npx --yes hyperframes@0.8.149 render number --variables-file number/examples/sample.json -o out/number.mp4
npx --yes hyperframes@0.8.149 render list    --variables-file list/examples/sample.json    -o out/list.mp4
npx --yes hyperframes@0.8.149 render compare --variables-file compare/examples/sample.json -o out/compare.mp4
```

- 0.8.149 は動作を確かめた版（2026-11）。新しい版に上げるときは見本で1本書き出して確かめてから
- 下書きは `-q draft`（速い）。15秒の型で、初回はブラウザの準備を含めて2分前後
- 書き出す前に前回の mp4 を消しておく（成否は出力ファイルで見る）
- 静止画の `npx hyperframes snapshot` は変数ファイルを受け取らない（0.8 系）。別の話を下見するなら、書き出した mp4 から一覧画像を作る：

```bash
ffmpeg -i out/number.mp4 -vf "fps=1,scale=270:-2,pad=iw+8:ih+8:4:4:white,tile=8x2" -frames:v 1 out/number_tiles.png
```

## 量産（JSON 1件＝1本）

```bash
for f in episodes/*.json; do
  name=$(basename "$f" .json)
  rm -f "out/$name.mp4"
  npx --yes hyperframes@0.8.149 render list --variables-file "$f" -o "out/$name.mp4"
done
```

メモリの少ない機械では1本ずつ回す（並べて走らせると落ちる・古い HTML で書き出されることがある）。

## BGM を付ける（任意）

テンプレートには音を入れていない。曲を用意したら：

1. 曲のテンポ（BPM）と最初の拍の秒を測る（例：`python -c "import librosa;y,sr=librosa.load('bgm.mp3');t,b=librosa.beat.beat_track(y=y,sr=sr);print(t,librosa.frames_to_time(b,sr=sr)[:4])"`）
2. JSON の `bpm` と `beat_offset` に入れて書き出す。テンポが型の範囲（`index.html` の bpm の説明）から外れる曲は、倍か半分の値を入れる（76BPM の曲なら 152）
3. 書き出した mp4 に重ねる（尺に合わせて切り、最後1.5秒でフェード）：

```bash
ffmpeg -i out/list.mp4 -i bgm.mp3 -map 0:v -map 1:a -c:v copy \
  -af "apad,afade=t=out:st=22.5:d=1.5,loudnorm=I=-16:TP=-2" -c:a aac -b:a 192k -ar 48000 -t 24 out/list_bgm.mp4
```

`st` は「尺 − 1.5」。生成曲・手持ち曲とも、公開先での利用条件を確かめる。

## 代わりの書き出し（Chrome＋ffmpeg）

HyperFrames が動かない環境では、ブラウザでコマを撮って ffmpeg でつなぐ `capture.py` を使う（遅い）。

```bash
pip install playwright && python -m playwright install chromium
python capture.py number/index.html number/examples/sample.json out/number.mp4
python capture.py list/index.html list/examples/sample.json out/list.mp4 --bgm bgm.mp3
python capture.py compare/index.html - out/preview.mp4 --fps 2     # 既定値のまま粗く下見
```

## 書き換えるときの注意

- **色**は各 `index.html` の `<style>` の色コード。書体を替えるなら Google Fonts の `<link>` と `font-family` の2か所
- **文字幅の見積もり**（`est()`）はフォントの読み込みを待たずに大きさを決めるための概算。欧文や別の書体では外れることがあるので、必ず一覧画像で確かめる
- **遅れて出る要素**は CSS で最初から `opacity:0` にし、アニメは `immediateRender:false` にする（逆だとちらつく）
- **カウントアップ**はプロキシの setter で数字を書き換えている（`onUpdate` はコマ送りで呼ばれないことがある）
- **書体に無い字**は別の書体で出る。記号（✉ ₂ など）を使ったら書き出し前に確かめる
- **ネット無しで書き出す**なら、GSAP と書体のファイルを `assets/` に置き、`<script src>` と `@font-face` を相対パスに替える
- GSAP と Noto Sans JP（SIL Open Font License）の利用条件は、それぞれの公式で確かめる
