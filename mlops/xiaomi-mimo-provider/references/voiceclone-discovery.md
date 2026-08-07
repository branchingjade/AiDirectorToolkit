# MiMo Voice Clone — Format Discovery Log

**Date:** 2026-07-20
**Reference audio:** 万倩.wav (48kHz stereo, 24-bit, 9.36s)
**Goal:** Clone voice and synthesize 3-minute speech ("四季的礼物", ~730 chars)

---

## Format Discovery

### Attempts that FAILED

| # | Format | Error |
|---|--------|-------|
| 1 | `content: [{type:"input_audio", input_audio:{data:...,format:"wav"}},{type:"text",text:"..."}]` | `400: "audio must not be empty for voice clone model"` |
| 2 | `audio: {data: data_uri, format: "mp3"}` (top-level) | `400: "audio must not be empty..."` |
| 3 | `audio: {voice: {data: b64, format: "mp3"}}` (object) | `400: "audio.voice must not be empty..."` |
| 4 | `audio: b64_string` (plain string) | `400: "audio.voice must not be empty..."` |
| 5 | `audio: {voice: b64_string}` (string without data URI prefix) | `429` (rate-limited, untested) |

### Format that WORKED

```json
{
  "model": "mimo-v2.5-tts-voiceclone",
  "messages": [
    {"role": "user", "content": "测试语音。"},
    {"role": "assistant", "content": ""}
  ],
  "audio": {
    "voice": "data:audio/mpeg;base64,<base64-string>"
  },
  "max_tokens": 4096
}
```

**Key insight from error messages:**
- `"audio.voice must not be empty"` → the field name is `audio.voice`, and it expects a non-empty value
- When passing an object `{data:..., format:...}`, the API saw the voice field as "empty" because it's looking for a string, not an object
- `data URI string` works — `"data:audio/mpeg;base64,..."`

**Successful output:** 4.64s WAV (222,764 bytes, 24kHz mono 16-bit) from 4-character input "测试语音"

---

## Hard Truncation — Platform Limitation

After format was cracked, testing revealed a hard ~1-second output ceiling across ALL MiMo TTS models.

### Test Matrix

| Input chars | Model | Output duration | completion_tokens | Notes |
|:-----------:|-------|:---------------:|:-----------------:|-------|
| 4 | voiceclone | 4.64s | — | Baseline, works |
| 30 | voiceclone | 1.44s | 11 | Already truncated |
| 159 (spring paragraph) | voiceclone | 1.28s | 10 | Severe truncation |
| 159 | voiceclone (max_tokens=65536) | 1.28s | 10 | No improvement |
| 159 | regular TTS (mimo-v2.5-tts) | 1.12s | 9 | Same across all models |

### Conclusions

1. **`max_completion_tokens` has zero effect on audio output length** — tried values from 4096 to 65536 with identical results.
2. **The truncation is at the platform level**, not model-specific — `mimo-v2.5-tts`, `mimo-v2.5-tts-voiceclone`, and `mimo-v2.5-tts-voicedesign` all exhibit the same behavior.
3. **For a 3-minute (730-char) script**, brute-force chaining would require ~180 API calls × ~35s cooldown = nearly 2 hours, with high risk of 429 rate-limit failures mid-batch. **Not viable.**

---

## Rate Limiting Observations

- HTTP 429 returned after approximately **6 requests** in rapid succession
- Cooldown period: **~90 seconds** minimum
- Payload size: ~99 KB per voiceclone request (with 64kbps MP3 reference)
- The TTS `/v1/chat/completions` endpoint appears to share the same rate limit pool as chat models

---

## Migration Path

For long-form voice-cloned synthesis, MiMo voiceclone is **not viable**. Alternatives tested/recommended:

| Solution | Pros | Cons |
|----------|------|------|
| **GPT-SoVITS** (local) | No truncation, 1-shot full-text synthesis | ~30 min setup (PyTorch + models), needs GPU |
| **Fish Audio API** | Quick, no setup | Needs account + API key, 9s reference = mediocre quality |
| **CosyVoice** (local) | Good zero-shot cloning, open-source | Heavier than GPT-SoVITS, needs more VRAM |

Session was cut short during PyTorch installation for GPT-SoVITS — see memory for process state.
