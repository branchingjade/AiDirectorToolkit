# 戈达尔轮（godard-study-2026-08）

> 2026-08-08 布局研习轮（法国新浪潮/跳接）。产出《戈达尔_导演美学卡片.md》+《戈达尔_手法体系深化.md》→ `_work/布局研习-20260808/戈达尔/`（非技能目录）；pages/ 存档 24 个。编号 S1–S20 见卡片附录。

## 来源地图（存档 → 内容）

| 存档 | 内容 | 用途 |
|---|---|---|
| godard_enwiki.txt | 英维主条目（API explaintext 纯文本） | 箴言（girl and gun / beginning-middle-end）/ "As a critic, I thought of myself as a film-maker…" / 奖项 / 各时期 |
| breathless_enwiki.txt | 英维《筋疲力尽》 | 跳接/23 天拍摄/练习本剧本/Rissient"跳接非拍摄初衷"/Decugis/HP5 手持/遗言 dégueulasse/High Sierra 凝视/Monogram 献词 |
| pierrot_enwiki.txt | 英维《狂人皮埃罗》 | "last romantic couple" 自述/开拍前一日写剧本/蓝脸炸药结局/票房 |
| vivresavie_enwiki.txt | 英维《随心所欲》 | 十二表章（"film en douze tableaux"）/Parain 对话/声道中断旁白覆盖/娜娜之死 |
| weekend_enwiki.txt | 英维《周末》 | 科塔萨尔改编/FLSO 食人族/元电影 |
| histoires_enwiki.txt | 英维《电影史》 | 八章 266 分钟/1988–98 |
| petitsoldat_enwiki.txt | 英维《小兵》 | "Photography is truth…24 times a second"（含法文原文）/1963 审查后公映 |
| nouvellevague_enwiki.txt | 英维 French New Wave | 运动背景 |
| pov_raskin.txt | P.O.V. 期刊 Raskin《跳接的五种解释》**（原始 HTML，未转文本）** | 戈达尔 Gordon Gow 访谈整段转引（合同 90 分钟/掷硬币删四分钟）/Guillemot "true respiration"/五种假说 |
| soc_weekend_essay.txt | SoC 2017《周末》影评 | "所谓最长移动镜头"300 米轨道/字卡打断/Fin de conte→Fin de cinéma/"ANAL YSE" |
| soc_dossier_intro.txt | SoC Issue 100 导言（Daniel Fairfax） | "it is the forms that think"/1971 摩托车事故/"last of the Mohicans" |
| soc_godard_2001_text.txt | SoC 2001 会议报道（For Ever Godard） | 晚期作品（The Old Place 等）状态 |
| criterion_526.txt | Criterion（经 Wayback）《Breathless Then and Now》 | Numéro Deux/"second first film" |
| rosenbaum_1980_interview.txt | Rosenbaum 网站·Soho News 1980 访谈 | "landing on the earth of story"/Schrader 轶事/"I'm not against cities"/6X2/莫桑比克 |
| rosenbaum_1996_interview.txt | Rosenbaum·Film Comment 1998 访谈 | Histoire(s) 制作经过/"increasing solitude"/"obsessively concerned with beauty" |
| guardian_obit_text.txt | Guardian 讣告 2022 | 生平/Karina years/Dziga Vertov"make films politically"/Pierrot 原色/Fuller 台词/箴言两条/Histoire(s) 蒙特利尔起源 |
| guardian_champetier_text.txt | Guardian "remembered by" 系列·摄影师 Caroline Champetier 回忆 | **"he didn't believe in characters, he only believed in actors responding to his directing"**/戈达尔-特吕弗决裂/三派分立 |
| newyorker_brody.txt | New Yorker·Richard Brody 追思 | 跳接"cymbal crash"/协助自杀去世/录像时期与 Histoire(s)/唯戈达尔把电影做成活的批评 |
| filmreference_text.txt | Film Reference 档案 | 完整片目时间线/Langlois 事件/Sonimage/Rolle/《芳名卡门》金狮 |
| godard_montage_en.txt | O'Reilly《Fine Cuts》第 1 章（Wayback 存档） | 戈达尔 1956《蒙太奇，我的美丽忧愁》英译节选/"montage is above all an integral part of mise-en-scène…"/"If direction is a look, montage is a heartbeat" |

## 新通道（本次实测，可复用）

1. **jonathanrosenbaum.net = 导演访谈档案通道**：Rosenbaum 把自己发表过的导演访谈全文公开挂站（本轮两篇：1980《Soho News》"Catching Up with Godard"、1998《Film Comment》"Godard in the Nineties"）。**导演轮先查 Rosenbaum 是否采访过目标导演**——`site:jonathanrosenbaum.net <导演名> interview`，他采访过的导演（戈达尔/侯孝贤/…）都是一手访谈金矿，免费全文直抓（curl 带 UA 即可，无壳）。
2. **Guardian "remembered by" 系列 = 同事回忆一手通道**：导演去世后 Guardian 请合作者写回忆（本轮摄影师 Caroline Champetier），工作方法原话密度高（"不相信人物、只信演员反应"），且常带私人细节（煎蛋卷与啤酒度日）。抓讣告时顺手抓同系列回忆文章。
3. **Criterion 403 时 Wayback availability API 带 timestamp 定位快照**：`http://archive.org/wayback/available?url=<精确URL>&timestamp=2022` 返回 closest 快照 URL（本轮 posts/526 → 20230117 快照秒回全文）；同一站另一篇 posts/525 返回 None（无快照）——**availability 是精确 URL 的第一顺位，失败再走 CDX 通配**。
4. **O'Reilly 图书章节目录页经 Wayback 可取书内全文节选**：`oreilly.com/library/view/.../xhtml/09_Chap1.xhtml` 直连/jina 均 403，wayback 快照含《Fine Cuts》第 1 章正文节选（戈达尔 1956 论文英译）——**学术书章节 URL 已知时 wayback 直抓，免找扫描件站**。

## 新坑

1. **原始 HTML 存档直接参与引文校验 → 假 MISS**：pov_raskin.txt 是 25KB 原始 HTML（从未转文本），`"systematically cut out whatever could be cut" in 存档` 直接比对全 MISS——HTML 标签（`<i>`、`<p>`）把短语截断。校验脚本加载器必须**按存档形态归一**：纯文本/已转 `_text.txt`/原始 HTML（先剥标签+html.unescape+压空白再入语料），或三态都建变体。⚠️ 与 ⑰（豆瓣壳 vs jina 档映射）互补：⑰ 管"壳文件没正文"，本条管"正文在但被标签打断"。
2. **英文引文弯引号（’）同样假 MISS**：`"I'm not against cities"` vs 存档 `"I’m not against cities"`（U+2019）——norm 的弯→直引号归一对英文同样必要（中文轮常只注意中文弯引号）。
3. **SoC Great Directors 专条并非人人都有**：戈达尔专条（Sterritt）2002 URL 404、站内搜索未命中——**别假定大师级导演必有 GD 专条**；用 SoC 2022 专题专辑（Issue 100 "Forms That Think"）或会议报道替代，诚实声明注明。
4. **web_extract 工具后端是搜索-only（DDG）时不可用**——本环境直接改用 urllib/curl 抓取 + 上述回退链，全程无碍。环境相关，勿记成"web_extract 坏了"。

## 诚实边界（本轮未取证到）

- 未逐帧看片（所有成片描述引自来源）。
- "Le travelling est une affaire de morale"（移动镜头是道德问题）无一手出处 → 弃用。
- 《周末》堵车长镜秒数（坊间 8 分钟）未取证到 → 只写"SoC 所谓最长移动镜头+300 米轨道"。
- 《蒙太奇，我的美丽忧愁》法文原版未取到（filmfilm.eu 403 且无 wayback 快照），仅英译节选。
- Criterion posts/525 无 wayback 快照；SoC Great Directors 戈达尔专条 404。
- 跳接成因五口径（Raskin 综述）：本文采戈达尔本人口径并如实标注为"其一"。
