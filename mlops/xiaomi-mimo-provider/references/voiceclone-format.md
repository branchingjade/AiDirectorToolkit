# MiMo VoiceClone API — 已知格式与陷阱

## 正确格式（2026-07-21 查阅官方文档后修正）

```json
{
  "model": "mimo-v2.5-tts-voiceclone",
  "messages": [
    {"role": "user", "content": ""},
    {"role": "assistant", "content": "<要朗读的文本>"}
  ],
  "audio": {
    "voice": "data:audio/mpeg;base64,<base64编码的参考音频>",
    "format": "wav"
  },
  "max_tokens": 65536
}
```

**关键发现**：
- `audio.voice` 必须是**纯字符串**（data URI），不是对象，不是嵌套字典
- **CRITICAL — 文本必须放在 `role: assistant` 的 content 中，`role: user` 留空**
- 参考音频用 MP3 格式（`data:audio/mpeg;base64,...`），ffmpeg 压缩后可大幅缩小 payload

## 重大踩坑：文本放错角色 → 50+ 轮误判为"平台截断"

**2026-07-20 整天的测试全用错了格式：** 把文本放在 `role: user`、`role: assistant` 留空——导致 API 每次只输出 ~1 秒音频。这个 1 秒截断被误判为"MiMo 平台级限制"，触发逐句拆分、本地 GPT-SoVITS、Edge-TTS 兜底等无意义操作。

**真相（2026-07-21 查阅官方文档后确认）：** voiceclone 的文本应在 `role: assistant`。修正后一次调用输出 **130 秒完整音频**（696 chars 文稿，completion_tokens=815）。

### 错误格式（导致 ~1s 截断）
```json
"messages": [
  {"role": "user", "content": "大段文本"},
  {"role": "assistant", "content": ""}
]
```

### 正确格式（完整输出）
```json
"messages": [
  {"role": "user", "content": ""},
  {"role": "assistant", "content": "完整文稿文本"}
]
```

## 铁律：先查文档，禁止盲调

**反面案例**：整整 50+ 轮 API 调用、无数次 format tweak、切换到 4 个不同方案——全部因为没看官方文档。用户明确给了文档链接（`https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/speech-synthesis-v2.5`），但 agent 一再推迟查阅、优先尝试试错。

**规则**：当用户给出官方文档链接时，立即打开并对照调用格式，然后再发 API 请求。

## VoiceClone 模型列表（来自官方文档）

| Model | 用途 | 音色来源 |
|-------|------|----------|
| `mimo-v2.5-tts` | 预置音色合成 | 冰糖/茉莉/苏打/白桦 等 |
| `mimo-v2.5-tts-voicedesign` | 文本描述设计音色 | 文本 prompt |
| `mimo-v2.5-tts-voiceclone` | 基于音频复刻音色 | 参考音频文件 |
