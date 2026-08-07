---
name: cdp-browser-debugging
description: CDP 直连用户真实浏览器调试行为问题。触发词：点了没反应、调试浏览器、用我的浏览器。
metadata:
  version: "1.0.0"
---

# CDP 直连真实浏览器调试

当用户报告**他自己浏览器里的行为问题**（第三方登录点了没反应、某网站 Chrome 好 Edge 坏、扩展干扰）时，必须在**用户的真实浏览器**里复现——真实 profile（cookie/扩展/登录态全保留）+ 真实鼠标输入（isTrusted=true）抓网络请求和 JS 报错。不要用 agent 独立浏览器查资料代替（用户明确纠正过："我让你用我的浏览器调试"）。

与 browser-control（user-owned，需 `hermes curator adopt` 才能后台改）是姊妹篇：browser-control 管日常操控分层，本 skill 管行为问题复现调试。

## 前置：WebBridge 优先，但先验证它连的是哪个浏览器

用户浏览器有登录态、优先走 Kimi WebBridge（见 browser-control 层3）。**但 daemon 连的不一定是用户日常浏览器**——实测它可能连的是 Kimi 桌面应用内嵌的浏览器实例。验证：

```bash
# navigate 到任意页后 evaluate：
navigator.userAgent
# 含 "Edg/" = Edge；纯 "Chrome/" = Chrome
```

用户说"我的 Chrome 没装插件"而 daemon 却连着扩展 → 八成是 Kimi 桌面应用内嵌实例，WebBridge 这条路作废，直接转 CDP 直连。

## 完整流程（CDP 直连真实浏览器）

### 1. 完全退出目标浏览器

后台进程不杀干净的话，带调试端口的新实例会被复用忽略参数（Chromium 经典行为）。git-bash 里 `/F` 会被路径转换，用 MSYS_NO_PATHCONV=1：

```bash
MSYS_NO_PATHCONV=1 taskkill /F /IM msedge.exe   # 只杀目标浏览器，不碰 chrome
tasklist | grep -i msedge.exe                   # 确认 0 残留
```

### 2. 带调试端口启动（真实 profile）

**端口用 9223+，绝不要用 9222！** `~/.hermes/chrome-cdp-profile` 的 agent Chrome 默认占 9222（`browser.cdp_url` 指向它），`curl localhost:9222/json/version` 返回的可能是 **agent 浏览器而非目标浏览器**——本会话因此误连一整轮（/json/list 里看到的"历史标签"其实是 agent 浏览器自己开过的页面）。调试用户浏览器一律换端口，启动后先用 psutil 确认监听端口归属。

**参数必须用 Python `subprocess.Popen([...])` 数组传参**——bash 直接启动 Windows GUI 程序会丢参数：实测 msedge 主进程命令行只剩 `--remote-debugging-port=9223`，`--user-data-dir` 和 `--remote-allow-origins` 全被吞（`--remote-allow-origins=*` 的 `*` 被 glob 展开、带引号/等号的参数在 bash→Windows 参数转换时失效——**引号包裹也救不了**）。用系统 Python（`C:\Users\HMSJ\AppData\Local\Programs\Python\Python312\python.exe`）写启动脚本，execute_code 沙箱的 subprocess 无桌面权限：

```python
import subprocess
subprocess.Popen([
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--remote-debugging-port=9223",
    "--remote-allow-origins=*",
    r"--user-data-dir=C:\Users\HMSJ\AppData\Local\Microsoft\Edge\User Data",
    "about:blank"
])
```

要点：
- `--user-data-dir` 指向**用户真实 profile 路径** → cookie/扩展/登录态全保留，复现的就是用户现场
- `--remote-allow-origins=*` **必须加**（新版 Chromium 拒绝无此参数的 WS 连接，报 403 "Rejected an incoming WebSocket connection... Use the command line flag --remote-allow-origins"）
- Chrome 同理：`r"C:\Program Files\Google\Chrome\Application\chrome.exe"`
- **subprocess 拿到的 PID 是启动器进程**：Chromium 启动器 spawn 真浏览器主进程后自身 exit 0 退出属正常——判断浏览器是否存活要看"无 `--type=` 的主进程" + 端口连通，别信 spawn PID 的退出（曾因此误判"Edge 启动即退"多轮）

### 3. 验证端口 + 看标签

```bash
curl.exe -s http://127.0.0.1:9222/json/version   # 通 = {"Browser":"Chrome/...","webSocketDebuggerUrl":...}
curl.exe -s http://127.0.0.1:9222/json/list       # 列出恢复的标签——注意找历史现场的 Error 页（如 OAuth state 过期显示 Error 400，这本身就是"点了没反应"的根因之一）
# 开新标签（PUT）：
curl.exe -X PUT "http://127.0.0.1:9222/json/new?https://login.tailscale.com/"
```

### 4. Python websocket-client 连 CDP 复现 + 抓包

- Hermes venv 的 python 无 pip → 用系统 Python：`C:\Users\HMSJ\AppData\Local\Programs\Python\Python312\python.exe`（websocket-client 已装；缺则 `python -m pip install websocket-client`）
- 模板脚本：`scripts/edge-cdp-repro.py`（参数化：URL、按钮匹配文字）——连 tab → Network/Runtime.enable → 真实鼠标输入（`Input.dispatchMouseEvent` mousePressed/mouseReleased = isTrusted=true，等效真人手点）→ 捕获 `Network.requestWillBeSent` / `Network.loadingFailed` / `Runtime.exceptionThrown` / `Runtime.consoleAPICalled`

**"点了没反应"的判定标准**：点击后 location 未变 + 无新增网络请求 + 无 JS 异常 = 点击事件根本没触发导航（事件层被吞）；有请求但 loadingFailed = 网络层失败。

### 5. 收尾

调试完杀调试实例，让用户正常方式重启浏览器。调试端口实例接管了真实 profile，长期开着不安全。

## 已验证的坑（2026-08 实测）

1. **bash 星号 glob**：`--remote-allow-origins=*` 不带引号会被展开，参数静默失效 → 403。必须 `"--remote-allow-origins=*"`。
2. **WebBridge 后台 tab 输入无效**：WebBridge 打开的 tab 若 `active:false`（list_tabs 可见），CDP 真实输入点击无反应——是假象不是真问题，用户前台手动操作可能完全正常。复现前确认目标 tab 在前台。
3. **WebBridge 硬限制**：`navigate chrome://...` / `edge://...` 直接报 "Cannot access chrome:// and edge:// URLs"——浏览器内部管理页必须用户手动操作。
4. **OAuth 一次性 URL 陷阱**：用户给的 OAuth 链接（accountchooser 等带 state/dsh 参数）可能已被消费/过期——打开显示 Error 400，点账号当然没反应。别拿过期 URL 复现，从源头重走完整流程（如 login.tailscale.com → 点 Sign in with Google → 让 Google 生成新鲜 state）。
5. **判断 WebBridge 控制的是哪个浏览器**：/status 只有 extension_id（同扩展包在 Chrome/Edge 里 ID 相同），无法区分浏览器；必须 evaluate UA。
6. **execute_code 里跑 CDP 脚本可能触发安全审批**：脚本运行时若审批超时会被 BLOCKED——先告知用户脚本将做什么，请求确认后再跑，避免中断。

7. **9222 是 agent Chrome 的端口（误连元凶）**：`~/.hermes/chrome-cdp-profile` 的 agent Chrome 带 `--remote-debugging-port=9222` 常驻（开机自启 VBS），`curl 9222/json/version` 显示的是它。判别 CDP 端点归属：`psutil.process_iter` 拿浏览器主进程（无 `--type=`）命令行，看 `--user-data-dir` 值——`chrome-cdp-profile` = agent 的；`Microsoft\Edge\User Data` = 用户 Edge；`Google\Chrome\User Data` = 用户 Chrome。

8. **真实 profile 可能拒绝开调试端口（重要）**：Edge/Chrome 用真实 profile 启动时，主进程活着但调试端口**永不监听**（全新临时 profile 秒开，同环境对照实验钉死差异在 profile 内容；原因未最终定位，排除扩展/组策略/端口占用后仍复现）。**A/B 诊断法**：复制 `Default\Network\Cookies` + `Default\Login Data` + `Default\Local Storage`（Chromium 新版本 cookie 在 `Network\` 子目录，不在 `Default\` 根）到临时 profile 目录，用它带调试端口启动——既有用户登录态又能开端口、还能隔离扩展变量。本会话凭此法定位：真实 profile 点 Google 登录 0 请求 0 异常（静默失败）vs 临时 profile（同 cookie 无扩展）27 请求正常跳转 → 差异在扩展/配置而非网络/cookie/服务端。收尾：删临时 profile 即可，用户真实数据零改动。

9. **强杀（taskkill /F）浏览器会留孤儿进程占 profile**：孤儿 gpu/子进程（父进程已死）继续持有 profile 锁，下次启动检测到"已有实例"直接退出。启动前 `tasklist | grep -i msedge` 确认 0 残留；杀不干净就再杀一轮。

## 已验证的补充（2026-08 后半段实测）

- **系统 Python subprocess 启动的 Edge 有真实窗口、CDP 真实输入有效**（临时 profile 复现中点击后抓到 27 个网络请求正常跳转）——CDP 直连场景不受"后台 tab 输入不派发"影响（那是 WebBridge 场景的假象，见坑 2）。
- **真实 profile 的 A/B 结论**（Edge 第三方 Google 登录"点了没反应"案例）：真实 profile（14 个扩展 + 长期配置）点击后 0 请求 0 异常；临时 profile（复制同 cookie、零扩展）点击后 27 请求正常跳转 accounts.google.com → 问题变量 = 扩展或 profile 配置，不是网络/cookie/Google 服务端。给用户的判别实验：真实浏览器开无痕窗口（不加载扩展）再点——无痕正常 = 扩展实锤，逐个禁用（优先全站注入型的 Video Download Helper / Listen 1 类）；无痕也坏 = profile 配置损坏，重置设置或新建 profile。
