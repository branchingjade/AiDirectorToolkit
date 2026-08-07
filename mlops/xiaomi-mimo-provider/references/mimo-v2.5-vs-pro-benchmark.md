# MiMo v2.5 vs v2.5-pro: Prompt Optimization A/B Test

**Date**: 2026-07-17
**Task**: Seedance 2.0 prompt optimization (Chinese script → cinematic prompt)
**Input**: 180+ character script excerpt with multi-character dialogue and action

## Results

| Dimension | v2.5 (¥1/¥2) | v2.5-pro (¥3/¥6) |
|-----------|------|------|
| Physicalization quality | ✅ Detailed (muscle groups, body parts) | ✅ Concise but accurate |
| Action chain completeness | ✅ 12 start→process→end completions | ✅ 4 completions (more selective) |
| Sound integration | ✅ 3 natural sound descriptions | ✅ 2 sound descriptions |
| Literary metaphor removal | ✅ 8 replacements | ✅ 5 replacements (missed some nuance) |
| Response speed | ~14s | ~71s (sub-agent) |
| Cost | ¥1/¥2 per MTok | ¥3/¥6 per MTok (3x) |

## Verdict

**v2.5-pro showed no detectable quality advantage** for Chinese creative/prompt optimization. Both models:
- Correctly physicalized emotional descriptions
- Preserved all dialogue verbatim
- Followed the formatting specification
- Generated valid cinematic shot descriptions

v2.5 produced richer action detail (12 vs 4 completions) while v2.5-pro was more concise. Neither was objectively better — just stylistic difference.

**Recommendation**: Use v2.5 as default for all tasks. Reserve v2.5-pro only for pure-text deep reasoning where 42B active parameters might matter (uncommon in practice).
