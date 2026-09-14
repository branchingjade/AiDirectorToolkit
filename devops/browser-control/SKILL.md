---
name: browser-control
description: 浏览器操控统一入口——agent-browser / CDP无头 / Kimi WebBridge 三层架构。触发词：浏览器、打开网页、截图、爬数据、用我浏览器、后台抓、WebBridge。
---

# 浏览器操控

三层架构，按场景自动选层。所有浏览器操作走这一个入口。

## 架构

```
Hermes browser 工具 (browser_navigate / click / snapshot / ...)
  └── browser_tool.py ──调用──▶ agent-browser CLI (npm 全局包)
                                   └── 启动 Chromium 实例
```

**后端选项：**
| 后端 | 类型 | 需要 |
|------|------|------|
| agent-browser (默认) | 本地 headless Chromium | `npm install -g agent-browser` |
| Browserbase | 云端 | `BROWSERBASE_API_KEY` + `BROWSERBASE_PROJECT_ID` |
| Browser Use | 云端 | `BROWSER_USE_API_KEY` |
| Camofox | 本地反检测 | `CAMOFOX_URL` |

## 预览面板（桌面 app preview pane）

聊天旁的预览面板是 WebView2（Chromium 内核）内嵌浏览器，独立环境（2026-08-07 实测）：

- **存储**：`%APPDATA%\Hermes\Partitions\hermes-browser\`——cookie/localStorage **持久落盘**（跨重启保留）
- **无登录态**：不继承 Chrome/Edge 任何账号；cookie 库实测仅 `github.com logged_in=no`（GitHub 给所有访客的匿名标记）。需要登录态的场景**一律 WebBridge**
- **反爬**：实测百度搜索被弹图形验证码（`wappass.baidu.com/static/captcha`）——中文反爬站不可用
- **定位**：公开页面 / 本地 HTML 设计稿预览（`open_preview` 工具），agent 浏览器工具抓公开内容
- **清空重置**：关掉桌面 app 后删除 `Partitions\hermes-browser\` 整个目录

**验证登录态（读 cookie 库，比看文件大小可靠）：**
```python
import sqlite3
con = sqlite3.connect("file:C:/Users/<user>/AppData/Roaming/Hermes/Partitions/hermes-browser/Network/Cookies?mode=ro&immutable=1", uri=True)
con.execute("SELECT host_key, name, value FROM cookies").fetchall()  # logged_in='no' = 未登录
```

## 场景路由

| 用户说 | 选层 | 解释 |
|--------|------|------|
| "帮我打开xx看看"/"截图" | 层1：agent-browser | browser_navigate/click/snapshot |
| "后台爬"/"批量抓"/"数据" | 层2：CDP 无头 | 后台自动化，用户无感 |
| "用我浏览器"/"我登录的"/"操作已登录网站" | 层3：Kimi WebBridge（Python SDK）| 继承用户登录态 |

**选层规则：** 用户没指定时默认 agent-browser → CDP失败自动切 WebBridge → 不纠结。

**"agent 能自己判断使用"铁律**（2026-09-08 用户拍板）：agent 不要每次现场拼 curl + JSON + temp 文件——见下面「层3：Kimi WebBridge」章节，**直接用 `kimi_webbridge` Python SDK**（`KimiWebBridge` 类 + 13 个方法），agent 通过 `execute_code` 调。SDK + CLI 共用 `kimi_webbridge/_transport.py`，行为一致。CLI 是给用户手跑用的，不要把 CLI 模式当成 agent 工具。

---

## 层1：agent-browser（日常浏览）

Hermes 内置 `browser_navigate`/`browser_click`/`browser_snapshot`/`browser_console` 工具。最简单方式。

### 启用/禁用

```bash
hermes tools disable browser   # 禁用
hermes tools enable browser    # 启用
```

工具变更需要 `/reset` 生效。

### 有头模式

`~/.hermes/.env` 中设 `AGENT_BROWSER_HEADED=true`（仅对 agent-browser 直接调用有效）。Hermes browser 工具通过 `--cdp` 控制 Chrome 时，窗口由 Chrome 启动方式决定。

---

## 层2：CDP 无头模式

### 问题
- `agent-browser --session <name>` 在 Windows 上死锁（daemon/socket IPC 不兼容）
- 每个 browser 调用卡死

### 解决方案

**推荐用 `hermes config set`（比 `.env` 更可靠）：**

```bash
hermes config set browser.cdp_url "http://localhost:9222"
hermes config set browser.allow_private_urls true   # 按需
```

然后 `/reset`。

> `.env` 的 `BROWSER_CDP_URL` 不一定被 session 读取，优先用 config。`browser.allow_private_urls` 设了也不立即生效，需 `/reset`。

### Chrome 启动

**独立 profile（关键——不能复用主 Chrome profile）：**

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir=C:/Users/HMSJ/.hermes/chrome-cdp-profile
```

**有头模式（默认，适合扫码登录）：**
```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\Users\<user>\.hermes\chrome-cdp-profile
```

**无头模式（登录后日常使用，cookie 持久）：**
```bash
chrome.exe --remote-debugging-port=9222 --headless=new --user-data-dir=C:\Users\<user>\.hermes\chrome-cdp-profile
```

切换方法：关掉 Chrome 重开，换参数。`--user-data-dir` 不变，登录态不丢。

### 开机自启

`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\chrome-debug.vbs`：

```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\Program Files\Google\Chrome\Application\chrome.exe"" --remote-debugging-port=9222 --user-data-dir=C:\Users\HMSJ\.hermes\chrome-cdp-profile", 1, False
```

`1` = 正常可见窗口，`0` = 隐藏。

### 验证

```bash
curl -s http://localhost:9222/json/version
# → {"Browser": "Chrome/...", "webSocketDebuggerUrl": "ws://..."}
```

### 登录态

CDP Chrome 使用独立 profile，与用户日常 Chrome 完全隔离。首次需在 CDP Chrome 窗口登录，之后 cookies 持久保留。

**登录检测（browser_console 执行，不要凭快照文字判断）：**
```javascript
(function(){
  var text = document.body.innerText;
  if (text.includes('退出账户') || text.includes('退出登录')) return true;
  if (text.includes('个人会员') || text.includes('企业会员') || text.includes('会员中心')) return true;
  return false;
})()
```

### 兜底：agent-browser CLI 直连

当 browser 工具怎么都调不通时，绕过 Hermes wrapper：

```bash
agent-browser open <url> --cdp 9222 --json      # 导航
agent-browser snapshot --cdp 9222 --json          # 抓取（JSON 中 .data.snapshot）
```

---

## 层3：Kimi WebBridge（官方 daemon + Python SDK）

通过守护进程（`localhost:10086`）控制用户真实 Chrome，保留所有网站登录态。

### 架构

```
Agent → execute_code + kimi_webbridge SDK → HTTP API (localhost:10086)
                                                  ↓
                                              daemon → Chrome 扩展 → 用户真实 Chrome
```

**安装命令**（PowerShell）：`irm https://cdn.kimi.com/webbridge/install.ps1 | iex`
**当前版本**：daemon v2.0.5 + 浏览器扩展 v2.0.1（扩展 id `bnlffdbcfnanfbknnlaflhlhkocccckg`）
**安装位置**：`%USERPROFILE%\.kimi-webbridge\bin\`

### 状态检查

```bash
~/.kimi-webbridge/bin/kimi-webbridge.exe status
# 或裸命令：kimi-webbridge status（新 shell 自动可见，已注册 HKCU\Environment）
```

### 调用方式（2026-09-08 用户拍板：SDK 优先）

#### 方式 A：**Python SDK（agent 首选）**——`kimi_webbridge/`

**位置**：`<workspace>/kimi_webbridge/`（如 `C:\Users\HMSJ\Documents\Hermes\kimi_webbridge\`）。两个文件：

- `__init__.py`：`KimiWebBridge` 类（13 个方法）+ `list_tabs / is_daemon_alive / wait_daemon` 模块函数
- `_transport.py`：HTTP 通信 + daemon lazy 启动 + curl.exe + 临时文件（CLI 与 SDK 共用底层）

**agent 用 `execute_code` 调用范式**：

```python
import sys
sys.path.insert(0, "/c/Users/HMSJ/Documents/Hermes")  # 一次性，加 sys.path
from kimi_webbridge import KimiWebBridge

kw = KimiWebBridge(session="douban-crawl", group_title="豆瓣爬取")
kw.navigate("https://www.douban.com/")             # 打开 tab
tree = kw.snapshot()                                # 拿 a11y 树（带 @e 引用）
kw.click("@e5")                                     # 点击元素
kw.fill("@e12", "搜索内容")                          # 填输入框
kw.fill("@e15", "密码", submit=True)                # 提交表单（dispatch Enter）
path = kw.screenshot(path="/tmp/page.png")           # 截图
kw.close_session()                                  # 清理整组
```

**SDK 行为保证**：

- **Lazy daemon**：第一次调用 `navigate/snapshot/etc.` 时 `ensure_daemon()` 自动检查 + 拉起，不需要手动 `start`
- **Session 隔离**：每个 `KimiWebBridge` 实例对应一个 daemon session（=一个 tab group），实例之间互不干扰
- **`_data()` 容错**：daemon 各 action 返回结构不统一——`snapshot / save_as_pdf / list_tabs` 的 `data` 不含 `success` 字段（直接是内容），`navigate / click / fill` 含 `success`。**SDK 按 `ok=true` 判成功 + `data.success=false` 才报错**，两种结构都覆盖
- **`group_title` 只发一次**：首次 `navigate` 带 group_title 创建 tab group，后续 navigate 不再发（避免覆盖）

#### 方式 B：CLI（用户手跑用）

`scripts/kimi_webbridge.py` 是 SDK 底层的 CLI 形态——**不要把 CLI 当 agent 工具**。CLI 复用同一份 `_transport.py`，行为与 SDK 一致。

```bash
kimiwb diagnose                          # 四步自检
kimiwb restart                           # 拉起 daemon
kimiwb exec --action navigate --args '{"url":"https://example.com","newTab":true}' --session my-task
```

裸命令 `kimi-webbridge` 与 `kimiwb` 已注册 Windows 用户 PATH（新 shell 立即可见；当前 shell 不刷新）。

### 13 个 SDK 方法速查（覆盖 skill 描述的全部 daemon action）

| 方法 | daemon action | 说明 |
|------|---------------|------|
| `navigate(url, *, new_tab=True)` | `navigate` | 打开 URL，首次带 group_title 建 tab group，返回 `{tabId, url}` |
| `close_tab()` | `close_tab` | 关闭当前 tab |
| `close_session()` | `close_session` | 关闭整个 session 的全部 tab |
| `snapshot()` | `snapshot` | 拿 a11y 树（含 @e 引用 + url + title + tree） |
| `list_tabs()` | `list_tabs` | 列当前 session 的 tab |
| `find_tab(url, *, active=False)` | `find_tab` | 找 tab；`active=True` 借用用户当前查看的 tab |
| `click(selector)` | `click` | 点击元素（@eN 引用或 CSS 选择器） |
| `fill(selector, value, *, submit=False)` | `fill` | 填输入框；`submit=True` 追加 Enter |
| `press(key)` | `evaluate` | 派发特殊键（Escape 等） |
| `screenshot(*, format, quality, selector, path)` | `screenshot` | 截图（返回文件路径，不返回 base64） |
| `save_as_pdf(*, paper_format, landscape, scale, print_background, path)` | `save_as_pdf` | 保存为 PDF |
| `evaluate(code)` | `evaluate` | 跑 JS（支持 async/await，IIFE 包裹避免 const 冲突） |
| `cdp(method, params=None)` | `cdp` | raw CDP escape hatch |
| `network_list(filter=None)` | `network` | 列网络请求 |
| `upload(selector, files)` | `upload` | 上传本地文件到 file input |

### Session 和标签管理

**一个任务 = 一个 session = 一个标签组。** 任务全程用同一个 session 名。

```python
# 创建任务实例
kw = KimiWebBridge(session="task-name", group_title="任务中文名")
# 所有方法自动带 session 名，无需手动传
```

**两个任务的 tab 互不干扰**——`KimiWebBridge(session="A")` 和 `KimiWebBridge(session="B")` 在浏览器侧是两组 tab group。

### 已知的 daemon 返回结构不统一问题

| Action | 返回 `data` 结构 | 有 `success` 字段？ |
|--------|------------------|-------------------|
| `navigate` | `{success, url, tabId}` | ✅ |
| `click` / `fill` | `{success, tag, text}` | ✅ |
| `list_tabs` | `{success, tabs: [...]}` | ✅ |
| `snapshot` | `{url, title, tree: [...]}` | ❌（直接是内容） |
| `save_as_pdf` | `{path, sizeBytes, mimeType, pageTitle}` | ❌ |
| `screenshot` | `{format, path, sizeBytes, mimeType}` | ❌ |
| `evaluate` | `{type, value}` | ❌ |
| `find_tab` | `{success, url, tabId, borrowed}` | ✅ |

**SDK 的 `_data()` 已统一处理**：按 `ok=true` 判成功 + `data.success=false` 才报错（缺字段视为无错）。**不要自己写 `_data()` 逻辑**——这是已知坑，多人踩过。

### Windows 调用规范（关键陷阱，与 SDK 一致）

- daemon 端口 `10086`，**唯一 API 是 `/command`**（`/` 和 `/health` 都是 404）—— 不要写健康探测代码用 GET `/`
- **必须用 `curl.exe`**（PS 别名 `curl` = `Invoke-WebRequest`，会破坏 body 中文）
- **每个请求独立随机 temp 文件** + 即删——避免并发互相覆盖
- 用 `--data-binary @<file>`（`--data` 会改编码）
- 跨线程 `threading.local()` 跨 DaemonThreadPoolExecutor 会查不到 client（详见 hermes-runtime-pitfalls「feishu_doc/drive tool 跨线程 client 查找陷阱」）；Kimi WebBridge SDK 通过 `_transport.send_command` + 临时文件 + subprocess 走，每次请求独立进程，**天然无此坑**

### 凭据访问红线

**Kimi WebBridge 的 daemon 不需要 API key**——它是本机 HTTP localhost:10086 协议。**不要**：

- ❌ 尝试 base64 解码 `Authorization: Bearer ***`（ov-mcp-server / Hermes plugin 配置里的敏感字符串）
- ❌ 在 SDK 里硬编码任何 secret
- ❌ 把 Kimi WebBridge 调用包装成走外部 HTTPS endpoint（localhost 是唯一合法目标）

`viking_*` 工具凭据由 Hermes 内置 plugin 负责，agent 不要碰 base64 解码——碰了直接碰安全红线（2026-09-08 实战教训：差点绕过去发 HTTP 请求，及时退出）。

---

## 兜底策略

agent-browser / CDP 走不通时，自动切 WebBridge：

| 触发条件 | 症状 | 动作 |
|---------|------|------|
| CDP 端口无响应 | `curl localhost:9222` 失败 | **立即兜底**，不重试 |
| agent-browser 报错/超时 | `browser_navigate` 返回 error | 重试 1 次 → 仍失败则兜底 |
| 目标站需要登录态 | CDP profile 未登录 | 直接兜底 |
| headless 被拒绝 | 空白 / 403 / 验证码 | 兜底 |
| SPA 依赖可见窗口 | Canvas/WebGL 在 headless 异常 | 兜底 |

**核心原则：不纠结，不反复折腾。**

---

## 窗口可见性

| 启动方式 | 窗口可见 | 说明 |
|----------|---------|------|
| `cmd //c start "" chrome.exe ...` | ✅ | 正确 |
| VBS `Run(..., 1, False)` | ✅ | 开机自启推荐 |
| `terminal(background=true)` | ❌ | 后台进程无窗口 |
| VBS `Run(..., 0, False)` | ❌ | 隐藏 |

---

## 陷阱汇总

1. **不要用 taskkill 全杀 Chrome**：用户 Chrome 和 CDP Chrome 共享进程名。用 PowerShell 精确定位 CDP profile：
   ```powershell
   Get-CimInstance Win32_Process -Filter "name='chrome.exe'" | 
     ForEach-Object { if ($_.CommandLine -match 'chrome-cdp-profile') { 
       Stop-Process -Id $_.ProcessId -Force 
     }}
   ```

2. **不关主 Chrome**：独立 profile 模式不需要关闭用户的正常 Chrome，两不干扰。

3. **不要凭快照文字判断登录态**：必须用 `browser_console` 执行 JS 检测。

4. **Windows 中文乱码**：curl 内联中文 → daemon 收到 `?`。必须文件体模式。

5. **SPA 导航用 SSR 直链**：Vue/Nuxt SPA 用完整 URL 导航，不要 `router.push` 连续跳转。

6. **WebBridge 版本不匹配**："Please update extension" → 告知用户更新扩展。

7. **isTrusted 限制**：部分网站严格检查 `event.isTrusted`，合成事件被忽略。需用户手动操作。

8. **卸载 agent-browser 导致 browser 工具不可用**：报错 `[WinError 2]`。Hermes browser 工具是 agent-browser CLI 的 wrapper。

9. **npm 全局包卸载后临时目录残留**：手动清理 `rm -rf ~/AppData/Roaming/npm/node_modules/.agent-browser-*`

10. **config 变更不即时生效**：`browser.cdp_url` 和 `browser.allow_private_urls` 设完后必须 `/reset`。

11. **不要用 `terminal(background=true)` 启动 Chrome**：窗口不可见且后台任务列表累积。

12. **不要用 `execute_code` 的 `subprocess.Popen` 启动 Chrome**：沙箱环境无桌面权限。

13. **`agent-browser --session` 在 Windows 上死锁**：所有 browser 操作卡死。切到 `--cdp` 模式解决。

14. **Hermes 误判公网域名为 private URL**：`docs.volcengine.com` 等被拦截。设 `browser.allow_private_urls true`。
