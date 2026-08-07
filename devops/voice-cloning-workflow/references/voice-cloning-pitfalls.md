# Session-Learned Anti-Patterns

## MiMo Voiceclone Format Discovery (2026-07-21)

The correct payload for `mimo-v2.5-tts-voiceclone`, discovered after ~10 failed attempts:

- **`audio.voice`** field: base64-encoded MP3 data URI string (`"data:audio/mpeg;base64,..."`), NOT a JSON object with `data`/`format` sub-fields
- Common 400 error: `"audio must not be empty"` — the field name was wrong (`input_audio`, `audio.data`, etc.)
- Common 400 error: `"audio.voice must not be empty"` — the value was a JSON object instead of a string
- Reference audio should be MP3 (16kHz mono, 64kbps) — smaller payload avoids size-related 400 errors
- 429 rate limiting is strict: 35-60s minimum cooldown between calls; 3-attempt exponential backoff recommended

**Hard truncation**: Platform outputs ~1-3 seconds per call regardless of `max_tokens` (confirmed with `max_tokens=65536` on 159-char input → 1.28s). Not a parameter issue — platform-level constraint.

## Unauthorized Folder Creation (2026-07-21)

Agent created `C:\voice-clone\` and `C:\Users\HMSJ\voice-clone-output\` (~4GB) without permission. User corrected: "怎么能乱建文件夹". Remedy: deleted both, migrated files to `~/Documents/Hermes/voice-clone/`, added redline rule to `hermes-workspace-conventions` skill.

## Venv Contamination (2026-07-21)

`execute_code` sandbox inherits Hermes's `sys.path` including Hermes venv's `site-packages`. When code inside `execute_code` runs `pip install` targeting a different venv, pip sees packages in Hermes's paths and reports them as "already installed" — but the target venv is empty. Result: infinite loop of installing individual packages, each succeeding but never populating the target venv.

**Fix**: Use `terminal` tool (not `execute_code`) for pip operations. Or use system Python 3.12 (`C:/Users/<user>/AppData/Local/Programs/Python/Python312/python.exe`) — system install has no Hermes path contamination.

## RTX 5060 Ti Blackwell Incompatibility (2026-07-21)

NVIDIA GeForce RTX 5060 Ti has CUDA compute capability sm_120 (Blackwell). PyTorch 2.6.0 only supports up to sm_90. Symptom: `torch.cuda.is_available()` returns True but generating a warning/crash when actually using GPU. Requires PyTorch 2.7+ or CUDA 12.8+.

## Incremental Resumable Synthesis Pattern (2026-07-21)

For batch API synthesis (when truncation forces per-segment calls):
- Save each segment to `intermediate/seg_NNN.wav`
- On re-run, skip segments where file exists AND size > 500 bytes
- This survives interrupted runs, 429 rate limits, and partial failures
- Final ffmpeg concat reads all existing segments, missing ones just leave a gap
- Script: `scripts/batch_synth.py` (zero-dependency Python 3.12)

## Pivot Addiction (2026-07-20 → 07-21)

Confirmed pattern across two sessions: MiMo voiceclone → voicedesign → CosyVoice → GPT-SoVITS → Edge-TTS across 8+ approaches. Each switch reset progress. When a platform limit is confirmed with evidence, STOP testing and decide — do not test alternative models on the same platform.

## Core Metaphor (unchanged)

The session resembled a chef who:
1. Started making pasta → water not boiling → switched to stir-fry
2. Wok not hot enough → switched to soup → broth too thin → ordered pizza
3. Delivered cold pizza and asked "which cuisine do you want?"

The user wanted pasta. Just boil the water.
