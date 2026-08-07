#!/usr/bin/env python3
"""
MiMo Audio Analyzer - Analyze audio files using MiMo v2.5 audio understanding.
Usage: python3 mimo_audio.py <audio_file> [question]
"""

import base64, json, os, sys, urllib.request, urllib.error

API_KEY = os.environ.get('XIAOMI_API_KEY', '')
if not API_KEY:
    print("ERROR: XIAOMI_API_KEY not set. Run: source ~/.hermes/.env")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python3 mimo_audio.py <audio_file> [question]")
    sys.exit(1)

audio_path = sys.argv[1]
question = sys.argv[2] if len(sys.argv) > 2 else "请详细分析这段音频：有什么声音元素（乐器、人声、环境音）？描述氛围、节奏、时长。"

# Read and encode
with open(audio_path, 'rb') as f:
    audio_bytes = f.read()

b64 = base64.b64encode(audio_bytes).decode()
b64_size = len(b64) / 1024 / 1024

if b64_size > 50:
    print(f"ERROR: Base64 size {b64_size:.1f} MB exceeds 50 MB limit")
    sys.exit(1)

# Detect MIME type from extension
ext = os.path.splitext(audio_path)[1].lower()
mime_map = {'.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.flac': 'audio/flac',
            '.m4a': 'audio/mp4', '.ogg': 'audio/ogg'}
mime = mime_map.get(ext, 'audio/wav')

print(f"文件: {os.path.basename(audio_path)} ({len(audio_bytes)/1024/1024:.1f} MB)")
print(f"Base64: {b64_size:.1f} MB | MIME: {mime}")
print("分析中...")

# Build request
body = json.dumps({
    'model': 'mimo-v2.5',
    'messages': [
        {'role': 'system', 'content': '请用中文回答。'},
        {'role': 'user', 'content': [
            {'type': 'input_audio', 'input_audio': {'data': f'data:{mime};base64,{b64}'}},
            {'type': 'text', 'text': question}
        ]}
    ],
    'max_completion_tokens': 4096
}).encode()

req = urllib.request.Request(
    'https://api.xiaomimimo.com/v1/chat/completions',
    data=body,
    headers={'api-key': API_KEY, 'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read())

    msg = result['choices'][0]['message']
    usage = result['usage']
    
    print(f"\n--- Token 用量 ---")
    print(f"  总输入: {usage['prompt_tokens']} (音频: {usage['prompt_tokens_details']['audio_tokens']})")
    print(f"  总输出: {usage['completion_tokens']} (推理: {usage['completion_tokens_details']['reasoning_tokens']})")
    print(f"--- 分析结果 ---\n")
    
    content = msg.get('content', '')
    if content:
        print(content)
    else:
        print(f"(无输出 - finish_reason={result['choices'][0]['finish_reason']},推理tokens可能耗尽)")
        if msg.get('reasoning_content'):
            print(f"\n[推理过程]\n{msg['reasoning_content'][:500]}...")

except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()}")
    sys.exit(1)
