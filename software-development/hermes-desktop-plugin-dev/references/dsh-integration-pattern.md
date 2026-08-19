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

## PluginContext 关键 API（**能力边界**实测版，2026-08-19）

`PluginContext = { register, registerMany, onDispose, rest, socket, os, storage, i18n }`

- `ctx.register({id, area, data, render})` 注册 UI
- `ctx.storage.get/set(key, value)` UI 状态持久化
- `ctx.onDispose(() => {...})` 清理（必须解绑事件、关闭 WebSocket）
- `ctx.os.notify({title, body})` 系统级原生通知
- `host.notify({kind, title, message, durationMs, action})` in-app toast
- `host.navigate(path)` 跳转

**⚠️ PluginContext 没有 fs（文件读取）API**——这是高频踩坑点（dsh-inbox 第二轮就撞）：

- `require('fs')` 在 Electron **渲染进程默认禁用**（sandbox + nodeIntegration 默认关闭），抛错被 `try/catch` 吞了会静默失败
- `ctx.rest()` 走 `/api/plugins/<id>/...`——**只对插件自己的后端有效**，不能读别的文件
- **没有通用文件读 API**（`hermes:fs:readFile` 不存在；只有 `readDir` / `writeText` / `trash` / `reveal`）
- **要持久化任何 token / 配置 → 走 `ctx.storage`**（同步、内存级，插件退出仍在）
- **要读平台文件（DSH token / 配置文件）→ 三条路**：
  1. **插件后端（`plugin_api.py`）**—— 后端是 Python Electron 主进程进程，有完整 fs，通过 `ctx.rest('/path')` 读
  2. **用户在面板里手动填**（type=password input + 保存按钮）作为 fallback（dsh-inbox 当前实现就是这个）
  3. **DSH 侧暴露 HTTP endpoint** 让插件 fetch（`GET /api/<thing>` 返回数据）—— 最干净但需要 DSH 支持

**manual config fallback 模式**（dsh-inbox 用的）：

```js
// state
const [draftToken, setDraftToken] = useState($muxToken.get())

// 面板输入框
jsx(Input, {
  type: 'password',
  placeholder: '~/.dsh/.mux-token 内容',
  value: draftToken,
  onChange: e => setDraftToken(e.target.value),
  onKeyDown: e => { if (e.key === 'Enter') saveToken(draftToken) }
})

// 保存
function saveToken(raw) {
  const next = String(raw || '').trim()
  $muxToken.set(next)              // 立即更新 atom
  ctxRef.storage.set('mux-token', next)  // 持久化
  restart()                         // 触发重连
}
```

**为什么这是 fallback 而非首选**：用户每次 DSH 重启 token 都可能变（如果 DSH 重新生成），需要再粘一次。**首选还是后端路径**——加一个 `dashboard/<id>/plugin_api.py` 暴露 `/token` 端点读 `~/.dsh/.mux-token`。

## DSH 信任栅栏与 mux-token 旁路（2026-08-19 dsh-inbox 实战）

**事件**：Hermes 桌面 app 用 file:// 页面加载插件 → WebSocket 必然带 `Origin: null` 或具体 Origin → DSH `packages/client/connection/src/api-request-trust.ts` 拒 → 握手 403 → 一直"重连中"。

**DSH 的解决方案**（DSH 自己改自己，2026-08-19 由 `dsh-mux-token-001` 任务完成）：

1. DSH 服务端改 `trust.ts` + `index.ts`（WS handler）：增加 `?token=xxx` query 参数旁路——带正确 token 放行任意 Origin
2. 启动时自动生成 token 到 `~/.dsh/.mux-token`（44 字符 base64）
3. 改 `mux-token.ts`（新建）做 token 加载/存储

**插件侧 token 加载**（dsh-inbox 当前实现）：

```js
function loadMuxToken(ctx) {
  // 1) 优先 ctx.storage（用户在面板里粘过）
  let stored = ctx.storage.get('mux-token', '')
  if (stored) return stored
  // 2) fallback 读 DSH 自动生成的文件（要求 Electron 渲染进程开放 fs——默认禁用，多走 ctx.storage）
  try {
    const fs = require('fs')
    if (fs.existsSync('C:/Users/HMSJ/.dsh/.mux-token')) {
      stored = fs.readFileSync('C:/Users/HMSJ/.dsh/.mux-token', 'utf8').trim()
      if (stored) {
        ctx.storage.set('mux-token', stored)
        return stored
      }
    }
  } catch (_error) { /* fs 不可用 → 走手动粘 */ }
  return ''
}

function connect() {
  const token = $muxToken.get()
  const url = token
    ? `ws://127.0.0.1:${port}/api/events.mux?token=${encodeURIComponent(token)}`
    : `ws://127.0.0.1:${port}/api/events.mux`
  // ... new WebSocket(url)
}
```

**为什么"DSH 自己改 mux-token 是最优解"**（vs A: Hermes 主进程代理 / vs B: DSH 加 token / vs C: 找别的）：

| 方案 | 改动量 | 破坏面 | 维护方 | 长期可持续 |
|---|---|---|---|---|
| A: Hermes 主进程代理 | 1-2h | 改 Hermes desktop | Hermes 端 | ❌ 反模式——Hermes 给 DSH 当网关 |
| **B: DSH mux-token** | 4-6h | DSH 服务端 | DSH 端 | ✅ **正交**——DSH 自己解决信任 |
| C: 临时绕过去 | 10min | 零 | 无 | ❌ 治标 |

B 方案正交 +跨平台受益（任何浏览器/桌面端都能用）。**Hermes 端的插件只需读 token（任何途径），不污染 DSH 协议边界**。

## dsh-inbox 完整架构（参考实现）

```
Hermes 桌面插件 dsh-inbox/plugin.js
 ↓ 读 token：ctx.storage 优先 / fs 文件 fallback / 用户面板手动粘
 ↓ WebSocket 客户端
WS /api/events.mux?token=<xxx>（127.0.0.1:8080）
 ↓ DSH 推 question/requested 帧（信任栅栏放行 file:// Origin）
 ↓ 解析入 pending 列表 + 调 host.notify + ctx.os.notify
 ↓ 用户在 DSH web 回答
 ↓ DSH 推 question/resolved 帧
 ↓ 插件移除 pending 条目
```

**文件位置**：`C:\Users\HMSJ\AppData\Local\hermes\desktop-plugins\dsh-inbox\plugin.js`（约 20000 字节，约 515 行）

**启用**：Hermes 桌面 app ⌘K → "Reload desktop plugins"（**必须**——启动不自动发现 runtime 插件，见上文「Runtime 插件 reload 不对称」）；titleBar 右上角出现 dsh-inbox 图标 + ⌘K "DSH Inbox" 调色板命令

**PluginContext 没有 fs 的解决方案**：

- **首选**：插件后端 `dashboard/dsh-inbox/plugin_api.py` + `ctx.rest('/token')` 读 `~/.dsh/.mux-token`
- **Fallback**：用户面板手动粘（当前实现）
- **未来**：DSH 暴露 `GET /api/mux-token`（最干净）

## 为什么不 Hermes 自己写

Hermes 不知道 SDK 所有可用导出、不知道 DSH wire 协议细节、不知道哪些 Hermes toast kind 实际存在；这些坑只有**让 DSH 自己查自己的 source**（同时读 SDK + apiproxy + 跑真实端点）才能全暴露。

**方法论泛化**：遇到「DSH 内部的事」——端点 / SDK 行为 / 内部组件 / wire 格式 / 内部配置 schema——**先发 DSH 任务问**，别在 Hermes 端 HTTP 探测瞎猜。详细 DSH 问询模板见 `hermes-dsh-fusion` skill。
