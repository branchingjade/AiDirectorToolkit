---
name: runninghub-workflow-authoring
description: "在 RunningHub 平台上编写/修改/生成 ComfyUI 工作流 JSON。包含 RH 特有节点、JSON 格式规范、程序化生成模式。触发词：RunningHub 工作流、RH JSON、写工作流、导出工作流、GetNode、SetNode。"
version: 1.0.0
category: creative
---

# RunningHub Workflow Authoring

在 RunningHub 平台上编写和生成 ComfyUI 工作流 —— 从零建或基于模板修改。

## When to Use

- 用户要在 RunningHub 上创建新工作流
- 需要基于现有工作流生成变体（改参数、增减路径）
- 需要批量生成多个测试工作流 JSON
- 需要了解 RH 特有节点的用法

## Core Knowledge

### RH JSON Format (Editor Format)

RH 使用 ComfyUI editor 格式，不是 API 格式。顶层包含 `nodes[]`、`links[]`、`groups[]`：

```
{
  "id": "00000000-0000-0000-0000-000000000000",
  "last_node_id": 349,
  "last_link_id": 592,
  "nodes": [...],    // 节点数组
  "links": [...],    // 连线数组 [id, from_node, from_slot, to_node, to_slot, type]
  "groups": [...],   // 画布分组
  "config": {},
  "extra": {"ds": {"scale": 0.7, "offset": [-1400, -2100]}},
  "version": 0.4
}
```

### Link Format

```json
[link_id, from_node_id, from_slot_index, to_node_id, to_slot_index, type_string]
```

链接 ID 必须连续且不超过 `last_link_id`。slot 从 0 开始计数。

### Node Port Structure

每个节点必须有完整的 `inputs[]` 和 `outputs[]` 数组：

- **Linked input**: `{"label":"model","name":"model","type":"MODEL","link":519}` — `link` 值是 links 数组中的 link_id
- **Widget input**: `{"label":"seed","name":"seed","type":"INT","widget":{"name":"seed"}}` — 值来自 `widgets_values[]`，按位置对应
- **Optional input**: `"shape":7` 标记可选
- **Output**: `{"label":"IMAGE","name":"IMAGE","type":"IMAGE","links":[530,532]}` — `links` 是该端口发出的 link_id 列表

## RH-Specific Nodes

### GetNode
- 类型: `GetNode`
- 用途: 引用用户上传的图片，作为工作流输入源
- 特点: 有 `title` 字段（如 "Get_原图"），widget 为 `["原图"]`
- 输出: 单个 IMAGE 端口
- 注意: 多个 GetNode 可以引用同一张上传图

### SetNode
- 类型: `SetNode`
- 用途: 透传/路由节点
- 输入: IMAGE，输出: IMAGE

### ModelSamplingAuraFlow
- 类型: `ModelSamplingAuraFlow`
- 用途: RH 平台的 AuraFlow 采样封装
- 输入: model(MODEL linked), shift(FLOAT widget)
- 输出: MODEL

### SeedVR2 / SeedVR2BlockSwap
- `SeedVR2`: 视频超分模型（也用于单图修复）
- `SeedVR2BlockSwap`: SeedVR2 的显存管理配置节点

## HM-RunningHub 模型封装节点

RH 官方 GitHub (https://github.com/HM-RunningHub) 提供 25+ 模型封装节点，分类见 `references/rh-model-nodes.md`。常用：

| 节点类型 | 用途 | 输入 |
|---------|------|------|
| `RunningHub ICCustom Loader` + `RunningHub ICCustom Sampler` | 图像定制/修复，有 ref_image 图输入 | IMAGE → 修复后 IMAGE |
| `RH_QwenImageGenerator` | 文生图（无图输入） | text prompt → IMAGE |

## Generation Pattern

始终从已验证的模板工作流出发生成变体。用 `copy.deepcopy()`：

```python
import copy, json

with open("template.json") as f:
    tpl = json.load(f)

wf = copy.deepcopy(tpl)

# 删节点
remove_ids = {326, 333}
wf["nodes"] = [n for n in wf["nodes"] if n["id"] not in remove_ids]

# 删连线
remove_links = {553, 554}
wf["links"] = [l for l in wf["links"] if l[0] not in remove_links]

# 加新节点（从模板节点深拷贝）
new_node = copy.deepcopy(getnode_template)
new_node["id"] = 500
new_node["pos"] = [100, 3000]
wf["nodes"].append(new_node)

# 加连线
wf["links"].append([700, 500, 0, 502, 1, "IMAGE"])

# 更新计数器
wf["last_node_id"] = max(n["id"] for n in wf["nodes"])
wf["last_link_id"] = max(l[0] for l in wf["links"])

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
```

## Validation

生成后必须校验（用户会直接指出连线错误）：

1. 所有 link 的 from_node/to_node 在 nodes 中存在
2. 所有 link 的 slot 索引 ≤ 对应节点 ports 数量
3. `widgets_values[]` 数量匹配 widget 类 input 数量
4. GetNode 有 `title` 字段
5. Image Comparer 的 `widgets_values` 为 `[[]]`（空嵌套数组）
6. LoadImage、GetNode、SetNode 三者都存在
7. LoadImage 输出连到 SetNode 输入

### 端口 link 引用同步

修改 links 数组后必须同步节点端口引用：

```python
# 清旧引用
for n in wf["nodes"]:
    for i in n.get("inputs", []):
        if "link" in i: i["link"] = None
    for o in n.get("outputs", []):
        if "links" in o: o["links"] = []

# 从 links 数组重建
nodes = {n["id"]: n for n in wf["nodes"]}
for l in wf["links"]:
    lid, fn, fs, tn, ts, _ = l
    nodes[fn]["outputs"][fs].setdefault("links", []).append(lid)
    nodes[tn]["inputs"][ts]["link"] = lid
```

## Pitfalls

1. **write_file 对大 JSON 不可靠** — 超过 ~10KB 可能静默写 0 字节。用 Python `json.dump()` 或 terminal `python3 -c` 写文件
2. **空 ports 的节点不接受连线** — 新节点必须从模板深拷贝，不能手动造空 inputs/outputs
3. **widgets_values 按位置匹配** — 不是按 name，顺序错了参数就错
4. **Clean GPU 节点需要 `color`/`bgcolor`** 字段才能在画布渲染
5. **节点类型名称含空格和括号要原样保留** — 如 `"Image Comparer (rgthree)"`、`"LayerUtility: ImageScaleByAspectRatio V2"`
6. **从浏览器提取模板用 `app.graph.serialize()`** — 返回 editor 格式，不是 API 格式
7. **NODE_CLASS_MAPPINGS key ≠ Python class name** — 在用如 `"RunningHub ICCustom Sampler"` 而非 `"RH_ICCustom_Sampler"`。从 HM-RunningHub 仓库的 `__init__.py` 确认注册名
8. **LoadImage → SetNode 必须连线** — RH 需要这个连线才能正确识别上传/输出，即使 SetNode 输出端无下游
9. **links 数组和端口 link 引用必须同步** — 删连线后必须同时清理对应 `outputs[i].links` 和 `inputs[i].link`，否则 UI 显示断线。修改后运行同步脚本
10. **三个上传节点缺一不可** — 每个 RH 工作流必须有 LoadImage + GetNode + SetNode
