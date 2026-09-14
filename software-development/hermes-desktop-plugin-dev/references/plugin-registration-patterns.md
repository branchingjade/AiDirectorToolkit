# 插件注册模式与 config.yaml 注册要求

实测日期：2026-08-20。来源：dsh-web-panel 插件开发。

## 前端插件必须在 config.yaml 注册

**铁律**：`~/AppData/Local/hermes/config.yaml` 的 `plugins.enabled` 列表**同时控制前端和后端插件的发现**。新插件目录建好后，如果不在 `plugins.enabled` 里，runtime-loader 完全忽略它——**不报错、不加载、不渲染**。

```yaml
plugins:
  enabled:
    - channel-sessions
    - dsh-settings
    - dsh-web-panel    # ← 必须加
    - ops-panel
    - ...
```

修改方式：`hermes config set plugins.enabled '["a","b","c"]'`（config.yaml 是安全敏感文件，agent 不能直接写）。

**陷阱**：新建 plugin.js 后 Ctrl+K reload 没反应 → 看 config.yaml 是否包含该插件 id。这不是 hot-reload 失败，是插件根本没被发现。

## 三种面板注册模式对比

| 模式 | area | 用途 | 退出机制 |
|---|---|---|---|
| **路由面板** | `ROUTES_AREA` + `SIDEBAR_NAV_AREA` | 侧边栏入口 + 主内容区渲染（如"运维面板"） | 点其他侧边栏项切换 |
| **布局面板** | `PANES_AREA` + `placement` | 嵌入 layout tree（bottom/right/left）或独立浮动 | 关对应 zone 或 floating 关闭 |
| **命令面板** | `PALETTE_AREA` | ⌘K 搜索入口 | 无（只注册命令） |

**路由面板 = 运维面板模式**（推荐默认）：
```js
ctx.register({
  area: ROUTES_AREA,
  data: { path: '/dsh-web-ui' },
  render: () => jsx(DSHWebPane, {}),  // 内容渲染在主区域
})
ctx.register({
  area: SIDEBAR_NAV_AREA,
  data: { path: '/dsh-web-ui', label: 'DSH Web UI', codicon: 'globe' },
})
```

**SIDEBAR_NAV 必须和 ROUTES_AREA 配对**：SIDEBAR_NAV 注册侧边栏入口，ROUTES_AREA 注册路由渲染——两者用**相同 path**。缺 ROUTES_AREA 时，点击侧边栏无响应（路由不存在）。

**布局面板 = PANES_AREA 模式**（嵌入 layout tree）：
```js
ctx.register({
  id: 'dsh-web-pane-v2',  // 新 id 避免旧幽灵 pane
  area: PANES_AREA,
  title: 'DSH Web UI',
  data: { placement: 'bottom', height: 480 },
  render: () => jsx(DSHWebPane, {}),
})
```

**PANES_AREA 不需要 SIDEBAR_NAV**——它直接在 layout tree 里显示（如 terminal/git 面板）。但用户不知道怎么找到它 → 可以同时注册 SIDEBAR_NAV 指向该 pane 的路径。

## PALETTE_AREA 可能 undefined（2026-08-20 实测）

`PALETTE_AREA` 在 plugin-sdk 的 `index.ts:250` 导出（`'palette'` 字符串），但在某些 Hermes Desktop 版本/构建里可能未被 shim 注入——报 `ReferenceError: PALETTE_AREA is not defined`。

**降级策略**：PALETTE_AREA 注册是可选的（⌘K 搜索依赖它，但没有它插件仍可正常运行）。如果 PALETTE_AREA 加载失败导致整个插件崩溃，**把 PALETTE_AREA 注册包在 try-catch 里或直接去掉**。

```js
// 安全写法（如果 PALETTE_AREA 不可用）
try {
  ctx.register({
    area: PALETTE_AREA,
    data: { id: 'my-plugin-open', title: '打开 XXX', keywords: [...] },
    run: () => host.navigate('/my-plugin'),
  })
} catch (_) { /* PALETTE_AREA 不可用，忽略 */ }
```

## codicon 值有效性

codicon 是 VS Code codicon 字体（`codicon.css`），**大部分名字可用但不是全部**。已验证可用：`settings-gear`、`organization`、`extensions`、`globe`、`browser`（有报错但不确定是 codicon 问题还是其他）。

**建议**：用已知成功的值（`settings-gear` / `globe` / `extensions`），不要用未验证的值。

## 新插件目录需要完整重启（首次注册）

**runtime-loader 发现新目录的时机**：
- 目录已存在 → `watchDirectory` IPC 监听新文件夹
- 但**首次注册新目录**时，可能需要**完整重启 Hermes Desktop app**（不是 Ctrl+K reload）

**排查路径**：
1. Ctrl+K → "Reload desktop plugins" → 检查 sidebar
2. 如果没出现 → 重启 Hermes Desktop app（完全退出 Hermes.exe + 重开）
3. 如果重启后仍没 → 检查 config.yaml 是否包含该插件 id
4. 如果 config.yaml 有 → 检查 desktop.log 的 `runtime load failed` 错误
