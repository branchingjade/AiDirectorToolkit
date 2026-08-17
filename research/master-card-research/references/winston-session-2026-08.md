# Stan Winston 研习轮记录（实体特效轴第一轮，2026-08-09）

产出：《温斯顿_制作大师卡片.md》→ `_work/v2-大师卡-20260809/温斯顿/`（含 pages/ 13 个存档）。

## 来源清单（13 存档，编号 S1-S11 中 S7/S9 各含双文件）

| 编号 | 存档文件 | 来源 | 层级 |
|---|---|---|---|
| S1 | stanwinston_wiki.txt | 英文维基·Stan Winston 主条目 | 二手 |
| S2 | stanwinston_school.txt | Stan Winston School 官网传记页（Cameron 悼词/"best for the shot"/Hybrid） | 官方（准一手） |
| S3 | winston_cinefantastique1993.txt(+.html) | Cinefantastique 1993-08 专访（Steve Biodrowski）——经 JP 维基脚注挖到 Wayback 存档 URL 后直连 | **一手** |
| S4 | jp_wiki.txt | 英文维基·Jurassic Park (film)（脚注引 Shay&Duncan 1993 制作书） | 二手 |
| S5 | t2_wiki.txt | 英文维基·Terminator 2: Judgment Day | 二手 |
| S6 | t2_sfx_wiki.txt | 英文维基·Special effects of Terminator 2: Judgment Day（脚注引 Duncan 1991/2006 书） | 二手（转引一手书） |
| S7 | t2_school_blog.txt | SWS 博客《T2 T-1000 Effects》(2023-02-12)——整段引《The Winston Effect》书中温斯顿原话 | 博客转引书中原话 |
| S8 | t2_vulture_oral.txt | Vulture 2015-07-01 T2 液态金属口述史（Kenny Herzog；温斯顿已故未受访） | 同事口述 |
| S9 | aliens_wiki.txt | 英文维基·Aliens (1986 film) | 二手 |
| S10 | predator_wiki.txt | 英文维基·Predator (film) | 二手 |
| S11 | t1000_wiki.txt | 英文维基·T-1000 | 二手 |

## 关键 URL 模式（可复用）

- SWS 传记页：`https://www.stanwinstonschool.com/artists/special-effects-character-creator-<人名>`
- SWS 博客（引书原话）：`https://www.stanwinstonschool.com/blog/<slug>`（T2 篇 slug 为 `t2-judgement-day-t1000-fx`）
- 老杂志专访经维基脚注→Wayback：`https://web.archive.org/web/<ts>/http://cinefantastiqueonline.com/1993/08/interview-stan-winston-on-making-jurassic-parks-full-size-dinos-live-and-breath/`（JP 维基脚注 237 直接给出；Wayback 被 jina 永久封禁→直连 curl + Chrome UA；取回 99KB HTML → python 剥导航壳 + 按引号切句提取）
- Vulture 口述史：`https://www.vulture.com/2015/06/oral-history-of-emt2ems-liquid-metal-effect.html`
- 维基特效专条：`https://en.wikipedia.org/wiki/Special_effects_of_Terminator_2:_Judgment_Day`

## 已验证引语锚（grep 全过，卡片内引）

- S2: "What I came to admire more than his artistry and technical wizardry, was Stan's most amazing gift: the ability to lead a team."（Cameron）；"Winston never professed a preference for any specific technique; rather, he'd insist on using whatever method was 'best for the shot'"
- S3: "Steven [Spielberg] wanted to do live action as much as possible"；"Our job was to create the most realistic dinosaurs that anyone has ever seen"；"They had to act"；"we had to create saurian Robert DeNiros and Jack Nicholsons"；"Danny DeVito and Arnold Schwarzenegger are both men"；"performance-capturing Waldo"；"It worked beautifully"；"not all Raptors, for example, are created equal"；"maintained a legitimacy to all of the available knowledge"；"the most perfectly coordinated movie I've ever worked on"；"Phil's a dinosaur himself"
- S7: "Nobody realized that was a puppet. Everybody assumed that was really Robert Patrick and that the hole in his head was done with CG. But that was a puppet that we built."（Donut Head）；"Everybody who looks at Terminator 2 now thinks that it was all done with CG -and that's fine with me... But nearly all of those liquid-metal-man shots were done using our puppets. We created 300 separate effects for Terminator 2."；Rosengrant "in-camera magic tricks"
- S8: "Hasta la vista, baby" 碎裂镜头=温斯顿模型（Keegan）；"100-year-old techniques that work to this day"（Warren Jr.）；"when it was no longer putting that surface over real human beings – that's when it rarely looks real, no matter how good you are"（Warren Jr.）；汞材质："mercury doesn't look real in real life"；"it's the whole package that sells it"（Keegan）
- S4: "After we created it, they discovered it."（迅猛龙玩笑）；"the closest I've ever been to a live dinosaur"（Horner）；Queen 比恐龙容易（"it was lightweight and did not have to look like a real animal"）
- S3 工艺：1/5 模型切片放大（"like the hull of an airplane"）；T-Rex 飞行模拟器基座；"we needed to be able to take direction on a set"（Waldo 动机）

## 核心论证数据（实体 vs CG 分工）

- T-1000 银幕 15 分钟 = 实体实拍 9 分钟 + CG 6 分钟（S11）
- T2：CG 42–43 镜头 vs 实体 50–60；特效总预算 $15–17M、T-1000 独占 $5M；150 总特效镜头（S5）；T-1000 相关 52 镜头（S6）
- "For budget reasons, Cameron assigned as many T-1000 effects as possible to Winston's makeup team to avoid costly computer graphics"（S6）——预算反推分工
- JP：恐龙银幕 15 分钟 = 实体 9 分钟 + CG 6 分钟；全片 CG 仅 52 镜头（S4）；T-Rex 20ft/9000lbs/40ft
- Aliens：12 套异形服；女王 14ft 聚氨酯泡棉木偶、2 人控臂/4 人控头/液压首次使用（S9）
- 吉尼斯：T-1000 = "first major blockbuster movie character generated using computers"（S5）

## 本轮踩坑（已回写 SKILL.md）

- **429 重试覆盖好文件**：`curl -o t2_wiki.txt` 重试时被 jina 429（242B JSON 错误体）覆盖了之前抓好的 368KB 正文——重试同名前先验当前文件完好性，或写新文件名。
- jina 429 特征与恢复：`{"data":null,"retryAfter":1,...RateLimitTriggeredError}`，sleep 15-20s 重试可恢复。
- Wayback 经 jina 返回 403 AbuseAlleviationError（blocked until 时间戳）——直连 curl 即通。

## 诚实声明要点（本轮）

未逐帧看片；温斯顿 2008 年去世→T2 口述史（2015）无本人受访，本人原话以 S7（引书）与 S3（1993 杂志专访）为准；「genie out of the bottle」轶事流传但未抓到《The Winston Effect》原文文字版→不转引；"Let's shoot for the first computer-generated man" 维基标 attribution needed；数据口径并存（150 vs 52 镜头等）。
