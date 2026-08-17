# 基耶斯洛夫斯基轮来源地图（2026-08-09，欧洲作者导演轮）

> 导演卡片 + 手法体系深化双文档轮；14 存档、69 条引文校验 0 真 MISS；产出目录 `_work/v2-导演研习-20260809/基耶斯洛夫斯基/`。S1-S14 编号见《基耶斯洛夫斯基_导演美学卡片.md》附录。

## 本轮的可靠流程（可直接复用）

1. **批量抓英维 raw**（`w/index.php?title=<URL编码>&action=raw` 直连无 429）：导演主条目 + 系列专条（Three Colours trilogy）+ 单片条目（Dekalog/Blind Chance/The Double Life of Veronique）+ **合作者条目（Zbigniew Preisner）**。导演主条目 41KB、十诫 21KB、普莱斯纳 15KB 一次到手。
2. **Criterion essay URL 一站收割**：一条正则扫全部已抓存档——`re.findall(r'criterion\.com/(?:current/posts|films)/[a-z0-9-]+', txt)`——6 篇 essay URL 全由此拿到，零猜 URL：
   - posts/2067 Three Colors（Colin MacCabe《A Hymn to European Cinema》2011）——三色专条+主条目都列
   - posts/1733 两生花（Slavoj Žižek《The Forced Choice of Freedom》2011）——两生花条目
   - posts/457 两生花（Jonathan Romney《Through the Looking Glass》2011）——两生花条目
   - posts/4235 十诫（Paul Coates《"And So On"...Metaphysics of the Everyday》2016）——十诫条目
   - posts/3706 Blind Chance（Dennis Lim《The Conditional Mood》2015）——机遇之歌条目
   - posts/8063 普莱斯纳三色配乐专文（Tim Greiving《Under the Sign of Sadness》2023）——**在普莱斯纳条目 External links 里**
3. **CDX 批量兜底**：6 篇 essay 直连全 403、wayback availability API 全 429 → CDX 精确 URL 查询（`url=<精确URL>&output=json&limit=3&collapse=urlkey`）拿 timestamp → `web/<ts>id_/<url>` 直抓 → `<article>` 容器剥标签 → 6/6 成功（9.9KB–30KB）。间隔 3-4s。
4. **SoC 专条**：站点搜索 `?s=Kieslowski` 定位 `2003/great-directors/kieslowski/`（Doug Cummings）→ `<article>` 容器提取 38KB。SoC 专条=导演自述转引金矿（含《Kieślowski on Kieślowski》Stok 页码脚注）。
5. **中维**：zhwiki API 连续请求 429（间隔 sleep+重试可过）；真实条目名「克日什托夫·基斯洛夫斯基」（探测候选「克里斯多夫·奇士勞斯基」等均 MISSING）。
6. **重定向探测**：`The Double Life of Véronique`（带重音）raw 返回 60 字节 `#REDIRECT [[The Double Life of Veronique]]`——真实条目名无重音；`Blind Chance (film)` 404，真实标题是 `Blind Chance`（无消歧）。

## 欧洲作者导演轮来源优先级（本轮验证）

- **enwiki 主条目可能没有 Style/Themes 段**（基氏主条目即无，纯生平+作品表）——主题/风格证据主力 = SoC Great Directors 专条 + Criterion essay；别在主条目耗 grep 轮次，直接抓这两类。
- **作曲家/合作者条目 = 配乐合作事实的一手底座**：普莱斯纳条目含 Van den Budenmayer 化名出处（"because we both loved the Netherlands"）、《Requiem for My Friend》纪念始末、欧洲统一之歌=哥林多前书 13 章、E 小调独唱跨片预演链——配乐轴论断（旋律跨片引用/虚构作曲家）全由此取证。
- **配乐署名边界必查**（本轮实例）：《机遇之歌》配乐是 Wojciech Kilar 非普莱斯纳（英维 infobox music 字段）——"普莱斯纳=基氏全部配乐"是错误笼统说法；普莱斯纳合作始于《无休无止》。
- **Criterion essay 作者署名以 essay 页头为准**：2067 实为 Colin MacCabe（任务/直觉以为 Coates——Coates 是 4235 十诫文作者），抓回必看 byline 再挂名。

## 校验实例（69 条 0 真 MISS）

- 命运原话 "It's a description of the powers which meddle with our fate... which pushes us one way or another" 是 SoC 记者插语断句格式（㉑ 坑）：整句 MISS，分片两段各自命中——写作时按两片段引用。
- 中文短语凭记忆写「道德的焦慮」MISS，中维原文是「道德焦虑电影」——校验短语必须从存档原文逐字取。
- "vocation" 短词命中 S3 也命中 S10（wrong-file 警示）——短词只作辅助，主校验用 "calm life"+"vocation" 连续组合。
- 终验对账脚本：正文 [S#] ⊆ 1..14 + 无孤儿号 + 无越界；对比节侯孝贤转引裸 [S16]/[S21] 等被误报越界 → 改写 [卡侯孝贤·S#] 前缀（小津轮三坑① 再证）。
- 卡片正文未引 S10（齐泽克）→ 补一段引用闭环孤儿号（雪国列车轮③ 再证）。

## 未取证到（诚实声明已记）

- 三色逐镜色彩量化（某色出现次数/滤镜占比）无来源。
- Ebert 三色影评全文未抓（"anti-tragedy/anti-comedy/anti-romance" 经三色维基 Themes 段转引）。
- 《Kieślowski on Kieślowski》原书未直抓（SoC 脚注页码 Stok p.113 等未逐一核对）。
- 「必然（necessity）」哲学概念无基氏直接论述，正文以 "powers which meddle with our fate" + 中维「命運是註定還是個人意志的延伸」为准。
