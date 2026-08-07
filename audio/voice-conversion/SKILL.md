---
name: voice-conversion
description: "音色替换（Voice Conversion）——将已有音频中A的声音替换为B的音色，保留语调、节奏、停顿。非TTS、非声音克隆。触发词：音色替换、voice conversion、变声、timbre transfer、换音色。"
version: 1.0.0
tags: [voice-conversion, rvc, seed-vc, audio, timbre, post-production]
platforms: [windows, linux, macos]
related_skills: [voice-cloning-workflow]
---

# Voice Conversion（音色替换）

Class-level skill for converting one speaker's timbre to another while preserving all prosodic features (timing, intonation, pauses, emotion).

## ⚠️ 与 Voice Cloning 的区别

| | Voice Conversion (本 skill) | Voice Cloning (voice-cloning-workflow) |
|---|---|---|
| **输入** | 已有音频（A 说话的录音） | 文本 |
| **输出** | 同一段话，音色变成 B | B 的声音读任意文本 |
| **保留** | 原句时长、语调、停顿、情感 | 不保留（重新合成） |
| **典型工具** | RVC, Seed-VC, Applio | GPT-SoVITS, CosyVoice, Fish Speech |

**关键判断**：用户说"把这句话换成 X 的声音" → VC（本 skill）。用户说"用 X 的声音念这段文字" → TTS+克隆（voice-cloning-workflow）。

## 工具选型决策树

```
需要零样本（不想训练）？
  → Seed-VC v2（给 1-30s 参考音频即可）
  → 质量中等，适合快速试听
需要最高质量？
  → RVC（训练 10min 音频 → 模型）
  → 质量最好，社区最大（36.5K ⭐）
需要简单界面？
  → Applio（RVC 封装，MIT 协议，3.5K ⭐）
需要实时变声（直播/通话）？
  → voice-changer（w-okada，20.6K ⭐）
```

## RVC（首选方案）

**GitHub**: RVC-Project/Retrieval-based-Voice-Conversion-WebUI（36.5K ⭐，活跃）

### 工作流
1. 收集目标人（B）干净语音，10 分钟左右
2. RVC WebUI 训练模型（RTX 5060 Ti 约 10-15 分钟）
3. 导出原句音频（WAV）从 DAW/Resolve
4. RVC 转换：输入原句 → 输出 B 音色版本
5. 导回 DAW，对齐原句时间线

### 关键参数
- **f0 提取算法**: RMVPE（推荐，中文效果好）/ CREPE / PM
- **Index Rate**: 控制检索匹配强度，0.5-0.75 通常最佳
- **Pitch Shift**: 通常 0（不移调），除非原句和目标音域差距大
- **Filter Radius**: 平滑度，3-7 为常用范围

### 实时模式
- 延迟 ~170ms（普通）/ ~90ms（ASIO）
- 适合预览监听，最终输出用离线模式

## Seed-VC v2（零样本方案）

**GitHub**: Plachtaa/seed-vc（3.9K ⭐）

### 特点
- 零样本：不需要训练，直接给参考音频
- 使用 hubert-bsqvae-small 模型，专门抑制源说话人特征
- 支持实时和离线

### 工作流
1. 准备目标人（B）参考音频 1-30 秒
2. 输入原句音频 + 参考音频
3. 直接输出转换结果

### 局限
- 质量略低于训练后的 RVC
- 对参考音频质量敏感（需干净、无背景音）

## Applio（RVC 友好封装）

**GitHub**: IAHispano/Applio（3.5K ⭐，MIT，2026-07 仍活跃）

- 底层是 RVC，但界面更直观
- 适合不想折腾 RVC WebUI 配置的场景
- 支持语音、歌声、实时变声

## ⛔ 已废弃工具

| 工具 | 状态 | 说明 |
|------|------|------|
| **So-VITS-SVC** | ❌ 2023.11 归档 | 不再维护，不推荐新项目使用 |
| **OpenVoice** | ⚠️ 2025.04 停更 | 主要是克隆，VC 能力弱 |

## 商业方案（即开即用）

| 产品 | 类型 | 适用场景 |
|------|------|---------|
| **ElevenLabs Voice Changer** | API/网页 | 最方便，按量付费 |
| **Respeecher** | API | 影视级，好莱坞用过，贵 |
| **Descript** | 桌面端 | Overdub 功能，但是 TTS 不是纯 VC |
| **Kits.AI** | 网页 | 偏音乐制作 |

## 后期制作工作流（DaVinci Resolve）

1. **导出**：Resolve → 选中目标句 → Export WAV（Timeline > Export > Audio）
2. **转换**：RVC WebUI / Seed-VC 处理
3. **导入**：Resolve Media Pool → 拖入时间线对齐
4. **对齐**：用波形对齐原句起止点
5. **微调**：EQ/压缩与原素材匹配（避免"贴上去"的感觉）

## Pitfalls

1. **VC ≠ Cloning 混淆** — 用户说"替换音色"是 VC，说"用他的声音念"是 TTS 克隆。选错方向全白做。先确认需求再动手。
2. **So-VITS-SVC 还推荐** — 已于 2023.11 归档，不再维护。只推 RVC / Seed-VC / Applio。
3. **GPT-SoVITS 当 VC 用** — 它是 TTS 工具，不能保留原句时长语调。用户要保留原句节奏 → 必须用 VC 工具。
4. **参考音频质量** — RVC 训练数据和 Seed-VC 参考音频都要求干净人声。有 BGM/噪声 → 先用 UVR 或 Demucs 分离。
5. **音域差距大不移调** — 男声转女声（或反之）时，Pitch Shift 设 0 会导致不自然。差 12 半音以上考虑移调。
6. **直接给结论不绕圈** — 用户问"找方案" → 给方案表，不问"你想用哪种"。用户自己选。
