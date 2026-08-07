# 飞书会话人显示三层链路（实测 2026-08-06）

回答「Hermes 能显示飞书会话人吗」类问题的完整诊断模型。三层分别查，结论模板见文末。

## ① Agent 上下文（LLM 知道是谁）——✅ 能

- feishu adapter `_resolve_sender_name_from_api`（plugins/platforms/feishu/adapter.py:4174）用 `contact.v3.user.get` 反查真名，成功则 `source.user_name` 有值（失败静默，返回 None）。
- 上下文注入（gateway/session.py:575-592）：
  - 私聊 → `**User:** <真名>` 行
  - 多用户群会话 → `**Session type:** Multi-user session — messages are prefixed with [sender name]`，每条用户消息带 [sender name] 前缀
  - 反查失败降级 → `**User ID:** ou_xxx`（开 privacy.redact_pii 则哈希）
- 前提：应用开通 `contact:user.base:readonly`。验证：`lark-cli contact +get-user --user-id ou_xxx --as bot` 返回 `data.user.name` 非空即生效（本例已开通，实测反查到「全志越」）。

## ② state.db sessions 表——⚠️ 存了，但私聊 display_name 落 chat_id

- 字段：`user_id`（open_id）+ `display_name` + `chat_id` + `title`（AI 自动生成）。
- **关键事实：display_name 写入用 `source.chat_name`（gateway/session.py:1821），不是 user_name**：
  - 群聊 → 群名（如「开工」）
  - 私聊 → chat_id（oc_xxx）——P2P 的 chat_info.name 为空回退 chat_id，**即使真名已解析也不落库**
- 历史会话不回填，仅新消息触发解析（权限开通后需 `hermes gateway restart`）。
- 排查命令：
  ```python
  import sqlite3
  conn = sqlite3.connect(r'C:\Users\HMSJ\AppData\Local\hermes\state.db')
  cur = conn.cursor()
  cur.execute("SELECT id,title,user_id,display_name,chat_id FROM sessions WHERE source='feishu' ORDER BY id DESC LIMIT 15")
  for r in cur.fetchall(): print(r)
  ```
- 若要私聊 display_name 落真名：改 session.py:1821 私聊分支用 `source.user_name`（gateway 源码改动，升级会被覆盖）。

## ③ 桌面端 UI——❌ 不显示会话人

- 侧边栏 Messaging 区块：每行标题 = `session.title || session.preview`（`sessionTitle`，apps/desktop/src/lib/chat-runtime.ts:64），即 AI 自动生成的会话标题（如「深渊古堡的紧急密谈」），**无发送人信息**。
- 聊天区消息气泡不标发送人。
- 唯一显示 user_name 的地方：配对用户管理面板（apps/desktop/src/app/messaging/index.tsx，`pairingLabel = user.user_name || user.user_id`）。
- 若要 UI 显示发送人：改 apps/desktop/src/app/chat/sidebar/session-row.tsx 渲染 + 数据流补 user_name（desktop 端源码改动，需重新构建）。

## 结论模板

「Hermes 内部知道谁在说话（`**User:**` 行），数据库存了 open_id，但桌面界面看不到发送人——列表只有 AI 标题，私聊 display_name 是 chat_id 而非真名。」

## 注意

- 群聊里所有成员的 display_name 都是群名，区分发言者只能靠 user_id（open_id）或 [sender name] 前缀。
- 换应用后 open_id 全变（应用级隔离），历史会话的 user_id 与新会话无法对应。
