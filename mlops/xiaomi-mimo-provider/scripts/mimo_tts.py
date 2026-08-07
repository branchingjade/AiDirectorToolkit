#!/usr/bin/env python3
"""MiMo TTS command provider for Hermes.
Usage: python mimo_tts.py <text> <output_path>
Reads XIAOMI_API_KEY and XIAOMI_BASE_URL from env.
"""
import sys, os, json, base64, urllib.request

text = sys.argv[1]
output_path = sys.argv[2]

api_key = os.environ.get("XIAOMI_API_KEY", "").strip()
base_url = os.environ.get("XIAOMI_BASE_URL", "https://api.xiaomimimo.com/v1").strip()

if not api_key:
    print("XIAOMI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

payload = json.dumps({
    "model": "mimo-v2.5-tts",
    "messages": [
        {"role": "user", "content": text},
        {"role": "assistant", "content": ""}
    ],
    "max_tokens": 32768
}).encode("utf-8")

req = urllib.request.Request(
    f"{base_url}/chat/completions",
    data=payload,
    headers={
        "api-key": api_key,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        msg = data["choices"][0]["message"]
        audio = msg.get("audio", {})
        audio_data = audio.get("data") if isinstance(audio, dict) else None
        if not audio_data:
            print(f"TTS error: no audio in response. Keys: {list(msg.keys())}", file=sys.stderr)
            sys.exit(1)
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(audio_data))
except Exception as e:
    print(f"TTS failed: {e}", file=sys.stderr)
    sys.exit(1)
