# DSH llm-fallback 插件技术细节

## 插件架构

`packages/llm/llm-fallback/src/index.ts` — 同时做两件事：
1. **Fallback 逻辑**：hook `llm/stream` waterfall，拦截主模型首个响应块
2. **Settings namespace 注册**：用 `installSettingsSection()` 注册 `llm-fallback` namespace

```typescript
import { installSettingsSection, settingsNamespace } from '@deepseek-ai/dsh-settings'
const FALLBACK_NS = settingsNamespace('llm-fallback')
// 在 apply() 中：
installSettingsSection(ctx, FALLBACK_NS, schema, { rules }, { setSource, onChange })
```

## 规则读取：直接读 settings.yaml 文件

`installSettingsSection` + `setSource` 回调在初始加载时**不会触发**——`setSource` 只在 settings 变更时才调用。因此插件用 `js-yaml` 直接读 `~/.dsh/settings.yaml`：

```typescript
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const yaml = require('js-yaml')  // DSH 的 node_modules 里有 js-yaml
// 在 apply() 中：
const content = readFileSync(join(homedir(), '.dsh', 'settings.yaml'), 'utf-8')
const parsed = yaml.load(content)
const rules = parsed?.['llm-fallback']?.rules ?? []
```

## ⚠️ ESM 不能用 `require()`（2026-08-17 实测）

DSH 是 ESM（`"type": "module"`），顶层 `require()` 直接报错：
```
ReferenceError: require is not defined in ES module scope
```

**正确写法**：用 `createRequire` from `node:module`：
```typescript
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const yaml = require('js-yaml')
```

## Settings API（WebSocket JSON-RPC）

DSH 设置 API 不是 REST，是 WebSocket JSON-RPC：
- 端点：`ws://127.0.0.1:8080/api/events.mux`
- 读取：`{jsonrpc:"2.0", id:1, method:"settings.describe", params:{}}`
- 写入：`{jsonrpc:"2.0", id:2, method:"settings.mutate", params:{ns:"llm-fallback", ops:[{op:"set", path:["rules"], value:[...]}]}}`

前端通过 `api.settings.describe()` / `api.settings.mutate()` 调用（连接层封装了 WebSocket）。

## 依赖注意

`@deepseek-ai/schemastery`（不是 `dsh-schemastery`）是 workspace 内的包名。

## Bundle 注册位置

- **服务端插件**：`packages/bundle/base/cordis.patch.yml`（所有 profile 共用）
- **客户端插件**：`packages/bundle/web-app/cordis.patch.yml`（仅 web profile）

服务端从 workspace 解析，客户端从 `~/.dsh/profiles/web/` 解析——这是客户端新包无法加载的根因。

## Waterfall hook 验证

`preparedCall.stream()` 确认会走 `ctx.waterfall()` 路径（通过 `streamWithRegistration()`），所以 `ctx.on('llm/stream', ...)` 是正确的 hook 点。

## 当前状态（2026-08-17）

- ✅ 插件加载成功，规则从文件读取（1 条）
- ✅ `llm/stream` waterfall handler 已注册
- ⚠️ fallback 触发尚未实测验证（opencode-go 余额用完时应触发，但 bridge 返回的 AUTH 错误可能在 waterfall 之前被捕获）
- 待验证：加 `console.log` 确认 handler 被调用，或用 `deepseek-official` 作为主模型测试
