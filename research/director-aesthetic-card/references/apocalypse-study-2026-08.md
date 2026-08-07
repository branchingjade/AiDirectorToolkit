# 《现代启示录》单片研习轮来源地图（2026-08，科波拉第二代表作）

> 产出：研习报告/现代启示录_研习报告.md + 技法卡片源稿/现代启示录_技法卡片.md。导演本体此前仅教父轮（references/godfather-coppola-study-2026-08.md），本片零存量。校验脚本 scripts/verify_apocalypse_citations.py：**132 引文 0 MISS**。

## 存档对照（pages/cop_apoc_*，[研S#]）

| 编号 | 文件 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | cop_apoc_enwiki_raw.txt (144KB) | 英维 Apocalypse Now raw | 制作史/戛纳金句/238 天/结局即兴（渔王）/声音设计 |
| 研S2 | cop_apoc_zhwiki_raw.txt (47KB) | 中维「现代启示录」raw（**简体条目名直存**） | 繁体版制作史/抵押教父利润/白兰度黑衣只拍脸 |
| 研S3 | cop_Apocalypse_Now_Redux.txt | 英维 Redux 条目 | 法国种植园/「biggest nothing in history」/Storaro 三色法 |
| 研S4 | cop_Hearts_of_Darkness__A_Filmmaker_s_Apocalypse.txt | 英维 HOD 纪录片条目 | 纪录片史/「we went insane」采样 |
| 研S5 | cop_Francis_Ford_Coppola.txt (169KB) | 英维科波拉主条目 | Apocalypse When?/双金棕榈/Ebert 长引/Sound Designer 首署名/S&S 2022 #19 |
| 研S6 | cop_apoc_ebert_1979.txt | Ebert 1979-06-01 首评（jina live 直抓） | 战争即地狱/教父对照/直升机段并置 |
| 研S7 | cop_apoc_ebert_great1999.txt | Ebert 1999-11-28 Great Movies 重评（**wayback=英维 ref 的 archive-url**） | 河流期待/库尔兹声音/「The End」首尾/结局误解澄清 |
| 研S8 | cop_apoc_guardian_sheen2001.txt | 卫报 2001-11-02 马丁·辛访谈（**作者署名未取证到**） | 酒店开场自毁戏/都朗桥雨戏/「damaged perspective」 |
| 研S9 | cop_apoc_gq_coppola2010.txt | GQ 2010 Devin Gordon 访谈 | 没有结局/剪 20-30 分钟/加州战争/霍珀角色即兴/教父编号/Transformers 3 |
| 研S10 | cop_apoc_script_imsdb_1975.txt (174KB) | IMSDb **1975-12-03 拍摄前稿**（293 编号场景） | 稿版结局（背库尔兹上船+遗孀尾声）/Charlie don't surf=威拉德 |
| 研S11 | cop_apoc_script_redux.txt (262KB) | Script Slug Redux 剧本 PDF（pdftotext） | napalm 名台词首次成文/法国种植园/「The horror….the horror. He dies.」 |
| 研S12 | cop_apoc_rexxar_reviews.json | 豆瓣 rexxar 长评列表（537 篇，subject 1292260） | 选题排序依据（1101654=2896 有用居首） |
| 研S13-25 | cop_apoc_review_*.txt | 豆瓣 13 篇长评 | 1101654 剃刀边缘（六段疯狂/全景削弱残酷/库尔兹打光）、1097799 湄公河上的公路片（公路片置换/五人物谱/双叙事线）、13268511 **中译剧本全本**（陈笃忱译 30K 字，编者按=《世界电影》刊物）、12125354 默奇剪辑（95:1 片比/八机同拍/1.47 剪接）、5369525 自由的尽头（金枝祭司）、7833105 库尔茨的手表、2277802 导演评论音轨摘录、12794448 教父对照、1107890 康拉德对照（先知/后知/不知不觉）、12888268 深焦逆历史奥德赛、9294331 明暗线、5678728 恐惧论、1045838 生态存档 |

## 核心发现（写入报告的）

1. **剧本 vs 成片四断裂**：1975 稿结局=威拉德背垂死库尔兹上船+遗孀尾声（「He spoke of you, ma'am.」撒谎）→成片=水牛献祭中砍刀弑神+土著跪拜；兰斯稿中死/片中生；Charlie don't surf 说话人威拉德→基尔戈；napalm 名台词两稿无。
2. **河流=精神之旅容器**：中译剧本「河流宛如伸进战场咽喉的一条粗大的输电线路……它的顶端径直插入库尔兹的脚下」；公路片模式置换（河=路、艇=车）。
3. **库尔兹缺席结构**：档案录音→祭坛剪影→读报哲学家→临终低语四次递进；Ebert「The river journey creates enormous anticipation about Kurtz, and Brando fulfills it」。
4. **制作史诗**：238 天/台风毁 40-80% 布景/谢恩心脏病/白兰度超重无结局/95:1 片比/抵押教父利润/Apocalypse When?/「My film is not about Vietnam, it is Vietnam」。
5. **教父两极**：黑帮秩序（仪式化暴力/关门）vs 战争混沌（美学化暴力/瓦格纳）；GQ 自述 Godfather I&II 编号是他开的头。

## 渠道实测

- **豆瓣 subject id**：DDG-jina `site:douban.com/subject 片名 导演` 得候选 → rexxar `/v2/movie/<id>` 逐个验证（返回 title/year，404=错 id）——4 候选 1 命中 3 404（与蓝丝绒轮同端点互证）。
- **中维条目名**：简体「现代启示录」直存（无重定向非繁体）——titles 探测简体命中。
- **Ebert**：1979 首评 live jina 直抓（reviews/apocalypse-now-1979 非 great-movie slug）；1999 重评 jina 429 → **英维词条 Critical response 段 ref 的 archive-url 快照（20081216072521 id_）**一次到手 8.8KB。
- **卫报**：URL 从 enwiki Casting 段 ref 挖（typhoons-binges...）；byline 空（HTML+API 双查无果）→ 诚实标注。
- **剧本双稿**：IMSDb 页面含 scrtext 真正文（1975-12-03 稿）；Script Slug PDF 直链 assets.scriptslug.com/live/pdf/scripts/<slug>.pdf + pdftotext（**同片两稿不同，IMSDb=拍摄前稿、Script Slug=Redux 后配稿**）。
- **jina 限流**：连续请求触发 429（retryAfter 2s），错峰重试；429 时 wayback archive-url 第一顺位兜底。

## 校验记录（132 引文 0 MISS）

- **zhconv 替代手写繁简表**：`zhconv.convert(存档,'zh-cn')`（本机已装）比手写 maketrans 表稳（手写表漏 為/擔/種 等字）。
- **strip_wiki 判定条件坑**：cop_Francis_Ford_Coppola.txt 不带 `_raw.txt` 后缀 → 按后缀判断跳过剥壳，`[[Harvey Keitel]]` 残留假 MISS；判定改 `'_raw.txt' in fn or 'Coppola' in fn or 'Redux' in fn or 'Hearts' in fn`。
- **译文标注纪律**：中文引号句分三类——存档原文直引（豆瓣/中维）、自译（必须紧跟英文原文并核验）、英源译文（标注）；文档诚实声明写清规则。
- **译名并存**：豆瓣长评「史华特/古华特/柯兹」vs 通行「威拉德/库尔兹」——引用长评原句保留其译名并加注。
- 假 MISS 修法：引文跨行/书名号/弯引号/繁简（zhconv）；「My river...」句被括号舞台指示打断→换短短语。

## 未取证清单

- Criterion essay（华纳/狮门版权片，未入收藏，按版权判断未做站内负面取证）；卫报访谈作者署名；「白兰度三周即兴」深焦单源转述；科波拉渔王方案自述原文；镜头级量化（直升机段落镜头数）。
- 片长双口径：70mm 147 分钟 vs Redux +49 分钟（GQ）vs +53 分钟（Redux 条目/卫报）——并存不统一。
