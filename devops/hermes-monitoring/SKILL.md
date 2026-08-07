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

## Reading state.db Safely

Hermes holds a write lock on state.db while running. Copy first:
```bash
cp "$HERMES_HOME/state.db" /tmp/state_copy.db
python3 -c "import sqlite3; db = sqlite3.connect('/tmp/state_copy.db'); ..."
```

On Windows: `C:\Users\<user>\AppData\Local\hermes\state.db`

## Credential Health

```bash
hermes auth list  # Shows providers, key count, status
```

For programmatic access in Python plugins, import Hermes auth internals or parse CLI output.

## Dashboard Integration

Hermes Web Dashboard supports plugins (manifest.json + JS bundle + Python FastAPI router). See `hermes dashboard` docs for theme/plugin extension system. State.db queries above serve as the data layer for a monitoring plugin tab.
