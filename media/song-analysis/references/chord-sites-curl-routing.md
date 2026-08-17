# 和弦数据源纯 curl 路由（2026-08-14 实测）

日本动漫曲/日曲抓和弦与 BPM 数据。全部无需浏览器，curl + python 即可。抓不到直接标注「未验证」，不要反复重试。

## 可用源（按优先级）

### 1. songbpm.com（服务端渲染，Key/BPM/时长）
- URL：`https://songbpm.com/<artist-slug>/<song-slug>`（无 @ 符号）
- slug 靠猜，404 就换变体。实测：`ikimonogakari/blue-bird`（青鸟）、`lisa/gurenge`（红莲华）、`myth-roid/styx-helix`（STYX HELIX）；`aoi-tori`/`aoitori`/`mythroid` 等均 404
- 「Song Metrics」的 `<dl>` 区块含 Key / Duration / Tempo (BPM)，直接静态 HTML
- 提取正则：`<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>`（re.S）
- ⚠️ 它的 Key 是机器频谱判定，与谱面常冲突（STYX HELIX 报 Key A、谱面 B 小调；青鸟报 F♯/G♭ 与谱面 F♯m 一致）——**只采信 BPM/时长**，Key 以和弦谱为准并标注分歧

### 2. chordu.com（搜索摘要即和弦数据）
- 入口：web_search「chordu <歌名> chords」，结果摘要直接含：
  - `emphasize these chord progressions: A, B, C#m, A, C#m, E, A`（和弦序列）
  - `key of C# Minor`（调）
  - `start slowly at 61 BPM and progress to the song's BPM of 123`（半速起练 → 实际 BPM = **半速律动证据**，可写进拆解卡）
- 页面 HTML 可 curl（HTTP 200）：完整谱面是 JS 加载（"Loading chords sheet..."），但摘要文本 + `Counter(re.findall(r'\b[A-G][#b]?(?:m|maj7|m7|7|sus4|add9)?\b', html))` 的 token 频次足够定和弦池
- 翻唱页 = 移调佐证：度数一致即确认骨架（STYX HELIX 原曲 Bm 系 ↔ 翻唱 C#m 系）

### 3. ultimate-guitar.com（官方 tab 可 curl）
- `https://tabs.ultimate-guitar.com/tab/<artist>/<song>-chords-<id>`，和弦文本直接可见
- 青鸟实测：`Cadd9 D Em | Am7 D G | Cmaj7 B7 Em | Em7 D Cadd9 G`（Em 移调版）

## 不可用源（2026-08-14 状态）
| 站点 | 现象 |
|---|---|
| ja.chordwiki.org | Cloudflare JS 挑战，curl 403 |
| music.j-total.net/db/search.cgi | GET/POST、UTF-8/EUC-JP 均返回同一 30089 字节空结果页 |
| gakufu.gakki.me | 连接超时（HTTP 000） |
| chordify.net | 403 |
| web.archive.org | 无 chordwiki/j-total 存档（CDX 查无） |

## 移调互推法（定原调关键）
chordu 常给移调版（如 Gm），UG 给另一移调（如 Em）——统一转度数（i–VI–III–VII），跨源一致即定原调。
例：青鸟 chordu 报 Gm-Cm-Dm-Bb-Eb（= 原调 F♯m-Bm-C♯m-D-A-E 的 i-iv-v-VI-III-VII），UG 报 Em 版 → 原调 F♯m，主循环 i–VI–III–VII（F♯m–D–A–E），段尾 V7（C♯7）回旋。

## 已验证数据集（可直接引用，2026-08-14）
| 曲 | BPM | Key | 主循环 | 色彩和弦 | 来源 |
|---|---|---|---|---|---|
| 青鸟（生物股长） | 152 | F♯m | F♯m–D–A–E（i–VI–III–VII） | C♯7 属七 | songbpm + chordu + UG |
| 红莲华（LiSA） | 135 | Em | Em–C–G–D（i–VI–III–VII） | E 大和弦（平行大调借用）、Bm | songbpm + chordu |
| STYX HELIX（MYTH&ROID） | 123 | Bm | Bm–A–C#m–E（i–VII–ii–IV） | C（bVI） | songbpm + chordu |

规律：三首均为「小调四和弦循环 + 1-2 色彩和弦 + 半速律动（chordu 61/67 半速证据）+ 落ち断崖→終サビ核爆」。
