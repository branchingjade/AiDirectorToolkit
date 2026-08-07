# Hermes 会话数据 API 与字段清单

2026-08-06 实测。源码位置：`~/AppData/Local/hermes/hermes-agent/`。

## REST 端点

### GET /api/profiles/sessions（跨 profile 会话列表）
`hermes_cli/web_routers/profiles.py:57`

参数：
- `limit` 0-500（默认 20；桌面端实际用 200）
- `offset`（默认 0）
- `min_messages`（默认 0）
- `archived`: `exclude`（默认）| `only` | `include`
- `order`: `recent`（默认，按 last_active）| `created`（按 started_at）
- `profile`: `all`（默认，聚合所有 profile）| 具体 profile 名
- `source`: 单一 source 过滤（如 `feishu`、`cron`）
- `exclude_sources`: 逗号分隔排除（如 `cron`）
- `full=1`: 含 system_prompt/model_config blob（默认省略）

返回：`{sessions, total, profile_totals, limit, offset, errors}`

注意：每 profile 单独 LIMIT 过取再合并排序；pinned 会话会跨过 LIMIT 窗口回填。跨 profile 聚合时每 profile 的 state.db 以 read_only 打开。

### GET /api/profiles/sessions/sidebar（批量三切片）
`hermes_cli/web_routers/profiles.py:201`

一次请求返回 recents + cron + messaging 三个切片，每切片独立 limit/exclude。桌面端 10s 轮询一次（apps/desktop/src/app/contrib/hooks/use-background-sync.ts）。

### 会话管理（hermes_cli/web_routers/sessions.py）
- `GET /api/sessions` — 单 profile 列表
- `GET /api/sessions/{id}` — 单会话详情
- `GET /api/sessions/{id}/messages` — 消息
- `PATCH /api/sessions/{id}` — rename / archive / pin（桌面端封装：setSessionArchived / setSessionPinnedRemote / renameSession）
- `DELETE /api/sessions/{id}` — 删除
- `POST /api/sessions/bulk_delete` — 批量删除（:393）
- `GET /api/sessions/search` — 搜索（:167）

## list_sessions_rich 返回字段（字段投影）

`hermes_state.py:5547`。`compact_rows=True`（列表默认）时返回：

`id, source, model, title, started_at, ended_at, message_count, preview, last_active, pinned, archived`

+ profiles.py 附加：`profile, is_default_profile, is_active, archived(bool), pinned(bool)`

**关键缺口**：不含 `user_id` / `display_name` / `chat_id` / `chat_type` / `thread_id` / `session_key`——会话人信息在列表接口不投影。要拿这些字段必须：
1. 直接查 state.db sessions 表（read_only 打开），或
2. 会话详情端点 /api/sessions/{id}（origin_json 等完整行）

## state.db sessions 表关键列

`id, source, user_id, title, session_key, chat_id, chat_type, thread_id, display_name, started_at, ended_at, message_count, last_active, pinned, archived, profile_name`

- 群聊 display_name = 群名（如「开工」）
- 私聊 display_name = chat_id（oc_xxx）——根因见 SKILL.md 关键坑 #1
- 所有渠道会话都有 session_key（feishu:dm:{chat_id} / feishu:group:{chat_id}:{thread_id}:{user_id} 等）

## 桌面端渲染事实

- 侧边栏 messaging 区块：按平台分组（`normalizeSessionSource(session.source)`），组内按 last_active 排序，行显示 `sessionTitle(session)` = `title?.trim() || preview?.trim() || 'Untitled session'`（lib/chat-runtime.ts:64）
- 打开会话：`openSession(id, navigate, intent)`（app/open-session.ts:72），插件用 `host.navigate(sessionRoute(id))`
- 配对用户管理面板（app/messaging/index.tsx）显示 `user_name || user_id`——这是桌面端唯一显示会话人名的界面，但那是配对授权管理，不是会话列表

## 查询示例

```bash
# 直接读 state.db 查会话人（read_only）
python -c "
import sqlite3
conn = sqlite3.connect('state.db')
cur = conn.cursor()
cur.execute('SELECT id, source, user_id, display_name, chat_id FROM sessions WHERE source LIKE \"%feishu%\" ORDER BY id DESC LIMIT 10')
for r in cur.fetchall(): print(r)
"
```
