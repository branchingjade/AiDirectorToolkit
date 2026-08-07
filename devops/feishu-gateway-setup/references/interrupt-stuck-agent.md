# Agent 卡死导致 Interrupt 循环

## 现象

飞书群中每条消息都收到：
```
⚡ Interrupting current task (14 min elapsed, iteration 1/60). I'll respond to your message shortly.
```
但机器人永远不会回复。用户连续发多条消息，每条都触发同样的打断回复。

## 根因

### 打断机制工作流程

1. 用户发新消息 → `base.py:handle_message()` 检测到 `session_key in _active_sessions`
2. 调用 `_handle_active_session_busy_message()`（run.py:5362）
3. 存储消息：`_queue_or_replace_pending_event(session_key, event)` → 存入 `adapter._pending_messages`
4. 打断 agent：`running_agent.interrupt(event.text)` → 设 `_interrupt_requested = True`
5. 发送确认："⚡ Interrupting current task..."
6. 返回 True（消息已处理）

Agent 完成后（run.py:19934-19960）：
- `_dequeue_pending_event()` 取出排队消息
- 递归调用 `_run_agent()` 处理下一条消息

### 卡死原因

`interrupt()` 只是设了个软标志位：
```python
# agent_init.py:584
agent._interrupt_requested = False
agent._interrupt_message = None
```

Agent 在下一个检查点才会检查这个标志。如果 agent 卡在 blocking 操作上（API 超时、流式响应无返回），标志永远不被检查 → agent 永远不结束 → 排队消息永远不被处理。

### 典型触发场景

- MiMo API 流式响应超时（"waiting for stream response (150s, no chunks yet)"）
- 工具调用卡死（terminal 命令无返回、外部 API 超时）
- 网络中断导致 HTTP 连接 hang
- 音频文件处理（STT 转录）卡死

## 诊断方法

1. 群里连续发 2 条消息，如果都收到"⚡ Interrupting"，说明 agent 卡死
2. 检查消息记录中的 `iteration` 和 `elapsed` 时间是否异常增长
3. 如果 `iteration` 停在 1/60 不变，说明 agent 卡在第一次 API 调用

## 修复

### 立即修复

**第一选择：群里发 `/stop`**
- `/stop` 走 `should_bypass_active_session` 路径，直接取消卡死的 agent
- 清理 `_active_sessions` 和 `_pending_messages`
- 下一条消息可以正常处理

**第二选择：重启 Gateway（当 `/stop` 无效时）**

如果 `/stop` 也无响应（gateway 进程本身卡死），需要强制重启：

```bash
# 查找 gateway PID
hermes gateway status

# 强制杀进程（hermes gateway stop 可能超时）
powershell.exe -Command "Stop-Process -Id <PID> -Force"

# 等 3 秒后重启
hermes gateway start
```

⚠️ `hermes gateway stop` 和 `hermes gateway restart` 在 gateway 卡死时可能超时（30s）。直接用 PowerShell 杀进程更可靠。

### 长期缓解

1. **减小 gateway_timeout**：
   ```bash
   hermes config set agent.gateway_timeout 300  # 5分钟
   ```
   超时后 agent 自动终止，不会永远卡死。

2. **在 channel_prompt 中加超时指引**：
   ```
   如果某个操作超过 60 秒无响应，主动放弃并回复错误信息，不要无限等待。
   ```

3. **使用更稳定的模型**：MiMo API 偶尔超时，考虑 fallback 到 deepseek-v4-flash。

## 话题模式的故障隔离

飞书话题模式下，每个话题有独立的 session key：
```
agent:main:feishu:group:{chat_id}:{thread_id}
```

好处：
- 一个话题卡死不影响其他话题
- `/stop` 只终止当前话题的 agent，不影响其他话题
- 不同话题的上下文完全隔离

对比普通群聊（`group_sessions_per_user: true`）：
- session key 为 `feishu:group:oc_xxx:user_id`
- 该用户的所有消息共享一个 session
- 卡死后该用户所有消息都被打断

## 代码路径参考

| 组件 | 文件 | 行号 |
|------|------|------|
| busy handler 入口 | gateway/run.py | 5362 |
| 消息排队 | gateway/run.py | 5580 |
| interrupt 调用 | gateway/run.py | 5589-5593 |
| 打断确认消息 | gateway/run.py | 5694-5697 |
| agent 完成后 dequeue | gateway/run.py | 19942-19943 |
| 排队消息处理 | gateway/run.py | 20050-20224 |
| interrupt 标志位 | agent/agent_init.py | 584-585 |
| /stop 命令绕过 | gateway/platforms/base.py | 4689-4703 |
| session key 构建 | gateway/session.py | 871-959 |

## 更新依赖包（必须用 venv 的 pip）

Hermes gateway 使用 venv Python 3.11，不是系统 Python 3.12。直接 `pip install` 会装到系统 Python，gateway 看不到。

```bash
# 正确：用 venv 的 python.exe -m pip
/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pip install <package>==<version>

# 验证安装到正确环境
/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "import importlib.metadata; print(importlib.metadata.version('<package>'))"
```

安装后必须重启 gateway：`powershell.exe -Command "Stop-Process -Id <PID> -Force"` 然后 `hermes gateway start`。

## 相关配置

```yaml
display:
  busy_input_mode: interrupt  # 默认值，可改为 queue 或 steer
agent:
  gateway_timeout: 1800       # 默认 30 分钟，建议减小
```

- `interrupt`：新消息打断当前任务（默认）
- `queue`：新消息排队等待当前任务完成
- `steer`：新消息注入到当前运行中
