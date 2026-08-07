# 导演美学卡片取证工作流（2026-08-07 张艺谋卡实测）

用途：为知识库产出【从成片表现/访谈/幕后取证的一手美学卡片】（区别于维基二手理论；如妖玉影视「导演美学卡片」系列，用户偏好国风意境：大漠孤烟/金碧楼阁）。产出一张卡 ≈ 1 次子代理会话。

## 卡片八段结构（照此写，保持系列一致性）

1. **风格签名**：一句话（如「色彩即叙事的东方视觉大师」）
2. **美学体系**：构图/画面、运镜/调度、色彩/光线、声音/配乐、剪辑/节奏 五小节
3. **创作思路**：工作方法，全部访谈/自述取证（本卡最有价值段）
4. **桥段设计**：2-4 个招牌桥段拆解（场景→技法拆解 2-4 条）
5. **画面锚点**：5-9 个一句话画面
6. **可复用时机**：对接用户创作偏好，用「用户要的效果→大师方案→现成桥段」表格
7. **AI 提示词对接**：转译为提示词骨架（色彩分区/仪式大场面/水墨/国风直译）
8. **⚠️ 诚实声明**：逐条列出未取到/未核验项

## 来源组合（按价值排序）

1. **en.wikipedia 影片条目**：制作事实、色彩体系、拍摄地、影评人引文（Ebert/Dargis/Washington Post 全文引用常被 wiki 转述）、学界引用（如 Harvard 专章标题本身即论点："Human Wave Tactics: Cinematic Ritual and the Problems of Crowds"）
2. **zh.wikipedia 影片+导演条目**：中文色彩解读、服装设计（和田惠美类）、幕后细节
3. **zh.wikipedia 导演条目引文区**：= 访谈金矿（见 SKILL.md「维基引文区=死链金矿」——本次凭此拿到 8 段导演自述原话）
4. **影评原文**：rogerebert.com curl 直抓成功；NYT 走 web.archive.org 回放（时间戳取自 wiki ref）
5. **导演访谈**：优先自述；其次摄影指导/美术的转述（杜可风 NYT 访谈、赵小丁 ASC 访谈）

## 渠道状态表（2026-08-07 实测）

| 渠道 | 结果 | 备注 |
|---|---|---|
| curl en/zh wiki `action=raw` | ✓ 全过、无 429 | 8 页一批，引文 URL 免费附带 |
| web.archive.org `/web/<时间戳>/<原URL>` | ✓ | 死链访谈全文（新浪读书） |
| rogerebert.com | ✓ 直抓 | 影评全文含场景描述细节 |
| baike.baidu.com | ✗ 「百度安全验证」壳页 ~2.5KB | UA/cookie 无用；需登录态浏览器 |
| movie.douban.com subject 页 | ✗ curl 302 拦截 | 需浏览器过验证（见 cn-content-site-extraction） |
| bing.com curl | ✗ JS 壳 | 换 Sogou/Baidu 或放弃 |
| html.duckduckgo.com | ✗ 无结果壳（非 202 anomaly 形态） | 判定标准=有没有结果链接 |
| Kimi WebBridge /command | ⚠️ 可能 `"no extension connected"` | 守护进程在（/status 200）≠ 扩展已连；探一次失败即放弃，不重试 |

## 纪律（写入卡片并遵守）

- 论断必有来源；每条关键论述附来源文件/URL。
- 场景描述标「影评共识/媒体记载，非逐帧核对」；俗称（如「胡杨林」）在来源中未确证时用来源原文表述（「金黄落叶林」）。
- 抓不到的标「未取证到」，不凭印象展开（本次：自然声设计、长镜头调度、张艺谋「电影是视觉艺术」直接原话）。
- 引文逐字照录：从存档 grep 出来复制，不许凭记忆。
- 存档命名 `pages/<导演>_<来源>.txt`；产出落位 `film-suite-research/技法卡片源稿/<导演>_导演美学卡片.md`。

## 方法论发现模板（每张卡最重要发现）

张艺谋卡的最重要发现是**「色彩倒推故事」**：黑色宫殿→故事定秦朝；敦煌画册里「最敦煌的颜色」→朝代定唐代；九寨沟湖水→蓝色章节。访谈原话：「对于这种大红大绿，就是本能地喜欢」「感性的选择胜过理性的选择」。写卡时把这类「一句可偷的方法论」提炼成最终回复的「最重要发现」。

## 希区柯克卡实测补充（2026-08-07 第二次会话，欧美导演）

### 搜索引擎全灭时的原话检索通道：Goodreads 引文库
本次 Google（sorry 页）、Bing（ERR_ABORTED/JS 壳）、DDG html（CAPTCHA）、Startpage（proof-of-work）、Mojeek（空）、SearX（antibot）、Brave（JS 壳）**全部被 bot 拦截**后，唯一走通的通用检索是**站点内引文库搜索**：
```
curl -sL -A "$UA" "https://www.goodreads.com/quotes/search?commit=Search&q=<引文短语url编码>"
```
返回页直接含完整引文段落（"Showing all quotes that contain ..."）。本次凭此拿到特吕弗对话录「炸弹桌下」整段原文（署名 Hitchcock，出处标注 Hitchcock/Truffaut）——比任何二手转述都完整。适用场景：找「某本书/某访谈的著名原话」；判定标准=页内有引文结果而非壳。

### 特吕弗对话录引文四通道（原书文本难直接获取时）
1. **Wikiquote 词条**：标注 "As quoted in Hitchcock (1967) by François Truffaut" 的条目 = 引文金矿（"There is no terror in a bang, only in the anticipation of it"）
2. **Goodreads 引文库**：按短语搜，拿整段论证（炸弹桌下全文）
3. **Ebert Great Movies 影评**：转引书长度访谈原话（"I was directing the viewers... playing them like an organ"）
4. **维基影片/导演条目正文**：Truffaut 1983 p.xx 脚注体系，直接引语常被转述（"33% of the effect of Psycho was due to the music" 等）

### 「纪录片片名即数据」验证法
浴室戏镜头数的权威来源是 2017 年纪录片《78/52》——**片名本身就是「78 个机位设置/52 次剪辑」的数据编码**。查维基该片条目一行即得权威数字，并据此纠正中文流行说法「45 秒 78 个镜头」（45 秒未取证到 → 标流传说法）。遇到「流传说法 vs 权威数字」之争，先找以数字命名的纪录片/书籍/论文。

### 神话纠正三连（希区柯克卡实做）
①「一镜到底」→ 实为拼接长镜头伪装（Rope：10 分钟片盒上限、4 个拼接长镜头伪装实时）；②「绿色滤镜」→ 取证到的是绿霓虹+绿光雾+全片绿色象征体系（修复时福特供原车绿漆校准色）；③「详细分镜」神话 → 维基指出多由本人/宣传放大，实为剪辑留选项。**纠正句式**：取证到的表述 + 「未取证到」标记，不直接否定流行说法。

### Ebert Great Movies 系列 = 影评实证金矿
`rogerebert.com/reviews/great-movie-<片名>-<年份>` 直抓 ✓（2026-08-07 实测，浏览器 UA），每篇含场景级技法阐释（变焦实现、剪辑功能、主题判断），且常转引导演访谈原话——是「成片表现+访谈」双证交叉的桥梁。

### WebBridge 无扩展失败模式（二次确认）
守护进程 /status 200 ≠ 扩展已连；`navigate` 返回 `"no extension connected"` 时探一次即放弃，不重试、不深排障，中文渠道记为「未取到」。

### 希区柯克卡「最重要发现」示例
炸弹桌下比喻全文（十五秒惊奇 vs 十五分钟悬念 + 「只要可能就必须让观众知情」）——一句可偷的方法论，写作模板同张艺谋卡。

## 王家卫卡实测补充（2026-08-07 第三次会话）

### 维基引用区 = 访谈 URL 金矿（搜索引擎全灭时的主通道）
所有搜索引擎被 bot 拦截后，**已抓到的维基条目 HTML 本身就是 URL 矿**：
```
links = re.findall(r'https?://[^"\'<> )]+', raw_html)   # 全量提取
Counter(domain for link in links).most_common()          # 按域名计数
# 过滤 theguardian/nytimes/indiewire/bfi/criterion/variety → 这些就是真采访/真影评
```
维基 raw HTML 的 `<ref>` 里常带 `archive-url=...` + `archive-date=...` 字段——**时间戳直接抄，`web.archive.org/web/<时间戳>/<原URL>` 免搜索直达全文**。本次凭此拿到：BFI《视与听》2025 王家卫 25 周年专访（全新一手访谈）、IndieWire 2004 戛纳专访、NYT 2013 影评、Criterion 两篇影评（Jenkins 视觉分析 + Haunted Heart）。比 Bing/DDG 搜索可靠一个数量级。

### criterion.com 新状态：Cloudflare 复选框挑战，Wayback 直通
现场站（2026-08-07 实测）不再 JS 跳转，而是 Cloudflare「请验证您是真人」复选框——点击后回到未勾选状态、循环无解。但 `web.archive.org/web/2023/https://www.criterion.com/current/posts/<id>-<slug>` 抓全文 ✓（含作者署名行）。**criterion 一律走 Wayback，别碰现场站。**

### 中文渠道新状态 + zh.wikipedia 一线后备
- baike.baidu.com 词条页 = 「百度安全验证」JS 挑战壳（~2.5KB，UA/cookie 无用）——与上表一致，确认稳定。
- movie.douban.com：curl 拿 JS loading 壳；**浏览器导航也被重定向到 `sec.douban.com` 安全验证空页**——豆瓣浏览器路线本次失效，记为「未取到」。
- **zh.wikipedia 词条（导演/影片）是中文反爬墙外的最佳一线源**：评价段/制作段信息密度极高，本次拿到铁三角（杜可风手提式/半掩式）、无完整剧本/拍摄当日给台词、「拍电影的方法有两种，第二种是王家卫的拍法」、情欲与回忆主题、《2046》「复古未来漫画色调」+ 内地审查迫使改「边拍边写」工作法等。baike/douban 被墙时先抓 zh.wikipedia 同名词条，别急着开浏览器。

### Bing `format=rss` 第二失败形态
已知形态是返回空；本次另见：**返回 10 条与查询无关的热门结果**（搜电影技巧得到词典介词条）——bot 检测后给垃圾结果。判定标准=结果标题与查询的相关性，别只看有没有 item。

### 同一访谈的两种转写 = 互证
BOMB Magazine 2001 与 IndieWire 2004 是**同一场戛纳访谈的两种转写**（同源问题、措辞略异）——两句自述用两条独立转写互相印证（「观众是邻居」「记忆色鲜活」），引用强度翻倍。写卡时发现两处文字几乎同源时，可标注「同源访谈双转写互证」。

### 纠偏示例（2046「冷调」神话）
流行说法「2046 未来冷蓝调」→ 王家卫自述为「怀旧色彩的未来幻想、漫画般风格色调、刻意不做高科技冷感」（zh.wikipedia 制作段引述）+ Glenn Kenny「幽闭的未来 CGI 大都会」。卡片写法：流传说法标「未取证到」，以自述为准并给出两方表述。

### 王家卫卡「最重要发现」示例
两条可偷方法论：①「重复是记忆的工作方式——同一首歌、同一段楼梯，每一次意义都在改变」（BFI 2025 专访原话）→ 情绪戏的重复即进度条；②「AI 可以复制，但 AI 会渴望吗？算法能理解两个人之间一个无法言说的眼神的分量吗？」——直接写进 AI 提示词对接段的诚实边界。

## 库布里克卡实测补充（2026-08-07 第四次会话，欧美导演·访谈密集型）

### Wayback 年份前缀直取 = 免 API 快照通道（新）
上一卡用 `web.archive.org/web/<时间戳>/<原URL>`（时间戳抄自维基 ref）。本次补一条更省事的：**不知道时间戳时直接 `web.archive.org/web/<年份>/<原URL>`**（如 `/web/2024/`），自动 302 到该年份最近快照。⚠️ 不要先调 `archive.org/wayback/available` API——连发 4 个即 429 限流；年份前缀直取无此问题。抓回的快照页含导航噪音（"About this capture" 时间轴），提取后从标题/首段起读或直接 grep 关键段。

### rogerebert.com 兜底三连（本次 urllib 直抓全部 403，浏览器也 403）
1. **slug 变体猜测**：改版会换 slug——`reviews/the-shining-1980` 404，但 `reviews/great-movie-the-shining-1980` 存在（Great Movies 系列）。试 2-3 个变体 × 2-3 个年份（2013/2015/2018/2020/2023/2024）。
2. **Wayback 年份前缀直取**（见上）即得全文；本次拿到 2001 首映版、闪灵 Great Movie 2006、巴里·林登 2009 三篇。
3. **无快照就诚实放弃**：Ebert《发条橙》影评在所有年份/变体下均无快照 → 标「未取证到」，不用别的影评冒充。每篇影评是「成片表现+访谈」双证交叉点（闪灵篇含 Duvall 一手访谈：哭 12 小时/天×9 个月、160 次重拍报道）。

### 豆瓣检索三形态失败（浏览器可用但检索全灭）
豆瓣**首页/影人页在自动化浏览器可加载**，但检索族全部失效：① `search.douban.com/movie/subject_search` SPA 卡在「正在搜索…」不渲染（无登录 cookie）；② `www.douban.com/search` 结果区为空（需登录）；③ `movie.douban.com/j/subject_suggest?q=` 自动化上下文 `Failed to fetch`（CORS/风控）。**影人 ID 不能凭记忆猜**：`celebrity/1054441/` 实测 302 到凯特·布兰切特页——导航后必须核对标题。结论：豆瓣检索一律路由到 WebBridge 登录态或 wayback 快照，无登录态反复试是浪费预算。

### WebBridge 探测细节：404 属正常，别误判 daemon 挂了
`GET /` 与 `POST /api/probe` 返回 404 是**正常**的（正确端点是 `POST /command`）——探测 daemon 存活别用这俩路径。真实信号：`navigate` 返回 `{"ok":false,"error":{"code":"tool_error","message":"no extension connected"}}` = daemon 在跑但浏览器扩展离线。与前卡结论一致：探一次失败即放弃，不重试不深排障。

### 纪律补充两条（写入卡片）
- **数字冲突双说并存**：同一事实两来源数字不同（闪灵单场重拍：维基 70-80 次 vs Ebert 报道 160 次）→ 两说并列标注出处，不取平均、不删一方。
- **术语级未取证**：流传的影史术语（如「强迫透视」「心跳声」「跳切」）在文献中查不到时，单列「未取证到」清单，并用相近已取证概念替代说明（本次：单点透视对称构图 + 埃舍尔式空间悖论替代「强迫透视」），不硬套术语。

### 库布里克卡「最重要发现」示例
**纠正任务预设**：任务给的「不给演员明确指导」是流传说法——一手访谈（Rolling Stone 1987、Modine 转述 Nicholson 的 take 3→40 曲线）证明实为「重拍到台词磨成别的东西」+ 长谈推入无意识表演区；Playboy 1968 蒙娜丽莎引语 = 删解释原则的直接宣言（写卡时把「一句可偷的方法论」提炼进最终回复）。

## 奉俊昊卡实测补充（2026-08-07 第四次会话，韩国导演）

### 新通道①：Guardian Content API（搜索引擎全灭时的访谈发现器）
卫报开放 API 用 test key 即可 curl，返回 JSON（webTitle/webUrl），**比任何搜索引擎都稳**：
```bash
curl -sL -A "$UA" "https://content.guardianapis.com/search?q=<关键词>&api-key=test&page-size=10&show-fields=standfirst"
# 加时间窗精确捞年代专访：&from-date=2020-01-01&to-date=2020-06-30
```
本次凭此捞出 3 篇关键卫报专访（2020-01-31「Korea seems glamorous」、2020-02-14「The real star? The house」、2025-02-22 Mickey17 期）。搜到文章 URL 后 `curl` 正文 + python 剥壳（卫报正文含大量导航，剥壳后从标题行开始切、到 "Sign up to/Explore more" 截断）。**电影导演研究优先查 Guardian tag**（`q=parasite bong&from-date=...`）。

### 新通道②：Criterion 站内搜索 + essay 页 curl 直抓（修正上节「一律走 Wayback」）
- **criterion.com/search?q=<关键词>** 现场站 curl ✓（返回 176KB 静态 HTML），`/current/posts/<id>-<slug>` 链接可直接 grep 出来——**站内搜索是发现 essay URL 的正道**（搜索引擎全灭时）。
- essay 页 `criterion.com/current/posts/<id>-<slug>` 本次 **curl 直抓全文 ✓**（Parasite「Notes from the Underground」88KB、MoM「In the Killing Jar」84KB，含作者署名行）。与王家卫卡「Cloudflare 复选框挑战」状态并存——**抓前先看字节数，<10KB 即挑战壳 → 转 Wayback**；抓到后核对标题行（历史上有 JS 跳转货不对板）。
- Criterion essay = 论文级影评，含构图/色彩/声音的成片表现分析 + 引导演自述，是「成片表现取证」最高密度源。

### zh.wikipedia 一线后备的补充细节（韩国片中文标题陷阱）
`zh.wikipedia.org/w/api.php?action=query&titles=<url编码>&prop=extracts&explaintext=1&format=json&redirects=1&variant=zh-cn` ✓（variant=zh-cn 强制简体）。
- **片名消歧义坑**：「寄生虫」词条=寄生虫生物条目；韩影条目在台湾译名「寄生上流」下。查不到 extract 时（如「杀人回忆 (电影)」返回空）改 `action=raw` 拿 wikitext 再剥模板。
- zh.wikipedia 含**采访引文的中文转述**（本次拿到「楼梯电影」自述 + 金绮泳楼梯意象影响 + 结局「确认击杀」확인사살），是 baike/douban 被墙时的中文金矿。

### 神话纠正第五、六例（任务预设 ≠ 事实，必须过证）
⑤任务预设「帕赫贝尔卡农反讽」→ 全部已取证来源（en/zh wiki 配乐段 + Criterion）均为**亨德尔《罗德琳达》选段 + 郑在日极简钢琴**，卡农判断为流传误记（帕赫贝尔常见于韩国爱情片非奉俊昊作品）；⑥任务预设「地下室黄光 vs 豪宅冷光」→ Criterion 明写豪宅为**蜂蜜色调（honey-toned）**，冷暖分区预设方向相反。写法：预设说法标「未取证到/与取证不符」，以取证为准。**任务书里的美学预设也要当流行说法一样过证**。

### 数字出入双源并存的处理
「基宇买豪宅需 547 年（IndieWire）vs 564 年（zh.wikipedia 引崔宇植）」——两源不一致时**两数都保留并标注出入**，不取其一。

### 用户真实浏览器慎用（串页+被劫持）
本次 navigate 用户真实 Chrome：Target.createTarget + Page.navigate 后页面被重定向到无关中文页（库布里克搜索/青蛇百科）——用户浏览器存在劫持/残留 tab 状态，**且乱开 tab 打扰用户**。教训：能 curl 的渠道（wiki API/Guardian API/Criterion search/essay 页）全试完再考虑浏览器；豆瓣/百科被墙时直接记「未取到」走 zh.wikipedia，别拿用户浏览器硬闯。

### AI 提示词对接段的标注纪律
奉俊昊卡的「空间阶级视觉提示词」（半地下室窗口/楼梯纵深/同一场雨两极/摩斯密码结局光语）属**从美学体系推导的创作物**——段落首行必须标注「非导演原话，创作推导」，与取证内容严格分离。

### 奉俊昊卡「最重要发现」示例
「楼梯电影」自述原话（每个空间由楼梯连接，我们称之为楼梯电影——空间即阶级是导演方法论不是影评人概括）+ 评论音轨构图语法（穷人同框/富人独框，构图直接编码亲情与裂痕）+ 神话纠正两连（亨德尔非帕赫贝尔、蜂蜜色非冷光）。
