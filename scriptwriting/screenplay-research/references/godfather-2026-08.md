# 教父 (The Godfather, 1972) 抓取与研习记录（2026-08-07）

## 来源与状态

- **Script Slug PDF**（主源）：页面 https://www.scriptslug.com/script/the-godfather-1972 → PDF 直链 `https://assets.scriptslug.com/live/pdf/scripts/the-godfather-1972.pdf`（146KB，124 页）
- **IMSDb `Godfather,-The.html` = 7,785 字节空壳**（软 404，无 scrtext）——与 SKILL.md 主文记录一致（教父是该模式的经典案例），别死磕
- 转换：pdftotext -layout → cp1252 解码（UTF-8 读报 UnicodeDecodeError，0xAD 软连字符）

## 文本层质量与教父专用伪影

- 238,861 字符 / 22,306 词 / 7,097 行；**对白层完整可信**；场景标题前缀大量损坏（INT./EXT. 仅 13 处：8 INT + 5 EXT；裸标题约百处可辨）
- 裸标题形态：`INSIDE THE RESTROOM`、`CAUSEWAY TOLLBOOTHS  DAY`、`CLEMENZA'S CELLAR  DAY`——双空格分隔是常态
- 教父专用伪影三件套：
  1. **折行粘连**：`real m an`（man 被拆成 "m an"）、`I wan some fruit`
  2. **撇号伪影**：`her nose was a'broken. Her jaw was a'shutted`（Bonasera 独白，成片为 "broken/shattered"）
  3. **稿内笔误**（保留，标 [sic]）：`FABRISIO (Cont'd)`（应为 FABRIZIO）、`sprinkle's the baby's lip`

## 版本指纹：接近拍摄稿的流传终稿（非完成台本）

- 无日期页/无修订标记/无制作公司抬头；但开场 Bonasera 独白、结尾「Neri 关上门挡住 Kay 视线」均与成片一致，关键台词齐备
- 含 `(something in Latin)` 占位符（洗礼戏拉丁文稿面未写定，拍摄期现场补）——**占位符 + 成片式首尾 = 「流传终稿」判定组合**
- 网传「1971-03-29 最终拍摄稿」无法在本稿证实，如实标注

## 关键行号（grep 定位，总 7,097 行；行号占比 = 结构推断，非作者声明）

| 事件 | 行号 | 占比 |
|---|---|---|
| `Some day, and that day may never come...`（人情债语法） | L156 | 2% |
| `That's my family, Kay. It's not me.`（婚礼，局外人宣言） | L761 | 10.7% |
| Don 水果摊中弹（幕一转折） | L1848 | 26% |
| 医院夜戏空城计（`I'm with you now` / `Put your hand in your pocket like you have a gun`） | L2818 | 39.7% |
| `It's not personal, Sonny. It's strictly business.`（餐厅刺杀计划=全片中点） | L3179 | 44.8% |
| 西西里 Apollonia（`She would tempt the devil`） | L4226 | 59.6% |
| 过路费亭桑尼之死（`The toll-collector 'drops' Sonny's change` / `stops, then kicks him in the head`） | L4965 | 70% |
| `I've decided to be Godfather to Connie's baby`（洗礼计划=幕三启动） | L6409 | 90.3% |
| 结尾 `Is it true? Is it?` / `No.` | L7070+ | ~99% |

三幕切分：0–26% 建置 / 26–70% 入局（医院→餐厅→西西里→桑尼之死）/ 70–100% 登基（清算→洗礼→门缝谎言）。

## 台词拼写实测（对记忆的勘误，引用以稿为准）

- `I'm gonna make him an offer he can't refuse.`（Vito 对 Johnny，婚礼戏）；Michael 对 Kay 的版本是过去时 `My father made him an offer he couldn't refuse.`
- `Leave the gun. Take the cannoli.`——**大写 T**：小写搜 `take the cannoli` 会 MISS（大小写陷阱再次应验，见 SKILL.md）
- `It's a Sicilian message. It means Luca Brasi sleeps with the fishes.`——**Clemenza 说的**，不是 Sonny；Sonny 只说 `What the hell is this?`
- `I never wanted this for you`——**Vito 花园对 Michael**（`you would be the one to hold the strings`），非 Michael 对 Kay
- 婚礼戏潜台词自曝在舞台指示：`(to Johnny, but toward and about Sonny)`

## 结构研习要点（权力转移片模板）

- 地理标记灵魂位移：新英格兰大学 → 医院 → 餐厅 → 西西里 → 纽约；`DISSOLVE TO` 46 次（流亡=溶解）vs `CUT TO` 124 次（清算=硬切）
- 暴力后置渲染：全片直给暴力仅餐厅刺杀一场；马头只给结果（`finds Khartoum's severed head in his bed; and SCREAMS ah...ah...ah...ah...ah!`），桑尼之死先日常后屠杀
- **镜头指令词频 = 编剧稿指纹**：CLOSEUP 1 / PAN OF 1 / FULL SHOT 1——全片唯一一次 CLOSEUP 指令用在马头戏后 `CLOSEUP OF VITO CORLEONE'S FACE / He nods.`（稀缺性即力量）

## 摘录校验记录（v5）

- 首轮 57/57 全假 FAIL（负例却正确报错）→ 归一化不对称（候选剥空格、源没剥）；二轮 12 残留 → 省略号先于 norm 被吞 / ` / ` 拼接未拆 / 中文括注英文残留 / 前缀名单漏 MCCLUSKEY / 本地路径未白名单
- 修复后 56 条 0 FAIL + 双断言（负例 FAIL、正例 PASS）。细节与清洗顺序已并入 SKILL.md 校验器节

## 产出

- `研习报告/教父_研习报告.md`（含三幕行号占比表/15 画面锚点/潜台词 4 例/动作层 4 例/桥段 3 个）
- `技法卡片源稿/教父_技法卡片.md`（8 张：开场双线/offer 潜台词/人情债语法/医院空城计/餐厅刺杀/马头/桑尼之死/洗礼+门缝）
- `剧本原文/godfather_剧本_来源.md`（全文 + frontmatter，正文无 H1）
- `pages/godfather-1972.pdf` / `godfather-1972.txt`（规范化 UTF-8）
