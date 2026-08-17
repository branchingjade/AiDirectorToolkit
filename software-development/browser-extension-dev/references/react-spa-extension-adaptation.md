# React SPA 画布适配（RunningHub 新版画布实战，2026-08-10）

浏览器扩展适配第三方 React 应用（如 RunningHub 新版 React Flow 画布）的完整方法。
旧版画布是 Vue Flow（数据层通过 `#appVue.__vue_app__.$pinia` 全局可访问），新版换成 React Flow 后数据层藏进模块闭包——本文件是破译与写入的实战记录。

## 核心铁律：ISOLATED world 看不到 React fiber

**content script（ISOLATED world）的 `Object.keys(element)` 看不到页面 JS 设置的 expando 属性**——React 挂在 DOM 元素上的 `__reactFiber$xxx` / `__reactProps$xxx` 就是这种属性。在 MAIN world（WebBridge / 页面 console）能扫到 fiber，但插件 content script 里 `document.querySelector('.react-flow')` 后 `Object.keys()` 返回空、找不到 fiber 键 → 「未找到平台写入函数」。

**结论**：所有 fiber 扫描 + 调用页面内部函数，必须放在 MAIN world 的 bridge.js 里做，content script 通过 postMessage 协议请求、bridge 执行后回传结果。这与旧版 Vue 画布的 bridge 架构同构（`rename` / `rename-authority` 两个消息类型）。

## 破译平台写入链的方法（bundle 静态分析）

平台调试钩子（`window._exportYjsJSON` / `_canvasGetYjsNode` 等）的源码会泄漏内部函数名，顺着反推：

1. 列出页面加载的脚本：`document.scripts` → 拿 bundle URL
2. 本地下载 bundle（6.3MB 级别直接 curl 下载，别在页面里 fetch 会超时）
3. grep 关键符号：
   - `getFullNodesByIds` → 发现 `an()` 单例（`D6||(D6=new dFt),D6`），dFt 类持有 `ydoc`/`ynodes`（Y.Array of Y.Map）
   - `onNodeDataPatch` → 找到平台注册的权威写函数（`CUt({onNodeDataPatch: Ge})`）
   - 看函数体源码：`bn(e,t,n){jQ?.(e,t,n)}` → `jQ=e.onNodeDataPatch` → `an().patchNodeData(nodeId, patch, opts)` → `ydoc.transact()` 权威写入
4. 从 React fiber 的 `memoizedProps.onNodeDataPatch` 拿到实际函数引用（在 MAIN world 扫描：`rf[__reactFiber$xxx]` 向上到根、BFS child/sibling、检查 `memoizedProps`）

## 权威写入调用参数（关键坑）

```js
patchFn(nodeId, { label: newName, title: newName }, { allowFields: ['label','title'], immediate: true });
```

- **`allowFields` 必须显式传**——平台默认字段白名单会过滤掉 label（实测：不传则静默无效，传了才写入成功）
- `immediate: true` 立即写入
- 锁定节点（`data.labelLocked`）**只拦截 UI 双击入口**（`!editable || labelLocked` 才进入编辑态），不拦数据写入——权威写入天然绕过锁定
- 写入是异步的，等 300ms 左右让 Yjs 同步，然后可刷新页面验证持久化

## React Flow 虚拟化坑

- 视口外的节点 label 是 `visibility:hidden`（React Flow 12 虚拟化）——`getBoundingClientRect()` 有坐标但 `elementFromPoint()` 命中不到、点击/双击无效
- 测试点击前先确认节点在视口内：`getComputedStyle(label).visibility !== 'hidden'` + rect 在窗口范围内
- 画布 transform 是平台自己管理的，`store.setCenter/panBy/setViewport` 都不生效，别浪费时间

## 实测验证流程（复现用）

1. MAIN world 扫 fiber 找 `onNodeDataPatch`（434 个 fiber 内命中）
2. 直接调用 → Yjs label 立即变化，刷新页面持久化
3. content script 侧同样代码 → 找不到（ISOLATED world 限制）→ 确认必须走 bridge
4. postMessage 协议端到端：content 发 `{source:'rh-extension', type:'rename-authority', nodeId, newName}` → bridge 执行 → 回 `{source:'rh-bridge', type:'rename-authority-result', ok:true}` → 验证 Yjs 变化

## 其他坑

- `__ $YJS$ __` 是 boolean 标记（Yjs 库存在标志），不是 doc 引用——别在它身上找写入口
- `_canvasGetYjsNode` 返回的是 toJSON 快照（普通对象无 set 方法），不是 Y.Map 引用——不能直接改
- WebBridge evaluate 长脚本会超时/断连，拆成小步调用；页面 JSON.stringify 巨大对象（如 Yjs 全局）会卡死线程
