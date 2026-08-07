---
name: hermes-desktop-plugin-dev
description: "Hermes 桌面插件开发实战（本机验证的架构与坑）。触发词：桌面插件、desktop plugin。"
version: 1.0.0
tags: [hermes, desktop, plugin, development]
---

# Hermes 桌面插件开发实战

写 Hermes 桌面 App 插件（带 Python 后端的完整形态）的本机验证经验。官方 SDK 参考用 bundled skill `hermes-desktop-plugins`（不可编辑），本文档补充源码级实测结论与本机环境事实。

## 架构三件套（缺一不可）

| 组件 | 路径 | 说明 |
|---|---|---|
| 前端 | `~/AppData/Local/hermes/desktop-plugins/<id>/plugin.js` | 纯 ESM，写入即热加载（几秒内生效，出错有 toast），无需重启 |
| 后端 | `~/AppData/Local/hermes/plugins/<id>/dashboard/manifest.json` + `plugin_api.py` | FastAPI `router`，挂载在 `/api/plugins/<id>/`，业务逻辑放同目录 `<id>/service.py` |
| 注册 | `config.yaml` → `plugins.enabled` 列表 | 不加这个，后端永不挂载（web_server.py 的安全门禁，source=user 必须 enable） |

manifest.json 最小结构：`{"name": "<id>", "label": "...", "description": "...", "version": "1.0.0", "tab": {"hidden": true}, "api": "plugin_api.py"}`。

**⚠️ 最关键的坑：后端 API 是 `hermes_cli/web_server.py` 启动时 `_mount_plugin_api_routes()`（模块级，~17284 行）挂载的。热重载只覆盖前端 plugin.js；新插件/后端代码改动必须重启桌面应用（完全退出 Hermes.exe 重开）才生效。重启 gateway 没用——插件 API 不在 gateway 进程里。** 判断已挂载：`netstat -ano | grep LISTENING` 找 python 监听端口，逐个 curl `/api/plugins/<id>/<path>`，200 即挂载成功（本机桌面后端曾在 38766 端口）。

## 数据通道

- **前端调后端唯一正路：`ctx.rest(path, {method, body})`**（SDK 的 `pluginRest`，走 `/api/plugins/<id>/...`）。`host.request` 是 gateway JSON-RPC，**不是**插件 REST——别用。
- 模块级 `let apiRest = ...` 在 `register(ctx)` 里注入，组件用 `useQuery({queryFn: () => apiRest('/sessions')})`。
- 管理操作完成后 `queryClient.invalidateQueries({queryKey})` 刷新。
- 后端 Python 可以 `from hermes_constants import get_hermes_home` 定位 home；可以 `from hermes_state import SessionDB` 直接读写 state.db（管理操作复用 `set_session_title` / `set_session_archived` / `set_session_pinned` / `delete_session`，短事务 + SQLite WAL 并发安全）。
- 只读扫描 state.db 用 `sqlite3.connect("file:...?mode=ro", uri=True)`，排除子会话用 `WHERE parent_session_id IS NULL OR parent_session_id = ''`。

## 前端组件 API（源码实测，bundled skill 文档没写全）

- 文件不能用 JSX 语法（不编译），全部 `jsx('div', {children})` / `jsxs`。
- `SegmentedControl`：`options={[{id, label}]}` + `onChange`（**不是** items/onValueChange）。
- `SearchField`：`containerClassName` 控制宽度（**没有** className/clearable prop）。
- `DropdownMenuItem` 红色项：`variant: 'destructive'`（**不是** destructive prop）。
- `ConfirmDialog`：`open/onClose/onConfirm(async)/title/description/confirmLabel/destructive/dismissOnConfirm`。
- 对话框打开时用 `key={target?.id}` 强制重建组件（useState 初始值只读一次，避免渲染期 setState）。
- 打开历史会话：`host.navigate('/' + encodeURIComponent(sessionId))`（SESSION_ROUTE_PREFIX='/'）。
- 侧边栏导航：`ctx.register({area: SIDEBAR_NAV_AREA, data: {path, label, codicon}})`；全页面：`{area: ROUTES_AREA, data: {path}, render}`；命令面板：`{area: PALETTE_AREA, data: {id, title, keywords}, run}`。

## 前端模式补充（v1.2 迭代后）

- **UI 状态记忆（用户要求「记忆我选的」）**：`ctx.storage` 是同步 API。持久化全部 UI 状态：
  ```js
  const [filters, setFilters] = useState(() => ({ ...DEFAULT_FILTERS, ...apiStorage.get(KEY, {}) }))
  const save = patch => setFilters(prev => { const next = {...prev, ...patch}; apiStorage.set(KEY, next); return next })
  ```
  视图/筛选/搜索词全部记住，重开插件恢复。
- **失效筛选自动回退**：数据刷新（删除会话等）后，选中项可能已不存在——用 useMemo 校验 `options.some(o => o.key === f.x)`，不存在则回退默认值，避免筛选悬空。
- **多条件组合筛选模型**（用户纠正过「不能同时筛选平台和会话人了」）：筛选器对象 `{platform, person, status, type, query}`，五个维度独立可叠加（AND），每个维度内部单选（再点取消）。左栏分「平台/会话人/状态/类型」四个筛选区 + 搜索框；右栏标题显示当前组合（如「飞书 · 徐学环 · 已置顶」）带一键清除。不要用单选导航（一次只能选一个维度）。
- **会话对象键通用化**（主流平台适配）：`objectKey(s)` 对所有平台归一——本地会话='local'、群/频道='group:chat_id'、话题='topic:chat_id:thread_id'、私聊='person:user_id'。`objectLabel(s)`：群=群名（display_name）、话题=群名/平台话题、私聊=user_name 或 userFallback（数字 ID→「用户 后四位」、超长截断、ou_ 开头→飞书用户）。飞书群 display_name 是群名，其他平台群名也在 display_name。
- 每个筛选区独立计数：`buildFilterOptions(all)` 一次算好 {platforms, persons, groups, localCount, statuses, types}，UI 与校验都从它取。
- **平台标签映射表**（PLATFORM_LABELS）：收录 feishu/telegram/discord/slack/whatsapp/signal/matrix/mattermost/email/sms/cron + weixin/wechat/dingtalk/wecom/teams/instagram/messenger/line/viber/googlechat/irc/webhook/api。**新渠道接入零代码**——后端实时读 state.db，前端平台选项从数据动态推导，未收录 source 显示原始名，对象识别已通用化。唯一例外：真名反查目前只对飞书做了（contact.v3.user.get），其他平台显示 user_name 或 ID 短格式。

## 三栏布局 + 消息详情（v1.3，用户要求「直接在插件面板看到会话内容」）

- **布局演进**：v1 单栏 → v1.2 双栏（左筛选 + 右列表）→ v1.3 三栏（左筛选 w-64 | 中列表 w-[380px] | 右详情 flex-1）。4K 屏下三栏完全放得下；用户要「直接看内容不跳转」。
- **消息读取后端**：新增 `@router.get("/messages")`（session_id/profile/limit），复用 `SessionDB.get_messages(sid, limit)`（read_only），返回字段瘦身为 {id, role, content, timestamp, tool_name, tool_calls, active, compacted}。先 `resolve_session_id` 再 `resolve_resume_session_id`（压缩续体会把 id 投影到最新续体）。
- **分角色渲染**（MessageItem）：role=user →「我」+ accent 底色；assistant →「AI」；tool → 灰底小字「🔧 工具名 + 展开详情（N字）」；session_meta → 直接隐藏。压缩段标注「（此段已被压缩）」。
- **折叠展开模式**（useState 每消息独立）：
  - 工具消息**默认折叠**为一行（工具名 + 「展开详情（N字）」按钮），防刷屏；
  - 长消息（>600 字）默认显示前 600 字 + 「展开全文（共N字）」/「收起」；
  - 初始化 `useState(() => !isTool && !isLong)`。
- **选中行高亮 + 点击切换**：`selectedId` state，点击行 toggle；`selected = all.find(s => s.id === selectedId)` 从最新数据取（标题随刷新更新）。删除选中会话后同步清空 selectedId。
- **详情头部**：返回按钮（arrow-left）+ 标题 + 对象名/平台/消息数 + 「完整打开」（host.navigate 跳聊天页）+ 操作菜单（重命名/置顶/归档/删除复用）。
- 消息 30s refetch（`refetchInterval`）——新消息进来能看到；会话列表 15s。
- **左栏筛选分区可折叠**：FilterSection 标题行变 button（chevron-down/right），默认全展开；折叠时若区内有激活筛选，靠右栏标题的「清除筛选」兜底不迷路。

## 测试方法（不重启也能测）

1. **后端**：`venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'.'); import plugin_api; plugin_api.get_sessions(limit=5)"` —— 直接调 FastAPI 路由函数，模拟 Hermes 的 spec_from_file_location 加载方式。管理操作测完必须恢复原状并验证。
2. **前端**：`node --check plugin.js` 验证语法（write_file 的 lint 在 Windows 上报路径 bug `C:\c\Users\...`，不可靠，用 node --check）。
3. 飞书 open_id→真名反查：`lark-cli contact +get-user --user-id <ou_> --as bot`（Windows 下 `shutil.which("lark-cli.cmd")`），解析 `data.user.name`，结果落 JSON 缓存（7 天 TTL）避免 5 QPS 限流。「用户+N」格式是账号资料不完整，保持原名不误标。

## 桌面内置 UI 面板体系与「面板消失」排查（实测 2026-08）

用户报「上下文用量/定时任务/用量/代理面板都没了」时，先分清每个面板住哪、默认显示还是隐藏：

| 用户说的 | 实际位置 | 默认状态 |
|---|---|---|
| 上下文用量 | 状态栏 `context-usage` 芯片（`app/shell/context-usage-panel.tsx`，接线在 `use-statusbar-items.tsx`） | **隐藏** |
| 定时任务 | 状态栏 cron 快捷入口 + 侧边栏 Cron 区（`app/chat/sidebar/cron-jobs-section.tsx`，cronJobs>0 即渲染） | 状态栏入口隐藏，侧边栏区在 |
| 网关/代理状态 | 状态栏 gateway 芯片（`app/shell/gateway-menu-panel.tsx`） | 随状态栏 |
| 用量/余量 | 标题栏右上角 quota-panel 插件（TITLEBAR_AREAS.right） | 独立于状态栏，不受影响 |

- **根因（源码铁律）**：`apps/desktop/src/store/statusbar-prefs.ts` 里 `$statusbarVisible` 默认 `false`——状态栏是 opt-in 设计（VS Code workbench.statusBar.visible 同款）。且 `STATUSBAR_HIDDEN_BY_DEFAULT` 出厂隐藏：`['agents','approval-mode','context-usage','cron','running-timer','session-timer','terminal','webhooks']`。用户偏好存 localStorage（`hermes.desktop.statusbarVisible` / `hermes.desktop.statusbarHidden`），升级/重置丢 key → 回到全默认隐藏 → 用户觉得「面板没了」。
- **恢复路径**：Ctrl+Shift+S（`view.toggleStatusbar`，`lib/keybinds/actions.ts` 默认 `mod+shift+s`）或 ⌘K 搜 "Toggle Statusbar" → 状态栏出现；在状态栏上**右键**勾选要显示的项目。
- **诊断入口**：`~/AppData/Local/hermes/logs/desktop.log` grep `runtime load|error-boundary|SyntaxError|ReferenceError` 看插件加载失败；`~/AppData/Local/hermes/desktop-build-stamp.json` 的 `builtAt` 看桌面构建版本。**packaged build 不开 CDP**——9222 端口可能是用户自己开的 Chrome（`/json/list` 里 title 是 chrome://newtab 就是），别当桌面应用连。
- **插件加载失败两种报错形态**：`runtime load failed (<id>) SyntaxError: Invalid or unexpected token` = plugin.js 语法错误（或 SDK 不兼容的旧语法）；`error-boundary:contrib:<id>-plugin:pane ReferenceError: X is not defined` = 渲染期引用了未定义标识符（漏 import 或旧代码残留）。**但看到 error 日志先别急着修文件**——先按下面的方法论验证是不是历史遗留（web-browser 案例：错误看似真实，深挖后证明文件无 bug，是旧版本记录）。
- 详细清单、时间线验证法与 web-browser 案例全程：`references/desktop-ui-panels-statusbar.md`

### 插件「加载失败」深挖方法论（2026-08-06 实测，web-browser 案例）

desktop.log 有错误 ≠ 当前有 bug。判定顺序：

1. **时间线验证**（desktop.log 无时间戳，用三个锚点定位错误发生的时段）：
   - 渲染错误 URL 里的会话 ID 带日期：`index.html#/20260709_141153_3dcbce` = 7月9日的会话
   - `[tls] trusting N Windows system CA certificate(s)` 的 N 变化标志 Hermes 版本更新（实测 95→98）
   - 配合 `desktop-build-stamp.json` builtAt + `bootstrap-installer.log` 更新线
   - 错误只出现在一段区间、之后长区间无错 = 已修复的历史记录（文件 mtime 即修复点）
2. **确认当前文件语法**：`cd <插件目录> && node --check plugin.js`（⚠️ 绝对 Windows 路径传给 node 会变 `C:\c\Users\...` 报 MODULE_NOT_FOUND——必须 cd 到目录；write_file 的 lint 在 Windows 同样误报，不可信）
3. **SDK 兼容检查**（插件 vs SDK 谁坏）：import 的名字逐一核对 `apps/desktop/src/sdk/index.ts` 导出（icons/KEYBINDS_AREA/atom 在 239/240/279 行）；注册契约核对 `KeybindContribution`（lib/keybinds/actions.ts:170）、`TitlebarTool`（app/shell/titlebar-controls.tsx:26）、`TITLEBAR_AREAS`（sdk/index.ts:261）、`titleBar.tools.<side>`（contrib/panes.tsx:143）、`webviewTag`（electron/session-windows.ts:44）
4. **热加载验证**：touch/patch plugin.js 触发 fs-watch 重载（runtime-loader.ts 链路：readFileText → rewriteSpecifiers 正则替换 import specifier 为 shim blob → Blob+import() → register）。**成功无日志，失败新增 `runtime load failed`**——touch 后 grep 日志尾部即可判死活
5. **⚠️ console.log 不转发**：`[renderer console]` 只转发 error 级别，普通 console.log 不会出现在 desktop.log——用 console.log 验证插件执行是无效手段（实测踩坑：patch 加日志 → 日志无输出 → 误判「未执行」，实际是转发机制）
6. **重复注册安全**：registry `put()` 是覆盖语义（同 area 同 id 过滤后追加），togglePane 每次 ctx.register 同名 pane 不会堆积/冲突

## 参考

- `references/filter-model.md` — 多条件筛选模型（五维 AND）、失效回退、会话对象键跨平台归一、双栏 UI 组织、状态记忆、node 冒烟测试。任何列表类插件直接复用。
- `references/message-detail-pane.md` — 消息详情面板通用模式：/messages 后端路由（resolve_session_id + resolve_resume_session_id）、三栏布局、选中管理、分角色渲染、折叠展开。任何「列表+详情」类插件直接复用。
- 官方 SDK 接口参考：bundled `hermes-desktop-plugins` skill（不可编辑）。

## 参考实例

- 本机完整示例：`~/AppData/Local/hermes/plugins/channel-sessions/`（后端：读 state.db + 真名反查 + 管理操作 + /messages 消息读取）和 `~/AppData/Local/hermes/desktop-plugins/channel-sessions/plugin.js`（前端 v1.3：三栏布局 筛选|列表|详情 + 多条件组合筛选 + UI 状态记忆 + 消息分角色渲染与折叠展开 + 主流平台对象识别；`node -e` 提取纯函数做冒烟测试的样板）。
- 官方参照：`~/AppData/Local/hermes/plugins/skill-manager/`（完整 Python 后端结构）和 `~/AppData/Local/hermes/desktop-plugins/skill-manager/plugin.js`（成熟前端模式）。

## 用户偏好（本机）

- UI 中文、高密度、theme vars（`--ui-*`）不硬编码颜色。
- **宽屏双栏/三栏**：左栏导航/筛选 + 右栏列表（v1 单栏被嫌「排版不直观」）；数据管理工具进一步接受三栏（筛选|列表|详情）——用户要「直接看内容不跳转」，点列表行右侧同屏显示详情。
- **多条件组合筛选**：平台 × 会话人 × 状态 × 类型 × 搜索独立叠加（AND）——用户明确纠正过「不能同时筛选平台和会话人了」，单选导航被否。
- **UI 状态记忆**：视图/筛选/搜索持久化到 ctx.storage，重开恢复（用户原话「记忆我选的」）。
- **折叠展开**：工具调用/长消息默认折叠，点击展开——用户主动要求「折叠展开功能也要」。
- 功能分级实现（P0 核心 → P1 管理 → P2 增强），用户拍板核心后按评级做。
- 破坏性操作（删除）必须带确认流。
