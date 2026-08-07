---
name: cn-content-site-extraction
description: 百度百科/豆瓣/知乎抓取专项：搜索页发现URL→导航→evaluate。触发词：抓百科词条、豆瓣影评、知乎回答。
category: devops
---

# 中文内容站抓取专项（百科/豆瓣/知乎）

与 `web-content-extractor` 的分工：它管"用哪一层管道"（Tier 0-3），本技能管"这三类站点各自的 URL 发现、反爬降级与正文提取细节"。走 WebBridge 时用文件体模式发中文 payload，见 `kimi-webbridge` 技能。

## 核心套路

**先搜索页发现真实 URL，再导航**——不要凭记忆猜条目 ID。导航后必须验证 `document.title`（猜错 ID 会被重定向到无关页，甚至残留上一任务的 tab 状态），再抓正文。

大页面返回是双层 JSON：`json.loads(json.loads(out)['data']['value'])` 取字段；返回前先 `text.slice(0, 15-18KB)` 截断防 stdout 超限。

**NUL 字节坑（实测多次）**：WebBridge evaluate 取回的 innerText 经 JSON 双解析写盘后可能夹 NUL 字节（U+0000）——read_file 会误判 "Binary file" 拒绝显示，而 `file` 命令仍报 UTF-8。处理：写盘前 `text.replace('\x00', '')`，或读取时用 python `open().read().replace('\x00','')`。凡 read_file 报 binary 但 file 显示 UTF-8 文本，先怀疑 NUL。

**display:none 容器坑（实测 2026-08-06，juben.pro 剧本正文）**：JS 站点的 tab/分页容器常为 `display:none`，此时 `innerText` 返回空串（看似抓取失败，页面长度对不上），但 `textContent`/`innerHTML` 有全文。凡 evaluate 返回空而页面明显有内容，先查容器的 `style`/`offsetParent`，改用 `textContent` 提取（或先 `el.style.display='block'`）。

**read_file 误报 "Binary file" ≠ NUL 坑（实测 2026-08-06）**：WebBridge 写盘的 UTF-8/CRLF 中文 md 文件（**无 NUL 字节**，控制字符只有 \r）可能被 read_file 判 binary 拒绝显示，且同批文件判定不稳定（有的能读有的被拒）。先跑 `python 检查 b"\x00"` 排除 NUL 后，别再折腾文件——直接用 Python `open(path, encoding='utf-8').read()` 读取/分析（execute_code 里切片打印），绕开 read_file 即可。

## 百度百科

- 词条 URL 形如 `/item/<名称>/<ID>`，ID 靠猜极易错。
- **无 ID 直达（实测 2026-08-06）**：`navigate('https://baike.baidu.com/item/<名称>')`（不带 ID）会自动跳转到正确词条，比站内搜索页少一步；若 ID 猜错则重定向到百度**首页**（`document.title` 变"百度首页"、正文只剩导航样板即信号）——每次导航后先 title 验证。
- 正确路径：`navigate('https://baike.baidu.com/search?word=<关键词>')` → evaluate 提取 `a[href*="baike.baidu.com/item"]`（innerText+href 去重）→ 选对词条再 navigate。
- 词条结构：基本信息（含主题句）→ 剧情简介 → 角色介绍 → 幕后制作（剧本创作常含改编动机/审查背景，研究改编类电影必看）→ 影片评价（专业评价含媒体引文）→ 相关讨论。
- **直连 403 时用 jina reader 拿全文（实测 2026-08-07）**：`curl -s "https://r.jina.ai/https://baike.baidu.com/item/<百分号编码名>"` 返回整词条 markdown（75KB 级，含全部章节，无需 WebBridge）。**词条名编码坑**：用原始名（含繁体）编码更稳——`胡金銓` 通，`胡金铨` 曾 404（baike 会跳转但 jina 有时不跟随）；编码用 python `urllib.parse.quote` 生成，别手写。
- **同名词条被占用时（实测 2026-08-06《大话西游》）**：`/item/<名称>/<ID>` 带 `fromid=<ID>` 也会被重定向到占用者——1995 电影词条被 2017 同名电视剧《大话西游之爱你一万年》抢占，fromid=19442305 仍跳电视剧页（`document.title` 是电视剧名即信号）。**ID 钉不住时别恋战**，直接换源：维基百科中文版 `zh.wikipedia.org/w/index.php?search=<关键词>` 发现真实条目名——中文电影条目常用**港版原名**（《大话西游》的条目是《西游记第壹佰零壹回之月光宝盒》《西游记大结局之仙履奇缘》），系列总述页可能是消歧义页（"大话西游"原为粤语成语，消歧义页有该注记）；维基条目含制作背景/票房/奖项/媒体评价，做电影研习时信息密度高于百度百科。
- 尾部大量无关推荐，正文切片 ~18KB 足够，不必抓全页。
- **正文含大量导航样板**（百度首页/百科冷知识/相关星图/词条图册等，可占一半以上字符）。提取后用章节标题 grep 切有效内容：`grep -A N "幕后制作|影片特色|获奖记录|影片评价|主题寓意"`——研究改编类电影时"幕后制作→剧本创作/角色选择/特效制作/拍摄场景/轰动戛纳"+"主题寓意/视觉风格"+"专业评价"即全部干货。

## 豆瓣电影

- subject ID 易记错（实测 2131459 是《机器人总动员》而非《画皮》）。用 `https://search.douban.com/movie/subject_search?search_text=<片名> <年份>` → 提取 `/subject/\d+` 链接，按标题+年份选对条目。
- 主页热评区标题链接不暴露 href（文本被折叠），拿不到 review URL；改走 `https://movie.douban.com/subject/<id>/reviews?sort=hot` 列表页提取 `/review/\d+` 链接（含标题）。**nuance（实测 2026-08-06）**：部分渲染状态下主页 evaluate `a[href*="/review/"]` + innerText 过滤也能一次拿全热评链接与标题——先试主页，空则走列表页。
- 影评正文页 innerText 前 ~7KB 即全文，末尾"有用/没用"计数可作热度佐证。**正文容器 selector：`.review-content`**（实测 2026-08-06 新版豆瓣 `#link-report` 已失效返回空，`.review-content` 是现行主容器，`.article` 兜底；`#link-report` 只在老页面有效）；影评列表页用 `a[href*="/review/"]` 一次拿全链接+标题（含"展开"折叠的短评影评标题）。
- **国产片剧本的豆瓣转帖渠道（实测 2026-08-06）**：长影评中有人整篇转帖剧本全文——《大话西游》全文 29487 字（review/3115577），含场次/动作描述/完整台词。转帖稿特征：无版本注明、文内标注"*"为大陆公映被删段落（=港版录音整理稿特征）、措辞与上映版有出入（"波若波罗密" vs 影片"般若波罗蜜"、"七色的云彩" vs 流传"七色云彩"）。引用必须标注"转帖稿"并 grep 校验原文，不许凭记忆。juben.pro 没有的国产片剧本，先来豆瓣影评搜转帖。
- **转帖稿可为"剧本与实拍改动对照"整理稿（2026-08-07 小武轮实测）**：《小武》全文 26343 字（review/5760698）文内大量"（原剧本，实拍时删去）/（实拍时增加的场次）/（实拍时即兴找到的新的结尾）"标注——实拍删改信息直接进稿，属对照整理稿变体，引用时注明；含录入笔误（"M90OO"应为"M9000"、"打吨"应为"打盹"）。**与 juben.pro 免费预览交叉验证法**：juben.pro 作品页免费预览（梗概＋首场，见 juben.pro 节）→ 与豆瓣转帖稿首场逐句比对一致即认可稿——两渠道互证可显著提升网传转帖稿可信度，且全程 curl 免浏览器。
- 评分/人数/热门短评在主页一次抓全。主页短评区常有高质量一句话美学点评（如"横摇=卷轴"），抓主页时一并保留。
- **反爬验证页（实测 2026-08-06）**：navigate 后 title 只剩"豆瓣"、URL 跳转 `sec.douban.com/c?r=...`、body 仅剩"请点击下方按钮继续浏览或登录使用豆瓣/点我继续浏览"——evaluate 找 `a,button` 中 textContent 含"点我继续浏览"的元素 `.click()`，sleep 5-6s 页面自动跳回原 URL 即可正常抓取。**搜索页同样触发**（search.douban.com 首访必过验证），不只条目/影评页。每个新豆瓣页都可能再触发，统一重试模式：`location.host` 含 sec.douban → 点击 → sleep → 重抓正文。**细节：必须点击真正的 `<button>`**——含该文本的容器 `<div>` 无点击处理器，点了无效（实测 div 无效、button 有效）；抓取结果极短（~37 字符=安全页残留）即未过验证，重试而非采信。cookie 种下后短时间内多页可连续抓，但隔段时间会再触发，循环里保留绕过逻辑。**批量循环的实用形态（nav_robust，实测最稳）**：navigate → 检查 `location.href.includes('sec.douban.com')` → 是则点按钮 + sleep 3 → **重新 navigate 同一 URL**（不要只等自动跳转，自动跳转不总是发生），最多 3 轮；每次 navigate 后都先验证过没过验证页再 evaluate，避免把安全页残留当正文。

## 知乎

- **未登录搜索降级**：`zhihu.com/search` 对任意 query 返回"未搜索到相关内容"（空壳页 LEN≈800）。不要换关键词重试搜索。
- **DuckDuckGo HTML 端点可 curl 直取（实测 2026-08-06）**：`https://html.duckduckgo.com/html/?q=<关键词>+site:zhihu.com` 普通 curl（带 UA）即返回结果，链接在 `uddg=<urlencoded>` 参数里，`urllib.parse.unquote` 后提取——**发现知乎 question/专栏 URL 不需要 WebBridge**。限流：连续第二次查询返回 202——间隔 ≥5s 或换 Bing（WebBridge）。
- 发现问题 URL 用 Bing：`https://www.bing.com/search?q=site:zhihu.com+<关键词>` → 提取 `li.b_algo h2 a`（标题+URL 一次拿全）。**必须走 WebBridge 真实浏览器**（实测 2026-08-06：curl 直接请求 Bing 返回 200 但 li.b_algo 提取为空，疑似反爬壳页；WebBridge navigate 后正常）。**不必限定 /question**：不限时同时返回 question 页与 zhuanlan 专栏链接（实测专栏链接质量更高）。百度网页搜索已变成 AI 聚合页，site: 查询拿不到真实链接。
- **zhuanlan 专栏文章（zhuanlan.zhihu.com/p/xxx）未登录即全文可读**，正文比 question 页干净（无回答列表噪声）；question 页未登录也能读前排回答全文。实测一次 navigate 抓专栏 5-12K 字符正文成功；长篇专栏正文可能超 40K，先 `text.slice(0, 50000)` 截断再存盘。
- 未登录可直接访问 question 页：问题描述、前排回答、回答中引用的长文（如古籍原文）通常全文可读。
- **navigate 可能报 `page load timeout (30s)`（extension_error），但页面内容实际已加载**——超时后不要重试导航，直接 evaluate 抓正文。
- 知乎话题页/搜索页的链接都在 JS 里，evaluate 拿 `a[href*="zhihu.com/question"]` 有时为空，属正常。

## juben.pro（华语剧本网）剧本全文分页抓取——免登录/VIP 全量（实测 2026-08-06）

**修正旧认知**：`电影大师研习` skill 的渠道表写"免费只读前 N 场、全文需 VIP"——**实测分页 URL 免登录可读全量**（《新龙门客栈》13 页 / 175 场全部抓到，未登录未付费）。华语电影剧本难得，此渠道值得先试。**⚠️ 权限因作品而异（2026-08-07 小武轮实测）**：《小武》（writing/7-16081.html）正文需登录——curl 直抓第 1/2 页只给梗概＋首场＋"阅读剧本正文"按钮，正文位置是"您没有登录，免费注册并登录后方可阅读作品正文！"。判定：提取文本 grep `您没有登录` 即登录墙，别当抓取失败。**登录墙下免费预览仍有价值**：梗概＋首场＋（有时）"剧本与实拍时的改动对照"标题，可与豆瓣转帖稿逐句比对交叉验证（见豆瓣节）。

- **URL 模式**：作品页 `https://www.juben.pro/writing/<id>.html`；正文分页为 `https://www.juben.pro/writing/<id>-<页码>-ccontent-hpdefault.html`（第 2..N 页直接访问即可读正文，无需点任何按钮）。
- **第 1 页特殊**：需点「阅读剧本正文」（找到文本含该字样的元素 `.click()`，DIV 也有效；点击后 body 从 ~1.4K 扩到 ~4K）。**再次返回第 1 页时可能只取到 1 字符**（页面状态重置）——此时重试导航并再点一次按钮。
- **提取**：evaluate `document.body.innerText`，从首个 `\d+、`（场次标题）切片到「下一页」/「编辑：」标记（去尾部样板）；`replace('\x00','')` 防 NUL。
- **合并 + 统计**：各页拼一个 md；场景标题正则 `^\s*(\d+)、([^，]+)，(日|夜|黄昏|黎明|清晨)(?:，|$)`（**行首是全角空格，必须 `^\s*`**）可数场景总数与地点分布（如"客栈内戏份占比"）。**中文数字场号变体（2026-08-07 小武轮实测）**：转帖稿场号可能是中文数字＋字母后缀（"七十五、村子里，中午""八十二a街道上，上午"）——计数正则用 `^\s*([一二三四五六七八九十百千]+[aA]?)、`；grep 中文数字零命中时别判"无场号"，先怀疑行首空白/全角空格。转帖稿末尾常带版本注记（如"剧终 一九九七年三月十二日晨六点"），是判定版本/成稿时间的线索。
- **站内搜索（实测 2026-08-06）**：URL 参数 `?s=<词>` **无效**（返回首页，无结果区）。正确姿势：evaluate 找 `input[type="search"], input[name="s"], input[placeholder*="搜索"]` → 用原生 setter 设值（`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(box, 词)`）+ dispatch `input` 事件 → `box.closest('form').submit()` → 落地 `/search/?SearchKeywords=<词>`。**curl POST 免登录也拿不到**（带 __RequestVerificationToken 的 POST /search/ 回 0 字节空文件，2026-08-07 实测——搜索要求登录态，别绕）。**同名影视多为投稿同人**：搜"大话西游"返回的全是用户投稿同人（大话西游之浮尘幻梦等），名作是否收录以搜索结果为准——不要默认站内有名作。
- **搜索落地页可直接 curl（实测 2026-08-07，免 WebBridge）**：`curl "https://www.juben.pro/search/?SearchKeywords=<URL编码词>"` 直抓返回 200 全量结果。**坑：结果标题是 HTML 实体编码**（`&#x65B0;&#x9F99;&#x95E8;...` = 新龙门客栈），grep 原始中文零命中、被误判为"无结果"——先 `html.unescape()` 或 python `re.findall(r'href="(/writing/\d+[^"]*)"[^>]*>([^<]{0,60})', text)` 再核对标题。r.jina.ai 对 juben.pro 超时（422 TimeoutError），别走 jina。此直连法同样用于"确认某片是否收录"（龙门客栈 1967 轮：只命中徐克 1992《新龙门客栈》writing/4-15669，胡金铨原版未收录→标「剧本未取到」）。
- **同名影视多为投稿同人**：搜"大话西游"返回的全是用户投稿同人（大话西游之浮尘幻梦等），名作是否收录以搜索结果为准——不要默认站内有名作。
- **版本风险**：网版流传稿与上映版有出入（人名用字如 贾延/贾廷、台词措辞），引用必须注明"网版流传稿+URL"；缺页可去知乎专栏搜同名剧本片段补齐（如 `zhuanlan.zhihu.com/p/421095121` 有《新龙门客栈》第 1-10 场）。
- 完整抓取/合并/统计代码与实测记录：`references/juben-pro-pagination.md`。

## 批量抓取（单代理多页，实测高效）

抓 5-10 个同站页面（如豆瓣多篇影评）时用 `execute_code` 循环代替逐条手调：

1. 每页两连发：`navigate`（sleep 2-3s 等加载）→ `evaluate` 提取正文容器。
2. 请求体逐个写临时 JSON 文件（唯一文件名）→ `curl.exe -o resp_<tag>.json`（**输出落盘而非 stdout**，规避大响应截断）→ python 解析双层 JSON。
3. 提取结果直接写 `_source/<站点>_<id>.md`（带来源 URL/标题头），**循环只 print 状态行**（OK/FAIL + len），正文不进上下文。
4. 失败页打标记继续，不中断整批；evaluate 里 JS 包 IIFE 防重复声明报错。

实测：8 篇豆瓣影评 + 4 个知乎页 ≈ 75s 跑完，上下文零污染。

### WebBridge 请求直发（execute_code + urllib，免临时文件，推荐）

临时 JSON 文件 + curl 的模式有两个坑：① 每个请求都要写文件再删；② **git-bash 的 MSYS curl 读 `--data-binary @/c/...` 会报 "error encountered when reading a file"**（实测 2026-08-06，@ 路径须写成 Windows 风格 `C:/...` 才认）。更省事的路子：**在 `execute_code` 里用 Python `urllib.request` 直接 POST 到 `http://127.0.0.1:10086/command`**——JSON 用 `json.dumps` 构造，中文零编码问题，无临时文件：

```python
import json, urllib.request
def cmd(action, args, session="dxxd-7k2m"):   # session 唯一命名
    body = json.dumps({"action": action, "args": args, "session": session}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:10086/command", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))
# 循环：cmd("navigate", {"url": url}) → sleep(2-3) → cmd("evaluate", {"code": code}) → 结果直接写 _source/
```

循环只 print 状态行，正文写盘不进上下文（同上面的纪律）。navigate 不带 `newTab` 会复用当前 tab，天然适合"逐页顺序抓"。

## 并发子代理抓取（delegate_task 批量研究）

- **WebBridge 默认 session 与并发进程冲突**：多个子代理共用一个默认 session 会导致 tab 串页（A 导航的页面在 B 的 evaluate 里读到）。每个子代理/每个任务用**随机唯一 session 名**（如 `f'{os.urandom(4).hex()}'` 或按任务命名）规避。
- 百度百科**默认词条页可能跳转到翻拍/同名版**（如《倩女幽魂》1987 版词条 URL 跳 2011 翻拍版）——必须经站内搜索页定位正确年份的 ID，核对 `document.title`。
- 豆瓣电影 ID 记错时用 suggest API：`https://movie.douban.com/j/subject_suggest?q=<片名>` 返回 JSON 数组（title/year/id），比搜索页更省事。**实测普通 curl 直连可用**（中文参数 URL 编码，无需浏览器/无鉴权），比 navigate 搜索页快一截。
- 大批量（3+ 子代理并行）时各任务独立命名 session，抓完关闭标签组。

## 通用降级：失效链接回源 / Wikipedia 直抓 / 搜索引擎反爬 / 内置浏览器串页（2026-08-07 实测）

**Wayback Machine 回源失效文章**：媒体改版后旧文章 URL 常 404（实测 Film Comment 2011 徐克访谈两篇直连全 404）。配方：
`curl -sL "https://web.archive.org/web/2023/<原URL>" -H "User-Agent: Mozilla/5.0..." -o out.html`（`/web/2023/` 取近年快照，返回原页 200）。维基引用里直接给出的 web.archive.org 链接可直接用。

**Wikipedia 直抓（en/zh 均可 curl）**：REST 纯文本端点（`/api/rest_v1/page/plaintext/<标题>`）实测 404；正确姿势 = curl 普通页面 HTML（带浏览器 UA + Accept-Language）+ python 剥壳：
```python
import re, html
raw = open('p.html', encoding='utf-8', errors='ignore').read()
raw = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', raw, flags=re.S|re.I)
text = html.unescape(re.sub(r'<[^>]+>', '\n', raw))
open('p.txt','w',encoding='utf-8').write('\n'.join(l.strip() for l in text.split('\n') if l.strip()))
```
大词条 HTML 400KB+ → 文本 25-40K 字符，够用；从 HTML 里还能提取 References 外部链接（`href="https?://..."` 正则 + 媒体白名单过滤）——**维基 References 是发现访谈/影评 URL 的索引**。

**搜索引擎反爬（别浪费时间）**：百度搜索 curl 只回 302 壳（需 JS）；Bing 即使用内置浏览器也触发人机验证（body 只剩 ~35 字"请解决以下难题以继续"）；搜狗 curl 直接 ERR_ABORTED。搜索引擎只用于发现 URL，发现后直接进站；发现不了 → 用 Wikipedia References / 站内搜索 / 站点地图。知乎发现仍用 DuckDuckGo HTML 端点（见上）。

**内置浏览器 tab 串页（非 WebBridge 场景）**：navigate 到 A 却读到 B 的内容——残留 tab/缓存（实测：打开百度百科读到 juben.pro 搜索页；豆瓣 reviews 页显示《让子弹飞》影评正文）。规避：**每次提取表达式第一行带 `location.href`** 与预期 URL 核对，不符即串页——重新 navigate 一次，或 evaluate `location.href='<目标>'` 二次导航后再提取。**点击链接导航也可能落错页**（点击影评标题却跳到另一部电影的影评）：先在当前页 evaluate 提取 标题→href 映射，再直接 navigate href（别点）。

**MSYS curl 写盘坑（exit 23）**：git-bash 里 `curl ... -o /c/Users/.../x.html` 可能 HTTP 200 但文件没写出来（SIZE:0 + exit 23，文件不存在）——先 `cd` 到目标目录再用相对文件名 `-o x.html`（与 `--data-binary @/c/...` 同类 MSYS 路径问题，见上）。

**豆瓣无浏览器直抓全链路（WebBridge 扩展未连接时可用，实测 2026-08-07）**：桌面站 movie.douban.com 对 curl 只回 ~3KB JS 挑战壳；以下三条纯 curl/python 通道互相补位，覆盖"找 ID → 短评 → 长评全文"：
- **m.douban.com 手机 UA 直连**：subject 页与搜索页 `https://m.douban.com/search?query=<URL编码片名>`（UA 用 iPhone Safari 串）直接 200 全文，无验证页；搜索页 grep `href="/movie/subject/<id>/"` 得 ID。**别用 `/j/search`**（返回空壳 JSON `{"count":0}`）。
- **短评全量 = rexxar API**：`https://m.douban.com/rexxar/api/v2/movie/<id>/interests?count=30&start=<n>&order_by=hot`，手机 UA + `Referer: https://m.douban.com/movie/subject/<id>/`，返回 JSON `interests[].comment`（含用户名）。翻页改 start，每页 sleep 1s。拿"影迷口碑证据/金句"最快通道，无任何浏览器。
- **interests 端点双用途（实测 2026-08-07 龙门客栈轮）**：①短评里常藏高密度分析型金句（蓄势/去势、三一律、空间叙事）——比 subject 页可见的 5 条多得多；②**引文校验兜底**——研习报告引用的短评若在条目页存档中 MISS，直接 interests 翻页抓 60 条核对原文（本轮的"蓄势"引文即由此修复）。**用户名可取**（`interests[].user.name`），与 reviews 列表 API 的 `author: None` 互补——要署名引用短评走 interests。
- **长评全文 = jina reader 绕 App 门禁**：m.douban 的 review 页只有 ~60 字 teaser（全文 App 专属）；`https://r.jina.ai/https://movie.douban.com/review/<id>/` 返回 markdown 全文（带 Title/URL 头）。部分影评 403（jina 报 Forbidden，如账号注销者的影评）→ 换别的影评或标"未取证到"；连续请求限流，间隔 2-3s。jina 对 baike/其他 403 站同样有效（见上）。
- **长评全文免 jina = rexxar 单篇 API（实测 2026-08-07，比 jina 更稳，普通 curl 即可）**：`https://m.douban.com/rexxar/api/v2/review/<id>?ck=&for_mobile=1`，手机 UA + `Referer: https://m.douban.com/movie/subject/<id>/`，返回完整 JSON（`content`=HTML 正文、`author.name`/`title`/`rating` 同包），无 jina 限流/403 问题。**content 是 HTML：先 `</p>`→`\n\n`、`<br>`→`\n` 再剥标签，否则全文挤成一行没法读**（实测踩坑）。
- **影评清单发现 = rexxar 列表 API（实测 2026-08-07）**：`https://m.douban.com/rexxar/api/v2/movie/<id>/reviews?start=0&count=20&order_by=hot`（同 UA/Referer）直接 200，`reviews[]` 含 id/title/rating/abstract/author.name——一次拿全热评 ID+评分+摘要，再按需逐篇抓全文。**rexxar 搜索 API 需登录**（`/rexxar/api/v2/search` 回 `{"msg":"need_login","code":103}`，别用）；找 ID 走 `m.douban.com/search?query=`（见上）或 jina 读桌面 `douban.com/search?q=<词>&cat=1002`（subject ID 藏在 link2 跳转 URL 里，grep `subject/\d+` 提取）。
- **rexxar review 单篇另一变体（实测 2026-08-07 空山灵雨轮，两变体并存）**：`?api_version=2` + Referer `https://m.douban.com/movie/review/<id>/` 同样 200 全文；**该变体 `author.name` 常为空**（要署名用 `?ck=&for_mobile=1` 变体或 interests）。完整配方/批量抓取模板/403 实测档案：`references/douban-rexxar-review-api.md`。

**zh.wikipedia 直抓两个坑（实测 2026-08-07）**：① 路径里放裸 UTF-8 中文 → 404；必须百分号编码（`urllib.parse.quote`）。② 条目名用**真实名（常为繁体/港版名）**——`胡金銓` 有条目，简体 `胡金铨` 404；不确定时用 API 搜索 `zh.wikipedia.org/w/api.php?action=query&list=search&srsearch=<词>` 拿真实标题。提取时先切 `<div id="mw-content-text">...</div>` 再剥标签，可去掉 infobox CSS 噪声。

## 验证清单

1. 每次 navigate 后核对 `document.title` 与预期条目一致
2. 抓正文前先看 `len`，超大页面先切片
3. 引用来源 URL 用最终确认的条目页（勿用搜索页）
