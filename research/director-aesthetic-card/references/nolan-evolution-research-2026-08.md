# 诺兰手法体系深化轮来源地图（2026-08，第十八轮）

产出：《诺兰_手法体系深化.md》（技法卡片源稿/，25KB）+ 校验脚本 verify_nolan_deep.py。**零新抓取**：24 个 nolan_* 存量存档全复用，仅 grep 取证。

## 存量盘点（开局）

- `pages/` 24 个 nolan_* 存档：主条目/风格专条/7 部单片维基（Inception/Interstellar/Dunkirk/Oppenheimer/Tenet/TDK/Prestige/Memento）+ Ebert 3 篇（memento/inception/darkknight wayback）+ Guardian 2014 + The Talks 2023 + 豆瓣盗梦条目页 + 百度百科失败壳（nolan_baike_probe.html=安全验证）。
- `技法卡片源稿/`：《诺兰_导演美学卡片.md》（S1-S16）、记忆碎片_技法卡片.md、黑暗骑士_技法卡片.md 已落盘；**盗梦/星际技法卡片+研习报告、库布里克_手法体系深化.md 写作时均未落盘**。
- `memento_script.txt` 在 film-suite-research/ 根目录（非剧本原文/）；darkknight_slug.txt 在 pages/。

## 关键引文位置（存档→引文，全部 28 条 0 MISS 核验）

- nolan_wiki_Cinematic_style.txt：诺兰实拍原话 "I believe **in an absolute difference** between animation and photography"（注意措辞是 believe in，非 believe there is，主卡片译文对应此句）；Lyttelton "fatherhood has been at the emotional heart of almost everything he's made, at least from Batman Begins onwards"；VFX 数据 "620, 500, and 850 visual-effects shots"；主观视点原话 "subjective perception of reality, that we are all stuck in a very singular point of view"。
- nolan_wiki_Inception.txt：旋转走廊 "It was like some incredible torture device; we thrashed Joseph for weeks..."；"it rotated a full 360 degrees"；层级时间 "Time on each layer runs slower than the layer above...music-synchronized 'kick'"。
- nolan_wiki_Interstellar_(film).txt：时间膨胀 "decades have passed in Earth-years" / "extreme time dilation he experienced near Gargantua"；tesseract "a higher-dimensional tesseract where time is 'physical'"；一页纸作曲 "a single page that told the story of a father leaving his child for work"；黑洞可视化 "Thorne collaborated with Franklin and a team of 30 people at Double Negative, providing pages of deeply sourced theoretical equations to the engineers, who then wrote new CGI rendering software based on these equations"。
- nolan_wiki_Dunkirk_(2017_film).txt：三线 "The story is told from three perspectives—land (one week of action), sea (one day of action) and air (one hour of action)"。
- nolan_wiki_Tenet.txt：747 "purchasing a Boeing 747 proved more cost-effective"；"objects with 'inverted' entropy that move backward through time"；"temporal pincer movement"；"what's happened, happened"；Neil "inverts to return to where he sacrifices himself in the hypocenter"。
- nolan_ebert_inception_wb.txt："Here is a movie immune to spoilers"；"when Nolan left the labyrinth, he threw away the map"。
- 本地卡片/剧本：[卡记忆碎片] 开场 L17-31/显影 L6554-6558/环形 L53-57+L7278-7287；[卡黑暗骑士] 缅甸寓言 L2920-2941/小丑独白 L5351-5362/双船 L5957-5967。

## 预设修正（写入诚实声明）

1. 「反派哲学演变（小丑混沌 vs 更抽象的时间敌人）」→ 取证为三段链：人格化（小丑）→人性+法则（曼恩/时间膨胀）→非人格法则（未来人+熵）。**星际穿越的"时间"是环境法则不是反派**（夺走 23 年的是引力），与信条"熵"不可混同。
2. 「情感内核显性化（早期结构优先→后期情感驱动）」→ 修正为"从隐性（结构内）走向显性（创作起点）"——《记忆碎片》的失忆体验本身就是情感装置，非后期才出现。

## 未取证清单

- 「米勒星球一小时=七年」精确倍率：维基存档无此数字，只有 "decades have passed"（主卡片 S6 同源，深化文档按通行说法标注+诚实声明注明）。
- 百度百科被安全验证拦截（沿用主卡片结论）。
- 库布里克深化文档未落盘→vs 节经其主卡片转引（内部编号 [W-K]/[W-2001]/[E-SH] 保留原样）。

## 编号纪律实测

- 深化文档正文 [S#] ⊆ 主卡片 S1-S16（`grep -o '\[S[0-9]*\]' | sort -u` 对账，0 越界）。
- [卡盗梦]/[卡星际] 双轨：存档本身在主卡编号表内（S3/S6），前缀只作"同批产物未落盘"占位；附录登记"证据直接取 pages/ 存档，落盘后可互引"。
- 转引 [卡库布里克·W-K] 等保留对方原编号，不冲突。

## 校验脚本要点（verify_nolan_deep.py）

- 每条短语带 expect_keys（预期存档文件名关键词），命中但文件不符 → "OK? wrong-file" 警示（抓归属错挂，站台轮 S12/S13 同型）。
- norm 管道：迭代剥 [[A|B]] 链接→剥 ''→剥 {{}}→剥 jina markdown 链接→压空白→弯引号统一→全角括号转半角→删《》→lower。
- 兜底：去引号（strip_quotes）双侧再比一次；存档 glob 覆盖 nolan_*.txt + nolan_*.html。
- 28 条 0 MISS 定稿。

## 渠道备忘

- 本轮回扫 `ls 技法卡片源稿/ | grep -E '诺兰|盗梦|星际|库布里克'` 确认并行产物未落盘 → 按小津轮先例 [卡X] 登记存档本身、按吴宇森轮先例回退主卡片转引链（两条先例的组合场景）。
- 深化文档结构：0 路线归类（4 线）→ 1 演变脉络（4 表：非线性时间/实拍执念/反派哲学/情感内核，每阶段独立证据）→ 2 工具箱（4 件套泛用+AI 提示词）→ 3 vs 库布里克 → 4 诚实声明 → 5 附录。
