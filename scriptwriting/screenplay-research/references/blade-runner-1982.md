# 银翼杀手（Blade Runner, 1982）研习抓取记录（2026-08-07）

## 渠道与版本地图（三源对照，本片是"流传稿≠成片"的教科书案例）

| 渠道 | 抓到什么 | 版本定性 |
|---|---|---|
| IMSDb `https://imsdb.com/scripts/Blade-Runner.html` | 202KB HTML → scrtext 提取 20.2 万字符 | **Fancher 单署名早期稿**：经典独白 `I've seen things...` **grep 零命中**；罗伊之死是战斗戏（"It's time to die"）。作版本对照，不作精读底本 |
| Script Slug `scriptslug.com/script/blade-runner-1982` | 页面 200，但 PDF 直链 `assets.scriptslug.com/live/pdf/scripts/blade-runner-1982.pdf` 仅 **10 页节选**（175KB） | 非全文——发现 10 页小 PDF 时直接放弃，别当全文 |
| **Internet Archive（唯一全文）**：`blade-runner-1982-hampton-fancher-david-peoples-1981-02-23` | `*_djvu.txt` 134,645 字符纯文本，130 场 | **1981-02-23 Fancher & Peoples 双编剧稿**（拍摄前期稿）——精读底本 |
| IA 同批 `blade-runner-1982-1981.05.15` | 134,331 字符 | 1981-05-15 修订稿，正文与本稿基本一致（交叉核验用） |
| IA 同批 `blade-runner-1982-1980.07.24` | 条目存在（未细读） | 更早 1980-07-24 稿——多稿演化链完整 |

发现路径：`archive.org/advancedsearch.php?q=blade+runner+screenplay&fl[]=identifier&fl[]=title&rows=20&output=json` 一次命中三个日期稿条目——**查 IA 用 `screenplay` 关键词比裸片名更容易命中带日期的扫描稿条目**。

抓取要点：
- `*_djvu.txt` 文件即纯文本，免 OCR 管线直接可用；URL 中 `&`→`%26`、`[`→`%5B`、`]`→`%5D`（第一次 500 是瞬时故障，`curl --retry 3` 即好——**IA 下载 500 先重试，别改编码策略**；逗号规则不变：不 encode 成 %2C）
- OCR 质量：分栏错乱（"EXT. MOVING TR...ES" 场标题残缺）、缺字、`Tanhauser` 应为 `Tannhäuser`；摘录前必须人工核对语义，frontmatter/report 诚实标注

## 版本指纹：名台词形态对比（本片核心发现）

**指纹检测要对比"形态"而非仅查"存在"**——最著名的台词存在≠该稿是拍摄稿：

- 稿本（1981-02-23）罗伊独白：
  > "I've seen things... (long pause) seen things you little people wouldn't believe... Attack ships on fire off the shoulder of Orion bright as magnesium... I rode on the back decks of a blinker and watched c-beams glitter in the dark near the Tanhauser Gate. (pause) all those moments... they'll be gone."
- 成片版（鲁特格尔·豪尔即兴改写，维基证实）：
  > "I've seen things you people wouldn't believe. Attack ships on fire off the shoulder of Orion. I watched C-beams glitter in the dark near the Tannhäuser Gate. All those moments will be lost in time, like tears in rain. Time to die."
- 差异点即指纹：稿本 `you little people` vs 成片 `you people`；稿本无 `tears in rain`/`Time to die`（豪尔加写）；IMSDb 更早稿连独白都没有

## 稿 vs 成片差异表（最高价值产出）

| 项 | 1981-02-23 稿 | 成片 |
|---|---|---|
| 泰瑞之死 | `I want more life, fucker.` | `I want more life, father.`——一稿之差，弑父变求父 |
| 独白结尾 | `all those moments... they'll be gone.` | 加 `tears in rain. Time to die.` |
| 标语 | 无 `More human than human` | 有 |
| 结尾 | 公路逃逸 + Gaff 飞车追猎 + 终场旁白 `We were brothers, Roy Batty and I!` + "CREDITS ARE ROLLING, God help us all!" | 电梯门 + 独角兽梦境镜头（该镜头系补拍，第二摄影组 Brian Tufano，维基证实） |
| 旁白 V.O. | 稿内已有（`I watched him die all night`） | 试映后强制加（福特厌恶）——稿有 V.O. ≠ 成片 V.O. 是后来加的，两回事 |
| 开场 | 眼睛反射场景 `The following scene is reflected in the eye until HOLDEN is seated.` 已在稿中 | 基本一致——开场眼睛是剧本自带，不是导演现场加的 |

## 结构数据（130 场 / 13,588 行 OCR 文本，占比=行号÷总行数）

- 1.6%：开场 EXT. HADES - DUSK（泰瑞金字塔、眼睛）
- 4.8%–5.6%：V-K 测试乌龟问题、里昂杀霍顿
- 8.6%–11.3%：面摊戏德卡登场（盖夫"寿司"挑衅）
- 13.7%：布莱恩特办公室强征归队（激励事件）
- 22%–25.1%：泰瑞办公室、瑞秋登场、"They want memories?"
- 25.7%–31.7%：里昂旅馆（蛇眼对峙）
- 37.8%–39.7%：塞巴斯蒂安楼普莉丝入场
- 44.6%–54.7%：祖拉/蛇坑 → **中点：祖拉之死**
- 66%–72.3%：普莉丝/罗伊/塞巴斯蒂安
- 83.9%：`I want more life, fucker.`（罗伊杀泰瑞）
- 86.7%–90.4%：终战、普莉丝之死（鸽子群爆出）
- 93.5%–94.2%：罗伊独白、鸽子落肩
- 96.2%：盖夫 `It's too bad... But who does.`
- 98.4%–98.6%：锡纸独角兽（Gaff's gauntlet）
- 99.4%：终场旁白 `We were brothers, Roy Batty and I!`

## 关键摘录行号（1981-02-23 稿，grep 实证）

- L212 开场眼睛 / L656-717 乌龟问答 / L11397 "I want more life, fucker." / L12752 c-beams / L12794 鸽子 / L13066 "It's too bad" / L13395 锡纸独角兽 / L13513 终场 V.O.；泰瑞"cushion or pillow"记忆论在 L3400-3489 段

## 研习产物落位（film-suite-research 本地源）

- `研习报告/银翼杀手_研习报告.md`（含画面锚点 15 个、潜台词 3 例、动作层 3 例、桥段 3 个）
- `技法卡片源稿/银翼杀手_技法卡片.md`（8 张：开场眼睛/V-K 测试/罗伊独白/折纸独角兽/追猎嵌哲学/雨夜屋顶/瑞秋照片/终场旁白）
- `剧本原文/blade-runner_剧本_来源.md`（1981-02-23 稿全文 + frontmatter 标注版本/OCR 质量）
- 页面存档 `pages/blade_*.txt|html|pdf`（IMSDb 提取稿、IA 双稿、Script Slug 10 页 PDF、维基纯文本）

## 对妖玉影视套件的一句话

银翼杀手最值得偷的一招：**把哲学问题装进类型片引擎里跑**——每场追猎戏都是一次"谁是人"的拷问（V-K 测谎开场、照片记忆、独白审判、折纸暗示），两条线共用同一套动作。
