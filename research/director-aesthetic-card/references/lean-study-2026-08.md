# 里恩轮（2026-08-09，史诗轴·导演卡片+手法体系深化双文档）

> 任务：全链条研习大轮第 2 项，研习 David Lean（桂河大桥/阿拉伯的劳伦斯/日瓦戈医生），产出《大卫·里恩_导演美学卡片.md》+《大卫·里恩_手法体系深化.md》到 `_work/全链条研习-20260809/大卫·里恩/`。产出物 44.5KB，pages/ 22 存档 842KB，87/87 引文校验 0 MISS。
> 规范：`_work/全链条研习-20260809/规范.md`；模板：侯孝贤_导演美学卡片 + 胡金铨_手法体系深化。

## 通道矩阵（经典好莱坞/英国史诗导演轮可复用）

- **cinephiliabeyond.org = 导演轮一手口述辑录站（本轮最强单一来源）**：Sven Mikulec 2014 单页聚合了 Coates 火柴切自述（"That's nearly perfect. Take it away and make it perfect."/两帧/33 英里胶片）、Freddie Young 500mm 海市蜃楼+110°F 湿布冰箱自述（经 Nicolas Roeg 转述）、Lean 两条引语（"lightness of a pen while you are writing" / "dedicated maniacs"）、O'Toole-Ebert 对话引文——发现路径：web_search 命中，r.jina.ai 直抓 22KB 无壳。**经典好莱坞/史诗导演轮第一顺位**，先搜 `<片名> site:cinephiliabeyond.org` 或直接搜片名+filmmaking history。
- **NPR Fresh Air transcripts = 演员/导演访谈转写一手通道**：`npr.org/transcripts/<id>` 经 r.jina.ai 直抓 17KB 全文（O'Toole 2013 转写：约旦沙漠九个月/帐篷/DC-3/"No poetry" 替身轶事/骑骆驼 "Impossible"）。NPR 官网 transcripts 页无壳；发现路径：web_search `<人名> NPR interview transcript`。
- **Criterion 站内搜索 = 发行/essay 存在性负面取证（朴赞郁轮④ 再证）**：criterion.com/search?q=<片名> 经 r.jina.ai 返回 Shop 结果即发行目录证据——本轮三部曲（桂河/劳伦斯/日瓦戈）全未发行 → "Criterion essay" 渠道不存在，诚实声明写"任务预设未获证实"，不猜 essay URL。
- **Ebert 通道三态（本轮三篇全遇到）**：① rogerebert.com 直连 Chrome UA 成功（劳伦斯 100KB——jina 403 但直连可过，同 web-fetch-fallbacks 域级封禁实例）；② wayback `id_` 快照成功（桂河 20230101000000id_，52KB）；③ **单篇可能任何快照都没有（日瓦戈：2017/2018/2023 三个时间戳全 404）——换 1-2 个时间戳仍 404 即标「未取证到」，不无限换年份**。Ebert HTML 正文提取：`<div class="review-content...">` 容器正则 + meta description 首句定位（沿用用心棒轮纪律）。
- **维基 raw 重定向再证**：zh.wiki 简体「大卫·里恩」→ `#REDIRECT [[大卫·利恩]]`；en.wiki「Doctor Zhivago (1965 film)」→ `#REDIRECT [[Doctor Zhivago (film)]]`——#REDIRECT 存根即标题探测手段（既有坑，第三实例）。
- **SoC Great Directors 年份变体**：`/2003/great-directors/lean/` 404，真实 `/2004/great-directors/lean/`——年份也可能变，站内搜索 `?s=<导演名>` 一步定位（既有坑再证）；jina 渲染丢作者署名 → 引用标「2004 专条，作者待补」。

## 校验坑新实例（已登记 pitfalls-log「㊿ 里恩轮」）

- **norm 引号剥离顺序坑**：先 `.replace('"','')` 删直引号、后映射弯引号→直引号，弯引号存活 → 含引号专名（"epic"/"Ryan's Daughter"）的引文假 MISS。正确顺序：**弯→直映射在先、删引号在后**（或映射后二次删引号兜底）。本轮首轮 19 条假 MISS 中 4 条因此；修正归一化管道后 87/87 归零。经验：**批量校验首轮成片 FAIL 时，先系统性检查 norm 管道的顺序与覆盖（映射→删除的顺序、[[ ]] 剥壳保显示文本、''/_ 斜体、…省略号、重音字符），把"校验器 bug"与"真 MISS"分开，别逐条手工修**。

## 数据双口径实例（沿用「双口径并列」纪律）

- 奥斯卡数：SoC 正文「combined 21 Academy Awards」vs SoC 自身片目奖项统计 7+7+5=19——两口径并存，正文采用片目统计并标注差异。
- 海市蜃楼镜头焦距：Young 自述 500mm（一手转述）vs colorculture 调色师博客 450mm T8——以自述为准，差异如实记录。
- 劳伦斯时长四口径：221（roadshow）/200（普通发行）/184（1971 重映）/216（1989 修复）+overture/intermission/exit music（BD 导演版 227 含 11 分钟过场音乐）。

## 诚实声明模式（本轮实例）

- 未逐帧看片声明（成片描述全部引自已署名影评/口述并保留署名）。
- Criterion essay 渠道不存在（站内搜索负面证据存档 13/14）。
- 三重转引标注：Young 自述经 British Cinematographer 转述 Roeg 转述 → 标注「经三重转引」。
- 负面证据留档：ASC 404（11）、theasc 搜索无结果（19）、NYT 讣告 403（17）、Ebert 日瓦戈 404（08）、jina wayback 封禁 JSON（06 旧档）——附录登记「另存档未引用/失败存档」。
- SoC 专条作者署名未取证到（jina 渲染丢失 byline）。

## 产出与来源

- 交付：`_work/全链条研习-20260809/大卫·里恩/大卫·里恩_导演美学卡片.md`（8 节模板）+ `大卫·里恩_手法体系深化.md`（5 节变体：三阶段路线/五条演变/5 件工具/vs 黑泽明·胡金铨·徐克/诚实声明）。
- S1-S13 来源清单见卡片附录；pages/ 22 存档（维基 raw×5、SoC、Ebert×3、cinephiliabeyond、NPR、colorculture、Criterion 搜索×2、ASC、kieransomers 等）。
- 校验收尾：87/87 引文 0 MISS（含 zh.wiki 繁体短语直录校验）。
