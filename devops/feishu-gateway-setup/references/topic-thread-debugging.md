# 飞书话题/引用回复消息诊断指南

## 问题现象

用户在飞书「话题」中 @Hermes，Bot 不回复。普通群聊消息正常。

## 消息处理流程

```
飞书 WebSocket event (im.message.receive_v1)
  → _on_message_event (adapter.py:2408)
    → _handle_message_event_data (adapter.py:2542)
      → _admit(sender, message) (adapter.py:4251)     ← 第一道关卡
        ├─ _allow_group_message → 检查群策略
        └─ _mentions_self → 检查 @提及              ← 关键：parent_id 不为空时 mentions 可能为空
      → _process_inbound_message (adapter.py:3245)
        → _extract_message_content                  ← 日志 "Received raw message"
        → 空文本检查 (line 3263-3265)               ← 第二道关卡
        → 日志 "Inbound group message received"      ← 成功标志
```

## 诊断步骤

### 1. 开启 DEBUG 日志（前台模式）

**⚠️ `LOG_LEVEL=DEBUG` 在 `.env` 中对 gateway 无效。** Gateway 的日志级别由 CLI 参数 `-v`/`-vv` 控制，不读取 `LOG_LEVEL` 环境变量。

```bash
# 先停止后台服务
hermes gateway stop

# 前台运行，-vv 开启 DEBUG 级别 stderr 输出
# --force: 即使 systemd/launchd 已安装也强制前台运行
hermes gateway run -vv --force 2>&1
```

运行后会持续输出到终端。测试完毕后 `Ctrl+C` 停止，再用 `hermes gateway start` 恢复后台运行。

**注意**: `hermes gateway start -vv` 不支持——`-v` 只对 `gateway run`（前台子命令）有效。

### 2. 触发问题

让用户在话题中 @Hermes，发送测试消息。

### 3. 检查日志

```bash
LOG_DIR="$(dirname "$(hermes config path)")/logs"
# 查看该消息是否到达
grep "om_x<message_id>" "$LOG_DIR/gateway.log"
# 查看丢弃原因
grep "dropping inbound event" "$LOG_DIR/gateway.log" | tail -10
# 查看空文本丢弃
grep "Ignoring empty text message" "$LOG_DIR/gateway.log" | tail -10
```

### 4. 症状诊断矩阵

| 日志症状 | 根因 | 修复 |
|---------|------|------|
| 完全没有该 message_id 的日志 | 飞书 WebSocket 未推送事件 | 检查飞书开发者后台事件订阅，确认 `im.message.receive_v1` 已订阅 |
| 有 "Received raw message" 但无 "Inbound group message received" | `_admit` 或 `_process_inbound_message` 中途丢弃 | 检查 DEBUG 日志中的 "dropping inbound event" 原因。若 DEBUG 仍无输出，用增强日志注入（见下方 §6）定位 |
| "dropping inbound event: group_policy_rejected" 且消息有 parent_id | `_mentions_self()` 检测不到 @提及（mentions 数组为空） | ①确认 `group_rules` bridge 已修复 ②确认群 `require_mention: false` |
| "Ignoring empty text message" | 文本归一化后变空 | `_strip_edge_self_mentions` 将纯 @Bot 消息剥离为空白——这是预期行为；如果内容应非空却被丢弃，检查 normalize 逻辑 |

### 5. 高级：增强日志注入（绕过 DEBUG 级别）

当 `_admit` 的丢弃原因只有 DEBUG 级别（你看不到），或需要确认 adapter 初始化参数时，直接在 adapter.py 注入 INFO 级别临时日志：

**adapter 初始化参数确认：**（adapter.py ~line 1650 的 `self._require_mention = settings.require_mention` 之后）
```python
logger.info("[Feishu] Adapter init: _require_mention=%s, _group_rules=%s, _group_policy=%s",
            self._require_mention,
            {k: (v.policy, v.require_mention) for k, v in self._group_rules.items()} if self._group_rules else {},
            self._default_group_policy or self._group_policy)
```

**`_admit` 入口追踪：**（adapter.py ~line 4269 的 `require_mention = ...` 之后）
```python
logger.info("[Feishu] _admit: chat_id=%s is_group=%s require_mention=%s _require_mention=%s sender=%s",
            chat_id, is_group, require_mention, self._require_mention,
            getattr(sender, "sender_id", None))
```

**消息内容增强：**（adapter.py ~line 3765 替换原有的 "Received raw message" 日志）
```python
logger.info("[Feishu] Received raw message type=%s message_id=%s chat_id=%s chat_type=%s parent_id=%s content=%s",
            raw_type, message_id,
            getattr(message, "chat_id", "") or "",
            getattr(message, "chat_type", "") or "",
            getattr(message, "parent_id", "") or getattr(message, "root_id", "") or "",
            raw_content[:200] if raw_content else "")
```

**消息归一化追踪：**（adapter.py ~line 3258 的 `_strip_edge_self_mentions` 前后）
```python
text_before_strip = text
text = _strip_edge_self_mentions(text, mentions)
if text_before_strip != text:
    logger.info("[Feishu] Stripped edge mentions: %r -> %r (mentions=%d)",
                text_before_strip[:80], text[:80], len(mentions))
```

这些日志每次都输出到 INFO 级别，无需 DEBUG 模式就能看到完整决策链。排查完毕后记得 revert。

### 6. 已知代码位置 (hermes-agent)

- `adapter.py:4251` — `_admit()`: 准入检查入口
- `adapter.py:4294` — `require_mention and not self._mentions_self(message)` → 拒绝
- `adapter.py:4351` — `_mentions_self()`: 从 `message.mentions` 读取提及列表
- `adapter.py:3245` — `_process_inbound_message()`: 消息处理入口
- `adapter.py:3263` — 空文本检查: `if not text and not media_urls: return`
- `adapter.py:3765` — `_extract_message_content()`: "Received raw message" 日志
- `adapter.py:3288` — "Inbound group message received" 日志（到达此处＝消息通过所有关卡）
- `adapter.py:3272` — `thread_id = getattr(message, "thread_id", ...)`: 话题 ID 提取
- `adapter.py:1616` — `_require_mention` 从 `extra.get("require_mention")` 初始化
- `adapter.py:1530` — `_group_rules` 从 `extra.get("group_rules")` 解析，但此值依赖 bridge 传入
- `gateway/config.py:1207-1208` — `free_response_channels` **已 bridge**（但 adapter 不读取它——零引用）
- `gateway/config.py` — `group_rules` **未 bridge**（grep 确认零引用），需手动添加 bridge 代码

## 已确认的根因

**飞书 API 行为**: 当消息带有 `parent_id`（话题回复/引用回复），飞书不在 `message.mentions` 中包含 @提及信息。此时 `_mentions_self()` 无法通过 mentions 数组检测到 @Bot，只能依赖文本内容中的 `@_all` 或 normalize 后的二次检测。

当前 normalize 路径的 `_post_mentions_bot()` 检查的是 normalize 产生的 mentions，但如果 Feishu raw mentions 为空且文本中没有 `@_all`，整个 `_mentions_self()` 返回 False。

## 关联配置

- `FEISHU_GROUP_POLICY=open` (env var) — 必须设置，否则所有群消息被拒
- `platforms.feishu.group_rules.<chat_id>.require_mention: false` (config.yaml) — 需要 `group_rules` bridge 修复才能生效
- `platforms.feishu.require_mention: true` (config.yaml) — 全局默认，`group_rules` 未 bridge 时生效
