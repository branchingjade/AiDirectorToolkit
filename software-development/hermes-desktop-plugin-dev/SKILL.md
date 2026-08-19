---
name: hermes-desktop-plugin-dev
description: "Hermes 桌面插件开发实战（本机验证的架构与坑）。触发词：桌面插件、desktop plugin、PluginContext、require fs、mux-token、dsh-inbox、render process、Electron sandbox。"
version: 1.1.0
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

**⚠️ 最关键的坑：后端 API 是 `hermes_cli/web_server.py` 启动时 `_mount_plugin_api_routes()`（模块级，~17284 行）挂载的。热重载只覆盖前端 plugin.js；新插件/后端代码改动必须重启桌面应用（完全退出 Hermes.exe 重开）才生效。重启 gateway 没用——插件 API 不在 gateway 进程里。** 判断已挂载：看 `~/AppData/Local/hermes/logs/agent.log` 里 `Mounted plugin API routes: /api/plugins/<id>/` 行；**不要用裸 curl 探测 404**——见下方「API 404 = 鉴权门，不是故障」。

### ⚠️ API 404 = 鉴权门，不是故障（2026-08-09 实测）

`web_server.py` 的 `_plugin_api_runtime_gate`（~569 行）对未鉴权请求**故意返回 404**（防插件名枚举 oracle，注释明说 "an unauthenticated caller could fingerprint which plugins are installed/enabled by reading the status code"）。因此：

- 裸 `curl http://127.0.0.1:<port>/api/plugins/<id>/sessions` 返回 404 **不代表插件坏了**——它可能挂载正常只是你没带 token。
- 带鉴权重测：`X-Hermes-Session-Token: <token>` 或 `Authorization: Bearer <token>`。token 是 gateway 启动时从 `HERMES_DASHBOARD_SESSION_TOKEN` 环境变量取的（`_SESSION_TOKEN`，每次启动随机，死在进程里），auth_required=true 时不注入 SPA HTML（`window.__HERMES_SESSION_TOKEN__` 只在未开鉴权时注入）。
- **可靠验证路径 = 跳过 HTTP 直接测业务**：`python -c "import sys; sys.path.insert(0,'<dashboard>'); from channel_sessions.service import list_sessions; list_sessions(limit=5)"` 真库真调用，测的是业务逻辑本身。HTTP 层只负责鉴权/路由，业务验证不需要它。
- 结论：**404 先查鉴权，再查挂载日志（agent.log 的 Mounted 行），最后才怀疑代码**。

### ⚠️ 插件 Tailwind 类必须存在于 Hermes 编译 CSS（2026-08-09 根因级教训）

**Hermes 桌面 app 的 CSS 是 Tailwind v4 从 app 自身源码编译的；插件目录在构建图之外——插件 JS 里写的 className，只要 app 源码没用过，就没有对应 CSS，UI 静默破损（不报错）。** 本会话实锤：

- `--ui-fill-tertiary` / `--ui-fill-secondary` **变量不存在**（app 用 `--ui-bg-*` 系列）→ 消息气泡/头像/hover 背景全透明 =「看不到会话内容」的视觉根因；
- `text-[10.5px]` / `[12.5px]` / `[13px]`、`w-[380px]`、`max-w-24`、`min-h-[30px]`、`space-y-3.5`、`bg-x/50` `/60` 变体（app 只编译过 `/40`）全部缺失；
- Codicon 图标名则相反：`codicon-<name>` 是字体类（codicon.css），**任何名字都能用**（如 `tag-add`/`checklist` 存在，`check-circle-filled` 不存在——照码有图标名的黑名单）。

**纪律（写任何插件 className 后必做）**：对照 dist CSS 精确审计，脚本 `scripts/audit-tailwind-classes.py`（Tailwind 转义精确匹配：`[`→`\[`、`.`→`\.`、`(`→`\(`、`/`→`\/`，变体只取冒号后主体）。审计脚本放插件 tests/ 下并在 CI/selfcheck 里跑，防止回归。Hermes 内置可用变量速查（编译产物验证过）：`--ui-bg-tertiary`（hover/底）/`--ui-bg-secondary`、`--ui-text-primary/secondary/tertiary/quaternary`、`--ui-stroke-secondary`、`--ui-accent`、`--ui-control-active-background`、`--ui-red`、`text-destructive`（tailwind 语义色）。

### ⚠️ 块注释 `*/` 提前闭合 = 整文件语法崩（2026-08-09 实测）

版本注释里写 `--ui-fill-*/字号`（含 `*/`）会**提前终止 `/* */` 块注释**，后面的代码全部变成裸语法 → 整个插件加载失败。desktop.log 报 `SyntaxError` 但错误行号定位到注释行附近（stack 行号不可靠）。**检查法**：`grep -n '\*/' plugin.js` 应该只出现注释结尾处；版本注释里禁用 `*/` 组合（写成「--ui-fill 系」）。

### 前端语法验证（Windows 实测可靠路径）

`node --check` **只查语法不解析模块**——不用替换 import，直接 `cp plugin.js "$TEMP/chk.mjs" && node --check "$TEMP/chk.mjs"`（MSYS `/tmp` 会被 node 解析成 `C:\tmp` 报 MODULE_NOT_FOUND，用 Windows 临时目录）。**不要用 vm.Script + 手动替换 import**（stub 插错位置产生假语法错，本会话白绕一圈）。

## 数据通道

- **前端调后端唯一正路：`ctx.rest(path, {method, body})`**（SDK 的 `pluginRest`，走 `/api/plugins/<id>/...`）。`host.request` 是 gateway JSON-RPC，**不是**插件 REST——别用。
- 模块级 `let apiRest = ...` 在 `register(ctx)` 里注入，组件用 `useQuery({queryFn: () => apiRest('/sessions')})`。
- 管理操作完成后 `queryClient.invalidateQueries({queryKey})` 刷新。
- 后端 Python 可以 `from hermes_constants import get_hermes_home` 定位 home；可以 `from hermes_state import SessionDB` 直接读写 state.db（管理操作复用 `set_session_title` / `set_session_archived` / `set_session_pinned` / `delete_session`，短事务 + SQLite WAL 并发安全）。
- 只读扫描 state.db 用 `sqlite3.connect("file:...?mode=ro", uri=True)`，排除子会话用 `WHERE parent_session_id IS NULL OR parent_session_id = ''`。

## 前端组件 API（源码实测，bundled skill 文档没写全）

- **⚠️ 必须用 ESM import 获取 React，不能用全局 `React`**（2026-08-17 实测 `ReferenceError: React is not defined`）。正确写法：
  ```js
  import { jsx, jsxs, Fragment } from 'react/jsx-runtime'
  import { useState, useEffect, useCallback } from 'react'
  import { Badge, Button, ... } from '@hermes/plugin-sdk'
  ```
  错误写法（会崩溃）：`const { useState } = React` 或直接用 `React.jsx(...)`。
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
- **对象显示名覆盖（displayOverrides，v1.4.3）**：用户「重命名显示名」= 只改列表显示、不动原始数据。`ctx.storage` 存 `{objectKey: 自定义名}`，`objectLabel(s, t, overrides)` 先查覆盖名再回落原逻辑，`buildFilterOptions` 同步接收 overrides 生成选项标签（筛选列表也显示自定义名）；清空输入 = 删 key 恢复默认。空值恢复默认是用户可感知的安全网，对话框初始值 = `overrides[key] || 原始label`。
- **列表行操作按钮必须常显**（2026-08-09 用户反馈「重命名也没有」「删除时直接删会话」根因）：对象行的 ✏️/🗑 用 `opacity-0 group-hover:opacity-100` 隐藏后用户根本发现不了，误以为功能缺失、误操作别的入口。**管理类操作（重命名/删除分类）一律常显**；危险批量删除（按对象删全部会话）用户明确否决「不删会话」，对象行不做破坏性批量操作，删除只保留单会话级（带确认流）。分类删除 = 纯前端从 sessionCats 映射移除，会话数据一条不动。
- **批量赋分类（v1.4.3）**：列表头部「选择」按钮切换 selectMode → 每行 checkbox（`Codicon check/circle-outline`）→ 底部批量条出现「批量分类」下拉（DropdownMenu 列分类，onSelect 批量写 sessionCats）→ 完成 notify + 清空选择。多选 state 独立于 selectedId（选中查看）不冲突。
- **批量 mutation（v1.5.0）**：批量置顶/归档 = `selectIds.map(sid => apiRest('/pin'|'/archive', {method:'POST', body:{session_id, profile, pinned|archived}}))` + `Promise.allSettled` 后统一 `invalidateQueries` + notify + 清空选择。批量条按钮 `disabled: !selectIds.length`。
- **全文搜索模式（v1.5.0，对标 Pi Session Manager 的标配）**：
  - 后端：`GET /search?q=&limit=` → `search_messages()` 扫**全部 profile** 的 messages 表 `content LIKE %q%`（`ORDER BY id DESC` 最新优先），**按 session_id 去重**（同会话多命中只留最新一条），附会话上下文（title/source/user_id/display_name/chat_type 子查询）。空查询返回零命中不抛错。SQLite LIKE 对中文是子串匹配（无分词问题），万级消息量够用；百万级才需要 FTS5。
  - 前端：`useQuery({queryKey:[ID,'search',searchQ], enabled: searchQ.length>=2, staleTime:15000})`——queryKey 带搜索词天然防抖（输入变化才重新请求），无需手动 debounce。列表头部渲染「消息内容命中 N 条」徽标（`search.hits` 函数插值），点击 `setSelectedId(first.session_id)` 跳转首个命中会话。
  - **搜索框语义扩展**：原 matchesAll 的 query 只搜标题/ID/人名，全文搜索补上消息内容维度——搜索框同时覆盖三类。
- **右键上下文菜单（v1.5.0）**：行 div 加 `onContextMenu: e => {e.preventDefault(); setCtxPos({x:e.clientX,y:e.clientY}); setCtxOpen(true)}` + 受控 `DropdownMenu open={ctxOpen} onOpenChange` + `DropdownMenuContent style={{position:'fixed', left:ctxPos.x, top:ctxPos.y, zIndex:9999}}` + `sr-only` 的 DropdownMenuTrigger（隐藏锚点）。复制用 `navigator.clipboard.writeText` + notify。⚠️ 选择模式下禁右键（`if (selectMode) return`）。
- **排序切换（v1.5.0）**：`sortMode` state 持久化 ctx.storage（'last'|'created'|'title'）；标题排序用 `localeCompare(other, 'zh-Hans-CN')` 中文感知；头部 DropdownMenu 三项带 `check` 勾选态，onSelect 同时 setState + `apiStorage.set`。
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

## Windows subprocess 四坑 + 服务检测三路直查（ops-panel 实测 2026-08-09）

插件后端（plugin_api.py / service.py）用 subprocess 查系统状态、跑 git 的四个坑：

1. **PowerShell 检测命令自匹配**：`Where-Object { $_.CommandLine -like '*marker*' }` 会把 powershell.exe 自己算进去（`-Command` 参数里含 marker 字符串）→ 误报目标进程存在。**必须限定进程类型**：`$_.Name -match 'python' -and $_.CommandLine -like '*marker*'`。
2. **PS 表达式里 `and` 不合法**：脚本块表达式必须用 `-and`（`and` 是语句级关键字），否则报"位置 行:1 字符: N"语法错。`$_.Name -eq 'X' and $_.Y -like 'Z'` 错，`-and` 对。
3. **subprocess 编码**：Windows 中文系统 `text=True` 默认按 GBK 解码子进程输出。**git 输出是 UTF-8**（diff 含中文注释），GBK 解码出乱码/替换符 → 写回 diff 文件即损坏 → `git apply --check` 必失败。git 调用必须 `subprocess.run(..., encoding='utf-8')`；powershell 保持默认 GBK。
4. **write_text 的 CRLF 坑**：Python 写文本默认 `newline=None`，Windows 上把 `\n` 转成 `\r\n`。**写 git diff 文件必须 `write_text(content, encoding='utf-8', newline='\n')`**——CRLF 的 diff 文件 `git apply --check` 失败（本会话双坑叠加：GBK 乱码 + CRLF，正本 diff 连续坏两次）。

**服务状态检测三路直查（不调 hermes CLI）**：端口（`netstat -ano` 找 LISTENING + PID）· 进程（CIM 按 CommandLine 匹配，限定 python）· 计划任务（`Get-ScheduledTask` State: Ready/Running/Disabled）。**不要用 `hermes gateway status` 等 CLI 查状态**——可能触发中断 update 的恢复流程连带停 gateway。

**⚠️ 批量状态查询两坑（2026-08-10 ops-panel 实测）**：
1. **`Get-ScheduledTask | ConvertTo-Json` 的 State 是枚举数字**（TaskState: 0=Unknown, 1=Disabled, 2=Queued, 3=Ready, 4=Running），不是字符串 `"Ready"`——字符串比较全不匹配导致 alive 判定全错。Python 侧映射 `{"1":"Disabled","3":"Ready","4":"Running"}`。
2. **串行逐服务查 = 性能灾难**：六服务 × 每个 2-3 个 powershell/netstat 子进程（冷启动 1-2s）≈ 11s。合并为 3 次批量调用（一次 `netstat -ano` 解析全部端口、一次 `Get-CimInstance` 取全部 python 进程 + `ConvertTo-Json -Compress` 输出防分隔坑、一次 `Get-ScheduledTask -TaskName 'a','b'` 查全部任务）+ TTL 缓存（3s）→ 首次 2.6s、缓存命中 13ms。**写操作后 `_invalidate_services_cache()` + `get_services_status(force=True)`**（防操作后读到旧缓存）。

**一键更新编排顺序（Windows，ops-panel 模式）**：① 禁用 watchdog（防更新期间拉起 gateway 锁 venv）→ ② 停远程 serve/守卫/gateway（计划任务 Stop + taskkill 兜底）→ ③ 关桌面 app（检测 Hermes.exe 主进程，排除 `--type=` 子进程；守护进程可倒计时自动杀）→ ④ 执行 update → ⑤ 补丁自检恢复（git apply --check --reverse 正本 diff）→ ⑥ 恢复服务。runner 用 `DETACHED_PROCESS | CREATE_NO_WINDOW` 启动独立 python 进程（app 关闭后接管），状态机用标记 JSON 文件驱动（`state/ops-panel-update.json`）+ 日志文件（`state/ops-panel-update.log`），面板轮询展示。

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
- **⚠️ 第三种形态（completion-sound 错误，2026-08-09 两轮实测修正）**：`runtime load failed (<id>) SyntaxError: Unexpected token ']'` 或 `ReferenceError: moduleT is not defined` 且**错误文件路径是 `app.asar/dist/assets/completion-sound-*.js`**（app 自己的音频资源，不是插件文件）。分两种结局：
  - **历史遗留/写入竞态**：touch 热加载无新增错误 + **重启后不再报** = 忽略旧记录。
  - **⚠️ 持续失败（本轮新增）**：touch 无新增错误**但重启冷加载仍报**（desktop.log 行号持续增长、多个页面插件同错、包括从未动过的插件如 web-browser）→ **不是插件代码问题，是桌面端产物/运行时加载链缺陷**（本机案例：12:05 桌面端自动重建后出现，quota-panel/skill-manager 不报而页面插件全报）。**touch 热加载通过 ≠ 冷加载正常**（热加载有缓存掩盖），别据此判健康。
  - **深挖链**（全验证过）：① `node --check plugin.js` 排除插件语法 → ② **asar 内容验证**：`npx @electron/asar listPackage <asar>` 能列出 + node API `extractFile(p, path)` 提取 chunk（⚠️ CLI `extract-file` 对 Windows 路径报 "not found"——用 node API 且路径去前导反斜杠；在 `"type":"module"` 包里验证脚本要 `.cjs`）→ ③ `node --check` 提取出的 chunk（本机 completion-sound 144KB 语法正常）→ ④ 依赖链完整性：正则 `from"\./([^"]+)"` 提取兄弟 chunk 逐一 extractFile（本机 30+ chunk 全完整）→ ⑤ 全正常则判定桌面端产物缺陷，修复 = 重建桌面端（`cd apps/desktop && npm run build && npm run builder -- --dir`，builder 需关 app 防 asar 文件锁）。
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

- `scripts/verify-asar-chunk.cjs` — **app.asar chunk 完整性验证**（提取 + node --check + 依赖链检查）。completion-sound 类错误深挖用：`node verify-asar-chunk.cjs <app.asar> <chunk名>`（⚠️ CLI `extract-file` 对 Windows 路径报 not found，用此 node API 版；路径去前导反斜杠）。
- `scripts/audit-tailwind-classes.py` — **插件 className 存在性审计**（对照 Hermes 编译 CSS，Tailwind 转义精确匹配）。任何插件写完后必跑，防止 UI 静默破损回归。用法：`python audit-tailwind-classes.py plugin.js [dist-css-dir]`。
- `references/filter-model.md` — 多条件筛选模型（五维 AND）、失效回退、会话对象键跨平台归一、双栏 UI 组织、状态记忆、node 冒烟测试。任何列表类插件直接复用。
- `references/message-detail-pane.md` — 消息详情面板通用模式：/messages 后端路由（resolve_session_id + resolve_resume_session_id）、三栏布局、选中管理、分角色渲染、折叠展开。任何「列表+详情」类插件直接复用。
- 官方 SDK 接口参考：bundled `hermes-desktop-plugins` skill（不可编辑）。

## 参考实例

- 本机完整示例：`~/AppData/Local/hermes/plugins/channel-sessions/`（后端：读 state.db + 真名反查 + 管理操作 + /messages 消息读取）和 `~/AppData/Local/hermes/desktop-plugins/channel-sessions/plugin.js`（前端 v1.3：三栏布局 筛选|列表|详情 + 多条件组合筛选 + UI 状态记忆 + 消息分角色渲染与折叠展开 + 主流平台对象识别；`node -e` 提取纯函数做冒烟测试的样板）。
- 官方参照：`~/AppData/Local/hermes/plugins/skill-manager/`（完整 Python 后端结构）和 `~/AppData/Local/hermes/desktop-plugins/skill-manager/plugin.js`（成熟前端模式）。

## Runtime 插件 reload 不对称（2026-08-19 实测教训，必看）

`controller.tsx` 启动时只调 `discoverBundledPlugins()`（扫 `apps/desktop/src/plugins/` 内置插件）——**`desktop-plugins/<name>/plugin.js` 里的 runtime 插件不会自动被发现**。新写完一个 runtime 插件后**必须** ⌘K → "Reload desktop plugins" 触发 `discoverRuntimePlugins()`，否则：

- **desktop.log 里看到新插件 0 行日志**（因为根本没尝试加载）
- 用户看不到任何 toast/图标/错误提示
- 排查会走到死路：plugin.js 语法对、node --check 通过、cwd 对、mux-token 对、握手也能复现，但**就是没出现在 app 里**——因为 app 没扫这个文件

**症状 → 病因 → 修复表**：

| 症状 | 病因 | 修复 |
|---|---|---|
| 写完 plugin.js 重启 app，titleBar 仍无图标 | `discoverBundledPlugins()` 没扫 `desktop-plugins/` | ⌘K → "Reload desktop plugins" |
| desktop.log 完全没出现新 plugin 的 log | 同上 | 同上 |
| reload 后立即出现 log 但仍报错 | 真 bug | 查 host/ctx 用法 |
| reload 后图标出现但**点不动/状态不对** | 状态同步问题 | `useValue` 在最里层组件订阅 |

**热加载（已加载后改文件）vs 冷加载（首次 reload）的陷阱**：
- **热加载有缓存掩盖**——改 plugin.js 后 5s 内自动 reload（runtime-loader.ts: readFileText → rewriteSpecifiers → Blob+import()），但**它只覆盖前端 plugin.js**；新增插件**必须**显式 reload
- **冷加载（首次 reload）才暴露真问题**——completion-sound 错误（dsh-integration-pattern.md 里有）只出现在冷加载路径，热加载路径看不见
- **判断"插件是否健康"必须** reload 一次（不仅靠热加载通过）

**为什么 bundled skill 没说**：`hermes-desktop-plugins` SKILL.md 写 "the app watches that directory: the plugin loads within a few seconds"——**这句话对内置插件（bundled）成立，对 runtime 插件不成立**。bundled 在 `apps/desktop/src/plugins/` 里，启动时和 HMR 一起被 `discoverBundledPlugins` 处理；runtime 在 `desktop-plugins/`，启动时被忽略，只在 reload 路径被扫。

## 用户偏好（本机）

- UI 中文、高密度、theme vars（`--ui-*`）不硬编码颜色。
- **插件名用中文**（2026-08-09 拍板）：manifest.json 的 `label` + 侧边栏导航 + 面板标题 + 命令面板全中文（先例：channel-sessions label「渠道会话管理」、ops-panel label「运维面板」）；**id 必须英文 kebab-case**（SDK 硬限制，目录/API 路径用）——中文项目/插件用拼音或英文 id + 中文显示名（同飞书看板 slug 规则）。
- **宽屏双栏/三栏**：左栏导航/筛选 + 右栏列表（v1 单栏被嫌「排版不直观」）；数据管理工具进一步接受三栏（筛选|列表|详情）——用户要「直接看内容不跳转」，点列表行右侧同屏显示详情。
- **多条件组合筛选**：平台 × 会话人 × 状态 × 类型 × 搜索独立叠加（AND）——用户明确纠正过「不能同时筛选平台和会话人了」，单选导航被否。
- **UI 状态记忆**：视图/筛选/搜索持久化到 ctx.storage，重开恢复（用户原话「记忆我选的」）。
- **折叠展开**：工具调用/长消息默认折叠，点击展开——用户主动要求「折叠展开功能也要」。
- 功能分级实现（P0 核心 → P1 管理 → P2 增强），用户拍板核心后按评级做。
- 破坏性操作（删除）必须带确认流。
