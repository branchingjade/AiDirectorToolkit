#!/usr/bin/env python3
"""MiMo ASR via /v1/chat/completions — called by Hermes local_command STT provider.
Usage: python mimo_asr.py <input_audio_path>
Output: transcription text to stdout

Setup:
  1. Copy to ~/.hermes/scripts/mimo_asr.py
  2. In ~/.hermes/.env:
     HERMES_LOCAL_STT_COMMAND=python "C:/Users/HMSJ/AppData/Local/hermes/scripts/mimo_asr.py" {input_path}
  3. hermes config set stt.provider local_command
  4. hermes gateway restart

MiMo ASR uses /v1/chat/completions (NOT /v1/audio/transcriptions).
Audio is sent as base64-encoded input_audio in the message content.
Pricing: ¥0.5/hour.
"""
import base64, json, os, sys, urllib.request

API_KEY = os.environ["XIAOMI_API_KEY"]
BASE_URL = os.environ.get("XIAOMI_BASE_URL", "https://api.xiaomimimo.com/v1")


def main():
    if len(sys.argv) < 2:
        print("Usage: python mimo_asr.py <audio_path>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    format_map = {"wav": "wav", "mp3": "mp3", "flac": "flac", "m4a": "m4a", "ogg": "ogg"}
    audio_fmt = format_map.get(ext, "wav")

    with open(path, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    payload = json.dumps({
        "model": "mimo-v2.5-asr",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "input_audio", "input_audio": {"data": audio_b64, "format": audio_fmt}},
                {"type": "text", "text": "请转写这段音频为中文文本。只输出转写结果，不要添加任何解释。"}
            ]
        }],
        "max_tokens": 4096
    }).encode()

    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=payload,
        headers={"api-key": API_KEY, "Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            text = result["choices"][0]["message"]["content"].strip()
            print(text)
    except Exception as e:
        print(f"MiMo ASR error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
