# 飞书语音/音频能力

## 核心结论

飞书**不支持原生语音气泡**。`msg_type="audio"` 本质是**文件附件**，不是 Telegram/Discord 那种内联语音条。

## 源码分析

### 飞书消息类型

飞书 API 支持的消息类型中没有 `voice` 类型：
- `text`、`post`（富文本/Markdown）、`image`、`file`、`audio`（音频文件）、`media`（视频）、`share_chat`、`share_user`、`sticker`

`audio` 即文件附件——对方看到的是文件名+播放按钮，需要手动点击。

### adapter.py 的实现

```python
# 第177行 — Opus 文件上传类型映射
_FEISHU_OPUS_UPLOAD_EXTENSIONS = {".ogg", ".opus"}

# 第4926-4941行 — 文件路由决策
def _resolve_outbound_file_routing(file_path, requested_message_type):
    ext = Path(file_path).suffix.lower()
    if ext in _FEISHU_OPUS_UPLOAD_EXTENSIONS:
        return "opus", "audio"   # file_type="opus", msg_type="audio"
    ...

# 第2106-2123行 — send_voice 实现
async def send_voice(self, chat_id, audio_path, ...):
    """Send audio to Feishu as a file attachment plus optional caption."""
    return await self._send_uploaded_file_message(
        chat_id=chat_id,
        file_path=audio_path,
        outbound_message_type="audio",
    )
```

流程：`.opus`/`.ogg` 文件 → `im.v1.file.create` 上传（file_type="opus"）→ 返回 file_key → 发 `msg_type="audio"` 消息 → 飞书端显示为**音频文件附件**。

### 支持的音频扩展名

```python
_AUDIO_EXTENSIONS = {".ogg", ".mp3", ".wav", ".m4a", ".aac", ".flac", ".opus", ".webm"}
```

所有格式统一走文件上传+附件消息路径，无格式转换。

## 跨平台语音能力对比

| 平台 | 语音气泡 | 语音频道推流 | Hermes 适配器 |
|------|---------|-------------|--------------|
| Telegram | ✅ 原生 Opus 语音条 | ❌ | ✅ 内置 |
| Discord | ✅ 原生语音条 | ✅ VC 加入说话 | ✅ 内置 |
| 飞书 | ❌ 仅文件附件 | ❌ | ✅ 内置 |
| 微信 | ❌ 无 send_voice | ❌ | ✅ 内置 |
| 黑盒语音 | ❌ | ✅ 推流 API | ❌ 需自建 |

## 实践建议

- **要语音气泡体验**：只能用 Telegram 或 Discord
- **飞书上用语音**：用户需下载/点击文件播放，体验差
- **黑盒语音**：可推流到语音频道（Bot 直接出声），但也不是语音气泡，需自建适配器
