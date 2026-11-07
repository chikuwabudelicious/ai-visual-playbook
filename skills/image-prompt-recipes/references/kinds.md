# 図の種類別の中身テンプレ

`styles.md` の画風の頭文のあとに置く「中身」。ラベルは `'…'` で引用し、短く。
作例の題材・数字は架空。自分の題材に差し替えて使う。

| 種類 | 向いている内容 | 推奨の縦横比 |
|---|---|---|
| 工程フロー | 手順・段階（3〜5個） | 16:9 / 3:2 |
| 物質収支（入る→処理→出る） | 量の変化・変換 | 16:9 / 3:2 |
| 循環図 | 繰り返す仕組み（4〜6個） | 1:1 |
| 2面の比較 | これまで⇔これから、A⇔B | 16:9 |
| 数字が主役 | 1つの大きな成果 | 16:9 |
| 年表・ロードマップ | 時期ごとの到達点（3〜5個） | 16:9 / 3:1 |
| 断面図 | 装置・建物の中身 | 3:2 |
| ハブ＆スポーク | 1つの目的と6つの手段 | 1:1 / 16:9 |
| 2つの力 | 「AとBの組み合わせ」 | 16:9 |
| 3列 | 3つの観点を並べる | 16:9 |
| 時間の対比 | 長い⇔短い（棒の長さで見せる） | 16:9 |
| 地図・俯瞰 | 地域の中の流れ | 3:2 |

---

## 工程フロー

```
Content: a horizontal FOUR-STEP process flow, left to right, four equal rounded cards connected by
thin chevron arrows.
Card 1 amber badge '1', heading '回収', thin icon of a small collection truck.
Card 2 amber badge '2', heading '洗浄', small subtext '約30分', icon of a washing tank with bubbles.
Card 3 amber badge '3', heading '粉砕', icon of a shredder with small flakes.
Card 4 amber badge '4', heading '再生素材', icon of a sack of pellets with a small leaf.
Keep each heading SHORT exactly as given. Numbers must be exactly: 30.
```

## 物質収支

```
Content: a horizontal INPUT -> PROCESS -> OUTPUT diagram with thick amber arrows between three zones.
LEFT zone label '入る', icon of mixed used bottles, big figure '約3 トン/日'.
CENTER dark green rounded box, icon of a processing machine, label '再生工程'.
RIGHT zone label '出る', icon of a sack of pellets, big figure '約2.4 トン/日', small subtext '年間 約800 トン'.
Below the center, a thin downward branch arrow to a small node 'ラベル・キャップ → 別回収' in gray.
Numbers must be exactly: 3, 2.4, 800.
```

## 循環図（1:1）

```
Content: a circular CYCLE diagram (closed loop) with 5 nodes evenly placed around a central dark green
filled circle. Center text two lines: '町の' / '資源循環' in white. Thin amber arrows flow clockwise
connecting the five nodes in order.
Node 1 (amber badge 1) icon of a kitchen: '家庭の生ごみ'.
Node 2 (badge 2) icon of a compost bin: '地域で処理'.
Node 3 (badge 3) icon of a sack with sprout: '土の材料'.
Node 4 (badge 4) icon of a community garden: '市民農園'.
Node 5 (badge 5) icon of vegetables in a basket: '地元の野菜'.
Short labels exactly as given, placed beside each node.
```

ノードは6個まで。7個以上は文字が小さくなり崩れやすい。

## 2面の比較

```
Content: a TWO-PANEL side-by-side comparison.
LEFT panel tinted warm brown, heading 'これまで', icon of a long queue at a counter, big label '待ち 40分'
in brown, subtext '紙の申込書を手で転記'.
RIGHT panel tinted fresh green, heading 'これから', icon of a phone with a check mark, big label '待ち 5分'
in green, subtext 'スマホで事前に申込'.
A thin centered ribbon at the bottom: '窓口の混雑を8分の1に'.
Numbers exactly: 40, 5, 8.
```

## 数字が主役

```
Content: a HERO data panel. Centered very large figure '12,000' in deep green, directly beneath it the
unit '冊 / 年 の貸出増'. Below, a row of THREE small rounded chips each with a thin icon and short caption:
chip A icon of a child reading: '子どもの利用 2倍';
chip B icon of a clock: '夜9時まで開館';
chip C icon of a growth arrow: '3館に拡大予定'.
Figures exactly: 12,000 and 2 and 9 and 3.
```

## 年表・ロードマップ

```
Content: a horizontal TIMELINE with a thin baseline and four milestone markers (amber dots) left to right,
ascending small step bars.
Milestone 1 '1年目' caption '1店舗で試行'.
Milestone 2 '2年目' caption '市内5店舗へ'.
Milestone 3 '3〜4年目' caption '県内へ展開'.
Milestone 4 'その先' caption '他地域のモデルに'.
Short captions exactly as given, stacked under each marker.
```

## 断面図

```
A clean cross-section cutaway of <a two-story timber house with a rooftop solar panel and a rainwater
tank>, technical but elegant line-art style, four amber numbered callouts pointing to parts:
1 '屋根で発電', 2 '雨水をためる', 3 '断熱の壁', 4 '床下の換気'.
Labels exactly as given.
```

## ハブ＆スポーク

```
A radial hub-and-spoke diagram: a central green circle '食品ロスを6方向から減らす', with six small cards
around it, each a thin icon + short label: '買いすぎない', '小分け販売', '期限前の値引き',
'寄付につなぐ', '量り売り', '土に返す'. Balanced, symmetrical, six nodes.
```

## 2つの力

```
Two large side-by-side panels combined by a central plus sign.
LEFT panel green, icon of a teacher with a tablet, heading '先生の工夫', subtext '毎回5分の振り返り'.
RIGHT panel brown, icon of students in a circle, heading '生徒どうし', subtext '教え合いの時間'.
Center a bold amber '＋'. Bottom thin ribbon: '定着率が上がる'.
```

## 3列

```
Three vertical columns under a heading '3つの約束':
Column 1 icon of a leaf '地元の材料';
Column 2 icon of a recycling arrow '容器は回収';
Column 3 icon of a handshake '売上の1%を寄付'.
Clean three-column layout.
```

## 時間の対比

```
A dramatic time comparison. Two horizontal bars: a very long gray bar labeled 'これまで 3週間',
and a very short green bar labeled '新しい方法 2日'. Big amber callout 'わずか2日'.
Clean, minimal, lots of space.
```

棒の長さを実際の比に合わせたいときは、方式A（図形で描く）にする。生成は長さの比を正確に守らない。

## 地図・俯瞰

```
A bird's-eye illustrated map of <a small fictional town> on an off-white background: a river crossing
from left to right, a market in the center, farms at the top, houses at the bottom. Thin amber dashed
route lines with arrows connect: market → '回収所' → '処理場' → farms. Only these labels: '回収所', '処理場'.
Roads must connect continuously; no dead ends.
```

道や線路は「途切れずにつながる」と書く。速いモデルほど道が途中で切れる。
