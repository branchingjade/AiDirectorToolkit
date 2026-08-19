# 写对接 DSH 的 Hermes 桌面插件（dsh-inbox 案例，2026-08-19）

**用户原话**：「返给 DSH 执行」+「做成和 Hermes 原生一致」——当插件对接 DSH（订阅 DSH 事件、调 DSH API、显示 DSH 状态），**把写作任务派给 DSH 自己**最可靠，Hermes 只做验收。

## 操作流程

1. **创建 DSH 任务会话**（workspaceId=ef9bd119，creator）：
   ```python
   session.create {workspaceId, sessionId: "dsh-build-<plugin>-001"}
   ```

2. **任务书必须包含**：
   - 直接指明文件路径（`C:/Users/HMSJ/AppData/Local/hermes/desktop-plugins/<id>/plugin.js`）
   - 列出 2-3 个参考插件让 DSH `read`：
     - `quota-panel`（最简结构：titleBar + Popover）
     - `skill-manager`（含 i18n/registerMany/palette 命令）
     - `dsh-settings`（DSH 对接先例——已有）
   - **要求核对 SDK 源码**——`apps/desktop/src/sdk/index.ts` 每个 import 的导出都要对得上
   - **要求真连一次目标服务**做端到端验证（如 DSH 的 `ws://127.0.0.1:8080/api/events.mux`）
   - **要求诚实报告坑**（"如果你建议的方案有更好的写法，先问我"）

3. **Hermes 端验收**：DSH 写完后只做 `node --check` 语法验证 + 真实业务链路端到端跑。**不要自己重写或修补**——DSH 写的代码结构通常比 Hermes 直写更对齐 SDK。

## DSH 报告的真实坑（dsh-inbox 案例）

写对接 DSH 的插件时**直接套用**，不必再探测：

| 坑 | 真相 |
|---|---|
| `host.notify({ kind: 'input' })` | ❌ Hermes toast kind 只有 `error/warning/info/success`；OS 系统通知用 `ctx.os.notify`，kind 固定 `'plugin'`，由"设置 → 通知 → Plugin notifications"开关 gate |
| `ctx.config` | ❌ 不存在；PluginContext 只有 `{ register, registerMany, onDispose, rest, socket, os, storage, i18n }`；配置走 `ctx.storage` + 弹层内输入框 |
| DSH wire 格式 | `{ type: 'server-request', rpcId, method, payload }`；`method === payload.type`；`question/requested` 载荷含 `sessionId + questions[{id, question, options?, multiSelect?}]` |
| DSH 服务端 `close(1008)` | 客户端发的消息——插件只收不发（响应走其他 RPC） |
| `events.mux` | HTTP 探测永远 404；接受 WebSocket 升级（必须 ws upgrade） |
| `POST /api/respond` | 不是 `/api/session.respond`；GET 一律 404，必须 POST |

## SDK 导出核对（已实测可用——写插件时直接 import）

```js
import { 
  atom, haptic, host, Button, Codicon, EmptyState, Input,
  Popover, PopoverContent, PopoverTrigger, ScrollArea,
  PALETTE_AREA, TITLEBAR_AREAS 
} from '@hermes/plugin-sdk'
import { useEffect, useState } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'
```

`PluginContext = { register, registerMany, onDispose, rest, socket, os, storage, i18n }`

## PluginContext 关键 API

- `ctx.register({id, area, data, render})` 注册 UI
- `ctx.storage.get/set(key, value)` UI 状态持久化
- `ctx.onDispose(() => {...})` 清理（必须解绑事件、关闭 WebSocket）
- `ctx.os.notify({title, body})` 系统级原生通知
- `host.notify({kind, title, message, durationMs, action})` in-app toast
- `host.navigate(path)` 跳转

## dsh-inbox 完整架构（参考实现）

```
Hermes 桌面插件 dsh-inbox/plugin.js
 ↓ WebSocket 客户端
WS /api/events.mux（127.0.0.1:8080）
 ↓ DSH 推 question/requested 帧
 ↓ 解析入 pending 列表 + 调 host.notify + ctx.os.notify
 ↓ 用户在 DSH web 回答
 ↓ DSH 推 question/resolved 帧
 ↓ 插件移除 pending 条目
```

**文件位置**：`C:\Users\HMSJ\AppData\Local\hermes\desktop-plugins\dsh-inbox\plugin.js`（15395 字节，约 380 行，纯前端无后端）

**启用**：Hermes 桌面 app ⌘K → "Reload desktop plugins"（或等自动热加载）；titleBar 右上角出现 dsh-inbox 图标 + ⌘K "DSH Inbox" 调色板命令

## 为什么不 Hermes 自己写

Hermes 不知道 SDK 所有可用导出、不知道 DSH wire 协议细节、不知道哪些 Hermes toast kind 实际存在；这些坑只有**让 DSH 自己查自己的 source**（同时读 SDK + apiproxy + 跑真实端点）才能全暴露。

**方法论泛化**：遇到「DSH 内部的事」——端点 / SDK 行为 / 内部组件 / wire 格式 / 内部配置 schema——**先发 DSH 任务问**，别在 Hermes 端 HTTP 探测瞎猜。详细 DSH 问询模板见 `hermes-dsh-fusion` skill。
