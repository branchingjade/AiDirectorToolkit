# 《恐怖分子》(The Terrorizers, 1986) 单片研习轮来源地图（2026-08，第二十八轮并行批）

杨德昌补代表作单片轮，创作极=多线结构/都市冷漠。产出《恐怖分子_研习报告.md》+《恐怖分子_技法卡片.md》+ 校验脚本 `_verify_terrorizers.py`。与《杨德昌_手法体系深化.md》（第二十七轮）构成双向互引（对方以 [卡恐怖分子·研S5/7] 引本轮存档）。

## 存档对照（新抓 18 项，研S1-18）

| # | 存档文件 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | yang_terrorizers_enwiki_raw.txt | 英维 `Terrorizers`（裸名，无冠词）raw | Plot 全本（prank calls 启动机制）/Jameson "the postmodern film"/杨德昌 "puzzle" 自述/双结局模糊性/奖项 |
| 研S2 | yang_terrorizers_zhwiki_raw.txt | 中维「恐怖分子 (電影)」raw（繁体、无年份） | 剧情/角色表/奖项/片长 109 分钟/票房 |
| 研S3 | yang_terrorizers_baike_jina.txt | 百度百科电影词条 3654819（jina） | 上映/剧情一句话/金马奖/2007 洛杉矶"里程碑电影"；缪骞人词条"最佳女配角"双口径 |
| 研S4-18 | yang_terrorizers_review_*.txt | 豆瓣 rexxar 15 篇长评全文 | 8605793(1742) 冷枪/9890443(929) 细节=杨德昌灵感自述+建筑类比/1034778(777) 四段循环/8693873(409) 三线+红色+双结局/2020605(282) 反人人皆恐怖分子/1190262(134) 周郁芬独白+唯一"恐怖"二字/5459117(56) 平行空间/12600044(34) 方格牢笼+门框构图+电话顺序重组/12742219(6) 画框与窗+开场长镜/8115896(48) 电话非根本原因/4493741(10) YY 结局/17313793(24) 荣格人格面具/8650014(44) 两次枪声+标题多义/12603250(27) 个人主义困境/8239550(16) 共谋论 |

## 存量复用（对应主卡片编号）

yang_wiki_edward [卡S1] multi-narrative urban thriller / yang_zhwiki_yiyi3 [卡S4] 百大华语电影 41+12 位 / yang_criterion_yiyi [卡S6] Kent Jones "gridlike coolness" / yang_criterion_hunghung [卡S8] 鸿鸿 "society killing its own people"+恐怖分子是鸿鸿首部合作片 / yang_senses_austerlitz [卡S11] 六人物+照片墙+艺术家主题→一一 / yang_bordwell_absd [卡S12] network narrative+jerky coincidences+双血泊一虚一实+windows and partitions+planimetric 三镜 / yang_rosenbaum_exiles [卡S14] crisscrossing strands+Jameson 光论 / yang_nyrb_taipei [卡S15] prank calls 引爆+cool urban alienation+impersonal buildings

## 任务预设验证

- 多线结构 ✓（Bordwell network narrative + 英维 multi-narrative + Austerlitz 六人物 + 华语三线/四段读法）
- 巧合 ✓（jerky coincidences + "begins at random" + 8693873"偶然之下的必然性"）
- 恶作剧电话引爆点 ✓ 升级一手（9890443 长评转述杨德昌亲述灵感=被锁家里的女孩乱打电话真事，含美军打火机徽章细节）
- 都市冷漠 ✓（NYRB cool urban alienation + Jones gridlike coolness + 8693873 极端冷漠 + 4493741 冰冷）
- 结尾交汇 → 细化为双结局悬置（Bordwell "Two final bloodbaths, one imaginary" + 英维 ambiguous + 4493741 YY 读法）
- 与《一一》结构关系 ✓ 五链（network 家族/巧合驱动→仪式骨架/情绪进化/小强→洋洋艺术家链/鸿鸿三部曲桥）

## 通道坑（本轮新取证）

1. **英维冠词歧义**：`The Terrorizers`=Donald Hamilton 1977 小说（Matt Helm 系列，2093 字节 Infobox book）；电影在裸名 `Terrorizers`（无冠词）。{{For}} 模板即线索，探测序列加"去冠词裸名"。
2. **中维标题探测新形态**：简体+年份「恐怖分子 (1986年电影)」API redirects=1 探测显示 redirect 标志但 prop=revisions 仍 missing:True、raw 报 Wikimedia Error；list=search（srsearch=片名+导演名）一次命中「恐怖分子 (電影)」繁体无年份。redirect 标志 ≠ 可抓取，revisions missing 后直接 list=search。
3. **百度百科裸词条静默重定向到概念词条**：`item/恐怖分子` 无 id 经 jina 返回 73KB「恐怖主义」概念词条（19 世纪无政府主义者史）——体量正常≠内容正确；DDG site: 定位真实电影词条 id=3654819。
4. **juben.pro 搜索页超时**：`/search/?q=` 经 jina TimeoutError 422（networkidle 15000ms）——剧本标未取证到，不纠缠。
5. 豆瓣 subject 1305261（suggest 裸片名一次命中）；reviews 549 条，15 篇长评 0.4s 间隔连抓零失败。

## 校验记录

- 第一层手写 72 条关键引文 0 MISS（norm_zh 删引号 + 繁简映射 + 剥链接/模板 + 全空白剥离）
- 第二层自动提取 132 条引文段 54 假 MISS（译文/叙述被「」正则误捕；中文引文被双引号正则误分类为 en）
- 第三层"仅校验带 [研S#]/[卡S#] 标注引文块 + 省略号分片"56 条 0 MISS，抓到 2 真问题：8693873 拼接引文两句间原文隔"为什么？"未标省略号（补……修复）、12600044 半角冒号 vs 全角冒号（按原文直录）
- S# 对账：正文研S1-18 ↔ 来源表全一致；卡S 引用全合法
- 修正：缪骞人奖项双口径（中维/英维最佳女主角 vs 百度百科最佳女配角，并记）

## 互引

《杨德昌_手法体系深化.md》同批落盘，§2.4 以 [卡恐怖分子·研S5/7] 引用本轮存档（杨德昌灵感自述+偶然之下的必然性）→ 本轮研习报告 §5 与技法卡片诚实声明补回引链，双向互引闭环。
