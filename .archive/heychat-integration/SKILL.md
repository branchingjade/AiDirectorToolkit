---
name: heychat-integration
description: 黑盒语音(Heybox Voice/chat.top) Bot API 集成参考。触发词：黑盒语音、Heybox、heychat、黑河语音、chat.top、bot.xiaoheihe、推流到语音频道。
version: 1.0.0
category: devops
---

# 黑盒语音 Bot 集成

黑盒语音（chat.top / Heybox Voice）是小黑盒旗下的游戏语音平台（类似 Discord），提供公开 Bot API。

## 平台入口

| 资源 | 地址 |
|------|------|
| API 文档 | https://s.apifox.cn/43256fe4-9a8c-4f22-949a-74a3f8b431f5/320947513e0 |
| 开发者认证 | https://open.xiaoheihe.cn/zh_cn/chat_robot/home |
| 创建 Bot | https://bot.xiaoheihe.cn |
| 官方 Demo | https://github.com/QingFengOpen/HeychatDemo (Python + Go) |
| 开发者 QQ 群 | https://qm.qq.com/q/998HfX7ENa |

## 架构

- **WebSocket 长连接** + **HTTP REST API** 混合架构
- 鉴权：HTTP Header `token`（Bot 创建后获取）
- 心跳：WebSocket 每 30s 发送 `PING`，回复 `PONG`

## WebSocket 连接

```
wss://chat.xiaoheihe.cn/chatroom/ws/connect
```

Query 参数（全部必需）：
- `client_type=heybox_chat`
- `x_client_type=web`
- `os_type=web`
- `x_os_type=bot`
- `x_app=heybox_chat`
- `chat_os_type=bot`
- `chat_version=1.30.0`

Header: `token`

## 核心 API

### 推流至语音频道（关键能力）

```
POST https://chat.xiaoheihe.cn/chatroom/v3/channel/stream/push
```

Body (JSON):
```json
{
    "room_id": "房间ID（必需）",
    "channel_id": "频道ID（必需）",
    "stream_url": "音频流URL，支持mp3等（必需）",
    "volume": 100,
    "operator": "操作用户UID（必需）",
    "callback_url": "回调URL（可选）",
    "seek_second": 0,
    "repeat_num": 1,
    "max_duration": 233
}
```

- `volume`: 0-100，默认100（原音量）
- `repeat_num`: -1=循环播放，默认1次
- `max_duration`: 仅 repeat_num=-1 时生效，单位分钟，范围[1, 10080]
- 返回 `task_id`，用于停止推流

### 停止推流

```
POST https://chat.xiaoheihe.cn/chatroom/v3/channel/stream/stop
```

Body: `{"task_id": "..."}`

### 消息发送（展开子页面查阅具体接口）

- 发送频道消息（文字/图片/Markdown/卡片）
- 发送频道消息 @全体/@在线成员
- 私聊消息
- 更新/删除指定频道消息
- 频道消息表情回应

### 媒体文件上传

独立的上传接口，用于获取文件 URL。

## 服务端推送事件

| type | 描述 |
|------|------|
| 50 | 用户使用 Bot 命令 |
| 3001 | 用户加入/退出房间 |
| 5003 | 用户对消息添加/删除表情回应 |
| card_message_btn_click | 卡片消息按钮点击 |

事件基础格式：
```json
{
  "sequence": 8830551,
  "type": "5003",
  "data": {},
  "timestamp": 1728454873111
}
```

## Bot 命令

- 后台配置斜杠命令
- 用户在文字频道输入 `/` 唤起命令列表
- 命令触发通过 WebSocket `type=50` 推送

## Hermes 集成状态

- ❌ Hermes 无内置适配器
- ✅ API 完整，可自行开发适配器
- 语音路径：TTS 生成音频 → 上传到可访问 URL → 调用推流 API → 语音频道播放

## 与其他平台对比（语音能力）

| 平台 | 语音气泡 | 语音频道推流 | Hermes 适配器 |
|------|---------|-------------|--------------|
| Telegram | ✅ 原生 | ❌ | ✅ 内置 |
| Discord | ✅ 原生 | ✅ VC 加入 | ✅ 内置 |
| 飞书 | ❌ 仅文件附件 | ❌ | ✅ 内置 |
| 微信 | ❌ 无 send_voice | ❌ | ✅ 内置 |
| 黑盒语音 | ❌ | ✅ 推流 API | ❌ 需自建 |
