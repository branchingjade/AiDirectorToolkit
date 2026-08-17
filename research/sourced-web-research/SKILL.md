---
name: sourced-web-research
description: 抓取权威网页产出带来源 URL 的中文调研笔记。触发词：研究规范/格式、抓取权威网页、带来源笔记。
category: research
---

# 带来源引用的网页调研（Sourced Web Research）

任务形态：抓取 3-5 个权威页面 → 提取正文存档 → 产出每条规范/结论都标注真实来源 URL 的笔记（常为中文 markdown）。

## 工作流

1. **候选 URL 先行**：权威站优先（官方软件商、行业组织、作者本人博客、Wikipedia）。用 curl 试抓，一次批量多个。
2. **抓取**：
   ```bash
   UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
   curl -sL -A "$UA" --compressed -m 40 -o pages/raw_<名>.html -w "<名> HTTP %{http_code} size %{size_download} final %{url_effective}\n" "<URL>"
   ```
   - `-w "%{url_effective}"` 看 301 落点；**笔记里引用的应是最终生效 URL**，并标注跳转关系。
   - HTTP 000 / <200 bytes / 106-byte 壳 → 直接换源，不纠缠。
3. **正文提取**：bs4 可用则用；不可用 → `scripts/extract_text_stdlib.py pages/raw_x.html pages/format-x.txt`（stdlib 零依赖）。存档命名 `format-<来源名>.txt`，与 raw html 分开。
4. **精读 + 摘录**：对每个来源 grep/read 关键词段落，摘**原文英文句子**（引号保留），笔记中每条规范 = 中文规则 + 来源 URL + 原文摘录。
5. **写笔记**：表格列来源清单（# 编号、站点、URL、本地存档路径）；正文每条规范用 [S1]/[S2] 标来源；文末附关键原文摘录与抓取说明（404/跳转/失败源）。

## 死链恢复：Wayback CDX（关键技巧）

已知文章 URL 404 时，**别依赖 Bing/Google curl 搜索**（常返回 consent/JS 壳，正文 100+ chars 即废）。用 CDX API 按域名 + URL 关键字过滤：

```bash
curl -s -m 40 "http://web.archive.org/cdx/search/cdx?url=<域名>&matchType=domain&filter=urlkey:.*<关键字>.*&collapse=urlkey&limit=40&output=text"
```

返回行格式：`urlkey 时间戳 原URL 状态码 长度`。挑 status 200 的原 URL 直接 curl；仍 404 则用 `web.archive.org/web/<时间戳>/<原URL>` 快照。
实战：`johnaugust.com/2000/screenplay-format` 404 → CDX 过滤 `.*format.*` 定位到 `/2003/script-formatting`、`/2003/courier-12-pt-font` 仍存活（2026-08 验证）。

**快速查快照（先于 CDX 用）**：`curl -s "http://archive.org/wayback/available?url=<完整URL>"` 返回 JSON，`archived_snapshots.closest.url` 即最近快照直链（`available:true` 才可用）。2026-08 实测 rogerebert.com / ascmag.com 的 403/202 反爬页均有快照，直接 `curl -L "<快照URL>"` 即得完整正文。

**CDX 前缀查询可能空手而归**：`url=<域名>/<路径前缀>*&matchType=prefix` 实测返回空（rogerebert.com/reviews/parasite* 无结果）；此时改回 **domain + filter 组合**必中：
`url=<域名>&matchType=domain&filter=urlkey:.*<关键字>.*&collapse=urlkey&limit=30&output=text`
实战：rogerebert.com 寄生虫影评 `/reviews/parasite-2019` 404 → domain+filter 定位真实 slug `/reviews/parasite-movie-review-2019`，还顺带挖出同站导演访谈页（"找真实 URL"场景也可用此法反查站点全部相关文章）。
**第三条路（大红灯笼轮 2026-08 实测）：url 尾部 `*` 前缀通配、不带 matchType=prefix 也可用**——`url=rogerebert.com/reviews/raise-the-red-lantern*` 直接返回 2013-2016 快照列表，一次定位 Ebert 老影评真实 slug `raise-the-red-lantern-1992`（按 great-movie 惯例猜的 URL 是 404）。判定：403 多出在域名级/长路径通配，短 slug 前缀值得先试一发；wayback available API 429 限流时 CDX 不受影响。

## 中文官方源（政府/法规站）专项（2026-08 实测）

- **搜索引擎，curl 只有 DDG html 版可用**：`curl -s -A "$UA" "https://html.duckduckgo.com/html/?q=<url编码>"`，真实 URL 在 `uddg=` 参数里（url-decode 即最终地址）。⚠️ 限流极快：连发 2+ 查询即 202 anomaly 页（body 含 "anomaly"），查询间必须 sleep 8–15s。另有失败形态（2026-08 实测）：返回 200 但内容是 ~6.7KB 的地区下拉壳页（无任何 uddg= 结果链接）——判定标准是**有没有结果链接**，别只看状态码。DDG 连续失败时直接换 Sogou（下节表格）。
- **政府站检索别依赖 Bing curl**：Bing `format=rss` 返回空、HTML 链接包成 `bing.com/ck/a` 重定向（且查询串含 `site:gov.cn` 时朴素 grep 会误匹配搜索 URL 本身）。2026-08-07 另见第二失败形态：**返回 10 条与查询无关的热门结果**（bot 检测后给垃圾）——判定标准=结果标题与查询的相关性，别只看有没有 item。注：2026-08 后续实测，**普通内容搜索 Sogou/Baidu curl 均可用**（见下节"中国站抓取要点"），gov.cn 检索仍建议用 gov 站内或 DDG html。
- **gov.cn**：http 一律 301→https，curl 必须 `-L`；旧 xinwen 全文页大量 404（链接腐烂），引用前先验状态码；国务院公报 `https://www.gov.cn/gongbao/content/<年>/content_<id>.htm` 仍存活，但 **id 不能凭记忆猜**——content_61858.htm 实测是"奥组委通知"而非《电影管理条例》，抓下来先 grep 标题再引用。
- **flk.npc.gov.cn（国家法律法规数据库）是 Vue SPA + 反爬**：curl 只能拿壳，旧教程的 `POST /api/search` 已失效（405），新 API 直连返回 500 系统异常；浏览器可走深链 `https://flk.npc.gov.cn/search?searchType=title;accurate&searchValue=<关键词>` 直接出结果。详见 `references/cn-official-sources.md`。
- **预算纪律**：官方库 SPA 难啃时，先花 10 分钟试平行权威镜像（部门官网、国务院公报、司法部行政法规库 `xzfg.moj.gov.cn/law/detail?LawID=<id>`），别把预算耗在单一 SPA 上；法规/条文原文抓不到完整版就**如实标注"未抓取/未核验"，绝不凭记忆补法条**。

## 中国站抓取要点（2026-08 实测）

| 站点 | curl 直抓 | 关键技巧 |
|---|---|---|
| Bing cn.bing.com | ✗ 返回 JS 壳空页（~6.5KB） | 别用，换 Sogou/Baidu |
| Sogou 网页搜索 | ✓ 结果页 ~140KB | 结果链接是 `/link?url=...` 重定向；**抓该链接页（约 230B 的 HTML）grep `https?://` 即得真实目标 URL**（知乎问题/专栏直链等）。⚠️ **失效形态（大红灯笼轮 2026-08 实测）：老查询的 link 页 curl 只拿页脚备案链接（JS 跳转）、r.jina.ai 渲染同样无果、WebBridge navigate 后跳回 sogou.com 首页**（链接过期或需 cookie）——解析不到就换关键词重搜或标注未取到，别纠缠 |
| Baidu 网页搜索 | ✓ 需 cookie | 先 `curl -c jar https://www.baidu.com/` 再 `-b jar`；结果 `www.baidu.com/link?url=...` 用 `curl -L` 解析最终 URL（中文路径可能乱码截断，够识别目标站点即可） |
| 百度百科 baike.baidu.com | ✗ 403（带 cookie/UA 仍 403） | curl 路线用 openapi：`https://baike.baidu.com/api/openapi/BaikeLemmaCardApi?scope=103&format=json&appid=379020&bk_key=<URL编码词条名>` → JSON 词条卡（摘要/目录/redirect/url）；未命中返回 `{"errno":2}`（15B）。**要全文正文走 WebBridge 浏览器路线**（`.J-lemma-content` 容器；裸 `/item/<名>` 会落错义项，先经 search/none 定位精确词条，见 `references/china-sites-webbridge.md`） |
| 百度知道 zhidao.baidu.com | ✓ 带 cookie | 问题页直抓；提取用 `scripts/extract_zhidao.py`（全页去标签+连续行去重；**页面含 \x00 字节需剔除**，否则 read_file 判为二进制）。找问题页：`zhidao.baidu.com/search?word=<URL编码>` 再解析结果链接 |
| 豆瓣电影 movie.douban.com | ✗ curl JS loading 壳；浏览器也被重定向到 `sec.douban.com` 安全验证空页（2026-08-07 实测） | **2026-08-07 重庆森林实战突破：rexxar 移动 API 纯 curl 可拿影评列表+全文**（免登录，配方见 `references/douban-rexxar-api.md`）：`movie.douban.com/j/subject_suggest?q=<片名>` 纯 curl 直接返回 JSON 含精确 subject id（无需 WebBridge）；`m.douban.com/rexxar/api/v2/movie/{id}/reviews?start=0&count=8&sortby=hot` 返回热门长评列表（total/标题/id/useful_count，content 为空）；逐篇 `m.douban.com/rexxar/api/v2/review/{id}` 拿全文（content 含 HTML 需剥离）。网页双路线仍挂时先试 rexxar，别急着「未取到」。**豆瓣笔记 note/ 页另走 WebBridge `/command` + snapshot 树提取**（curl/jina 只拿"载入中"壳；配方见 director-aesthetic-card `references/douban-note-webbridge.md`，2026-08-07 无人知晓轮实测拿到 206 场剧本拉片转写） |
| 360问答 wenda.so.com | ✓ | 直抓 |
| 知乎 zhihu.com | ✗ curl 403；搜索页/API 需登录（ZERR_NOT_LOGIN） | **WebBridge 问题页直链免登录可读**（Bing `site:zhihu.com/question` 找直链，见 `references/china-sites-webbridge.md`）；无浏览器时用 Jina Reader：`https://r.jina.ai/<完整URL>`。正文带导航噪声需从头精读 |

流程：搜国内内容用 Sogou/Baidu 出结果列表 → 按上表解析出直链 → 逐页抓取存档。百度文库/豆丁需登录或 JS，直接放弃。

## 英文影评/技术媒体抓取（2026-08 实测）

| 站点 | curl 直抓 | 关键技巧 |
|---|---|---|
| rogerebert.com | ⚠️ 分 URL 家族 | `/reviews/great-movie-*`（Great Movies 系列）2026-08-07 实测 **curl 直抓 ✓**（浏览器 UA，93–99KB 全文，含 Ebert 转引导演访谈原话）；其他 slug 家族仍可能 403 Cloudflare 壳 → Wayback `available` API 查快照直抓；r.jina.ai 也被 Cloudflare 挡（403 "Just a moment" 挑战页） |
| ascmag.com（ASC 杂志） | ✗ 202 + 213B 壳 | Wayback 快照可用；摄影师深度访谈在此（滤镜型号/灯光方案/画幅决策） |
| criterion.com | ⚠️ 现场站 Cloudflare「请验证您是真人」复选框（点击循环无解；早期形态为 JS 重定向到无关影片页如 Elephant Boy） | **essay 页现场站 curl 直抓 ✓**（`criterion.com/current/posts/<id>-<slug>` 全文 84-88KB 含作者署名；站内搜索 `criterion.com/search?q=<关键词>` 也是静态 HTML，`/current/posts/` 链接可直接 grep 出）。**单片页 `/films/<id>-<slug>` 是另一回事（Murch 轮 2026-08 实测）：直接 curl 返回 403 Forbidden，拿不到 essay**——要 Criterion 单片 essay 时走 essay 页/站内搜索定位，别抓 /films/ 页；抓不到就如实声明「未取到」。**补充（和田惠美轮 2026-08 实测）：curl 拿 5.6KB 壳的 /films/ 页走 `r.jina.ai` 代取成功**——返回影片页正文（简介+Special Features 列表，含「PLUS: An essay by critic ...」作者线索，可据作者名再搜 essay 直链）；essay 全文 `criterion.com/current/posts/<id>-<slug>` 也走 r.jina.ai 直取 ✓（一轮内两 URL 均成功，未遇限流）。判定：抓前看字节数，<10KB 即挑战壳 → 转 Wayback `web.archive.org/web/2023/<原URL>`；提取后必须核对标题，货不对板直接弃用 |

## 全书 PDF 抓取通道（教材站全文，2026-08 Murch 轮实测）

**找"书内全文"时，搜索引擎直接搜 `"<书名> pdf"`，电影学院/课程站常挂教材全书 PDF**——比访谈摘录强一个量级：整本书可全文 grep 验证引文，且是一手原文。实测：craftfilmschool.com 挂有《In the Blink of an Eye》修订二版全书 PDF（88 页 600KB，提取 210K 字符），一次拿齐"六项剪辑标准/眨眼理论"原文。

```python
import urllib.request, urllib.parse
# 坑①：URL 含空格/+ 直接 urlopen 会 400 Bad Request —— 必须先 quote
url = "https://www.craftfilmschool.com/userfiles/files/Walter Murch - In the Blink...pdf"
req = urllib.request.Request(urllib.parse.quote(url, safe=":/"), headers={"User-Agent": "Mozilla/5.0 ..."})
data = urllib.request.urlopen(req, timeout=120).read()

from pypdf import PdfReader
r = PdfReader(io.BytesIO(data))
text = "\n".join((p.extract_text() or "") for p in r.pages)
```

**坑②（实测踩过）：pypdf 提取文本单词间常夹制表符/诡异换行**（如 `blink\tof\tan\teye`），跨词短语直接 grep 必 MISS——第一次 grep "blink of an eye" 全 NO HIT，归一化后才命中。验证前必做：

```python
text = text.replace("\t", " ").replace("\r", " ")
text = re.sub(r"[ \t]+", " ", text)   # 折叠空白
```

**坑③：PDF 行尾断词导致跨行引文 grep MISS**（"the cut is a \"blink\" that\nseparates and punctuates"）——先 `" ".join(所有行)` 再宽松子串匹配（大小写不敏感），命中即算验证通过；卡片里引用时按语义还原断词。

**403 回退补充**：访谈站 403 时先换 curl UA 重试（transom.org 换 `curl/8.0` UA 即通）；**同文 PDF 常托管在镜像/学术站**（Transom Review 2005 全文 PDF 在 studyingsound.org/documents/reading/ 下，编号 6_Transom_Review.pdf）——被拦时搜 `<刊物名> <期号> pdf` 找 PDF 版。



## Internet Archive 全文提取通道（2026-08-09 控方证人轮实测）

找绝版剧本/旧书全文时，web_search `"<片名> screenplay"` 常直接命中 archive.org 详情页——整本可全文 grep 验证引文，比访谈摘录强一个量级。**别抓详情页 HTML，用 metadata JSON API 列文件**：

```bash
curl -sL "https://archive.org/metadata/<identifier>"    # identifier = /details/ 后那串
```

返回 `files[]`，挑 `*_djvu.txt`（纯文本全文）或 `*_text.pdf`；下载直链 `https://archive.org/download/<identifier>/<文件名>`（空格 URL 编码）。实测：《控方证人》Final Script（Wilder & Kurnitz，1957-06-10 标注版）174KB 全文一次到手，还白捡一条实物证据——剧本内印着 "THE FINAL 10 PAGES OF THIS SCRIPT WILL NOT BE ISSUED..." 保密声明。

**⚠️ djvu.txt 是扫描 OCR，错字是常态不是意外**（实测：1s=is、Prau=Frau、thet=that、fell=fall、m faet=in fact、"eve @ "=What a、befọre=before、4=a、fret=that、"liar" 被截成 "Tr"）。引文验证必须走三级阶梯（精确 → 空白折叠 → OCR 归一化），且**字符替换必须先于去标点**——先 strip 标点会把 "1s" 的 1 吃掉，替换永不生效。完整配方、错字映射表与工作样例见 `references/archive-org-ocr-verification.md`。



电影技法调研的来源组合（详见 `references/film-criticism-sources.md`）：Wikipedia（制作事实/主题引用）＋ rogerebert.com 影评（技法功能阐释）＋ ASC 杂志（摄影技术细节）＋ 导演访谈（创作意图直接引语）。

## 维基百科批量抓取（MediaWiki action API，2026-08-05 实测）

批量抓取维基词条正文并逐条引用时，**别用 REST plaintext 端点**（`/api/rest_v1/page/plaintext/<标题>` 实测全部 404）。用 action API：

```
https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&explaintext=1&redirects=1&titles=<标题>
```

- `explaintext=1` 直接给纯文本正文（无 HTML/导航壳），逐字摘录引用零成本；`redirects=1` 自动跟随重定向（如 `Sound_bridge` → Split edit 词条正文）。
- **限流**：连续 ~13 个请求后开始 HTTP 429；请求间 `sleep(2)`，遇 429 指数退避重试（5/10/15s，最多 5 次）。25+ 词条分两批跑或统一退避循环。
- **三个标题陷阱**：①词条不存在 → JSON 里 `"missing":""`（如 `Shot list` 不存在，镜头清单内容在 `Storyboard`）；②消歧义页 → 正文是 "X may refer to:" 列表（如 `Cutaway (film)` → 正条 `Cutaway (filmmaking)`）；③重定向/替代条目在笔记里标注实际落点。**④电影条目常不带年份消歧义后缀**（2026-08-07 龙门客栈轮实测：`Dragon_Inn_(1967_film)` 404 返回 50KB 错误页，真条就是 `Dragon Inn`——别按"片名 (年份 film)"惯例猜 URL，猜前先 `action=query&list=search&srsearch=<片名>+film` 拿真实标题）。完整脚本与响应判读见 `references/wikipedia-action-api.md`。
- **zh.wikipedia 非 ASCII 标题 curl 直抓报「标题无效」**（和田惠美轮 2026-08 实测）：路径 URL 带中文标题（如 `/zh-hans/和田惠美`）返回「标题无效 / invalid UTF-8」错误页；修复用 action API 的 `prop=parse&prop=wikitext`（注意与英文条惯用的 `prop=extracts&explaintext=1` 不同——parse 返回 wikitext 需自解析模板/表格，但正文引语与 `<ref>` URL 都在）：
  ```bash
  curl -sL -A "$UA" --get --data-urlencode "action=parse" --data-urlencode "page=和田惠美" --data-urlencode "format=json" --data-urlencode "prop=wikitext" --data-urlencode "formatversion=2" "https://zh.wikipedia.org/w/api.php"
  ```
  JSON 的 `.parse.wikitext` 即词条正文，ref 段能挖出一手访谈直链（本轮凭此拿到 LA Times 2006《A costume design empress》专访 URL）。
- 存档仍按 `pages/pro-<关键词>.txt` 一份词条一个文件，最终笔记的英文摘录从存档 grep 逐字复制。
- **维基引用区 = 访谈 URL 金矿**（2026-08-07 实测，搜索引擎全灭时的主通道）：对已抓回的维基条目 HTML 做 `re.findall(r'https?://[^"\'<> )]+', raw)` 全量提链接 → 按域名计数 → 过滤 theguardian/nytimes/indiewire/bfi/criterion 等目标媒体——得到的就是真采访/真影评直链；`<ref>` 里的 `archive-url=`/`archive-date=` 字段直接提供 Wayback 时间戳，`web.archive.org/web/<时间戳>/<原URL>` 免搜索直达全文（本次凭此拿到 BFI《视与听》2025 导演专访、IndieWire 2004 访谈、NYT 影评、Criterion 两篇全文）。详见 `references/director-aesthetics-card.md`。
- 导演技法四主题（动作编排/转场/场景镜头逻辑/表演连续性）的正确条目地图见 `references/film-directing-sources.md`。
- **电影台词原文 → Wikiquote**（2026-08-07 重庆森林实测）：`en.wikiquote.org/w/api.php?action=query&format=json&prop=extracts&explaintext=1&titles=<片名>` 拿经典台词集合。⚠️ **标题不带年份/体裁后缀**（2026-08-09 逍遥骑士轮实测：`Easy Rider (film)` 返回 missing，真条就是 `Easy Rider`——与英文维基电影条惯例相反，别按「片名 (film)」猜，但**后缀规则不是普适的——先试带 (film) 形态，missing 则试裸标题，两次都空再放弃**（2026-08-09 闪灵轮实测：`The Shining (film)` 一次命中，与逍遥骑士轮 `Easy Rider` 裸标题成功相反；一次 action API 请求成本极低，不值得赌）。注意：非英语片收录的是**英译版**，非原声逐字稿——引用时必须标注「英译版，非原声」，中文通行版台词若未核验逐字原文要如实标注「通行转述」。

## 陷阱

- **引文行号引用必须二次 grep 验证（遗传厄运轮 2026-08-09 实测，10 处漂移全被抓回）**：研习报告/卡片用 `S1:L123-127` 式行号引用时，从 sed/grep 输出"凭记忆"回填的行号会漂移（长文里差 5-40 行），且初看无感。写完产出后必须对每条引文做 `grep -n "<原文精确短语>" 存档.txt` 复核——一次查出 10 处行号错误并修正。教训：**引文文本正确 ≠ 行号正确**；行号是"定位键"，读者/后续验证脚本靠它回查，错了等于引文失效。长文件（剧本 7000+ 行）尤其如此。
- 内容站 URL 会静默 301 到另一篇文章——正文先 head 一眼确认主题匹配，别拿到标题就当成功。
- **引文自动验证三连（闪灵轮 2026-08-09 实测，27 条全量 0 真错）**：①提取器正则 `"([^"\n]{20,})"` 有两个坑——**引文内嵌引号**（如 `"Kubrick described Steadicam as being like a "magic carpet""`）会让正则从第二个引号截断产生碎片 MISS；中文转述句里嵌英文引号会被误判为英文引文——内层引号对先剥、中文转述句豁免；②归一化必须**引号字符全移除**（只转弯引号不够：单/双引号类型差异就假 MISS）+ **NFKD 去重音**（`György Ligeti` vs `Gyorgy Ligeti`、`Béla Bartók`——配乐清单/人名密集的引文必踩）+ 压空白/破折号/冒号；③**省略号拼接引句是硬伤**：相隔数句的两段用 `...` 拼成一条引文必 MISS——拆成逐句引用并注明「非连续」，别用省略号假装连续（闪灵轮迷宫剧情引文实测踩到）。
- **Sogou 解析出的真实 URL 可能与搜索词错位**（2026-08 实测：搜"可灵多图参考"，批量解析 /link?url= 后其中一条 CSDN 链接实为西湖心辰融资分析文）——Sogou 结果链接与标题顺序不对应，逐条解析后**必须核对正文标题/主题**，错位即弃用。
- **r.jina.ai 是 SPA 官方文档站的通用通路**：火山引擎 docs、可灵 API Overview、Runway docs、ElevenLabs docs 均实测成功（curl 直抓只能拿壳/404 页）；命令 `curl -sL -A "Mozilla/5.0" -m 60 "https://r.jina.ai/<完整URL>"`，请求间 sleep 5-7s 防限频。Fern 系文档站（ElevenLabs 等）的 404 页自带 "Were you looking for one of these?" 真实链接——**404 先 grep 该页找正确 URL 再换**；其 llms.txt 索引也可用。注意 jina 返回的是渲染后页面：可灵 API 子页会 JS 跳回主站（Overview 可用、详情页不可用），抓到后核对 Title 行。
- **中文新闻站双重编码乱码**：UTF-8 严格解码成功但正文仍是 mojibake（2026-08 央广网实测，`file` 报 UTF-8 但内容不可读）——页面在源头已双重编码，latin-1→gbk 逆向同样失败；**别纠缠，换源或标注"未核验"，绝不引用其数据**（Wayback 快照可试，但 429 就别等）。
- **抓回的 HTML 先剥 \x00 再提取**（CSDN 等页面含 \x00，read_file 直接判二进制）；剥完仍被 read_file 判 binary 或 dedup 挡重读时，用 `python -c "print(open(...).read())"` / grep 查看，别依赖 read_file。
- 视频转发帖/问答薄帖（正文 <3KB）不算好来源，继续找同站专文。
- **维基"想当然 URL"主题错位**：需求方给的条目常指向无关主题——`Character_creation` 实测是 RPG 词条（编剧人物塑造的正页是 `Characterization`，页面自带跳转提示）。抓 200 页也要核对正文第一句；编剧/银幕写作主题的完整条目映射见 `references/screenwriting-theory-sources.md`（含 `Dialogue_in_fiction` 404→`Dialogue_in_writing`、`B_story` 301→`Subplot` 等）。
- 视频转发帖/问答薄帖（正文 <3KB）不算好来源，继续找同站专文。
- 不要用 `-s` 静默后不查 `%{http_code}`：404 页也可能返回 200 且大小正常。
- 存档目录常混有其他任务产物（如 film-suite-research 共享目录）：只认自己本次生成的前缀文件，不删不碰他人文件；并行任务同页同名提取覆盖前，核对来源 URL 相同（同 URL 同内容覆盖无害）。
- **抓取前先 ls pages/ 找同主题前缀存档**（2026-08-07 重庆森林实测）：并行/前序子代理的存档是免费素材——本次直接复用前序「王家卫」任务的英文维基+访谈存档，还借机发现其 Criterion 存档实为错页（Night Train to Munich），省掉一次重复踩坑。复用前仍要核对标题/来源 URL。**⚠️ pinyin 前缀会跨片轮碰撞（英雄轮 2026-08 实测）：`yingxiong_*` 前缀 11 篇豆瓣长评+baike+imsdb 全是《英雄本色》(1986) 而非《英雄》(2002)**——同 pinyin 前缀被不同片轮重复使用，`ls | grep` 命中后必须核对 subject id/正文首行，新轮存档用区分前缀（hero2002_*）。
- **Windows 主机上 search_files 对 `C:/...`/`/c/...` 路径报 "系统找不到指定的路径"**（目录+glob 形式同样失败）→ 精读大文件改回 terminal grep（MSYS 路径可用）；read_file 不受影响。**另一形态（2026-08-09 实测）：MSYS 路径当参数传给原生 Windows Python 会被吞成 `C:\c\Users\...` 报 No such file**——`python script.py` 的参数路径改用 `C:/Users/...` 正斜杠盘符形式（或 `cd` 到目标目录后传相对路径）。

## 支持文件

- `references/douban-rexxar-api.md` — **豆瓣 rexxar 移动 API 配方**（2026-08-07 重庆森林实测）：subject_suggest 纯 curl 拿 id → 影评列表 → 逐篇全文，三步端点/UA/Referer/字段结构与陷阱（列表 content 为空需 detail API、content 含 HTML、引用用网页版 URL）。
- `references/china-sites-webbridge.md` — 中国内容站 WebBridge 浏览器路线（2026-08-05 实测）：百度百科精确词条定位（裸 URL 会落错义项）+ 全文提取、豆瓣 subject_suggest API 拿精确 id、知乎免登录读回答的 Bing 直链绕过（搜索页/API 均 ZERR_NOT_LOGIN）、知乎导航超时但 tab 存活的处理。

- `references/film-criticism-sources.md` — 电影技法调研来源地图（2026-08 实测）：Wikipedia/rogerebert.com/ASC/导演访谈四级来源分工、各站反爬与 Wayback 恢复、criterion.com JS 跳转陷阱、多片对比笔记模板。
- `references/screenwriting-theory-sources.md` — 编剧理论调研维基条目地图（2026-08 实测）：人物/类型/对白/序列副线四主题的正确条目与陷阱（Character_creation 是 RPG 词条、Dialogue_in_fiction 404→Dialogue_in_writing、B_story 301→Subplot、Screenwriting 页含 Frank Daniel 八序列法节拍表）。
- `scripts/extract_text_stdlib.py` — 无 bs4 的 HTML→纯文本提取（跳过 script/style/nav，块级换行，折叠空行）。用法：`python extract_text_stdlib.py <in.html> <out.txt>`
- `scripts/extract_zhidao.py` — 百度知道问题页→可读文本（去标签+连续行去重+\x00 剔除）。用法：`python extract_zhidao.py raw_zhidao_<id>.html`，输出 `cn-format-zhidao-<id>.txt`
- `references/cn-official-sources.md` — 中国大陆政府/法规站抓取速查（2026-08 实测）：flk.npc.gov.cn SPA 结构/API 端点/反爬行为、gov.cn 公报 URL 模式、国家电影局 chinafilm.gov.cn 栏目结构、司法部行政法规库、浏览器工具对中文政府页编码错误的 CDP 解法。
- `references/wikipedia-action-api.md` — 维基批量抓取脚本与限流退避（2026-08-05 实测）：action API 端点、429 退避参数、missing/消歧义/重定向三陷阱判读。
- `references/film-directing-sources.md` — 导演技法调研维基条目地图（2026-08-05 实测）：动作编排/转场/场景镜头逻辑/表演连续性四主题的正确条目与内容锚点（Cutaway_(film) 消歧义、Shot_list 不存在→Storyboard、Sound_bridge→Split edit 等）。
- `references/director-aesthetics-card.md` — 导演美学卡片取证工作流（2026-08-07 张艺谋/希区柯克/王家卫/库布里克四卡实测）：卡片八段结构、来源组合、渠道状态表、纪律（未取证到/引文逐字照录/神话纠正/**数字冲突双说并存**）、Goodreads 引文库通道（搜索引擎全灭时的原话检索）、特吕弗对话录引文四通道、「纪录片片名即数据」验证法、**Wayback 年份前缀直取（`/web/<年>/<URL>` 免 availability API）**、豆瓣检索三形态失败（SPA/搜索页/API 均需登录）、WebBridge 探测 404 属正常、Guardian Content API 访谈发现器（api-key=test）、Criterion 站内搜索 + essay 页现场站 curl 直抓、zh.wikipedia variant=zh-cn 一线后备（韩国片中文标题陷阱：寄生虫=生物词条→寄生上流）、用户真实浏览器慎用（tab 串页/被劫持）。
- `references/quote-verification.md` — **研习报告/技法卡片引文全量校验协议**（2026-08-07 未麻轮实测，0 MISS）：三类引文提取（反引号/块引用/行内平衡「」、只认带 [研S#] 的行、表格行跳过）、**语言感知归一化**（日文含假名→去全部空白解决换行劈词；中日英折叠空白；英文源剥 markdown 强调符；弯引号转直；**加强版：引号字符全移除**）、失配陷阱目录（繁简/引号类型/全角逗号/省略号长度/源站讹误照抄/标签张冠李戴/**多来源标签行全源兜底/省略号拼接引句拆分/无引号块引用按句拆分**）、译文注疏显式豁免表纪律。可运行样例 `film-suite-research/pages/_verify_kon_pb.py`；**通用脚本 `scripts/verify_quotes.py`**（配置 BASE/SRC_MAP/DELIVERABLES/MANUAL 四件套即用，2026-08-09 逍遥骑士轮 156 项 0 FAIL）。
- `references/production-master-cards.md` — **制作大师卡片研习轮工作流**（2026-08-09 和田惠美轮实测）：规范 8 节卡片结构、上一轮模板定位、服装设计大师来源组合（英/中维基、讣告引语、传真访谈、大报专访、Criterion essay、影迷深度分析）、双口径数据纪律（服装数量/色彩叙事）、zh.wikipedia action API 修复配方、英文站弯引号 grep 验证陷阱。
- `references/archive-org-ocr-verification.md` — **archive.org 全文提取 + OCR 引文验证**（2026-08-09 控方证人轮实测）：metadata JSON API 列文件 → `_djvu.txt` 直链下载；三级验证阶梯（精确→空白折叠→OCR 归一化）、**替换先于去标点的顺序坑**、扫描 OCR 错字映射表（1s=is / Prau=Frau / 4=a…）、严重损坏行用 IMDb quotes 交叉核对并显式标注的纪律、工作样例（49 项引文全 PASS + 剧本内保密声明实物证据）。
