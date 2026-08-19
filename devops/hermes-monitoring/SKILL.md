---
name: hermes-monitoring
description: Monitor Hermes Agent token usage, costs, and credential health. Use when the user wants to query session analytics, build cost dashboards, or inspect Hermes data.
---

# Hermes Monitoring

Query and monitor Hermes Agent usage data — token consumption, cost tracking, credential status.

## Data Sources

| Data | Location | Access |
|------|----------|--------|
| Session stats | `$HERMES_HOME/state.db` → `sessions` table | SQLite (read-only copy if Hermes is running) |
| Credential list | `hermes auth list` CLI | Subprocess |
| Credential details | `$HERMES_HOME/auth.json` | Protected, use CLI or internal import |

## State DB Schema

Full schema details: `skill_view(name="hermes-monitoring", file_path="references/state-db-schema.md")`

Key fields in `sessions`:
- `input_tokens`, `output_tokens`, `reasoning_tokens`, `cache_read_tokens`, `cache_write_tokens`
- `estimated_cost_usd` — Hermes auto-calculates; price source from `official_docs_snapshot`
- `actual_cost_usd` — usually NULL (provider APIs rarely expose real billing)
- `cost_status`, `cost_source`, `pricing_version`
- `model`, `billing_provider` — for grouping
- `started_at`, `ended_at` — unix timestamps
- `source` — `tui`, `feishu`, etc. (useful as profile/proxy identifier)

**Important:** `estimated_cost_usd` is already populated per session. No manual pricing table needed unless you want custom pricing.

## Query Patterns

### Daily spend by model
```sql
SELECT date(started_at, 'unixepoch', 'localtime') as day,
       billing_provider, model,
       SUM(input_tokens) as total_input,
       SUM(output_tokens) as total_output,
       SUM(estimated_cost_usd) as total_cost,
       COUNT(*) as sessions
FROM sessions
GROUP BY day, billing_provider, model
ORDER BY day DESC, total_cost DESC;
```

### Total by model (all time)
```sql
SELECT model, billing_provider,
       SUM(input_tokens), SUM(output_tokens),
       SUM(estimated_cost_usd) as total_cost,
       COUNT(*) as sessions
FROM sessions
GROUP BY model, billing_provider
ORDER BY total_cost DESC;
```

### By source (tui vs feishu etc.)
```sql
SELECT source, COUNT(*), SUM(input_tokens), SUM(estimated_cost_usd)
FROM sessions GROUP BY source;
```

### Grand total
```sql
SELECT SUM(input_tokens), SUM(output_tokens), SUM(reasoning_tokens),
       SUM(estimated_cost_usd), COUNT(*)
FROM sessions;
```

### 按任务类别聚类（哪类任务最耗 token）
按会话标题正则归类统计 tokens/费用：完整脚本与坑见 `references/token-by-task-class.md`。**推荐直接用 `scripts/task-cost-classify.py`**（改进版：额外处理无标题子代理会话，费用按人民币）。

### Cost in RMB（DeepSeek 原生人民币计费）
`estimated_cost_usd` 是 Hermes 按官方快照换算的美元估算；**DeepSeek 实际按人民币计费**（用户明确要求费用用人民币报）。报钱数按官方人民币价重算：flash 输入命中 0.02 / 未命中 1 / 输出 2 元每百万，pro 0.025 / 3 / 6 元每百万。定价表与计算函数见 `references/deepseek-cny-pricing.md`。

## Reading state.db Safely

⚠️ **WAL 陷阱（实测 2026-08-08）**：Hermes 运行时 state.db 是 WAL 模式（同目录有 state.db-wal / -shm）。`cp` 只复制主文件，**复制出的副本可能是空库**——1.58GB 主文件复制后 `sqlite_master` 查不到任何表（表结构/数据大部分在 WAL 里未 checkpoint）。先 cp 再查会白忙一场。

正确做法：**只读 URI 直连原文件**（SQLite 允许多读，Hermes 正在运行也不冲突）：

```python
import sqlite3
db = sqlite3.connect('file:C:/Users/<user>/AppData/Local/hermes/state.db?mode=ro', uri=True)
```

On Windows: `C:\Users\<user>\AppData\Local\hermes\state.db`（路径用正斜杠 + `?mode=ro`）

## Runtime Health Check（网关/服务存活探测）

被问「网关正常吗」或排查服务存活时——**不要跑 `hermes gateway status/start`**（可能触发 update 恢复流程连带停 gateway，见 hermes-maintenance）。改用被动探测三件套：

```bash
# 1. 端口监听（全部服务端口）
netstat -ano | grep LISTENING | grep -E ":(8644|8642|9177|9119|8080)"
#    8644 = gateway webhook 平台（gateway 进程内）
#    8642 = API Server（OpenAI 兼容端点，gateway 进程内）
#    9177 = Hindsight 记忆 daemon（独立进程，由 guard 计划任务 Hermes_Hindsight_Daemon 每5分钟保活）
#    9119 = 远程 serve
#    8080 = DSH web（完全独立于 Hermes，由 DSH_Watchdog 计划任务每分钟保活，需 DEEPSEEK_API_KEY）
# 2. 日志新鲜度（logs/ 下 gateway.log mtime 在几分钟内 = 正在跑）
ls -lt "$LOCALAPPDATA/hermes/logs/" | head
# 3. 进程确认（大内存 python.exe = gateway 主进程）
tasklist | grep -i python
```

**⚠️ 服务独立性（2026-08-17 实测确认）**：

| 服务 | 跟随 Hermes 启动？ | 自己的保活机制 | 端口 |
|------|-------------------|---------------|------|
| gateway | 是（At logon 计划任务 Hermes_Gateway） | Hermes_Gateway_Watchdog 每5分钟 | 8644/8642 |
| Hindsight daemon | 否（独立进程） | Hermes_Hindsight_Daemon 每5分钟 + watchdog 探针 | 9177 |
| DSH web | 否（完全独立，重启 Hermes 不影响 DSH） | DSH_Watchdog 每1分钟 | 8080 |
| HermesDashboard | 是（At logon 计划任务） | 无自愈（常驻） | 9120 |

用户问「DSH 呢」/「Hindsight 呢」时——这些服务的死活与 gateway 无关，需单独查端口。

**watchdog --status 快查**（覆盖 gateway + Hindsight daemon 两层）：
```bash
python3 'C:/Users/HMSJ/AppData/Local/hermes/scripts/gateway_watchdog.py' --status
# alive=true, hindsight_daemon=ok → 两层都正常
```

logs 里常见的「噪音」≠故障：
- `PermissionError: delegate_task child contexts cannot mutate Kanban tasks or boards` —— kanban dispatcher 防护性报错（子代理上下文禁改 kanban），设计内，忽略
- `Skill 'X' maps to slash command /ai already claimed by ...` —— 中文 skill 斜杠命令冲突（多个 skill 抢 /ai），只影响快捷指令，不影响 skill 加载
- `check_web_api_key returned False` —— web_search/web_extract 被凭据 gate 住，诊断链路见 `references/web-tools-backends.md`

## Credential Health

```bash
hermes auth list  # Shows providers, key count, status
```

For programmatic access in Python plugins, import Hermes auth internals or parse CLI output.

Web 工具集（web_search/web_extract）的凭据 gate 与后端选型/定价：见 `references/web-tools-backends.md`。

## Dashboard Integration

Hermes Web Dashboard supports plugins (manifest.json + JS bundle + Python FastAPI router). See `hermes dashboard` docs for theme/plugin extension system. State.db queries above serve as the data layer for a monitoring plugin tab.
