# CHANGELOG

## v1.0.2（2026-08-05）

渠道质量分级（用户要求"登录态可解决，重要的是质量"）：

- **juben.pro 质量实测**：抽查《荒野猎人》44747字译/曹轶、《鸟人》43977字译/吉晓倩、《婚姻故事》46883字译/闵泽霖——专业译者署名、国内标准格式（`内景，农舍，夜`）；《黑客帝国》104130字中英对照（站点诚实标注 DeepSeek 翻译未核对）→ 渠道库标注升级为「高质量」，定位为**学国内标准格式的最佳范本库**
- **国外渠道按质量分级**（★★★★★~★★）：Script Slug（官方/FYC 版本）> IMSDb（全但流传稿需核版本）> SimplyScripts/Go Into the Story/John August > Daily Script/MovieScripts > Archive（扫描件看运气）> Scripts.com（社区投稿，仅查缺补漏）
- **登录态处理**：明确"免费注册/用户手动登录一次即可解决"，解决后 juben.pro 即完整渠道
- **选择规则更新**：学国内标准格式 → juben.pro 中文译本；原版 → Script Slug/IMSDb；作者亲自公开 → John August

来源：2026-08-05 质量抽查实测（juben.pro 4 部名作试读验证）+ 用户反馈（质量优先于登录门槛）

## v1.0.1（2026-08-05）

自跑测试（《肖申克的救赎》IMSDb 全文 159K +《小山回家》节选）后的实战回填：

- **🔴 纠错**：juben.pro「免费直读」→「前 N 场免费试读，全文需注册登录」（实测《你好，李焕英》试读 9 场/全文 31990 字；《小山回家》试读 2 场；页面隐藏提示登录门槛）——SKILL.md 渠道库 + references 渠道库同步修正
- **🟡 新增**：三读法补「程序化粗读」（场景正则/年份跨度/行号占比推断三幕）——agent 无法逐字读 15 万字符，统计代替通读（肖申克验证）
- **🟡 新增**：「关键场景定位法」（主题词 grep → 场景边界 → 精读 → 摘录纪律）
- **🟢 新增**：研习报告模板加「流传稿 vs 上映版差异核查」（实测 IMSDb 肖申克 1966 vs 电影 1967）
- **🟢 新增**：渠道边界标注（华语早期作者电影剧本网上多无全文，《小山回家》案例）

来源：真实项目测试发现（2026-08-05 自跑验证）

## v1.0.0（2026-08-05）

首个版本。电影树的输入侧引擎——读大师一手剧本原文，提炼技法卡片作为 AI电影编剧/导演的创作土壤。

- **渠道库**：2026-08-05 全量实测（curl HTTP 探测 + WebBridge 浏览器验证）：
  - 可用：juben.pro 名作（国内稀缺，完整剧本免费直读，国内标准格式实证范本）、IMSDb、Script Slug、SimplyScripts、Go Into the Story、John August、The Daily Script、MovieScriptsAndScreenplays、Scripts.com、Internet Archive
  - 已死：The Script Lab、sfy.ru、剧本联盟 juben68（实测确认，防止后人再试）
  - 排除：奥斯卡官网（无集中剧本页）、No Film School（非剧本库）、豆瓣（搜索不稳定，降级补充）
  - 排除：抖几句/万众/原创剧本网ju20/script.wendong/varoo（交易平台非阅读渠道）
- **大师学习法**：三读法（粗读结构/细读手法/反拆成立性）+ 技法卡片 + 研习报告 + 问题集原则（从画面出发、问题不是禁令）
- **同步修正**：screenplay-research 的 references/script-reading-sites.md（剔除死站、补 Scripts.com/Internet Archive、juben.pro 直读实证）

来源：真实调研（2026-08-05 渠道全量实测 + 知乎/微博/万兴文章二手佐证）
