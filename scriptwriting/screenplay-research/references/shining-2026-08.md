# 《闪灵》The Shining 1980 抓取与研习记录（2026-08-06）

## 版本：Post Production Script（后期制作稿）——第三版本类别的实证

- 标题页指纹：`"THE SHINING."` / `Post Production Script.` / `A STANLEY KUBRICK FILM` / `July, 1980`；IMSDb 页脚 `Writers : Stanley Kubrick  Diane Johnson`
- **IMSDb 与 Script Slug 双源同版**（2026-08-06 实测）：首场文本一致（`EXT. COLORADO MOUNTAIN (U.S.A.) - DAY - L.S.`）、结尾 FADE OUT + 1921 照片一致、**场景标题 231/231 一致**、9 条关键台词双源全命中
- URL：IMSDb 真稿 `https://imsdb.com/scripts/Shining,-The.html`（scrtext 224,978 字符）；⚠️ `Shining.html` 是 559 字符软 404 空壳（老陷阱复现）；Script Slug 页面 `https://www.scriptslug.com/script/the-shining-1980`，PDF 直链 `https://assets.scriptslug.com/live/pdf/scripts/the-shining-1980.pdf`
- 本地文本：`film-suite-research/pages/shining-imsdb.txt`（208,078 字符 / 8,132 行；行号均指此文件）

## 格式特征：分镜式镜头级标题（后期制作稿变体）

- 每条标题 = 地点-时间-景别缩写：`EXT. COLORADO MOUNTAIN (U.S.A.) - DAY - L.S.`、`INT. HOTEL/LOBBY - DAY - M.L.S.`、`M.S.` / `M.C.S.`（231 处）
- 正文全大写镜头指令：CAMERA TRACKS FORWARD / TRACKS BACK / PANS / TILTS、机位 `cam.L / cam.R`、`back to camera in f.g.`、`in b.g.`
- 与后窗拍摄稿（LONG SHOT 全称）的差异：后期稿用缩写景别后缀
- **后期稿可能回填成片台词**：`Here's Johnny!`（L7361）与打字机重复句（L5943-5973）已在稿中——不能据此断言"拍摄期即兴"（如实标注）

## 与 Stephen King 小说差异（版本指纹）

- Room **237**（稿 L2425-2465）vs 小说 217；结局 Jack 冻死迷宫 + 1921 照片（L8091-8117）vs 小说酒店爆炸；小说树篱动物删除改树篱迷宫；Wendy 人设大改

## 结构统计（程序化粗读）

- 231 场景分布：Overlook 室内 103（44.6%）+ 迷宫 14 + 酒店外景 26 + Boulder 8 + 山路 8 + 裸标题 72 → 入住后叙事封死在酒店+迷宫
- 道具词频：corridor 65 / maze 55 / TONY 49 / snow 37 / typewriter 9 / tricycle 5 / ball 7 / mirror 6；grep "carpet" 零命中（成片地毯图案稿中不可考，标注）
- 结构占比（行号/总行数）：入住 ≈15%（CLOSING DAY L1230）、打字机真相 ≈73%（L5943）

## 日期卡时间骨架（新推断器）

- 稿本 6 张：**CLOSING DAY（L1230）→ TUESDAY（L2754）→ THURSDAY（L3024）→ SATURDAY（L3050）→ MONDAY（L3381）→ WEDNESDAY（L3621）**，格式 `Superimposed Title over:` / `Superimposition over:` + 星期词独立行
- ⚠️ 稿本卡片顺序/数量与成片字幕卡有出入（如实标注，别用记忆补成片卡）

## 关键场景行号（供未来引用）

- 开场航拍 L19-72；面试/Grady 灭门 L540-620（"stacked them neatly" L583）
- 血潮电梯 L770-803（稿用 **lift** 非 elevator；第三次 `gushes up into camera lens causing black out` L802-803）
- 双胞胎走廊 L3264-3336（对称站位 + 台词三段：`For ever...` L3299 / `... and ever...` L3317 / `...and ever.` L3331）
- Room 237：对话 L2425-2465（`There ain't nothing in Room 237` L2463-2465）、门牌 L2823、三轮车 L2837-2848
- 浴缸女 L4312-4313；REDRUM L4580-4581（稿写 `word "MURDER" written backwards`）+ 呓语 L5349-5370
- Lloyd 戏：`White man's burden` L3973-3975；情话威胁 `Darling, light of my life... bash your brains in` L6364-6370
- 打字机 `How do you like it?` L5987/L5995；Grady 厕所 `You have always been the caretaker... I've always been here` L5159-5163
- 斧头破门/Here's Johnny L7295-7392；迷宫脚印 L7837-7889（`CAMERA TRACKS FORWARD and stops when footprints end. CAMERA TILTS UP to snow without footprints.` L7887-7889）；冻死 L8093-8094；1921 照片 L8098-8117

## 摘录复核 v3 实测（本片 39/44 → 修 2 处后 39/44，余 5 条全为路径/URL 元数据）

- 候选提取三源：反引号代码块 + 中文全角引号“”内英文 + `> ` 引用行；英文占比过滤 ≥0.55 排除元数据
- 清理顺序：剥（Lxx-xx）行号标注 → 剥角色名前缀（含 `(OFF)`/`(CONT'D)`/`(OFF) (CONT'D)` 变体）→ 归一化空白 → `in` 校验；宽松回退：去标点小写后子串匹配
- **台词被反应镜头打断必须拆段**：cabin-fever 台词 L595-597 与 L604-605 中间插入 `CUT TO: M.C.S. JACK`，整句校验 FAIL，拆两段分别校验通过
- **多行居中字幕逐行校验**：`OVERLOOK HOTEL` / `JULY 4th BALL` / `1921` 三行分别命中

## 产出

- `film-suite-research/研习报告/闪灵_研习报告.md`（封闭空间叙事/氛围机制/库布里克冷峻/冬眠时间结构/日常异化/画面锚点 12 个）
- `film-suite-research/技法卡片源稿/闪灵_技法卡片.md`（8 张卡片）
