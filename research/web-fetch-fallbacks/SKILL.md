---
name: web-fetch-fallbacks
description: 被拦/404/Cloudflare时用——Brave Search、r.jina.ai、Wayback 取证回退链。
category: research
---

# 网页取证回退链（web-fetch-fallbacks）

> 2026-08 全链路实测（深挖《八部半》范本时验证）。核心原则：**被拦不是终点，换通道**——不要一两次失败就下"某站抓不了"的结论，按下面顺序回退，总能找到一条活路。

## 回退链总览

```
直连 curl（Chrome UA）→ 被拦？
├─ 需要"搜什么"（发现 URL）→ Brave Search HTML（唯一 curl 友好的搜索引擎）
├─ Cloudflare 质询/JS 验证 → r.jina.ai 代取（Markdown 化全文）
├─ 页面 404 / 域名已死 → Wayback Machine（id_ 原始 HTML / CDX 反查 URL）
├─ 已知条目但缺一手来源 → Wikipedia action=raw 的 External links 段
└─ 拿到 HTML 但内容在 JS 里 → 页面内 JSON 快取 / 浏览器 snapshot
```

## 1. Brave Search HTML（curl 可搜，2026-08 实测唯一存活）

Google（gbv=1 也重定向）、Bing（JS 空壳）、DuckDuckGo lite（验证码）、Mojeek（空结果）全被 bot 拦截时，Brave 直接可 curl：

```bash
curl -sL --max-time 30 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" \
  "https://search.brave.com/search?q=<URL编码查询>&source=web" -o out.html
```

提取结果链接：

```python
import re
raw = open('out.html', encoding='utf-8', errors='ignore').read()
raw = re.sub(r'<script.*?</script>', ' ', raw, flags=re.S|re.I)
links = re.findall(r'href="(https?://[^"]+)"', raw)
# 过滤掉 brave.com 自身域名，按关键词过滤候选
```

- 必须带桌面 Chrome UA，否则 403。
- `source=web` 参数保持常规网页结果。

## 2. r.jina.ai 代取（破 Cloudflare / JS 渲染）

目标站出 Cloudflare 质询（浏览器里复选框也点不动，iframe OOPIF 拦点击）时：

```bash
curl -sL --max-time 90 -A "Mozilla/5.0" "https://r.jina.ai/<目标URL>" -o out.md
# 返回 Markdown 化全文，自动过 Cloudflare
```

⚠️ **中文/非 ASCII URL 必须先 percent-encode（2026-08 李小龙轮实测）**：`curl "https://r.jina.ai/https://zh.wikipedia.org/wiki/李小龍"` 不编码直接传，r.jina.ai 会把中文按错误编码转发，目标站返回 404「标题无效」占位页（~6KB，标题乱码如 `С`）——**文件有大小、wc -c 不小，看起来像成功，实际是垃圾**。正确做法：Python 里 `urllib.parse.quote(url, safe='')` 后再拼 jina 前缀（`https://r.jina.ai/<编码后URL>`）。批量抓中文站（维基/百度百科）前统一编码，并抽查文件头 `Title:` 行确认不是「标题无效」。成功的中文维基条目通常 16KB+，百度百科 60KB+；命中 ~800B 或 ~6KB 的「标题无效」即编码失败或 ID 错误。

⚠️ **百度百科条目 URL 不用猜数字 ID（2026-08 李小龙轮实测）**：`baike.baidu.com/item/<词条名>` 不带 ID 会自动重定向到正确条目（r.jina.ai 全程跟随）；猜 `item/精武门/10353297` 式数字 ID 反而得 ~800B 占位页。词条名用简体即可。

实测成功案例：dokumen.pub（学术书籍扫描件站）——全书 46 万字符一次取回，含完整剧本/附录/访谈。

**已知边界（不是"jina 坏了"）：**
- 匿名访问对 `www.google.com` 域限流（403 AbuseAlleviationError，按小时解封）；其他域正常。
- **匿名 403 可能是全域名限流（北野武轮 2026-08 实测）**：`https://r.jina.ai/<任意URL>` 连续全部返回 `HTTPError 403: 'Forbidden'`（连 example.com 测试页也 403）——此时不是目标站问题，是 jina 侧限流/无 key；别再逐站试 jina，直接切浏览器通道（下条）。
- **域级封禁 ≠ 全局限流（雨中曲轮 2026-08 实测）**：错误体含 `Anonymous access to domain <域名> blocked until <时间> due to previous abuse found on <某URL>` 时，是 jina 对该**域**封禁（常因该域某 URL 被滥用/疑似 DDoS 牵连，同域全封），其他域不受影响。**此时直接 curl 原站 + Chrome UA 往往能通**——rogerebert.com 经 jina 403，直 curl 取回 102KB 全文，再走第 6 条 HTML→文本管线。判断法：错误信息点名具体域名+封禁到期时间=域级，先换直连再考虑浏览器通道；连 example.com 都 403=全局限流。**但直连也可能同样 403（末路狂花轮 2026-08 实测：rogerebert.com 直 curl 返回 403 Forbidden，且"解封时间戳"到了重试依旧 403）**——同域连试 2-3 次仍败即放弃该域一手抓取：用维基条目内大段转引原文（标注「经维基转引」）+ 报告如实声明，不硬编引文、不无限重试。
- **web.archive.org 已被 jina 永久封禁（blocked until 2035，2026-08 实测）**——Wayback 永远走第 3 条直连 `id_` 通道，别套 r.jina.ai。
- **付费墙站经 jina 只回首段（末路狂花轮实测）**：The Atlantic 长文返回首段+导航壳（15KB 里正文仅一段）。抓到后先看正文占比（`grep -c` 行数或目测），不足就如实声明截断，不反复重试。**付费墙关键词速判（遗传厄运轮 2026-08-09 实测）**：Vox 正文经 jina 返回 24KB 但全是导航壳+"Keep reading with a Vox Membership"（`grep -i "keep reading\|membership\|subscribe"` 命中即正文不可得）；页内若还有可用引言（如题记引语）就只引那句并标注"正文付费墙截断"，不耗调用重试。
- **jina Markdown 化有排版伪影**：段落首字母可能被拆出空格（"F alling looks like flying..."，疑似首字下沉处理），精确短语 grep 会假 MISS——校验时先用部分短语 `grep -o "like flying[^.]*"` 看实际字符再判 MISS。
- 返回体头部有 `Title:` / `URL Source:` 元信息，正文从 `Markdown Content:` 开始。
- **429 按 IP 限流（Per IP rate limit exceeded，谍战特工轮 2026-08-09 实测）**：错误体 `{"data":null,"retryAfter":1,"retryAfterDate":"...","code":429,"name":"RateLimitTriggeredError"}`——区别于 403 域级封禁，这是 jina 侧按 IP 的短时限流（retryAfter 秒后可恢复）。**不必干等重试：维基/语录类站点直接绕开 jina 走 `action=raw` 直连**（`en.wikiquote.org/w/index.php?title=X&action=raw`、`en.wikipedia.org/w/index.php?title=X&action=raw`，curl 直连零依赖、无 jina 排版伪影）；其他站点则等 retryAfter 后重试或切浏览器通道。判断法：错误体含 `retryAfter`/`retryAfterDate` = 429 限流（等或绕）；含 `blocked until <时间>` = 域级封禁（换直连/浏览器）。
- **403 错误体是 JSON，`wc -c` 秒判被拦**：返回体约数百字节（`{"data":null,"code":403,"name":"AbuseAlleviationError","readableMessage":"Anonymous access to domain <域> blocked until <时间>..."}`，readableMessage 含解封时间），成功页至少数 KB——不必打开文件逐字读。影评站被拦后的维基 Reception 段转述兜底与错误体样例见 `references/影评站被拦的维基转述兜底.md`（2026-08-09《芝加哥》轮）。

## 2b. r.jina.ai 全 403 时 → 浏览器通道（豆瓣影评实测可用，2026-08 北野武轮）

r.jina.ai 全域名 403 + Rexxar API 也不通时，**豆瓣长评页是服务端渲染的，浏览器直开可取全文、免登录**：

1. `browser_navigate` 到 `https://movie.douban.com/review/<id>/`（正常返回页面骨架，正文不在 snapshot 里）
2. `browser_console` 提取：`document.querySelector('#link-report')?.innerText`（或 `.review-content`/`#content` 兜底）——一次拿到全文
3. 落盘到 pages/ 并登记来源（浏览器抓取档命名带 `_browser` 后缀）

**豆瓣页面类型路由（2026-08 李小龙轮实测）**：只有 `movie.douban.com/review/<id>/`（单篇长评）是服务端渲染可抓；`movie.douban.com/subject/<id>/reviews`（评论**列表页**）是 JS 渲染——r.jina.ai 只回 123 字节「豆瓣 d o u b a n 载入中...」占位，浏览器打开还会触发 sec.douban.com 验证码跳转。所以：**先搜到单篇 review/<id>/ 再抓，别抓列表页**；列表页抓不到就标「未取证到」，不耗调用。Rexxar API（`m.douban.com/rexxar/api/v2/subject/<id>/reviews`）本轮未验证，可用作备选。

同族：Wayback `archive.org/wayback/available?url=<域名>/<路径>` 对豆瓣影评/卫报文章常返回 `"archived_snapshots": {}`（北野武轮 4 个 URL 全空）——**先查 availability 再投入，空则如实标「未取证到」，不反复重试**；卫报类反爬站（curl 403 + 无快照）同样直接放弃并声明。

## 2c. JS 渲染站取结构化数据 → 浏览器 innerText（日本和弦谱站 U-FRET，2026-08-13 实测）

U-FRET（ufret.jp，日本和弦谱站）curl 抓回 225KB HTML 但**全是 loader 脚本，和弦数据 JS 渲染**（grep 标签无结果）；ChordWiki 被 Cloudflare 质询（浏览器直开也是「正在进行安全验证」占位页）。活路：browser_exec 打开目标页 → `wait_for_load()` + sleep 数秒 → `js("document.body.innerText")` 一次拿全曲和弦+歌词分段（页面正文直接带「和弦+歌词混排」，可反推调性/结构/每段和声）。适用判据：`<script data-sdk>` loader 壳（html-load.com 类）或 `grep 不到数据标签` = JS 渲染，直接上浏览器通道，别耗 curl 重试。同类站点（Chord Galaxy 等）同理。调性判定时与机器检测源（SongBPM/SongData.io）交叉验证，机器报 key 常互相矛盾且被半音进行带偏——以人耳转录的和弦谱为准（落点主和弦+属和弦解决+bIII/IV 在调内）。

## 3. Wayback Machine（救 404 与死域名）

- **取快照原文**：`https://web.archive.org/web/2012id_/<原URL>` — `id_` 后缀返回原始 HTML（无 wayback 顶栏壳），直接喂给 HTML→文本管线。年份随便给一个已知存在的年份。
- **单篇影评可能任何快照都没有（里恩轮 2026-08-09 实测）**：Ebert Great Movies《日瓦戈医生》在 2017/2018/2023 三个不同年份的 `id_` 快照全 404——不是时间戳选错，是该文无快照；换 1-2 个时间戳仍 404 即标「未取证到」，不无限换年份（Ebert 有快照是常态、无快照是变体，别把变体当通道故障）。
- **URL 反查（CDX）**：只记得内容不记得确切 URL 时：

```bash
curl -sL "https://web.archive.org/cdx/search/cdx?url=<域名>/*&output=text&limit=50&collapse=urlkey&fl=original,timestamp"
```

- **archive.today 被安全验证挡（"One more step" 壳）时换 wayback 同文快照（2026-08-09 王童轮实测）**：`archive.today` 快照链接直抓返回安全验证页（55KB 壳）——用 `http://archive.org/wayback/available?url=<精确URL>` API 一次拿到最近 wayback 快照 URL（JSON 的 `archived_snapshots.closest.url`），再 `curl -sL` 直抓；老台湾/港站（台湾咁仔店等）的 wayback 快照**可能是 Big5/cp950 编码**——UTF-8 硬解码出乱码+控制字符（read_file 误报 binary），先按 `raw.decode('cp950'/'big5', errors='ignore')` 试解再走 §6 剥标签（老中文媒体站：内地 GBK 系、台湾 Big5 系）。

- **注意**：CDX 的 `filter=` 参数语法挑剔（匹配整个 urlkey），先不加 filter 拉列表再本地 grep，比带 filter 重试快。
- 实测：rogerebert.suntimes.com 老站已死，`web.archive.org/web/2012id_/<article URL>` 直接取回 2000 年 Ebert 影评原文。

## 4. Wikipedia 当搜索/目录用

- **raw wikitext**：`https://en.wikipedia.org/w/index.php?title=<URL编码标题>&action=raw` — 特殊字符标题（如 8½）REST plain 端点会 404，action=raw 更稳。
- **一手来源发现**：条目的 `==External links==` 段常挂着该主题最权威的一手 URL（影评/官方长文/访谈）——比任何搜索都精准。本会话靠它一次拿到 Ebert 两篇、Criterion 长文、Guardian 的准确 URL。
- 模板/参考段（`==Bibliography==`）列出的书，是找"书内全文"的线索（如 Rutgers Films in Print 系列收录完整剧本译本）。

## 5. 学术书籍扫描件站（dokumen.pub 等）

- URL 模式：`dokumen.pub/<书名-slug>-<ISBN>.html`，页内含整本书的 OCR 文本。
- 定位章节：用 Python 在全文里 `finditer` 章节标题的 char offset，按区间切块（`[start:end]`）落盘——比逐行读快得多。
- OCR 残留如实标注（页码残渣如 "8V2"=8½），对白/正文通常完整可读。
- Cloudflare 挡 curl 与浏览器 → 走第 2 条 r.jina.ai。

## 6. HTML → 纯文本管线（通用）

```python
import re, html
raw = open(f, encoding='utf-8', errors='ignore').read()
raw = re.sub(r'<script.*?</script>', ' ', raw, flags=re.S|re.I)
raw = re.sub(r'<style.*?</style>', ' ', raw, flags=re.S|re.I)
txt = re.sub(r'<[^>]+>', '\n', raw)
txt = html.unescape(txt)
lines = [l.strip() for l in txt.splitlines() if l.strip()]
open(f.replace('.html', '.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
```

## 7. GitHub raw 通道（raw.githubusercontent 被墙 / 404）

墙内 `raw.githubusercontent.com` 经常直接超时/空响应（curl -sL 返回空文件，exit 0 但 wc -c 为 0）。不用 r.jina.ai 绕，直接用 GitHub API 的 readme 端点，稳定可 curl（2026-08 实测）：

```bash
curl -sL -H "Accept: application/vnd.github.raw" "https://api.github.com/repos/<owner>/<repo>/readme"
```

- `Accept: application/vnd.github.raw` 头必须带——默认返回 base64 JSON，带了这个头才返回 README 原文 markdown。
- API 自动跟默认分支（master/main 都行），不存在"分支猜错 404"问题。
- 同一端点体系可扩展：仓库元信息 `repos/<owner>/<repo>`（star/archived/pushed_at）、release notes `repos/<owner>/<repo>/releases?per_page=N`。
- 免 key，限额 60 次/时，批量核查够用。

## 8. 剧本/PDF 直链返回 HTML → 从页面里挖真实资源地址（Script Slug 2026-08-09 实测）

抓电影剧本（scriptslug.com 等）时，猜的 PDF 直链（如 `www.scriptslug.com/assets/scripts/<slug>.pdf`）可能返回 **HTTP 200 + HTML 页面**（服务器把请求路由到脚本展示页，不是 404）——`file` 一看是 "HTML document" 就露馅：

```bash
file out.pdf    # 显示 HTML document = 假 PDF，别信 HTTP 200
grep -o 'href="[^"]*pdf[^"]*"' out.pdf | head -5   # 从假 PDF 页里挖真实资源地址
```

Script Slug 实测：假 PDF 页 HTML 里藏着 CDN 真链 `https://assets.scriptslug.com/live/pdf/scripts/hereditary-2018.pdf?v=1729114924`（带 `?v=` 时间戳）；带 Chrome UA 直接 curl 该链得真 PDF（497KB），再 `python -c "import fitz"`（pymupdf）转文本（119 页→16 万字符剧本全文，可 grep 行号引用）。教训：**HTTP 200 + 非预期 Content-Type 一律先 `file` 再处理**；假 PDF 页本身也是线索——grep 出 `pdf` 链接即可，不必换站。

## 纪律

1. **摘录必须来自实际取回的文件**，不许凭记忆写引文——这是研究类任务的第一纪律。
2. 回退链每层都**先小成本试水**（curl -sL --max-time 25 + wc -c 看大小），成功再深耕。
3. 诚实标注来源形态：网页原文 / OCR 扫描件 / 存档快照，各自注明。
4. 被拦时记录"这条通道对某域失效"，不要上升为"这工具坏了"的全局结论——环境会变，通道会换。
