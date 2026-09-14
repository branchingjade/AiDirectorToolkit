# iframe 黑屏陷阱与 placement 绑定坑

实测日期：2026-08-20。来源：dsh-settings 插件 4 轮 iframe 嵌入迭代。

## 陷阱1：`style: { background: '#0d0d0d' }` 导致 iframe 黑屏

**现象**：iframe 嵌入 DSH Web UI 后显示纯黑，用户误判"DSH 没启动"。但 `curl -I http://127.0.0.1:8080/` 返回 200 OK，浏览器直接访问正常。

**根因**：`#0d0d0d` 是深色背景色（接近纯黑）。iframe 在加载期间或加载失败时显示该背景色，视觉上就是黑屏——DSH web UI 本身是浅色主题（React + Tailwind dark mode 需要 JS 渲染才生效）。

**修复**：`style: { border: '0', background: '#fff' }`（或完全不设背景）。DSH web UI 自己是浅色，加载期间/失败时都显示白底，用户不会误判。

**其他场景适用**：所有在 Hermes 桌面 iframe 里嵌入浅色 web UI（React/Vite 默认浅色主题）的场景——不要给 iframe 设深色背景。

## 陷阱2：`placement: 'right'` 让 pane 绑定在右侧栏

**现象**：用户关闭右侧栏时 DSH Web UI 的 pane tab 也跟着消失。用户问"为什么关了侧边栏 DSH 窗口也会跟着关"。

**根因**：layout tree 的 zone 绑定机制——`placement: 'right'` 的 pane 归属于右侧栏 zone，zone 关闭时其内所有 pane 一起消失。同理 `'left'` 绑定左侧栏，`'bottom'` 绑定底部栏。

**placement 选择决策树**：

| placement | 影响 | 适用场景 |
|---|---|---|
| `'right'` | 绑定右侧栏，关栏即关 | 嵌入式面板（用户接受关栏连带关） |
| `'bottom'` | 绑定底部栏，关栏即关 | 嵌入式面板（底部栏通常不关） |
| `'left'` | 绑定左侧栏，关栏即关 | 嵌入式面板（如 ops-panel） |
| `'floating'` | 完全独立，不受任何栏影响 | 需要独立浮动的监控面板 |

**用户真实诉求**（实测）：
- "嵌入 Hermes 里面" → 需要 `placement: 'right'/'bottom'/'left'`
- "关其他栏不影响" → 需要 `placement: 'floating'`
- **两者互斥**——只能选其一

**推荐**：默认 `'floating'`（独立不受影响），用户明确接受关栏影响时改 `'right'`/`'bottom'`。

## 陷阱3：`floating` placement 不能 resize

**现象**：浮动 pane 只能拖动位置和折叠/展开，不能通过拖拽边框调整大小（宽高固定在 `data: { width: N, height: N }`）。

**根因**：`floating-panes.tsx` 的 `FloatingPane` 组件用 `fixed` 定位，没有 resize handle。这是 Hermes 桌面的设计限制——floating pane 是"飘浮卡片"不是"可调窗口"。

**如果用户需要 resize**：必须用 `placement: 'right'/'bottom'/'left'`（layout tree 内的 pane 有 resize 句柄），但会绑定到对应 zone。

## 决策树

```
用户要在 Hermes 内显示外部 URL
├─ 需要嵌入 Hermes（不能是系统浏览器）？
│  ├─ 需要 resize 调整大小？
│  │  └─ placement: 'bottom'（底部栏日常不关）或 'right'（接受关栏连带关）
│  └─ 不需要 resize（可接受固定大小）？
│     └─ placement: 'floating'（独立浮动，不受任何栏影响）
├─ 需要临时打开（点按钮看一下然后关）？
│  └─ host.preview(url)（PR #90437 合并后）
└─ 可以用系统浏览器？
   └─ window.open(url, ...) 或 <a target="_blank">
```
