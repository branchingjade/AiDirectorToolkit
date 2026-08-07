# Workspace Directory Conventions

Supplementary redline rule for `hermes-workspace-conventions`. Documents special project directory templates and the cleanup procedure when unauthorized folders are created.

## Core Redline

**Never create directories outside `~/Documents/Hermes/` without explicit user consent.**

This includes:
- Any drive root (`C:\`, `D:\`, etc.)
- User profile subdirectories other than `Documents/Hermes/`
- System temp directories used as "permanent" storage

When corrected by the user, the cleanup procedure is:
1. Immediately acknowledge the mistake
2. Copy/move all files to `~/Documents/Hermes/<project-name>/`
3. Delete the unauthorized directories
4. Do NOT ask "should I delete?" — just do it and report what was cleaned

## Voice Clone Project Template

For voice cloning projects, use this directory structure under `~/Documents/Hermes/`:

```
voice-clone/
├── original/           ← Reference audio + reading script (immutable inputs)
│   ├── 万倩.wav
│   └── 四季的礼物_文稿.txt
├── intermediate/       ← Per-segment synthesis outputs, concat lists (rebuildable)
│   ├── seg_000.wav
│   ├── seg_001.wav
│   └── concat_list.txt
├── output/             ← Final deliverables (WAV files, NOT intermediate artifacts)
│   ├── 四季的礼物_voiceclone.wav
│   └── 四季的礼物_edge_tts.wav
└── scripts/            ← Reusable synthesis/splitting scripts
    └── batch_synth.py
```

**Rationale**: `original/` is immutable (never delete), `intermediate/` is rebuildable (safe to clean), `output/` is the user-facing deliverable. This maps directly to the batch synthesis workflow's incremental resumable pattern.

## Other Special Projects

| Project Type | Template | Notes |
|-------------|----------|-------|
| Analysis reports | `分析/<project>/` with `assets/` subdir | MD cites images as relative paths |
| Scripting/storyboards | `分镜/` | Creative outputs, not analysis |
| Software dev | `Projects/<name>/` | Has independent git repo |
| Plugins/extensions | `Plugins/<category>/` | Archived releases, not development |
