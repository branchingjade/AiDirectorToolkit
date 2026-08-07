# 《罗生门》Rashomon 剧本获取记录 + 多视角研习实证（2026-08-06）

## 获取记录

- **目标**：黑泽明《罗生门》(1950) 英文剧本（Donald Richie 译）——多视角叙事研习
- **三主库全灭形态**（都是实测，勿再试）：
  - IMSDb `https://imsdb.com/scripts/Rashomon.html` 与 `Rashomon,-The.html`：**都是 7,785 字节空壳**（软 404——下载后 `wc -c` 判壳，`grep -c scrtext` = 1 但无 `<title>`）
  - Script Slug `rashomon-1950` / `rashomon`：404；PDF 直链 403
  - Internet Archive `rashomon0000akir`（1969 Grove Press 书，Akira Kurosawa）：**借阅受限**——`/download/rashomon0000akir/rashomon0000akir_djvu.txt` 返回 `401 Authorization Required`（nginx）。**IA 借阅限制识别法：/download/*_djvu.txt 401 即受限**，换搜索路径
  - scripts-onscreen.com 聚合页 `rashomon-script-links/`：有页面但只有付费 ScriptFly + subslikescript 字幕站，无免费直链
- **成功路径**：Kimi WebBridge Bing 搜 `"Rashomon" screenplay pdf Richie full` → 命中 **The Successful Screenwriter**：
  - `https://thesuccessfulscreenwriter.com/wp-content/uploads/Rashomon-Continuity-Script.pdf`（199KB）
  - 检索词**带译者名（Richie）命中率远高于裸片名**
  - 同命中还有 garryvictorhill.com/pdf/Rashomon.pdf（10KB 节选，弃用）

## 文本层结构（关键）

- PDF = Grove Press 1969 书《Rashomon》文本层：**连续剧本 + 芥川两篇短篇**同书
  - 剧本部分：L1–3119（`THE END`），3,120 行 / ~91,800 字符，**406 个镜头（编号 1–407 缺 1）**，镜头号+景别行首标记（`1   LS: ...`）
  - 剧本后是影评文章（L3120–3373），`"In a Grove" by Ryunosuke Akutagawa` 从 **L3374** 起（7 份证词完整）
- 编码 cp1252/latin-1，`pdftotext -layout` 转换；正文含零星 OCR 噪声（`begisn`/`spears` 语境），引用保留原貌
- 清理后落盘：`pages/screenplay-rashomon.txt`（剧本部分）、`pages/akutagawa-in-a-grove.txt`（原著，行号 = 全文件行号 − 3374）

## 多视角叙事结构实证（行号占比）

| 层 | 镜头 | 行号 | 占比 |
|---|---|---|---|
| 框架·雨中门楼 | 1–12 | L1–131 | 0–4.2% |
| 樵夫庭证（伪） | 13–55 | L132–440 | 4.2–14.1% |
| 僧人庭证 | 56–64 | L442–553 | 14.2–17.7% |
| 多襄丸供词（版1） | 65–210 | L581–1400 | 18.6–44.9% |
| 门楼插曲①（"全是谎言！"） | 211–218 | L1404–1520 | 45–48.7% |
| 妻子忏悔（版2） | 219–253 | L1524–1730 | 48.9–55.4% |
| 亡灵之语（版3） | 254–305 | L1735–2188 | 55.6–70.1% |
| 门楼插曲②（"没有匕首！"） | 306–310 | L2191–2260 | 70.2–72.4% |
| 樵夫真实版（版4，无音乐） | 311–375 | L2260–2765 | 72.4–88.6% |
| 门楼收束（弃婴/雨停） | 376–407 | L2767–3119 | 88.6–100% |

## 四版本"藏与改"速查（研习核心）

- 多襄丸：美化决斗（23 回合 L1360–1366）——真实版跪地求婚被拒、被吐口水
- 妻子："我昏倒了"（L1713–1717）——真实版狂笑辱骂、吐口水、逼决斗（L2490–2518）
- 武士（亡灵）：自尽（L2156–2160）——真实版喊"我不想死"（L2715–2717）
- 樵夫：庭证"无匕首"——真实版偷走珍珠柄匕首（平民推理 L2986–2993 揭穿）
- 道具杠杆：匕首在四版中分别"插在土里/在丈夫胸口/被拔走/根本不在场"

## 原著（《竹林中》）vs 电影

- 原著 7 份证词（樵夫/行脚僧/捕快/**老妪**/多襄丸/妻子/亡灵）；电影删老妪，5 段
- **原著妻子承认亲手杀夫**（"I stabbed the small sword ... into his breast"）；电影改为"昏倒"
- **樵夫真实版为电影原创**；原著"有人拔走我胸口的刀"是悬案，电影破案（樵夫偷的）
- 电影并《罗生门》短篇：门楼 + 弃婴（替换原著拔死人头发的老妪），结尾加救赎
- 主题差异：芥川停在不信任；黑泽明"相对主义外壳 + 人道主义内核"（"keep my faith in men" L3077–3080）

## 复核实测

- 交付 md 27 条英文摘录：首轮多行块提取 27/27 全误报 FAIL（列表项被吞进引文）→ 改逐行 `(?m)^\s*>\s*(.+)$` 提取 + 剥行尾（L…）注释 + 剥角色名前缀 + 剥镜头号前缀（`^\d{1,3}\s+(LS|MS|MCU|CU|ECU|MLS)\s*[:.]?\s*`）→ 27/27 直过
- 背景事实交叉核实：维基百科 https://en.wikipedia.org/wiki/Rashomon （威尼斯金狮/奥斯卡最佳外语片/宫川一夫直拍太阳+镜子反光/早坂文雄/88 分钟/大映）+ https://en.wikipedia.org/wiki/Rashomon_effect （"罗生门效应"进入法律/心理学通用语）

## 研习产出落盘（film-suite-research/）

- `研习报告/罗生门_研习报告.md`、`技法卡片源稿/罗生门_技法卡片.md`（8 张卡：框架容器/分叉点精确/自夸型叙述/被动者叙述/尊严自杀拆穿/道具杠杆/声轨缺席=真相/撒谎者行善）
