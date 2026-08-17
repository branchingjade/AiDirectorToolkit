# 伊纳里图轮（2026-08-09，v2.0 导演研习轮·多线/长镜导演）

## 产出
- `_work/v2-导演研习-20260809/伊纳里图/`：《伊纳里图_导演美学卡片.md》（8 节 + 附录 S1-S10 来源清单）+《伊纳里图_手法体系深化.md》（三线归类/四组演变/五件工具箱/vs 卡隆·基氏·诺兰对比/诚实声明）
- 模板取自 `ClaudeCode/AiDirectorToolkit/妖玉影视/_知识库/references/导演美学卡片/`（侯孝贤卡 + 胡金铨深化）；v2.0 规范在轮次目录 `规范.md`（web_extract 不可用 → curl + r.jina.ai 回退链、grep 验证铁律）
- pages/ 存档 12 文件：enwiki raw ×6（主条目/狗娘/21克/通天塔/鸟人/荒野猎人）+ zhwiki（jina）+ 访谈 ×3（Collider/Film Stage/Global News）+ IndieWire 404 弃用

## 本轮新通道（好莱坞当代导演轮可用）
- **AFI 电影节映后座谈经 Collider 报道 = 好莱坞导演一手话通道**（S1）：Iñárritu & Lubezki 同台问答，含一镜动机原话（"the movie was about the ego… we have to be inside him"）、连续时间哲学（"We are trapped in continuous time"）、结尾彗星/死水母意象、"Olympic one shot just to show off"——导演+摄影同台的映后 Q&A 是导演理念一手金矿，搜 `site:collider.com <导演> <片名> interview`
- **Film Stage 转引 Arri 访谈**（S2）：Lubezki "upside down movie where you do post-production before the production"、Steadicam+手持混合、拒炫技（"dishonest, or gimmicky"）
- **Global News 加媒报道 = 导演争议/拍摄原话聚合通道**（S3）：加媒常全文转引 THR/Grantland 的导演回应原话（管弦乐调音比喻、"green screen with coffee… a piece of s***"、脱手套 40 秒失知觉）——北美拍摄争议轮（剧组离职/超支/极端环境）优先搜 globalnews.ca
- **enwiki 单片词条 Production 段 = 一镜/隐藏剪辑技术细节金矿**（S8）：Technicolor 调色师 Steven Scott 的隐藏剪切法（静止处+摇镜中插入剪切、dissolve 式调色、rotoscoping 手绘 matte）、30 天拍摄、Sony proxy 排练、"no room to improvise at all"、"we live our lives with no editing"（经 Variety 转引）——一镜到底/特效技法类论断直接 grep Production 段
- **多线/命运主题学术通道**（S7）：enwiki《通天塔》Themes 段整段转引 Poulaki《Network films and complex causality》(Screen 2014) 与 Bordwell《The Way Hollywood Tells It》(2006, p.98)——"network narrative / complex causality / pure chance / small-world effect" 术语与引文一次到手；多线导演轮的命运论述首选学术引文而非影评
- **"Death Trilogy"/hyperlink cinema 术语**：enwiki 主条目+单片词条首段自带（狗娘 = "triptych… connected by a car crash"；21克 = "non-linear fragments… coalescing"）

## 本轮坑
- **web_extract 后端 ddgs 仅搜索不可提取**（本环境工具配置）：返回 `{'success': False, 'error': 'DuckDuckGo (ddgs) is a search-only backend...'}`——不要调试结构，直接走 curl 直抓 + r.jina.ai 兜底（v2.0 规范已预设此回退链）
- **zhwiki 直连 Wikimedia Error**（1930 字节 HTML 错误页）；r.jina.ai 无 key 限速 429（`Per IP rate limit exceeded`）→ **sleep 5-10s 重试成功**；简体猜测标题 404 → `action=query&list=search&srsearch=<词>` 找真实标题——**西语人名中维转写奇特，别猜**：真实条目名是「阿利安卓·崗札雷·伊納利圖」（崗札雷≠冈萨雷斯）
- **维基词条重定向存根按字节数预检**：`Amores_Perros`→`Amores perros`（43 字节 `#REDIRECT`）、`21 Grams (film)`→`21 Grams`（1931 字节）——抓回后 `wc -c`，<2KB 先 `cat` 看是否 #REDIRECT 再换标题重抓
- **批量抓取模式**：bash `fetch()` 函数（直连 → 字节数 <800 则 `r.jina.ai/<url>` 重抓，一次循环管多 URL）——避免逐条手动重试；`&` 并行在 Hermes terminal 被禁（"Re-send WITHOUT the '&'"），用 for 循环顺序抓
- **访谈 HTML 清洗**：剥 script/style/noscript + `</p>`/`<br>`→换行 + 实体解码（&amp; &quot; &#8216; 等）后存档 .txt；Collider 导航噪音大但正文完整（正文从作者行开始）；IndieWire 2015 旧文 404 属常态，弃用不纠缠
- **诚实声明要点**（本轮已写入）：鸟人隐藏剪辑点具体数量未取证到（enwiki 只描述技术不给计数）；《荒野猎人》"全片长镜"未取证到（维基无此表述，仅"自然光+按序实拍"）；Babel 词条无导演原话（以 Poulaki/Bordwell 学者引文代）；vs 卡隆/基耶斯洛夫斯基/诺兰对比为分析判断逐条标注

## 验证
- 25 条关键摘录用 `for pat in "..."; do grep -l "$pat" *.txt; done` 批量循环验证，全部命中对应存档（含中文维基"Three Amigos"）
- 编号纪律：S1-S10 单一编号表跨两文档共用（卡片附录登记，深化文档沿用），[S#] 引用 62+35 处
