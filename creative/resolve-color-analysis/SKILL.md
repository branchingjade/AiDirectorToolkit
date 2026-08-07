---
name: resolve-color-analysis
description: Analyze color grading in DaVinci Resolve projects via MCP — grab frames, evaluate look consistency, and produce structured visual reports.
version: 1.0.0
category: creative
---

# Resolve Color Analysis

Analyze and evaluate color grading in DaVinci Resolve projects through the davinci-resolve MCP server. Covers frame sampling, vision-based color description, structural evaluation (consistency / strengths / improvements / verdict), and report production.

## When to Use

- User asks about color/grade/look of a specific scene, timeline, or project
- User says "分析调色"、"颜色如何"、"这场的调色"、"看一下颜色"
- User wants a visual report with screenshots and structured evaluation

## Non-Negotiable

1. **Analyze and advise only** — do NOT execute color operations (CDL writes, grade copy, DRX apply) unless explicitly asked. The user wants evaluation, not automation.
2. **MD format for reports** — never produce HTML. MD uses far fewer tokens (no CSS, no base64 image encoding). Images are local files referenced with `![](filename.jpg)`.
3. **Organized file storage** — reports and frames go under `分析/项目名/` within the Hernes working directory (`$HOME/Documents/Hermes/`), never scattered in root.

## Workflow

### 1. Understand the scope
- Ask/clarify which scene/timeline to analyze
- Open the project and set current timeline
- Use `probe_timeline_structure` to understand clip count and layout
- Probe node graphs to determine which clips are graded (check `tools` field: `["HDR"]`, `["RGB混合器"]` etc. signal active grading)

### 2. Sample frames
- Switch to **Color page** (`open_page(page="color")`)
- Move playhead with `set_current_timecode`
- Grab frames with `grab_and_export(cleanup=false, folder_path=..., format="jpg")`
- Sample 3-5 frames across the scene range (not just start/end — include middle)
- Pitfall: `cleanup=true` deletes the files after returning data; use `false` when you need them on disk for the report

### 3. Analyze each frame
- Use `vision_analyze` on each frame
- Ask specifically about: color palette, color cast, contrast, saturation, warmth/coolness, shadow/black handling, highlight handling
- For consistency check between frames, explicitly ask: "Is this consistent with the previously described frame that had [characteristics]?"

### 4. Synthesize
Structure the evaluation in this order:
```
## 一致性 — are frames unified in look? temperature shifts? contrast jumps?

## 做得对 — what the grade does well (restrained blacks on 8-bit, intentional warm accents, secondary tools that signal skill)

## 可精进 — what could improve (highlight rolloff, black level consistency, over-stylization)

## 评价 — one-paragraph verdict
```

### 5. Produce report
- MD file at `分析/项目名/报告名.md`
- Include a frame sampling table with timecodes and inline images
- Use relatively compact language — user has explicitly asked for concise, readable output
- Do NOT add HTML, CSS, or base64 images

## Resolve-Specific Knowledge

### Node graph probing
- Default Resolve state: 1 node, `tools: null`, no LUT, no label — this means UNGRADED
- `tools: ["HDR"]` on node 1 means HDR palette adjustments were made — the clip IS graded
- `tools: ["RGB混合器"]` signals secondary color work (channel-level separation)
- Pitfall: Resolve API can only tell WHICH tools exist, not their parameter values. You can confirm grading happened but can't read the exact Lift/Gamma/Gain numbers.

### Frame grabbing
- Requires Color page with a current clip selected
- `grab_and_export` is atomic (grab + export in one call), more reliable than separate grab-then-export
- Frames are grabbed at timeline resolution (1920×1080 from a 4K timeline)
- The `.drx` sidecar is always produced alongside the image — can be ignored for analysis

### Technical context for evaluation
- 8-bit h264 has very narrow grading latitude — pushing shadows up or highlights down quickly introduces banding
- Rec.709 color space means display-referred, no Log/RAW transforms needed
- HDR palette (not HDR video) is Resolve's primary correction tool — it replaces the old Lift/Gamma/Gain wheels

## Pitfalls

- `cleanup=true` deletes exported frames — use `false` when building a report that references local image files
- Item indices skip when there are gaps or non-video items on a track; `available: false` means no video clip at that index
- Gallery still grab may fail if the Gallery panel isn't open in the Color page UI — but `grab_and_export` should work regardless
