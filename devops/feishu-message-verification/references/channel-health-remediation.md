# 飞书三渠道健康度修复落地（2026-09-03 实战）

**何时读**：本节 `references/channel-health-triage.md` 诊断完三个渠道的根因后，按本文件落地修复。**本章是诊断→修复的桥梁**——不是"诊断方法学"（那个在 triage 文档），是"代码改动 + 验证步骤"。

**与 triage 文档的对应**：

| triage 优先级 | 本文件对应修复 |
|---|---|
| 🔴 P0 评论会话持久化 | 修复 2（feishu_comment.py 双写 state.db） |
| 🟡 P1 群聊 `require_mention` 误伤 | 修复 1（config.yaml group_rules） |
| 🟢 P2 feishu-collab-health.py 指标定义偏差 | 修复 3（脚本改口径） |

---

## 修复 1：群聊 require_mention 关闭（config 改动）

**根因**：全局 `platforms.feishu.require_mention: true` + 已知活跃群不在 `group_rules` 里独立声明 → 走默认 → 用户不 @bot 群消息全被 `group_policy_rejected`。

**最小修复原则**：
- 不全局关 `require_mention: false`（避免未知群被乱触达）
- 只给已知活跃且**有人用**的群加 `group_rules[oc_xxx].require_mention: false`
- 冷群（如 47 天没说话的 `oc_984...`）保持默认 `require_mention: true`

**改法**（必须用 `hermes config set` CLI，禁 `patch`/`write_file` 改 config.yaml）：

```bash
# 给开工群加白名单
hermes config set platforms.feishu.group_rules.oc_685820a739882df67954e0923ec9ab73.require_mention false --force
# 给另一个活跃群加白名单
hermes config set platforms.feishu.group_rules.oc_b7396f845a84a3aebdb1bf38c872e37a.require_mention false --force
```

**三件套验证**：
1. `hermes config get platforms.feishu.group_rules` 看到两条新记录
2. `hermes config check` 无错
3. gateway 重启后**只对这两个群生效**——其他群仍走默认

**配置改动铁律**：改 Hermes `config.yaml` 必须走 `hermes config set` CLI——MEMORY 实战教训：`patch`/`write_file` 工具会被 Hermes 拒（"Refusing to write to Hermes config file"）。

---

## 修复 2：评论 session 持久化（核心修复）

**根因**（详见 triage 第三节）：`_save_session_history` 只写进程内存 `_session_cache` dict，`_SESSION_TTL_S=3600` 自动过期，**gateway 重启即清零**。

**修复策略**——双写：内存缓存 + state.db messages 表。

### 2.1 代码改动（`hermes-agent/plugins/platforms/feishu/feishu_comment.py`）

**新增 imports**（放在文件顶部 import 块）：
```python
import os
import sqlite3
import threading as _threading
```

**新增持久化层**（紧贴 `_session_cache` 定义后）：
```python
_persist_lock = _threading.Lock()
_PERSIST_TTL_S = 7 * 24 * 3600  # DB 历史保留 7 天


def _state_db_path() -> str:
    home = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
    return os.path.join(home, "state.db")


def _load_persisted_session(key: str) -> List[Dict[str, Any]]:
    db_path = _state_db_path()
    if not os.path.exists(db_path):
        return []
    cutoff = _time.time() - _PERSIST_TTL_S
    try:
        with _persist_lock:
            conn = sqlite3.connect(db_path, timeout=5)
            try:
                rows = conn.execute(
                    """SELECT role, content, timestamp FROM messages
                       WHERE session_id = ? AND timestamp > ?
                         AND role IN ('user', 'assistant')
                         AND active = 1 AND compacted = 0
                       ORDER BY timestamp ASC""",
                    (key, cutoff),
                ).fetchall()
            finally:
                conn.close()
    except sqlite3.Error as e:
        logger.warning("[Feishu-Comment] persist read failed for %s: %s", key, e)
        return []
    return [{"role": r, "content": c, "timestamp": t} for r, c, t in rows if c]


def _persist_session(key: str, messages: List[Dict[str, Any]])]) -> None:
    """删旧行 + 按当前消息列表重写（消息列表本身已按 _SESSION_MAX_MESSAGES 裁剪）。"""
    db_path = _state_db_path()
    if not os.path.exists(db_path):
        return
    rows = []
    now_ts = _time.time()
    for m in messages:
        role = m.get("role")
        content = m.get("content")
        if role not in {"user", "assistant"} or not content:
            continue
        ts = float(m.get("timestamp") or now_ts)
        rows.append((key, role, content, ts))
    if not rows:
        return
    try:
        with _persist_lock:
            conn = sqlite3.connect(db_path, timeout=5)
            try:
                conn.execute("BEGIN")
                conn.execute("DELETE FROM messages WHERE session_id = ? AND active = 1", (key,))
                conn.executemany(
                    """INSERT INTO messages
                         (session_id, role, content, timestamp, active, compacted)
                       VALUES (?, ?, ?, ?, 1, 0)""",
                    rows,
                )
                conn.commit()
            finally:
                conn.close()
    except sqlite3.Error as e:
        logger.warning("[Feishu-Comment] persist write failed for %s: %s", key, e)
```

**改造 `_load_session_history`**（缓存 miss 时回退 db）：
```python
def _load_session_history(key: str) -> List[Dict[str, Any]]:
    now = _time.time()
    with _session_cache_lock:
        entry = _session_cache.get(key)
        if entry is not None:
            if now - entry["last_access"] > _SESSION_TTL_S:
                del _session_cache[key]
                logger.info("[Feishu-Comment] Session expired (cache): %s", key)
                entry = None
            else:
                entry["last_access"] = now
                return list(entry["messages"])
    # Cache miss → 回退 db
    persisted = _load_persisted_session(key)
    if persisted:
        with _session_cache_lock:
            _session_cache[key] = {"messages": persisted, "last_access": now}
        logger.info(
            "[Feishu-Comment] Session loaded from db: %s (%d messages)",
            key, len(persisted),
        )
    return persisted
```

**改造 `_save_session_history`**（写完内存后调 persist）：
```python
def _save_session_history(key: str, messages: List[Dict[str, Any]]) -> None:
    cleaned = [m for m in messages if m.get("role") in {"user","assistant"} and m.get("content")]
    if len(cleaned) > _SESSION_MAX_MESSAGES:
        cleaned = cleaned[-_SESSION_MAX_MESSAGES:]
    now = _time.time()
    with _session_cache_lock:
        _session_cache[key] = {"messages": cleaned, "last_access": now}
        logger.info("[Feishu-Comment] Session saved (cache): %s (%d messages)", key, len(cleaned))
    # 持久化：失败不阻断（评论主链路不能因 db 故障而失败）
    _persist_session(key, cleaned)
```

### 2.2 关键设计取舍

- **删旧行 + 重写 vs 增量 upsert**：选重写。因为 `_SESSION_MAX_MESSAGES=50` 截断在 save 时已完成，重写简单无重复风险；增量 upsert 要算差集更复杂。
- **messages 表 vs 新建独立表**：选 messages 表。复用已有 schema（role/content/timestamp/active/compacted 字段全有），无 schema migration 风险。**代价**：messages 表会增长——`_PERSIST_TTL_S=7 天` 是兜底，防止长期膨胀。
- **失败不阻断**：persist 写失败只 log warning，不抛异常。理由：评论主链路不能让 db 故障拖垮，最多丢最近一次持久化（下次 event 重新写入）。
- **不写 active=0 软删除**：直接 DELETE，不用 active=0。原因是 session 是原子替换，旧的 active=1 行直接 DELETE 比 UPDATE 更干净。

### 2.3 单测（隔离环境）

写一个独立测试 `feishu_comment_persist_test.py` 验证 6 项：
1. save → 读一致（4 条消息对得上）
2. 清空 `_session_cache` → 懒加载恢复
3. 再次 save → 重写不重复（6 条不 8 条）
4. 超 `_SESSION_MAX_MESSAGES` 截断到 50
5. 7 天前的 key → TTL 过期不读
6. role 过滤（system/tool 不入库）

**测试代码骨架**（可直接跑）：
```python
import os, sys, tempfile, time
test_dir = tempfile.mkdtemp()
import sqlite3
conn = sqlite3.connect(os.path.join(test_dir, 'state.db'))
# 创建 messages 表（schema 与生产一致）
conn.executescript("""
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT,
    tool_call_id TEXT, tool_calls TEXT, tool_name TEXT,
    timestamp REAL NOT NULL, token_count INTEGER DEFAULT 0,
    finish_reason TEXT, reasoning TEXT, reasoning_content TEXT,
    reasoning_details TEXT, codex_reasoning_items TEXT,
    codex_message_items TEXT, platform_message_id TEXT,
    observed INTEGER DEFAULT 0, active INTEGER DEFAULT 1,
    compacted INTEGER DEFAULT 0, effect_disposition TEXT,
    api_content TEXT, display_kind TEXT, display_metadata TEXT,
    _compressed_summary INTEGER DEFAULT 0
);
CREATE INDEX idx_messages_session ON messages(session_id);
""")
conn.close()

os.environ['HERMES_HOME'] = test_dir

# 用 importlib 加载目标模块
import importlib.util
spec = importlib.util.spec_from_file_location(
    'fc',
    'C:/Users/HMSJ/AppData/Local/hermes/hermes-agent/plugins/platforms/feishu/feishu_comment.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# 然后跑 6 项断言...
```

### 2.4 生产实测（在真实 state.db 上）

测试通过隔离环境验证后，**必须在生产 state.db 上再跑一遍**：
- 构造一个 test key（如 `comment-doc:docx:test-prod-verify-N`）
- save → load → SQL 三件套
- 清 `_session_cache` → 再 load → 验证懒加载
- 清理测试数据（`DELETE FROM messages WHERE session_id = ?`）

### 2.5 gateway 重启 + 飞书 WS 验证

修复必须配合 gateway 重启让代码生效：
```bash
hermes gateway status  # 确认状态
hermes gateway run &   # 后台启动（按需；也可用 hermes gateway restart）
sleep 30
curl -s http://127.0.0.1:8644/health  # 期望 {"status": "ok"}
grep "Connected in websocket mode" logs/gateway.log | tail -1  # WS 连接成功
```

**端到端验证最可靠的方法**：
- 让 gateway 跑起来，等待真实飞书评论事件触发 → 日志里出现 `Session saved (cache)` + state.db messages 表对应 session_id 行数增加 → 真实持久化生效

---

## 修复 3：feishu-collab-health.py 改口径

**根因**：脚本三个指标定义与实际实现偏差（详见 triage 第五节）。

**最小修复**（保持脚本结构，只改数据源）：

### 3.1 `comment_activity` 改读 state.db messages

```python
def comment_activity(since_ts: float):
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute(
        """SELECT session_id, COUNT(*), MAX(timestamp)
           FROM messages
           WHERE session_id LIKE 'comment-doc:%'
             AND active = 1 AND compacted = 0
             AND role IN ('user', 'assistant')
           GROUP BY session_id""",
    )
    by_user, detail = {}, []
    for key, cnt, max_ts in cur.fetchall():
        # 从首条 user 消息 content 里抽 open_id
        cur.execute(
            """SELECT content FROM messages
               WHERE session_id = ? AND role = 'user'
               ORDER BY timestamp ASC LIMIT 1""",
            (key,),
        )
        row = cur.fetchone()
        oid = _extract_open_id(row[0] if row else "") or key
        cur_entry = by_user.get(oid, [0, 0.0])
        cur_entry[0] += 1
        cur_entry[1] = max(cur_entry[1], max_ts or 0)
        by_user[oid] = cur_entry
        if max_ts and max_ts >= since_ts:
            detail.append((key, cnt, max_ts))
    db.close()
    return by_user, detail
```

### 3.2 新增群聊维度

```python
def group_activity(since_ts: float):
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute(
        """SELECT session_key, COUNT(*), SUM(message_count), MAX(started_at)
           FROM sessions WHERE chat_type = 'group' AND started_at > ?
           GROUP BY session_key""",
        (since_ts,),
    )
    by_chat, detail = {}, []
    for sk, cnt, msg_sum, last_ts in cur.fetchall():
        chat_id = sk.split(":group:")[1].split(":")[0] if ":group:" in sk else ""
        if not chat_id:
            continue
        cur_entry = by_chat.get(chat_id, [0, 0, 0.0])
        cur_entry[0] += cnt
        cur_entry[1] += (msg_sum or 0)
        cur_entry[2] = max(cur_entry[2], last_ts or 0)
        by_chat[chat_id] = cur_entry
        detail.append((chat_id, cnt, (msg_sum or 0), last_ts))
    db.close()
    return by_chat, detail
```

### 3.3 新增 group_rules 白名单覆盖检查（自动报警）

```python
def group_whitelist_coverage() -> list:
    """已知活跃群必须在 group_rules 显式登记——否则走默认 require_mention 误伤。"""
    import yaml as _yaml
    try:
        with open(os.path.join(HERMES_HOME, 'config.yaml'), encoding='utf-8') as fh:
            cfg = _yaml.safe_load(fh) or {}
    except Exception:
        return []
    rules = ((cfg.get('platforms', {}) or {}).get('feishu', {}).get('group_rules', {}) or {})
    default_require = (
        (cfg.get('platforms', {}) or {}).get('feishu', {}).get('require_mention', True)
    )
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("SELECT DISTINCT session_key FROM sessions WHERE chat_type = 'group'")
    known_chats = set()
    for (sk,) in cur.fetchall():
        if sk and ":group:" in sk:
            known_chats.add(sk.split(":group:")[1].split(":")[0])
    db.close()
    return [(cid, default_require) for cid in sorted(known_chats) if cid not in rules]
```

### 3.4 main 输出段加群聊渠道

```python
# 5b. 群聊渠道明细 + 白名单覆盖
print("【5b】群聊渠道（按 chat_id）")
if grp_detail:
    for chat_id, sessions, msgs, last in grp_detail:
        ts = datetime.datetime.fromtimestamp(last).strftime("%m-%d %H:%M") if last else "?"
        print(f"  {chat_id} | {sessions} 会话 / {msgs} 消息 | 最后 {ts}")
else:
    print(f"  (近 {HOURS}h 无群聊活跃)")
print()
gaps = group_whitelist_coverage()
if gaps:
    print(f"  ⚠️ 已知活跃群未在 group_rules 显式登记（走全局默认 require_mention={gaps[0[1]}）：")
    for chat_id, default in gaps:
        print(f"    - {chat_id} (default={default})")
else:
    print("  ✓ 所有已知活跃群都已显式登记 group_rules")
```

### 3.5 跑通验证

```bash
cd /c/Users/HMSJ/AppData/Local/hermes
python scripts/feishu-collab-health.py 48
```

**预期输出变化**：
- 修复前：【5】评论线程 = "无活跃评论线程"（误报，因为查的是文件目录）
- 修复后：【5】评论线程 = "无活跃评论线程"（因为修复前没历史数据） + 【5b】群聊渠道 + 白名单覆盖检查

**实测口径校验**：跑通后必须 grep 三个数据源：
1. `state.db` 里 `SELECT COUNT(*) FROM messages WHERE session_id LIKE 'comment-doc:%'` 应 = 0（修复前没历史数据）
2. `logs/gateway.log` 里 `handle_drive_comment_event START` 数 = 当前活跃评论事件数
3. `config.yaml` 里 `group_rules` 应有 3 条记录（1 老 + 2 修复 1 加的白名单）

---

## 三件套验证铁律（每次修复后必跑）

参考同根元铁律「memory 写盘必须 grep 验证」、「patch/write_file 写入必须三件套验证」：

1. **mtime 变化**：`stat -c '%Y %n' <file>` 对比修改前后——确认磁盘真改
2. **grep 独有锚点**：在改后的文件里 grep 本次改动独有的字符串（如新函数名 `_persist_session`、新 config key `require_mention: false`）——确认改动真在
3. **AST 解析**：`python -c "import ast; ast.parse(open('<file>').read())"` ——确认 Python 语法没崩

**额外**（生产环境）：
- gateway 重启 + 飞书 WS 重连 + `/health` 返回 ok
- 真实业务事件触发一次（日志 + state.db 双验证）

---

## Pitfalls 速查

| 现象 | 根因 | 处理 |
|---|---|---|
| `hermes config set` 后 gateway 没生效 | 没重启 gateway | `hermes gateway restart`，WS 重连标志看 `Connected in websocket mode` |
| 评论修复后 state.db 还是 0 条 | 修复前评论事件没触发过 | 不算 bug——等真实评论事件即可 |
| `feishu-collab-health.py` 改后报 KeyError | 漏 `from typing import Dict, List, Tuple` | 加 typing imports |
| `_load_session_history` 第一次启动很慢 | 内存 cache 全 miss，全部回退 db | 正常，启动后稳定 |
| persist 写失败但 cache 写成功 | db 锁或权限问题 | log warning 即可，不影响本次评论回复 |
| `import threading as _threading` 引入后模块内还有 `import threading` 旧引用 | 1003 行有遗留 import | 删旧 import 行（功能不影响但易后人困惑） |
| gateway 反复 `exited UNCLEANLY (SIGKILL/OOM)` | 根因未明（看 `lifecycle_ledger` 警告） | 不在本次修复范围——单独排查 watchdog |
| gateway 不在运行时改 config 仍生效？ | config 是 yaml，运行时 hot-reload 由 gateway 决定 | 改完直接重启 gateway 最稳 |

## 相关 skill

- [feishu-outage-recovery](../feishu-outage-recovery/SKILL.md) — gateway 重启方法
- [lark-im](../../lark-im/SKILL.md) — lark-cli `+chat-messages-list` 参数
- [feishu-gateway-setup](../feishu-gateway-setup/SKILL.md) — config.yaml 改通道配置
- [hermes-runtime-pitfalls](../hermes-runtime-pitfalls/SKILL.md) — `hermes config set` CLI 铁律 / patch verified 但 mtime 未动 教训