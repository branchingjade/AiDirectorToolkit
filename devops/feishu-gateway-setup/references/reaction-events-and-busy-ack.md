# Feishu Reaction 事件与 "⚡ Interrupting current task" 误触发（实测 2026-08-07）

## 症状

用户在飞书群里收到「⚡ Interrupting current task. I'll respond to your message shortly.」，
但 agent 当时**并没有在处理别的会话/任务**——回复早已发完，会话看起来应该是空闲的。

## 排查结论（gateway.log 证据链）

开工群 oc_685820... 时间线：

| 时间 | 事件 |
|---|---|
| 16:58:01 | 用户 @Hermes 提问 → 会话 `20260807_165801` 启动 |
| 16:58:48 | 回复完成（47.3s, 839 chars）→ `response ready` + `Sending response` |
| 17:09:02 | 用户给 bot 回复**点赞**（reaction:added:THUMBSUP）→ adapter 构造成 TEXT 消息进管线 |
| 17:09:03 | 取消赞（reaction:removed）又进一条 |
| 17:09:47 | `Queued follow-up ...: final stream delivery not confirmed; sending first response before continuing` |
| 17:09:52 | 8 chars 响应发出（50.1s, 1 次 API 调用） |

## 根因（两层叠加）

### 1. 深层：回复的流式投递最终确认没收到，会话 11 分钟不释放

`response ready` + `Sending response` 之后，gateway 一直在等「投递完成」的最终确认
（`final stream delivery not confirmed`）。没等到 → 会话保持 busy 状态。
17:09 点赞事件进来时撞上这个未释放的 busy 状态 → 走 interrupt 分支 → 发
「⚡ Interrupting current task」。**会话是独立的，没被别的任务占用——是它自己被卡在 busy 判定里。**

日志关键词：`Queued follow-up ...: final stream delivery not confirmed`。
排查方法：`grep -n "<chat_id>" gateway.log | tail` 按 chat_id 追全时间线，看
`response ready` 之后是否隔了很久才出现 follow-up/ack。

### 2. 表层：点赞/取消赞被当成对话消息处理（设计冗余）

`plugins/platforms/feishu/adapter.py` 的 reaction 路由（约 3020-3028 行）：

```python
synthetic_text = f"reaction:{action}:{emoji_type}"   # "reaction:added:THUMBSUP"
synthetic_event = MessageEvent(
    text=synthetic_text,
    message_type=MessageType.TEXT,   # ← 当成普通文本消息
    ...
)
await self._handle_message_with_guards(synthetic_event)  # ← 进正常消息管线
```

结果：一个点赞触发**一次完整的 agent 运行**（实测 50.1s、1 次 LLM 调用），
取消赞再触发一次。第二条 reaction 进来时若第一条还在跑 → busy → interrupt ack。

**注意**：`_handle_reaction_event`（run.py:7248，emit hook，非阻塞）与 adapter 的
`_handle_message_with_guards` 是**两条不同路径**——点赞事件两者都走，既 emit hook 又进 agent 对话。

## 相关配置开关（gateway/run.py）

| 配置 | 位置 | 效果 |
|---|---|---|
| `display.busy_ack_enabled`（env: `HERMES_GATEWAY_BUSY_ACK_ENABLED`） | run.py:9076 | `false` = 忙时**完全静默**：消息照常排队处理，但不再发任何 ack（含「⚡ Interrupting」） |
| `display.busy_input_mode`（env: `HERMES_GATEWAY_BUSY_INPUT_MODE`） | run.py:8325 `_load_busy_input_mode` | `interrupt`（默认）/ `queue` / `steer`。`queue` = 不打断当前任务，发「⏳ Queued for the next turn」 |
| `display.busy_ack_detail` | run.py:9140 附近 | 控制 ack 里的状态详情（iteration/tool），不是开关本身 |
| `display.busy_steer_ack_enabled` | run.py:9106 | steer 模式的确认回显开关 |

`_busy_text_mode`（run.py:8338）是 legacy 开关，仅显式设置时优先；新安装跟随 `busy_input_mode`。

首次提示 onboarding（`busy_input_prompt`，onboarding.seen）只控制是否附首次说明文案，
**不控制提示本身是否发送**——用户可能误以为「关过」，实际只关掉了首次引导。

## 关联：`streaming.enabled: false` 与投递确认（2026-08-07 追加排查）

本机 `config.yaml` 的 `streaming.enabled: false`（流式输出关闭）——投递确认路径
不走流式 consumer 时，`_stream_confirmed_final_delivery`（run.py:25118）的
`final_response_sent` 标志可能一直不置位，会话 busy 状态释放依赖非流式路径的确认。
排查「final stream delivery not confirmed 为什么 10+ 分钟不释放」时，把
`streaming.enabled` 也纳入检查项：`false` 时该日志出现频率更高、busy 挂得更久。

## 「之前关掉过的心跳检查」——gateway 心跳/检查类机制全景（2026-08-07）

用户问「关掉过的心跳检是？」时，先盘清楚本机存在哪些心跳/检查类机制，
别把不同机制混为一谈。五层：

| 机制 | 位置/默认 | 可关？ | 说明 |
|---|---|---|---|
| gateway loop heartbeat | `state/gateway.heartbeat`（每 30s 重写，`loop_heartbeat_forever` run.py:11401） | 否（内部） | loop 冻结则文件 mtime 停更，供外部监控判断卡死 |
| watchdog 日志新鲜度 | `scripts/gateway_watchdog.py` `STALE_LOG_MINUTES=10`（计划任务每 5 分钟） | 否（自愈用） | gateway.log mtime 超 10 分钟 = 疑似卡死 → 拉起+告警 |
| gateway 空闲缩容 scale_to_zero | `config.yaml` `gateway.scale_to_zero.idle_timeout_minutes: 5` | 可（调大/移除） | 空闲 5 分钟休眠，恢复时需重新 dial |
| Hindsight daemon 空闲检查 | `hindsight/config.json` `idle_timeout: 300` | 可（调大） | 空闲 5 分钟自动退出 → retain/recall 连接被拒（曾实测踩过） |
| 流式投递确认 | `streaming.enabled: false` | 可 | 非流式下投递确认路径不同，见上节 |
| **`/heartbeat` 会话定时提醒** | `hermes_cli/heartbeat.py`（`_handle_heartbeat_command` cli_commands_mixin.py:2371），存 state_meta `heartbeat:<session_id>` | 可（`/heartbeat clear\|pause`） | 会话级 recurring 指令（如 `/heartbeat every 10m 检查部署`），空闲时按周期注入成用户轮。**本机实测从未使用**（state_meta 0 条 heartbeat 记录）——用户说「关过心跳」时先查这里 |
| **auto-continue 断线自动继续** | `tui_gateway/turn_marker.py` + `desktop/interrupted_turns.json`；`desktop.auto_continue` 配置（默认 enabled，freshness 15min、max_attempts 2） | 可（`desktop.auto_continue.enabled: false`） | turn 开始时写标记、正常结束清除、**进程死亡残留**；恢复后自动重发中断的提示。⚠️ 标记文件里出现**当前会话** ≠ 异常——是 turn 进行中的正常记录（`attempts: 0` + started_at 是刚才），别误判为残留 |
| **cron ticker heartbeat** | `cron/ticker_heartbeat`（时间戳文件） | 否（内部） | cron 调度器存活心跳，mtime 新鲜 = 调度器在跑；`python -c` 解析时间戳对比当前时间 |

另外两条已有的心跳类条目（SKILL.md 正文）：
- **Hermes 通知层心跳**：「⏳ Working — N min」——`agent.gateway_notify_interval`（默认 180s），可 `set 0` 关闭
- **飞书协议层 ping**：lark_oapi SDK `_ping_loop` 每 120s WebSocket ping frame——**不可关**（SDK 强制）

用户说「关掉过的心跳检」通常是：①`gateway_notify_interval` 心跳通知（确实可关、可能已关）；②`/heartbeat` 会话定时提醒（名字最像「心跳检查」，本机从未使用过，`/heartbeat status` 秒查）；③auto-continue 断线自动继续（`desktop/auto_continue`）；④`scale_to_zero` 空闲缩容；⑤Hindsight `idle_timeout`。先 `grep -n "heartbeat\|scale_to_zero\|idle_timeout\|notify_interval" config.yaml`、`hindsight/config.json`、`state_meta`（`/heartbeat` 记录）对照现状，再回答「关没关过」——**大多数情况结论是「没关过，只是默认状态看着像关了」**。

## 决策建议（按用户偏好「最小必要实现」）

- 只想去掉噪音 → `display.busy_ack_enabled: false`（彻底静默，消息照常处理）
- 想保护当前任务不被打断 → `busy_input_mode: queue`（换「⏳ Queued」提示，不是去掉）
- 点赞触发 agent 浪费 token → 属 Hermes 源码行为，需改 adapter reaction 路由（点赞不进 `_handle_message_with_guards`），改代码要重启 gateway 且会被 `hermes update` 覆盖（见 feishu-comment-pipeline.md 的升级覆盖文件清单）
