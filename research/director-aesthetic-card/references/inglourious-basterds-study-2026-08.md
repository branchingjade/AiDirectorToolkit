# 无耻混蛋（Inglourious Basterds, 2009）单片研习轮 — 来源地图（2026-08）

昆汀导演本体补课轮（创作极：改写历史 / 章回体 / 紧张对白〔酒馆戏〕）。低俗小说已在库，本文档为同导演第二片。产出：`研习报告/无耻混蛋_研习报告.md` + `技法卡片源稿/无耻混蛋_技法卡片.md`，共享 [研S1–研S20] 编号体系；存量转引链 [卡低俗]（《低俗小说_技法卡片.md》，章节式结构技法）。

> ⚠️ SKILL.md 正文已达 100K 容量上限（2026-08），本轮的泛化校验坑无法并入正文 ㊿ 系列，全部记在本文件「新坑」节，下轮合并正文时优先抄入。

## 存档清单（pages/qtar_*）

| 编号 | 文件 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | qtar_inglourious_enwiki_raw.txt（111,836 B） | 英维 raw | 剧情/制作（"gave me my movie"/"unplayable"/"too precious about the page"）/口碑争议（Mendelsohn/Rosenbaum/Hitchens/Le Monde）/片名 Basquiat-esque |
| 研S2 | qtar_inglourious_zhwiki_raw.txt（92,312 B） | 中维「惡棍特工」raw | 兰达四语（德语/英语/法语/意大利语）/酒馆英式手势暴露/德国版加长 50 秒/预告片台词 |
| 研S3 | qtar_ebert_review.txt（10,637 B） | rogerebert.com 四星影评 2009-08-19 直连 | "alternative ending"/Landa 画像/"embeds Tarantino's love of the movies" |
| 研S4 | qtar_guardian_2009_aug_19_..._v2.txt | 卫报 Bradshaw 差评 | 负面参照系；猜牌游戏段落被批"unendurably tedious" |
| 研S5 | qtar_guardian_2009_aug_23_..._v2.txt | 卫报 Philip French 影评 | 五章结构/"grand central conceit"电影院之死 |
| 研S6 | qtar_guardian_2009_aug_15_..._v2.txt | 卫报 Damon Wise 指南 | 四语拍摄/拼写原话/施魏格 fairytale |
| 研S7 | qtar_guardian_2009_may_20_..._v2.txt | 卫报 Mark Brown 戛纳现场 | 昆汀"my characters change the outcome of the war"原话 |
| 研S8 | qtar_guardian_cox_jina.txt（39,571 B） | 卫报 David Cox 博客（jina 复活） | 昆汀"cinema changes the world, and I fucking love that idea!"/Reality got this one wrong |
| 研S9 | qtar_imsdb_script.txt（265,194 字符，9,587 行） | IMSDb 剧本流传稿 | 五章标题卡/酒馆戏行号/巨脸复仇/片尾战报字幕 |
| 研S10–研S17 | qtar_douban_rev_*.txt（8 篇） | 豆瓣 rexxar 长评（7652→61 有用区间） | 骗术论/关于电影的电影/剧本分解/酒吧火拼顺序/后现代游戏/杰作·未完成/三一律/疯癫的诗意 |
| 研S18 | qtar_sensesfive_loveletter.txt | sensesfive 影迷长文（Kotzer 2010） | "电影强过历史"论（影迷层级） |
| 研S19/20 | qtar_douban_reviews_list.json / qtar_douban_suggest.json | rexxar 列表（total 1126）+ suggest | subject id 1438652 裸片名一次命中 |

## 探测与抓取要点

- **中维条目名探测**：简体「无耻混蛋」「无耻混蛋 (电影)」双候选全 MISSING（API 返回 -1/-2），真实条目为**台译「惡棍特工」**（list=search 命中后抓 raw）——韩/日/外语片用台/港译名作条目的又一实例（母亲轮 非常母親 同族）。
- **豆瓣 subject_suggest 直连成功**：裸片名「无耻混蛋」一次命中 subject 1438652（本轮无需 jina 代理兜底）。
- **Ebert 直连成功**：rogerebert.com/reviews/inglourious-basterds-2009 直接 curl 96KB（无需 wayback）；CDX 查询两次 403（"requires authorization"）后放弃 CDX，改直连——与变脸/大红灯笼轮同配方。
- **Guardian 2009 老页无 articleBody**：见下「新坑 ①」。

## 剧本证据（研S9 行号速查）

- 标题卡：CHAPTER ONE L26-30 "ONCE UPON A TIME IN... NAZI OCCUPIED FRANCE"（**省略号是源文本一部分**）；CHAPTER TWO L1051-1053 "INGLORIOUS BASTERDS"；CHAPTER THREE L2183-2185 "GERMAN NIGHT IN PARIS"（附 NOTE：全章原计划法国新浪潮黑白）；CHAPTER FIVE L7315-7317 "REVENGE OF THE GIANT FACE"；**该稿缺 CHAPTER FOUR 卡**（OPERATION KINO 以英维+豆瓣「第四幕：基诺行动」转引佐证，诚实声明已标注）；片尾 L9407-9409 重打首章标题卡=章回闭环。
- 酒馆戏：三杯威士忌 L6077（英式手势 "pinky to index"）L6080-6081；桌下鲁格 L6092-6094 / L6126-6129 / L6131-6132（two of us/three of us）；猜牌游戏 L5851-5862；三十三年威士忌 L6052-6053。
- 结尾：苏珊娜短片 L9288-9305（**剧本为法语+字幕，成片英维记载用英语**——版本差异标注）；"BURN IT DOWN" L9331-9335；火焰穿脸 L9340-9344；战报字幕 L9385-9395；刻卐字 L9535-9537 + 末句 "I think this just might be my masterpiece" L9553-9555。

## 新坑（2026-08 无耻混蛋轮；SKILL.md 已满未并入正文，下轮合并时抄入 ㊿ 系列）

① **卫报 2009 老页无 articleBody JSON-LD**——2009 年旧版卫报文章 HTML 无 `"articleBody"` JSON 字段、无 `content__article-body` class（判据：`raw.count('articleBody')==0`），正文在 `<div id="article">` 内的一串 `<p>/<h2>/<h3>` 标签；提取法=定位 `id="article"` → 正则收集 `<(p|h2|h3)[^>]*>...</\1>` → 剥标签+html.unescape+压空白（现代卫报页 JSON-LD articleBody 路径照旧，两版并存，先探测再选路）。
② **卫报直链 404 的老文可用 r.jina.ai 直抓同一 URL 复活全文**——Cox《Inglourious Basterds is cinema's revenge on life》直连返回 "Page Not Found" 页，jina 抓同 URL 一次拿 39KB 全文；404 页与 jina 全文双留档。比 wayback CDX（本轮两次 403）更省事。
③ **源文本自带 "..." 的引文（剧本标题卡字面省略号）**——IMSDb 标题卡原文是 `"ONCE UPON A TIME IN...` + 换行 + `NAZI OCCUPIED FRANCE"`，省略号是源文本一部分；压空白后短语必须含 "..."（`IN...NAZI` 连续），去省略号必假 MISS。判据：先 grep 源文本确认省略号是否在原文里，别默认 "..." 是引文拼接标记。
④ **引文内括号插入语必须保留或分片（㉑/迷魂记轮 ② 的括号变体补强）**——French 引文 `...but are unworthy of them (eg Goebbels) will die in a cinema`：norm 删括号字符但**保留括号内词**，短语写 `unworthy of them will die` 对源 `unworthy of them eg Goebbels will die` 必假 MISS——含插入语的引文要么连插入语直录、要么按插入语分片，不能指望删括号字符。
⑤ **中文长评句内拉丁人名逐字保留（⑭/㊸ 句内混排家族再扩展）**——豆瓣 2807075 该句原文 "放映机仍旧把Shosanna的脸投到滚滚的浓烟上" 用拉丁 Shosanna 而非中译苏珊娜——文档侧按存档字形直录（修文档不修脚本）。
⑥ **孤儿号对账先滤来源表行（雪国列车轮 ③ 的执行细节）**——审计脚本把来源清单表行（`| 研S\d+ |` 开头）算进"正文引用"会掩盖真孤儿号（研S19/20 首轮即被表行掩盖，补正文引用才闭环）——对账前按行正则剔除表行再数正文引用，双向（正文缺号+清单孤儿号）都按滤后集跑。
⑦ **测试侧垃圾条目**：记忆污染短语（"a round for the house"——成片里有、IMSDb 这版剧本里没有）与"中译替代行"（"我要给你一件脱不掉的东西"=剧本英文行的中译）都不该进校验清单——引文必须从交付文档逐字提取（⑬/㊲ 再证），翻译行只校验英文原句。

## 校验会话记录（102 条 0 MISS）

首轮 5 MISS 全为假 MISS/测试侧问题：①括号插入语缺词（新坑④）②标题卡省略号缺失（新坑③）③两条测试侧垃圾条目（新坑⑦）④句内拉丁名（新坑⑤）——修正后全过。定稿前另修一处 write_file/patch 引起的列表行合并（patch 的 new_string 忘带换行导致两列表项并成一行，diff 自查发现并修复）。

## 双文档对账

- 正文引用计数：研习报告 119 处 + 技法卡片 34 处；研S1–S20 全部在正文（非来源表）有引用，无孤儿号、无缺号。
- **对账细节坑**：首轮审计把来源清单表行算进"已引用"集，掩盖研S19/20 孤儿（只在表内）——滤掉 `| 研S\d+` 开头行后再数才暴露（新坑⑥）。

## 诚实声明项（写入文档）

- 任务预设昆汀原话「这是对电影院的情书」（love letter to cinema）**未逐字取证**：The Daily Beast《Tarantino's Love Letter》正文被订阅墙截断（jina 只取到标题+导语，留档 qtar_beast_loveletter.txt），sensesfive 影迷文标题为评论者措辞；正文改用已核实等价原话（昆汀 "In this story, cinema changes the world, and I fucking love that idea!"〔研S8〕+ Ebert "embeds Tarantino's love of the movies"〔研S3〕）。
- IMSDb 流传稿非官方拍摄稿；第四章标题卡缺失；苏珊娜短片法/英语版本差异——均已按层级标注。
