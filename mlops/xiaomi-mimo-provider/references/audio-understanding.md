# MiMo Audio Understanding — API Reference

Source: https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/multimodal-understanding/audio-understanding

## API Format

Uses `input_audio` content type in chat/completions:

```json
{
  "type": "input_audio",
  "input_audio": {
    "data": "<URL or data:...;base64,...>"
  }
}
```

## Supported Models

- `mimo-v2.5`
- `mimo-v2-omni` (being deprecated)

## Audio Formats

MP3, WAV, FLAC, M4A, OGG

## Size Limits

| Method | Limit |
|--------|-------|
| URL | ≤ 100 MB per file |
| Base64 | ≤ 50 MB (encoded string size) |

## Base64 Format

```
data:{MIME_TYPE};base64,{BASE64_AUDIO}
```

Example: `data:audio/wav;base64,UklGRiQAAABXQVZFZm10...`

## Token Calculation

Total tokens ≈ audio_duration_seconds × 6.25 (estimate only; actual usage in API response)

## Multiple Audio Files

Total tokens (all audio + text) must be < model context length.

## No Local File Upload

MiMo does not support direct local file upload. Must use public URL or Base64.
