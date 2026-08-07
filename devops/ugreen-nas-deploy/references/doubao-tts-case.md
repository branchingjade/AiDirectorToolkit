# 豆包音频生成 API（POST /api/v3/tts/create）速查

来源：docs.volcengine.com/docs/6561/2550782（2026-07 抓取）+ 多轮实测。

## 端点与鉴权

- `POST https://openspeech.bytedance.com/api/v3/tts/create`
- Header：`X-Api-Key`（新版控制台单头鉴权）；可选 `X-Api-Request-Id` 追踪

## 关键行为（实测，文档没写清）

- **成功响应没有 `code` 字段**，只有 `audio`/`url`/`duration`。判错：`code = data.get("code"); if code is not None and code != 0`。**禁止**写 `data.get("code", -1)`——成功时缺省 code 会被误判成 -1。
- 成功字段：`audio`(base64) / `url`(CDN 链接，2h过期) / `duration`(变速后) / `original_duration`(原始=计费时长，上限120s) / `subtitle`(需 enable_subtitle=true)
- **图片参考与音频参考互斥**：不能同传
- 纯文本生成模式：不传 references，音色完全由 text_prompt 中的自然语言描述决定（非"默认音色"）

## 请求体

| 字段 | 说明 |
|------|------|
| model | `seed-audio-1.0`（中英）/ `seed-audio-1.0-multilingual`（18语种 + text_prompt 时间轴控制 `[2s:5s]`） |
| text_prompt | ≤3000 字符；纯文本 / `@音频N` 引用参考音频（从1编号，最多3条） |
| references[] | 音频≤3条，每条≤30s≤10MB（wav/mp3/pcm/ogg_opus）；图片≤1张≤10MB（jpeg/png/webp）。组合：纯文本 / 文本+图片 / 文本+音频 |
| references[].speaker | 音色ID，与 audio_data/audio_url 互斥 |
| audio_config.format | wav（用户默认）/ mp3 / ogg_opus / pcm |
| audio_config.sample_rate | 默认 44100；可选 48000/44100/40000/32000/24000/16000/8000 |
| audio_config.speech_rate / pitch_rate / loudness_rate | 默认 0，范围 -100~100 |
| audio_config.enable_subtitle | bool |
| watermark | object，`{}` |

## 限流

10 并发 + 5 次/分钟 + 20000 字符/分钟。输出最长约 120s。

## 部署案例：doubao-tts-server

项目正本：`~/Documents/Hermes/Projects/doubao-tts-server/`（git `v2.2-dual-panel` 分支）
NAS 运行：`192.168.1.2:8000`（Docker + compose，重启自恢复）

**架构：** FastAPI wrapper → doubao_client → 豆包语音 API。SQLite 持久化在 Docker volume。

**接口：**
- `GET /` — Web UI（双栏：左输入+结果+历史，右参数面板常驻）
- `POST /tts` — 完整 JSON 接口（支持所有参数）
- `POST /tts/simple?text=...` — 简化 query 参数版
- `GET /history` — 历史记录（分页）
- `DELETE /history/{id}` — 删除记录

**Web UI 参数全部常驻右侧面板：** 模型、格式、采样率（默认44100）、语速/音调/音量滑杆、字幕开关、音色ID、3个独立参考音频槽位（拖拽上传）、1个参考图片槽位（与音频互斥）。Ctrl+Enter 生成，参数 localStorage 记忆。
