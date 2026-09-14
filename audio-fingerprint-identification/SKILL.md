---
name: audio-fingerprint-identification
description: 识别未知音频/检测串烧 mashup/查撞旋律——AudD.io 零凭据识别 + 多切片采样诊断法。
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [audio, fingerprint, identification, mashup, plagiarism, audd]
    related_skills: [song-analysis, music-transcription, mimo-audio-analyzer]
---

# 音频指纹识别 / 撞旋律检测

## When to Use

用户给一段音频（wav/mp3/m4a），要回答以下任一问题：
- 这是什么歌？（识别未知歌曲）
- 这首歌撞了哪首歌？（查旋律/歌词抄袭）
- 这是不是串烧/mashup？（多歌拼接检测）
- 这是不是 AI 生成的多语种拼贴？（Suno/Udio/短视频模板输出）

**核心方法 = AudD.io 零凭据识别 + 多时间点切片采样诊断法**。一次识别回答不了"撞旋律"——必须切多段，每段独立识别。

## AudD.io 零凭据识别（首选，10 次/天免费）

AudD 是 Shazam 同类商业级音频指纹服务，**免费 tier 用 `api_token=test` 即可**，免注册、无 key，每天 10 次请求上限（2026-08 实测有效）。

### 标准识别端点

```bash
# 单段 30 秒以内识别
curl -s -X POST "https://api.audd.io/" \
  -F "file=@/path/to/clip.mp3" \
  -F "api_token=test" \
  -F "return=apple_music,spotify"
```

响应结构：
```json
{
  "status": "success",
  "result": {
    "artist": "Saroja",
    "title": "Raas",
    "album": "Gautam",
    "release_date": "2025-04-21",
    "timecode": "01:04",
    "song_link": "https://lis.tn/Raas"
  }
}
```

**关键字段解读**：
- `result: null` = 该段未匹配（曲库无此歌/纯原创/AI 瞎生成/前奏无 hook）
- `timecode` = AudD 在原音频中识别到的匹配时间点（不是 mp3 自己的时间戳，是被识别歌曲在源音频中的出现位置）
- `song_link` (lis.tn) = Shazam 同款的短链，可在浏览器打开看到 Apple Music/Spotify 链接

### 限制

- 标准端点单文件 ≤ 10 MB（30 秒以内 128kbps mp3 ≈ 470KB，绰绰有余）
- 分析窗口 ≈ 12 秒（所以 30 秒片段已包含足够信息）
- 超过 12 秒一般没帮助——切短别切长

## 多切片采样诊断法（核心技巧）

**单点识别回答不了"撞旋律"问题**——必须多时间点采样，组合识别结果下结论。

### 采样策略

音频时长 ≥ 4 分钟的歌，至少切 **5 段**：
- 0:30（前奏/人声未起，常未识别——正常）
- 1:00 / 1:30（主歌 A 段）
- 2:00 / 2:30（副歌 B 段）
- 3:00（间奏/桥段）
- 4:00（落段/终副歌）

**切片命令**（Windows MSYS / git-bash 通用）：
```bash
for ts in 30 60 90 120 150 180 210 240; do
  ffmpeg -y -i input.wav -ss $ts -t 20 -vn -ac 1 -ar 16000 -b:a 128k "clip_${ts}.mp3"
done
```

参数说明：
- `-ss $ts`：从 $ts 秒开始切
- `-t 20`：切 20 秒（足够 AudD 12 秒分析窗口）
- `-ac 1 -ar 16000`：单声道 16kHz（mp3 不需要高保真）
- `-b:a 128k`：128kbps（10MB 限制下质量绰绰有余）

### 结果判读（4 种典型模式）

| 模式 | 表现 | 结论 |
|---|---|---|
| **A. 同首歌** | N 段都识别到同一首 | 是已知歌，可直接给链接 |
| **B. 串烧/Mashup** | N 段识别到 N 首不同的歌 | 这就是串烧本身，不是撞旋律 |
| **C. 部分原创** | 部分段 NONE、部分段同首 | 原创 + 引用某首歌的某段 |
| **D. 多语种乱炖** | N 段识别到不同语言/地区的歌（Bhojpuri/泰米尔/阿拉伯/粤语）| **高度疑似 AI 生成**（Suno/Udio 全球风 mashup）|

模式 B/C/D 都没法直接回答"撞了 X 歌"——因为音频本身就是拼的。

### 实测案例（2026-08-21，4:27 长音频）

```
clip_0_30       → NONE
clip_60_80      → RELAX WORLD — Sky Shower (英文白噪音)
clip_90_110     → Rishi Raushan Yadav — Deewana Ke Maar Gayilu (印地语)
clip_120_150    → Saroja — Raas (印尼/泰米尔)
clip_150_180    → سحر حبيبة — إنتي ملكة على عرشك (阿拉伯语)
clip_240_260    → Sanjay Chauhan — Bhukh Pyas Lage Nahi (印地语)
```

**模式 D**——四语种 + 大量 DistroKid 自助发行号段（8996756 Records DK）= AI 生成的多语种 mashup。无"撞 X 歌"答案。

## 撞旋律问题的诚实边界

**仅靠音频指纹**回答不了"撞旋律"——指纹只能告诉你"是或不是这首"，不能告诉你"和这首像不像"。

要精确比对撞旋律，需要：
1. **MFCC/chroma 特征相似度**：拿两段音频提梅尔频谱算余弦相似度（参考 songsee 技能）
2. **段落级匹配**：AudD 给出的 `timecode` 是关键——如果用户怀疑的歌 B 在用户音频 A 的 1:04 出现，那 A 在 1:00-1:04 段大概率就是 B
3. **歌词文本比对**：拿到歌词后做 n-gram 比对

如果用户给的是"我觉得像 X 歌"，正确路径是：
- 用 AudD 切几段定位 X 歌在音频中的位置（看 `timecode` 字段）
- 用 MiMo audio understanding（mimo-audio-analyzer）拿歌词文本
- 文本比对

## 与手机 Shazam 的关系

**AudD.io 是 Shazam 的服务端等价物**——同样基于音频指纹识别，同一算法，1.6 亿曲库。用户手机上 Shazam 能识别的，AudD 也能识别；反之亦然。

什么时候该让用户手机 Shazam 兜底：
- AudD 10 次免费额度用完
- 用户怀疑的曲目非常冷门（AudD 库可能没覆盖）
- 用户希望直接看 Apple Music/Spotify 链接（AudD `return=apple_music,spotify` 也行）

## 与 MiMo audio understanding 的分工

| 工具 | 擅长 | 不擅长 |
|---|---|---|
| **AudD** | "这是什么歌"（曲名/艺人/专辑） | 歌词文本、风格分析、情绪识别 |
| **MiMo v2.5** | 歌词转写、风格/情绪/乐器分析、提问式查询 | 识别曲名（不返回歌名） |

**音频分析第一步先 AudD 拿曲名**——拿到曲名后再决定要不要 MiMo 转歌词做文本比对。不要一上来就用 MiMo 转音频浪费 token（4 分钟音频 ≈ 1675 token，按 6.25/s 算）。

## Pitfalls

- **不要单次识别下结论**：一次 `result: null` 不代表"不是歌"——可能是前奏无 hook、切到间奏、或采样位置不巧。**永远多切几段**
- **`timecode` 字段含义易误解**：是 AudD 在**你的音频里**识别到匹配的开始时间，不是 mp3 文件自己的时间戳。例如 `timecode: "01:04"` 表示在源音频第 64 秒处匹配到该歌
- **免费额度有限**：`api_token=test` 每天 10 次。规划切片数——5 段诊断 + 2 段精确定位 = 7 次，留 3 次给异常
- **10MB 限制**：标准端点不接收大文件。如果用户给的是 wav（通常 30MB/分钟），**必须先 ffmpeg 转 mp3 128kbps**（4 分钟音频约 4MB mp3）
- **印度/印尼/阿拉伯 remix 误识别**：DistroKid 自助发行号段（9999 Records DK 类）+ 非英语艺人名 = 高度可能是 AI 生成噪声，不是真撞旋律。看到 Saroja / Sanjay Chauhan / سحر 这种名字+小语种+自助发行号组合，**直接下结论"AI 串烧"**，别继续抠细节

## 实测验证

- 2026-08-21 4:27 wav 音频 5 切片识别出 4 种语言/地区的不同歌，确认模式 D（AI 多语种串烧），调用 5/10 免费额度
