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
