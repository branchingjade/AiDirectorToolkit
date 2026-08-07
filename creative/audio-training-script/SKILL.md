---
name: audio-training-script
description: "音频训练/校准用朗读文稿设计——参数推算、语言学特征覆盖、格式规范。触发词：音频训练、TTS训练文本、ASR校准文本、朗读文稿。"
version: 1.0.0
tags: [audio, training, tts, asr, chinese, linguistics, prompt-design]
platforms: [windows, linux, macos]
---

# Audio Training Script Design

Class-level skill for designing reading scripts for TTS training, ASR calibration, or voice model fine-tuning. Covers parameter estimation, linguistic coverage, and delivery formatting.

## Parameter Estimation

| Goal duration | Speaking rate | Recommended chars | Sentences | Paragraphs |
|:-------------:|:-------------:|:-----------------:|:---------:|:----------:|
| 3 minutes | 220-280 字/分钟 | 650-780 | 30-45 | 4-5 |
| 5 minutes | 220-280 字/分钟 | 1100-1400 | 50-70 | 6-8 |
| 10 minutes | 220-280 字/分钟 | 2200-2800 | 100-140 | 10-15 |

Sentence length: 10-25 characters natural. Paragraph gaps: 1.5-2 seconds recommended.

## Design Constraints for Training Scripts

Training scripts differ from ordinary text — they must deliberately cover specific linguistic features:

### Chinese-Specific (Mandarin)

| Feature | Requirement | Verification |
|---------|------------|-------------|
| Four tones (1-4) | Uniform distribution | Spot-check: pick 5 random chars, verify all 4 tones present |
| Neutral tone (轻声) | Multiple occurrences | Common words: 孩子, 我们, 时候, 笑着, 凉凉的 |
| Retroflex vs alveolar | zh/ch/sh/r vs z/c/s | Both sets must appear |
| n/l contrast | Both initials present | 暖(n) vs 路(l) as minimum|
| "一/不" sandhi | Trigger contexts needed | e.g. 一阵阵(yí), 不过(bú) |
| Third-tone sandhi | Two 3rd tones in sequence | e.g. 好心情 (3-3→2-3) |
| Interrogative sentence | At least 1 | "你有没有想过……？" |
| Exclamatory | At least 1 | "笑声比雷声还响亮！" |
| Imperative | At least 1 | Minimal: "珍惜当下" |
| Erhua (儿化) | Moderate | 小孩儿, 雪片儿, 香味儿 — don't overdo |

### Delivery Preferences

- Output as plain text in a code block — user wants clean copy-paste
- No SSML or markup unless explicitly requested
- Paragraphs separated by blank lines
- Each paragraph labeled with season/section header in bold

## Example: "四季的礼物" (730 chars, ~3 min)

See `examples/chinese-tts-training-scripts.md` for the full manuscript with linguistic annotations.

## Pitfalls

1. **Over-engineering the linguistic coverage** → text reads unnatural. Balance coverage with readability.
2. **Forgetting paragraph breaks** → script becomes a wall of text. Use clear section separators.
3. **Using technical/domain vocabulary** that training speakers may mispronounce. Keep vocabulary conversational.
4. **Asking user "what theme?" without first suggesting a concrete one** → just write a seasonal/daily-life script; it naturally covers all linguistic features.
