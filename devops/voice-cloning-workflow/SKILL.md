---
name: voice-cloning-workflow
description: "音色克隆完整工作流——平台选型、格式破解、本地方案搭建、批量合成拼接。触发词：音色克隆、voice clone、TTS训练、参考音频合成、GPT-SoVITS。"
version: 1.1.0
tags: [voice-clone, tts, gpt-sovits, cosyvoice, api, audio, chinese]
platforms: [windows, linux, macos]
---

# Voice Cloning Workflow

Class-level skill for cloning a speaker's voice and synthesizing long-form text. Covers platform selection, local environment setup, API format discovery, and batch synthesis patterns.

**⚠️ 如果用户要"替换已有音频的音色"（保留原句时长语调），这是 Voice Conversion，不是 Cloning → 见 `voice-conversion` skill。**

## Reference Audio Minimums

| Duration | Quality | Notes |
|----------|---------|-------|
| <15s | Unstable | Most platforms accept but output degrades (pitch drift, truncation) |
| 15-30s | Minimum viable | "Sounds like" but not 1:1 |
| 30-90s | Good | Sweet spot for API + local |
| 2-5 min | Excellent | Near-perfect clone |

**Always warn user if reference is under 15s** — don't just proceed silently.

## Platform Decision Tree

```
Has API key (Fish Audio / 火山引擎)?
  → Use API (5 min, no local setup)
Has GPU (RTX 3060+ 8GB)?
  → CosyVoice (easier setup, zero-shot) or GPT-SoVITS (better quality, requires build tools on Windows)
Neither?
  → User needs to provide API key or hardware — stop and explain
```

## Local Environment: GPT-SoVITS (Windows)

See `references/gpt-sovits-windows-setup.md` for step-by-step dependency installation and common compilation pitfalls.

See `references/voice-cloning-pitfalls.md` for anti-patterns and session-learned rules.

## MiMo Voiceclone API

The correct payload format for `mimo-v2.5-tts-voiceclone`:

```json
{
  "model": "mimo-v2.5-tts-voiceclone",
  "messages": [
    {"role": "user", "content": "<text to speak>"},
    {"role": "assistant", "content": ""}
  ],
  "audio": {"voice": "data:audio/mpeg;base64,<base64-encoded-ref-mp3>"},
  "max_tokens": 16384
}
```

Requirements:
- Reference audio: MP3 format, 16kHz mono, 64kbps recommended
- API key: `XIAOMI_API_KEY` in `~/.hermes/.env`
- Base URL: `https://api.xiaomimimo.com/v1/chat/completions`

**Fatal limitation**: Platform hard-truncates output to ~1-3 seconds per call regardless of input text length or `max_tokens` setting. Once confirmed, do NOT test alternative models (`voicedesign`, `tts`) — they share the same platform behavior. Viable only for batch synthesis (50-90 calls).

> Format discovery history and 429/400 error responses: `references/voice-cloning-pitfalls.md`

## Batch Synthesis Pattern (when API truncation forces it)

1. Split text by sentence-ending punctuation (`。！？`), merge segments < 8 chars with neighbors
2. Encode reference audio as MP3 (16kHz mono, 64kbps) — smaller payload, fewer 400 errors
3. Synthesize each segment independently with 10s cooldown between calls
4. **Incremental resumable**: skip already-synthesized segments (file-exists + size check → survives interrupted runs)
5. ffmpeg concat + loudnorm normalization (-16 LUFS, LRA=11, TP=-1.5)
6. Expect ~90s total from ~30 segments at ~3s/segment avg

> **Reusable script**: `scripts/batch_synth.py` — zero-dependency Python 3.12, reads `XIAOMI_API_KEY` from `~/.hermes/.env`, auto-splits script from `original/` directory, skips existing segments for fast retries.
>
> **Segments are intermediate artifacts** — persist in `intermediate/` for fast re-runs. Final output goes to `output/`.

## Pitfalls

1. **Pivot addiction** — Confirming a platform limit → testing 3 more variations anyway, wasting 10+ calls. Once a limit is confirmed, STOP. Pivot once.
2. **Dependency whack-a-mole** — Hitting one missing module → installing just that one → hitting the next → 30+ rounds. Fix: install ALL dependencies in one `requirements.txt` shot, or use system Python for zero-dep scripts.
3. **Venv contamination** — Hermes agent's venv leaking into target venv via `sys.path`. Causes `pip install` to falsely report packages as "already installed" (they're in the Hermes venv, not the target). Use `terminal` (not `execute_code`) for pip operations, or use system Python 3.12 to avoid path pollution.
4. **RTX 5060 Ti (Blackwell sm_120)** — Requires PyTorch 2.7+. PyTorch 2.6.0 only supports up to sm_90 → CUDA unavailable for local inference on this GPU.
5. **Dithering between options** — Repeatedly asking user "which direction?" after every technical bump kills momentum. Pattern: state the blocker, give ONE alternative, estimate time. Pick a default instead of a blank menu.
6. **Delivering the wrong thing silently** — When all cloning approaches failed, delivered a non-cloned Edge-TTS WAV without warning. Always flag: "This is NOT the cloned version you asked for — it's a fallback."
7. **Creating folders without permission** — Never create directories outside `~/Documents/Hermes/` without explicit user consent. When corrected, immediately clean up and migrate files to the workspace. (See `hermes-workspace-conventions` redline rule.)

> Full session-learned lessons: `references/voice-cloning-pitfalls.md`
