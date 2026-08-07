#!/usr/bin/env python3
"""Test MiMo vision capability for a given model.

Usage:
  python vision-test.py [model_name] [image_path]

Defaults:
  model_name: mimo-v2-omni
  image_path: auto-downloads Python logo

Example:
  python vision-test.py mimo-v2-omni /tmp/my_image.png
  python vision-test.py mimo-v2.5
"""

import urllib.request, json, base64, os, sys

# --- Load env ---
env_path = os.path.expandvars(r"$HOME\AppData\Local\hermes\.env")
env = {}
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k] = v.strip().strip('"').strip("'")

api_key = env.get("XIAOMI_API_KEY", "")
base_url = env.get("XIAOMI_BASE_URL", "https://api.xiaomimimo.com/v1")

if not api_key:
    print("ERROR: XIAOMI_API_KEY not set in .env")
    sys.exit(1)

# --- Model ---
model = sys.argv[1] if len(sys.argv) > 1 else "mimo-v2-omni"

# --- Image ---
img_path = sys.argv[2] if len(sys.argv) > 2 else None
if img_path and os.path.exists(img_path):
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    # Detect mime type from extension
    ext = os.path.splitext(img_path)[1].lower()
    mime_map = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".gif": "gif", ".bmp": "bmp", ".webp": "webp"}
    mime = mime_map.get(ext, "png")
else:
    # Download Python logo as test image
    print("Downloading test image...")
    img_url = "https://www.python.org/static/img/python-logo.png"
    img_data = urllib.request.urlopen(img_url).read()
    img_b64 = base64.b64encode(img_data).decode()
    mime = "png"

print(f"Testing model: {model}")
print(f"Image size: {len(img_b64) // 1024} KB (base64)")

# --- Call ---
data = json.dumps({
    "model": model,
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "用中文一句话描述这张图。"},
            {"type": "image_url", "image_url": {"url": f"data:image/{mime};base64,{img_b64}"}}
        ]
    }],
    "max_tokens": 200
}).encode()

req = urllib.request.Request(
    f"{base_url}/chat/completions",
    data=data,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())
        content = body['choices'][0]['message'].get('content', '')
        usage = body.get('usage', {})
        print(f"HTTP {resp.status} — OK")
        print(f"Response: {content}")
        print(f"Tokens: prompt={usage.get('prompt_tokens')}, completion={usage.get('completion_tokens')}")
        reason = usage.get('completion_tokens_details', {}).get('reasoning_tokens', 0)
        if reason:
            print(f"  (reasoning: {reason})")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"HTTP {e.code} — FAILED")
    print(body[:500])
except Exception as e:
    print(f"Error: {e}")
