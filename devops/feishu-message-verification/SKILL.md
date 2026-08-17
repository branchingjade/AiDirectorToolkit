---
name: feishu-message-verification
description: "Use when 核实飞书消息事实——某人真的发了N次吗、bot是否重复回复、补推重放排查。"
version: 1.0.0
tags: [feishu, gateway, message, forensics, replay, dedup]
---

# 飞书消息事实核实与补推重放排查

当用户质疑「某人是不是真的重复发了消息」「bot 是不是重复回复了」「这条回复到底是谁发的/我补的还是对方重发的」时，用本流程。**核心原则：gateway 日志和 bot 自己的描述都不是事实，飞书 API 历史才是事实**——一切结论以 `lark-cli im +chat-messages-list` 返回的 message_id 为准。

2026-08-07 实战验证：叶子「重复发三次」案例——最终查明叶子实际发了 4 次（3 次在停机窗口内），bot 的「这是第三次发了」回复是被**补推重放**触发的假象。

## 一、消息事实的三层证据链（从弱到强）

| 层级 | 来源 | 可信度 | 说明 |
|---|---|---|---|
| 1 | bot 回复内容自称（「这段是第三次发了」「给过三次成品了」） | ❌ 不可信 | bot 只会按自己收到的入站事件数数，不知道补推重放，也不知道用户实际发了几次 |
| 2 | gateway.log 的 `inbound message` / `Sending response` | ⚠️ 半可信 | 能证明 gateway 处理了多少次，但**补推重放会被误记为「新消息」**——收到次数 ≠ 用户真实发送次数 |
| 3 | `lark-cli im +chat-messages-list` 返回的真实消息历史（含 message_id） | ✅ 事实 | 飞书服务端记录，用户真实发送/撤回的全部消息都在这里 |

**判定「某人真的发了 N 次」只能信第 3 层**——数 API 历史里该用户（`sender.sender_type == 'user'`）的同类内容消息条数。

## 二、补推重放陷阱（核心坑）

**现象**：gateway 停机（WebSocket 断连）期间用户发的消息，会在恢复后**数小时**以「补推」形式重新进入 gateway——实测停机 10:56-14:18，11:43/11:51/14:00 的旧消息在 15:05/18:48/18:56/18:57 才到达，且 **message_id 仍是旧消息的 id**。

**危害**：gateway 没有按 message_id 去重，补推消息被当新消息处理 → 对同一素材重复回复（实测对同一段提示词回了 3 次，每次还自称「这是第三次发了」）。

**识别方法**：gateway 日志入站消息的 message_id，如果在 API 历史里对应的是**更早时间**的消息 → 这是重放，不是新消息。

```bash
# gateway 日志里的入站 message_id（含完整 id）
grep "Inbound dm message received" ~/AppData/Local/hermes/logs/gateway.log | grep "2026-08-07 1[5-9]:"
# → id=om_x100b6863086954a8c278d9842e40348  ← 尾部 42e40348 与 API 历史 14:00 那条消息 id 吻合

# API 历史里的真实消息（含 message_id、sender_type、deleted 标志）
lark-cli im +chat-messages-list --chat-id <oc_xxx> --as bot --order desc --page-all
```

**对比方法**：把 gateway 日志入站 id 的尾部（如 `42e40348`）与 API 历史各消息 id 尾部匹配——命中旧消息 = 重放。也可看 bot 回复消息的 `reply_to` 字段指向哪条 user 消息：若指向几小时前的旧消息，说明这次回复是被补推触发的。

**对宕机恢复流程的影响**：⚠️ 恢复后**不要急着把停机窗口消息手动补发**——消息可能已被补推重放处理过，再补就重复了。先查重放，再决定补不补。这与 feishu-outage-recovery skill 里「停机消息不会自动补推」的说法矛盾（2026-08-07 实测证明会补推，只是延迟数小时）——若该 skill 已 adopt 修正，以新版本为准。

## 三、核实步骤（完整流程）

1. **收集 bot 侧处理记录**：
   ```bash
   grep "oc_c9469b68b96284d358a1be43185d692b" ~/AppData/Local/hermes/logs/gateway.log | grep "2026-08-07"
   ```
   记录每次 `inbound message`（入站）和 `Sending response`（出站）的时间与 id。

2. **拉取 API 真实历史**（bot 身份，勿用 user 身份——实测 `--as user` 对该会话返回 0 条）：
   ```bash
   lark-cli im +chat-messages-list --chat-id <oc_xxx> --as bot --order asc --page-all --page-limit 30
   ```
   - **输出可能带 warning 行**（如 `warning: reactions_partial_failed: ...`）在 JSON 前面——解析时先 `raw.find('{')` 再 `json.loads`。
   - 消息结构：`content` 在顶层（不是 body.content）；`msg_type`（text/post）；`sender.sender_type`（`app`=bot / `user`=人）；`create_time`；`deleted`（True=已撤回）；`reply_to`（回复指向的消息 id）。
   - content 可能是 JSON 字符串（post 类型）——`json.loads(content).get('text')` 才拿得到正文。

3. **数真实发送次数**：过滤 `sender_type=='user'`，按内容归类统计。注意相同素材可能带/不带「生成提示词：」前缀（长度差 6），要按去前缀后的正文比对。

4. **判定重复回复**：数 bot（`sender_type=='app'`）的同类回复条数 + 查每条 `reply_to` 指向的 user 消息时间。reply_to 全部指向旧消息 = 全是补推重放触发，用户并没有再发。

5. **汇报时给出完整时间线表格**：用户消息（真实次数）→ bot 回复（每条对应哪条 user 消息）→ 指出哪些是重放触发。用户会追问证据，把 message_id 尾部列出来。

## 四、lark-cli 实测坑速查

| 坑 | 现象 | 处理 |
|---|---|---|
| `--as user` 返回 0 条 | 同一会话 user 身份拉不到消息（权限/可见性） | 改用 `--as bot` |
| warning 行混入输出 | `reactions_partial_failed` 等 warning 在 JSON 前 | `raw[raw.find('{'):]` 再 json.loads |
| content 解析为空 | post 类型消息 content 是 JSON 字符串 | `json.loads(content).get('text')` |
| 消息数对不上 | 分页/时间窗参数问题 | 用 `--order asc --page-all --page-limit 30` 拉全量，再过滤日期 |
| 想数 bot 发了多少 | 只看 `Sending response` 不够 | 用 API 历史里 `sender_type=='app'` 条数 |

## 五、报告格式（用户认可）

结论先行（「叶子真的发了 4 次，不是 3 次」），然后：时间线表格（每条含时间/内容首 40 字/message_id 尾部）、bot 回复与 user 消息的对应关系（reply_to 链）、补推重放识别依据、根因总结（如「3 次撞停机窗口没回复，她反复重发；bot 后两次回复是补推误触发」）。最后给修复建议（gateway 应对入站 message_id 去重/打重放标记）。

## 相关 skill

- [feishu-outage-recovery](../feishu-outage-recovery/SKILL.md) — 宕机恢复主流程（user-owned；其中「停机消息不补推」表述已被本 skill 实测推翻，待 adopt 后修正）
- [lark-im](../../lark-im/SKILL.md) — `+chat-messages-list` 完整参数参考
