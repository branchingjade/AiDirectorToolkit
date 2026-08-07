# 六部剧本抓取记录（2026-08-05，高分剧本分析任务）

工作区：`_work/film-suite-research/`，笔记 `高分剧本分析.md`，原文 `pages/screenplay-*.txt`

## 逐片结果

| 电影 | 文件（pages/） | 来源 | 规模 | 文本层质量 |
|---|---|---|---|---|
| 肖申克的救赎 | screenplay-shawshank.txt（主用）+ screenplay-shawshank-slug.txt | IMSDB + Script Slug PDF（126 页） | 29,155 词 / 242 编号场景 | IMSDB 版完整可靠；Slug PDF 版丢失场景号但标题格式同款（250 处 `INT -- ...`） |
| 教父 | screenplay-godfather.txt | Script Slug PDF | 124 页（formfeed 实测）/ 22,164 词 | ⚠️ 场景标题仅恢复 13 处（`INT. DON CORLEONE'S HOME OFFICE  DAY` 式，破折号被字库吞掉）；对白文本完整 |
| 寄生虫 | screenplay-parasite.txt | Script Slug FYC PDF（FOR YOUR CONSIDERATION 页眉） | 144 页 / 29,708 词 / 158 编号场景（1–159 连续） | 良好 |
| 银翼杀手2049 | screenplay-bladerunner2049.txt | Script Slug PDF（FINAL SHOOTING SCRIPT） | 109 页 / 24,578 词 / 169 标题 | 标题完好；部分动作行文本层有损（词数偏低） |
| 低俗小说 | screenplay-pulp-fiction.txt | IMSDB | 27,566 词 / 94 标题 | 完整；空行多（<br> 换行） |
| 卧虎藏龙 | screenplay-crouching-tiger.txt | Internet Archive OCR（`crouching-tiger-hidden-dragon_20260606`） | 20 扫描页 ≈ 40 剧本页 / 21,327 词 / 147 标题 | OCR 有噪声（页脚 CVISION 水印）；**Schamus "First Draft, Revised 25 March 1999" 修订初稿，非最终拍摄稿**（最终稿署名 Wang Hui-ling / James Schamus / Tsai Kuo-jung） |

## 启发式统计结果（parse_stats.py，2026-08）

| 剧本 | 动作% | 对白% | 平均动作行(词) | 平均对白行(词) |
|---|---|---|---|---|
| 肖申克 | 62 | 28 | 6.5 | 6.1 |
| 教父 | 47 | 48 | 4.3 | 5.1 |
| 寄生虫 | 58 | 35 | 5.7 | 5.2 |
| 银翼杀手2049 | 66 | 29 | 6.5 | 5.9 |
| 低俗小说 | 58 | 36 | 5.4 | 5.5 |
| 卧虎藏龙 | 55 | 39 | 5.6 | 5.6 |

（百分比为启发式状态机估计，含折行；仅作横向比较。）

## URL 模式验证记录

- IMSDB 正文提取正则：`<td class="scrtext">(.*?)</td>`（re.S）→ `<br\s*/?>`→`\n` → 去 `<[^>]+>` → html.unescape → `\n{3,}`→`\n\n`。头部反框架 JS 片段会混入，忽略即可。
- Script Slug：页面 HTML 里 grep `https?://[^"']+\.pdf` 即得 assets.scriptslug.com 直链；slug 需从 web 搜索确认（`/scripts` 索引页 JS 渲染，裸 HTML 仅 5 条链接）。
- Internet Archive：`/metadata/<id>` 返回 JSON 含 files[]（name/size/format）；下载 URL 中文件名含逗号时逗号不编码（%2C → nginx 500）。
- 失败的路径：IMSDB 教父页（scrtext 提取仅 84 字符，结构不同）；Script Slug 无卧虎藏龙条目（含 `crouching-tiger-hidden-dragon-2000` 404）；weeklyscript.com（onload 跳 /lander）；html.duckduckgo.com 与 Bing 搜索页（curl 返回空/无法解析）。
- 值得再试的：scriptslug 其他片 PDF 直链模式（`assets.scriptslug.com/live/pdf/scripts/<slug>.pdf`）覆盖面广，先试再搜。

## 分析引用锚点（grep 用）

- 肖申克：`Get busy living`（≈99% 处）、`I'd only ask three beers apiece`（屋顶戏）
- 教父：`I believe in America`（开场）、`Blood is a big expense`（Sollozzo）、`offer he couldn't refuse`（Michael 解释）
- 寄生虫：`PIZZA BOXES`（折叠戏）、`Same smell`（Da-Song 点题）
- 银翼2049：`interlinked`（基线测试诗）、`breathe in detail`（K 出场）
- 低俗小说：`Royale with Cheese`、`Ezekiel 25`（两次出现）、`foot massage`
- 卧虎藏龙：`Li Mu Bai (30s)`（人物小传段）
