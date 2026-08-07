# 芬奇深化轮来源地图（fincher-evolution-2026-08）

任务：产出《芬奇_手法体系深化.md》——跨作品矩阵三线（罪案解剖/身份操控/群像叙事）。**零存量全新建档**：起步时 pages/ 无任何 fincher_*/f_* 存档。

## 产出
- `技法卡片源稿/芬奇_手法体系深化.md`（203 行 / 40.6KB，6 节：3 创作线 / 3 演变链 / 8 工具箱 / vs 希区柯克与诺兰 / 诚实声明 / 附录）
- `verify_fincher_deep.py`（73 条引文短语 0 MISS）

## 存档清单（S1-S7，全部 enwiki raw，新抓）
| S# | 文件 | 关键内容 |
|---|---|---|
| S1 | fincher_David_Fincher_raw.txt | 风格方法段全部原话：take 17 论/50 takes/99 takes、Handheld stranglehold、sinister cloaks itself、perverts 论、desaturated 蓝绿黄配色、Swiss watch 剪辑、Red 数字机偏好、Krutnik 内驱力转引 |
| S2 | fincher_Fight_Club_raw.txt | unreliable narrator、分镜隐瞒纪律（不同框/无过肩/单帧插入）、little devil on the shoulder、烟疤镜头自我指涉、twist 信任额度原话、myopic framework、no solution 原话 |
| S3 | fincher_Se7en_raw.txt | 四帧 Tracy 插入代偿盒子、切黑屏意图、twist ending 影史地位、试映反应、bleach bypass、13 稿/盒子结局保卫战、motivated cut、标题序列设计创新、盒子实物=shot bag+wig |
| S4 | fincher_Gone_Girl__film__raw.txt | 日记伪造情节（fabricated diary entries）、seizing the narrative initiative、Fincher 指导 Flynn 原话、unreliable narrators 分类 |
| S5 | fincher_The_Girl_with_the_Dragon_Tattoo__2011_film__raw.txt | 全片 RED MX、冬季=沉默角色（Cronenweth）、shadows/flaws/reality、victim-turned-vigilante、wish fulfillment 原话 |
| S6 | fincher_Zodiac__film__raw.txt | 18 个月独立调查、police reports 为准原话、无解结局动机、posthumously 责任原话、Viper 数字机、McMenamin 法医语言学、Fuller/Ansen 跨片对比 |
| S7 | fincher_The_Social_Network_raw.txt | 双作证室框架、Sorkin three versions 原话×2、Ebert 原话、Morgenstern 不可尽信、ScreenCrush spiritual sequel、Esquire Citizen Kane |

## 重定向探测（enwiki）
- `Fight Club (film)` → 116 字节 `#REDIRECT [[Fight Club]]`（去消歧后缀）
- `Se7en` → 169 字节 `#REDIRECT [[Seven (1995 film)]]`（风格化名→真实条目）
- 探测法：`action=query&list=search&srsearch=<片名+导演>` 拿真实标题后重抓

## 关键证据位置（后续轮次复用）
- **信息差操控进化链四节点**：「藏→骗」——S3 四帧 Tracy 插入（盒子内容代偿，观众与角色同瞒）→ S2 分镜纪律+单帧插入（剪辑隐瞒）→ S7 三版本并置（版本歧义，不裁决）→ S4 日记假叙述（主动撒谎）。头号演变链，直接对接《消失的爱人_技法卡片》[研S#]（并行轮已落盘，gg-study-2026-08.md）。
- **线定义直接文献新渠道**：S6 Fuller（Sight & Sound 2007）同一篇评论直接对比七宗罪/十二宫/搏击俱乐部谱系（"Zodiac is considerably more adult than both Seven... and the macho brinkmanship of Fight Club"）+ Ansen（Newsweek）"withholds the emotional and forensic payoff"——深化轮线定义优先扫「同一篇评论里对比导演多部片」的批评家段落，比自行归纳线定义更有力。
- **跨线互接**：S7 ScreenCrush "spiritual sequel to Fight Club"（群像线承接身份线的批评家证据）。
- **vs 节悬念三系**：希区柯克=视点/知情（观众先知），诺兰=结构/理解（观众=角色），芬奇=信任/裁决（观众被骗是默认配置）——三方转引链均已在本文完成。

## 校验新坑（㊿ 芬奇轮五例，SKILL.md 校验节有全文）
① enwiki raw 全文 JSON 转义（`\"` `\'`）strip 第一步先解壳（首轮 13 条假 MISS 根因）
② 链接剥壳循环上限 8→while+500（100KB+ 文章剥不完，`[[two shot]]s`→"two shot s" 签名）
③ `{{Cquote|...}}`/`{{Quote|...}}` 剥模板前先提取入 kept 池（㉛ 同族变体）
④ 斜体剥除后残留「标点前空格」→ norm 补 `re.sub(r'\s+([,.;:!?])', r'\1', s)`
⑤ 并行轮同文存档容差（expect 列双文件名命中，109116==109116）

## 并行轮存档（共享 pages/ 中途出现）
- `fincher_fc_*` 20+ 档（并行《搏击俱乐部》轮：fc_enwiki_raw/fc_cinefex/fc_ebert/fc_imsdb/fc_script_raw/fc_review_*/fc_crit_*/fc_interviewmag）；fc_enwiki_raw 与自抓 S2 同字节同文，验证按同文容差处理，附录登记并行副本。
- 并行《消失的爱人》轮产物已落盘：`技法卡片源稿/消失的爱人_技法卡片.md` + `references/gg-study-2026-08.md`（其 [研S1-18] 含剧本行号级证据，深化轮日记欺骗链可与其互引）。

## 未取证清单
- 各片镜头数/均镜时长无量化数据（仅表演数据：50/70/99 takes）
- Fight Club "I am Jack's..." 台词系列（无剧本存档，仅维基剧情转述）
- Gone Girl 日记闪回的具体镜头呈现方式（逐镜头证据；仅情节事实+芬奇指导原话）
- Social Network 99 takes 具体场景归属
