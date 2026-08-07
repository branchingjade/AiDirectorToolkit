# 《2001太空漫游》抓取记录 + 极简对白量化法（2026-08-06）

## 来源与抓取路径

- **IMSDb 双壳全灭**：
  - `imsdb.com/scripts/2001-A-Space-Odyssey.html` → HTTP 200 但 **0 字节**（新壳形态，区别于 7,785 字节软 404 壳）
  - **规范 URL 查询法（新技巧）**：`curl imsdb.com/all-scripts.html` 后 grep 片名 → 拿到带冒号/空格的规范路径 `https://imsdb.com/Movie%20Scripts/2001:%20A%20Space%20Odyssey%20Script.html`（URL 编码：空格 %20、冒号 %3A）——但仍是无 scrtext 的 40KB 壳。**判据永远是 grep scrtext 长度，不是 HTTP 状态码**
- **Script Slug（唯一可用源）**：页面 `scriptslug.com/script/2001-a-space-odyssey-1968` → PDF 直链 `assets.scriptslug.com/live/pdf/scripts/2001-a-space-odyssey-1968.pdf`（80KB → pdftotext 126KB 文本 → 归一化 3507 行 / 119,163 字符）

## 版本指纹：早期工作稿（非拍摄稿）

- grep 成片终局台词当指纹，**全部零命中**：`Open the pod bay doors` / `I'm afraid I can't do that` / `My God, it's full of stars` / `Its origin and purpose` / `star child` / `starchild` / `foetus` / `fetus`
- 稿内证据：① 全文带 **NARRATOR 旁白**（140 词，成片删光）；② 目的地 **Saturn**（成片改 Jupiter——维基记载特效组做不出可信土星环）；③ 结尾=星孩引爆地球轨道核弹（维基确认因与《奇爱博士》核爆雷同被弃用）；④ 残留写作占位符 L3382-3383 `The rest of this sequence is being worked on now by our designers.`；⑤ 标题卡 PART III = "14 MONTHS LATER"；⑥ 标题页署名 "Stanley Kubrick & Arthur C. Clark"（Clarke 拼写误）
- 维基交叉验证：https://en.wikipedia.org/wiki/2001:_A_Space_Odyssey —— 139 分钟、首尾各约 20 分钟无对白、"By the time shooting began, Kubrick had removed much of the dialogue and narration"、Alex North 原创配乐被临时古典乐顶替（North 首映现场才知道）、最后一句对白 "Its origin and purpose still a total mystery."

## 极简对白量化法（可复用于任何"对白缺席"片）

1. 归一化：`\r\n`→`\n`、`\f`→`\n`、压缩空行
2. 对白行判定启发式：行首缩进 ≥15 空格 + 非全大写 + 非空 → 2001 实测 808/2127 行 = 38%；对白词 4,766（角色 4,626 + 旁白 140）——口径是近似，标注"横向比较用"
3. **PART 标题卡切分**（正则 `^"PART [IVX]+$`）→ 逐段对白词数：
   - PART I（非洲 300 万年前，L9-443）：435 行 **0 词**——"零对白开场"直接量化
   - PART II（YEAR 2001，L444-1681）：2,343 词（含旁白 87）
   - PART III（14 MONTHS LATER，L1682-3507）：2,421 词（含旁白 53）
4. 角色台词词数：cue 正则 `^NAME( \(CONT'D\))?$` + 下一行文本 → FLOYD 498 / BOWMAN 431 / POOLE 415 / HAL 394 / NARRATOR 140
5. 横向参考：话痨片《安妮·霍尔》约 24,000+ 词 → 2001 约 1/5，极简可量化

## 摘录复核新变体：⑦破折号归一化

- PDF 文本层破折号是 **U+00AD 软连字符**（cp1252 0xAD），摘录里的 —/– 全部 in 校验失败
- 解法：校验前双方 `re.sub(r'[\xad\u2013\u2014-]', '-', ...)` 归一后再 in 校验（格式化伪影 ≠ 内容错误，别改稿）
- 2001 实测：33 段摘录（卡片+报告反引号 span，剥角色名前缀 `^[A-Z][A-Z .'()/-]{0,30}:\s*` + 拆 ` / ` 拼接段）33/33 命中

## 关键场景行号图（2001-normalized.txt，3507 行）

- L9-11 PART I 卡 / L444-446 PART II 卡 / L1682-1684 PART III 卡
- L245-345 石板第一课（L253 `A simple, maddeningly repetitious rhythm pulses out of the crystal cube...`）
- L316-319 觉醒（`the urge to kill. He had taken his first step towards humanity`）
- L438-441 骨头统治→PART II 转场（`Now he was master of the world... But he would think of something.`）
- L1495-1530 TMA-1 挖掘（L1517 `deliberately buried about four million years ago`）
- L1934-1941 "Just ask Hal"（信任即反讽）
- L1950-1958 HAL 礼貌拒绝（`I'm sorry, Frank, but I don't think I can answer that question...`）
- L2061-2100 纪录片序列时刻表（慢节奏证据）
- L2127-2128 HAL 生日打断（`Sorry to interrupt the festivities, Dave`）
- L2216-2258 Decompress Pod Bay 程序化对白（`Five by five` 链）
- L2617-2619 `I'm not capable of being wrong.`
- L3096-3160 HAL 之死（L3135-3142 求饶退化 / L3153 `Urbana, Illinois, January 12th, 1991` / L3156 `Daisy, Daisy`）
- L3330-3344 Floyd 安全简报（成片删除的唯一"解释"）
- L3358-3359 土星石板（`black, mile long, geometrically perfect rectangle`）
- L3382-3383 占位符 / L3407-3410 外星动机旁白（成片删）/ L3504-3505 结尾句

## 产出

- 研习报告 + 8 技法卡片：零对白开场/标题卡时间跳跃/不解释符号/礼貌的拒绝（AI 冷静恐怖）/机器之死（反派死亡戏）/程序化对白/清单式慢节奏/删解释的结尾（版本对比教学）
- 成片事实（维基，URL 见上）+ IMDb 条目 https://www.imdb.com/title/tt0062622/
