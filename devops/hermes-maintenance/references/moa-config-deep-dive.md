# Hermes MoA (Mixture of Agents) — config schema & internals

Verified against Hermes v0.18.2 source (2026-07). Files of record:
- `hermes_cli/moa_config.py` — schema, normalization, defaults
- `agent/moa_loop.py` — runtime (reference fan-out + aggregator)
- `cli.py` (~L8878) and `gateway/run.py` (~L10058) — `/moa` handlers
- `hermes_cli/config.py` — `DEFAULT_CONFIG["moa"]` and `auxiliary.moa_reference` / `auxiliary.moa_aggregator`

## What MoA is (in this implementation)

- `/moa <prompt>` marks **one user turn** as MoA-enabled. It is NOT a model tool —
  the normal agent loop still owns tool calling; MoA only injects advisory
  context before each main-model iteration.
- Reference models are **advisors**: no tools, parallel independent calls
  (ThreadPoolExecutor, cap 8 concurrent).
- The **aggregator** is the acting model whose output the user sees.
- MoA is exposed as a **virtual provider** (`provider: "moa"`) internally.
  A preset can never use `moa` as a reference/aggregator provider (rejected
  at normalization to prevent recursion).
- Presets also appear in the `/model` picker → selecting one enables MoA
  for the whole session; `/moa` is one-shot sugar that restores the previous
  model after the turn.
- Gateway note: on Slack, `/moa` is only reachable via `/hermes moa`
  (`_SLACK_VIA_HERMES_ONLY`). CLI and desktop handle `/moa` directly.
  If the agent is mid-run: "Agent is running — wait or /stop first".

## Config schema (the ONLY keys that are read)

```yaml
moa:
  default_preset: default      # which preset /moa uses
  active_preset: ""            # session-independent sticky preset ("" = none)
  save_traces: false           # JSONL full-turn traces
  trace_dir: ""                # default <hermes_home>/moa-traces/<session_id>.jsonl
  presets:
    <name>:                    # any name incl. non-ASCII (e.g. 自用)
      enabled: true
      reference_models:        # list of {provider, model} slots
        - provider: deepseek
          model: deepseek-v4-pro
        - provider: xiaomi
          model: mimo-v2.5-pro
      aggregator:              # single {provider, model} slot
        provider: deepseek
        model: deepseek-v4-pro
      reference_temperature:   # null = omit param (provider default)
      aggregator_temperature:  # null = omit param
      max_tokens: 4096         # aggregator output cap
      reference_max_tokens:    # null = uncapped advisors; set e.g. 600 for speed
      fanout: per_iteration    # per_iteration | user_turn
```

- `fanout: per_iteration` — advisors re-run every tool iteration (advice
  tracks live task state; slower, costlier).
- `fanout: user_turn` — advisors run ONCE per user turn (classic MoA shape).
- `reference_max_tokens` is the main latency knob: turn latency correlates
  ~0.88 with advisor output tokens. Capping (~600) roughly halves wall time.
- Transport-level knobs (timeout 900s, base_url/api_key overrides,
  reasoning_effort) live in `auxiliary.moa_reference` and
  `auxiliary.moa_aggregator`, NOT inside the preset.

## Normalization rules (why misconfig is SILENT)

From `normalize_moa_config()` / `_normalize_preset()` / `_clean_slot()`:

1. **Legacy flat shape only applies when `presets` is empty/absent.**
   `moa.reference_models` / `moa.aggregator` etc. at the top level become
   the `default` preset ONLY `if not presets`. The moment `moa.presets:`
   has one entry, all flat keys under `moa:` are ignored with no warning.
   (This is how "配了没反应" happens after failed `hermes config set` runs
   left keys at the wrong level.)
2. **Invalid slots are silently dropped → defaults kick in.** A slot missing
   `provider` or `model` (or `provider: moa`) → `None` → filtered out. If NO
   valid reference slots remain, the preset falls back to
   `DEFAULT_MOA_REFERENCE_MODELS` = `openai-codex/gpt-5.5` +
   `openrouter/deepseek-v4-pro`. A missing/invalid aggregator falls back to
   `DEFAULT_MOA_AGGREGATOR` = `openrouter/anthropic/claude-opus-4.8`.
   ⚠️ So a botched preset doesn't error — it silently swaps in providers
   the machine may have no keys for.
3. **No credential validation at config time.** Provider names are accepted
   verbatim; failures only surface mid-turn when the reference/aggregator
   call errors out.
4. `default_preset` not found in presets → first preset name wins.
   `active_preset` not found → treated as "".

## Diagnosis path (order matters)

1. Parse `config.yaml` → list `moa.presets` keys + spot stray flat keys.
2. Cross-check every `provider` in every slot against actual credentials:
   `.env` key names (`grep -oE '^[A-Z_]+=' .env | sed 's/=$//'`) and
   `auth.json → credential_pool` keys (do NOT print values; filter out
   `api_key`/`token` fields when dumping entries).
3. Remember fallback defaults (rule 2 above): even a preset that *looks*
   local-only can fall back to openai-codex/openrouter if its slots are
   malformed.
4. Fix by rewriting `config.yaml` via Python yaml — `hermes config set`
   cannot express list-of-dicts (known serializer limitation; same bug as
   MCP `args` editing).
5. Change takes effect on next session (`/reset`); MoA config is read per
   turn from the loaded config, but the model/preset selection is
   session-level state.

## Real-world case (2026-07-17)

Symptom: "无法配置 MoA". Config had presets `default` + `自用`, all slots
`provider: openrouter`, but the machine's credentials were only
deepseek / xiaomi / kimi-coding / copilot / tencent-tokenhub — no
`OPENROUTER_API_KEY`. Additionally `moa:` carried dead flat keys
(`reference_models`, `aggregator`, `max_tokens`, `fanout`, `enabled`)
from earlier failed `hermes config set` attempts. Both facts together:
runtime always failed AND edits appeared to do nothing.

## Cost reality check

Default preset ≈3 model calls per iteration (2 refs + 1 aggregator).
With premium models this is easily 20x the cost of a single-model turn.
Recommend `/moa` one-shot for hard bugs / architecture decisions only;
don't set a MoA preset as the session default for routine work.
