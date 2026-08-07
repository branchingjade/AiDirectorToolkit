# 桌面内置 UI 面板体系与「面板消失」排查（2026-08-06 实测）

用户报「hermes 客户端之前好用的 UI 小面板没了：上下文用量、定时任务面板、用量面板、代理面板」的完整排查路径与结论。

## 面板 → 位置映射（源码级）

| 用户说法 | 组件 | 位置 | 默认 |
|---|---|---|---|
| 上下文用量 | `ContextUsagePanel`（`apps/desktop/src/app/shell/context-usage-panel.tsx`） | 状态栏 `context-usage` 芯片，`app/shell/hooks/use-statusbar-items.tsx:527` 接线；`hidden: !contextUsage` | 隐藏 |
| 定时任务 | cron 状态栏入口 + `SidebarCronJobsSection`（`app/chat/sidebar/cron-jobs-section.tsx`） | 侧边栏区在 `app/chat/sidebar/index.tsx:1499`，`cronJobs.length > 0` 即渲染 | 状态栏入口隐藏；侧边栏区默认在 |
| 代理/网关 | `GatewayMenuPanel`（`app/shell/gateway-menu-panel.tsx`） | 状态栏 gateway 芯片（连接状态/重启/平台） | 随状态栏（不在隐藏默认列表） |
| 用量/余量 | quota-panel 插件 | 标题栏右上角 `TITLEBAR_AREAS.right`（`~/AppData/Local/hermes/desktop-plugins/quota-panel/plugin.js:360`） | 独立于状态栏 |
| 技能管理/渠道会话 | skill-manager / channel-sessions 插件 | ROUTES_AREA 全页面 `/skill-manager`、`/channel-sessions` | 插件加载即注册 |

## 根因：状态栏 opt-in 设计

`apps/desktop/src/store/statusbar-prefs.ts`：

```ts
// Off by default — the bar is opt-in.
export const $statusbarVisible = persistentAtom(STATUSBAR_VISIBLE_STORAGE_KEY, false, Codecs.bool)

export const STATUSBAR_HIDDEN_BY_DEFAULT: readonly string[] = [
  'agents', 'approval-mode', 'context-usage', 'cron',
  'running-timer', 'session-timer', 'terminal', 'webhooks'
]
```

- 持久化 key：`hermes.desktop.statusbarVisible`（bool）、`hermes.desktop.statusbarHidden`（JSON 数组，空数组也是真值——用 json codec 而非 stringArray 防「全开后被复活默认」）。
- localStorage 位置（Electron userData）：`~/AppData/Roaming/Hermes/Local Storage/leveldb/`（leveldb 是 snappy 压缩，`grep -a` 只能抓到未压缩块，**抓不到 key 不能证明 key 不存在**；`LOG`/`LOG.old` 看 compaction/恢复记录）。
- 升级/重置丢 key → 回默认：状态栏整体隐藏 + 上述项目全隐藏 → 用户感知「面板全没了」。
- 设计意图（源码注释）：状态栏职责=「后端健康吗/我在哪/在干嘛」，路由快捷入口（cron/webhooks/agents）和每轮诊断读数（timer/context meter）默认藏起来保持安静；用户在右键菜单打开后偏好落盘。

## 恢复操作

1. 开状态栏：**Ctrl+Shift+S**（`view.toggleStatusbar`，`lib/keybinds/actions.ts` 默认 `mod+shift+s`；⌘K 命令中心搜 "Toggle Statusbar" 也可）。
2. 状态栏上**右键** → 勾选 Context Usage / Cron / Terminal 等。
3. 勾选后写回 localStorage，重启不再丢。

## 诊断入口速查

| 目的 | 路径/命令 |
|---|---|
| 插件加载失败 | `~/AppData/Local/hermes/logs/desktop.log` grep `runtime load|error-boundary|SyntaxError|ReferenceError` |
| 桌面构建版本 | `~/AppData/Local/hermes/desktop-build-stamp.json` → `builtAt` |
| 后端/代码更新记录 | `~/AppData/Local/hermes/logs/bootstrap-installer.log`（git update 时间线） |
| 桌面应用进程 | `tasklist | grep -i hermes`（多 Hermes.exe 是正常的，Electron 多进程） |
| 窗口/布局状态 | `~/AppData/Roaming/Hermes/window-state.json`、`desktop-installation.json` |

## CDP 陷阱

- **packaged build 不开 CDP**（`apps/desktop/electron/dev-cdp.ts`：打包构建永远关闭，无环境变量可覆盖）。
- 探测 9222 端口前先 `curl :9222/json/list` 看 title——如果列的是 `chrome://newtab`/Omnibox，那是**用户自己的 Chrome**，不是 Hermes 桌面，别继续当桌面应用连。
- 因此桌面应用实时 DOM 检查（inspecting-hermes-desktop-dom skill 的方法）对打包版不可用——靠 desktop.log 的 `[renderer console]` 前缀行拿渲染进程报错（主进程日志会转发渲染进程 console）。

## 案例：web-browser 插件加载失败（本次实测）

desktop.log 反复出现：

```
[plugins] runtime load failed (web-browser) SyntaxError: Invalid or unexpected token
[error-boundary:contrib:web-browser-plugin:pane] ReferenceError: onCopyBoth is not defined
```

两种报错形态的含义：
- `runtime load failed (<id>) SyntaxError: Invalid or unexpected token` → plugin.js 文件本身有语法错误（或 SDK 版本不兼容的旧语法）。
- `error-boundary:contrib:<id>-plugin:pane ReferenceError: X is not defined` → 渲染期引用了未定义标识符（漏 import / 旧代码残留变量），错误边界兜住不让整个应用崩，只挂该 pane。

**⚠️ 但「有错误日志」≠「当前有 bug」——二次深挖（同日下午）推翻了最初的「插件坏」结论**：

1. **时间线锚点证明错误是历史遗留**：desktop.log 无时间戳，但渲染错误 URL 带会话 ID 日期（`index.html#/20260709_141153_3dcbce` = 7-09、`20260804_184650` = 8-04），且 `[tls] trusting N Windows system CA certificate(s)` 的 N 在版本更新时变化（95→98）。web-browser 错误只出现在 4168-4442 行区间，之后 1900+ 行（8-05/8-06）零错误——文件 mtime 7-28 09:43 即修复点。
2. **当前文件全检通过**：`node --check` 语法 OK；import 的 `icons`/`KEYBINDS_AREA`/`atom` 全部存在于 sdk/index.ts（239/240/279 行）；keybind/titlebar/pane 注册格式与 `KeybindContribution`（lib/keybinds/actions.ts:170）、`TitlebarTool`（titlebar-controls.tsx:26）、`titleBar.tools.<side>`（contrib/panes.tsx:143）契约匹配；`webviewTag: true` 已启用（electron/session-windows.ts:44）。
3. **热加载验证**：touch 插件文件触发 fs-watch 重载，成功无日志、失败新增 `runtime load failed`——touch 后无新错误 = 加载正常。
4. **console.log 验证是无效手段**：`[renderer console]` 只转发 error 级别（desktop.log 里全是 Uncaught error/ReferenceError/Blocked call，无普通 log），加 console.log 测「插件是否执行」永远看不到输出，会误判。
5. **最终结论**：web-browser 插件当前无 bug，面板不显示是布局/禁用状态问题（`hermes.desktop.pluginDecisions.v2` localStorage 存插件启用决定，absence=用 defaultEnabled）。恢复：Settings → Plugins 确认启用 + Ctrl+Shift+B（插件自带 keybind）切换面板。

教训：看到 desktop.log 里插件的加载错误，先做时间线验证（错误区间 + 文件 mtime + 版本锚点）再决定是否修文件——不要见 error 就改代码。
