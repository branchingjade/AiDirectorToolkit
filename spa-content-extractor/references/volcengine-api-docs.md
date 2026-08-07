# 火山引擎（豆包语音）API 文档提取参考

本文档是 `spa-content-extractor` 的补充参考，记录火山引擎文档站的特定模式。

## 页面结构

火山引擎文档站是 SPA。API 参考文档的 URL 模式：
- `https://docs.volcengine.com/docs/6561/{page_id}?lang=zh`

其中 `6561` 是豆包语音的产品ID。

## URL 重定向检测

某些旧 API 文档 URL 已失效，会被重定向到"产品动态"页面。导航后**必须**在 snapshot 中检查面包屑确认页面身份。

**正常页面**的面包屑:
```
- listitem - StaticText "文档首页"
- generic - StaticText "豆包语音"  
- generic - StaticText "语音合成大模型"
- generic - StaticText "音频生成HTTP"          ← 具体接口名
```

**重定向页面**的面包屑:
```
- listitem - StaticText "文档首页"
- generic - StaticText "豆包语音"
- generic - StaticText "产品概述"
- generic - StaticText "产品动态"              ← 仅此而已
```

已知已重定向的旧 URL（不可直接提取 API 内容）:
| 预期页面 | 旧 URL | 现状 |
|---------|--------|------|
| 异步长文本语音合成 | /docs/6561/2536398 | → 产品动态 |
| 声音复刻 | /docs/6561/1374038 | → 产品动态 |
| 音色设计 | /docs/6561/1598072 | → 产品动态 |
| 音色管理 | /docs/6561/1630433 | → 产品动态 |

这些页面的 API 文档可能需要通过侧边栏导航点击进入，或已迁移到新的 URL 路径。导航菜单中仍显示这些条目，但旧直链失效。

## 有效页面参考

当前可用的 API 参考页面（已验证 2026-07-21）:

| 页面 | URL ID | 端点 |
|------|--------|------|
| 音频生成HTTP | 2550782 | POST /api/v3/tts/create |
| 单向流式语音合成HTTP | 2528925 | POST /api/v3/tts/unidirectional |
| 错误码查询 | 2534853 | (错误码对照表) |

## snapshot 中的参数模式

### 普通参数（v3 音频生成接口）
```
- StaticText "参数名 类型 必选"      ← 参数声明
  - generic
    - StaticText "参数说明"          ← 同一列框内
- StaticText "参数名2 类型"          ← 可选参数
  - generic
    - StaticText "参数说明"
```

### 嵌套参数
```
- StaticText "parent object"
  - generic
    - generic
      - generic
        - StaticText "child_field string"
      - generic
        - StaticText "child_field 说明"
```

### HTML 表格（错误码页面）
```
- table
  - row
    - cell "Http 状态码"
      - generic [onclick] → StaticText "Http 状态码"
    - cell "错误码code"
      - generic [onclick] → StaticText "错误码code"
```

提取时注意：每个 cell 内通常有一层 `generic [onclick]` 或 `- paragraph` 包裹 StaticText。

## 服务地址

- API 请求: `openspeech.bytedance.com`
- 控制台接口: `open.volcengineapi.com`
- WebSocket: `wss://openspeech.bytedance.com`

## 鉴权方式

| 方式 | 请求头 | 说明 |
|------|--------|------|
| 新版 | X-Api-Key | 单头鉴权，推荐 |
| 旧版 | X-Api-App-Id + X-Api-Access-Key | 双头鉴权，即将下线 |
