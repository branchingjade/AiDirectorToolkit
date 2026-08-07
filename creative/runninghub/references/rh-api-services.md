# RunningHub API 服务（模型API / AI应用API）

RunningHub 除了 ComfyUI 工作流市场之外，还有独立的 **API 市场**（`runninghub.ai` 导航栏 → 模型API / AI应用API），提供封装好的 AI 服务端点，不需要写工作流 JSON，直接 HTTP POST 调用。

## 与 ComfyUI 节点的区别

| | ComfyUI 工作流节点 | API 服务 |
|---|---|---|
| 入口 | runninghub.cn 工作流编辑器 | runninghub.ai API 市场 |
| 调用方式 | 在 RH 画布上搭工作流，或用工作流 API 提交 | HTTP POST，标准 REST API |
| 底层 | ComfyUI 节点图 | 后端封装（可能走火山引擎等第三方服务） |
| 代表 | GetNode/SetNode/SeedVR2 | volc-subtitle-erase-pro |

## 已知 API 服务

### volc-subtitle-erase-pro — 火山字幕擦除

- **接口**: `POST /openapi/v2/volc-subtitle-erase-pro/video`
- **说明**: 自动将视频上传至火山引擎视频点播（VOD），执行精细化字幕擦除，返回去字幕视频
- **底层**: 火山引擎（Volcengine / 字节跳动云）的 VOD 字幕擦除能力
- **参数**:
  - `videoUrl` (必填) — 视频 URL，最大 500MB
  - `eraseType` (可选) — `subtitle`（擦字幕）或 `text`（擦文字）
  - `encodeMode` (可选) — `size`（体积优先）或 `quality`（画质优先）
  - `eraseRatioLocation` (可选) — 指定矩形框选区域做局部擦除
  - `clientToken` (可选) — 幂等控制 token
- **定价**: RunningHub 标准模型 API 计费（非免费）

## 搜索技巧

RH API 服务在 GitHub / HuggingFace 上搜不到（不是开源模型），用搜索引擎（DuckDuckGo 比 Google 少验证码）搜 `volc-subtitle-erase` 或直接浏览 `runninghub.ai` 的 API 市场页面。
