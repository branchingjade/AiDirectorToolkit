---
name: heychat-bot
description: "黑盒语音 Bot API 集成——WebSocket 连接、消息发送、推流到语音频道。触发词：黑盒语音、Heybox Voice、chat.top、heychat、开黑语音。"
version: 1.1.0
---

# 黑盒语音 Bot 集成

黑盒语音（chat.top / Heybox Voice）是游戏语音平台，提供完整的 Bot API。**核心亮点：可以通过 HTTP API 将音频流推送到语音频道，实现 Bot 在语音频道里"说话"。**

## 触发条件

- 需要在黑盒语音上接入 AI Bot
- 需要在语音频道实现 TTS 语音回复
- 查询黑盒语音 API 端点

## 平台概览

| 项 | 值 |
|------|-----|
| 首页 | https://chat.top |
| 开发者认证 | https://open.xiaoheihe.cn/zh_cn/chat_robot/home |
| Bot 管理后台 | https://bot.xiaoheihe.cn |
| API 文档 | https://s.apifox.cn/43256fe4-9a8c-4f22-949a-74a3f8b431f5 |
| 官方 Demo | https://github.com/QingFengOpen/HeychatDemo（Python + Go） |
| API Base | https://chat.xiaoheihe.cn |

## 架构

```
WebSocket (实时事件) + HTTP REST (消息/媒体/推流)
鉴权：Header token（从 Bot 后台获取）
心跳：30s PING/PONG
```

## 关键 API 端点

详见 `references/api-endpoints.md`。

### WebSocket 连接
```
wss://chat.xiaoheihe.cn/chatroom/ws/connect
Query: client_type=x_client_type=web&os_type=web&x_os_type=bot&x_app=heybox_chat&chat_os_type=bot&chat_version=1.30.0
Header: token
```

### 推流到语音频道（核心）
```
POST /chatroom/v3/channel/stream/push
Body: {room_id, channel_id, stream_url (mp3), volume (0-100), operator, callback_url?, repeat_num?}
返回: {task_id} — 用于停止推流
```

### 发送频道消息
```
POST /chatroom/v3/channel/message/send
Body: {room_id, channel_id, content, msg_type}
支持：文字、图片、Markdown、卡片消息、@全体/@在线
```

### 停止推流
```
POST /chatroom/v3/channel/stream/stop
Body: {task_id}
```

## 语音频道：双向流（推流 + 输入流）

Bot 不仅能推音频到语音频道，还能**接收语音频道的音频**。

### 推流（输出）
Bot 说话：POST TTS 音频 mp3 URL → 语音频道播放。详见 `references/api-endpoints.md`。

### 输入流（监听）
Bot 听语音频道里其他人的发言。通过"输入在线媒体流 REST API"实现，底层走 TRTC（腾讯实时音视频）或 Volcengine（火山引擎）中继。

**端点未在公开文档侧边栏列出**，但在"在线媒体流说明文档"中确认存在。回调示例：
- **TRTC 线路**：`EventGroupId=7, EventType=701, Status=0`（输入流开始成功）
- **Volc 线路**：`EventType="RelayStreamStateChanged", Status=3`
- Header 用 `SDK-Type: trtc` 或 `SDK-Type: volc` 区分
- 回调 JSON 含 `RoomId`, `TaskId`, `UserId`, `StreamUrl`, `Status`

**这意味着 Bot 理论上可以实现完整的语音对话**：收听 → STT → LLM → TTS → 推流回复。不需要 Windows 音频回路 hack。

⚠️ 输入流 API 的完整端点和参数需联系开发者确认（QQ 群 `qm.qq.com/q/998HfX7ENa` 或开发者平台 `chat.xiaoheihe.cn/iwvueiny`）。

## 服务端推送事件

| type | 描述 |
|------|------|
| 50 | 用户使用 Bot 命令 |
| 3001 | 用户进出房间 |
| 5003 | 表情回应 |
| card_message_btn_click | 卡片按钮点击 |

## Hermes 集成架构（已实现）

项目位置：`~/Documents/Hermes/Projects/heychat-bridge/`
Git repo 已初始化 (commit `5c1da26`)，全部代码通过 16/16 模块检查。

```
黑盒语音 ←WS→ main.py ←subprocess→ hermes chat -m deepseek-v4-flash
              ↓
          TTS (MiMo)
              ↓
        音频托管 → stream/push → 语音频道
```

模块（全部编译通过）：
- `ws_client.py` — WebSocket + 30s PING/PONG 心跳 + 断线重连
- `event_handler.py` — type 50/3001/5003/card_click 事件分发
- `hermes_client.py` — `hermes chat -m deepseek-v4-flash -Q -q "..."` 子进程调用
- `msg_sender.py` — HTTP 发文字/Markdown 到频道
- `tts_pipeline.py` — MiMo TTS 生成 mp3（通过系统 Python 调用 `mimo_tts.py`）
- `streamer.py` — POST `/channel/stream/push` + `/channel/stream/stop`

延迟预估（v4-flash）：2.5~3.5 秒/轮。

**模型选择**：仅 Bot 用 `deepseek-v4-flash`（比 v4-pro 便宜 3 倍，更快），主 Hermes 会话仍用 `deepseek-v4-pro`。在 `hermes_client.py` 中通过 `hermes chat -m deepseek-v4-flash` 指定，不修改全局 config。

**DeepSeek 模型命名**：`deepseek-chat` 和 `deepseek-reasoner` 将于 2026/07/24 弃用，对应 `deepseek-v4-flash` 的非思考与思考模式。`deepseek-v4-flash` 已可直接使用（即使 Hermes 模型选择器未列出），价格 ¥1/¥0.02/¥2（缓存未命中/命中/输出）。

## 与其他平台对比（语音能力）

| 平台 | 语音气泡 | 语音频道参与 | Hermes 适配器 |
|------|---------|-------------|--------------|
| Telegram | ✅ 原生 | ❌ | ✅ 内置 |
| Discord | ✅ 原生 | ✅ VC 加入+收听 | ✅ 内置 |
| 黑盒语音 | ❌ | ✅ 推流+输入流（双向） | ❌ 需自建（本项目） |
| 飞书 | ❌ 仅文件附件 | ❌ | ✅ 内置 |
| 微信 | ❌ 无 send_voice | ❌ | ✅ 内置 |

## Pitfalls

- 推流 API 需要**静态 URL**（mp3），不支持流式推送——必须等音频文件完整生成后再推
- 音频托管方案待定：推流需要公网可访问的音频 URL（选项：本地 HTTP server / alist WebDAV / 媒体上传 API）
- 当前"停止推流"API 标注为"开发中"
- 官方 Demo 代码较旧（2 年前），API 可能有变化。GitHub 文档仓库 `github.com/QingFengOpen/HeychatDoc` 仍停留在 v2 API（无语音推流），最新 v3 API 仅在 ApiFox 文档上
- v2 vs v3 消息格式不同：v2 用 `msg_type: 1/3/4/10`（文本/图片/Markdown/Markdown+@），v3 接口路径和字段可能有调整，需拿到 token 后实际调用验证
- 开发者认证审核需 3 个工作日
- Hermes 没有内置适配器，需自建桥接程序
- WS 事件字段结构需拿 token 实际验证（文档不够详细）
