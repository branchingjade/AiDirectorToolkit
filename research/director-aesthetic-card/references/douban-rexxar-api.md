# 豆瓣 Rexxar API 长评直抓配方（2026-08 英雄本色轮实测）

**场景**：研习报告/技法卡片需要豆瓣长评（影评）的标题、热度、全文——网页端（movie.douban.com）对 curl 只回 ~3KB JS 壳或 302 到 sec.douban.com 验证码；r.jina.ai 对 subject 页也只回「载入中...」；m.douban.com 手机页同样只回「载入中...」。Rexxar 移动 API 是**免浏览器、免验证码、免 jina** 的直连通道。

## 三端点（全部普通 curl 即可，需手机 UA + Referer）

```bash
UA="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
REF="https://m.douban.com/movie/subject/<id>/"

# 1) 片名 → subject id（无需 Referer；中文参数要 URL 编码）
curl -s "https://movie.douban.com/j/subject_suggest?q=%E8%8B%B1%E9%9B%84%E6%9C%AC%E8%89%B2" -A "$UA"
# → JSON 数组 [{title, year, id, url}]，按 year 选对条目（同名多部时）

# 2) 热门长评列表（含 abstract/标题/有用数/id/total）
curl -s -A "$UA" -H "Referer: $REF" \
  "https://m.douban.com/rexxar/api/v2/movie/<id>/reviews?start=0&count=20&sort=hotest"
# → {"start":0,"count":20,"total":812,"reviews":[{id,title,abstract,useful_count,rating,...}]}
# 翻页改 start=20/40/...；sort=hotest 按热度。abstract 是全文前 ~200 字的截断。
# ⚠️ 翻页恒定 count=20（异形轮 2026-08 实测）：count=30 的首页可行，但 `start=30&count=30` 返回 {"total":0,"reviews":[]} 空壳；改 start=20&count=20 即正常——翻页参数保持 count=20、start 步进 20，看到 total 变 0 先查 count 是否 >20。

# 3) 单篇长评全文（content 字段 = HTML，剥标签即得正文）
curl -s -A "$UA" -H "Referer: $REF" "https://m.douban.com/rexxar/api/v2/review/<review_id>"
# → {"title":..., "content":"<div id='content'><p>...</p>...", "useful_count":...}
```

## 关键细节

- **搜索类端点需登录，suggest 类免登录（芙蓉镇轮 2026-08 实测）**：`m.douban.com/rexxar/api/v2/search?q=<词>&type=1001` 返回 92 字节壳 `{"request":"GET /v2/search","msg":"need_login","code":103}`——rexxar 搜索端点必须登录；免登录定位 subject id 只有第 1) 条的 `movie.douban.com/j/subject_suggest`（芙蓉镇=1297880 一次命中，按 year 字段区分同名条目）。任何"搜索定位失败"先检查是不是误走了 rexxar search 而非 j 端点。**suggest 经 r.jina.ai 代理 403 时直连可用（莱昂内轮 2026-08 实测）**：`https://r.jina.ai/https://movie.douban.com/j/subject_suggest?q=...` 直接 HTTP 403，但 iPhone UA + `Referer: https://movie.douban.com/` 直连一次全中五条（西部往事=1293394/荒野大镖客=1302522/黄昏双镖客=1295586/黄金三镖客=1401118/导演条目=1013894）——jina 是兜底不是第一顺位，suggest 族先直连、403/空数组再换道。**⚠️ j/subject_suggest 空数组变体（费穆狼山轮 2026-08 实测）**：`j/subject_suggest` 不再报错而是直接返回 `[]`（HTTP 200 空数组，非 need_login 壳、非 404）——看到 `[]` 别反复试不同编码/写法，直接走下一行的 DDG+jina subject 兜底（狼山喋血记=1461808 一次命中）。
- **j/search_suggest=PC 端搜索建议免登录通道（特吕弗轮 2026-08 实测）**：rexxar 搜索族全灭 + j/subject_suggest 空数组双失败时，`https://www.douban.com/j/search_suggest?q=<URL编码词>`（带 `-H "Referer: https://www.douban.com/"`）一次命中——返回 JSON `cards[]`（每条含 `url: movie.douban.com/subject/<id>/`、year、card_subtitle 可核对年份与导演），朱尔与吉姆=1292338/射杀钢琴师=1298095/黑衣新娘=1303544 三连中零失败，日以作夜=1293299 经 zhwiki 渲染页外部链接拿到后同通道互证；与 subject_suggest 同属免登录 suggest 族，作其空数组后的第二兜底（排在 DDG+jina 之前），cards[0] 即目标片时直接可用。
- **rexxar 搜索族端点退化 + DDG subject 兜底（降临轮 2026-08 实测）**：`m.douban.com/rexxar/api/v2/movie/suggestion?q=<片名>` 不再返回目标片（返回一批 2025-2026 无关新片）、`/v2/subject_suggest` 直接 404 `traversal_error`、`/v2/search` 只回 `smart_box` 市场内容（专栏/付费课）——m.douban.com 的 rexxar 搜索族全灭时**先别认定是反爬**，改走 DDG 经 r.jina.ai 搜 `site 或裸词 douban.com/subject <片名> <年份>`，从结果 `uddg=` 参数解出真实 subject id（降临=21324900 一次命中）；**reviews 列表与单篇 `/v2/review/<id>` 端点仍稳定可用**，只有搜索定位需换道。**搜索引擎全灭时的 GitHub Top250 兜底（摩登时代轮 2026-08 实测）**：`j/subject_suggest` 空数组 + `j/search_suggest` 无果 + DDG/Bing/百度百科经 r.jina.ai 全 CF 壳（搜索路线整体失效）时，改走 `api.github.com/search/repositories?q=douban+top250`（免登录免 token，10 次/分限流够用）→ 找含 Top250 数据文件的仓库（Mayandev/where-is-douban250 的 `where-is-top250.csv` 含片名/年份/评分/subject URL，摩登时代=1294371 一次命中）——Top250 内老片（1930s-1990s 经典）此通道最稳；拿到 id 后必须经 `/v2/movie/<id>` 或 `reviews` 端点按片名/影评内容确认归属，防 id 猜错。
- **缺 Referer 的错误签名（出租车司机轮 2026-08 实测）**：reviews 端点不带 Referer 时返回 `{"request": "GET /rexxar/v2/movie/<id>/reviews", "msg": "invalid_request_1284", "code": 1287}`（`total=None` 且 `got=0`）——看到该签名先补 `-H "Referer: https://m.douban.com/movie/subject/<id>/"` 再谈别的；subject_suggest 端点无需 Referer。**单篇 review 全文端点缺 Referer 是另一种签名（斯科塞斯轮 2026-08 实测）**：`/rexxar/api/v2/review/<id>` 无 Referer 直接 HTTP 400 Bad Request（非 1287 JSON）；带任意 m.douban.com 页 Referer（如 `https://m.douban.com/review/<id>/` 或 subject 页）即通——批量抓全文前先带 Referer，别用「无 Referer 试一轮」浪费 22 连败。
- **ID 猜错的症状模式（《一一》轮实测）**：手猜 ID 会让所有路由"同时坏掉"——m 站 subject URL 404、PC 页跳 sec.douban.com 墙、jina 回 JS 壳「载入中」。三路死因其实是同一个：ID 不存在（一一=1292434，猜的 1292400 是错的）。**任何路由失败都先回 subject_suggest 核 ID（片名+年份比对），再谈反爬**——别在三条死路上各试一轮才回头。
- **用 execute_code + subprocess 循环抓**（每篇 0.4s sleep），一次抓 8-10 篇 + 扫描多个列表页零压力；列表页 `total` 字段是影评总数（《英雄本色》812 篇）。
- **关键词扫描选稿**：抓列表页时对 `title+abstract` 做关键词过滤（如"白鸽/枫林阁/拿回来/暴力"），命中再抓全文——比盲抓全文省流量省上下文。注意：**abstract 里没有的意象不要下结论**（《英雄本色》"白鸽"在 10 篇热门影评 abstract 中零命中，最终标「未取证到」，未杜撰）。
- **来源类型扫描（龙门客栈轮新增）**：另按**来源类型**关键词过滤标题——`访谈|节选|对谈|专访|语录|自述`、`翻译|...|XX评` 组合（外国经典影评/《电影手册》文章全译转帖，四百击轮 2026-08：里维特评《四百击》13 有用=《电影手册》1959-05 p.37-39 全译，标题即「翻译|在安托万家那边|里维特评《四百击》」）——影迷把访谈书节选整篇转帖成影评（《胡金铨武侠电影作法》对谈专章 6080 字 = review/15239527），是华语老片导演一手材料的隐藏通道；`useful_count > 100` 的资料型长文优先抓（300/229/90 有用三篇撑起全卡）。转帖稿引用注明"转帖节选，原书未核验"。
- **虹膜译稿转帖通道（斯科塞斯轮 2026-08 实测）**：标题带「【译】」、作者行「译者：csh」、译文首发于《虹膜》的转帖=外国导演/经典影评一手原话中译通道——凯尔经典影评全译（出租车司机/好家伙）、Film Comment 摄影指导访谈全译（普列托谈爱尔兰人暴力「像发条」+年代乳剂方案）、NYT 双雄长谈（斯科塞斯表演观原话）。选稿关键词表补「【译】/访谈/摄影指导/书摘」；此类转帖为中译，英文原句未回源时诚实声明标注。
- **转帖访谈回源英文原档（沙丘轮 2026-08 实测）**：豆瓣长评整篇转帖外国媒体导演访谈中译（沙丘轮：review/13945789 内含 WIRED Q&A 全译）时，**可回源升级引文等级**——CDX `url=<站点>/story/<导演名>*&collapse=urlkey` 定位真实 slug（WIRED 真实 slug `denis-villeneuve-dune-q-and-a`，猜的 `-dune-interview` 404；slug 不能猜），r.jina.ai 直抓英文原档，与中译逐句配对；配对成功则引文标注「英文原句已回源核验」而非「转帖」，诚实声明相应升级。WIRED/卫报类站点 CDX 域名级通配 403 时，`站点/story/<名>*` 短前缀可用。
- **短评引文校验兜底（龙门客栈轮新增）**：写报告引用短评金句时，若条目页存档中该句 MISS，走 `rexxar/api/v2/movie/<id>/interests?count=30&start=<0,30,...>&order_by=hot` 翻页抓 60 条核对原文——**interests 端点带 `user.name`**（reviews 列表 API 的 author 是 None），署名引用短评必须走 interests。
- **全文清洗**：`re.sub(r"<[^>]+>", "", content)` + `html.unescape()`。
- **⚠️ 原始 JSON 是 \uXXXX 转义（徐克轮实测）**：curl 直接存的 reviews/review JSON 里中文全是 `\uXXXX`——对原始文件 grep 中文必 MISS，引文校验前必须 `json.loads` 解码（校验脚本里 `d = json.loads(open(fn, encoding='utf-8').read())` 后对 `content+title+abstract` 拼接文本比对）。另外 content 字段正文里夹 HTML 标签（如 `<br>` 断句）——剥标签后引文与原文的差异只是换行，属合法省略，不算 MISS。
- **⚠️ abstract 引文归属坑（徐克轮实测）**：列表端点（`reviews?start=0&count=20`）返回的 abstract 是**该条 review 自己的**全文截断——从列表页抄金句时先记下所在条目的 review id，引用前必须用该 id 抓全文核对（徐克轮把 review/7071519 的 abstract 金句误挂到 review/1006647 名下，写文档中途才发现补抓修正）。多条热门影评的 abstract 长得像，最容易串号。
- **作者字段在列表 API 中为空**（author: None），全文 API 的 author 也常缺——引用时标注"豆瓣影评 <id>《标题》"，不要写作者名。
- 存档命名建议：`pages/<片名slug>_review_<id>.txt`，文件头写 TITLE/AUTHOR/USEFUL。
- **失败留档**：直连 douban 网页被 sec.douban.com 拦截（`curl -L` 落到 `sec.douban.com/c?r=...`）属预期，不用重试浏览器路线，直接走 Rexxar。

- **候选 id 免登录验证端点 = rexxar `/v2/movie/<id>` 元数据（蓝丝绒轮 2026-08 实测）**：`curl -A "$UA" -H "Referer: https://m.douban.com/movie/subject/<id>/" "https://m.douban.com/rexxar/api/v2/movie/<id>"` 直接返回 JSON（title/original_title/year/actors/directors/genres/rating），搜索定位失败后批量验证候选 id 的第一端点——1293925=橡皮头、1293092=沙丘 一次验明（秒级，免登录）。**返回 `{"code":1000,"msg":"need_permission"}` = 该 id 不是可公开访问的电影条目**，直接弃用。
- **第三方搜索快照里的豆瓣 id 不可信（蓝丝绒轮实测）**：百度/网盘/下载站标题常拼「<数字>-豆瓣-x.x-<片名>」蹭权重（如「1298697-豆瓣 7.6-蓝丝绒」实为盗版站标题，验证 need_permission 直接证伪）；任何渠道拿到的 id 先经 `/v2/movie/<id>` 验 title 再投入 reviews 抓取。
- **search.douban.com subject_search 经 jina 可能漏本体条目（蓝丝绒轮实测）**：搜「蓝丝绒」只返回两部周边纪录片（重访蓝丝绒 27058856 / 遗落的影像 37228575），1986 电影本体不在结果里——jina 渲染搜索页缺条目 ≠ 豆瓣无此条目，勿据此下否定结论。
- **豆瓣 id 全渠道定位失败时的降级（蓝丝绒轮实测）**：j/subject_suggest 空数组 + suggestion 退化 + search.douban.com 漏本体 + m.douban /v2/search 需登录（code 103）+ api.douban.com/v2 需 apikey（code 104）五路全灭时，可试百度搜索经 jina（结果里的 baidu /link?url= 跳转壳可 -L 跟随拿真实 URL）；仍无果则标「豆瓣长评未取证」不硬凑，英维 raw 的 ref/External links 可替代部分影评证据。

## 配套渠道（同一轮实证）

- **香港影评库 filmcritics.org.hk**：文章可经 enwiki ref 里的 `archive-url` 快照直抓（`web.archive.org/web/<时间戳>/<原URL>`）。陈嘉铭《十大香港電影－第二位：英雄本色》即此渠道——**华语片粤语台词原句的一手来源**（「我唔見咗嘅嘢要自己攞番！」）。页面正文在 `<div class="field field-name-body">...</div>` 内，剥标签即得；文章短（<5KB），无 JS 壳。
- **维基 ref 是中文影评 URL 的索引**：zh/en wiki 的 ref 常带 archive-url（on.cc、香港01、星岛等），archive-url 可直接 curl。
- 台词交叉验证模式：粤语原句（影评库/访谈）↔ 普通话流传版（豆瓣影评记录）↔ 英译（enwiki 转引）——三级对照，措辞差异写进诚实声明。
