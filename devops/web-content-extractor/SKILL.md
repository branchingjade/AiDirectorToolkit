---
name: web-content-extractor
description: 通用网页内容批量提取——四级管道智能路由。支持 SPA/非SPA/登录态/纯文本。触发词：抓取页面、提取文档、批量下载网页、爬网站内容。
category: devops
---

# 通用网页内容提取技能

## 四级提取管道（按优先级）

### Tier 0 — 静态页直取（2s 试水）

```python
import requests
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0..."}, timeout=10)
if len(r.text) > 2000 and '<article' in r.text or '<main' in r.text:
    # 非 SPA，直接 BeautifulSoup 提取
```

**触发条件：** URL 以 `.html`/`.md`/`.txt` 结尾，或 Content-Type 非 `text/html`。GitHub、MDN 等纯文档站适用。

#### Tier 0-bis — Hermes 工具链全挂时的零依赖 fallback

当 `web_extract` 和 `web_search` 都不可用（ddgs 后端未装、或 backend 不支持 extract、或返回 schema 不对），需要**纯 stdlib 拉一个 CDN/文档页 HTML** 时，用 `urllib.request` 直接打。`requests` 不一定在 venv 里。

**gzip 解压陷阱：** 默认情况下 `urllib.request` 会按 `Content-Encoding` 自动解压，但少数 CDN（包括腾讯云 cloud.tencent.com）即使你**不**声明 `Accept-Encoding: gzip` 也会返回 gzip 字节流，自动解压遇到坏头会**静默把 gzip 字节当字符串**返回，看着像 base64 乱码但本质是未经解压的二进制。修法：手动 `Accept-Encoding: identity` 强制明文接收，或者拿到响应后 `gzip.decompress(r.read())`。

```python
import urllib.request, gzip, re
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "identity",   # 关键：关掉自动 gzip 协商
})
r = urllib.request.urlopen(req, timeout=20)
raw = r.read()
if r.headers.get("Content-Encoding") == "gzip":
    raw = gzip.decompress(raw)
html = raw.decode("utf-8", errors="replace")

# 提取可见正文
body = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", html, flags=re.I)
text = re.sub(r"<[^>]+>", "\n", body)
text = re.sub(r"\n\s*\n+", "\n", text).strip()
```

**自签证书应对：** 不要 `CERT_NONE` 全关校验——那是 MITM 漏洞。改成 `ssl.create_default_context()` 后 `ctx.load_verify_locations(cafile)` 加载站点 CA，或临时对单 host 走 `unverified_context`（仅限内网/已知 CDN），并加注释说明原因。

**何时跳过 Tier 1/Tier 2：** 用户只要一个独立 HTML 文档（API 文档站、产品手册），不是 SPA 也不是登录态——直接 Tier 0-bis，不要启动浏览器实例。

**调试信号：** 拿到的 `body` 里如果有大量 `\x00`/`\x1f` 控制字符 + 没有任何 `<` 字符 → 100% 是 gzip 没解压。看一眼响应头 `Content-Encoding` 确认。

### Tier 1 — Hermes CDP 浏览器（SPA/动态渲染，无登录态）

```
browser_navigate(url)
browser_snapshot(full=true)
read_file(返回的 snapshot 路径)
```

**从 snapshot 提取内容：**
- 参数行：`- StaticText "参数名 类型 说明"`
- 表头行：`- columnheader "字段"`
- 端点行：含 `POST https://` 或 `wss://`
- 代码块：`code` 节点的 `StaticText`

**Snapshot 空壳检测：** 如果只有 nav/header 无 article 内容 → 页面需要 JS 渲染 → 等 3s 再 snapshot，或点一下侧边栏菜单。

**防重复读：** 每个 snapshot 只读一次。工具会标记 `idempotent_no_progress_warning`。

### Tier 2 — Kimi WebBridge（需要登录态）

触发词：用户说"用我浏览器"、页面需要登录/cookie、CDP 返回登录页。

```python
# navigate
payload = {"action": "navigate", "args": {"url": "...", "newTab": True, "group_title": "任务名"}, "session": "extract"}
# → curl 到 127.0.0.1:10086/command

# snapshot
payload = {"action": "snapshot", "session": "extract"}

# evaluate 提取结构化数据
payload = {"action": "evaluate", "args": {"code": "document.body.innerText"}, "session": "extract"}
```

### Tier 3 — 页面内 JSON 快取（速度最优）

部分 SPA 将初始数据序列化在 `<script>` 标签中：

```js
// 提取 __NEXT_DATA__ / __INITIAL_STATE__ / window.__DATA__
JSON.stringify(window.__NEXT_DATA__ || window.__INITIAL_STATE__ || null)
```

**优先尝试 Tier 3，失败再退到 Tier 1。**

## 智能路由

```
1. URL 结尾是 .md/.txt/.json/.html → Tier 0 直取
2. browser_navigate 后 snapshot 空壳/登录跳转 → Tier 2 WebBridge
3. 先试 evaluate('__INITIAL_STATE__') → 有数据则 Tier 3
4. 默认 → Tier 1 CDP 三步法
```

## 并行策略

`delegate_task` 分片，每片 5 页，每个子 agent 独立浏览器实例：

```
任务 A: navigate(url1) → snapshot → read_file → write_file(batch_a.txt)
任务 B: navigate(url6) → snapshot → read_file → write_file(batch_b.txt)
...
```

子 agent 指令必须明确：三步法 + StaticText 解析规则 + 输出路径。

## 输出格式参数化

用户可指定：
- `--extract params` — 参数表（字段/类型/说明）
- `--extract endpoints` — 端点 URL
- `--extract code` — 代码示例
- `--extract all` — 全文
- `--output vault/` — 输出路径

## 已踩坑（跨平台通用）

- **SPA 空壳**：`requests.get()` 只拿到 500 chars 空壳 → 升级到 Tier 1
- **CORS 拦截**：浏览器内 JS `fetch()` 跨域失败 → 不要用 browser_console 批量 fetch
- **sandbox 拒绝**：cron/execute_code 可能拒绝网络请求 → 用 browser 工具
- **snapshot 截断**：超过 ~15K chars 的 snapshot 存文件 → `read_file` 分段读
- **鉴权不统一**：同一平台可能多种鉴权方式（API Key / AKSK / OAuth）
- **SPA 子导航**：默认页显示"产品动态"，API 内容在子菜单 → 点侧边栏或从 snapshot 中直接提取
