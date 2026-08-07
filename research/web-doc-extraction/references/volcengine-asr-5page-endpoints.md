# 火山引擎豆包语音 ASR/端到端 API — 5 页面端点参考

验证日期: 2026-07-21

## 页面索引

| # | 名称 | 文档 ID |
|---|------|---------|
| 1 | 流式语音识别WebSocket | `6561/1354869` |
| 2 | 录音文件识别标准版HTTP | `6561/1354868` |
| 3 | 录音文件极速版识别HTTP | `6561/1631584` |
| 4 | 录音文件识别闲时版HTTP | `6561/1840838` |
| 5 | 端到端实时语音大模型API接入文档 | `6561/1594356` |

基础 URL: `https://docs.volcengine.com/docs/{id}?lang=zh`

## 1. 流式语音识别WebSocket

**接口地址:**
- 双向流式模式: `wss://openspeech.bytedance.com/api/v3/sauc/bigmodel`
- 流式输入模式: `wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_nostream`
- 双向流式优化版: `wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async`

**资源ID:**
- 模型1.0: `volc.bigasr.sauc.duration`(小时版) / `volc.bigasr.sauc.concurrent`(并发版)
- 模型2.0: `volc.seedasr.sauc.duration`(小时版) / `volc.seedasr.sauc.concurrent`(并发版)

**协议:** WebSocket + 4字节二进制Header + Payload

**参数表特征:** 6列(字段/说明/层级/格式/是否必填/备注)，~35个请求字段，含user/audio/request三层嵌套

**关键参数:** model_name=bigmodel, format=pcm/wav/ogg/mp3, enable_itn=true(默认), enable_nonstream(二遍识别)

**错误码:** 20000000(成功), 45000001(参数无效), 45000002(空音频), 45000081(等包超时), 45000151(格式不正确), 55000031(服务器繁忙)

## 2. 录音文件识别标准版HTTP

**接口地址:**
- 提交: `POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit`
- 查询: `POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/query`

**资源ID:** `volc.bigasr.auc`(1.0) / `volc.seedasr.auc`(2.0)

**协议:** HTTP POST, JSON Body

**特有字段:** callback(回调地址), callback_data(回调信息), enable_channel_split(双声道), vad_segment(vad分句)

**响应Header:** X-Api-Status-Code(20000000=成功), X-Api-Message(OK=成功), X-Tt-Logid

**查询结果Body:** result.text(全文), result.utterances[](分句列表含start_time/end_time/text)

**直达submit任务ID上限:** 半小时最多500小时音频

## 3. 录音文件极速版识别HTTP

**接口地址:** `POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash`

**资源ID:** `volc.bigasr.auc_turbo`(固定值)

**协议:** HTTP POST, JSON Body — 一次请求即返回结果，无需轮询

**使用限制:** 时长≤2h, 大小≤100MB, 格式WAV/MP3/OGG OPUS

**请求体:** `audio.url`(URL方式) 或 `audio.data`(base64编码) 二选一

**与标准版差异:** 移除callback/callback_data字段，移除客服能力字段(enable_lid/enable_emotion_detection/enable_gender_detection/show_volume/show_speech_rate)

## 4. 录音文件识别闲时版HTTP

**接口地址:** 同标准版 submit + query

**资源ID:** `volc.bigasr.auc_idle`(固定值)

**SLA:** 24h内完成，闲时算力队列，优先级低于标准版/极速版

**请求/响应格式:** 同标准版

## 5. 端到端实时语音大模型API接入文档

**接口地址:** `wss://openspeech.bytedance.com/api/v3/realtime/dialogue`

**资源ID:** `volc.speech.dialog`(固定值)

**协议:** WebSocket + 4字节二进制Header + Payload

**特殊鉴权:**
- X-Api-App-Key: 固定值 `PlgvMymc7f3tQnJ6`
- X-Api-App-ID: 必填，控制台获取
- X-Api-Resource-Id: 固定值 `volc.speech.dialog`
- X-Api-Connect-Id: 可选，推荐传UUID

**模型版本:**
- 1.2.1.1 = O2.0版本(多模态, 精品音色, 系统Prompt配置)
- 2.2.0.0 = SC2.0版本(角色扮演, 克隆音色, character_manifest配置)
- O版本/SC版本已停止迭代维护

**客户端事件(17个):**
| ID | 事件 | 说明 |
|----|------|------|
| 1 | StartConnection | 声明创建连接 |
| 2 | FinishConnection | 断开WS连接 |
| 100 | StartSession | 启动会话(asr/dialog/tts三层配置) |
| 102 | FinishSession | 结束会话(可复用WS) |
| 200 | TaskRequest | 上传音频二进制数据 |
| 201 | UpdateConfig | 更新SP配置 |
| 300 | SayHello | 打招呼文本 |
| 400 | EndASR | push_to_talk结束信号 |
| 500 | ChatTTSText | 指定文本合成音频 |
| 501 | ChatTextQuery | 文本query |
| 502 | ChatRAGText | 外部RAG知识输入 |
| 510-514 | Conversation* | 上下文管理(创建/更新/查询/截取/删除) |
| 515 | ClientInterrupt | 按键模式打断响应 |

**服务端事件(11个):**
| ID | 事件 | 说明 |
|----|------|------|
| 50 | ConnectionStarted | 成功建立连接 |
| 51 | ConnectionFailed | 建立连接失败 |
| 52 | ConnectionFinished | 连接结束 |
| 150 | SessionStarted | 成功启动会话(含dialog_id) |
| 152 | SessionFinished | 会话已结束 |
| 153 | SessionFailed | 会话失败 |
| 154 | UsageResponse | 用量信息 |
| 251 | ConfigUpdated | UpdateConfig的ack |
| 350 | TTSSentenceStart | 合成音频起始 |
| 351 | TTSSentenceEnd | 合成音频结束 |

**StartSession配置结构:**
- asr: audio_info(format/sample_rate/channel) + extra(end_smooth_window_ms/enable_custom_vad/enable_asr_twopass/热词等)
- dialog: bot_name(仅O)/system_role(仅O)/speaking_style(仅O)/character_manifest(仅SC)/location/dialog_context/extra(含model必传)
- tts: speaker(音色)/audio_config(speech_rate/loudness_rate)/extra(explicit_dialect/aigc_metadata/tts_2.0_model)

**音色列表:**
- O2.0精品: zh_female_vv_jupiter_bigtts, zh_female_xiaohe_jupiter_bigtts, zh_male_yunzhou_jupiter_bigtts, zh_male_xiaotian_jupiter_bigtts
- 英文(O2.0): en_male_tim_uranus_bigtts, en_female_dacey_uranus_bigtts, en_female_stokie_uranus_bigtts
- SC克隆音色: ICL_* (21个)
- SC2.0克隆: saturn_* (21个)

**限流:** QPM 60(默认), TPM 10w(默认)
