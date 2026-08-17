# Hermes 桌面插件前端坑（channel-sessions 实战验证，v1.4.2/v1.5.0）

## Tailwind 类审计（v1.4.2 UI 破损根因，最重要）
Hermes 桌面 app 的 CSS 是构建时从**自己的源码**编译的（Tailwind v4），插件文件在构建图之外——
插件 JS 里写的 className，如果 app 源码没出现过，**编译产物里就没有对应 CSS**，UI 静默破损
（气泡/头像/hover 背景全透明、字号失效、宽度失效）。selfcheck 查不出，`node --check` 查不出，
只有对照编译 CSS 才能发现。

验证法：读 `hermes-agent/apps/desktop/dist/assets/index-*.css`，对插件每个 className 做
Tailwind 转义精确匹配（`[`→`\[`，`.`→`\.`，`(`→`\(`，`)`→`\)`，`/`→`\/`，变体取 `:` 后的主体），
如 `"." + esc(body) not in css`。可用脚本：`scripts/audit-plugin-classes.py <plugin.js>`。

## 主题变量：`--ui-fill-*` 不存在
Hermes 主题只有 `--ui-bg-*`（bg-tertiary/bg-quinary 等）、`--ui-text-*`（primary/secondary/
tertiary/quaternary）、`--ui-stroke-*`、`--ui-control-*`、`--ui-accent`、`--ui-red`。
**`--ui-fill-tertiary` / `--ui-fill-secondary` 不存在**——背景色必须写 `bg-(--ui-bg-tertiary)`。
透明度变体 app 只用 `/40`（`/50`、`/60` 未生成，也要替换成 `/40`）。

## 任意值类要逐个核对
实测编译产物缺失：`text-[10.5px]`、`text-[12.5px]`、`text-[13px]`、`w-[380px]`、`min-h-[30px]`、
`max-w-24`、`space-y-3.5`、`hover:bg-(--ui-bg-secondary)`。
存在的替代：`text-[10px]/[11px]/[12px]`、`w-80`、`min-h-7`、`max-w-60`、`space-y-3`、
`hover:bg-(--ui-bg-tertiary)`。

## 块注释里的 `*/` 会提前闭合（v1.4.2 语法崩溃根因）
版本头注释里写 `--ui-fill-*/字号` 这类内容，`*/` 在 `/* */` 块注释中**提前终止注释**，
后续代码变裸文本 → 整个 plugin.js 语法错误 → "failed to render"。文件头注释写路径/通配符
必须避开 `*/`（改为「--ui-fill 系」）。

## codicon 图标
Codicon 用 `codicon-${name}` 运行时类（VS Code codicon 字体），不走 Tailwind——但名字仍要
确认存在于 dist CSS。实测 `codicon-check-circle-filled` 不存在，用 `codicon-check`；
`codicon-tag-add` / `codicon-checklist` / `codicon-circle-outline` 存在。

## 语法验证
`cp plugin.js chk.mjs && node --check chk.mjs` 即可全文件语法验证（不解析 import）。
注意：用 vm.Script 手动 stub import 时，跨行 import（`import {\n...}`）的正则替换容易
残留代码导致误报 "Illegal continue statement"——直接用 node --check 更可靠。

## 插件 API 测试：404 = 鉴权，不是坏了
`/api/plugins/<name>/*` 未带 session token 的请求返回 **404**（防插件名枚举，
见 web_server.py `_plugin_api_runtime_gate` 注释）。验证后端逻辑**不要 curl**——直接
python 调 service 层：`sys.path.insert(0, '<dashboard 目录>')` 后
`from channel_sessions.service import list_sessions, get_messages, search_messages`，
用真实 state.db 只读调用（`_profile_dbs()` 已处理路径）。

## gateway 加载后端代码在启动时
plugin_api.py / service.py 改动需**重启 gateway** 才生效（日志 `Mounted plugin API routes`
只在启动时打）。前端 plugin.js 热重载即可生效，两边机制不同。

## useI18n 与 "t is not a function"（v1.5.0，根因未 100% 定位）
插件用 SDK `useI18n()` 时注意：SDK 的 `useI18n()` 返回 I18nContextValue，其中
**`t` 字段是 `TRANSLATIONS[locale]`（字典对象，不是函数）**（context.tsx）。
曾出现渲染崩溃 "t is not a function"，但 node+mock hooks 模拟执行**不崩**（mock 的
useI18n 返回形状与真实环境不同；插件 import 还会被 runtime-loader 重写为
sdkImportMap() 的 shim blob URL）。防御性修复（已验证不依赖 SDK）：语言检测改
`navigator.language`（zh*→zh，否则 en），t 用普通闭包不用 useMemo 包装。若再遇此错，
优先排查 useI18n / usePluginI18n 相关交互，而不是逐个 t() 调用点。

## 行尾符
仓库存 LF、Windows 工作区 CRLF——`git diff <(git show HEAD:file)` 会整文件报差异。
用 `tr -d '\r'` 双侧对比，或加 `.gitattributes`（`* text=auto` + `*.js text eol=lf`）。
