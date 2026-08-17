# Storaro 研习轮 2026-08-09（摄影指导·欧系老牌 DP 来源地图）

产出：`_work/制作大师研习-20260809C/Storaro/Storaro_制作大师卡片.md`（38KB，S1–S15，89 条引语片段 grep/re 验证全过）；pages/ 15 个存档。

## 对同类任务最可复用的发现

1. **维基主条目「参考文献」段 = 一手来源索引**：`en.wikipedia.org/wiki/Vittorio_Storaro` 的 refs（L240–264）直接给出：
   - ASC 亲撰长文：`ascmag.com/articles/whos-afraid-of-red-green-and-blue`（Storaro 2017 自撰，色彩理论最完整自述：红/绿/蓝三色定义、色彩生理学、牛顿+歌德、爱森斯坦）
   - Guardian 专访：`theguardian.com/film/2003/jul/09/artsfeatures`（《Painting with light》，逐片自述）
   - ASC 新闻：`theasc.com/news/vittorio-storaro-asc-aic-honored-with-george-eastman-award`
2. **theasc.com flashback 系列** = AC 旧刊原文重发：`theasc.com/article/flashback-apocalypse-now/`（2001 年 2 月刊圆桌访谈全文，Storaro/Burum 亲述 Do Lung 桥、ENR、flashing、Hogarth/Rousseau）。检索式 `site:theasc.com OR site:ascmag.com flashback <人名/片名>`。
3. **ASC 主席专栏（President's Desk）** 常整段转引大师原话：`staging.ascmag.com/articles/presidents-desk-platos-cave` 含《末代皇帝》「太阳=全光谱/半影/第一次见影子」长段原文——转引来源，但引语是一手，可标注「转引」使用。
4. **AIC（意大利摄影师协会）官网**：`aiccine.com/interview/writing-with-light-vittorio-storaro-...`（2025-03 长访）——Bertolucci 合作史、牛顿七色结构=人生阶段、「九年教育无人教色彩」。
5. **Criterion current/posts**：影评（556=Thomson《The Last Emperor, or The Manchurian Candidate》2008 版）+ 官方博客（713=Emperor 2.0 画幅公案、728=Voyagers）——修复/画幅类公案的官方一手记载常在这里。

## 已 grep 验证的要点锚（卡片 §4 内文可直查）

- 七色=人生阶段：AIC 访谈 "seven-color structure devised by Isaac Newton... different stage of human life"
- 光谱局部叙事：Guardian "only in limited parts of the spectrum... We would know violet only when he's free from the ideological prison"
- 光=觉醒曲线：ASC Plato's Cave "he never sees his own shadow... the more light I poured on him, and the darker his shadow became"
- 三色定义：ASC RGB 长文 "Color of the PAST" / "Color of the Soul, and represents Knowledge" / "color of INTELLIGENCE and the FUTURE"；色彩生理学 "modify our metabolism and blood pressure"
- 文化叠加/人造光 vs 自然光/黑=潜意识/ENR：ASC Apocalypse 圆桌 "one culture superimposing itself on another"、"colored smoke"、"black is such an important color"、"flash the negative"
- 故宫实拍：维基 "never before been opened up for use in a Western film"、19,000 群演；Criterion 影评 "Chinese light (granted an Italian marinade)"

## 未取到清单（如实写进诚实声明，勿硬编）

- AC 1987 年 12 月《末代皇帝》摄影专文：无公开全文（theasc.com flashback 系列无此篇）
- Visions of Light (1992) 纪录片：无文字稿（维基仅确认其盛赞《同流者》）
- ICG 2004《Maestro of Light》：web.archive.org 被 r.jina.ai 403 封锁（AbuseAlleviationError 至 2035），直接 curl archive.org 未试——下轮可试直连
- Cooke Optics 访谈页：仅视频简介无文字稿
- 二手 StillsLab 2026 分析史实有误（首合作片名），只采其逐帧色板走向（暖红帝王黄→灰绿）

## 坑

- 弯引号：`wouldn't` 类片段先怀疑 U+2019，用短片段（不含引号部分）匹配
- Windows execute_code 无 grep 可执行文件：用 Python re 逐行匹配（flags=re.I + 行号）
