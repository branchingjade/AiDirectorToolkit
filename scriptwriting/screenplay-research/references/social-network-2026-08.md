# 《社交网络》剧本获取与研习记录（2026-08-06）

## 来源
- **IMSDb（主用）**：https://imsdb.com/scripts/Social-Network,-The.html — HTTP 200，320KB HTML，scrtext 可提取；`Social-Network.html` 是软 404 导航页（7.8KB，无 scrtext）
- **Script Slug（对照）**：https://www.scriptslug.com/script/the-social-network-2010 → PDF 直链 assets.scriptslug.com/live/pdf/scripts/the-social-network-2010.pdf（164 页，拍摄稿）

## 版本差异（重要）
IMSDb 稿 = **May 28, 2009 早期稿**（稿头 "May 28, 2009"）：
- 无上映版名句 "You have part of my attention"（仅拍摄稿 L3910）
- 结尾 Marylin 判词 "You just want to be"（早期稿 L10651）；拍摄稿/上映版 "You're just trying so hard to be"（slug L8713）
- 片尾 TITLE 卡：早期稿 180 million members / 15 billion（L10693-10694）；拍摄稿 500 million / 25 billion（slug L8739）
- "I'm CEO...Bitch" 两稿都有（早期稿 L8086、拍摄稿 L8572）
- 结论：索金片两稿差异大，引用上映版台词必须回拍摄稿 grep，报告必须标版本

## 文本层噪声模式（IMSDb 版）
- 空格注入：`f acebook-pics`、`want: to . be`
- 标点噪声：`blow. jobs`、`an. 800`、`work, station`
- 人名变形：`MARK S`、`MART`、`MARX'S`、`BRICA`、`T'RICA`、`ERICA OF`
- 场标题 OCR：`NIGL'3T`=NIGHT、`CO&PUTER`、`TNT_`=INT.、`INT..`、`INT. 66 - NIGHT`（66 是 Tribeca 餐厅名，不是解析错误！）
- 省略号 `..`/`...` 混用、引号全角/半角混用

## 格式方言
- 场景头：`INT. CAMPUS BAR - NIGHT`（**无场号行首**），156 处
- 场号：`2.`/`3.` 独立成行，落在上一场对白之后（Final Draft 提取错位），101 处
- 转场：`CUT TO:` 大量使用（蒙太奇骨架）；`TITLE:` 时间戳（"8:13 PM"）；音乐进场写成动作（"Love of the Common People" CRASHES IN----）
- 节奏标点：`(BEAT)`/`(PAUSE)`/`(MORE)`/`(CONT'D)` 密集

## 结构行号图（双诉讼框架，行号对应提取文本）
- 开场酒吧分手：L37-573（0.3%-5.3%）
- 博客+Facemash：L626-1458（"I need the algorithm" L988）
- 首场作证（闪前框架进入）：L1458-1581（"It's three years later" L1460、"flash-forward scenes" L1475）
- 双作证室对切最密集：L2272-3227（FIRST DEPOSITION ROOM=Saverin 案 Gretchen / SECOND=Winklevoss 案 Gage）
- Sean Parker 登场：L5623-5822（Napster 反转 L5766-5785）
- "A million dollars isn't cool"：L6939-6958
- "I'm CEO...Bitch"：L8070-8091
- Eduardo 退场 "I like standing next to you"：L10006-10008
- 结尾回环 + TITLE 卡：L10600-10716（"Farm animals?" L10622 三重回收点：L1922/L5195/L10622）

## 研习产出
- 报告：film-suite-research/研习报告/社交网络_研习报告.md
- 卡片：film-suite-research/技法卡片源稿/社交网络_技法卡片.md（8 张：快节奏对白三件套/双作证室对切/问答=闪回触发器/对白即行动/信息延迟反转/修辞三拍/动机独白/结尾回环）
