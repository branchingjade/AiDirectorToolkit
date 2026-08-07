# MiMo API Limits Reference

Extracted from https://mimo.mi.com/docs/zh-CN/ — as of 2026.06.

## Image Understanding

- **Content type**: `image_url` with `url` field
- **Formats**: JPEG, PNG, GIF, WebP, BMP
- **Size**: URL ≤ 50 MB, base64 ≤ 50 MB
- **Multi-image**: Supported (within context limits)
- **Token formula**: PATCH=16, SPATIAL_MERGE=2, min 8192px, max 8388608px. See docs for full code.
- **Anthropic API**: `/anthropic/v1/messages` with `type: "image"`, `source: {type: "url"|"base64", ...}`
- **No local file upload** — URL or base64 only

## Audio Understanding

- **Content type**: `input_audio` with `data` field
- **Formats**: MP3, WAV, FLAC, M4A, OGG
- **Size**: URL ≤ 100 MB, base64 ≤ 50 MB
- **Token**: ≈ duration(sec) × 6.25
- **No local file upload** — URL or base64 only
- **Models**: mimo-v2.5, mimo-v2-omni

## Video Understanding

- **Content type**: `video_url` with `url`, `fps`, `media_resolution` fields
- **Formats**: MP4, MOV, AVI, WMV
- **Size**: URL ≤ 300 MB, base64 ≤ 50 MB
- **fps**: 0.1-10, default 2 (higher = more temporal detail, more tokens)
- **media_resolution**: "default" or "max"
- **Token**: video_tokens (fps × resolution formula) + audio_tokens (≈6.25 × sec)
- **No local file upload** — URL or base64 only
- **Models**: mimo-v2.5, mimo-v2-omni

## Deep Think / Reasoning

- `mimo-v2.5` uses `reasoning_content` in responses
- Multi-turn agent sessions: must pass back `reasoning_content` for assistant messages containing tool calls, or API returns 400
- `reasoning_tokens` compete with `max_completion_tokens` — set generously (4096+)

## Auth

- Header: `api-key: $MIMO...- NOT `Authorization: *** (though both may work)

## V2 Deprecation Timeline

- V2-Pro/Omni/Flash: auto-routed to V2.5, deprecated 2026.6.30
- V2-TTS: auto-routed to V2.5-TTS on 2026.6.27, deprecated 2026.6.30
