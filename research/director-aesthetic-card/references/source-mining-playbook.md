# 取证手册（2026-08 黑泽明一轮实测）

所有命令在 git-bash / MSYS 下验证。UA 常量：
`UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"`

## 1. Wikipedia wikitext 取证

```bash
# 可 grep 的 wikitext（引用 ref/sfn 保留，可挖 archive-url）
curl -s -L -A "$UA" "https://en.wikipedia.org/w/index.php?title=<TITLE>&action=raw" -o wiki_<片名>.txt
```

- 标题带括号：`%28` `%29`（如 `Throne_of_Blood_%28film%29`）；实测部分括号标题仍失败 → 用 REST：`https://en.wikipedia.org/api/rest_v1/page/html/<TITLE>`（HTML，再清洗）
- 重定向：返回 `#REDIRECT [[X]]` → 真实条目是 X（Rashomon (film)→Rashomon；Akira Kurosawa's Dreams→Dreams (1990 film)）。**中文维基重定向常指向消歧义页**（`功夫 (电影)` → `#REDIRECT [[功夫 (消歧義)]]`，无正文）→ 用 API 搜真实条目名：`curl -s "https://zh.wikipedia.org/w/api.php?action=query&list=search&srsearch=<片名> 电影 <导演>&srlimit=5&format=json"`（功夫轮实测命中 `功夫 (2004年電影)`——带年份的繁体条目名）
- 条目名不确定：`https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=<词>&format=json&srlimit=5`
- **action=raw 404 ≠ 条目不存在**（杨德昌轮实测）：zh-wiki 的《一一》条目名就是 `一一`（无消歧义后缀），`一一_(电影)`（半角括号）与 `一一` 的 action=raw 都返回 Wikimedia 404 → 先用搜索 API 找真实条目名（`srsearch=一一 电影` 返回 title=一一/pageid），再用 REST `https://zh.wikipedia.org/api/rest_v1/page/html/<标题>`（中文 URL 编码）拿全文 HTML 再清洗（1.6MB HTML → 20KB 文本，正文完整）。中文条目常用全角括号 `（电影）` 或干脆无后缀，别按英文 `X (film)` 习惯猜标题；REST HTML 清洗后正文可能坍缩成长行，见第 3 节坑
- 挖什么：production 段（多机位/镜头数/实拍条件/天数/演员伤病）、themes 段、ref 里的 `archive-url=` 与 `quote=`（维基常把一手引文原句放进 quote 参数！黑泽明"黑墨水雨"原话就是这么白捡的）
- **ref 里的非主流域名 = 粉丝站一手访谈入口**（塔可夫斯基轮实测：nostalghia.com 的 Bachmann 1984《To Journey Within》、录音师 Sharun 访谈全文都在 Wikipedia ref 里，`http://www.nostalghia.com/TheTopics/<Name>.html` 直抓有效，老式 HTML）——grep refs 的域名，别只盯 archive-url
- 标题带撇号：`%27`（`Ivan%27s_Childhood`）
- **有 `Cinematic style of <导演>` 专条的优先抓**（诺兰轮实测：`Cinematic_style_of_Christopher_Nolan` 141KB wikitext，含 quote box 一手引文（诺兰"真诚论"整段）、波德维尔/学者分析、VFX 镜头数（620/500/850 vs 同行 1500-2000）、逐片时间线计数表、合作者表——信息密度比主条目高一个量级，是全卡的核心证据源）
- **批量收割 ref 里的存档链接（最高效一步，吴宇森轮实测：7 篇一手专访一次循环全拿到）**：
```bash
grep -oE 'https://web\.archive\.org/web/[0-9]+/[^ |}]*' wiki_*.txt | sed 's/&amp;/\&/g' | sort -u > archive_urls.txt
# for 循环逐个 curl -L 存 html——BBC/Salon/Guardian/NYT/Vulture/独立报/HK01/东方日报的专访原文全是从维基 ref 白捡的存档
```
- 中文维基 `#redirect[[简体名]]{{簡繁重定向}}` → 直接换简体标题再 action=raw 即可（吴宇森轮实测）

## 2. Wayback Machine 补源

**死链（Criterion 旧文案例）**：
```bash
curl -s -L -A "$UA" "https://web.archive.org/web/<时间戳>/<原URL>" -o out.html
# 时间戳从维基 ref 的 archive-url 直接拿，如 20101128061133
```

**Cloudflare 被挡站（rogerebert.com 案例）——CDX 发现存档 slug**：
```bash
curl -s "http://web.archive.org/cdx/search/cdx?url=rogerebert.com%2Freviews%2F&matchType=prefix&filter=original:.*seven-samurai.*&output=text&fl=original,timestamp&limit=8"
```
- 输出 `original,timestamp` 两列 → 挑一个时间戳抓快照：`https://web.archive.org/web/<ts>/<original>`
- 发现规律：Ebert Great Movies slug = `great-movie-<标题>-<年份>`（`great-movie-the-seven-samurai-1954`、`great-movie-rashomon-1950`）；裸 slug `/reviews/seven-samurai-1954` 是 404；live 站点有 Cloudflare "Just a moment..." 挑战页，直接走 wayback 别纠缠
- **普通影评 slug = `reviews/amp/<标题>-<年份>`**（2026-08 诺兰轮实测：`memento-2001`、`inception-2010`、`the-dark-knight-2008`；CDX `filter=original:.*关键词.*` 可发现，挑 2017+ 时间戳快照即得全文，含 Ebert 原文引句）
- CDX 匹配不到时换 `filter=original:.*关键词.*`（大小写敏感，用小写）

## 3. HTML → 文本统一清洗（python）

```python
import re, html
c = open(path, encoding='utf-8', errors='ignore').read()
c = re.sub(r'<script[^>]*>.*?</script>', ' ', c, flags=re.S|re.I)
c = re.sub(r'<style[^>]*>.*?</style>', ' ', c, flags=re.S|re.I)
c = re.sub(r'<[^>]+>', ' ', c)
c = html.unescape(c)
c = re.sub(r'[ \t]+', ' ', c)
c = re.sub(r'\n\s*\n+', '\n', c)
open(out, 'w', encoding='utf-8').write(c)
```
- **Criterion 现代 posts 页可 live 直抓**（塔可夫斯基轮 4/4 成功：`/current/posts/4739-stalker-meaning-and-making`、`/7453-mirror-all-is-immortal`、`/43-andrei-rublev-an-icon-emerges`、`/239-solaris-inner-space` 均 75–100KB 全文）——URL 从维基 External links/refs 直接拿（`criterion.com/current/posts/<id>-<slug>`）；先试 live、失败再走 wayback；正文容器 `<div class="pk-o-copy-body ...">`：`re.search(r'<div class="pk-o-copy-body[^>]*>(.*?)</div>', raw, re.S)`；老 post（<2015）仍按 §8 的 wayback 处理
- 清洗后先 `grep -n` 定位正文起点（很多页面正文前有几百行导航噪音，如 Criterion 的 "Current" 首页骨架、Ebert 的边栏）。
- **正文坍缩成一行巨长行**（Criterion/卫报/维基 REST HTML 清洗后常见）：read_file 会截断显示 `[truncated]`，看着像内容丢了，**文件本身是完整的**——用 python 按起止标记切片打印：`i=c.find('N ear the end'); j=c.find('This piece originally appeared'); print(c[i:j])`（杨德昌轮 Kent Jones 全文就是这么捞回的）；长文分两段 `print(body[:9000])` / `print(body[9000:])` 续读
- **wayback 快照"正文真截断"恢复法（吴宇森轮实测，与上一条不同）**：清洗文本真的只有导语+`[truncated]`字样（Guardian Kehr 2002、BFI 2019 中招），或问答被折叠 div 藏起（Salon 1997 的问答在 `toggle-group` 里，清洗后显示截断）——别信清洗结果，直接对**原始 HTML** 切片：`t = re.sub(r'<[^>]+>', ' ', raw)` 后 `t[t.find('<导语里的独特词>'):][:6000]`，或 `re.findall(r'<p>(.*?)</p>', raw, re.S)` 过滤长段。判断标准：清洗文本 <15KB 且含 [truncated] → 必回原始 HTML 找正文

## 4. 剧本行号证据

- 英译剧本存于 `film-suite-research/剧本原文/`（如 `乱_screenplay-shishido-en.txt`）
- `grep -n -i "yellow\|banner\|music" 剧本原文/<file>.txt` → 行号直接写进卡片（L688 不祥红日、L1061 红旗金"一"、L2295 真相无音乐、L2591 声音爆发点）
- 剧本层事实与成片观感冲突时（如《乱》阵营色剧本=次郎草绿/三郎天青），以剧本行号为准并注明"成片以服装设计为准，本卡只保证剧本层事实"

## 5. 中文渠道探活（先探活再投入）

```bash
curl -s -m 8 "http://127.0.0.1:10086/status"   # Kimi WebBridge：看 extension_connected 字段
```
- `extension_connected: false` → navigate 返回 `{"ok":false,"error":{"code":"tool_error","message":"no extension connected"}}`，直接放弃走英文源，不纠缠
- **WebBridge 未连接时的替代：r.jina.ai 代理**（2026-08 小津轮实测成功）：`curl -s -m 40 "https://r.jina.ai/https://baike.baidu.com/item/<URL编码词条>" -o out.txt`——输出即 markdown（Title/URL Source/Markdown Content 头），免 HTML 清洗。实测：百度百科「小津安二郎」19KB 全文、「豆腐匠的哲学」32KB 全文（含日文原书名=豆腐名言原文）。豆瓣 `https://www.douban.com/search?q=<词>` 经 jina 仍只返回登录壳（3.7KB）——豆瓣继续标「未取证到」。失败成本两次 curl 而已，值得每次都先试
- **jina-百度百科二轮复验有效**（塔可夫斯基轮：人物词条 79KB 全文，含期刊评语转述）——人物/图书词条稳定可抓；**rogerebert.com 经 jina 返回 403 AbuseAlleviationError（匿名域级封禁）**——Ebert 一律走 wayback CDX，别浪费 jina 配额
- 豆瓣分级（2026-08 诺兰轮更新）：**`m.douban.com/movie/subject/<id>/` 用 curl + UA 可直取正文**（剧情简介+短评/影评标题均在 HTML）——但 ⚠️ ID 必须核对：错误 ID 会静默返回另一部电影（1291841→《教父》），抓后必须检查 `<title>` 是否匹配目标片；长评全文走 Rexxar API（见 SKILL.md §6 / references/douban-rexxar-api.md）；PC 页与 jina 路由仍给登录壳/JS 壳。百度百科：`/item/<词>` 返回消歧义壳、`BaikeLemmaCardApi` 返回 `{'errno': 2}`、直抓返回「百度安全验证」壳（诺兰轮复验）——全部未取到正文。抓不到就标「未取证到」写进卡片诚实声明，留档失败的 html/txt 备查
- 站点反爬状态会变：探活失败≠永远失败，本轮失败只代表本轮（黑泽明轮 DDG html 失败，功夫轮实测有效——先探活再复用）
- **搜索引擎兜底链（功夫轮实测）**：Bing 经 r.jina.ai 返回 "About N results" 但内容全是无关站（anti-bot 喂垃圾）→ 换 **DuckDuckGo HTML 版**：`curl -sL "https://r.jina.ai/https://html.duckduckgo.com/html/?q=<urlencoded>"` → 提取真实 URL：`grep -oE "uddg=[^&]*" file | python -c "import sys,urllib.parse; [print(urllib.parse.unquote(l.strip().replace('uddg=',''))) for l in sys.stdin]"`
- **Brave 搜索直抓（杜琪峰轮实测，多引擎全挂时的最优解）**：同一轮里 Bing 返回验证码壳、DDG html 返回空壳、Mojeek 无结果——`search.brave.com/search?q=<urlencoded>&source=web` 配 UA 直抓有效（重复 4+ 次均成功），结果含豆瓣影评/知乎/维基/网易等真实 URL。解析：`re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.S)` 后按标题过滤（brave.com 自身链接剔除）。**中文影评检索用它找豆瓣 review id / 知乎 zhuanlan id，再走 jina 抓正文**——搜索引擎→jina 是这套管线的固定组合
- **豆瓣特定页面可抓性分级**：subject 页/影评列表页 = JS 壳（jina 只拿"载入中..."）；**具体影评页 `movie.douban.com/review/<数字id>/` 经 r.jina.ai 拿到全文 Markdown**（功夫轮：暗喜影评 review/15908346 全抓，含正文；杜琪峰轮复验：review/10082409 拿到 48KB 逐镜分镜表+书摘、review/2787430 拿到全文）。路由：搜索引擎找影评 URL → jina 直抓。⚠️ **`m.douban.com/movie/review/<id>/` 移动版是 App 墙**（只返回标题+「用 App 打开」，正文不进 HTML）——别走移动版，直接 PC 版 review URL 走 jina
- **知乎专栏经 r.jina.ai 可抓全文**（杜琪峰轮实测）：`r.jina.ai/https://zhuanlan.zhihu.com/p/<数字id>` 返回完整正文（黑社会深度解析 20KB、暗战解读 19KB）；**直接 curl zhuanlan.zhihu.com 只拿 650B 空壳**——知乎一律走 jina。搜狐 sohu.com 经 jina 返回 422 "No content available"，失败留档即可
- **jina 通道轮间不稳定**（杨德昌轮）：`r.jina.ai` 对豆瓣影评页/镜像站整轮返回 Cloudflare "Just a moment..." 壳（同 URL 功夫轮可抓、杨德昌轮全挂）——先探活一轮（抓 1 页看是不是壳），挂则立即转 zh-wiki/wayback，不纠缠；探活结果记入诚实声明
- **豆瓣/百度百科被挡时的中文证据主通道 = zh-wiki**（杨德昌轮实测）：`zh.wikipedia.org` 词条含导演言论转述（如杨德昌"人生光谱/婚礼葬礼意图"）、选角/表演指导/制作细节、票房、取景地，常比英文维基多"角色设定"级细节——条目名用搜索 API 找（见第 1 节）；正文为导演/影评人转述时卡片标注"经中文维基转引"
- **港片条目内嵌香港01 专访原文（杜琪峰轮实测）**：zh-wiki 港片条目（《鎗火》《黑社會》）的制作段常整段引用香港01（hk01.com）的导演专访并附 archive-url——杜琪峰"预算250万/4万呎菲林/只准NG 1-2次/不准乱开枪"、黑社会"创作源自社会气候"原话都是这么白捡的。挖法：`grep -n "hk01\|香港01" to_zh_*.txt` 找到引文 ref，必要时直接抓 archive-url 原文。这些原话比任何影评都硬——**先查 zh-wiki 港片条目再出去找访谈**
- **旧台湾学术/报刊页（Big5 编码）**：UTF-8 读出来是乱码 → 按字节读后依次试 `big5`/`big5-hkscs`/`cp950` 解码（中山大学论文案例：`raw.decode('big5')` 成功，转码后存 UTF-8 txt）

## 5.9 影评学术源（杜琪峰轮实测：导演美学卡的隐藏金矿）

风格/技法的**学术级二手分析**与一手访谈引用经常藏在这里，且大多反爬宽松：
- **Senses of Cinema**（sensesofcinema.com）：CTEQ 影评 + Great Directors 长文，作者常为重量级学者（Stephen Teo 写《The Code of The Mission》直接引用杜琪峰"静止受黑泽明影响"的 HKIFF 特刊采访）。直抓：`curl -sL -A "$UA" "https://www.sensesofcinema.com/<年份>/<栏目>/<slug>/"`，清洗后正文带脚注（脚注里常注明采访出处页码——转引链完整，可一路追到一手）
- **eJumpCut**（ejumpcut.org）：学术期刊，`/archive/jc<期>.2013/<作者><主题>/text.html` 形态可直抓。Gary Bettinson《Sounds of Hong Kong cinema: Johnnie To, Milkyway Image, and the sound track》——杜琪峰声音设计的权威研究（后期配音制度、环境声前置、"以静衬动"），直接补"声音/配乐"维度
- **David Bordwell 博客**（davidbordwell.net）：`/blog/category/directors-<导演名>/` 分类页直抓可用（UA 必需，无 UA 会 406 Mod Security）；CDX 对 davidbordwell.net 零命中时别纠缠，博客分类页已够用。波德维尔对银河映像视觉风格的概括（"audacious stylization"、饱和调色板）可作二手定调
- 用法：这些源给的是**评论家/学者对风格的命名与概括**（如"movement within stillness"），写进卡片时保留人名；若文中引了导演访谈（注明出处页码），可作为一手原话的转引链，但措辞以转引为准

## 6. 本轮存档示例（pages/ 命名约定）

```
kurosawa_criterion_rashomon_wb.txt   # Criterion 自传节选（wayback）
kurosawa_wiki_<片名>.txt             # 维基 wikitext
kurosawa_ebert_<片名>_wb.txt         # Ebert（wayback）
kurosawa_jims_ran.txt                # Jim's Reviews（wayback）
kurosawa_hagopian.txt                # Albany 电影笔记（wayback）
kurosawa_criterion_dreams_wb.txt     # Criterion The Color of Dreams
kurosawa_baike*.txt / kurosawa_douban*.txt  # 失败抓取留档，注明原因
ozu_wiki_<片名>.txt                  # 维基 wikitext（括号标题直接存为文件名，如 Good_Morning_(1959_film).txt）
ozu_ebert_<片名>_wb.txt              # Ebert（wayback 快照；tokyo 用维基 ref 的 archive-url，floatingweeds 用 suntimes 老快照）
ozu_rayns_tofumaker.txt              # Sight & Sound 豆腐名言（wayback old.bfi.org.uk 快照）
ozu_criterion_<主题>.txt             # Criterion 专栏（live 页是 JS 壳 → wayback 取全文）
ozu_baike_<词条>.txt                 # 百度百科（r.jina.ai 代理，免清洗）
ozu_douban_jina.txt                  # 豆瓣搜索（登录壳，失败留档）
```

## 7.5 剧本渠道取证（IMSDb + Internet Archive，2026-08 卧虎藏龙轮实测）

**IMSDb——空壳坑 + 正确 URL 形态**：
- 直接猜 `/scripts/<Title>.html` 可能返回 200 但正文为空壳（页面里 `<pre></pre>` 是空的）——**不要以 HTTP 200 判定命中**，先查页面有没有 `<pre>` 内容
- 正确流程：`/alphabetical/<首字母>` 页 grep 出真实链接（含空格形式 `/Movie Scripts/<Title> Script.html`）→ 该页 href 里拿最终正文页 `/scripts/<Title>,-<Subtitle>.html`（**逗号形式**，卧虎藏龙实测）
- 正文提取 python（IMSDb 页面 charset=iso-8859-1，需 latin-1 读取）：
```python
import re, html
raw = open('page.html', encoding='latin-1').read()
m = re.search(r'<pre>(.*?)</pre>', raw, re.S)
text = html.unescape(m.group(1))
text = re.sub(r'</?b>', '', text)          # IMSDb 用 <b> 包角色名/场景标题
text = text[:text.find('THE END.')+len('THE END.')]  # 截掉尾部广告脚本
text = re.sub(r'\n{3,}', '\n\n', text)
```
- 抓完先 grep 验证关键台词在场（`grep -n "Make a wish" file`），再做场景统计（正则 `^(INT|EXT|INT/EXT)[\.\s]` 数场景数）

**Internet Archive——绝版/修订稿剧本**（卧虎藏龙案例：搜到 James Schamus 修订稿 1999-03-25）：
```bash
# 1) 全文搜索找 identifier（mediatype:texts 限定文本类）
curl -s "https://archive.org/advancedsearch.php?q=%22crouching+tiger+hidden+dragon%22+AND+mediatype%3Atexts&fl%5B%5D=identifier&fl%5B%5D=title&rows=30&output=json"
# 2) 列文件清单（description 字段常含版本信息：编剧/稿本/日期）
curl -s "https://archive.org/metadata/<identifier>"
# 3) 下载纯文本 OCR（DjVuTXT，120KB 级）
curl -s "https://archive.org/download/<identifier>/<name>_djvu.txt" -o out.txt
```
- 版本纪律：同片两渠道常是**不同稿本**（IMSDb 流传稿 vs IA 修订稿）——卡片/报告引用必须注明渠道版本，不要混用；IA 的 DjVu OCR 有噪音（乱码行），只作版本对照与情节取证，**逐字摘录以 IMSDb 等干净文本为准**
- ⚠️ **IA 条目名≠版本，必须读正文首页确认**（2026-08-07 十二怒汉轮实测）：`12-angry-men-1957-reginald-rose` 标题/描述都像 1957 电影，实际正文首页是 **"FIRST DRAFT - 2/14/96"**（MGM 1997 电视翻拍版初稿，编剧虽同为 Rose 但非 1957 电影稿）——metadata 的 description 常是法/意语简介不标版本，下载 djvu.txt 后先 `head` 看首页页眉/日期行再决定能否当目标片稿引用；重拍版初稿可作 🟠 备查与版本对照，摘录以成片转录稿为准

**captcha 转录站 → Wayback 快照绕过（2026-08-07 十二怒汉轮实测）**：subslikescript 类对白转录站有 `captcha-protect-poj.js`（curl 只拿到 "Loading..." 壳 2KB），但 Wayback 常存全文快照：
```bash
# 1) CDX 查快照时间戳（旧快照常在 captcha 上线前）
curl -s -m 60 -A "$UA" "http://web.archive.org/cdx/search/cdx?url=subslikescript.com%2Fmovie%2F12_Angry_Men-50083&output=text&fl=timestamp,statuscode&limit=8"
# 2) 抓旧快照（2022 快照 86KB 含 2238 行完整对白转录，覆盖到结尾）
curl -s -L -m 60 -A "$UA" "https://web.archive.org/web/<ts>/https://subslikescript.com/movie/<Slug>" -o out.html
```
转录稿正文容器 `<div class="full-script">`，提取后逐行去广告行（`adsbygoogle`）即得全文。这类转录稿是**老片官方剧本未流传时对白手法研习的主源**（🟡：无角色名标注，需按上下文归位；无镜头指示）——与编剧亲笔重拍稿（IA）双份组合可支撑完整研习，转录稿为准。

## 7.6 无剧本华语片：剧本缺失证据链 + 台词证据分级（功夫轮实测）

华语片（尤其周星驰系）正式剧本大多未公开。先快速确认缺失，报告才能标"多源取证版"：
- scriptslug 猜 URL `scriptslug.com/script/<标题>-<年份>`（404）、IMSDb 条目页（返回 200 但无 `<pre>` 正文 = 无此片）、华语剧本网 juben.pro（404）、DDG 搜 `"<英文片名>" shooting script`（无有效结果）→ 四连击全空即确认无公开剧本

台词证据三级（卡片/报告引用必须标注级别，不许混用）：
1. **IMDb "Memorable quotes" 存档页**（英文译版，粤语原版措辞以翻译为准）：`https://web.archive.org/web/<ts>/http://www.imdb.com/title/<ttid>/quotes`（时间戳从维基 ref 拿，2009 年存档实测有效）；火云邪神"I only want to kill you, or be killed by you"、包租婆 "my ass" 系列、油炸鬼遗言串烧都在
2. **中文台词整理帖**（知乎"经典台词大全"类、搜狐自媒体）：中文原句但为网络流传版，标注"台词帖"，个别措辞可能与粤语原版有出入；多帖交叉验证
3. **访谈自述原文**（英文访谈存档的中文翻译，标注"访谈"）——一手优先，周星驰 AMA/MovieWeb 访谈经维基 ref 的 archive-url 直抓成功

华语片另一坑：**中文维基演员表/剧情段常比英文维基多"角色武功设定"细节**（如天残六式古琴法、包租婆狮吼功、火云邪神蛤蟆功），中英双抓交叉补全。

## 7.7 导演自传/理论书全文 = Internet Archive DjVuTXT（塔可夫斯基轮实测：《Sculpting in Time》474KB）

```bash
# 1) 按书名找 identifier（title:"..." 精确匹配）
curl -s "https://archive.org/advancedsearch.php?q=title%3A%22sculpting+in+time%22&fl%5B%5D=identifier&fl%5B%5D=title&rows=10&output=json"
# 2) 确认有 djvu.txt 文件
curl -s "https://archive.org/metadata/<identifier>"
# 3) 直接下载 OCR 全文（图书 400KB+ 级，剧本 120KB 级）
curl -sL "https://archive.org/download/<identifier>/<identifier>_djvu.txt" -o <导演>_<书名>_fulltext.txt
```

- 用途：**导演著作全文是「创作思路」节最高优先级一手源**——塔可夫斯基轮 10+ 条带页码原话直取：雕刻时光定义（"What is the essence of the director's work? We could define it as sculpting in time. Just as a sculptor takes a lump of marble…"）、拒绝蒙太奇两段（"I reject the principles of 'montage cinema'…" / "Eisenstein makes thought into a despot…"）、节奏论（"rhythm, and not editing, as people tend to think, that is the main formative element of cinema"）、梦境方法论（"cinema must expose reality, not cloud it"）、《伊万的童年》负片梦亲述、《镜子》概念来源、影像=一滴水、诗的逻辑
- 纪律：djvu.txt 是 OCR——有噪声（wiU/lives 类错字），引文按语义校正后转写；**页码取扫描页脚**（正文里的孤立数字行，如 28/29/30/63/71/83/118），与通行印本页码可能略差 → 卡片写 `p.~N` 并在诚实声明注明"archive.org 扫描件 OCR，页码以页脚为准"
- 行号证据法：`grep -n -iE "montage|sculpting in time" <file>` 拿行号 → `read_file` 读上下文核对原句 → 卡片按行号可查
- 书内引文优先于一切二手转引；找不到书则退 Criterion 自传节选/维基 quote 参数

## 7.7 Guardian Content API + Criterion 直抓（2026-08 是枝裕和轮实测）

**Guardian Content API——猜 URL 全 404 时的精确 URL 发现器**：
```bash
curl -s -m 30 "https://content.guardianapis.com/search?q=%22shoplifters%22%20kore-eda&tag=film/film&from-date=2018-01-01&to-date=2019-06-01&page-size=20&api-key=test" | python -c "import json,sys; d=json.load(sys.stdin); [print(r['webPublicationDate'][:10],'|',r['webTitle'],'|',r['webUrl']) for r in d['response']['results']]"
```
- `api-key=test` 免费可用；⚠️ **必须带 `tag=film/film` + 日期区间**——不带日期会返回无关近期文章（实测教训）
- q 支持引号短语（`%22...%22`）；输出 webUrl 即影评/访谈精确 URL，再 curl 原文
- 同款思路可扩展到其他站内搜索 API（如 Vox/卫报系）

**Criterion.com live 直抓（勿因旧轮 JS 壳结论一竿子打死——按页验证）**：
```bash
curl -s -L -A "$UA" "https://www.criterion.com/search?q=<词>" -o search.html
grep -o 'href="films/[0-9]*-[^"]*"' search.html | sort -u        # 电影条目页
grep -o 'href="current/posts/[0-9]*-[^"]*"' search.html | sort -u # essay/feature
```
- 实测可直抓：搜索页（164KB 含真实链接）、影片页（/films/<id>-<slug>，含**官方简介**——常是导演美学的浓缩一手表述，如《步履不停》"simple gestures and domestic routines"）、current posts（1743/2610/7492/7515 全文）
- **作者页 = 导演亲撰文章入口**：`https://www.criterion.com/current/author/<id>-<slug>` 列出导演自己写的 essay（是枝裕和《下一站，天国》小说后记由此挖到，一手方法论）；有影片页的导演先查作者页
- 清洗后先查正文关键词验证（对照 §8 坑：部分旧 post / 部分影片页仍会 301 到导航壳，壳则走 CDX wayback）

**百度百科（r.jina.ai）人物词条提取注意**（小津轮/是枝裕和轮双实测）：正文前有大量"相关星图/导航"垃圾（5-30KB），用 python `body.find('演艺经历')`/`body.find('人物评价')` 定位正文再切片；「人物评价」小节是媒体评语转引（搜狐/新浪/腾讯），引用时标注"经百度百科转引"非一手；「演艺经历」含中文片名/片名出处细节（是枝裕和轮：《比海更深》片名取自邓丽君日文歌歌词）

## 8. 本轮教训（坑清单）

- 大批量抓取用 for 循环 + `wc -c` 校验每个文件大小，小文件（<1KB）立刻排查（重定向/错误页）
- Criterion 旧 post URL 已死会 301 到 Current 首页（看起来"成功"但内容是导航壳）——清洗后先看正文关键词是否命中，别被文件大小骗了
- **Criterion live 页也会给 JS 导航壳**（2026-08 小津轮：/current/posts/667 直抓 5.8KB、正文仅 60 字符）——别被"能打开"骗了；用 CDX 找快照再抓：`curl -s "http://web.archive.org/cdx/search/cdx?url=criterion.com%2Fcurrent%2Fposts%2F667&fl=original,timestamp&limit=5"`，2022 快照即得全文（13KB）
- **Criterion 新式影片页 URL（/films/<id>-<slug>）也会 301 到全库浏览页**（吴宇森轮：/films/28624-the-killer 抓回 295KB 导航壳）——同样"清洗后查正文关键词"验证；CDX 前缀匹配 criterion current posts 对 essay slug 可能零命中，别纠缠、标未取证到即可
- goodreads / IMDb / **Bing（经 jina 被喂无关垃圾）** 未取到正文；**DDG html 经 r.jina.ai 在功夫轮实测有效**（黑泽明轮失败≠永远失败，先探活再复用）——引文验证失败即标未取证到，不要降级用二手转述冒充验证
- 维基转引的页码（Richie 1998 p.104 等）可信但原书未直抓时，卡片里注明"经维基转引"
- **来源编号纪律（是枝裕和轮教训）**：S# 在抓取成功当下即分配、立即登记进文末来源清单表；写卡片时只引用已登记编号，绝不后期补编——晚期补号导致 Criterion 影片页（官方简介）与 essay 页一度错挂同一编号 [S9]，返工改 3 处引用。写卡片前先 `grep -o "\[S[0-9]*\]" 卡片.md | sort -u` 与来源表对账
- 本机（Windows/MSYS）坑：`search_files` 工具对 `C:/...` 路径报 MSYS 路径转换错误（os error 3）——改用 terminal 的 `grep -n`/`awk` 或 `read_file` 按行读（诺兰轮全程 terminal grep + read_file 定位 wikitext 长行，无碍）
- 超长 wikitext 行的阅读技巧：`awk 'NR==<行号>' 文件 | fold -w 200 | head -20` 折行读；`grep -o ".\{N\}关键词.\{M\}"` 取上下文片段。⚠️ 复杂引号的长复合 one-liner（heredoc/巨型单行）会被本机命令解析器拦截（诺兰轮 sed 长命令被 BLOCKED）——拆成简单命令或写 python 脚本执行
