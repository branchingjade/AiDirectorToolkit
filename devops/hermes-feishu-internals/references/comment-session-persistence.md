# 评论会话持久化设计（2026-09-03 实装）

> 来源：飞书三渠道健康度诊断 + 评论侧边栏"会话没给全"修复。
> 代码位置：`hermes-agent/plugins/platforms/feishu/feishu_comment.py:_load_persisted_session / _persist_session / _save_session_history`

## 1. 旧机制的根因（已弃）

2026-08-10 之前的实现：

- 评论会话只存 `Obsidian Vault/_hermes/评论会话/comment_<token>_<oid>.json`（URL 编码文件名）
- 内存缓存 `_session_cache` 字典（TTL 1h）— gateway 重启 = 缓存清零 = 评论上下文全丢
- **完全没写 `state.db`**
- 结果：桌面侧边栏「飞书评论」平台按 `source='comment'` 过滤 sessions 表，**永远 0 条**——用户说"会话没给全"的根因

**为什么不写 state.db**：feishu_comment.py 是独立 AIAgent（`quiet_mode=True`），从设计之初就与聊天 agent 数据管线隔离。但侧边栏 / 健康检查 / 数据分析**全部**都查 state.db——这种隔离直接导致**评论会话在 Hermes 体系内不可见**。

## 2. 新机制（双写 state.db）

每次 `_save_session_history(key, messages, user_id='', doc_title='')` 触发：

### 2.1 内存缓存

```python
with _session_cache_lock:
    _session_cache[key] = {"messages": cleaned, "last_access": now}
```

保留 1h（`_SESSION_TTL_S=3600`），缓存命中走这里（速度）。

### 2.2 持久化到 state.db（双表）

**messages 表**：

```sql
DELETE FROM messages WHERE session_id = ? AND active = 1
INSERT INTO messages (session_id, role, content, timestamp, active, compacted)
VALUES (?, ?, ?, ?, 1, 0)
```

- 删旧 + 重写（不增量），保证消息数与缓存一致
- `active=1 AND compacted=0` 排除已压缩/失效行
- 只保留 `role IN ('user', 'assistant')`（system/tool 提示词不入库）
- `_SESSION_MAX_MESSAGES=50` 截断

**sessions 表**（UPSERT，幂等）：

```sql
INSERT INTO sessions
  (id, source, session_key, title, started_at, ended_at,
   message_count, user_id, archived, hidden, pinned,
   rewind_count, compression_fallback_streak,
   compression_ineffective_count,
   last_activity_at, last_activity_description)
VALUES (?, 'comment', ?, ?, ?, NULL, ?, ?, 0, 0, 0, 0, 0, 0, ?, 'comment session updated')
ON CONFLICT(id) DO UPDATE SET
  message_count = excluded.message_count,
  last_activity_at = excluded.last_activity_at,
  last_activity_description = excluded.last_activity_description,
  ended_at = NULL,
  user_id = COALESCE(NULLIF(excluded.user_id, ''), sessions.user_id)
```

关键设计点：

- **id = session_key**（如 `comment-doc:docx:K5d3d03...`）——避开与时间生成 ID 冲突
- **`source='comment'`**——这是侧边栏「飞书评论」平台的过滤键（不是 `feishu`）
- **`title` 字段有 UNIQUE 索引**（`idx_sessions_title_unique`）——必须用稳定的 doc_title 或 file_token 截断，**不能**用动态生成的"用户问 X / bot 答 Y"之类（会撞 unique 失败）
- **`started_at` 用 `min(timestamp)`**——但通过 `ON CONFLICT DO UPDATE` 不覆盖保留**首次**值
- **`user_id` 用 `COALESCE(NULLIF(excluded.user_id, ''), sessions.user_id)`**——首次写入有 user_id 则用，否则保留旧值（避免后续空 user_id 把首次值清空）
- **`ended_at = NULL`**——不写结束时间，活跃评论会话始终是 open 状态

## 3. 懒加载（缓存未命中时回填）

```python
def _load_session_history(key):
    # 1) 优先内存缓存
    if entry and now - entry['last_access'] <= _SESSION_TTL_S:
        return entry['messages']
    # 2) 缓存未命中或过期 → 查 db
    persisted = _load_persisted_session(key)
    if persisted:
        _session_cache[key] = {"messages": persisted, "last_access": now}  # 回填
    return persisted
```

gateway 重启后第一次评论事件触发：缓存空 → db 命中 → 回填到内存——**用户感知不到重启**。

## 4. 透传 user_id / doc_title

`handle_drive_comment_event` 已经能拿到 `from_open_id`（adapter 反查）和 `doc_title`（`query_document_meta` 返回）。透传链：

```
handle_drive_comment_event(file_type, file_token, from_open_id, doc_title, ...)
  → functools.partial(_run_comment_agent, user_id=from_open_id, doc_title=doc_title)
  → _run_comment_agent(prompt, client, session_key, *, user_id, doc_title)
  → _save_session_history(session_key, new_messages, user_id=user_id, doc_title=doc_title)
  → _persist_session(key, cleaned, user_id=user_id, doc_title=doc_title)
  → UPSERT 到 sessions 表（含 user_id='ou_xxx', title='《伏妖记》'）
```

`run_in_executor` 不接受 kwargs，所以用 `functools.partial` 提前绑定。

## 5. 实施验证（2026-09-03 生产实测）

5/5 全部通过（在真实 `C:/Users/HMSJ/AppData/Local/hermes/state.db` 上跑）：

| # | 用例 | 结果 |
|---|---|---|
| 1 | save → sessions + messages 双写 | sessions 行 id=`comment-doc:docx:PROD_TEST_001` source=`comment` title=`《伏妖记》` user_id=`ou_test123` message_count=2；messages 2 行 |
| 2 | 再次保存（追加 2 条） | sessions.message_count=4（UPSERT 不重复）；messages 4 行（删旧+重写） |
| 3 | 第二次写不更新 started_at | `started_at` 保持首次值（`ON CONFLICT DO UPDATE` 不覆盖该字段） |
| 4 | 不同 doc 不同 title 互不冲突 | sessions 表 2 条 comment 行；title 走 UNIQUE 索引 OK |
| 5 | 删 sessions 行后重建走 INSERT | 重建后正常（不走 ON CONFLICT 路径） |

## 6. 故障诊断清单

| 症状 | 检查点 |
|---|---|
| 侧边栏「飞书评论」平台无新会话 | `sqlite3 state.db "SELECT * FROM sessions WHERE source='comment'"` 是否有新行；`hermes config show` 看 source 值是否含 `comment` |
| 重复 message | `_persist_session` 必须 `DELETE FROM messages` 再重写，**不能 INSERT-only**——否则多次 save 会累积 |
| title UNIQUE 失败 | 检查 doc_title 是否每次变化（不变化才能用 UNIQUE），或用 `INSERT OR IGNORE` 替代 |
| gateway 重启后评论上下文丢 | 检查 `_load_persisted_session` 是否被调用，sqlite3.connect 是否成功（db 路径通过 `_state_db_path()` 读 HERMES_HOME） |
| user_id 为空 | `from_open_id` 是否从事件 payload 提取（看 `feishu_comment.py:147` 解析路径），`functools.partial` 绑定是否正确 |

## 7. 不再需要的事

- ❌ `Obsidian Vault/_hermes/评论会话/comment_*.json` 文件存储（旧实现）
- ❌ URL 编码文件名（`pct_3A`...）
- ❌ `feishu-collab-health.py` 读 JSON 目录的口径（已改读 state.db messages 表）
- ❌ channel-sessions 插件单独渲染评论视图的 workaround（侧边栏直接 source='comment' 过滤即可）

**保留**：`Obsidian Vault/_hermes/评论会话/archive/` 历史归档 23 个 JSON 文件——TTL 1h 的旧实现留的历史记录，**保留原文证据**。
