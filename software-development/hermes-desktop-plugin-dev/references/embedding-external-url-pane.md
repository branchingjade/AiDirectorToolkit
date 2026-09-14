# 在 Hermes 桌面里嵌入外部 URL —— 完整决策树

实测日期：2026-08-20。来源：dsh-settings 插件 4 轮迭代（floating → right → 底部 → 体验验收），最终落定 `placement: 'bottom'` + `host.preview` fallback + 自定义 DOM 事件做可见性同步。

## 用户要什么

> 「我想要的是 Hermes 预览框一致的体验」+「宿主必须是 hermes」+「单独的面板」

—— 在 Hermes 桌面里、能拖动、可折叠、跟 chat 预览一致的独立面板，能显示外部 URL（DSH web UI = vite + React + WebSocket @ `http://127.0.0.1:8080`）。

## 死胡同（按否掉的顺序）

1. **插件路由面板里 `<iframe>`**：不在 layout tree，不能拖动/折叠/关闭
2. **`window.open(url, ..., 'width=1280,height=820')`**：系统浏览器窗口，**不在 Hermes 里**——用户原话「我自己开浏览器不就行了」
3. **改主仓库加 `host.openWindow(url)`**（独立 Electron BrowserWindow）：工作量是 `host.preview` 的 3-4 倍，且不是用户要的"单独面板"
4. **`'floating'` 不能 resize**（floating-panes.tsx 写死 width/height）：用户要"调整大小"被否
5. **`'right'`/`'left'`**（layout tree）：关对应 zone 时 pane 跟着关，用户多次翻转接受度

## 最终方案

```js
// DSH Web Pane
ctx.register({
  id: 'dsh-web-pane-v2',  // 版本号后缀（避免 layout tree 旧 id 幽灵渲染）
  area: PANES_AREA,
  title: 'DSH Web UI',
  data: { placement: 'bottom', height: 480 },
  render: () => jsx(DSHWebPane, {}),
})
```

**为什么 `'bottom'`**：terminal / git 面板常驻底部，日常不关；`'right'/'left'` 关栏就一起关。

## iframe 跨源加载被 webSecurity 阻止 —— 根因级真相

`apps/desktop/electron/main.ts:6100` 的 webPreferences 写死 `webSecurity: true`、`contextIsolation: true`、`nodeIntegration: false`。

**iframe 加载 `http://127.0.0.1:8080` 这类跨源 URL 时被浏览器同源策略直接拒绝**——iframe 渲染空白（看起来"黑屏"）。**根因不是**目标服务挂了、不是 Hermes 拦截、不是 iframe sandbox 配错（`allow-scripts allow-same-origin` 都给了也没用）。

**为什么 `host.preview` 不受影响**：`store/preview.ts` 的 preview pane 用 Electron `<webview>` 标签（不走 `webSecurity` 限制），PR #90437 加 `host.preview(url)` 是唯一既能跨源、又在 Hermes 内的路径。

**为什么 iframe 黑屏看起来像 DSH web UI 死了**：curl 测目标服务 200 + 浏览器直接访问能看到 + iframe 在 Hermes 里黑屏 = 跨源阻止。

**修复路径**（三种，按代价递增）：
1. **接受 + fallback**：iframe 黑屏时给用户提示"在外部浏览器打开 URL"（用 `<a target="_blank">`），等 PR #90437 合并后用 `host.preview`
2. **改 main.ts webPreferences**：`webSecurity: false`（影响整个 renderer 的安全模型，hermes-agent 不会接受）
3. **加 host.preview 等 PR 合并**：1 文件 ~12 行，工作量最小

## Pane 可见性持久化模式（storage 不是 reactive）

`ctx.storage` 是同步 API，不通知订阅。要在 settings 卡片和浮动 pane 之间同步可见性，用自定义 DOM 事件桥接（**storage 不能用 useState subscribe**，必须手动 dispatch）：

```js
// module-level
let paneVisible = false
function setPaneVisible(next) {
  paneVisible = !!next
  apiStorage.set('pane-visible-key', paneVisible)
  window.dispatchEvent(new CustomEvent('my-plugin:pane-visible', { detail: paneVisible }))
}

// 在浮动 pane 组件 + settings 卡片组件里都订阅
useEffect(() => {
  const handler = (e) => setLocalVisible(!!e.detail)
  window.addEventListener('my-plugin:pane-visible', handler)
  return () => window.removeEventListener('my-plugin:pane-visible', handler)
}, [])

// render 函数根据 visibility 决定返回组件还是 null
render: () => paneVisible ? jsx(MyPane, {}) : null
```

**为什么返回 null 而不是 mounted+hidden**：render 函数返回 null 时，pane tree 不渲染该 wrapper（实测无空卡残留）；返回 mounted + display:none 会留 fixed div 占位（之前踩过坑）。

## Pane id 用版本号后缀（避免 layout tree 脏数据）

re-register PANES_AREA 时换 pane id（如 `dsh-web-pane-v2`），让旧 id 在 layout tree 静默 orphan（`watchContributedPanes` 不渲染未注册 id，但旧 state 还在 localStorage）。新 id 上线 + 用户 toggle 一次后，layout tree 的脏数据被后续 reload 慢慢 GC。**不要复用旧 id**——下次改动 placement / area 时，旧 entry 会在 layout tree 里持续渲染（"幽灵 pane"），清理要靠 Hermes 重置 localStorage。

## iframe 加载外部 URL 的合法模式

```js
function DSHWebPane() {
  const url = 'http://127.0.0.1:8080/'
  const [key, setKey] = useState(0)  // bump → 强制 iframe 重新加载
  const iframeRef = useRef(null)

  return jsxs('div', {
    className: 'flex flex-col h-full w-full',
    children: [
      jsx('iframe', {
        ref: iframeRef,
        key,  // 改 key 触发 unmount/remount（绕过同源策略下 reload() 不可调）
        src: url,
        className: 'flex-1 w-full bg-white',  // 白底避免加载期间黑屏
        style: { border: '0', minHeight: 0 },
        referrerPolicy: 'no-referrer',
        sandbox: 'allow-scripts allow-same-origin allow-forms allow-popups',
      }),
    ],
  })
}
```

**关键**：iframe 一定要 `flex-1` + `minHeight: 0`，否则父容器没有 flex 高度时 iframe 高度坍塌为 0；`sandbox` 至少给 `allow-scripts allow-same-origin`，否则目标 URL 大部分功能瘫痪（DSH web UI 用 React + Vite + WebSocket，缺 same-origin 直接挂）。

## host.preview SDK 扩展 —— 技术方案（PR 暂搁置，待重新提起）

`apps/desktop/src/sdk/index.ts` 加一行：

```ts
preview: (url: string) => {
  if (typeof url !== 'string' || !url.trim()) return
  openPreview({ kind: 'url', label: url, source: 'plugin', url }, 'manual')
},
```

- **PR NousResearch/hermes-agent#90437 已关闭**（2026-08-20 用户要求回滚所有改动）——方案技术上成立，暂搁置；如要重新提起，需要重新 fork + commit + push + 开 PR
- SDK 一加新方法 → runtime 插件自动可用（`sdkImportMap` 把 `__HERMES_PLUGIN_SDK__` 全部 named exports 反射成 shim blob，runtime-loader 的 `installPluginSdk()` 注入 `globalThis`）
- **合并前 plugin 写法**（fallback 模式让老 SDK 不崩）：

```js
const hasPreviewAPI = typeof host.preview === 'function'

function handleOpen(url) {
  if (hasPreviewAPI) {
    try { host.preview(url); return } catch (e) { /* 落到下面 */ }
  }
  // fallback: 复制 URL 让用户手动粘贴到预览窗
  navigator.clipboard.writeText(url)
}
```

## ⚠️ PANES_AREA placement 切换 → 孤儿 tab 残留（2026-08-20 实测）

**现象**：第一次注册 `placement: 'floating'`，后改为 `placement: 'bottom'`——旧的浮动 pane 在 layout tree 里持续存在（空白卡片或卡在旧位置），不能删除、不能拖动、用户视觉困扰。

**根因**：layout tree 把 pane id 持久化到 localStorage（`hermes.desktop.tree`），但 placement 值由每次 `ctx.register` 的 `data` 决定。旧的 placement → 新的 placement 不会触发 layout tree 的 orphan 清理——`watchContributedPanes` 只检查 id 是否在当前贡献里，不在则不渲染；但 layout tree 旧 state 里的 pane id 仍绑定在旧 zone 上。

**清理方式**：
- **方案 A**（推荐）：改 pane id（如 `dsh-web-pane-v2`），让旧 id 在 layout tree 里彻底 orphan（layout tree 只渲染已注册 id，旧 id 自动消失）
- **方案 B**（干净）：用户按 ⌘K → 进 edit mode → 右键旧 pane → 删除

**根因级教训**：**永远不要在同一个 pane id 上切换 placement**——每次切换 placement 必须同时换 pane id。

## 决策树（下次复用）

```
用户要在 Hermes 内显示外部 URL
├─ 临时打开（点按钮看一下然后关）？
│  └─ host.preview(url) [PR 已关闭，待重新提起]
├─ 持久在 layout 里 + 用户能拖动/折叠？
│  ├─ 目标 URL 同源（不会跨 webSecurity）？
│  │  └─ PANES_AREA + placement: 'bottom'/'right'/'left' + iframe
│  └─ 目标 URL 跨源（DSH 本地服务、第三方 API 文档）？
│     ├─ PR #90437 可重提 → host.preview
│     └─ 临时方案：PANES_AREA + placement: 'floating' + iframe（关栏不影响但跨源阻止）
│        + 同步显示 <a target="_blank"> 让用户外部打开
└─ 永久独立窗口（多显示器、各任务专用）？
   └─ 改主仓库加 host.openWindow (BrowserWindow)
```

## 参考

- iframe 内部刷新的 `key` 状态法：见 SKILL.md「面板内嵌入外部 URL」节的 iframe 范式
- SDK 扩展 PR 模式：`references/sdk-extension-pr-pattern.md`
- host.preview 完整讨论：见 SKILL.md「插件打开 Hermes 预览面板」节
