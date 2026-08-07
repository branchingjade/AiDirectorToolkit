# Gateway 停机期间飞书消息丢失与手动拉回（实测 2026-08-07）

## 核心事实

- 飞书 WebSocket 断连期间的消息**不会自动补推**——重连后只收到新消息，停机窗口内的消息对 Hermes 是丢失的（飞书侧保留，可经 API 拉回）。
- 自动 resume 机制只恢复「停机瞬间 in-flight 的会话」（`suspend_recently_active` 120s 窗口），**不**恢复停机期间新发的消息。停机 3 小时后重启，所有会话 `resume_pending: false` 属正常，不等于消息没丢。
- 判断停机时有无 in-flight 会话：gateway.log 的 drain 段 `active_at_start=0` = 无活跃会话，无需恢复。

## 手动拉回流程

1. **枚举候选会话**：`~/AppData/Local/hermes/sessions/sessions.json` 的 `session_key`（`agent:main:feishu:dm:oc_xxx` / `feishu:group:oc_xxx` 提取 chat_id）+ `lark-cli im +chat-list --as bot --types=group`（bot 能列出的群）。p2p 候选只能靠 sessions.json——bot 身份无法列 p2p 会话（隐私保护）。
2. **逐会话拉取停机窗口消息**：
```bash
lark-cli im +chat-messages-list --chat-id <oc_xxx> --as bot \
  --start "2026-08-07T10:56:00+08:00" --end "2026-08-07T14:18:00+08:00" \
  --order asc --page-all
```
3. **解析字段：`data.messages`，不是 `data.items`！** 解析错字段会得到假「0 条消息」——本次实测前几轮全被这个坑误导，误判「无消息」。先 `print(list(data.keys()))` 确认结构。
4. **补回复**：`lark-cli im +messages-send --chat-id <oc_xxx> --as bot --text "..."`（宕机道歉 + 简述处理），然后 `+chat-messages-list --order desc --page-limit 2` 验证送达（最近一条 sender 应为 Hermes）。

## 身份限制

- `--user-id` 仅限 user 身份；bot 身份传 `--user-id` 报 `invalid_argument`，必须用 `--chat-id`。
- `--as user --user-id <ou_>` 拉的是**该 user 自己**与目标用户的私聊，不是 bot 的会话——不要用这个找 bot 消息。
- bot 身份查 p2p 历史消息：只要 bot 还在会话里，`--chat-id` 就能拉（实测可行）。
- `+messages-search`（user 身份全局搜）需要 `search:message` scope，未授权时 `missing_scope`——不要走这条路，逐个 chat 拉更省事。

## 错误码与解析陷阱

- `230002 Bot/User can NOT be out of the chat` = bot 已不在该会话（旧应用迁移/被移出/历史 session），跳过即可，不是故障。
- 部分失败返回非 JSON 空输出——用 `2>&1 | head -c 500` 看原始输出判断，别直接 json.load 报 PARSE_ERR 后瞎猜。
- 停机窗口取 `--start`/`--end` 用 ISO 8601 带时区偏移（`+08:00`），`--order asc` 按时间正序，`--page-all` 翻全页。
