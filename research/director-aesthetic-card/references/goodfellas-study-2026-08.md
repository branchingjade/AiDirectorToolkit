# 《好家伙》(Goodfellas, 1990) 单片研习轮来源地图（斯科塞斯，零存量全新建档）

2026-08 实测。产出：`film-suite-research/研习报告/好家伙_研习报告.md` + `技法卡片源稿/好家伙_技法卡片.md`。编号 [研S1-19] 报告与卡片共用（单片研习独立编号变体，主卡片未落盘属预期）。引文校验 18 引文块 + 全部中文引文 0 MISS。

## 存档对照（pages/gf_*）

| 编号 | 存档 | 内容 |
|---|---|---|
| 研S1 | gf_enwiki_raw.txt | 英维 Goodfellas raw：制作/摄影/后期/试映/遗产/切斯《黑道家族》引语 |
| 研S2 | gf_zhwiki_raw.txt | 中维「盜亦有道」raw：拍摄背景/影响段（小弟 vs 老大）/史实对照/结尾字幕 |
| 研S3 | gf_ebert1990.txt | Ebert 1990 原评（wayback 20131002060956）："No finer film...not even The Godfather" |
| 研S4 | gf_ebert_great.txt | Ebert Great Movies（wayback 20150326042807）：Copa 184 秒/「nostalgia for the lifestyle」 |
| 研S5 | gf_nyt_banality.txt | NYT Linfield 1990-09-16《Goodfellas Looks at the Banality of Mob Life》（wayback 20171007070355）：斯科塞斯「电影关于钱」/Pileggi「副官」比喻/佩西谈杀 Spider |
| 研S6 | gf_mcconkey.txt | Filmmaker Magazine 2015 McConkey 斯坦尼康访谈（wayback 20250827010927）：8 条/厨房光线/桌子飞向镜头 |
| 研S7 | gf_kenny_excerpt.txt | RogerEbert.com Kenny《Made Men》书摘（wayback 2021id_）：Schoonmaker「Performance, performance, performance」 |
| 研S8 | gf_soundtrack_raw.txt | 英维 Goodfellas (soundtrack) raw：逐场景完整歌曲表 |
| 研S9 | gf_springfield_script.txt | Springfield 全片台词转录稿 81KB（含片头后备箱段） |
| 研S10 | gf_criterion_7103.txt | Criterion Current《Crime Bosses and Made Men》(2020)（jina）：教父/好家伙类型对照 |
| 研S11 | gf_douban_reviews.json | 豆瓣长评列表（subject 1292268，252 篇） |
| 研S12-16 | gf_review_*.txt | 豆瓣 5 篇：6376700(1052 用，Layla 浪漫迷狂)/1180242(558 用)/12854138(99 用，散文式)/12115410(36 用，**Kael 批判译文**)/9778817(10 用，继承与突破) |
| 研S17-19 | gf_review_*.txt | 豆瓣 3 篇：1280853(79 用，人物原型)/1888958(22 用)/7782127(14 用，双旁白+转引斯科塞斯) |

## 本轮新坑

1. **Criterion films/<数字> 猜错 = 无关影片完整页，非 404**：猜 `films/602-goodfellas` 实得今村昌平《猪与军舰》(The Pornographers) 完整页（jina 渲染 15KB 正常页）。比 404 壳更危险——内容完全可用、只是错的。title 必验。华纳大厂片（好家伙）无 Criterion 发行/专属 essay：DDG site: 搜索负面取证后，用 Current 相关文章代偿（posts/7103 含教父对照金句）。
2. **Springfield 转录稿截断坑**：goodfellas 转录稿容器 class 是 `movie_script`（非卢布廖夫轮的 `scrtext`）；且从记忆中的经典台词行（"As far back"）起截取会丢掉片头对白（后备箱开场整段）。正确做法：从页面正文**第一对白行**（grep 页面首个对话，如 "What the fuck is that"）起截，存后 grep 首句验证完整；转录稿无场次号/舞台指示，台词引文按「转录稿」标注、行号不可用。
3. **Ebert Great Movies slug 年份 ≠ 影片年份**：Goodfellas 上映 1990，slug 是 `great-movie-goodfellas-1991`（2011 年写入系列时的年份）。别按上映年份拼 slug——先 CDX `url=rogerebert.com/reviews/great-movie-<片名>*` 探测真实 slug。
4. **豆瓣繁体长评转简体加引号 = 假引文**：繁体原文转成简体放进「」引号，校验必 MISS 且属转述冒充引文（S19 三处中招）。修复：要么保留繁体原文进引号并标注「繁体原文」，要么转述不加引号。
5. **jina 渲染 Criterion 文章含 markdown `_斜体_`**：`_The Godfather_` 下划线破坏引文匹配，校验 norm 管道需剥 `_`（与剥 `''`/wikilink 并列）。
6. **成片字卡无逐字证据纪律**：「This film is based on a true story」字卡（任务预设）、《Mona Lisa》片尾歌、凯伦枪旁白原句均未在转录稿/维基/影评出现——诚实声明标未取证，正文用已验证等价物替代（凯尔转述「当她看到他的枪时，她感到很兴奋」）。

## 校验 norm 管道（本轮 0 MISS 配方）

弯引号归一（’‘“”→'"）→ 迭代剥 `[[target|display]]` 取 display → 剥 `''` 与 `_` → 去全部引号字符 → 压空白 → 小写。中文引号句=译文时，句内/句后必须附英文原句且原句过存档匹配（译文配对规则）。

## vs 教父对比链（对比节材料）

Ebert 1990 原评「No finer film has ever been made about organized crime – not even The Godfather」+ Criterion 7103「reinvented in 1972 with The Godfather and again in 1990 with Goodfellas」+ 切斯《黑道家族》自述（「something operatic about it, classical, even the clothing and the cars」，英维 Legacy 段）+ 中维影响段（小弟 vs 老大）+ 本地《教父》技法卡片/研习报告转引。对比维度表（视点/阶层/暴力/音乐/空间/结局）为分析框架，标注非单一文献原文。

## 未取证清单

- 「based on a true story」字卡措辞与位置（片头/片尾）
- 《Mona Lisa》片尾歌（英维 soundtrack 完整表未收录；片尾曲实为 Sid Vicious My Way + Layla Piano Exit）
- 凯伦枪旁白原句（转录稿无；Ebert 亦未提枪场景）
- 《Scorsese on Scorsese》原书（Thompson/Christie 1996 引文均经英维转引，页码 150–161）
- 豆瓣 7782127 转引的斯科塞斯谈 60 年代原话（中文转引，原访谈未核）
