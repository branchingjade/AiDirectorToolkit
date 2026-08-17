---
name: hermes-dashboard-plugin
description: Build UI plugins for the Hermes web dashboard — custom tabs, slots, and backend routes.
version: 1.0.0
tags: [hermes, dashboard, plugin, frontend, react]
related_skills: [hermes-monitoring]
---

# Hermes Dashboard Plugin Development

Build and deploy custom UI plugins for the Hermes web dashboard (`hermes dashboard`). Plugins add tabs, inject components into shell slots, replace built-in pages, and (when bundled) register FastAPI backend routes.

## When to Use

- User asks to add a custom tab/page to the Hermes dashboard
- User wants to monitor something in the dashboard (token usage, costs, custom metrics)
- User asks to extend or reskin the dashboard beyond themes

## Reference Files

- `references/token-monitor-plugin.js` — Working example using `fetchJSON` to call bundled backend route (correct pattern — NOT `getSessions()`)
- `references/bundled-plugin-pattern.md` — Complete backend+frontend pattern for bundled plugins with `plugin_api.py`
- `references/state-db-sessions-schema.md` — state.db sessions table schema (note: `estimated_cost_usd` etc. exist in DB but NOT in dashboard REST API)
- `references/ui-patterns.md` — UI 整改可复用模式（批量串行/防重复提交/自绘确认浮层+焦点陷阱/骨架屏/列表行键盘/空态区分/错误重试）+ **4K zoom 适配方案** + 用户拍板「筛选选项默认全部展开」+ **进行中会话判定（is_active=ended_at NULL+5min 窗口，last_activity_at 秒单位）** + **筛选单向层级联动（上层不被下层收缩）** + **后端改动须重启 dashboard** + 页面「卡住」排查链（channel-sessions 2026-08-10 实战）
- `references/windows-dashboard-service.md` — Windows 常驻 dashboard 服务实战（channel-sessions/ops-panel 网页版）：serve vs dashboard、--skip-build、manifest 缓存重扫、计划任务+vbs、esbuild 构建、验证命令

## Quick Reference

### Directory Layout

```
~/.hermes/plugins/<name>/dashboard/
├── manifest.json        # required — tab config, icon, entry point
├── dist/
│   ├── index.js         # required — pre-built JS bundle (IIFE)
│   └── style.css        # optional — custom CSS
└── plugin_api.py        # ONLY for bundled plugins — backend FastAPI routes
```

### manifest.json

```json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "icon": "Sparkles",
  "version": "1.0.0",
  "tab": {
    "path": "/my-plugin",
    "position": "after:sessions"
  },
  "entry": "dist/index.js",
  "css": "dist/style.css"
}
```

Available Lucide icons: Activity, BarChart3, Clock, Code, Database, Eye, FileText, Globe, Heart, KeyRound, MessageSquare, Package, Puzzle, Settings, Shield, Sparkles, Star, Terminal, Wrench, Zap.

### JS Bundle (IIFE pattern)

```js
(function() {
  "use strict";
  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { useState, useEffect } = SDK.hooks;
  const { Card, CardHeader, CardTitle, CardContent, Badge } = SDK.components;

  function MyPage() {
    return React.createElement(Card, null,
      React.createElement(CardHeader, null,
        React.createElement(CardTitle, null, "My Plugin")
      ),
      React.createElement(CardContent, null,
        React.createElement("p", null, "Hello")
      )
    );
  }

  window.__HERMES_PLUGINS__.register("my-plugin", MyPage);
})();
```

### SDK Surface

```
SDK.React                    // React instance (never import React directly)
SDK.hooks.useState           // Standard React hooks
SDK.hooks.useEffect
SDK.hooks.useMemo
SDK.components.Card          // shadcn/ui components
SDK.components.CardHeader
SDK.components.CardTitle
SDK.components.CardContent
SDK.components.Badge
SDK.components.Button
SDK.components.Tabs / TabsList / TabsTrigger
SDK.api.getSessions(limit)  // Fetch session data (includes token counts, costs)
SDK.api.getConfig()         // Fetch config
SDK.api.getStatus()         // Agent status
SDK.fetchJSON(url)          // Authed fetch for custom endpoints
SDK.utils.cn(...)           // Tailwind class merger
SDK.utils.timeAgo(ts)       // "5m ago" from unix timestamp
```

### Data from SDK.api.getSessions()

```typescript
// SessionInfo — the TypeScript interface at web/src/lib/api.ts:1633
{
  id, source, model, title,
  started_at, ended_at, last_active, is_active,
  message_count, tool_call_count,
  input_tokens, output_tokens,
  preview, parent_session_id
}
```

**IMPORTANT**: `SessionInfo` does NOT include `estimated_cost_usd`, `billing_provider`, `reasoning_tokens`, or `cost_status`. These columns exist in state.db's `sessions` table but the dashboard REST API filters them out. Using `SDK.api.getSessions()` for cost data will silently return `undefined` (costs show as `$0.00`).

### Getting cost data: bundled plugin + backend route

The only way to expose cost data to a dashboard plugin is a **bundled plugin** with `plugin_api.py` that reads state.db directly:

```
<repo-root>/plugins/<name>/dashboard/
├── manifest.json          # must include "api": "plugin_api.py"
├── dist/index.js          # calls SDK.fetchJSON("/api/plugins/<name>/stats")
└── plugin_api.py          # FastAPI router reading state.db via sqlite3
```

The JS bundle calls `SDK.fetchJSON("/api/plugins/<name>/stats")` which auto-injects the session auth token. The Python backend reads `estimated_cost_usd`, `billing_provider`, etc. from state.db and returns them as JSON.

See `references/bundled-plugin-pattern.md` for a complete backend route example.

## Critical Constraints

### Bundled vs User plugins

| Property | User (`~/.hermes/plugins/`) | Bundled (`<repo>/plugins/`) |
|----------|------|---------|
| UI (manifest + JS + CSS) | ✅ | ✅ |
| Backend routes (`plugin_api.py`) | ❌ ignored | ✅ auto-loaded |
| Deployment | Drop files, rescan | Restart dashboard after adding |

User-plugin `plugin_api.py` files are deliberately ignored (security: GHSA-5qr3-c538-wm9j). If your plugin needs backend data processing (cost aggregation, state.db queries), deploy it as a bundled plugin.

### Desktop App ≠ Web Dashboard

The Hermes Desktop app (`hermes desktop`) and the web dashboard (`hermes dashboard`) are **separate frontends** that both talk to the same backend:

- **Web Dashboard**: React SPA at `web/src/`, loads bundled+user dashboard plugins. Accessible at `http://127.0.0.1:<port>`.
- **Desktop App**: Electron app at `apps/desktop/src/`, has its own hardcoded sidebar navigation. Does NOT load web dashboard plugins. Its source changes need a full rebuild (`apps/desktop/release/win-unpacked/`).

Web dashboard plugins appear as tabs in the web dashboard's top navigation bar. They do NOT appear in the Desktop app's sidebar. To add a panel to the Desktop app, modify `apps/desktop/src/app/desktop-controller.tsx` (add route), `apps/desktop/src/app/routes.ts` (add route constant), `apps/desktop/src/app/chat/sidebar/index.tsx` (add SIDEBAR_NAV entry), `apps/desktop/src/app/types.ts` (add SidebarNavId), plus i18n and keybind entries — then rebuild the Desktop app.

### No React bundling

Plugins do NOT bundle React or UI components. Use `SDK.React` (React.createElement) and `SDK.components.*`. If using JSX, bundle with esbuild/Vite with React as external and IIFE output format.

### Chart rendering

The SDK does NOT include chart libraries. Use raw SVG in `React.createElement` calls — no external dependencies needed. See `references/token-monitor-plugin.js` for a complete example with BarChart and HBarChart SVG components.

## Testing

### Check if dashboard is running
```bash
curl -s http://127.0.0.1:9119/api/dashboard/plugins
```

### Start dashboard
```bash
hermes dashboard --no-open --port 9119
```

### Force plugin rescan (no restart needed after adding new files)
```bash
curl http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

### Verify plugin assets are served
```bash
curl -s http://127.0.0.1:9119/dashboard-plugins/token-monitor/dist/index.js | head -3
```

### Open dashboard
http://127.0.0.1:9119 — the plugin tab appears in the top navigation bar.

## Critical Pitfalls

### ⚠️ serve ≠ dashboard：headless 后端没有网页 UI（2026-08-10 本机实测）

`hermes serve` 是 headless 后端：`cmd_dashboard` 里 `_headless_backend=True` → 设置 `HERMES_SERVE_HEADLESS=1` → `mount_spa()` 禁用 SPA。用户访问 `http://<ip>:9119/` 登录后报 `Headless backend (hermes serve): web UI disabled — use \`hermes dashboard\` for the browser UI.`。**网页 UI 必须独立跑 `hermes dashboard`**（另一个端口）。

### ⚠️ dashboard 无 HERMES_WEB_DIST 且无 --skip-build → 强制 vite 全量构建

main.py cmd_dashboard：`elif "HERMES_WEB_DIST" not in os.environ and not skip_build: _build_web_ui(PROJECT_ROOT / "web", fatal=True)`——**即使 `hermes_cli/web_dist/` 已存在也会重新构建**（npm install + vite build，几分钟且可能失败），表现为进程活着但端口迟迟不监听。**常驻服务必须加 `--skip-build`**（用现成的 `hermes_cli/web_dist/`，秒起）。注意构建产物目录是 `hermes_cli/web_dist/`（vite outDir），不是 `web/dist/`。

### ⚠️ /api/dashboard/plugins 返回进程级缓存

`_dashboard_plugins_cache` 进程级缓存，manifest.json 改动后需 `GET /api/dashboard/plugins/rescan`（**需鉴权**，未登录 401）或**重启 dashboard 进程**才生效。诊断时注意：清单里 `tab.path/position` 是代码默认值（`f"/{name}"` + `"end"`），`hidden:true` 才是缓存旧 manifest 的证据。

### ⚠️ Tabs/TabsList/TabsTrigger 组件在本机 dashboard SDK 渲染崩溃（2026-08-10 实测）

`SDK.components.Tabs/TabsList/TabsTrigger` 渲染期抛错 → **整个 SPA 白屏**（body 空，不是局部 error boundary）。@nous-research/ui 0.18.2 的封装接口与 Radix 原生 Tabs 不同且 node_modules 未装无法本地验证。**标签切换改用原生 `<button>` + useState 实现**（零依赖），Card/Button/Badge/Input 等已验证可用。

### ⚠️ user 插件的 API 挂载（plugins.enabled 机制）与 dashboard 插件机制并存

本机 `~/AppData/Local/hermes/plugins/<id>/dashboard/plugin_api.py` 通过 config.yaml `plugins.enabled` 被 web_server `_mount_plugin_api_routes()` 挂载（agent.log `Mounted plugin API routes: /api/plugins/<id>/`），与 skill 所述「user plugin 的 plugin_api.py 被忽略（bundled-only）」是**两套并存机制**——后者指 dashboard 插件扫描器（manifest `api` 字段）对 user 插件的安全限制。前端 dashboard 插件（manifest + dist）可用 `SDK.fetchJSON('/api/plugins/<id>/...')` 调已挂载的 API。**「API 404 = 鉴权门」同样适用**：未带 token 返回 401/404。

### ⚠️ Windows ps1 必须带 UTF-8 BOM（write_file 产物踩坑）

write_file 写 .ps1 是 UTF-8 无 BOM，PowerShell 5.1 按 ANSI/GBK 解析 → 中文注释/em dash 字节错位 → 字符串破裂 `ParserError`（报错行号与实际行偏移）。**任何 ps1 用前先加 BOM**：`python -c "p=...; d=open(p,'rb').read(); open(p,'wb').write((b'\xef\xbb\xbf' if not d.startswith(b'\xef\xbb\xbf') else b'')+d)"`。另：bash 双引号内 `$var` 会被 bash 展开——内联 PowerShell 带 `$` 一律改 ps1 文件。

### ⚠️ WebBridge cdp/evaluate 无 target 连到任意 tab（2026-08-10 教训）

Kimi WebBridge 的 cdp/evaluate **不指定 tabId 时连到哪个 tab 不确定**（本机连到用户浏览器另一个 RH 画布 tab，导致「接口 120s 超时/找不到按钮」全假象）。**必须先 `list_tabs` 拿 tabId，再 evaluate 带 `"tabId": <id>`**（cdp 无 target 参数则用 evaluate 带 tabId）。

### ⚠️ audit-classes.py 必须传 Windows 路径（MSYS /c/ 路径 glob 0 文件）

`python audit-classes.py <jsx> "C:\Users\...\web_dist\assets"` —— 传 `/c/Users/...`（MSYS 风格）时 Windows Python 的 `Path.glob` 匹配 0 个文件 → `css_text` 为空 → **全部类报 MISSING（缺失 N=总数、已补 0）**，看似审计爆炸实则路径无效。Web_dist 实际位置：`C:\Users\<u>\AppData\Local\hermes\hermes-agent\hermes_cli\web_dist\assets`（注意多一层 `hermes-agent/`）。

### ⚠️ patch 工具写 CSS 转义类名双重转义（`\`→`\\`）

用 `patch` 给 style.css 追加 `.\:focus-visible...`、`\/` 等转义选择器时，new_string 里的 `\` 会被再转义一层落盘成 `\\`（`.bg-destructive\\/10`），CSS 选择器失效（审计立即重新报 MISSING）。**修法**：`python -c "p=...; d=open(p,encoding='utf-8').read().replace('\\\\\\\\', '\\\\'); open(p,'w',encoding='utf-8',newline='\\n').write(d)"`（双反斜杠→单反斜杠，CSS 无合法双反斜杠场景，全文件替换安全），然后重跑审计确认。

### ⚠️ WebBridge list_tabs 空 = session 隔离，看不到用户已开标签

`list_tabs` 只列**当前 session 内**由 WebBridge navigate 打开的标签；用户浏览器里自己开的标签（如 Edge 里的 dashboard）不在列表，`find_tab` 报 `no tab matching`。诊断用户已开页面：要么用 WebBridge navigate 新开（继承登录态，若该浏览器登录过），要么让用户手动操作/硬刷新。

### ⚠️ dashboard 静态资源未登录 302

`curl /dashboard-plugins/<id>/dist/index.js` 未登录返回 **302（跳登录页，size 0）**，不是 404——静态资源也在 auth gate 后面。验证部署用磁盘文件时间戳 + 浏览器登录态，别用 curl 裸 URL 判断。

### ⚠️ WebBridge evaluate 的 code 里中文字面量会损坏（2026-08-10 反复踩）
evaluate 的 code 字符串经 bash→curl→WebBridge→CDP 传输链，**中文字面量被破坏**——`btns.find(b => b.textContent === "本地补丁")` 永远匹配不到、「导出」`indexOf` 永远 -1，导致误判「按钮不存在/详情没渲染」（截图证明其实都在）。**中文判断改用 unicode 转义**：`"\\u672c\\u5730\\u8865\\u4e01"`（本地补丁）——或**直接 screenshot + vision_analyze**（本会话最终验证全靠截图，最可靠）。CSS 选择器里的 `\\[` 转义同样会在传输链被吃（`.w-\\[400px\\]` 报 invalid selector）——用 className 遍历匹配代替 querySelector。

### ⚠️ 插件 Tailwind 类缺失 = 布局静默全乱（2026-08-10 实测，与桌面端同坑）

web_dist 编译产物**只含 web 源码用过的类**——插件 JS 的 className 只要 `web/src` 没用过就没编译，UI 不报错但布局全乱（实测 w-52 渲染成 2091px、w-[400px] 渲染成 946px）。**任意值类（w-[400px]、text-[10px]、max-w-[85%]）几乎全缺**，微间距（gap-1.5、py-1.5）、透明度变体（bg-muted/30）也缺。**修复模式**：manifest 加 `"css": "dist/style.css"`，自定义 CSS 按 Tailwind 标准值 + Hermes 主题变量补齐（Tailwind v4 @theme：`--color-muted/primary/border/accent` 均为 color-mix 体系，透明度用 `color-mix(in srgb, var(--color-muted) 30%, transparent)`）。**写完插件必审计**：跑 `scripts/audit-classes.py <plugin.jsx> [web_dist_assets_dir] [dist/style.css]`（从 JSX 提取全部 className → 对照 `hermes_cli/web_dist/assets/*.css` 查缺失，传 style.css 时已补类自动排除）——缺失类进 style.css。手动 grep 转义注意：`[`→`\[`、`/`→`\/`。

### ALWAYS clarify frontend BEFORE building
The user saying "加面板" or "加功能" is ambiguous. Ask: **"要加到 Hermes 桌面端侧边栏，还是 web dashboard 标签页？"** before writing any code. Desktop and web dashboard are completely separate frontends — guessing wrong wastes an entire session. See Desktop App ≠ Web Dashboard below.

### Bundled vs User plugins

- **Plugin not showing**: Check manifest.json is at `~/.hermes/plugins/<name>/dashboard/manifest.json` (note the `dashboard/` subdirectory). Call `/api/dashboard/plugins/rescan`.
- **JS bundle errors**: Open browser DevTools → Console. Common issues: `__HERMES_PLUGINS__ is undefined` (SDK didn't initialize, React render crash earlier), or the IIFE threw before calling `register()`.
- **Mismatched name**: `manifest.json:name` must match the first argument to `window.__HERMES_PLUGINS__.register(name, Component)`.
- **Browser redirects to Desktop app**: When using `hermes` browser tools, navigating to `127.0.0.1:9119` may route to the Hermes Desktop app instead of the web dashboard. The user should open the URL directly in their real browser. Verify with `curl` instead.

### ⚠️ serve ≠ dashboard: "Headless backend (hermes serve): web UI disabled"（2026-08-10 实测）

`hermes serve` is the **headless backend** — by design it serves **no web UI/SPA** (`HERMES_SERVE_HEADLESS=1`, mount_spa disabled). Hitting `serve` in a browser gives `Headless backend (hermes serve): web UI disabled — use hermes dashboard for the browser UI.` **The browser UI is a separate process: `hermes dashboard`.** If the user already has `serve` on 9119 (remote gateway), run a second `dashboard` service on a different port (this machine: **9120**). Diagnostic shortcut: a working dashboard `/` 302s to `/login`; a headless serve may show a login page too but rejects after login.

### ⚠️ `hermes dashboard` hangs without `--skip-build`（2026-08-10 实测）

`cmd_dashboard` (main.py) runs `_build_web_ui(web, fatal=True)` — a **full vite rebuild** — whenever `HERMES_WEB_DIST` is unset and `--skip-build` is absent, **even if a dist already exists**. The process re-execs then sits in npm build for minutes with **no port bound and no dashboard log lines**. Fix:
- Web UI dist lives at **`hermes_cli/web_dist/`** (vite outDir) — NOT `web/dist/`. Check `hermes_cli/web_dist/index.html` before launching.
- Launch with `--skip-build` when the dist exists → instant bind.
- `HERMES_WEB_DIST` env is the alternative, but Electron-packaged dists are deliberately stripped by `cmd_dashboard` (`_is_electron_packaged_web_dist`).

### ⚠️ Manifest/UI changes need a scan or restart — scanner caches per-process

`_get_dashboard_plugins()` caches discovered plugins **per process** (`_dashboard_plugins_cache`); `GET /api/dashboard/plugins` reads that cache. Editing `manifest.json` (e.g. removing `tab.hidden`) is not picked up until `GET /api/dashboard/plugins/rescan` — which is **auth-gated (401 without login)** — or the dashboard/serve process restarts. Stale-cache tell: the list shows `tab: {"path": "/<name>", "position": "end", "hidden": true}` — `path`/`position` are **code defaults** (`data.get("path", f"/{name}")`, `"position"` default `"end"`), `hidden` only added when explicitly true, and `entry` defaults to `"dist/index.js"` — so defaults + old hidden = old manifest still cached.

### ⚠️ `plugins.enabled` user plugins DO get backend routes mounted (this machine)

The "user plugins can't have backend" rule applies to the dashboard **plugin_api.py import path**. Separately, `web_server._mount_plugin_api_routes()` mounts `/api/plugins/<id>/...` for every plugin in `config.yaml plugins.enabled` (this machine: channel-sessions, ops-panel, quota-panel, skill-manager, kanban, hermes-achievements). So a user dashboard plugin whose `plugin_api.py` lives in the same `dashboard/` dir gets **both** a working backend AND a dashboard tab — `has_api: true` in the plugin list confirms. API calls return **401 without auth** — that's the auth gate (防枚举 oracle), not a broken route; `SDK.fetchJSON` injects the session token.

### Windows 常驻 dashboard 服务（计划任务 + vbs，2026-08-10 实测）

Same official pattern as the remote serve launcher (wscript + vbs + venv console python.exe re-exec 垫片 + `sh.Run cmd, 0, False` 隐藏控制台):

```vbs
sh.Run """C:\...\hermes-agent\venv\Scripts\python.exe"" -m hermes_cli.main dashboard --host 0.0.0.0 --port 9120 --no-open --skip-build", 0, False
```

- Scheduled task: `New-ScheduledTaskAction -Execute wscript.exe -Argument <vbs>` + `New-ScheduledTaskTrigger -AtLogOn` + `-RunLevel Highest`.
- Restart to rescan manifests: stop task → kill pids matching `--port <port>` → start task → poll the port.
- After `hermes update`, the venv re-exec 垫片 follows the new runtime automatically — never hardcode `generation-<hash>` paths.

### SDK components actually exposed (registry.ts exposePluginSDK, 2026-08-10)

`Card, CardHeader, CardTitle, CardContent, Badge, Button, Checkbox, Input, Label, Select, SelectOption, Separator, Tabs, TabsList, TabsTrigger, PluginSlot` — plus `SDK.fetchJSON`/`authedFetch`/`buildWsUrl`, hooks `useState/useEffect/useCallback/useMemo/useRef/useContext/createContext`, `utils.cn/timeAgo/isoTimeAgo`, `useI18n`. There is **no** Dialog/ConfirmDialog/DropdownMenu in the dashboard SDK (unlike the desktop SDK) — build overlays as fixed-position divs and use `window.confirm` for destructive ops.

### JSX → IIFE via esbuild classic transform

```jsx
(function () {
  "use strict";
  const SDK = window.__HERMES_PLUGIN_SDK__;
  if (!SDK) return;
  const React = SDK.React;   // JSX compiles to React.createElement — resolves to this
  // ...components...
  window.__HERMES_PLUGINS__.register("my-plugin", MyPage);
})();
```
```bash
esbuild src/index.jsx --bundle --format=iife --outfile=dist/index.js --minify
```
esbuild's default classic JSX transform emits `React.createElement`, which resolves to the local `const React = SDK.React` — no React import, no externals. `node --check dist/index.js` validates the bundle. Keep sources in the workspace (e.g. `Projects/hermes-web-tools/<plugin>-web/src/`), copy the built `dist/index.js` into `plugins/<id>/dashboard/dist/`.

### Dashboard auth: sessions die on restart without a `secret`

`dashboard.basic_auth` with `username` + `password_hash` but **no `secret`** → signing key random per-process → **every dashboard restart invalidates browser sessions** (agent.log: "Sessions will not survive a restart…"). Set `dashboard.basic_auth.secret` (or `HERMES_DASHBOARD_BASIC_AUTH_SECRET`) for stable logins.

Worked example (channel-sessions v1.6.0 / ops-panel v1.1.0 → dashboard tabs): `references/windows-dashboard-service.md`.
