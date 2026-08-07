#!/usr/bin/env python3
"""MiMo Voice Clone 批量合成脚本。将长文稿拆分为短句，逐句调用 voiceclone API，
ffmpeg 拼接并响度归一化。适用于 MiMo TTS 平台硬截断（~1秒/次）的限制。

用法：python batch_synth.py
依赖：无（纯标准库 + ffmpeg）
环境：需 ~/.hermes/.env 中有 XIAOMI_API_KEY
"""

import os, json, urllib.request, base64, time, re, sys
import urllib.error

# === 配置 ===
KEY_PATH = os.path.expanduser(r"~\.hermes\.env")
OUT_DIR = os.path.expanduser(r"~\voice-clone-output")
REF_MP3 = os.path.join(OUT_DIR, "ref_64k.mp3")          # 参考音频（64kbps MP3 mono 16kHz）
API_URL = "https://api.xiaomimimo.com/v1/chat/completions"
COOLDOWN = 35                                            # 调用间隔（秒），避 429
MAX_RETRIES = 3
os.makedirs(OUT_DIR, exist_ok=True)

# 读 API key
api_key = ""
with open(KEY_PATH) as f:
    for line in f:
        if line.startswith("XIAOMI_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip('"').strip("'")
            break
assert api_key, "XIAOMI_API_KEY not found in ~/.hermes/.env"

# 编码参考音频
ref_b64 = base64.b64encode(open(REF_MP3, "rb").read()).decode()
DATA_URI = f"data:audio/mpeg;base64,{ref_b64}"


def call_voiceclone(text: str, attempt: int = 0) -> bytes | None:
    """调用 MiMo voiceclone API，返回 WAV bytes 或 None"""
    body = {
        "model": "mimo-v2.5-tts-voiceclone",
        "messages": [
            {"role": "user", "content": text},
            {"role": "assistant", "content": ""},
        ],
        "audio": {"voice": DATA_URI},
        "max_tokens": 16384,
    }
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=payload,
        headers={"api-key": api_key, "Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            r = json.loads(resp.read())
            ad = r["choices"][0]["message"].get("audio", {})
            return base64.b64decode(ad["data"]) if ad.get("data") else None
    except urllib.error.HTTPError as e:
        if e.code == 429 and attempt < MAX_RETRIES:
            wait = 60 * (attempt + 1)
            print(f"    429, waiting {wait}s...")
            time.sleep(wait)
            return call_voiceclone(text, attempt + 1)
    return None


def split_text(raw: str) -> list[str]:
    """按中文断句标点拆分，合并过短片段"""
    segments = []
    buf = ""
    for ch in raw:
        buf += ch
        if ch in "。！？":
            segments.append(buf.strip())
            buf = ""
    if buf.strip():
        segments.append(buf.strip())

    # 合并过短片段（< 8 字符）
    merged = []
    for s in segments:
        if len(s) < 8 and merged:
            merged[-1] += s
        else:
            merged.append(s)
    return merged


def main(raw_text: str):
    segments = split_text(raw_text)
    print(f"Script: {len(segments)} segments ({sum(len(s) for s in segments)} chars)")

    seg_files = []
    total_start = time.time()
    for i, seg in enumerate(segments):
        fname = os.path.join(OUT_DIR, f"seg_{i:03d}.wav")
        if os.path.exists(fname) and os.path.getsize(fname) > 500:
            seg_files.append(fname)
            print(f"[{i+1}/{len(segments)}] skip (cached)")
            continue

        wav = call_voiceclone(seg)
        if wav and len(wav) > 500:
            with open(fname, "wb") as f:
                f.write(wav)
            seg_files.append(fname)
            dur = len(wav) / (24000 * 2)
            elapsed = time.time() - total_start
            eta = (elapsed / (i + 1)) * (len(segments) - i - 1) / 60 if i > 0 else 0
            print(f"[{i+1}/{len(segments)}] ✅ {len(seg)} chars → {dur:.1f}s | ETA {eta:.0f}min")
        else:
            print(f"[{i+1}/{len(segments)}] ❌ FAILED")
        if i < len(segments) - 1:
            time.sleep(COOLDOWN)

    print(f"Done: {len(seg_files)}/{len(segments)} in {(time.time()-total_start)/60:.0f}min")

    # ffmpeg 拼接 + loudnorm
    if seg_files:
        concat_txt = os.path.join(OUT_DIR, "concat.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for sf in seg_files:
                f.write(f"file '{sf}'\n")
        final = os.path.join(OUT_DIR, "output_voiceclone.wav")
        import subprocess
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5", final,
        ], capture_output=True, timeout=120)
        if os.path.exists(final):
            import wave
            with wave.open(final, 'rb') as wf:
                dur = wf.getnframes() / wf.getframerate()
            print(f"🎉 {final}  |  {dur:.1f}s  |  {os.path.getsize(final)/2**20:.1f}MB")
        return final


if __name__ == "__main__":
    # 示例文稿
    SCRIPT = (
        "春天，总是悄悄地来。某天清晨推开窗，你会发现风里多了一丝温柔。"
        "路边柳树不知何时抽出了嫩绿的细芽儿。"
        "公园里的老人晨练，太极拳一招一式，不急不缓。"
    )
    main(SCRIPT)
