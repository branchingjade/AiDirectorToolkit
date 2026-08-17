---
name: hermes-session-management
description: "渠道会话的会话人/数据层/管理插件。触发词：会话人、渠道会话、会话管理、display_name、会话列表。"
version: 1.0.0
---

# Hermes 渠道会话数据层与管理

Hermes 渠道会话（飞书/Telegram/群聊/DM/话题）的展示、数据存储、查询与管理。做会话管理插件、查会话人、诊断 display_name 异常、构建会话列表 UI 时使用。

## 会话人显示三层事实（核心认知）

「Hermes 能不能显示会话人」取决于问哪一层：

| 层 | 能力 | 说明 |
|---|---|---|
| Agent 上下文 | ✅ 知道 | 私聊注入 `**User:** <真名>`（gateway/session.py:583-586）；群聊注入 `**Session type:** Multi-user session` + 每条用户消息前缀 `[sender name]`（session.py:577） |
| state.db | ⚠️ 半知道 | sessions 表存 user_id（open_id）+ display_name；群=群名，私聊=chat_id |
| 桌面 UI | ❌ 不显示 | 侧边栏行只显示 title/preview（sessionTitle()），聊天区不标发送人 |

结论：agent 内部一直知道谁在说话；用户界面看不到。用户问「会话人」先确认问的是哪一层。

## 会话「丢失/看不到」排查法（2026-08-07 两次实测）

用户报「之前的会话看不到了 / 消息全丢了 / 会话被替换成新会话」时，**数据层几乎总是完好的**——根因在桌面 app 显示层（会话列表读取失败/前端未刷新），不是数据库丢数据。

排查步骤（按顺序）：
1. **先查 state.db 确认数据完好**（不要信 UI，不要凭印象说"丢了"）：
   ```sql
   -- sessions 表列名：started_at / last_activity_at / message_count / end_reason / title（无 created_at 列！）
   SELECT id, started_at, title, message_count, last_activity_at FROM sessions WHERE id='<session_id>';
   -- messages 表列名：timestamp（无 created_at 列！）
   SELECT id, role, content, timestamp FROM messages WHERE session_id='<session_id>' ORDER BY id DESC LIMIT 10;
   ```
   ⚠️ 两个表都没有 `created_at` 列——查时间戳用 `started_at`（sessions）/`timestamp`（messages），写错列名直接 OperationalError。
2. **关键判据：当前对话是否仍在往原 session 写**。若用户说"新会话"，查原 session 的 messages 最新几条——如果当前这轮对话（含"真的丢了"和 agent 回复）就在原 session 里，说明**会话根本没被替换，是 app 把它显示成了新会话**（session 连续无断档 = 显示层问题实锤）。
3. **用 session_search 验证**：按用户记得的标题/关键词搜（如「记忆与画像机制推敲」），返回的 session 链接可直接点回。
4. **显示层问题结论**：数据完好 + 日志无崩溃 → 给用户 session 链接，说明是 app 显示问题，数据一条没丢。

**案例 5（2026-08-14 续接会话被列表 API 隐藏——别只当显示层）**：bot 主动私信/日常续接（同一 session_key 的新会话带 `parent_session_id`，parent end_reason=daily/session_reset/idle）**数据在 state.db 但 list_sessions_rich 不返回**——`_LISTABLE_CHILD_SQL` 只放行 root 与 branch（`_branched_from` 标记/`branched` end_reason），投影只对 `end_reason='compression'` 链生效，续接 tip 永不冒头。诊断特征：SQL 直查能看到新会话（30 条消息），`list_sessions_rich(session_key=...)` 却只返回旧 root。修复=本地补丁 hermes_state.py 投影边扩展（「parent 已结束 + 同 session_key」），已登记补丁正本。**⚠️ 改 hermes_state.py 等核心库后必须重启 gateway（8644）+ HermesDashboard（9120）双进程**——桌面 app 侧边栏列表数据源是 9120 不是 8644（只重启 gateway 不生效，实测）；重启用 `powershell Stop-Process -Force`（taskkill 报 Access denied）+ `schtasks /Run`；9120 API 验证链路：`POST /auth/password-login`（basic hermes/Huan1120）拿 cookie → `GET /api/profiles/sessions`。

实测案例（2026-08-07）：用户问「记忆的tag打了吗」→ 会话中断 → 用户重开 app 看到"新会话"说"真的丢了"。查 state.db 发现原 session（记忆与画像机制推敲）122 条消息全在，从 10:50 到 11:02 连续无断档，当前对话还在往同一 session 写。数据层 0 丢失，纯显示层。

## 续接会话在列表 API 不可见（2026-08-14 实测：bot 主动私信场景）

用户报「bot 主动给成员发消息，会话列表查不到」——**数据在 state.db（SQL 直查在），但 `list_sessions_rich`（侧边栏/列表数据源）不返回**。根因链：

1. bot 主动私信 → gateway 在同一 DM（session_key=`agent:main:feishu:dm:oc_xxx`，⚠️ 带 `agent:main:` 前缀）下创建**新会话**，带 `parent_session_id` 指向同 DM 旧会话（续接/恢复机制）
2. `_LISTABLE_CHILD_SQL`（hermes_state_common.py:103）= `(parent_session_id IS NULL OR branch标记)`——续接会话不是 branch（无 `_branched_from`、parent end_reason≠'branched'）→ **被当子会话隐藏**
3. root 投影到最新延续只对 **compression 链**生效（`_COMPRESSION_CHILD_SQL`：parent end_reason='compression'）——续接链是 `daily→session_reset→None` 不满足 → root 不投影，侧边栏显示旧 root（旧标题/旧消息数/旧时间），新会话永远不冒头

排查判据：被隐藏会话特征 = `parent_session_id` 非空 且 parent 的 `end_reason` 非 compression/branched。SQL 直查 + `list_sessions_rich` 对比即可实锤。API 参数坑：`list_sessions_rich` **无 `order` 参数**（排序用 `order_by_last_active=True`，传 `order=` 直接 TypeError）；SessionDB 构造要 `Path` 对象非 str。

**修复已实施（2026-08-14 用户拍板方案 A=投影扩展，合并进成员历史会话按上下文连续显示）**，改动 `hermes_state.py` 三处：
1. `get_compression_tip(session_id, continuation_edges_only=False)` 加参数——`continuation_edges_only=True` 时边条件扩展为 `parent.end_reason='compression' OR (parent.end_reason IS NOT NULL AND child.session_key=parent.session_key)`；默认窄边不动（归档/删除/ancestry 语义不变）。⚠️ SQL 里布尔参数必须绑定传参（`(current, continuation_edges_only)`），不能写进 f-string（`sqlite3.OperationalError: no such column`）
2. `list_sessions_rich` 投影 CTE（~7317 行）边条件同样扩展为宽边——否则 `effective_last_active` 排序不认续接链
3. 投影触发从 `end_reason=='compression'` 改为「parent_session_id IS NULL 的 root 都查宽边 tip」（branch 行 parent 非空，跳过防重复投影）

验证（独立进程，真实 state.db）：杨璇 DM 投影为「激励杨璇」30 条 + `_lineage_root_id` 指向旧 root；subagent 泄漏 0；include_children=True 不投影；500 条列表 0.27s。

**⚠️ 生效铁律（用户实测「FEISHU 里没看到」踩坑）**：桌面 app 侧边栏列表由 **HermesDashboard（9120）** 提供，不是 gateway（8644）——只重启 gateway 侧边栏不生效，必须**双进程都重启**（8644 管渠道/cron，9120 管桌面 UI 数据）。重启姿势：`powershell Stop-Process -Force`（`taskkill /F` 报 Access denied，旧 gateway 权限高于普通终端），再 `schtasks /Run /TN Hermes_Gateway` / `HermesDashboard`。真实链路验证：`POST http://127.0.0.1:9120/auth/password-login` body `{"provider":"basic","username":"hermes","password":"Huan1120"}` 拿 cookie（⚠️ basic auth 头不认，cookie 才认；/login POST 是 405）→ `GET /api/profiles/sessions` 应见投影后的 tip。改动已登记补丁正本（Obsidian Vault/_hermes/补丁管理/，22 段，`hermes update` 后 `reapply-patches.py --apply` 恢复）。完整复现配方见 references/invisible-continuation-sessions.md

## 关键坑

1. **私聊 display_name 落 chat_id 的根因**：gateway/session.py:1821 `display_name=source.chat_name`——P2P 会话的 chat_info.name 为空 → 回退 chat_id。即使 feishu adapter 已解析出真名（_resolve_sender_profile → user_name），也不写入 display_name。这是结构性的（不是权限问题）。
2. **REST 列表不含会话人字段**：list_sessions_rich 只返回 id/source/model/title/started_at/ended_at/message_count/preview/last_active/pinned/archived/profile——**没有 user_id/display_name/chat_id/session_key**（hermes_state.py:5547+ docstring）。纯前端拿不到会话人。
3. **历史会话不回填**：display_name 只有新消息触发解析时更新；权限开通前建的旧会话永久停留在 chat_id/群名。
4. **权限验证链**：`lark-cli contact +get-user --user-id ou_xxx --as bot` 返回非空 `name` 字段 = bot 权限已生效（contact:user.base:readonly）。返回「用户+N」= 该账号资料未设姓名，不是权限问题。
5. **评论会话不在任何会话列表 API 中**（2026-08-10 实测）：飞书文档评论会话走独立 AIAgent + JSON 文件（`Obsidian Vault/_hermes/评论会话/`，含 archive/），**不写 state.db**——`list_sessions_rich` / `GET /api/profiles/sessions` / 侧边栏「FEISHU」分类一律看不到。用户问「某会话客户端看不到」先查它是不是评论会话：评论会话查 Obsidian 目录，聊天会话才查 state.db。做「全部会话」类 UI/查询时，评论会话是独立数据源，需插件后端另读 JSON 目录——**channel-sessions 已实现**（2026-08-10「飞书评论」Tab，见下节 + references/comment-sessions-view.md）。

## 数据端点

| 端点 | 用途 | 参数要点 |
|---|---|---|
| GET /api/profiles/sessions | 跨 profile 会话列表 | limit(≤500)/offset/archived(exclude\|only\|include)/order(recent\|created)/source/exclude_sources |
| GET /api/profiles/sessions/sidebar | 批量三切片 | recentsLimit/cronLimit/messagingLimit + 各 exclude |
| PATCH /api/sessions/{id} | rename / archive / pin | 桌面端封装 setSessionArchived/setSessionPinnedRemote/renameSession |
| DELETE /api/sessions/{id} | 删除 | 支持 bulk_delete_sessions |
| GET /api/sessions/search | 搜索 | q 参数 |

代码位置：hermes_cli/web_routers/profiles.py（profiles 聚合）、hermes_cli/web_routers/sessions.py（管理操作）、hermes_state.py list_sessions_rich（字段投影）。

## 桌面插件接入（做会话管理 UI）

- 形态：ROUTES_AREA 全页面 + SIDEBAR_NAV_AREA 侧边栏导航 + PALETTE_AREA 命令（`host.navigate('/xxx')`）；管理密集操作用全页面而非 pane。
- 打开历史会话：`host.navigate(sessionRoute(id))`（apps/desktop/src/app/routes.ts:184）。
- **现成模板**：`~/AppData/Local/hermes/desktop-plugins/skill-manager/plugin.js`（全页面管理插件的实际范式：useQuery 数据 + mutation 操作 + 确认流）。
- **本插件（channel-sessions）已开源发布**：GitHub branchingjade/channel-sessions（MIT），当前 **v1.5.0**（2026-08-09，含全文搜索/右键菜单/批量置顶归档/排序 + 语言切换/自定义分类/收藏/导出/UI 破损修复）。仓库结构镜像 Hermes 目录约定（desktop-plugins/ + plugins/ 两个子目录），正本在 `~/Documents/Hermes/Projects/channel-sessions/`（独立 git 仓库，主工作区 gitignore）。**v1.5.0 功能扩展**（用户「重点功能型，全线优化」）：全文搜索（后端 `GET /search?q=` 扫 messages.content LIKE、按 session_id 去重、附会话上下文；前端 queryKey 带搜索词天然防抖、enabled≥2字符、列表头「消息命中 N 条」徽标点击跳首个命中）、右键上下文菜单（onContextMenu 定位 + 受控 DropdownMenu + fixed 定位）、批量置顶/归档（Promise.allSettled 批量 mutation，不删会话）、排序切换（last/created/title，`localeCompare(…,'zh-Hans-CN')` 中文感知，持久化）。详细模式见 hermes-desktop-plugin-dev skill。关键实现细节：
  - **i18n 必须用函数插值器**：Hermes 插件 SDK 的 `ctx.i18n`/`usePluginI18n` 的 `render()` 只支持字符串字面量或 `(...args) => string` 函数——`'{n}条'` 占位符不会替换，带参数文案必须写成 `n => \`${n}条\``。
  - **消息分页**：`GET /messages` 支持 `limit`+`offset`（插入序），返回 `has_more`（多查一条探测）。前端 React Query v5，queryKey 带 offset + `refetchInterval` 仅 offset=0 时开启 + 累积数组去重合并。
  - **后端读库模式**：`sqlite3.connect(f"file:{path}?mode=ro", uri=True)` 只读 + `WHERE parent_session_id IS NULL` 过滤压缩子会话 + `ThreadPoolExecutor(4)` 并发 lark-cli 反查 + 7 天 TTL 缓存（`name_cache.json`，**勿提交 git**）。
  - **SessionDB 依赖坑**（pytest fixture 建临时库时踩过）：`SessionDB.get_session` 的 SQL 依赖 `system_prompts` 表 + sessions 表的 `system_prompt_hash`/`system_prompt` 列——测试库缺任一列都会 OperationalError。
  - 测试：前端 `selfcheck.js`（import 检查+逻辑冒烟+i18n 键一致性+硬编码中文扫描），后端 pytest 23 例（临时 SQLite，不碰真实 state.db）；CI 在 .github/workflows/ci.yml（Ubuntu + Node22 + Python3.11 + PyPI hermes-agent）。
- **需要会话人维度 → 必须 Python 后端**（`~/AppData/Local/hermes/plugins/<id>/dashboard/plugin_api.py` + manifest `"api": "plugin_api.py"`），插件侧 `ctx.rest()` 访问。纯前端 host.request 拿不到 user_name。
- 会话分组维度：平台(source)/群聊|私聊|话题(chat_type/thread_id)/profile/时间/置顶|归档；自定义标签用 ctx.storage 持久化。
- 破坏性操作（删除/归档）沿用 skill-manager 的确认流：先弹确认再执行。
- **插件内语言切换必须自研 hook**（v1.4.1 实战）：SDK 的 `ctx.i18n`/`usePluginI18n` 只能被动跟随 app locale，**没有手动覆盖 API**。自研 `useLangT`：`useI18n()` 读 app locale（zh/zh-hant→zh，其余→en）+ `ctx.storage` 存手动选择（'auto'|'zh'|'en'）+ 组件内 `useMemo` 直接查 `MESSAGES[resolved]`（函数插值器复用）。头部 `SegmentedControl` 三段切换。**默认 'auto'=跟随设备/app 语言**——用户明确要求默认跟随设备而非写死中文（"怎么默认中文？不应该默认跟随设备？"）。
  - **⚠️ `useI18n` 的 `t` 字段是字典对象不是函数**（v1.5.0 崩溃调查）：SDK `useI18n()` 返回 I18nContextValue，其中 `t: TRANSLATIONS[locale]`（context.tsx:186）——**是翻译字典对象，不是翻译函数**。任何 `const { t } = useI18n()` 后 `t('xxx')` 的写法都会抛 `t is not a function` 使整个插件页渲染失败（错误边界显示 `"page-xxx" failed to render`）。安全写法：只解构 `{ locale }`，翻译函数自己用 `MESSAGES[resolved]` 构造。
  - **防御性版本（v1.5.0 已改）**：`useLangT` 完全去掉 `useI18n` 依赖——`detectLocale()` 用 `navigator.language`（zh*→zh 否则 en，try/catch 兜底），`t` 用普通闭包（不再 useMemo 包装，少一层依赖）。这样无论 SDK hook 在真实环境返回什么形状都不影响。
  - **调试教训：node+mock hooks 模拟执行通过 ≠ 真实环境不崩**。v1.5.0 崩溃时静态审查/mock 全部通过（mock 的 useI18n 返回 `{locale:'zh'}` 与真实形状不同），真实环境才崩。遇到「mock 干净但线上崩」先怀疑 **SDK hook 的真实返回形状**（查源码确认字段类型），不要逐个 t() 调用点排查浪费时间。
- **用户自定义分类 CRUD 模式**（v1.4.1 实战）：ctx.storage 两个 key——`categories`（[{id,name}]）+ `sessionCats`（{sessionId:[catId]}）。左侧栏独立区块：分类行=标签图标+名称+计数，悬停显示重命名/删除按钮，点击行=筛选该分类；新建/重命名共用 Dialog（autoFocus+Enter+防空）；删除走 ConfirmDialog 且**级联清理**所有会话的该分类引用、筛选中的自动回退 all。会话行 `⋮` 菜单和详情头部菜单都加「分类…」勾选分组（勾选=已分配，多分类）。删除会话时清理其 sessionCats 映射。危险色 hover 用 `text-destructive`（tailwind 语义色，kanban 同款）——**`--ui-text-danger` 变量不存在**。
- **收藏（favorites）实现**（v1.4.1 实战，对标 Pi Session Manager / Loominary）：ctx.storage 单 key `favorites`（[sessionId]）。菜单（行 `⋮` + 详情头部）加「收藏/取消收藏」项，星标图标（`star-full`/`star-empty`，收藏优先于 pinned 显示在行首）；状态组加「已收藏」筛选（buildFilterOptions 第三参 favorites 计数，matchesAll 用 `f.status==='favorites' && !(f.favorites||[]).includes(s.id)` 过滤）；删除会话时从 favorites 清理；validFilters 失效回退（favorites 为空时 status→all）。\n- **导出 Markdown 实现**（v1.4.1 实战）：后端 `GET /export?session_id=&profile=` → `export_markdown()`（复用 SessionDB，元数据头 `# 标题 + - Profile/Source/Model/Started/Messages` + 分角色消息 `### 👤/🤖/🛠` + 时间戳）；前端 `doExport` 用 `apiRest` 拿 markdown → `Blob` + 临时 `<a download>` 点击下载（文件名 sanitize 非法字符 + 截 80 字符）；失败 `host.notify({kind:'error'})`。\n- **v1.4.3 列表管理模型（用户拍板「改列表显示即可，分类管理分类筛选/批量赋值/删除分类，不删会话，只做前端」）**：
  - **重命名显示名**：会话人/群聊/分类行都有**常显 ✏️ 按钮**（复用 CategoryDialog），弹框改 `displayOverrides`（ctx.storage key `displayOverrides`，{objectKey: 自定义名}）——**只改列表显示，原始数据不动**；清空输入 = 恢复默认（delete next[key]）。`objectLabel(s, t, overrides)` 签名加第三参，overrides 优先；`buildFilterOptions(all, t, favorites, overrides)` 同步传；SessionRow/详情头部调用点都传 displayOverrides。
  - **批量赋分类**：会话列表头部「选择」按钮（`checklist` codicon）切换 `selectMode` → 行内 checkbox（`check`/`circle-outline`，⚠️ `check-circle-filled` codicon 不存在）→ 底部批量条（`filter.category.selected` 计数 + DropdownMenu 列出分类）→ `bulkAssignCategory(catId)` 对选中会话去重追加、`bulkClearCategory` 移除。完成后 notify + 清空选择。
  - **移除批量删会话**：用户明确「不删会话」——`POST /delete-by-object` 端点 + 后端 `delete_by_object` + `_object_key` + ObjectRow 的 trash 按钮**全部删除**（plugin_api.py 路由 8→7）。删除只保留**单会话**（行/详情菜单的 confirm 流）。分类删除保持纯前端（只移 sessionCats 映射）。
  - 交互铁律重申：对象行操作按钮**常显**（v1.4.2 教训），本版本 ✏️ 即常显实现。
- **用户偏好：做插件 UI 前先学官方内置插件范式 + 再找 GitHub 同类真实项目对标**——用户两次纠正确立：第一次「学习下其他的优质项目」（→kanban 内置 CRUD 参考），第二次「至少找同类型的项目，github等渠道」（→**只看内置不够**）。流程：①内置 kanban（apps/desktop/src/plugins/kanban/，NewBoardDialog+确认流+persist）②`gh search repos` / web_search 找同类真实开源项目（本会话：Pi Session Manager = 本地优先会话工作台，6 语言包/标签/收藏/导出/多视图；Loominary 457★ = Claude/ChatGPT 会话管理，全局搜索/分支/收藏/批量导出）③列出能力差距表（有/无/优先级）④按标配能力补齐。会话管理器标配：分类或标签、收藏、导出、搜索、多语言。\n- **⚠️ Tailwind 类存在性审计（v1.4.2 血泪，UI 静默破损根因）**：Hermes 桌面 app 用 Tailwind v4 **编译期**扫描**自己的源码**（apps/desktop/src/）生成 CSS——插件在 `~/AppData/Local/hermes/desktop-plugins/` **构建图之外**，插件 JS 里的 className 如果 app 源码没用过，**就没有对应 CSS 规则，UI 静默破损（无报错）**。症状像「消息气泡/头像全透明」「字号不对」「布局宽度塌了」——用户报「不能直接看会话内容」实际是气泡背景类缺失。**写插件前必须对照编译产物验证每个类**（dist/assets/index-*.css，scripts/audit_classes.py 可复用）：
  - **`--ui-fill-*` 变量不存在**（`--ui-fill-tertiary`/`--ui-fill-secondary` 全库 0 次）——app 用 `--ui-bg-*` 系列（`--ui-bg-tertiary`/`--ui-bg-secondary`/`--ui-bg-quinary`）。消息气泡/头像/hover 背景用 `bg-(--ui-bg-tertiary)`。
  - **任意字号类缺失**：`text-[10.5px]`/`[12.5px]`/`[13px]` 不存在；`[9px]`/`[10px]`/`[11px]`/`[12px]` 存在。替代：`[12.5px]→text-xs`、`[13px]→text-sm`、`[10.5px]→text-[11px]`。
  - **透明度变体只有部分存在**：`bg-(--ui-bg-tertiary)/40` 有，`/50`/`/60` 没有。
  - **布局类缺失**：`w-[380px]`/`min-h-[30px]`/`max-w-24` 不存在；用 `w-80`/`min-h-7`/`max-w-60`。任意 `[Npx]` 类先查 `scripts/list_utils.py` 可用值。
  - **`--ui-danger` 不存在**，危险色 hover 用 `text-destructive`（tailwind 语义色）。
  - 验证命令：`python plugins/channel-sessions/dashboard/tests/audit_classes.py`（Tailwind 转义精确匹配 dist CSS，缺失=0 才安全）。CI 无 dist 时跳过。独立可复用脚本：`scripts/audit_plugin_classes.py`（skill 自带，任意插件可跑）。
- **操作按钮勿用 hover 隐藏**（v1.4.2 用户三连反馈确立）：分类行/对象行的编辑删除按钮 `opacity-0 group-hover:opacity-100` 让用户**发现不了入口**——用户以为「没有重命名/删除功能」，且会误把会话行菜单的「删除会话」当成删分类（「你的删除时直接删会话，不是删分类」「重命名也没有」）。管理操作按钮**默认常显**（或至少 `focus-visible` 可达），hover 只用于次要装饰。kanban 的 hover 隐藏能成立是因为它还有列内其他入口；单行 CRUD 别学。
- **块注释里 `*/` 会提前闭合注释 → 整个插件 JS 崩溃**（v1.4.2 血泪）：头部注释写「`--ui-fill-*/字号`」——`*/` 在 `/* */` 块注释中间提前终止了注释，文件后半段变成垃圾 JS，插件加载失败且报错位置误导（指向注释行附近）。**任何块注释内禁止出现 `*/` 序列**（写通配符路径如 `--ui-fill-*` 时尤其小心，星号后别跟 `/`）。
- **ESM 插件语法验证用 `node --check`**（无需 stub import）：`cp plugin.js "$LOCALAPPDATA/Temp/chk.mjs" && node --check "$LOCALAPPDATA/Temp/chk.mjs"`——`--check` 只解析语法**不解析 import**，ESM 文件可直接查。⚠️ MSYS `/tmp` 路径 node 读不到（CJS loader 报 MODULE_NOT_FOUND），必须用 Windows 临时路径（`$LOCALAPPDATA/Temp`）。不要用 vm.Script 替换 import 的方式（stub 插入位置错会制造假语法错误）。
- **插件 API 未鉴权返回 404 是设计，不是故障**：`_plugin_api_runtime_gate`（web_server.py:569）对未带 session token 的 `/api/plugins/<name>/...` 请求返回 404 防插件名枚举（鉴权失败是 401，未鉴权是 404）。curl 裸测得 404 ≠ 路由坏了。验证插件 API 正确姿势：①查 gateway 日志 `Mounted plugin API routes: /api/plugins/<name>/` 确认挂载 ②直接调 service.py 业务函数（venv 内、真库）验逻辑 ③要 HTTP 全链路就带 token（桌面 app token 注入 SPA `window.__HERMES_SESSION_TOKEN__`，仅 auth_required=false 时；开了 basic auth 就难拿，走②更实际）。**改 plugin_api.py / service.py 的生效目标按形态分（2026-08-10 实测修正，原「必须重启 gateway」是错的）**：Web Dashboard 形态（9120）的插件 Python 后端由 **HermesDashboard 计划任务进程**加载——改动后必须重启 HermesDashboard（`Stop-Process -Id <9120 PID> -Force; Start-ScheduledTask HermesDashboard`），**重启 gateway（8644）对 dashboard 插件后端无效**（实测先重启 gateway 仍旧代码，重启 9120 才生效）。desktop-plugins 的 plugin.js 热加载，plugins/ 的 Python 后端不热加载；gateway 与 dashboard 各自挂插件 API，用户实际访问走 9120。
- **评论会话并入平台列表（2026-08-10 最终形态，用户三轮拍板）**：评论会话不进 state.db，插件后端直读 Obsidian 评论目录（`HERMES_OBSIDIAN_VAULT` 环境变量优先，回退 `Documents/KnowledgeBase/Obsidian Vault/_hermes/评论会话`）。完整实现（后端合成记录/文件名解码/消息三段解析/marked 渲染/只读防护）：`references/comment-sessions-view.md`
  - **⚠️ 形态铁律（用户三次纠正确立，最终=独立平台）**：①先做「飞书评论」独立 Tab 被否——「退回上一版，飞书评论放到平台里面即可」；②合成记录 source=feishu 混入飞书平台列表再被否——「评论会话独立，和飞书平级」；③**最终形态 = 独立平台**：合成记录 `source="comment"`（`_COMMENT_SOURCE` 常量），平台筛选自动多出「飞书评论」选项与飞书平级，互不混入；不做独立 Tab/独立视图。给现有插件加旁路数据源的三级演进：独立 UI 面 → 并入现有平台 → **独立平台（平级）**，用户最终要的是第三种。
  - **后端合成模式**：`list_sessions` 末尾把评论 JSON 合成 `{id:'comment:'+文件名, source:'comment', chat_type:'comment', title:'评论 · 项目', user_name:真名反查, is_comment:True}`；`get_messages` 检测 id 前缀 `comment:` 走 JSON 读取（消息预解析成 doc/comment/original/quoted 字段 + `is_comment:True`）；`search_messages` 追加扫评论 JSON（命中返回 `comment:<file>` 可跳转，source 也标 comment）
  - **文件名解码三坑**：① key 是 `comment:{项目}:{open_id}` **两个冒号**，别切固定前缀（切残首个 `%` 标记 → 项目名乱码）② 归档文件带 `_YYYYMMDD_HHMMSS` 后缀，必须先 regex 剥离否则 open_id 被污染 ③ 解码 = 剥时间戳 → `_pct_` 还原 `%` → unquote → split(":")
  - **消息渲染**：user 消息拆「在哪个文档评论 + 评论正文 + 引用原文」三段；assistant 纯 markdown → **marked**（npm install marked + esbuild --bundle 打进 IIFE）+ `.cs-md` 全套样式（代码块/表格/列表/引用）；XSS 防御剥 script/iframe/on* 属性；JSON 不存单条时间，按 last_access 倒推 60s/条
  - **前端平台平级**：`PLATFORM_LABELS.comment = "飞书评论"`；`objectKey`/`typeLabel`/`personKey` 加 is_comment 分支（typeLabel→「评论」、personKey→name:真名）——平台筛选项从 source 自动推导，无需写死
  - **只读防护**：评论会话无管理操作（置顶/归档/重命名/删除/导出全隐藏）、批量选择自动排除（`filter(!s.is_comment)`）——JSON 只读数据源没有 state.db 操作概念，按钮打上去会报错
  - **测试隔离坑**：pytest 里评论目录指向真实目录会让 `list_sessions` 测试混入真实评论会话——测试必须 `monkeypatch.setattr(service, "_comment_dir", lambda: None)`，评论功能单独建临时目录测
  - **类审计脚本 bug（实测）**：`scripts/audit_plugin_classes.py` 有 `Path(r"%LOCALAPPDATA%" % {"LOCALAPPDATA": ""})` 格式化占位 bug（ValueError: unsupported format character）且转义匹配易误报（CSS 选择器 `\.` 转义）。可靠替代：手工提取 JSX className + 提取 CSS 选择器集合（还原 `\[`/`\.`/`\:` 转义后比对）——见 references/comment-sessions-view.md 末尾的审计代码。
  - **列表 UI 偏好（2026-08-10 用户拍板，渠道+评论通用）**：排序下拉三档——时间↓（默认）/ 时间↑ / 消息数，localStorage 持久化（cs-dash-sort）；日期分组分隔符（sticky 吸顶条）——今天 / 昨天 / 前天 / 一周前(<7d) / 一月前(<30d) / 一年前(<365d) / 更早，每组显示「标签 (数量)」；边界规则 `Math.floor((now-ts)/DAY)`，`diffDays<1→今天`（含未来时区差）。
- 插件开源发布全流程（审计维度/目录布局/CI/发布步骤/坑）：references/plugin-open-source-release.md

## 渠道会话 busy input 行为（用户发消息的处理逻辑，2026-08-11 实测）

用户说「会话改成默认引导模式 / 引导当前运行」这类口头需求时，Hermes 没有叫「引导模式」的术语——**先澄清到具体机制，不要自己猜**。常见落点是 **busy input**（agent 忙时用户发新消息怎么处理，gateway 全局配置，非飞书专属，桌面/CLI 会话不受影响）：

| 模式 | 行为 | 引导提示（首次触发时） |
|---|---|---|
| `interrupt`（默认） | 直接打断当前任务立即响应 | 提示「可排队/注入/查状态」 |
| `queue` | 消息进 FIFO 排队，当前任务跑完再处理 | 提示「已排队，/busy interrupt 可改」 |
| `steer` | 消息注入当前运行（下个工具调用后到达），不打断 | 提示「已注入，/busy queue 可改」 |

配置与生效链路（2026-08-11 实测）：
1. 改配置：`"$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/hermes" config set display.busy_input_mode steer`——⚠️ hermes 可执行文件在 `hermes-agent/venv/Scripts/hermes`，`$LOCALAPPDATA/hermes/bin/` 下只有 uv（没有 hermes.exe）
2. 重启生效：`hermes gateway restart`——busy_input 在 gateway 启动时读一次（实例变量 `_busy_input_mode`）；本次实测 status/restart 均未触发 update 恢复流程，安全
3. 验证三连（比看状态命令全绿更硬）：① `grep busy_input_mode config.yaml` 值已改 ② 端口 8644 LISTENING + 日志「Gateway running with N platform(s)」③ **真实读取链路**：`cd $LOCALAPPDATA/hermes/hermes-agent && venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'.'); sys.path.insert(0,'gateway'); from run import GatewayRunner; print(GatewayRunner._load_busy_input_mode())"` 返回目标值
4. 读取优先级：`HERMES_GATEWAY_BUSY_INPUT_MODE` 环境变量 > config.yaml `display.busy_input_mode`（gateway/run.py:8553 `_load_busy_input_mode`）
5. steer 回退语义：消息为空/带附件/agent 无 steer()/steer 被拒 → 自动回退 queue（run.py:15327+）；用户可用 `/busy` 命令随时切回

相关但不同：`onboarding.profile_build`（config.yaml `onboarding:` 段，默认 `ask`）——**首次**接触引导（第一条消息自我介绍+opt-in 建画像），只触发一次非每次会话，可改 `off` 但无强制档；用户说「引导模式」若指开场引导往这澄清。

## 真名反查通道（按优先级）

1. bot 身份 `contact.v3.user.get`（lark-oapi GetUserRequest，adapter 内置，需 contact:user.base:readonly 权限）
2. user 身份批量 `lark-cli contact +search-user --user-ids`（返回 localized_name，实测稳定）
3. 群成员批量映射 `lark-cli im +chat-members-list --chat-id oc_xxx --as bot`（一次拿全群真名+open_id，摘要类 cron 首选）

## 飞书评论会话（channel-sessions v1.6.x，2026-08-10 落地）

**评论会话 ≠ state.db 会话**：评论 agent（feishu_comment.py）是独立 AIAgent，会话只存 JSON（`Obsidian Vault/_hermes/评论会话/*.json` + `archive/`），**不进 sessions 表**——客户端侧边栏/任何读 state.db 的列表天然看不到。channel-sessions 插件把它合成 session 记录暴露：

- **独立平台**（用户拍板「和飞书平级」）：合成记录 `source="comment"`（`_COMMENT_SOURCE` 常量），前端 `PLATFORM_LABELS.comment="飞书评论"`——平台筛选自动多出「飞书评论」选项，与飞书平级。**不要**混入 feishu（用户否过）也不要独立 Tab（用户也否过）
- **合成记录字段**：`id="comment:<文件名>"`、`title="评论 · 项目"`、`chat_type="comment"`、`user_name` 复用 NameResolver 反查、`archived` 从 archive/ 目录推断、`is_comment=True` 标记
- **文件名解码**（`_decode_comment_key`）：`comment_pct_3A_<URL编码>_pct_3A<open_id>.json`，编码规则 `quote(key, safe="").replace("%","_pct_")`；**归档文件 open_id 后有 `_YYYYMMDD_HHMMSS` 时间戳后缀要先剥离**（`re.sub(r"_\d{8}_\d{6}$","",body)`）；解码后 key 是 `comment:项目:open_id` 两段冒号，用 split(":") 取 [1]/[2:]（partition 只取第一段会错）
- **消息读取**：`get_messages` 检测 `session_id.startswith("comment:")` → 走 `get_comment_messages(file)` 读 JSON，解析出 `{doc, comment, original, quoted}` 结构化字段（解析 `The user added a reply in "X"` / `Current user comment text: "Y"` / `Quoted content: "Z"` 行）+ `is_comment=True`；assistant 消息是纯 markdown
- **只读数据源**：评论会话无置顶/归档/重命名/删除/导出概念（会打到 state.db 报错）——前端 SessionRow 用 `noOps=is_comment` 隐藏操作按钮，批量选择跳过，详情头部管理按钮条件渲染
- **全文搜索**：`search_messages` 额外扫评论 JSON（`_search_comment_messages`，content 子串匹配），命中返回 `session_id="comment:<file>"` 供前端跳转
- **测试隔离**：评论目录发现用 `_comment_dir()`（env `HERMES_OBSIDIAN_VAULT` + 两个 fallback 路径）；pytest 里 `monkeypatch.setattr(service, "_comment_dir", lambda: None)` 隔离真实评论目录，否则测试环境混入真实评论会话导致断言失败
- **前端渲染**：MessageItem 检测 `m.is_comment` → CommentMessageItem（三段式：文档名/评论正文/引用原文 + marked markdown 渲染，XSS 剥 script/iframe/on*）；`marked` 经 esbuild bundle 进 IIFE（`import { marked } from "marked"`，76KB）
- **时间戳是模拟的**：JSON 不存单条时间，按 `last_access - (条数-1-i)*60` 倒推——分钟级精度，非真实时间

## 相关文件路径（2026-08-06 实测）

- feishu adapter：plugins/platforms/feishu/adapter.py:4174 `_resolve_sender_name_from_api`、:4152 `_resolve_sender_profile`
- display_name 落库：gateway/session.py:1821 `_create_entry_from_recovered_row`
- 桌面渲染：apps/desktop/src/app/chat/sidebar/session-row.tsx:82 `sessionTitle(session)`；lib/chat-runtime.ts:64（title||preview||'Untitled'）
- 侧边栏 messaging 分组：apps/desktop/src/app/chat/sidebar/index.tsx:890+
- 详细端点/字段清单：references/session-data-apis.md
