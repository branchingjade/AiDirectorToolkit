# Hermes state.db — sessions table schema

The `sessions` table in `~/.hermes/state.db` (SQLite3) auto-tracks per-session token usage and cost.

## Key cost/token columns

```
input_tokens         INTEGER    Input tokens consumed
output_tokens        INTEGER    Output tokens generated
reasoning_tokens     INTEGER    Reasoning tokens (thinking models)
cache_read_tokens    INTEGER    Cache read tokens
cache_write_tokens   INTEGER    Cache write tokens
estimated_cost_usd   REAL       Hermes-calculated estimated cost in USD
actual_cost_usd      REAL       Actual cost from provider billing (rarely populated)
cost_status          TEXT       "estimated" when estimated_cost_usd is populated
cost_source          TEXT       Source of pricing data (e.g. "official_docs_snapshot")
billing_provider     TEXT       Provider key (e.g. "deepseek", "openrouter")
billing_base_url     TEXT       Provider base URL
billing_mode         TEXT       Billing mode
pricing_version      TEXT       Pricing data version used
```

## Other useful columns

```
id                   TEXT       Session ID (e.g. "20260624_131901_94d935")
started_at           REAL       Unix timestamp (float)
ended_at             REAL       End timestamp
source               TEXT       Origin: "tui", "feishu", "telegram", etc.
model                TEXT       Model name (e.g. "deepseek-v4-pro")
title                TEXT       Session title
message_count        INTEGER   Number of messages
tool_call_count      INTEGER   Number of tool calls
api_call_count       INTEGER   Number of API calls
```

## Notes

- `estimated_cost_usd` is populated for ALL sessions. Hermes has a built-in pricing table.
- `actual_cost_usd` is almost always NULL — provider billing APIs aren't consistently available.
- The `source` column can be used to distinguish profiles/usage channels.
- Sessions before mid-June 2026 may show $0.0000 cost (pricing data was added later).
- **The dashboard's `SDK.api.getSessions(limit)` does NOT return cost/provider columns** — the TypeScript `SessionInfo` interface at `web/src/lib/api.ts:1633` is limited to `id, source, model, title, started_at, ended_at, last_active, is_active, message_count, tool_call_count, input_tokens, output_tokens, preview`. To access `estimated_cost_usd` etc. from a plugin, use a bundled plugin with `plugin_api.py` that reads state.db directly via sqlite3 (see `references/bundled-plugin-pattern.md`).
