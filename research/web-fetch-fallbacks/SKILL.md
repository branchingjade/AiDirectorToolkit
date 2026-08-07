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

实测成功案例：dokumen.pub（学术书籍扫描件站）——全书 46 万字符一次取回，含完整剧本/附录/访谈。

**已知边界（不是"jina 坏了"）：**
- 匿名访问对 `www.google.com` 域限流（403 AbuseAlleviationError，按小时解封）；其他域正常。
- 返回体头部有 `Title:` / `URL Source:` 元信息，正文从 `Markdown Content:` 开始。

## 3. Wayback Machine（救 404 与死域名）

- **取快照原文**：`https://web.archive.org/web/2012id_/<原URL>` — `id_` 后缀返回原始 HTML（无 wayback 顶栏壳），直接喂给 HTML→文本管线。年份随便给一个已知存在的年份。
- **URL 反查（CDX）**：只记得内容不记得确切 URL 时：

```bash
curl -sL "https://web.archive.org/cdx/search/cdx?url=<域名>/*&output=text&limit=50&collapse=urlkey&fl=original,timestamp"
```

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

## 纪律

1. **摘录必须来自实际取回的文件**，不许凭记忆写引文——这是研究类任务的第一纪律。
2. 回退链每层都**先小成本试水**（curl -sL --max-time 25 + wc -c 看大小），成功再深耕。
3. 诚实标注来源形态：网页原文 / OCR 扫描件 / 存档快照，各自注明。
4. 被拦时记录"这条通道对某域失效"，不要上升为"这工具坏了"的全局结论——环境会变，通道会换。
