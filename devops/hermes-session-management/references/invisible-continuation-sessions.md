# 续接会话在会话列表不可见（bot 主动私信场景）

2026-08-14 实测。用户问「bot 身份主动给成员飞书发消息，我这边查不到会话吗」——确认：侧边栏/会话列表 API 确实查不到，但数据在 state.db 里一条没丢。这是 Hermes 本体的可见性过滤缺口（`_LISTABLE_CHILD_SQL`），不是数据丢失。

## 现象

- 数据层：state.db `sessions` 表有「激励杨璇」`20260814_095325_2cd38bda`（30 条消息，08-14 09:53）、「感恩🙏」`20260814_095547_96c3b5bf`（3 条，09:55）——内容齐全
- 列表层：`list_sessions_rich(limit=500, order_by_last_active=True)` 返回 99 条 feishu 会话，最新只到 09:11 的 reaction:added:DONE——激励/感恩都不在
- 按 `session_key` 精确过滤同样查不到（返回的全是 `parent_session_id IS NULL` 的旧 root）

## 根因链

1. bot 主动私信 → gateway 在同一 DM（session_key=`agent:main:feishu:dm:oc_xxx`）下创建**新会话**，带 `parent_session_id` 指向该 DM 的旧会话（会话续接/恢复机制，旧会话 end_reason 各异：daily/session_reset/idle）
2. `_LISTABLE_CHILD_SQL`（hermes_state_common.py:103）= `(s.parent_session_id IS NULL OR _BRANCH_CHILD_SQL)`——只有 root 和 branch 可见；branch 判定（hermes_state_common.py:85 `_BRANCH_CHILD_SQL`）= model_config 有 `_branched_from` 标记，或 parent end_reason='branched' 且 started_at >= parent.ended_at
3. 续接会话不满足 branch → 被当「子会话」隐藏
4. root 投影机制（`project_compression_tips`，list_sessions_rich 默认 True）只沿 compression 边走：`_COMPRESSION_CHILD_SQL`（hermes_state_common.py:96）= parent end_reason='compression'。本次链是 测试#2(daily) → 测试#3(session_reset) → 激励杨璇(None)，end_reason 全不是 compression → root 不投影 → 侧边栏显示旧 root（标题「测试 #2」、3 条消息、08-12 时间），新会话永远不冒头

## 排查步骤（复现配方）

```bash
# 1. 确认数据在：查目标 DM 的全部会话
cd "$LOCALAPPDATA/hermes" && python -c "
import sqlite3, datetime
conn = sqlite3.connect('file:state.db?mode=ro', uri=True)
conn.row_factory = sqlite3.Row
for r in conn.execute(\"SELECT id, title, parent_session_id, end_reason, message_count, started_at FROM sessions WHERE session_key=? ORDER BY started_at\", ('agent:main:feishu:dm:oc_xxx',)):
    d = dict(r); d['started_at'] = datetime.datetime.fromtimestamp(d['started_at']).strftime('%m-%d %H:%M'); print(d)
"
# 被隐藏会话特征：parent_session_id 非空 且 parent.end_reason 不是 compression/branched

# 2. 对比列表 API（hermes-agent venv）：
cd "$LOCALAPPDATA/hermes/hermes-agent" && venv/Scripts/python.exe -c "
import sys; sys.path.insert(0,'.')
from pathlib import Path
from hermes_state import SessionDB
db = SessionDB(Path(r'C:/Users/HMSJ/AppData/Local/hermes/state.db'))
rows = db.list_sessions_rich(limit=500, order_by_last_active=True)
feishu = [r for r in rows if r.get('source')=='feishu']
print([ (r['id'], r['title'], r['message_count']) for r in feishu[:5] ])
"
```

## API 参数坑（本次踩到）

- `list_sessions_rich` **没有 `order` 参数**——传 `order='recent'` 直接 `TypeError: got an unexpected keyword argument 'order'`；排序用 `order_by_last_active=True`（布尔）
- SessionDB 构造要 `Path` 对象：传 str 报 `AttributeError: 'str' object has no attribute 'parent'`
- 可用过滤参数：`source`/`sources`/`exclude_sources`/`session_key`/`min_message_count`/`include_archived`/`archived_only`/`include_children`/`compact_rows`/`include_pinned`/`id_query`/`search_query`
- `sessions` 表无 `created_at` 列（用 `started_at`）；WAL 模式下 SQLite 会打印 walreset 警告，无碍
- session_key 格式带前缀：`agent:main:feishu:dm:oc_xxx`，SQL LIKE 用 `'agent:main:feishu:dm:%'` 别漏前缀

## 代码位置

- hermes_state_common.py:103 `_LISTABLE_CHILD_SQL`；:85 `_BRANCH_CHILD_SQL`；:96 `_COMPRESSION_CHILD_SQL`
- hermes_state.py:7104 `list_sessions_rich`（docstring 详述投影逻辑）
- hermes_cli/web_routers/profiles.py:171（sessions 列表）、:305（sidebar 切片）→ 都走 `list_sessions_rich` 默认 include_children=False

## 修复（已实施，2026-08-14 用户拍板方案 A + 用户实测确认）

用户拍板「按上下文」= 合并进该成员历史会话显示最新内容。改动 `hermes_state.py` 三处（**注意不是 hermes_state_common.py**，因为 `_COMPRESSION_CHILD_SQL` 被归档/删除/ancestry 等多处共用，改它语义会变）：

1. **`get_compression_tip(session_id, continuation_edges_only=False)`** 加参数：宽边 = `parent.end_reason='compression' OR (continuation_edges_only AND parent.end_reason IS NOT NULL AND child.session_key IS NOT NULL AND child.session_key = parent.session_key)`。默认窄边不动。⚠️ **SQL 里的布尔参数必须作为绑定参数传**（execute 的 params 元组），写进 f-string 会 `sqlite3.OperationalError: no such column: continuation_edges_only`
2. **投影 CTE 边条件**（list_sessions_rich 内联 SQL，~7317 行）：同样扩宽为「parent.end_reason='compression' OR (parent.end_reason IS NOT NULL AND child.session_key=parent.session_key)」——否则 `effective_last_active` 排序（chain_max）不认续接链，root 排不到顶部
3. **投影触发条件**：`if s.get("end_reason") != "compression": continue` → `if s.get("parent_session_id") is not None: continue`（branch 行跳过防重复投影）+ `get_compression_tip(s["id"], continuation_edges_only=True)`

子会话排除双保险保留：`_branched_from IS NULL`（branch 不进链）、`_delegate_from IS NULL` + `child.source != 'tool'`（subagent/tool 不进链）——subagent 的 session_key 与 parent 不同或为 None，天然不匹配宽边。

### 验证（独立进程 + 真实链路）

- 独立进程：杨璇 DM 列表第一条 = `20260814_095325_2cd38bda`「激励杨璇」30 条 + `_lineage_root_id=20260812_153411_79b6caa8`（旧 root）；subagent 泄漏 0；include_children=True 不投影；500 条 0.27s
- **真实 HTTP 链路（关键！）**：桌面 app 侧边栏数据源是 **HermesDashboard(9120)** 而非 gateway(8644)——只重启 gateway 用户侧边栏仍看不到（本次实测「FEISHU 里没看到」）。必须双进程重启：`powershell Stop-Process -Force`（⚠️ `taskkill /F` 报 Access denied）+ `schtasks /Run /TN Hermes_Gateway` + `/TN HermesDashboard`
- 9120 验证链路：`POST http://127.0.0.1:9120/auth/password-login` body `{"provider":"basic","username":"hermes","password":"Huan1120"}` → 302 无；返回 `{"ok":true}` + Set-Cookie → 带 cookie `GET /api/profiles/sessions?limit=8` → 应见「激励杨璇」30 条。⚠️ basic auth 头不被接受（`{"error":"unauthenticated","reason":"no_cookie"}`），必须走 cookie 登录；`POST /login` 是 405（登录接口在 `/auth/password-login`）

### 补丁登记

改动已追加进 `Obsidian Vault/_hermes/补丁管理/hermes-local-patches.diff`（22 段，`git apply --check --reverse` 通过=已应用），README 已登记——`hermes update` 覆盖后用 `reapply-patches.py --apply` 恢复。
