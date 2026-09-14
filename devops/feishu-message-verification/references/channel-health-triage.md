# 飞书渠道健康度三渠道诊断方法学（2026-09-03 实战）

**适用范围**：当用户报告"飞书协作挂掉/某个渠道不工作"时，按本方法学三渠道（DM / group / drive.comment）逐项定位根因。**核心原则**：脚本输出永远不是事实，**三角验证**才是事实——state.db + gateway.log + adapter 源码，三处对齐才能下结论。

## 一、三渠道数据在哪（事实基准，2026-09-03 实证）

| 渠道 | state.db sessions 表 | gateway.log | 备注 |
|---|---|---|---|
| **DM（私聊）** | `chat_type='dm'` 或 session_key 含 `:dm:` | `[Feishu] Inbound dm message received` | ✓ 完整记录 |
| **group（群聊）** | `chat_type='group'` 或 session_key 含 `:group:` | `[Feishu-DIAG] ADMIT REJECTED` / 无 inbound | ⚠️ 被 require_mention 策略拦掉时**只在日志出现 Inbound candidate 但不写 sessions 表** |
| **drive.comment（文档评论）** | **0 条**（comment agent 是独立 AIAgent，sessions 表完全不写） | `[Feishu-Comment] ========== handle_drive_comment_event START/END` + `Session saved: comment-doc:docx:<token> (<N> messages)` | ⚠️ "Session saved" 看着像持久化，实际只存**进程内存 `_session_cache` 字典**（TTL 1h，gateway 重启清零）——见第三节 |

**脚本口径错误样本（避免重蹈）**：
- `scripts/feishu-collab-health.py` 查 `_hermes/评论会话/comment_*.json` 文件——但**当前实现根本没写这些文件**！日志里"Session saved"指的是 `_session_cache` 内存 dict，不是磁盘文件。脚本看到 0 文件 → 误报"评论渠道无活动"。
- 同脚本查 `comment_*.json` 文件 mtime 也是死指标——历史归档是 bot 自己一次性生成的回溯样本，不是实时数据。

## 二、三渠道诊断指纹对照表

| 渠道 | 看起来挂 | 真因分类 | 日志指纹 | state.db 表现 | 修复路径 |
|---|---|---|---|---|---|
| DM | DM=0 消息 | DM 正常但没人发 DM | 无 inbound 日志 | sessions 表无 DM 行 | 无需修——等待 DM 流量 |
| DM | DM 活但群死 | 根因 5：SDK dispatcher bug | 完全无 `Received raw message` | sessions 表有 DM 无 group | 升级 lark-oapi 或 webhook 回退 |
| group | 群=0 消息 | **根因 6（2026-09-03 新增）**：config require_mention 误伤 | `[Feishu-DIAG] ADMIT REJECTED: reason=group_policy_rejected mentions=[]` | sessions 表无 group 行 | `group_rules[oc_xxx].require_mention: false` |
| group | 群=0 消息 | 群里没人说话 | 无 inbound candidate | sessions 表无 group 行 | 无需修——等群流量 |
| drive.comment | 活跃线程 mtime 停在 8/27 | 评论渠道看似死 | `handle_drive_comment_event START/END` 持续出现但 state.db 0 条 | state.db 无 comment session | **不是死！是日志"Session saved" 和磁盘持久化是两件事**（见第三节） |
| drive.comment | 评论 @ bot 无回复 | 意图路由漏词 / 软提示跳过 / cold-shoulder | `Intent detected as REPLY` + `NO_REPLY` 或静默 | — | 看 hermes-feishu-internals §3.6/3.7/3.8 |

## 三、评论会话"挂"的真相（最容易误判）

**代码真相**（`hermes-agent/plugins/platforms/feishu/feishu_comment.py:1000-1044`）：

```python
_SESSION_MAX_MESSAGES = 50   # 内存里只留 50 条
_SESSION_TTL_S = 3600        # 1 小时不活动就 _session_cache.pop(key)

_session_cache_lock = threading.Lock()
_session_cache: Dict[str, Dict] = {}  # key -> {"messages": [...], "last_access": float}

def _save_session_history(key, messages):
    cleaned = [m for m in messages if m.get("role") in {"user","assistant"} and m.get("content")]
    if len(cleaned) > _SESSION_MAX_MESSAGES:
        cleaned = cleaned[-_SESSION_MAX_MESSAGES:]
    with _session_cache_lock:
        _session_cache[key] = {"messages": cleaned, "last_access": _time.time()}
        logger.info("[Feishu-Comment] Session saved: %s (%d messages)", key, len(cleaned))
```

**关键事实**：
1. "Session saved" 日志只表示**写入内存 dict**，**不代表落盘**
2. **零持久化层**：没有 sqlite 写入、没有 json 文件落盘
3. `_SESSION_TTL_S = 3600` = 1 小时无活动自动 `del _session_cache[key]`4. **gateway 重启 = 缓存清零 = 评论历史全丢**
5. `state.db sessions` 表里 0 条 comment session（独立 AIAgent 数据管线隔离）

**与 SKILL 描述的矛盾**：
- `hermes-feishu-internals` §3 写「评论会话磁盘持久化（`Obsidian Vault/_hermes/评论会话/`，重启不丢）」
- `feishu-comment-collab` §会话模型写「磁盘持久化：`Obsidian Vault/_hermes/评论会话/<percent-encoded-key>.json`」
- **两个 skill 都描述了一个当前实现里不存在的行为**——属于历史遗物。Obsidian 目录里确实有 `comment_*.json` 文件，但**那是归档/手写样本，不是 `_save_session_history` 写的**。

**正确修复方向**（任选其一）：
- **A. 真持久化**：把 `_session_cache` 改成 `sqlite3` 写入到 state.db 的 sessions 表，用 session_key=`comment-doc:<file_type>:<file_token>` 作为主键——和聊天会话共存同一张表。`_save_session_history` 改成 upsert；`_load_session_history` 改成 query。**副作用**：state.db 会膨胀，需加 sessions 表 `kind='comment'` 列区分 + 定期 archive。
- **B. 显式声明不持久化**：把 SKILL 描述改成「会话仅内存，1h TTL，gateway 重启丢失」，并在文档评论 @bot 时附 user 提示「上下文仅保留 1 小时，重启后请重新 @bot」。
- **C. Obsidian 文件持久化**：恢复 `_save_session_history` 写 `Obsidian Vault/_hermes/评论会话/<percent-encoded-key>.json`（这是 2026-08-07 之前的行为，但**当前实现已经没有这段代码**——可能历史改动时被精简掉了）。

**诊断铁律**：看到"评论渠道 0 活跃"先 grep gateway.log：
```bash
grep "handle_drive_comment_event START" logs/gateway.log | wc -l   # 看事件有没有到
grep "Session saved" logs/gateway.log | tail -5                    # 看 _session_cache 写入
```
有 START 有 Session saved 但 state.db 0 条 = **配置问题（持久化层缺失），** **不是渠道挂**。

## 四、三角验证最小命令集（诊断脚本）

任何渠道"挂"投诉，先跑这三段（秒级完成）：

```bash
# 1. state.db 三角查三个渠道
python -c \"
import sqlite3, datetime
db = sqlite3.connect('C:/Users/HMSJ/AppData/Local/hermes/state.db')
cur = db.cursor()
since = datetime.datetime.now().timestamp() - 48*3600
print('=== DM 近 48h ===')
for r in cur.execute('SELECT user_id, COUNT(*), SUM(message_count) FROM sessions WHERE chat_type=\\\"dm\\\" AND started_at > ? GROUP BY user_id', (since,)):
    print(f'  {r[0][:25]:25s} | {r[1]} 会话 | {r[2] or 0} 消息')
print('=== group 近 48h ===')
for r in cur.execute('SELECT user_id, COUNT(*), SUM(message_count) FROM sessions WHERE chat_type=\\\"group\\\" AND started_at > ? GROUP BY user_id', (since,)):
    print(f'  {r[0][:25]:25s} | {r[1]} 会话 | {r[2] or 0} 消息')
print('=== comment 近 48h（应为 0）===')
for r in cur.execute('SELECT COUNT(*) FROM sessions WHERE session_key LIKE \\\"comment-doc:%\\\" AND started_at > ?', (since,)):
    print(f'  comment sessions: {r[0]} (期望 0——独立 AIAgent 不写 state.db)')
\"

# 2. gateway.log 三层 grep
echo '=== Inbound DM ==='; grep "Inbound dm message received" logs/gateway.log | tail -3
echo '=== Inbound GROUP (期望空或 ADMIT REJECTED) ==='; grep -E "Inbound group message|ADMIT REJECTED.*group_policy_rejected" logs/gateway.log | tail -5
echo '=== drive.comment START（评论事件有没有到）==='; grep "handle_drive_comment_event START" logs/gateway.log | wc -l
echo '=== drive.comment Session saved（缓存写入）==='; grep "Session saved:" logs/gateway.log | tail -3

# 3. config.yaml 渠道策略速查
echo '=== feishu 渠道策略 ==='; python -c \"
import yaml
cfg = yaml.safe_load(open('config.yaml', encoding='utf-8'))
fs = cfg.get('platforms', {}).get('feishu', {})
print(f'group_policy: {fs.get(\\\"group_policy\\\", \\\"(unset)\\\")}')
print(f'require_mention (default): {fs.get(\\\"require_mention\\\", \\\"(unset)\\\")}')
print(f'group_rules: {list(fs.get(\\\"group_rules\\\", {}).keys())}')
for chat_id, rule in fs.get('group_rules', {}).items():
    print(f'  {chat_id[:25]:25s} → require_mention={rule.get(\\\"require_mention\\\", \\\"(inherit)\\\")}')
\"
```

**三段输出对照 SKILL 第六节根因 1-6 + 本节根因三**，下结论。

## 五、为什么不直接相信 `feishu-collab-health.py` 输出

`scripts/feishu-collab-health.py` 覆盖：①活跃度（IM + 评论文件 mtime）②路由覆盖 ③画像覆盖 ④画像使用率 ⑤评论线程文件清单。**问题清单**（2026-09-03 实战）：

| 指标 | 现状 | 问题 |
|---|---|---|
| 【1】成员活跃度（IM + 评论） | 用 `state.db sessions` 表 + `_hermes/评论会话/comment_*.json` 文件 mtime | 评论文件 mtime = 死指标（实际数据在内存） |
| 【1】"活跃"判定 | `i_cnt + c_cnt` 任一非零就算活跃 | 杨璇 IM=0 但评论=1 算"活跃"——口径偏宽 |
| 【3b】画像使用率 | grep gateway.log `Profile injected for <名>` | 48h 内零命中——**确认日志格式已变**，需去 `hermes-agent/gateway/run.py` 核对当前 tag |
| 【5】评论线程 | 读 `comment_*.json` 文件 | 0 文件即报"无活跃评论线程"——但实际评论在内存 cache 里 + log 里 9/3 还在跑——**完全误报** |

**结论**：脚本能跑、输出结构好看，但**指标定义本身有偏差**。用户问"飞书协作建康度"时**不能直接发脚本输出**，必须按本节三角验证手动跑一遍 state.db + log + config，**把脚本输出当辅助**。

## 六、修复建议优先级（用户拍板后再动手）

| 优先级 | 修复 | 工作量 | 影响 |
|---|---|---|---|
| 🔴 P0 | 评论会话持久化（第三节方案 A 或 C） | 中等：改 `_save_session_history` + `_load_session_history` + 加 sessions 表 `kind` 列 | gateway 重启不再丢评论上下文；评论会话能跨重启累积；state.db 可观测评论渠道真实活跃度 |
| 🔴 P0 | 修 `feishu-collab-health.py` 指标定义（不再读 `_hermes/评论会话/` 文件，改读 state.db sessions 表 `chat_type IN ('dm','group')` + log grep `handle_drive_comment_event START` 数评论事件） | 小：~80 行 Python 改动 | 健康检查不再误报；可放心作为 cron 投递 |
| 🟡 P1 | 群聊 `require_mention` 误伤（按用户偏好给目标群 `group_rules` 加 `require_mention: false`） | 1 行 config 改动 | 群聊渠道恢复；MEMORY 同步改协作预期 |
| 🟢 P2 | 画像注入日志格式核对（gate way/run.py 当前 tag 是啥、为什么 48h 零命中） | 查代码 + 加 INFO log | 画像使用率指标可重新可信 |

**决策建议**：用户在 2026-09-03 拍板"诊"诊断，没说要不要立刻修——**先把诊断结论给用户，等拍板再动代码**。