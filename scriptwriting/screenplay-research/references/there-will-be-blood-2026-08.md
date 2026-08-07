# 《血色将至》抓取记录 + 反英雄史诗研习要点（2026-08-06）

## 来源与版本

- **主源**：Script Slug PDF 直链 `https://assets.scriptslug.com/live/pdf/scripts/there-will-be-blood-2007.pdf`（页面 https://www.scriptslug.com/script/there-will-be-blood-2007 ），2,868KB
- **IMSDb**：`https://imsdb.com/scripts/There-Will-Be-Blood.html` HTTP 200 但仅 7,785 字节空壳（无 `scrtext`），软 404 弃用——又一部 PTA 档 IMSDb 空壳
- **版本识别**：首页 `FINAL SHOOTING SCRIPT / Pink 7.25.06 / Blue 5.18.06 / White (Numbered) 2.20.06` = **最终拍摄稿，白→蓝→粉三次修订，粉色最新**；正文行尾 `*` 标记 = 该页最新修订（Henry 谋杀序列 L4891-5055 整段 Pink，页眉 `Pink Revised 7/25/06`）；上映版 2007-12-26，158 分钟
- **存档**：`剧本原文/there-will-be-blood_slug_finalshooting_2006-07-25.txt`（191,238 字符 / 6,687 行）

## 文本层 OCR 噪声（pdftotext -layout）

- `1` = 感叹号：`I AM THE THIRD REVELATION 1`（=REVELATION!）
- `11` = 引号：`11 SMALL LOTS"`（左引号变 11，右引号幸存）
- 场景号并入动作行：`6A SHAFT WITH NO HOLD - AND LANDS AT THE BOTTOM`（行首场景号把 "down the / shaft" 断连）——摘录在该处拆段 + 标 [sic] 版式噪声
- 人名变形：`DARIBL`=DANIEL、`GBORGB`/`GBl>RGB`=GEORGE、`BW`/`s.w.`=H.W.、`AlLMAN`=AILMAN
- 字母级：`froa`=from、`yau`=you、`AllBY`=ALLEY、`STAIRWBLL`=STAIRWELL、`HIGHT`=NIGHT、`DRINNK`=DRINK、`loosing`=losing（稿内原貌）
- 稿内自带怪拼（非噪声，引用保留）：`ACCCRROSSSSSSSSSS`（奶昔台词，指示拖长语速）、`Me......._I am the Third Revelation.`（下划线为 OCR）

## 结构实证

- 115 场景（宽容正则 `^\d+\s+(INT|EXT|INT/EXT|OVER)`），编号至 138，缺号=删场留号；显式空号 `113 OMITTED`、131-134 连续四场 OMITTED
- 年份只标 3 处场景标题（L26 `- 1898`、L158 `1902`、L363 `1908`），其余靠内容推进；维基分类确认全片 1898→1902→1911→1927——**年份珠少时用维基分类确认跨度**
- 音乐提示入文：开场 `MUSIC BUILDS FROM SMALL TO LOUD, VIOLENT CRESCENDO, THEN OUT.` + `(START MUSIC)` ×2（L1642/L4542）

## 关键行号注册表（反英雄史诗研习）

- 开场无对白：L26-359（场景 2-21）零对白；**第一句台词 L370** `Ladies and Gentlemen, I've traveled over half our state...`（开口=掠夺开始）
- 坠落寓言：L102-110（`HEADS FEET FIRST STRAIGHT DOWN THE...`）
- 井喷/失聪：L2986-3100；**SOUND DROPS OUT 声轨主观化装置 4 处**：L2992（声音随视角回）、L3009（`SILENT WITH HIM`）、L3681（日常版：看 Henry 吃饭）、L4146（火车送别，`drops out slowly`）
- `ocean of oil`：L3131（井喷火中对 Al Rose）
- 竞争独白：L3851-3853；自我供词：L3917-3930（`I see the worst in people...I want to rule and never, ever explain myself`）
- 弃子：L4060-4181（H.W. 放火烧 Henry 的床→火车送走→`He's not my son.`）
- 标准石油威胁：L4381-4396（`One night.---! 'm gonna come inside your house...cut your throat.`，L4381 `!'m`=I'm 的 OCR）
- Henry 处决：L4937-5027（`DANIEL puts the GUN TO HENRY'S HEAD AND FIRES. HENRY SLUMPS OVER. HOLD ON DANIEL.`）
- Bandy 受洗交易：L5080-5208（`you should be washed in the blood of Jesus Christ.`）
- 洗礼回声：L5330-5416（Eli 领诵/Daniel 复诵，L5403-5407 三连 `I ABANDONED MY CHILD...I ABANDONED MY BOY.`）
- `sweet face to buy land` 首尾回收：L323-326（婴儿篮）→ L6196-6204（终局揭晓收养动机）
- 奶昔：L6554-6561（`DRAINAGE! DRAINAGE, ELI!` → `I DRINK YOUR MILKSHAKE! I DRINK IT UP.`）；终局 L6590-6682；`I'm finished.` L6682

## 版本指纹

奶昔台词**只在终局宅邸对峙**出现（非镇民演讲）；`Ladies and Gentlemen` 开场演讲即全片第一句台词。剧本 vs 上映版差异未逐条比对（H.W. 返场戏稿内为 `BW/GEORGE` 双人归属，上映版由 H.W. 独自开口）。

## 反英雄史诗研习法（本片新增，可复用）

1. **开场无对白实证**：定位第一句台词行号 ÷ 总行数 = 沉默开场占比；第一句台词 = 结构宣言（本片：沉默十五分钟的人开口就要钱）
2. **双谋杀对照**：第一次杀"假亲人"（Henry，供词被打断）vs 最后一次杀"真敌人"（Eli，宣言说完即杀）；两次都"杀人不给台词、杀人后 HOLD 脸、尸体处理单独成段"
3. **声轨主观化装置**：`SOUND DROPS OUT`/`SOUND COMES BACK WHEN WE ARE WITH HIM` 是剧本级可 grep 的感官装置（失聪/视角切换），"谁的视角谁的声音在场"
4. **时代史诗时间骨架**：年份珠少时用"每十年一场经济戏"代替编年史——话术演变（恳求→谈判→威胁→沉默）= 人物弧光；群众场面给一句作者旁白点题（`We witness human dignity go completely out the window.` L499）

## 摘录校验

142 spans 0 FAIL（反引号 span 提取 + 按 ` / `、`...` 拆段 + CJK/反斜杠 span 计 SKIP 不计 FAIL + [sic] 保留 OCR 噪声原貌）；自检坏例（植入 `HORSE MILKSHAKE`）2 FAIL 才可信。
