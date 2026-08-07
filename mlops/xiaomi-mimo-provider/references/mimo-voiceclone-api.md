# MiMo Voiceclone API

Discovered 2026-07-20. Working `mimo-v2.5-tts-voiceclone` format.

## Working Format

```json
POST /v1/chat/completions
{
  "model": "mimo-v2.5-tts-voiceclone",
  "messages": [
    {"role": "user", "content": "<text to speak>"},
    {"role": "assistant", "content": ""}
  ],
  "audio": {"voice": "<string>"},
  "max_tokens": 4096
}
```

**Critical discovery**: `audio.voice` must be a **plain string** (data URI or raw base64), NOT an object. `{"data": "...", "format": "..."}` returns `400: audio.voice must not be empty`.

A data URI with MIME prefix (`data:audio/mpeg;base64,...`) is accepted. Raw base64 is also accepted.

## Reference Audio Preparation

```bash
# Compress to MP3 64kbps mono 16kHz — payload stays <100KB vs ~4MB for WAV
ffmpeg -i ref.wav -ac 1 -ar 16000 -b:a 64k ref.mp3
```

## ⚠️ Hard Truncation (Platform Limit)

**Every MiMo TTS model produces ~1 second of audio per call, regardless of input length.** This is immutable — `max_tokens` and `max_completion_tokens` have no effect.

Evidence (2026-07-20):
| Model | Input chars | Output duration | completion_tokens |
|-------|:----------:|:---------------:|:-----------------:|
| voiceclone | 4 | 4.64s | — |
| voiceclone | 30 | 1.44s | 11 |
| tts | 69 | 1.92s | 14 |
| voiceclone | 159 | 1.28s | 10 |
| voiceclone + max_tokens=65536 | 159 | 1.28s | 10 |

**Conclusion**: MiMo TTS is NOT suitable for multi-sentence synthesis. Batch concatenation (one sentence per call) is theoretically possible but bottlenecked by rate limiting (~35-60s per call). For a 3-minute script → ~90 sentences → ~90 minutes minimum.

## ASR Format (also discovered)

```json
POST /v1/chat/completions
{
  "model": "mimo-v2.5-asr",
  "messages": [{
    "role": "user",
    "content": [{"type": "input_audio", "input_audio": {"data": "<b64>", "format": "wav"}}]
  }]
}
```

No assistant message needed for ASR. No text parts allowed (returns 400). Successfully transcribed a 9-second Chinese clip.

## Rate Limiting

- 429 returns rapidly with sequential requests
- Minimum 30-60s cooldown between calls
- Keep payloads under 200KB (compress ref to MP3)

## Formats Tested and Failed

| Format | Error |
|--------|-------|
| `{"audio": {"data": ..., "format": ...}}` | `audio.voice must not be empty` |
| `{"audio": "<b64>"}` | `audio.voice must not be empty` |
| `{"audio": {"voice": {"data": ..., "format": ...}}}` | `audio.voice must not be empty` |
| Content array with `input_audio` type | `audio must not be empty` |
