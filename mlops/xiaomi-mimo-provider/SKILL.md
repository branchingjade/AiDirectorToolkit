---
name: xiaomi-mimo-provider
description: "Xiaomi MiMo provider: model selection, vision support matrix, connectivity testing, auxiliary vision setup in Hermes."
version: 2.2.0
author: agent
tags: [xiaomi, mimo, provider, vision, multimodal, auxiliary, configuration, audio, video, tts, asr]
platforms: [windows, linux, macos]
related_skills: [mimo-audio-analyzer]
---

# Xiaomi MiMo Provider

Xiaomi MiMo is a Chinese LLM provider accessible via OpenAI-compatible API (also supports Anthropic API format for images). Use it for chat, vision, audio understanding, video understanding, TTS, and ASR tasks in Hermes.

See `mimo-audio-analyzer` skill for audio analysis. See `references/mimo-api-limits.md` for full MiMo API reference.

## Setup

```bash
# In ~/.hermes/.env
XIAOMI_API_KEY=<your-key>
XIAOMI_BASE_URL=https://api.xiaomimimo.com/v1
```

Get API key at: https://platform.xiaomimimo.com

## Available Models & Capabilities

| Model | Chat | Vision | Audio | TTS | ASR | Notes |
|-------|:----:|:------:|:-----:|:---:|:---:|-------|
| `mimo-v2.5` | ✅ | ✅ | ✅ | ❌ | ❌ | Omni-modal, 1M context. Vision + audio understanding |
| `mimo-v2.5-pro` | ✅ | ❌ | ❌ | ❌ | ❌ | 1T params/42B active, 1M context. Chat only |
| `mimo-v2.5-pro-ultraspeed` | ✅ | ❌ | ❌ | ❌ | ❌ | FP4 quantized, 1000 tok/s. **No vision/audio** |
| `mimo-v2-omni` | ✅ | ✅ | ❌ | ❌ | ❌ | ⚠️ Deprecated 2026.6.30 — use `mimo-v2.5` |
| `mimo-v2-flash` | ✅ | ❌ | ❌ | ❌ | ❌ | ⚠️ Deprecated 2026.6.30 |
| `mimo-v2-pro` | ✅ | ❌ | ❌ | ❌ | ❌ | ⚠️ Deprecated 2026.6.30 |
| `mimo-v2.5-tts` | ❌ | ❌ | ❌ | ✅ | ❌ | TTS with voice control (free) |
| `mimo-v2.5-tts-voiceclone` | ❌ | ❌ | ❌ | ✅ | ❌ | Voice cloning |
| `mimo-v2.5-tts-voicedesign` | ❌ | ❌ | ❌ | ✅ | ❌ | Voice design |
| `mimo-v2-tts` | ❌ | ❌ | ❌ | ✅ | ❌ | ⚠️ Deprecated 2026.6.27 |
| `mimo-v2.5-asr` | ❌ | ❌ | ❌ | ❌ | ✅ | Bilingual + dialects, lyrics |

> **⚠️ 无 embedding 端点（2026-08-06 实测）**：MiMo `/v1/embeddings` 返回 404，模型列表仅 chat/vision/audio/tts/asr——**不能用作 embedding provider**（如 OpenViking 记忆库的语义搜索）。embedding 需另选（本地 llama.cpp/Ollama 或火山/OpenAI embedding API）；MiMo 仍可作 VLM 用。

### Pricing (CNY per MTok, as of 2026.06)

| Model | Input (cache hit) | Input (cache miss) | Output |
|-------|:-:|:-:|:-:|
| `mimo-v2.5` | ¥0.02 | ¥1 | ¥2 |
| `mimo-v2.5-pro` | ¥0.025 | ¥3 | ¥6 |
| `mimo-v2.5-pro-ultraspeed` | ¥0.075 | ¥9 | ¥18 |
| TTS Series | Free (limited time) | — | — |
| ASR | ¥0.5/hour | — | — |

> V2 models auto-routed to V2.5 series with V2.5 pricing. Full deprecation 2026.6.30.

---

## Multimodal Understanding Limits

### Image (`type: "image_url"`, via `image_url.url`)

| Limit | Value |
|-------|-------|
| Formats | JPEG, PNG, GIF, WebP, BMP |
| URL size | ≤ 50 MB per image |
| Base64 size | ≤ 50 MB per image |
| Multi-image | ✅ Supported (within context limits) |
| Token calc | Complex — based on resolution (PATCH=16, MERGE=2, min 8192px, max 8388608px). See docs for formula. |
| Local file | ❌ URL or base64 only |
| API formats | OpenAI (`/v1/chat/completions`) + Anthropic (`/anthropic/v1/messages`) |

### Audio (`type: "input_audio"`, via `input_audio.data`)

| Limit | Value |
|-------|-------|
| Formats | MP3, WAV, FLAC, M4A, OGG |
| URL size | ≤ 100 MB |
| Base64 size | ≤ 50 MB (encoded string) |
| Token calc | ≈ duration(sec) × 6.25 |
| Local file | ❌ URL or base64 only |

### Video (`type: "video_url"`, via `video_url.url`)

| Limit | Value |
|-------|-------|
| Formats | MP4, MOV, AVI, WMV |
| URL size | ≤ 300 MB |
| Base64 size | ≤ 50 MB |
| Token calc | video_tokens (fps×resolution) + audio_tokens (≈6.25×sec). See docs for formula. |
| Local file | ❌ URL or base64 only |
| Control params | `fps` (0.1-10, default 2), `media_resolution` ("default" or "max") |

---

## Deep Think / Reasoning

MiMo v2.5 uses `reasoning_content` in responses. Key rule: in multi-turn agent sessions with tool calls, you **must** pass back `reasoning_content` for every assistant message that contains tool calls, or the API returns 400.

**PITFALL — Reasoning Delay (\"no chunks yet\")**: v2.5 has a built-in reasoning phase that runs BEFORE producing visible text. During this phase the model produces `reasoning_content` tokens internally but NO visible text chunks. Hermes shows `"waiting for stream response (Xs, no chunks yet)"` — this is NOT a timeout, NOT a network error, NOT a config issue. It's the model thinking. Real-world timings (tested 2026-07-17):

| Task complexity | v2.5 response | DeepSeek v4-flash |
|-----------------|:------------:|:-----------------:|
| Simple (\"测试\") | 10-14s | 3-8s |
| Complex (multi-char script) | 64-366s | 15-60s |

**Recommendation**: Do NOT use v2.5 as the primary chat model for latency-sensitive workflows (Feishu group chat, interactive Q&A). Use it as:
- **Auxiliary** vision/audio model (Hermes routes these separately, no user-facing delay)
- **ASR/TTS** provider (special-purpose endpoints, no reasoning phase)
- **Sub-agent** for async heavy analysis where delay is acceptable

For primary chat, DeepSeek v4-flash (or any non-reasoning model) delivers first-token latency under 3s consistently.

**PITFALL**: `reasoning_tokens` compete with `completion_tokens` budget. Set generous `max_completion_tokens` (4096+) or content output will be empty. This affects all modalities (text, image, audio, video).

---

## Hermes Provider Registration

MiMo requires a custom provider in Hermes. The provider name `xiaomi` is resolved via `XIAOMI_API_KEY` and `XIAOMI_BASE_URL` from `.env`.

### As primary (global default)

```bash
hermes config set model.provider xiaomi
hermes config set model.default mimo-v2.5
hermes config set delegation.model mimo-v2.5
hermes config set delegation.provider xiaomi
```

With DeepSeek as fallback (edit config.yaml via Python — `hermes config` can't set list values):
```yaml
fallback_providers:
  - provider: deepseek
    model: deepseek-v4-pro
  - provider: deepseek
    model: deepseek-v4-flash
```

### Per-platform override (recommended — keep DeepSeek as global default)

**PITFALL — Don't change global config for platform-specific needs.** When the user wants MiMo for "飞书所有会话" or "all Feishu sessions", set it at the **platform level**, NOT the global `model.provider`/`model.default`. Changing global config affects Hermes TUI, cron jobs, delegation, and everything else.

```bash
# ✅ CORRECT — platform-level: only Feishu uses MiMo, global stays DeepSeek
# Edit config.yaml via Python:
```
```python
import yaml
config_path = r'C:\Users\HMSJ\AppData\Local\hermes\config.yaml'
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
config.setdefault('platforms', {}).setdefault('feishu', {})
config['platforms']['feishu']['model'] = 'mimo-v2.5'
config['platforms']['feishu']['provider'] = 'xiaomi'
with open(config_path, 'w', encoding='utf-8') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
```

```bash
# ❌ WRONG — this changes everything including Hermes TUI
hermes config set model.provider xiaomi
hermes config set model.default mimo-v2.5
```

**Scope rules for MiMo config:**
- **Global** (`model.*`): Keep DeepSeek as default (fast for interactive use)
- **Platform** (`platforms.feishu.model/provider`): MiMo for all Feishu sessions
- **Channel** (`platforms.feishu.channel_overrides.oc_*.model/provider`): MiMo for specific chat
- **TTS/STT** (`tts.*`, `stt.*`): Always global — these are utilities, not chat models
- **Auxiliary** (`auxiliary.vision.*`): Global — used internally by Hermes regardless of chat model

### As per-channel override (e.g. specific Feishu group)

```bash
hermes config set platforms.feishu.channel_overrides.oc_CHAT_ID.model mimo-v2.5
hermes config set platforms.feishu.channel_overrides.oc_CHAT_ID.provider xiaomi
```

To remove a channel override, use Python (no `hermes config unset`):
```python
import yaml
with open(r'C:\Users\HMSJ\AppData\Local\hermes\config.yaml') as f:
    c = yaml.safe_load(f)
c['platforms']['feishu'].pop('channel_overrides', None)
with open(r'C:\Users\HMSJ\AppData\Local\hermes\config.yaml', 'w') as f:
    yaml.dump(c, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
```

### Model selection strategy (updated 2026-07-17)

**CRITICAL — Do NOT use v2.5 as primary chat model for Chinese creative/prompt-optimization tasks.** Real-world testing (2026-07-17) found v2.5 times out at 60s+ on ~80-char Chinese prompt optimization, while DeepSeek v4-flash completes in 1.4s (40x faster). v2.5's reasoning phase is not a "slow but thorough" tradeoff — it's a hard timeout for this workload class.

**Recommended role for MiMo models:**

| Role | Model | Rationale |
|------|-------|-----------|
| Primary chat | ❌ NOT v2.5 | 40x slower than DeepSeek on Chinese creative tasks |
| Auxiliary vision | `mimo-v2.5` | Native multimodal, used by Hermes vision_analyze |
| Auxiliary audio | `mimo-v2.5` | Native audio understanding |
| TTS | `mimo-v2.5-tts` | Free tier, correct endpoint via command provider |
| ASR | `mimo-v2.5-asr` | ¥0.5/hr, via local_command + HERMES_LOCAL_STT_COMMAND |
| Fallback chat | `mimo-v2.5` | When DeepSeek is down, acceptable for simple queries |

**For primary chat, use DeepSeek v4-flash** (tested same prompt: 1.5s vs MiMo 60s+):

| | DeepSeek v4-flash | DeepSeek v4-pro |
|--|:--:|:--:|
| Chinese prompt optimization | 1.5s, 78 chars | 7.0s, 430 chars (3 versions) |
| Price | ¥1/¥2 per MTok | ¥3/¥6 per MTok |
| Best for | Chat, quick optimization | Multi-version output, deep analysis |

**When MiMo is primary (non-Chinese or simple queries only):**

| Scenario | Model |
|----------|-------|
| Simple chat, quick Q&A | `mimo-v2.5` (acceptable ~3s) |
| Complex multi-step reasoning | `mimo-v2.5` via delegation (sub-agent runs async) |
| When MiMo is down | `deepseek-v4-pro` → `deepseek-v4-flash` (fallback chain) |

**Key insight**: v2.5-pro (¥3/¥6) costs 3x more than v2.5 (¥1/¥2) but showed no detectable quality improvement for Chinese creative/prompt optimization tasks. The multimodal advantage of v2.5 is also irrelevant for primary chat since Hermes already routes vision/audio through auxiliary models regardless of the chat model.

See `references/deepseek-v4-flash-vs-pro-benchmark.md` for full test data (2026-07-17).

```bash
# Correct vision model
hermes config set auxiliary.vision.provider xiaomi
hermes config set auxiliary.vision.model mimo-v2.5
```

Config result in `config.yaml`:
```yaml
auxiliary:
  vision:
    provider: xiaomi
    model: mimo-v2.5
```

The empty `base_url` and `api_key` in the auxiliary section are normal — Hermes falls back to `XIAOMI_API_KEY` and `XIAOMI_BASE_URL` from `.env`.

---

### Hermes TTS Setup

```bash
hermes config set tts.provider xiaomi
hermes config set tts.model mimo-v2.5-tts
```

**CRITICAL**: MiMo TTS does NOT use OpenAI's `/v1/audio/speech` endpoint.
See `scripts/mimo_tts.py` for a working command provider that uses the correct
`POST /v1/chat/completions` format.

To wire it into Hermes, add a command provider under `tts.providers.xiaomi` in
config.yaml:

```yaml
tts:
  provider: xiaomi
  providers:
    xiaomi:
      type: command
      command: python "C:/Users/HMSJ/AppData/Local/hermes/scripts/mimo_tts.py" "{text}" "{output_path}"
      timeout: 60
      output_format: wav
      env:
        XIAOMI_API_KEY: ${XIAOMI_API_KEY}
        XIAOMI_BASE_URL: ${XIAOMI_BASE_URL}
```

Adjust the script path for Linux/macOS. The `env` block expands `${ENV_VAR}`
references from the Hermes process environment at runtime.

**xiaomi is NOT a built-in TTS provider.** There is no bundled plugin for xiaomi
TTS. The dispatch falls through to Edge TTS (default). To actually use MiMo TTS,
register a custom command provider in `~/.hermes/config.yaml`:

```yaml
tts:
  provider: xiaomi
  providers:
    xiaomi:
      type: command
      command: python "<hermes_home>/scripts/mimo_tts.py" "{text}" "{output_path}"
      timeout: 60
      output_format: wav
      env:
        XIAOMI_API_KEY: ${XIAOMI_API_KEY}
        XIAOMI_BASE_URL: ${XIAOMI_BASE_URL}
  model: mimo-v2.5-tts
```

The command provider script is at `scripts/mimo_tts.py` in this skill.
Copy it to `~/.hermes/scripts/` and reference the absolute path in the command.

### Known Limitation: ~1s Audio (ALL models, platform-wide)

**Every MiMo TTS model** (`mimo-v2.5-tts`, `mimo-v2.5-tts-voiceclone`,
`mimo-v2.5-tts-voicedesign`) hard-truncates audio output to ~1 second per call,
regardless of input text length or `max_tokens`/`max_completion_tokens` setting
(verified up to 65536). Increasing token limits has zero effect — this is a
**platform-level constraint**, not a parameter bug.

For paragraphs or multi-minute content, chaining hundreds of calls is not
practical given MiMo's rate limiting (429 after ~6 calls, ~90s cooldown). Use:

- **Other cloud APIs**: Fish Audio, ElevenLabs, 火山引擎 TTS (long-form voice clone)
- **Local inference**: GPT-SoVITS / CosyVoice (requires GPU, ~30 min setup)
- **Edge TTS**: `hermes config set tts.provider edge` for non-cloned long-form speech

MiMo TTS works only for short utterances (single sentences ≤15 chars).

### Hermes MEDIA Delivery

TTS generates WAV files tagged with `MEDIA:<path>`. In **gateway sessions**
(Feishu/Telegram/Discord), the platform adapter auto-delivers audio as a voice
message. In **TUI mode**, MEDIA tags are displayed as text paths only — no
auto-playback.

**PITFALL — Fallthrough to Edge TTS**: The xiaomi provider is NOT a built-in
Hermes TTS provider. Without a command provider or plugin, the dispatch silently
falls through to Edge TTS. If `edge_tts` Python package is installed, TTS
"works" but uses Edge voices, not MiMo. If `edge_tts` is missing, all TTS calls
fail with "No audio was received" — the error looks like a MiMo problem but is
actually a missing Edge TTS dependency.

**Fix**: Add a command provider under `tts.providers.xiaomi` in
`~/.hermes/config.yaml`. See `scripts/mimo_tts_command.py` for the
ready-to-use command script:

```yaml
tts:
  provider: xiaomi
  model: mimo-v2.5-tts
  providers:
    xiaomi:
      type: command
      command: python "path/to/mimo_tts_command.py" "{text}" "{output_path}"
      timeout: 60
      output_format: wav
```

The script calls `POST /v1/chat/completions` with the MiMo TTS message format
and decodes the base64 WAV from `choices[0].message.audio.data`.

### Hermes TTS Dispatch Architecture

**xiaomi/mimo is NOT a built-in TTS provider.** Hermes built-ins are: `edge`,
`openai`, `elevenlabs`, `minimax`, `xai`, `mistral`, `gemini`, `neutts`,
`piper`, `kittentts`.  When `tts.provider: xiaomi`, the dispatch chain is:

1. **Command provider** — checks `tts.providers.xiaomi: type: command` in config. If
   not declared, skips.
2. **Plugin provider** — calls `agent.tts_registry.get_provider("xiaomi")`. The
   xiaomi TTS provider is registered at plugin-discovery time by a bundled plugin
   (under `hermes-agent/plugins/`). If found, calls `provider.synthesize()`.
3. **Fallthrough** — if no plugin found, falls through the built-in elif chain and
   lands on Edge TTS as default.

### MiMo TTS / ASR API Format (CRITICAL)

**ALL MiMo special-purpose models use the standard `/v1/chat/completions`
endpoint — NOT OpenAI-style dedicated endpoints.** Specifically:

| Task | Model | Endpoint | OpenAI equiv (DOES NOT WORK) |
|------|-------|----------|------------------------------|
| TTS | `mimo-v2.5-tts` | `POST /v1/chat/completions` | `/v1/audio/speech` → **404** |
| Voice Clone | `mimo-v2.5-tts-voiceclone` | `POST /v1/chat/completions` | `/v1/audio/speech` → **404** |
| Voice Design | `mimo-v2.5-tts-voicedesign` | `POST /v1/chat/completions` | `/v1/audio/speech` → **404** |
| ASR | `mimo-v2.5-asr` | `POST /v1/chat/completions` | `/v1/audio/transcriptions` → **404** |

**Correct TTS request format:**
```json
{
  "model": "mimo-v2.5-tts",
  "messages": [
    {"role": "user", "content": "<style instruction>. <text to speak>"},
    {"role": "assistant", "content": ""}
  ],
  "max_tokens": 4096
}
```

- **Both user AND assistant messages are required** (API returns 400 without
  assistant role: `"messages must contain an assistant role for TTS model"`).
- User message content: style instruction (first sentence) + text to speak.
- Response: `choices[0].message.audio` → dict with `data` key (base64-encoded
  WAV audio bytes).

**Auth**: Use `api-key` header (not `Authorization: Bearer`). A valid key
returns HTTP 200; an expired/revoked key returns 401 `Invalid API Key`.

### Hermes TTS Dispatch Architecture

**xiaomi/mimo is NOT a built-in TTS provider.** Hermes built-ins are: `edge`,
`openai`, `elevenlabs`, `minimax`, `xai`, `mistral`, `gemini`, `neutts`,
`piper`, `kittentts`.  When `tts.provider: xiaomi`, the dispatch chain is:

1. **Command provider** — checks `tts.providers.xiaomi: type: command` in config.
2. **Plugin provider** — the xiaomi TTS plugin (bundled under
   `hermes-agent/plugins/`) registers via `agent.tts_registry.register_provider()`.
   If found, calls `provider.synthesize()`.
3. **Fallthrough** — if no plugin, falls to Edge TTS default.

The bundled xiaomi plugin is in `hermes-agent/plugins/` (not the model-providers
subdirectory — that's only chat provider registration). The TTS plugin must call
`/v1/chat/completions` with the message format above.

### TTS Troubleshooting

When xiaomi TTS fails (\"No audio was received\"), check:
1. **Key validity** — `GET /v1/models` with `api-key` header. 401 = expired.
2. **Endpoint** — `/v1/audio/speech` will always 404. The plugin uses
   `/v1/chat/completions`.
3. **Fallback** — `hermes config set tts.provider edge` for free Edge TTS.
4. **Direct test** — use the Python script pattern above to verify the API works
   independently of Hermes plugin routing.

### MiMo TTS Raw API

See `references/mimo-tts-api.md` for the full request/response format, Python
example, and voice control instructions. Key points:

- Endpoint: `POST /v1/chat/completions` (NOT `/v1/audio/speech` — that 404s)
- Messages MUST include both `user` AND `assistant` roles (assistant content can
  be empty). Omitting assistant → 400.
- Response audio is in `message.audio.data` as base64-encoded WAV.
- No separate `voice` parameter — style instructions go in the user message
  content alongside the text.

### Voice Clone API Format (`mimo-v2.5-tts-voiceclone`)

Model `mimo-v2.5-tts-voiceclone` accepts a reference audio clip and synthesizes
new speech in that voice. The reference audio is passed via a top-level `audio`
object with a `voice` key containing a **data URI string** (NOT a nested object).

**Correct voiceclone request format (discovered 2026-07-20):**

```json
{
  "model": "mimo-v2.5-tts-voiceclone",
  "messages": [
    {"role": "user", "content": "要合成的文本"},
    {"role": "assistant", "content": ""}
  ],
  "audio": {
    "voice": "data:audio/mpeg;base64,<base64-encoded MP3>"
  },
  "max_completion_tokens": 65536
}
```

**Critical format notes:**

- `audio.voice` is a **bare string** (data URI), NOT an object like `{"data": ..., "format": ...}`. Passing an object returns `400: "audio.voice must not be empty for voice clone model"`.
- The reference audio MUST be base64-encoded (URL downloads not supported).
- Compress reference WAV to MP3 first (`ffmpeg -i ref.wav -ac 1 -ar 16000 -b:a 64k ref.mp3`) to stay well under the 50 MB base64 limit. A 9s WAV → 74KB MP3 → 101KB base64.
- `max_completion_tokens` (set to 65536) does NOT extend audio output — see truncation pitfall below.

**Response format** — same as regular TTS: `choices[0].message.audio.data` →
base64 WAV (24kHz mono, 16-bit).

**PITFALL — Hard ~1-second output truncation (ALL MiMo TTS models):**

**Every MiMo TTS model** (`mimo-v2.5-tts`, `mimo-v2.5-tts-voiceclone`,
`mimo-v2.5-tts-voicedesign`) hard-truncates audio output to approximately 1
second per API call, regardless of input text length or `max_tokens` setting.
Tested results (2026-07-20):

| Input chars | Model | Output duration | completion_tokens |
|:-----------:|-------|:---------------:|:-----------------:|
| 4 | voiceclone | 4.64s | — |
| 30 | voiceclone | 1.44s | 11 |
| 159 | voiceclone | 1.28s | 10 |
| 159 | regular TTS | 1.12s | 9 |
| 159 (max_tokens=65536) | voiceclone | 1.28s | 10 |

Increasing `max_completion_tokens` to 65536 had **zero effect**. This is a
**platform-level constraint** — not a parameter bug. MiMo TTS is unsuitable for
synthesizing paragraphs or multi-minute content. For long-form speech, use:
- **Local inference**: GPT-SoVITS / CosyVoice (requires GPU, ~30 min setup)
- **Other APIs**: Fish Audio, ElevenLabs, 火山引擎 TTS

Voice clone still works for short utterances (single sentences ≤ 15 chars, ~1-2s
audio), but chaining hundreds of API calls via ffmpeg concatenation is not
practical given MiMo's rate limiting (429 after ~6 requests, ~35s cooldown).

**Rate limiting:** MiMo returns HTTP 429 after approximately 6 calls. Cooldown
is ~90 seconds. For the voiceclone call pattern (~99 KB payload per call), plan
at least 90s between requests to avoid rate limits.

See `references/voiceclone-discovery.md` for the full discovery log.

### TTS Debugging Flow

See `references/hermes-tts-dispatch.md` for the full Hermes TTS dispatch
architecture and the xiaomi plugin registration path.

When xiaomi TTS fails ("No audio was received"), debug in this order:

1. **Test key validity** — `POST /v1/chat/completions` with any chat model.
   401 = expired key (fix: reissue at platform.xiaomimimo.com).
2. **Test TTS directly** — use the format in `references/mimo-tts-api.md`.
   Bypass Hermes plugin and call `/v1/chat/completions` with user+assistant
   messages. If this works but Hermes still fails, the plugin is the issue.
3. **Check endpoint** — `/v1/audio/speech` will always 404 on MiMo (MiMo TTS
   does NOT support OpenAI TTS format). Don't use this as a diagnostic.
4. **Check plugin registration** — the xiaomi TTS is registered by a bundled
   plugin at discovery time (`hermes-agent/plugins/`). If registration broke
   (e.g. after an update), dispatch falls through to Edge TTS silently.
5. **Fallback** — `hermes config set tts.provider edge` enables free Edge TTS
   immediately while debugging.

---

---------

## Hermes ASR Setup

MiMo ASR (`mimo-v2.5-asr`) uses `/v1/chat/completions` — NOT OpenAI's `/v1/audio/transcriptions`. Since Hermes has no built-in xiaomi STT provider, use the built-in `local_command` provider with `HERMES_LOCAL_STT_COMMAND`:

```bash
# 1. Copy the ASR script (see scripts/mimo_asr.py)
# 2. Set env var (in ~/.hermes/.env)
HERMES_LOCAL_STT_COMMAND=python "C:/Users/HMSJ/AppData/Local/hermes/scripts/mimo_asr.py" {input_path}
# 3. Switch STT provider
hermes config set stt.provider local_command
hermes gateway restart
```

The `{input_path}` template is replaced with the audio file path; script outputs transcription to stdout. Audio is sent as base64-encoded `input_audio` in chat completions, NOT multipart form upload.

**PITFALL**: MiMo ASR is NOT a streaming endpoint — send the full file. Pricing: ¥0.5/hour.

**PITFALL — ASR rejects text prompts**: The `mimo-v2.5-asr` model returns HTTP 400 `"ASR request must not include text parts; text prompt is injected by the gateway"` if the message content includes any `text` type part. Send ONLY `input_audio`:

```python
# ✅ CORRECT — audio only
{"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}}

# ❌ WRONG — text part causes 400
{"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}},
{"type": "text", "text": "请转写这段音频"}  # ← 400: "ASR request must not include text parts"
```

See `scripts/mimo_asr.py`.

## Audio Analysis Script

See `mimo-audio-analyzer` skill for a ready-to-use script that sends local audio files to MiMo v2.5 via base64 encoding.

## Voice Clone API

See `references/mimo-voiceclone-api.md` for the full discovery log and working `mimo-v2.5-tts-voiceclone` format (discovered 2026-07-20).

**Critical format**: `audio.voice` must be a **plain string** (data URI or raw base64), NOT a nested object. Passing `{"data": ..., "format": ...}` returns `400: "audio.voice must not be empty"`.

**⚠️ Platform hard truncation**: ALL MiMo TTS models output ~1 second of audio per call regardless of input length or `max_tokens` setting. This is a platform-level constraint, not a parameter bug. MiMo TTS is unsuitable for multi-sentence synthesis — use local GPT-SoVITS or Fish Audio for long-form voice cloning.

**Batch workaround** — for multi-sentence content under ~60s, use `scripts/batch_synth.py`:
- Splits long text into short sentences, calls voiceclone per-sentence
- 35s cooldown between calls (avoids 429 rate limits)
- ffmpeg concatenation + loudnorm at the end
- Run with system Python 3.12 (NOT execute_code) to avoid sys.path contamination
- **Ceiling**: ~30 segments produces ~40-60s total audio. For 3-minute productions (>90 segments), MiMo rate limiting makes this impractical — use Fish Audio / GPT-SoVITS instead.

---

## Testing Connectivity

### List models
```bash
curl -s "$XIAOMI_BASE_URL/models" -H "Authorization: Bearer $XIAOMI_API_KEY"
```

### Test vision with base64 image
MiMo vision API requires base64-encoded images (URL-based downloads may fail). Use `data:image/<type>;base64,...` format.

### Test chat
```bash
curl -s "$XIAOMI_BASE_URL/chat/completions" \
  -H "api-key: $XIAOMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"mimo-v2.5","messages":[{"role":"user","content":"hello"}],"max_tokens":20}'
```

---

## Notes

- **auth header**: MiMo uses `api-key` header (not `Authorization: Bearer`), though both may work.
- **Reasoning tokens**: `mimo-v2.5` and `mimo-v2.5-pro-ultraspeed` use reasoning/thinking tokens that consume `max_completion_tokens` quota. Set generous `max_tokens` to get actual content.
- **Image format**: bmp/gif/png/jpeg/webp supported. Must be base64-encoded data URL for best reliability.
- **URL images**: MiMo API may fail to download images from URLs directly. Always use base64.
- **Hermes URL safety**: Hermes vision tool validates URL safety via DNS — some URLs may be rejected before reaching MiMo. Use local files when possible.
- **Anthropic API**: MiMo supports Anthropic Messages API at `/anthropic/v1/messages` for image understanding. Uses `api-key` header.
- **Local files**: ALL MiMo models require URL or base64 — no direct file upload support.
