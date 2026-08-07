# 《后窗》(Rear Window, 1954) 研习记录 — 2026-08-06

## 获取记录

- **主源 IMSDb**：`https://imsdb.com/scripts/Rear-Window.html`，HTTP 200 直下（HTML 370KB → scrtext 提取 34.3 万字符 / 9171 行）。版本 = **John Michael Hayes Final Draft, December 1, 1953**（IMSDb 流传稿，分镜式拍摄稿）。
- **Script Slug 弃用**：`assets.scriptslug.com/live/pdf/scripts/rear-window-1954.pdf` 3.3MB 下载成功但 **pdftotext 仅得 165 字符**（文本层整体缺失）——与教父/断背山同类的 Slug PDF 文本层问题，直接换 IMSDb。
- 本地存档：`film-suite-research/剧本原文/rear-window_imsdb_1953-12-01.txt`

## 格式特征（分镜式拍摄稿 = 本片新方言）

- **442 条镜头级标题**，每条 `INT/EXT. 地点 - 时间 - 景别`，无场号。裸标题正则 `^\s*(INT|EXT|INT/EXT)[\.\s]` 命中 442；编号宽容正则命中 **0**。
- 地点分布：INT. JEFF'S APARTMENT 280（63.3%）+ EXT. NEIGHBORHOOD 150（33.9%）+ GUNNISON'S OFFICE 2 + PHONE BOOTH 2 = **430/442（97.3%）在公寓+院子**——单场景叙事铁证；全部外部镜头在 2.2%-4.1%（开场职业交代）与 42.4%（Lisa 电话亭查名）。
- 景别词频：SEMI-CLOSEUP 106 / SEMI-LONG SHOT 86 / MEDIUM SHOT 84 / LONG SHOT 20 / SEMI-CLOSE SHOT 13——中景基座的"窗口观察视距"。
- **FADE OUT/FADE IN 成对出现 11 对 = 天界**，时间序列：`DAY→SUNSET→NIGHT→DAWN→DAY→NIGHT→DAY→DUSK→NIGHT→DUSK→NIGHT→DAY`（3 天 3 夜，跨 12 个时间段落）。时间词取法：FADE 行后第一个场景标题的 DAY/NIGHT/DUSK/SUNSET/DAWN。

## 悬念升级阶梯（行号占比 = 结构定位，占比推断非作者声明）

| 占比 | 事件 | 原文锚点 |
|---|---|---|
| 0.2% | 开场拉回揭示偷窥宿主 | "THE CAMERA PULLS BACK until a large sleeping profile of a man fills the screen"（L48-51） |
| 8.4% | Stella 宣判偷窥罪 + Peeping Toms 对白 | "The New York State sentence for a peeping Tom is six months in the workhouse!"（L764-766） |
| 35.8% | 望远镜→长焦升级，刀锯包报纸 | "He quickly takes off the existing lens and puts on the telephoto lens"（L3270-3271） |
| 42.6% | Thorwald 名字拼出 L-A-R-S（Lisa 电话亭） | "The name on the second floor rear mailbox reads Mr. And Mrs. Lars"（L3902-3904） |
| 47.2% | Doyle 登场；"有谁真的看见她被杀了？" | "Now did anyone, including you, actually see her murdered?"（L4731-4732） |
| 53.1% | 中点断言：尸体在箱子里 | "Forget the story -- find the trunk. Mrs. Thorwald's in it!"（L4870-4871） |
| 65.5% | 权威否定 + 首饰推理确认 | "Lars Thorwald is no more a murderer than I am."（L6010-6011）；"That wasn't Mrs. Thorwald who left with him yesterday morning"（L5971-5972） |
| 73.4% | 狗被杀（悬念质变点） | "Which one of you killed my dog?"（L6754） |
| 77.0% | 花坛凹陷：铁证 = 日常知识 | "since when do flowers grow shorter in two weeks?"（L7066-7068） |
| 90.6% | POV 反转：被看者直视镜头 | "he looks right up -- directly into the lens"（L8315-8317）；"Stella! The lights! He'd seen us!"（L8325） |
| 95.0% | 高潮：破门 + 闪光灯反杀 | "What do you want from me?"（L8705）；"A vision of Jeff and the apartment as seen by Thorwald... filled with large twisting balls of bright yellow color"（L8796-8799） |
| 97.2% | Jeff 被扔出窗（主题审判） | "I'll give you a good look out the window."（L8882-8883） |
| 99.4% | 结尾反向全景逐窗结账 | "the CAMERA PANS FROM RIGHT TO LEFT"（L9117-9118）；"The newlyweds are arguing."（L9146） |

## 悬疑题材密码速览（与记忆碎片互补：视角即主题 vs 结构即主题）

1. **偷窥框架**：开场"看的行为先于看的人"（拉镜揭示宿主）建立视角合同；热 = 窗口洞开的物理前提（L41-46 社会契约段）。
2. **信息差矩阵**：夜间全景横移一次登记全院窗口（L3316-3391），每窗一个故事线、互不知情，仅观察者全知；切窗零解释。
3. **工具升级阶梯**：肉眼→望远镜→长焦，每次升级提升窥欲 + 危险度；"消失的一瞬"（L3287-3289）是免费悬念。
4. **悬念正当性检验**：每级怀疑过"正常生活解释"的关（Lisa 正常化反驳 L3741-3749）；铁证 = 日常知识无法解释的反常（花两周不会变矮）。
5. **POV 反转**：被观察者直视镜头 = 窥视闭环 + 即刻危险 + 观众进被告席。
6. **高潮**：瘫痪主角（断腿）+ 人设武器（摄影师闪光灯）+ 镜头叛变到反派主观视野。

## 交付物

- `film-suite-research/研习报告/后窗_研习报告.md`（偷窥框架/信息差/单场景/升级阶梯/12 画面锚点）
- `film-suite-research/技法卡片源稿/后窗_技法卡片.md`（8 张，全部摘录 39/39 校验通过）

## 版本诚实声明

IMSDb 流传稿为 1953-12-01 拍摄稿，与上映版整体一致但个别场次顺序有出入（明信片伪证戏排布、电话亭查名者为 Lisa 非 Jeff）；统计口径为镜头级标题，与传统场号不可直接对比。
