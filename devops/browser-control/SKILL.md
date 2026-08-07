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
| "用我浏览器"/"我登录的"/"操作已登录网站" | 层3：Kimi WebBridge | 继承用户登录态 |

**选层规则：** 用户没指定时默认 agent-browser → CDP失败自动切 WebBridge → 不纠结。

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

## 层3：Kimi WebBridge

通过守护进程（`localhost:10086`）控制用户真实 Chrome，保留所有网站登录态。

### 架构

```
Agent → HTTP API (localhost:10086) → 守护进程 → CDP → Chrome 扩展 → 用户真实 Chrome
```

### 状态检查

```bash
~/.kimi-webbridge/bin/kimi-webbridge.exe status
```

### 调用方式：execute_code（推荐）

```python
import json, subprocess, os

payload = {
    "action": "navigate",
    "args": {"url": "https://example.com", "newTab": True, "group_title": "任务名"},
    "session": "my-task"
}

tmpfile = os.path.join(os.environ["TEMP"], f"wb-req-{os.urandom(4).hex()}.json")
with open(tmpfile, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False)

result = subprocess.run(
    ["curl.exe", "-s", "-X", "POST", "http://127.0.0.1:10086/command",
     "-H", "Content-Type: application/json", "--data-binary", f"@{tmpfile}"],
    capture_output=True, text=True, timeout=30
)
os.remove(tmpfile)
print(result.stdout)
```

**为什么文件体模式：** 中文经 shell 管道到 daemon 会乱码。Python `json.dump` 写 UTF-8 文件再 `--data-binary`，彻底绕过。

### 工具速查

| 工具 | 核心参数 | 说明 |
|------|---------|------|
| `navigate` | `url`, `newTab`, `group_title` | 打开页面 |
| `find_tab` | `url`, `active` | 切换到已有标签 |
| `snapshot` | — | 可访问性树 |
| `click` | `selector` | 合成点击 |
| `fill` | `selector`, `value` | 填表 |
| `evaluate` | `code` | 执行 JS |
| `screenshot` | `format`, `quality`, `selector` | 截图 |
| `list_tabs` | — | 列出所有标签 |
| `close_session` | — | 关闭任务所有标签 |

### Session 和标签管理

**一个任务 = 一个 session = 一个标签组。** 任务全程用同一个 session 名。

```json
{"action":"navigate","args":{"url":"https://example.com","newTab":true,"group_title":"任务中文名"},"session":"task-name"}
```

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
