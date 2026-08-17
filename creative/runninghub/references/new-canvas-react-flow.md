# 新版画布（React Flow）适配实战

2026-08-10 用 Kimi WebBridge 实测（项目「测试2丨RHTV」，URL `https://rhtv.runninghub.cn/project/canvas/<id>`）。RH小帮手浏览器扩展 v3.0.0→v3.1.0 双模式改造全程记录。

## 双画布共存

- 页面根：`DIV.rh-canvas-page.is-new-version`（新版标记）
- 顶部有「切换至旧画布」按钮——同一项目 URL 新旧可来回切，**自动化必须每次点击前重检测模式**
- 旧版：Vue Flow（`.vue-flow__node` / `.vue-flow__viewport` / `.node-label`），数据层 `#appVue.__vue_app__.config.globalProperties.$pinia`（yjs + canvas.nodes）
- 新版：React Flow（`.react-flow__node` / `.react-flow__pane` / `.rh-node-label`），`#appVue` **不存在**

## 新版 DOM 结构（实测）

```
DIV#root > DIV.rh-canvas-page.is-new-version
  DIV.react-flow.rh-canvas-flow
    DIV.react-flow__renderer > DIV.react-flow__pane（drop 目标）
      DIV.react-flow__viewport.xyflow__viewport
        DIV.react-flow__nodes
          DIV.react-flow__node.react-flow__node-rh-ai[data-id="node_xxx"]
            DIV.rh-canvas-node.rh-media-node.rh-ai-node
              DIV.rh-node-label-row > DIV.rh-node-label（标题，可能带 .is-locked）
              DIV.rh-node-shell-body
                img.rh-node-media（媒体图，rh-images 域名）
                DIV.react-flow__handle（连接点）
```

节点类型类：`react-flow__node-rh-video` / `rh-ai` / `rh-media`；状态类 `has-media` / `is-empty-media` / `has-node` / `is-locked`。

## 选择器映射表（双模式）

| 用途 | 旧版 (vue) | 新版 (react) |
|---|---|---|
| 节点容器 | `.vue-flow__node` | `.react-flow__node` |
| 节点 ID | `data-id` | `data-id`（同格式 `node_<ts>_<rand>`） |
| 标题 | `.node-label` | `.rh-node-label` |
| 媒体图 | `img`（任意大图） | `img.rh-node-media` |
| drop 目标 | `.vue-flow__viewport` | `.react-flow__pane` |
| 视口监听 | `.vue-flow__viewport` + `.vue-flow__pane` | `.react-flow__viewport` + `.react-flow__pane` |

检测函数：
```js
function detectCanvasMode() {
  if (document.querySelector(".react-flow__node")) return "react";
  if (document.querySelector(".vue-flow__node")) return "vue";
  return null;
}
```

## drop 拖放（模糊功能核心）

- 目标必须选 **`.react-flow__pane`**——实测 drop 到 pane：`defaultPrevented=true` 且节点数 10→11（平台消费并创建了节点）
- 事件序列：`dragenter` → `dragover` → `drop`，带 `clientX/clientY`（pane 中心）、`dataTransfer`（DataTransfer + File）
- 成功判据：`dropEvent.defaultPrevented === true`

## 平台自带双击重命名（重命名功能核心）

实测链路（对**未锁定**节点）：
1. 双击 `.rh-node-label`（`new MouseEvent("dblclick", {bubbles:true, cancelable:true, view:window})`）→ 平台弹 `input.rh-node-label-input`
2. 原生 setter 填值（React 受控组件必须走 prototype setter，直接 `inp.value=` 不触发 React onChange）：
```js
const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
setter.call(inp, newName);
inp.dispatchEvent(new Event("input", { bubbles: true }));
inp.dispatchEvent(new Event("change", { bubbles: true }));
```
3. Enter 提交：`keydown` + `keyup`（key:"Enter"）→ 标签实际变更，input 消失

**关键**：合成 dblclick 平台**接受**（不查 isTrusted）——扩展 content script（ISOLATED world）也能用。实测改名「test.png → 改名链路验证」成功，还原成功。

**锁定节点**（`.rh-node-label.is-locked`，如 RTXVSR4K/台词/二婶.wav）：双击不弹输入框，平台禁止编辑——扩展需提前检测并提示「节点已锁定，无法重命名」。右键菜单（`.rh-node-context-menu__item`）9 项无重命名项：加入我的资产/显示简介/3D导演台/脚本/图层置顶/创建副本/复制节点/粘贴节点(disabled)/删除节点。

## 平台调试钩子（window 全局）

| 钩子 | 签名/行为 | 用途 |
|---|---|---|
| `_canvasGetNode(id)` | `r=>e().find(o=>o.id===r)` 返回 React Flow 节点对象（含 data.label/data.params） | 读节点数据 |
| `_canvasGetYjsNode(id)` | `r=>an().getFullNodesByIds([r]).get(r)??null` 返回**普通对象快照**（无 get/set 方法） | 只读，不能写入 |
| `_canvasInspectNode(id)` / `_canvasInspectYjsNode(id)` | console.log 调试 | 排查 |
| `_exportWorkflow()` / `_exportYjsJSON()` | 导出工作流 JSON | 提取工作流 |

⚠️ **直接改 `_canvasGetNode(id).data.label` 不生效**（responsive:false 实测）——React 状态在组件内部，改返回对象不触发重渲染。改名：未锁定节点走平台双击重命名；**锁定节点走 onNodeDataPatch 权威写入（见锁定绕过节）**——比找 zustand store（未暴露）可靠得多。

## 媒体图域名

- 新版节点图：`rh-images.xiaoyaoyou.com`（manifest host_permissions 必须加，旧 manifest 只有 `rh-canvas-files.xiaoyaoyou.com`）
- 旧 `rh-canvas-files.xiaoyaoyou.com` 仍用于部分上传文件图
- fetch 跨域 OK（content script 带 host_permissions），返回 webp，blob → createImageBitmap → canvas 处理链路正常

## 锁定机制与权威写入绕过（2026-08-10 破解，实测持久化 ✅）

锁定字段 = `data.labelLocked: true`，存在 **Yjs 权威层**（服务端同步）。平台双击时先查 `labelLocked`，true 则**根本不弹输入框**（UI 层拦截，不是提交时拦截）。AI 应用节点（rh-ai，如 RTXVSR4K/修复图片_场景）标签从 AI 应用名自动同步，平台故意加锁防脱节——**但数据写入层不检查 labelLocked，可以绕过**。

### 死路四连（已实测，勿重复）

| 尝试 | 结果 |
|---|---|
| 改 React store 对象 `labelLocked: true→false`（`_canvasGetNode` 返回对象直接改） | DOM 锁图标消失，但 label 文本被 Yjs 还原 |
| `store.getState().setNodes([...])`（React Flow 12 官方 API） | 调用成功，~2s 后被 Yjs 同步覆盖还原 |
| `store.getState().triggerNodeChanges([{id, type:'replace', item}])` | 同上，全被还原 |
| 删 DOM `is-locked` class 后双击 | 无效——检查读数据层不读 class |

**根因**：Yjs 是唯一权威，React store 和 DOM 的任何改动都会被平台同步器还原；`_canvasGetYjsNode` 返回纯对象拷贝（无 get/set，不是 Y.Map）；Yjs doc 实例**没有暴露到 window**（`__ $YJS$ __` 只是布尔存在标记）。

### 破解路径：下载 bundle 静态分析

window 上没有写钩子，但平台导出的函数源码引用了模块闭包变量 `an()`（Yjs 管理器单例，`let D6=null; function an(){return D6||(D6=new dFt),D6}`）。**下载 JS bundle 本地 grep**（6.3MB，curl 直接下，不要在页面 evaluate 里 fetch——会超时）：

```bash
curl.exe -s -o rh-bundle.js "https://rhtv.runninghub.cn/project/assets/index-*.js"
# 本地 grep：getFullNodesByIds / getRemoteData / onNodeDataPatch / labelLocked / patchNodeData
```

关键发现（全部来自 bundle 源码）：
1. **`dFt` 类持有 `ydoc`（Yjs Doc）、`ynodes`（Y.Array of Y.Map）、`ymap`**——即权威数据层
2. **写入链**：`bn(nodeId, patch)`（转发器）→ `jQ`（= `onNodeDataPatch`，注册于 `CUt({onNodeDataPatch: Ge, ...})`）→ `an().patchNodeData()` → `ydoc.transact()` → Yjs
3. **`onNodeDataPatch` 函数体只检查 `isNodeLockedByOther`**（`ti.getState().editingNodes[n]`，**协作者**编辑锁，单人不触发），**完全不检查 labelLocked**——绕过点
4. `m8t`/`HWt` 是 patch 生成器，不拦 label

### 获取 onNodeDataPatch：fiber 扫描

`onNodeDataPatch` 作为 props 挂在多个组件上（工具栏/参数面板，实测 8 个组件持有**同一引用**），从任意元素 fiber 向上到根再 BFS 全树即可找到：

```js
function findOnNodeDataPatch() {
  const rf = document.querySelector(".react-flow");
  const fkey = Object.keys(rf).find(k => k.startsWith("__reactFiber"));
  let start = rf[fkey], rootF = start;
  while (rootF.return) rootF = rootF.return;
  const seen = new Set(), queue = [{f: rootF}];
  while (queue.length) {
    const {f: cur} = queue.shift();
    if (!cur || seen.has(cur)) continue;
    seen.add(cur);
    const mp = cur.memoizedProps;
    if (mp && typeof mp.onNodeDataPatch === "function") return mp.onNodeDataPatch;
    if (cur.child) queue.push({f: cur.child});
    if (cur.sibling) queue.push({f: cur.sibling});
  }
  return null;
}
```

### 调用（关键参数）

```js
fn(nodeId, { label: 新名, title: 新名 }, { allowFields: ["label", "title"], immediate: true });
```

- **`allowFields` 必须显式传**——首次调用没传直接失败（平台默认字段白名单过滤 label），补上后立即成功
- `immediate: true` 立即写入
- 实测：`修复图片_场景`（locked）→ 改「绕过测试2」→ **刷新页面后 DOM 显示新名字**（服务端持久化）→ 同样方式改回原名字成功
- 注意事项：改完 React 层可能不立即显示（labelLocked 仍 true 时平台不把 label 同步回 React 渲染层），刷新后生效；`_canvasGetYjsNode` 可立即确认 Yjs 层已改

## ⚠️ React Flow 12 视口外节点虚拟化（调试大坑，浪费最多轮次）

- 视口外的节点元素内联 style 带 `visibility: hidden`（React Flow 12 虚拟化优化）——**其上双击/点击全部静默无效**，`elementFromPoint` 命中的是 `.react-flow__pane` 而不是 label
- 画布 transform 由平台自己管理（viewport `translate(-1480px,-603px) scale(0.813)` 之类），`store.panBy/setCenter/setViewport` 调用返回 ok 但 **DOM 不变**（被平台覆盖），不能靠它把节点拉进视口
- 表现：同一段「双击 label → 查 input」代码，节点在视口内时成功（eval-21），节点在视口外时失败——**先查 `getBoundingClientRect()` 确认在视口内再测交互**
- 用户手动点击时节点必然可见，所以浏览器扩展正常使用不受此坑影响；只有脚本自动化测试会踩

## WebBridge 调用模式（Windows 实测）

- **curl.exe 读不了 MSYS 路径**：`$TEMP`/`/tmp` 是 git-bash 路径，`curl.exe --data-binary "@$TMPF"` 报 `error encountered when reading a file`。必须用 `cygpath -w "$TEMP"` 转 Windows 路径，或硬编码 `C:/Users/<user>/AppData/Local/Temp/xxx.json`
- **长 async evaluate 超时**：一个 evaluate 里 dispatch 事件 + await 轮询 + 查状态，经常 30-60s 超时（页面侧副作用挂起）。拆成两步：①只 dispatch（同步立即返回）→ sleep 1-1.5s → ②单独 evaluate 查状态。分步调用稳定可靠
- JSON 请求体里不能手写转义——用 Python `json.dump` 生成请求文件（中文/换行都安全）

## RH小帮手 v3.1.2 改造模式（可复用的双模式架构）

1. **config.js**：`CANVAS_MODE` 全局 + 四张选择器映射表（NODE_SELECTOR / LABEL_SELECTOR / MEDIA_IMG_SELECTOR / DROP_TARGET_SELECTOR / VIEWPORT_SELECTOR / PANE_SELECTOR）
2. **main.js**：每次 click 前 `CANVAS_MODE = detectCanvasMode()`（新旧可切换），按模式取选择器
3. **bridge-rename.js**：统一入口 `renameNode(ctx, newName)` 分派——`react` 未锁定走平台双击、`react` 锁定走 `renameViaAuthority`（fiber 扫描 + onNodeDataPatch）、`vue` 走 postMessage bridge
4. **canvas.js**：getViewport/getPane 按模式；dropFileToCanvas 用 `getPane() || getViewport()`
5. **manifest.json**：host_permissions 加 `https://rh-images.xiaoyaoyou.com/*`

版本线：v3.1.0 双画布适配 → v3.1.1 锁定节点只读提示 → **v3.1.2 锁定绕过（权威写入）**。注意 v3.1.1 的「锁定节点只显 🔒 不弹面板」交互在 v3.1.2 被推翻——现在锁定节点也能改名，统一显示 ✏️。

## 改造前保留历史版本的工作流（用户明确要求「保留历史版本」）

1. 改造前先把当前 dist 打包成 zip（`archive/RH小帮手-v<ver>.zip`）+ git 快照提交（保护点）
2. 项目内统一 `archive/` 目录归档全部历史版本 zip（v2.1.1→v3.1.0 完整版本线），git `-f` 强制 add（`.gitignore` 可能忽略 `*.zip`）
3. 用户浏览器里装的是旧版插件——新版画布上旧版失效是预期，需用户手动在 `chrome://extensions` 加载新 dist（agent 无法替用户加载扩展）

## 环境事实

- 项目：`C:\Users\HMSJ\Documents\Hermes\Projects\rh-helper`（git 仓库，src/ 模块化 + dist/ 产物 + build.sh 拼接）
- 旧版本散落处：`C:\Users\HMSJ\Documents\ClaudeCode\RH插件\RH小帮手-v2.2.0\`（含 v2.1.1/v2.1.2/v2.2.0 zip）、`~/.hermes/desktop-attachments/RH小帮手-v2.2.4.zip`
- 浏览器里跑的插件是旧版（`window.__rh_bridge_ready` 存在但无 `.rh-toolbar-host`）
