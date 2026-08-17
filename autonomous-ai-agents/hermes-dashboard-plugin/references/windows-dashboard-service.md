# Windows Dashboard 服务部署实战 — channel-sessions / ops-panel 网页版（2026-08-10）

完整落地案例：桌面端插件（desktop-plugins/）因 Hermes 0.20.0 打包版 SDK blob shim 缺陷
全崩（`TypeError: t is not a function` / `Unexpected token ']'`，错误在 app.asar 的
vendor-react chunk 里，非插件代码）→ 用户拍板「换个思路做成网页版」→ 走 web dashboard
插件形态，后端零改动。

## 决策逻辑（为什么网页版可行）

- 死的是**桌面端 UI 壳**，后端是活的：`agent.log` 有 `Mounted plugin API routes:
  /api/plugins/channel-sessions/` 与 `ops-panel/`（config.yaml `plugins.enabled` 挂载）。
- 两个插件本来就以 dashboard 插件格式存在（`plugins/<id>/dashboard/manifest.json` +
  `plugin_api.py`），`/api/dashboard/plugins` 已识别（`has_api: true`），只缺
  `dist/index.js`（前端 bundle）且 `tab.hidden: true`。
- 于是：补 dashboard 前端 + manifest 取消 hidden → 标签页出现在 web dashboard。

## 目录与部署

```
~/AppData/Local/hermes/plugins/<id>/dashboard/
├── manifest.json        # name/label/icon/version/tab{path,position}/api
├── plugin_api.py        # FastAPI 路由（已在 web_server 挂载）
├── dist/index.js        # esbuild 产物（IIFE）
└── <id>_service/        # 业务逻辑包
```

manifest 显示标签页的关键：
```json
{ "icon": "MessageSquare",
  "tab": { "path": "/channel-sessions", "position": "end" },
  "api": "plugin_api.py" }
```
（去掉 `"hidden": true` 即显示；icon 用 Lucide 名。）

## 源码 → 构建 → 部署

- 源码放工作区：`Projects/hermes-web-tools/<plugin>-web/src/index.jsx`（JSX，`const React = SDK.React`）
- 构建：`esbuild src/index.jsx --bundle --format=iife --outfile=dist/index.js --minify`（classic JSX transform，React 变量解析到 SDK.React）
- 部署：`cp dist/index.js ~/AppData/Local/hermes/plugins/<id>/dashboard/dist/index.js`
- 语法验证：`node --check dist/index.js`

## manifest 生效：必须 rescan 或重启进程

扫描器 `_get_dashboard_plugins()` 每进程缓存一次；`GET /api/dashboard/plugins` 读缓存。
`rescan` 端点要登录态（401）。本机做法：重启服务计划任务
（`scripts/restart-dashboard.ps1`：Stop-ScheduledTask → 杀 `--port 9120` 匹配 PID → Start → 轮询端口）。

## 服务形态（本机三个 web 相关端口）

| 端口 | 服务 | 计划任务 | 用途 |
|---|---|---|---|
| 8644 | gateway | Hermes_Gateway | 渠道消息网关 |
| 9119 | serve（headless，无 UI） | HermesRemoteServe | 远程 API 接入（Tailscale） |
| 9120 | dashboard（网页 UI） | HermesDashboard | 浏览器访问 + 插件标签页 |

`dashboard_remote.vbs` 关键行（官方隐藏控制台模式，venv 垫片自动跟随 update）：
```vbs
sh.Run """C:\Users\HMSJ\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"" -m hermes_cli.main dashboard --host 0.0.0.0 --port 9120 --no-open --skip-build", 0, False
```

## 验证命令

```bash
# dashboard 活着：/ 302 → /login
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9120/
# 插件注册（无 hidden = 标签页会显示）
curl -s http://127.0.0.1:9120/api/dashboard/plugins
# 后端 API 挂载（401 = 鉴权门，活着）
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9120/api/plugins/channel-sessions/sessions
# 静态 bundle 可服务（需登录态，未登录 302）
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9120/dashboard-plugins/channel-sessions/dist/index.js
```

## 前端数据通道（SDK 实测）

- `SDK.fetchJSON('/api/plugins/<id>/sessions?limit=500')` — 自动带登录态，非 2xx 抛 `Error("<status>: <body>")`
- 轮询模式：列表 15s / 详情 30s，`useEffect` + `setInterval` + `alive` flag 清理
- UI 状态记忆：`localStorage`（dashboard 无 ctx.storage，与桌面 SDK 不同）
- 破坏性操作：`window.confirm`（dashboard SDK 无 ConfirmDialog）

## 踩坑清单（本次实锤）

1. **serve ≠ dashboard**：用户访问 9119 登录后报 `Headless backend (hermes serve): web UI disabled`。serve 不提供 SPA，必须另起 dashboard 进程。
2. **`--skip-build` 缺失 → 卡 vite 构建**：进程 re-exec 后无端口、无日志，agent.log 停在 venv 垫片；加 `--skip-build` 用 `hermes_cli/web_dist/` 秒起。
3. **manifest 缓存**：改 manifest 后清单仍显示旧 `tab.hidden: true` + 默认 path/position（path/position/entry 是代码默认值，勿误判为新值已生效）。
4. **PowerShell 5.1 无 BOM ps1 乱码**：UTF-8 中文/em dash 被按 GBK 解析 → 报错行号漂移 + 假「字符串缺少终止符」。所有 ps1 先加 UTF-8 BOM（python 3 行）。
5. **bash 吞 `$`**：内联 `powershell -Command "...$c..."` 里 `$c`/`$_` 被 bash 展开成空 → 语法错。复杂命令一律写 .ps1 文件执行，不在 -Command 里内联变量逻辑。
6. **write_file 写 ps1 的 `\"`**：JSON 转义会原样落盘（`\"` 留在文件里），PowerShell 解析报错。落盘后 `od -c` / `grep -n` 核对，或写文件后立即 patch 掉反斜杠。

## 遗留

- `dashboard.basic_auth.secret` 未配置 → 每次重启 dashboard 登录态失效（agent.log 提示）。
- 桌面端插件仍坏（SDK shim 缺陷，等官方修复或桌面端重新打包）。
- 远程访问：Tailscale `http://100.78.192.8:9120`。
