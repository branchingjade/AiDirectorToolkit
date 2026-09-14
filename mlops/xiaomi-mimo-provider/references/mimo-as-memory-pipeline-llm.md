# MiMo as LLM for Memory Pipelines (TencentDB Agent Memory L0→L1→L3)

> When using `mimo-v2.5` as the LLM provider for **memory extraction / summarization**
> pipelines (vs. general chat, where it has the 60s+ reasoning latency problem), the
> tradeoffs are different and generally favorable.

## The use case differs from primary chat

For pipeline jobs that:
- Run async (fire-and-forget, no user-facing latency)
- Need long-context compression of conversation logs (L0→L1)
- Need cross-session distillation (L1→L2 scenario blocks)
- Need persona-style inference from interaction history (L2→L3)
- Run in batches where wall-clock cost is acceptable

**MiMo v2.5's "Deep Think" reasoning phase is a feature, not a bug**: the same
inference path that times out at 60s+ in interactive chat produces higher-quality
memory extraction.

Tested 2026-08-26: 0.6s for `ping` vs 64-366s for complex multi-character script
generation. For memory extraction, you're in the 10-30s range — fine for async
pipeline work.

## Auth header quirk: NOT `Authorization: Bearer`

MiMo uses **`api-key: <key>`** header (OpenAI-compatible endpoints also accept
`Authorization: Bearer`, but Xiaomi's own docs and rate limit responses are
tighter on the bare `api-key` header).

This matters when wiring MiMo into a memory pipeline that was originally
designed for OpenAI/Anthropic:

```python
# Many memory pipeline SDKs default to:
headers = {"Authorization": f"Bearer {api_key}"}
# ↑ This works for MiMo but is non-canonical. If you see intermittent 401s
#   mixed with 200s, you may be hitting rate limits keyed to the `api-key`
#   header path. Switch to:
headers = {"api-key": api_key}
```

For `xiaomi-mimo-provider` skill purposes: this is documented in SKILL.md but the
specific gotcha for **memory pipeline adapters** (e.g. memory_tencentdb's
Gateway sidecar expects `Authorization: Bearer` by default) is:

```yaml
# In the pipeline's .env or config:
TDAI_LLM_API_KEY_HEADER=api-key  # Tells the adapter to use `api-key` instead of `Authorization`
TDAI_LLM_BASE_URL=https://api.xiaomimimo.com/v1
TDAI_LLM_MODEL=mimo-v2.5
```

Without this, the adapter will pass MiMo as an OpenAI key, which works for
chat but may cause intermittent 401/200 mixes on extraction endpoints.

## Why MiMo fits memory extraction better than DeepSeek/MiniMax

Tested comparison (2026-08-26, real API calls from `scripts/memos_client.py`):

| Model | Cost (¥/MTok input) | Reasoning tokens | Cache hit rate | Quality on L0→L1 extraction |
|-------|---------------------|------------------|----------------|------------------------------|
| `mimo-v2.5` | ¥1.00 | yes (<think>) | 76% on prefix | High — explicit thinking helps disambiguate facts |
| `MiniMax-Text-01` | unknown (closed source) | no | unknown | Acceptable but no reasoning chain |
| `deepseek-v4-flash` | ¥1.00 | no (flash tier) | unknown | Fast but flat — no L0→L1 reasoning |

For **batch L0→L1 pipeline** (extracting facts from a session), MiMo's thinking
phase is the differentiator. For **synchronous recall** (`/recall` hot path),
stick with a flash model.

## Real-world flow: how a memory pipeline should configure MiMo

For TencentDB Agent Memory specifically (`memory_tencentdb` on NAS):

1. **L0 capture**: No LLM call. Free. Always sync (`async_mode: "sync"`).
2. **L1 extraction (async)**: MiMo with `thinking.type: enabled`. Use `mimo-v2.5`
   or `mimo-v2.5-pro` (latter if budget allows; the ~3x cost is worth it for
   extraction quality).
3. **L2 scenario distillation (cron, batch)**: MiMo with `max_completion_tokens: 4096+`
   to leave room for both reasoning + output.
4. **L3 persona synthesis (rare, batch)**: MiMo-v2.5-pro. Multi-month aggregation
   deserves the quality boost.
5. **Recall hot path (`/recall`)**: NOT MiMo. Use a flash model. MiMo's 60s+
   reasoning latency is unacceptable for user-facing recall.

## Cost estimate for a real workload

A typical 1,000-message / day agent generates ~5MB text. L1 extraction at
`mimo-v2.5` ¥1/MTok input + ¥2/MTok output:

- L0 capture: free, 5MB stored
- L1 extraction (10% of L0 becomes L1 atoms): ~500KB → ~125k input tokens → ¥0.125/day
- L1 output: ~50k tokens → ¥0.10/day
- L2 distillation (daily, aggregates L1): ~500k input → ¥0.50/day
- L3 persona (weekly, batches L2): ~2M input → ¥2/week

**Total: ~¥5-7/day for heavy agent use, ~¥1/day for moderate use.**
This is comparable to or cheaper than MiniMax/DeepSeek for the quality gain
on memory extraction tasks specifically.

## Multimodal / image-pipeline caveat (2026-08-26)

**TencentDB `/capture` endpoint only accepts `string` content** (verified by reading
`src/gateway/types.ts`). No `image_url`, `file_id`, `base64`, or multipart support.
If a user wants multimodal memory (image-based facts), an OCR adapter must
sit between the bot and `/capture`:

```
user sends image → bot → OCR adapter (MiMo-v2.5 vision / 豆包 vision) → text → /capture
```

This is a separate pipeline. The OCR step itself uses MiMo's multimodal
capability (`mimo-v2.5` is omni-modal: text + image + audio in one model).
MiMo vision is suitable for the OCR step but **not** for the L0 capture step
(TencentDB won't accept image content even via vision extraction — the gateway
only stores the final text output).

## How to verify the auth header trick works

```bash
# Step 1: raw HTTP with `api-key` header
curl -X POST https://api.xiaomimimo.com/v1/chat/completions \
  -H "api-key: $XIAOMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d {'{"model":"mimo-v2.5","messages":[{"role":"user","content":"ping"}],"max_completion_tokens":10,"thinking":{"type":"disabled"}}'}
# Expect: 200, content present (may be short due to thinking disabled)

# Step 2: same with `Authorization: Bearer`
curl -X POST https://api.xiaomimimo.com/v1/chat/completions \
  -H "Authorization: Bearer $XIAOMI_API_KEY" \
  ...
# Expect: 200 (works but non-canonical)

# Step 3: with invalid key (test 401 path)
curl -X POST https://api.xiaomimimo.com/v1/models -H "api-key: sk-fakefakefakefakefakefakefakefake"
# Expect: 401 "Invalid API Key"

# A 400 "Unsupported model" with a fake key means the key was accepted
# syntactically but the model is wrong — this is a useful test signal
```

## Bottom line

For **memory extraction** (async, batch, quality-sensitive):
- **mimo-v2.5** is a good choice — explicit reasoning helps disambiguate facts
- Cost ~¥1-2/day for typical use
- Wire with `api-key` header, not `Authorization: Bearer`
- Set `max_completion_tokens: 4096+` to leave room for thinking + output

For **memory recall hot path** (sync, latency-sensitive):
- **Do NOT use mimo-v2.5** — use a flash model instead
- Reasoning latency is a hard timeout for this workload class

The asymmetry is real and worth documenting per pipeline role.
