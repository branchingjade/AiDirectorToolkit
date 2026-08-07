# State DB Schema (Hermes Agent)

Database: `$HERMES_HOME/state.db` (SQLite + FTS5)  
Windows path: `C:\Users\<user>\AppData\Local\hermes\state.db`

## sessions

The primary table for analytics. One row per conversation session.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Session ID (e.g. `20260624_130900_abc123`) |
| `source` | TEXT | Origin: `tui`, `feishu`, `telegram`, `discord`, etc. |
| `user_id` | TEXT | Gateway user identifier |
| `model` | TEXT | Model name (e.g. `deepseek-v4-pro`) |
| `model_config` | TEXT | Full model config JSON |
| `system_prompt` | TEXT | System prompt used |
| `parent_session_id` | TEXT | Forked/branched from |
| `started_at` | REAL | Unix timestamp with fractional seconds |
| `ended_at` | REAL | Unix timestamp when session ended |
| `end_reason` | TEXT | Why session ended |
| `message_count` | INTEGER | Total messages in session |
| `tool_call_count` | INTEGER | Total tool calls made |
| **Token fields** | | |
| `input_tokens` | INTEGER | Total input tokens |
| `output_tokens` | INTEGER | Total output tokens |
| `cache_read_tokens` | INTEGER | Cache read tokens (prompt caching) |
| `cache_write_tokens` | INTEGER | Cache write tokens |
| `reasoning_tokens` | INTEGER | Reasoning/thinking tokens |
| **Cost fields** | | |
| `estimated_cost_usd` | REAL | Estimated cost in USD |
| `actual_cost_usd` | REAL | Actual billed cost (usually NULL) |
| `cost_status` | TEXT | `estimated`, `actual`, `unavailable` |
| `cost_source` | TEXT | e.g. `official_docs_snapshot` |
| `pricing_version` | TEXT | Pricing data version used |
| `billing_provider` | TEXT | e.g. `deepseek`, `openrouter`, `anthropic` |
| `billing_base_url` | TEXT | API endpoint used |
| `billing_mode` | TEXT | Billing mode |
| **Metadata** | | |
| `title` | TEXT | Session title |
| `cwd` | TEXT | Working directory |
| `api_call_count` | INTEGER | Total API calls |
| `handoff_state` | TEXT | Handoff state |
| `handoff_platform` | TEXT | Handoff platform |
| `rewind_count` | INTEGER | Rollback count |
| `archived` | INTEGER | 0 or 1 |

## messages

Individual messages within sessions. Join on `session_id`.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment PK |
| `session_id` | TEXT | FK to sessions.id |
| `role` | TEXT | `user`, `assistant`, `system`, `tool` |
| `content` | TEXT | Message content |
| `tool_call_id` | TEXT | Tool call identifier |
| `tool_calls` | TEXT | Tool call JSON |
| `tool_name` | TEXT | Tool name if tool result |
| `timestamp` | REAL | Unix timestamp |
| `token_count` | INTEGER | Tokens in this message |
| `finish_reason` | TEXT | API finish reason |
| `reasoning` | TEXT | Reasoning content |
| `reasoning_content` | TEXT | Raw reasoning content |
| `reasoning_details` | TEXT | Reasoning details JSON |
| `codex_reasoning_items` | TEXT | Codex-specific reasoning |
| `codex_message_items` | TEXT | Codex-specific message items |
| `platform_message_id` | TEXT | Gateway platform message ID |
| `observed` | INTEGER | 0 or 1 |
| `active` | INTEGER | 0 or 1 |

## Other tables

- `state_meta` — key-value metadata store
- `compression_locks` — context compression locks
- `messages_fts*` — FTS5 full-text search indices (internal)

## Query Safety

state.db may be locked by running Hermes process. Always copy before querying:

```bash
cp "$HERMES_HOME/state.db" /tmp/state_copy.db
```

For programmatic Python access:
```python
import sqlite3
db = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
```

The `started_at` field uses Unix timestamps with fractional seconds. Convert with:
```sql
date(started_at, 'unixepoch', 'localtime')
datetime(started_at, 'unixepoch', 'localtime')
```
