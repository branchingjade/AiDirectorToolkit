# 从 RunningHub ComfyUI iframe 提取工作流数据

通过 Kimi WebBridge 的 `evaluate` 工具，访问 RunningHub 页面内嵌的 ComfyUI iframe，提取 `app.graph` 中的完整工作流数据。

## 前提

- Kimi WebBridge 守护进程运行中（`localhost:10086`）
- 用户 Chrome 已登录 RunningHub
- 工作流页面已打开且渲染完成（SPA 需等待）

## 步骤

### 1. 打开页面

```json
{"action":"navigate","args":{"url":"https://www.runninghub.cn/workflow/工作流ID","newTab":true,"group_title":"提取"},"session":"rh-extract"}
```

### 2. 等待渲染后提取节点

```javascript
const iframe = document.querySelector('iframe');
const app = iframe.contentWindow.app;
const graph = app.graph;
const nodes = Object.values(graph._nodes);

// 每个节点提取
nodes.map(n => ({
    id: n.id,
    type: n.type,
    title: n.title,
    widgets: n.widgets?.map(w => w.value),  // 参数值
    inputs: n.inputs?.map(i => ({
        name: i.name,
        type: i.type,
        link: i.link  // 有连线时
    })),
    outputs: n.outputs?.map(o => ({
        name: o.name,
        type: o.type,
        links: o.links  // 连出的 link_id 数组
    }))
}))
```

### 3. 提取连线

```javascript
const links = graph.serialize().links;
// 格式: [link_id, from_node, from_slot, to_node, to_slot, type]
links.map(l => ({
    link_id: l[0],
    from_node: l[1],
    from_slot: l[2],
    to_node: l[3],
    to_slot: l[4],
    type: l[5]
}))
```

### 4. 提取分组

```javascript
const groups = graph.serialize().groups;
// 格式: [{title, bounding: [x,y,w,h], color, font_size}, ...]
```

### 5. 列出 graph 方法（探索用）

```javascript
Object.getOwnPropertyNames(Object.getPrototypeOf(graph))
    .filter(m => typeof graph[m] === 'function')
// -> serialize, asSerialisable, getNodeById, findNodesByType, findNodesByClass, ...
```

## 注意事项

- RunningHub 的 ComfyUI iframe 和父页面同源，`contentWindow.app` 可直接访问
- `serialize()` 返回编辑器格式（nodes + links 数组），非 API 格式
- `graphToPrompt()` 返回 API 格式但可能在 RH 环境中为空
- 提取应在页面完全渲染后（等 iframe 加载 + 画布显示节点），否则 `app.graph._nodes` 可能为空
- 使用 `evaluate` 而非 `snapshot`——snapshot 只能看到可访问性树，看不到 JS 运行时数据
