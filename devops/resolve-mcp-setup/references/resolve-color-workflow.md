# Resolve Color Grading Analysis Workflow

Step-by-step pattern for analyzing timeline color state via the davinci-resolve MCP. Do NOT skip steps — leads from no-context to informed decision.

## Checklist

1. **Open project + timeline**
   - `project_manager load` → `timeline list` → `timeline set_current`

2. **Evidence base (mandatory first)**
   - `media_analysis coverage_report` on the timeline
   - If 0% analyzed → state the gap before proceeding

3. **Switch to Color page**
   - `resolve_control open_page page=color`

4. **Boundary report (one clip, first on V1)**
   - `timeline_item_color grade_boundary_report` on item_index=0
   - This gives: capabilities, version state, node graph, color groups, Gallery, timeline graph

5. **Sample across timeline**
   - Probe node graphs at: item 0 (start), item N/2 (middle), item N-1 (end), and one item on a higher track (V2 or V3 index 0)
   - Use `probe_node_graph` on each
   - If all show `num_nodes: 1, lut: "", label: "", tools: null` → Resolve factory default → **ungraded timeline**

6. **Technical analysis (if needed)**
   - `media_analysis analyze_sequence depth=quick include_visuals=false include_transcription=false timed_markers=no`
   - On first run, choose `sampling_mode=fixed` (irrelevant for quick-only)
   - After completion, extract technical.json per clip → aggregate codecs, resolutions, color spaces, bit depths, framerates
   - Python extraction snippet in this file's parent SKILL.md troubleshooting section

## Interpretation

| Finding | Meaning for color |
|---------|------------------|
| All clips 8-bit h264 | Very limited grading latitude — keep CDL adjustments light; see resolve-post-production skill refs/ |
| All Rec.709, no Log/RAW | No color management pipeline needed; display-referred throughout |
| Mixed resolutions (4K + 720p + tiny) | Fix scaling before grading; rogue clips will look soft |
| Missing color_space in metadata | Resolve may misinterpret; manually set input color space in clip attributes |
| Single codec, single framerate, single gamut | No shot-matching needed between cameras — just creative look |
| Default 1-node graph on every clip | Timeline is ungraded; no creative grades to preserve |
| `tools: ["HDR"]` or similar | Clip HAS been graded — HDR wheel adjustments, RGB Mixer, etc. were applied |
| `tools: null` on node 1 | Resolve factory default corrector — NO grading applied |
| `num_nodes: 2` with tools | Multi-node grading (primary + secondary) — more sophisticated work |
| Graded clips intermixed with ungraded | Inconsistent — find the boundary (binary-search probe) |

## Visual Frame Analysis (for assessing existing grades)

After probing nodes to find graded regions, grab frames and analyze with vision:

```
1. Set playhead: timeline_markers set_current_timecode → positions in graded region
2. Grab: gallery_stills grab_and_export cleanup=false folder_path=... format=jpg
3. Vision: vision_analyze each frame asking about color palette, cast, contrast, saturation
4. Compare: check consistency across sampled positions
```

For graded scenes, the vision prompts should ask:
- Color cast consistency: is the same cast (cool/warm) present in all frames?
- Black level consistency: are shadows crushed to the same degree?
- Saturation: is it uniformly high/low across frames?
- Highlight handling: is rolloff natural or harsh?

## Deliverable Format

**User prefers visual reports over pure text for color analysis.** When the user asks for color evaluation, produce an HTML file with embedded frame images and structured analysis sections (consistency, strengths, areas for improvement, verdict). Do NOT deliver color analysis as raw text if frame images are available.

## After Analysis

- Present findings grouped by: uniform base (good), anomalies (action needed), limitations (constraints)
- Offer concrete next actions (create color groups, set CDL, import DRX, version snapshot)
- Never apply grades blindly — the control surface via API is CDL/LUT/DRX only
