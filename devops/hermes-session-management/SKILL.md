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

实测案例（2026-08-07）：用户问「记忆的tag打了吗」→ 会话中断 → 用户重开 app 看到"新会话"说"真的丢了"。查 state.db 发现原 session（记忆与画像机制推敲）122 条消息全在，从 10:50 到 11:02 连续无断档，当前对话还在往同一 session 写。数据层 0 丢失，纯显示层。

## 关键坑

1. **私聊 display_name 落 chat_id 的根因**：gateway/session.py:1821 `display_name=source.chat_name`——P2P 会话的 chat_info.name 为空 → 回退 chat_id。即使 feishu adapter 已解析出真名（_resolve_sender_profile → user_name），也不写入 display_name。这是结构性的（不是权限问题）。
2. **REST 列表不含会话人字段**：list_sessions_rich 只返回 id/source/model/title/started_at/ended_at/message_count/preview/last_active/pinned/archived/profile——**没有 user_id/display_name/chat_id/session_key**（hermes_state.py:5547+ docstring）。纯前端拿不到会话人。
3. **历史会话不回填**：display_name 只有新消息触发解析时更新；权限开通前建的旧会话永久停留在 chat_id/群名。
4. **权限验证链**：`lark-cli contact +get-user --user-id ou_xxx --as bot` 返回非空 `name` 字段 = bot 权限已生效（contact:user.base:readonly）。返回「用户+N」= 该账号资料未设姓名，不是权限问题。

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
- **需要会话人维度 → 必须 Python 后端**（`~/AppData/Local/hermes/plugins/<id>/dashboard/plugin_api.py` + manifest `"api": "plugin_api.py"`），插件侧 `ctx.rest()` 访问。纯前端 host.request 拿不到 user_name。
- 会话分组维度：平台(source)/群聊|私聊|话题(chat_type/thread_id)/profile/时间/置顶|归档；自定义标签用 ctx.storage 持久化。
- 破坏性操作（删除/归档）沿用 skill-manager 的确认流：先弹确认再执行。

## 真名反查通道（按优先级）

1. bot 身份 `contact.v3.user.get`（lark-oapi GetUserRequest，adapter 内置，需 contact:user.base:readonly 权限）
2. user 身份批量 `lark-cli contact +search-user --user-ids`（返回 localized_name，实测稳定）
3. 群成员批量映射 `lark-cli im +chat-members-list --chat-id oc_xxx --as bot`（一次拿全群真名+open_id，摘要类 cron 首选）

## 相关文件路径（2026-08-06 实测）

- feishu adapter：plugins/platforms/feishu/adapter.py:4174 `_resolve_sender_name_from_api`、:4152 `_resolve_sender_profile`
- display_name 落库：gateway/session.py:1821 `_create_entry_from_recovered_row`
- 桌面渲染：apps/desktop/src/app/chat/sidebar/session-row.tsx:82 `sessionTitle(session)`；lib/chat-runtime.ts:64（title||preview||'Untitled'）
- 侧边栏 messaging 分组：apps/desktop/src/app/chat/sidebar/index.tsx:890+
- 详细端点/字段清单：references/session-data-apis.md
