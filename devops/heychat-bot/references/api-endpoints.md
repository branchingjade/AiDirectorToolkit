# 黑盒语音 Bot API 端点参考

> 来源：https://s.apifox.cn/43256fe4-9a8c-4f22-949a-74a3f8b431f5

## 鉴权

所有 HTTP 请求 Header 带 `token`（从 https://bot.xiaoheihe.cn 创建 Bot 后获取）。

WebSocket 连接：同上，Header 带 `token`。

## 通用 Query 参数

所有 API 需要以下 Query 参数：

| 参数 | 值 | 说明 |
|------|-----|------|
| client_type | heybox_chat | 声明请求黑盒语音 |
| x_client_type | web | 客户端类型 |
| os_type | web | 客户端类型 |
| x_os_type | bot | 声明客户端是 bot |
| x_app | heybox_chat | 声明请求黑盒语音 |
| chat_os_type | bot | 声明客户端是 bot |
| chat_version | 1.30.0 | 客户端版本号 |

---

## WebSocket 连接

```
wss://chat.xiaoheihe.cn/chatroom/ws/connect?client_type=heybox_chat&x_client_type=web&os_type=web&x_os_type=bot&x_app=heybox_chat&chat_os_type=bot&chat_version=1.30.0
```

Header: `token: <your-bot-token>`

连接后发送心跳：
- 发送文本 `PING`（每 30s）
- 收到 `PONG` 响应

### 事件格式

```json
{
  "sequence": 8830551,
  "type": "50",
  "notify_type": "",
  "data": {},
  "timestamp": 1728454873111
}
```

### 事件类型

| type | 描述 |
|------|------|
| 50 | 用户使用 Bot 命令 |
| 3001 | 用户加入/退出房间 |
| 5003 | 频道消息表情回应 |
| card_message_btn_click | 卡片按钮点击 |

---

## HTTP 接口

### 推流至语音频道

```
POST https://chat.xiaoheihe.cn/chatroom/v3/channel/stream/push
Content-Type: application/json
```

Body:
```json
{
    "room_id": "3886418517665415168",
    "channel_id": "3886418645352636424",
    "stream_url": "https://example.com/audio.mp3",
    "volume": 30,
    "operator": 8829829,
    "callback_url": "https://yourdomain.com/callback",
    "seek_second": 10,
    "repeat_num": 2,
    "max_duration": 233
}
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| room_id | string | ✅ | 房间 ID |
| channel_id | string | ✅ | 语音频道 ID |
| stream_url | string | ✅ | 音频流 URL（mp3 等） |
| volume | int | ❌ | 音量 0-100，默认 100 |
| operator | int | ✅ | 操作用户 UID |
| callback_url | string | ❌ | 回调链接 |
| seek_second | int | ❌ | 从第 N 秒开始播放 |
| repeat_num | int | ❌ | 循环次数，-1 无限循环，默认 1 |
| max_duration | int | ❌ | 循环最大时长（分钟），仅 repeat_num=-1 生效 |

响应：
```json
{
    "msg": "",
    "result": {"task_id": "VmKuXYqy..."},
    "status": "ok"
}
```

### 停止推流至语音频道 ⚠️ 开发中

```
POST https://chat.xiaoheihe.cn/chatroom/v3/channel/stream/stop
```

Body:
```json
{
    "task_id": "OUOdsOtpm3K2HEvI3..."
}
```

---

## 消息接口

### 发送频道文字消息

```
POST https://chat.xiaoheihe.cn/chatroom/v3/channel/message/send
```

### 发送图片消息

```
POST https://chat.xiaoheihe.cn/chatroom/v3/channel/message/send_image
```

### 发送 Markdown 文档

```
POST https://chat.xiaoheihe.cn/chatroom/v3/channel/message/send_markdown
```

### 发送卡片消息

```
POST https://chat.xiaoheihe.cn/chatroom/v3/channel/message/send_card
```

### @全体/@在线成员

```
POST https://chat.xiaoheihe.cn/chatroom/v3/channel/message/send_at_all
```

### 更新/删除消息

```
PUT  /chatroom/v3/channel/message/update
DEL  /chatroom/v3/channel/message/delete
```

### 表情回应

```
POST /chatroom/v3/channel/message/reaction
```

### 私聊消息

```
POST /chatroom/v3/dm/message/send
```

---\n\n## 在线媒体流：输入流（监听语音频道）\n\n> 来源：ApiFox \"在线媒体流说明文档\"\n\nBot 可以通过\"输入在线媒体流 REST API\"接收语音频道的音频。底层走 TRTC（腾讯实时音视频）或 Volcengine（火山引擎）中继。\n\n**⚠️ 具体端点和参数未在公开文档侧边栏列出**，但回调格式已确认。联系开发者获取完整 API：\n- QQ 群：https://qm.qq.com/q/998HfX7ENa\n- 开发者平台：https://chat.xiaoheihe.cn/iwvueiny\n\n### 回调配置\n\n在推流 API 中传入 `callback_url` 参数，即可接收输入流事件回调。\n\n### 回调格式\n\nTRTC 线路（Header: `SDK-Type: trtc`）：\n```json\n{\n    \"EventGroupId\": 7,\n    \"EventType\": 701,\n    \"CallbackMsTs\": 1701937900012,\n    \"EventInfo\": {\n        \"EventMsTs\": 1701937900013,\n        \"TaskId\": \"xx\",\n        \"Status\": 0\n    }\n}\n```\n\nVolcengine 线路（Header: `SDK-Type: volc`）：\n```json\n{\n    \"EventId\": \"Your_eventId\",\n    \"EventTime\": \"2021-08-17T19:22:02+08:00\",\n    \"EventType\": \"RelayStreamStateChanged\",\n    \"EventData\": {\n        \"RoomId\": \"Your_RoomId\",\n        \"TaskId\": \"Your_TaskId\",\n        \"UserId\": \"Your_UserId\",\n        \"StreamUrl\": \"rtmp://xxx\",\n        \"Status\": 3,\n        \"StartTimeStamp\": 0,\n        \"Msg\": \"\",\n        \"Vid\": \"xxxxvvv\",\n        \"Reason\": 0\n    }\n}\n```\n\n### 超时重试\n\n回调服务器 5 秒内无响应视为失败，10 秒间隔重试，超过 1 分钟不再重试。\n\n---\n\n## v2 vs v3 API 差异\n\n| 维度 | v2（GitHub 文档） | v3（ApiFox 文档） |\n|------|-------------------|-------------------|\n| 文档仓库 | `QingFengOpen/HeychatDoc` | ApiFox 在线文档 |\n| 发送消息 | `/chatroom/v2/channel_msg/send` | `/chatroom/v3/channel/message/send` |\n| 消息类型字段 | `msg_type`: 1=文本,3=图片,4=MD,10=MD+@ | 待验证 |\n| 媒体上传 | `/upload` | 待验证 |\n| 语音推流 | ❌ 无 | ✅ `/v3/channel/stream/push` |\n| 最后更新 | 2024-09（2 年前） | 约 11 个月前 |\n\nv3 是当前版本，v2 历史参考。\n\n---\n\n## 音频托管方案（待定）

推流 API 需要 `stream_url` 指向公网可访问的音频。选项：

| 方案 | 依赖 | 延迟 |
|------|------|------|
| A) 黑盒媒体上传 API | 需确认返回 URL 可直接用于推流 | 低 |
| B) alist WebDAV→百度网盘 | 已有 alist，需确认直链 | 中 |
| C) 本地 HTTP + frp 穿透 | 需额外搭隧道 | 低 |
