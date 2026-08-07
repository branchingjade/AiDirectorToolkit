# MiMo TTS API — Raw Format

As of 2026.06, MiMo TTS (v2.5) does **not** use OpenAI's `/v1/audio/speech`.
It uses the standard `/v1/chat/completions` endpoint with a specific message
structure.

## Endpoint

```
POST https://api.xiaomimimo.com/v1/chat/completions
```

## Request

```json
{
  "model": "mimo-v2.5-tts",
  "messages": [
    {
      "role": "user",
      "content": "<style instruction + text to speak>"
    },
    {
      "role": "assistant",
      "content": ""
    }
  ],
  "max_tokens": 4096
}
```

**Critical**: the `assistant` role message MUST be present. Omitting it returns
`400: "messages must contain an assistant role for TTS model"`.

The `user` message contains both the voice style description (natural language)
and the text to synthesize — no separate `voice` or `style` parameters.

## Response

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "",
      "audio": {
        "data": "<base64-encoded WAV>"
      }
    }
  }]
}
```

The `message.audio.data` field contains the raw WAV audio as base64. Decode and
write to a `.wav` file — no additional transcoding needed.

## Python Example

```python
import json, base64, urllib.request

payload = json.dumps({
    "model": "mimo-v2.5-tts",
    "messages": [
        {"role": "user", "content": "低沉说书人声音。关云长，河东解良人。"},
        {"role": "assistant", "content": ""}
    ],
    "max_tokens": 4096
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.xiaomimimo.com/v1/chat/completions",
    data=payload,
    headers={
        "api-key": "<YOUR_KEY>",
        "Content-Type": "application/json; charset=utf-8"
    },
    method="POST"
)

with urllib.request.urlopen(req, timeout=60) as resp:
    data = json.loads(resp.read())
    audio_b64 = data["choices"][0]["message"]["audio"]["data"]
    with open("output.wav", "wb") as f:
        f.write(base64.b64decode(audio_b64))
```

## Auth

- Header: `api-key: <key>` (NOT `Authorization: Bearer`)
- Key from https://platform.xiaomimimo.com
- TTS is free (limited-time promotion as of 2026.06)

## Voice Control

The `user` message content serves as both style prompt and text. Style
instructions are placed in the same content field as natural language
prefix before the actual text. Example style prompts:

- `低沉沙哑，像个历经沧桑的老前辈在讲述传奇人物。`
- `明亮活泼，语速稍快，像在分享好消息。`
- `温柔平静，像在给小孩子讲故事。`

The model auto-infers character voice and emotion from the style description.
Multi-character dialogue with distinct voices is also supported.

## Pitfalls

1. **Forgetting the assistant message** → 400 error
2. **Using `/v1/audio/speech`** → 404 (MiMo does not support OpenAI TTS format)
3. **Using `Authorization: Bearer` header** → may work but use `api-key` for reliability
4. **Expired API key** → 401 on any endpoint; test with `/v1/models` first
5. **VoiceClone: text in wrong role** → ~1 second output (NOT platform truncation, a format error). Text must go in `role: assistant`, `role: user` must be empty. See `references/voiceclone-format.md`.
