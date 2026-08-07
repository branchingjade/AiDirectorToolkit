# 《末代皇帝》The Last Emperor (1987) 抓取记录与转录稿分析法（2026-08-07）

## 获取记录：三主库全灭 → Script-O-Rama Wayback 存档（新兜底形态）

- **IMSDb**：`Last-Emperor,-The.html` 与 `Last-Emperor.html` 均为 **7,785 字节空壳**（软 404，与《罗生门》同款形态，`wc -c` 判壳）
- **Script Slug**：`the-last-emperor-1987` / `last-emperor-1987` 页面与 PDF 全 404
- **The Scripts Avant**：`The_Last_Emperor.pdf` / `Last_Emperor.pdf` 404
- **WebBridge**：无扩展连接（环境态，不判死）
- **发现路径**：`scripts-onscreen.com/movie/the-last-emperor-script-links/` 聚合页（200，14KB）——不列 PDF 直链，但列出 **Wayback 存档的 Script-O-Rama 转录稿链接**：
  `http://web.archive.org/web/20210302233951/http://www.script-o-rama.com/movie_scripts/l/last-emporer-script-transcript-bertolucci.html`
  抓得 71KB HTML → 清洗得 **36,121 字符 / 1331 行完整对话转录稿**（覆盖全片：监狱开场→登基→紫禁城→天津→伪满→监狱→红卫兵→故宫结尾）。
- **通用 URL 模式**：`http://web.archive.org/web/<时间戳>/http://www.script-o-rama.com/movie_scripts/<首字母>/<slug>.html`。Script-O-Rama 原站已死，wayback 是唯一入口；聚合页 scripts-onscreen 是发现 wayback 链接的捷径。
- **诚实定性**：这是 **Dialogue Transcript（对话转录稿）**，非正式分场剧本——无 INT./EXT. 场景标题、无镜头指令、无动作描写。对白层完整，可做对白手法/母题/结构分析，但景别/镜头断言必须标注【成片】或引用影评佐证。

## 转录稿的结构分析法（无场景标题时的替代骨架）

1. **章节标题卡分段**：转录稿内嵌标题卡（`TWILIGHTIN THE FORBIDDEN CITY`=Johnston 书名卡；`Tientsin,` / `MANCHURIA` 地点卡）即幕/段边界，grep 大写短语定位。
2. **母题词 grep = 主题母题实证**：`door`（"Open the door" ×6 = 门/囚禁母题文本铁证）、`wall`、`yellow`（"It is lmperial yellow / We say it is" = 颜色权力母题）、`cricket`（开场给/结尾取回 = 物件闭环）、`butterfly`（仅 1 处 "She is my butterfly" = 奶妈=自由隐喻）——**母题论证全部用 grep 行号，不凭观片记忆**。
3. **首尾台词呼应**：同一句质疑 "Prove it" 出现两次（幼年 L212 / 老年 L1323），两次回应方式不同（暴力→记忆）= 人物弧光的台词双响法。
4. **转录稿已知错误必须标注**：结尾字幕 "He died in 1963" 与成片/维基（1967）不符；站名拼写 "Emporer"；"TWILIGHTIN" 排版合并。

## 行号引用配对校验法（越界检查不够——本次新增）

md 里写 `（Lxxx-yyy）` 引用后，**只做越界检查会漏错位**（引用在界内但指向错误台词）。正确做法：
- 构建 norm 全文时同步记录**每个字符对应的原行号**（char_line 数组）
- 从 md 提取 `(Lxxx)` 引用 + 其上下文最近引文，引文在 norm 全文 `find` → 字符位置 → 映射回行号 → 与引用行号 ±6 比对
- 末代皇帝实测：研习报告 61 个引用 0 越界 + 0 错位（但初稿确有 12 处错位靠此法抓出，含 L916→L937 差 21 行、L609→L638 差 29 行）
- **反模式**：凭记忆写"期望内容@行号"抽查会大面积误报（24/56 不符全是抽查脚本自己的期望错位，不是 md 错）——校验必须从 md 自身提取配对，不许用记忆当期望值。

## 校验器：先 split 后 norm（顺序 bug，本次踩到）

`\.{3,}` 拆段（处理跨省略号拼接引文）必须在 **norm（删非字母数字）之前**做——norm 先把 `.` 删了，`\.{3,}` 永远匹配不到，省略号拼接引文整条连续校验必误报 FAIL（首轮 47 条 7 FAIL 中 2 条是此 bug，修顺序后 41/41 直过）。另：反引号包的存档路径（`pages/xxx.txt`）要加过滤器排除，否则当摘录误报。

## 影评/权威评论取证渠道（403 时走 wayback）

- rogerebert.com 直接 curl 403 → `http://web.archive.org/web/2023/https://www.rogerebert.com/reviews/the-last-emperor-1987` 可抓全文（63KB，2026-08-07 实测）
- 维基百科 EN/ZH 直接可抓（`<div id="mw-content-text">` 到 `catlinks` 截取正文，去 table/ref 标签）
- 本片"历史改编取舍"分析素材 = 维基 Historical accuracy 段（铁屑蛋糕事件、东京审判证词等 5 项不准确清单）

## 产出（film-suite-research 研习套件）

- `研习报告/末代皇帝_研习报告.md`（结构观察/画面锚点 15/对白潜台词 3/桥段 3/诚实声明）
- `技法卡片源稿/末代皇帝_技法卡片.md`（8 张：双线提问装置、被动主角史诗、门母题、颜色权力、物件闭环、台词双响、真实空间、历史改编减法）
- `剧本原文/last-emperor_剧本_来源.md`（YAML frontmatter + 转录稿全文）
- 本片核心可偷招：**"门"母题化**——抽象主题（自由）翻译成物理动作（开门），全片 6 次重复+结尾翻转（门向游客敞开）；次选：审讯线当提问装置。
