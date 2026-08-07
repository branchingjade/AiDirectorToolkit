# 《两杆大烟枪》(Lock, Stock and Two Smoking Barrels, 1998) 抓取记录 2026-08-06

## 来源与抓取

- **IMSDb 双 URL 全灭**：`imsdb.com/scripts/Lock-Stock-and-Two-Smoking-Barrels.html` 与 `,-The.html` 都是 7,785 字节空壳（软 404，grep scrtext 仅 1 命中）——又一个「多 URL 都 200 但都是壳」案例（同款：Rashomon/Seven-Samurai）。
- **Script Slug 可用**：页面 `https://www.scriptslug.com/script/lock-stock-and-two-smoking-barrels-1998`（125KB，grep 出 PDF 直链），PDF `https://assets.scriptslug.com/live/pdf/scripts/lock-stock-and-two-smoking-barrels-1998.pdf`（90KB）。
- **⚠️ 文本层是 SFY 遗产**：PDF 文末残留水印 "All movie scripts and screenplays on Screenplays for You site are intended for fair use only." —— Script Slug 托管的这个 PDF 文本层实为已死站 Screenplays for You 的旧抓取。**识别法：pdftotext 后 tail 看水印**。今后对 Script Slug PDF 都要跑这一步。

## 版本

- 标题页 "Final script by Guy Ritchie"（流传终稿），**含 9 处 "Cut from completed film" 标记**（L33/221/294/634/1041/1114/1439/1897/3725）→ 稿 ≠ 成片。
- 本稿**无成片"四人组抢赌局"戏**（grep mask / rob the game 零命中）——四人组实际直接伏击隔壁 Dog 家。稿vs成片差异表是分析产出的一部分。
- 稿内 Christie's（L353，Harry 持拍卖册）与 Sotherby's/Sotheby's（L4276，结尾）并存，拍卖行名不一致，按原文保留并标注。

## 文本层噪声（pdftotext 后，清洗时记录）

- 场景标题：`ED AIVD BACON'S HOUSE`(AND)、`MGHT`(NIGHT)、`SOLARiUM`、`SPLTT SCREEN`、`SLDANES'`
- 人名/角色：`Torn`=Tom、`HATCHER`=Hatchet、`CRUOPIER`=Croupier；场标题误挂角色名（`INT. HATCHET HARRY'S OFFICE - DAY EDDY`）
- 单词：`ftngernails`=fingernails、`based an`=based on（疑原稿如此，标 [sic] 保留）、`mare`=more（疑原稿）
- 稿内印刷页码行（20/55/56/58...）混在正文，统计时按场景标题正则过滤

## 结构统计（宽容正则 `^\s*\d*[A-Z]?\s*(INT|EXT|INT/EXT)[\.\s]`）

- 139 场景 / 19,872 词 / 4,297 行（清洗后，水印已剥）
- 时间词：DAY 81 / NIGHT 47 / MORNING 6 / AFTERNOON 1 / PRESENT 2（审讯室框架）
- 9 处 FREEZE/RELEASE FREEZE 定格卡；4 处分屏；3 处 "camera spins round to reveal"
- 关键事件位置（行号/总行数 = 结构占比）：
  - 审讯室框架 0.1%（L4）与 95.1%（L4089）闭合
  - 开场规则独白（three card brag）0.3%；Harry/Barry 定格卡 6-7%（L263/305）
  - 大赌局 30.8%（"One hundred grand" L1327）；输牌冻结卡 33.9%（"owed half a million"）
  - 双抢日（Dog 抢 Sloanes 家 ↔ 四人组伏击 Dog 家）53-67%
  - 全员互杀（Harry 办公室）91%；审讯室回收 95.1%；**枪值揭示 99.5%（Sotherby's brochure L4276）——最大反转放最后一分钟**

## 物件转手链（多线程片分析法实证，9 站）

枪（Purdey hammer-locks）：
1. 庄园枪柜（Sloanes 家 = Appleton Smythe 府邸）
2. Scousers 私卖（"they were ours, and we sold 'em!" L2146）——枪柜现代枪上交 Barry，两把老枪私卖
3. Nick the Greek（"Seven hundred each." L2185）
4. 四人组 £700 成交（"Seven hundred for the pair." L2362；"We paid seven hundred quid for those guns." L4164）——买来"装凶狠"伏击 Dog
5. 四人组公寓（Scousers 追查目标 + 命案唯一物证）
6. Dog 爬墙夺回（L3551-3613，含现金）
7. Big Chris 头槌截胡（L3660-3667），交 Harry
8. Harry 办公室全员互杀（L3914-3961，"a terrible mistake"）
9. Tom 桥上（L4255-4296 冻结帧）——知情权错位：Harry 不知私卖、Scousers 不知卖给谁、四人组不知值钱、观众最后才知道

**巧合枢纽物理化**：四人组公寓与 Dog 家共墙（壁橱）——"Not exactly thick, these walls."（L521）；Bacon 放大器窃听（L2276-2304）。所有巧合（两组抢同一栋房、互偷家、火并）都挂在这堵墙上。

## 摘录复核 v4 备注（verify_quotes 类脚本）

- 长引文跨 4-7 行：3 行滑动窗口下 8 处误报 FAIL → **窗口改 8 行**后 113 条 0 FAIL 0 行号错位
- （L#）注解出现在引文**内部**（非仅尾部）需全局剥离；md 内 `→` 连接符先拆成两个独立引文
- 跨片对照引用（如《低俗小说》"say what again"）进 EXCLUDE 白名单，**且必须归一化为无空格形态**（saywhatagain）才匹配得上；md 中同步标注"非本稿原文"
- 校验器自检双断言：改坏例（"I will loan you the munny."）必须 FAIL + 原文句必须 PASS
- 交付物：`研习报告/两杆大烟枪_研习报告.md` + `技法卡片源稿/两杆大烟枪_技法卡片.md`（8 张：规则独白框架/定格卡/汗滴特写/一墙之隔/物件转手链/全员互杀/斗嘴对白/结局冻结帧）
