---
name: runninghub-workflow
description: RunningHub 工作流提取、编写与调试。触发词：RH、RunningHub、runninghub、RH工作流、RH节点、RH导入、GetNode、SetNode。
version: 1.0.0
---

# RunningHub Workflow

在 RunningHub 平台上提取、编写和调试 ComfyUI 工作流 JSON。

## 架构认知

RunningHub = ComfyUI 内核 + RH 平台壳。

### 节点体系三层

```
标准 ComfyUI 节点    → LoadImage, KSampler, CLIPTextEncode, SaveImage ...
社区插件节点          → Impact Pack (PixelKSampleUpscalerProvider), rgthree (Image Comparer), WAS Suite, LayerUtility ...
HM-RunningHub 封装   → 34 个官方仓库，每个封装一个开源模型为 ComfyUI 节点
RH 平台特有           → GetNode, SetNode, ModelSamplingAuraFlow
```

### HM-RunningHub 组织

GitHub: `https://github.com/HM-RunningHub`，34 个仓库，全部是模型封装。每个仓库结构统一：`nodes.py`（节点定义）、`__init__.py`（注册）、`rh_config.json`（平台配置）。

关键：**Python 类名 ≠ ComfyUI 注册名**。检查 `__init__.py` 末端的 `NODE_CLASS_MAPPINGS` 获取实际注册名。例如 ICCustom 类名 `RH_ICCustom_Loader`，注册名 `RunningHub ICCustom Loader`。

### RH 上传三件套

每个 RH 工作流必须有：

| 节点 | 类型 | 作用 |
|------|------|------|
| LoadImage | 内置 | 上传控件，用户在此拖入图片 |
| GetNode("名称") | RH 特有 | 引用已上传的图片，多路径共享 |
| SetNode("名称") | RH 特有 | 输出声明，须有连线从 LoadImage 流入 |

GetNode 无输入端口，通过 widget `Constant` 值引用同名图片。同一工作流中多个 GetNode 可引用同一个上传。SetNode 接收 LoadImage 输出（link type `*`），其输出可为空。

## 从 RH 提取工作流 JSON

### 方法一：Kimi WebBridge 提取（有登录态）

必须通过用户真实 Chrome。步骤：

```
1. 打开 RH 工作流页面（等 SPA 渲染完成）
2. evaluate 进 ComfyUI iframe：
   const iframe = document.querySelector('iframe');
   const app = iframe.contentWindow.app;
   const graph = app.graph;  // graph 对象

3. 获取节点：graph._nodes（对象，key=id）
   每个节点有：type, title, id, inputs, outputs, widgets_values, pos, size, properties

4. 获取连线：graph.serialize().links
   格式：[link_id, from_node, from_slot, to_node, to_slot, type]

5. 检查 graph 方法：Object.getOwnPropertyNames(Object.getPrototypeOf(graph))
   关键方法：serialize(), asSerialisable(), getNodeById(), findNodesByType()
```

详细提取参考见 `references/comfyui-iframe-extraction.md`。

### 方法二：RH 画布导出

右上角下载按钮 → 导出 JSON。或使用用户浏览器操作。

## 编写 RH 工作流 JSON

### 完整 JSON 结构

```json
{
  "id": "0", "revision": 0,
  "last_node_id": N, "last_link_id": M, "version": 0.4,
  "config": {}, "extra": {"ds": {"scale": 0.7, "offset": [-1400,-2100]}},
  "nodes": [...],
  "links": [[link_id, from_node, from_slot, to_node, to_slot, "TYPE"], ...],
  "groups": [{"title":"分组名","bounding":[x,y,w,h],"color":"#hex","font_size":24}]
}
```

### 节点必需字段

```json
{
  "id": N,
  "type": "NodeClassType",
  "pos": [x, y],
  "size": [w, h],
  "flags": {},
  "order": 0,
  "mode": 0,
  "inputs": [
    {"label":"显示名","name":"内部名","type":"TYPE"},
    {"label":"参数名","name":"param","type":"FLOAT","widget":{"name":"param"}}
  ],
  "outputs": [
    {"label":"显示名","name":"内部名","type":"TYPE","links":[link_id,...]}
  ],
  "properties": {"Node name for S&R": "别名"},
  "widgets_values": [值1, 值2, ...]
}
```

**关键规则：**

1. **input 分两类**：有 `widget` 的是参数输入（值在 `widgets_values` 中），无 `widget` 的是连线输入（link 在 `inputs[i].link` 中）
2. **outputs[].links 必须与全局 links 数组同步**：每个 link_id 同时出现在 `links` 数组和源节点的 `outputs[slot].links` 中
3. **inputs[].link 必须与全局 links 数组同步**：目标节点的 input 端口须有 `link` 字段指向该 link_id
4. **widgets_values 顺序**与 `inputs` 中有 widget 的端口一一对应
5. **mode=4** 为输出节点（SaveImage 等），**mode=0** 为普通节点

### 连线同步（最常见的错误）

生成或修改 JSON 后必须执行同步：

```python
# 1. 清空所有端口 link 引用
# 2. 遍历 links 数组，对每条 link：
#    - 源节点 outputs[from_slot].links 添加 link_id
#    - 目标节点 inputs[to_slot].link = link_id
```

见 `scripts/sync_links.py`。

## 已验证的关键配置

### 迭代放大修复路径（原 "修复图片" 工作流）

| 节点 | 关键参数 | 值 |
|------|---------|-----|
| CheckpointLoaderSimple | ckpt_name | `z-image-turbo-bf16-aio.safetensors` |
| Upscale Model Loader | model_name | `RealESRGAN_x4plus.pth` |
| PixelKSampleUpscalerProvider | denoise | 0.25 |
| | steps | 3 |
| | CFG | 1 |
| | sampler | dpmpp_2m_sde |
| | scheduler | sgm_uniform |
| | tile_size | 512 |
| | scale_method | nearest-exact |
| ImageScaleToTotalPixels | megapixels | 1 |
| | upscale_method | nearest-exact |
| IterativeImageUpscale | upscale_factor | 1.5 |
| CLIPTextEncode (positive) | text | 空 |
| CLIPTextEncode (negative) | text | 空 |
| ModelSamplingAuraFlow | shift | 1 |

### SeedVR2 路径

| 节点 | 参数 | 值 |
|------|------|-----|
| SeedVR2 | model | `seedvr2_ema_7b_fp8_e4m3fn.safetensors` |
| | seed | 9527, fixed |
| | new_resolution | 2048 |
| | batch_size | 5 |
| SeedVR2BlockSwap | blocks_to_swap | 16 |
| | use_non_blocking | true |
| | offload_io_components | false |

## CFG=1 + 空 prompt 的修复机制

详见 `references/cfg1-restoration.md`。

核心：关闭文本引导，扩散模型退化为无条件的"投影到自然图像流形"操作。只修正偏离训练分布的部分——压缩噪声、VAE 模糊——不创造新内容。配合 denoise=0.25 恰好抹平伪影而不越界。

## Pitfalls

1. **Python 类名 ≠ NODE_CLASS_MAPPINGS 注册名**。必须查 `__init__.py` 端。ICCustom 类是 `RH_ICCustom_Loader`，注册名是 `RunningHub ICCustom Loader`。

2. **links 数组和端口 link 引用必须同步**。只写 links 数组不写节点端口引用 = 画布里线看起来断了。使用 `scripts/sync_links.py` 自动同步和验证。

3. **GetNode/SetNode/LoadImage 三件套缺一不可**。RH 用这套机制管理输入输出，缺少 LoadImage 用户无法上传图片，缺少 SetNode 输出声明不完整。

4. **widgets_values 顺序必须和 inputs 中有 widget 的端口对应**。位置错了 → 参数写进了错误字段。

5. **write_file 对大 JSON（>14KB）可能静默失败**。验证文件大小非零再继续。备选：terminal python3 -c 写文件。

6. **从截图视觉估计参数不可靠**。denoise 0.65 vs 0.25、steps 8 vs 3 都是视觉误读。必须从节点 widget 或 app.graph 提取真实值。参考 `references/rh-comfyui-extraction.md`。

7. **ICCustom 等 HM-RunningHub 封装的节点 RH 云端不一定已部署**。导入时节点报红（class_type not found）说明云端未上该插件，不是 JSON 错误。

8. **SeedVR2 的 `extra_args` 不接时有硬编码默认值**：tiled_vae=true, vae_tile_size=512, preserve_vram=false, cache_model=false, temporal_overlap=0（单图模式）。

9. **生成 JSON 必须从完整模板克隆节点**——手动造节点的 input/output 端口定义极易遗漏 widget 引用和 properties 元数据，导致导入后参数面板空白。

10. **从截图视觉估计参数不可靠**——denoise 0.25 被误读为 0.65、steps 3 被误读为 8。必须从节点 widget_values 或 app.graph 提取真实值。

11. **不要盲目加 prompt 和提 denoise**——CFG=1 空 prompt 的设计是有意为之，加 prompt 和提高 denoise 反而引入新人工痕迹。参考 `references/restoration-workflow-design.md`。

## Reference Files

- `references/cfg1-restoration.md` — CFG=1 + 空 prompt 修复机制详解
- `references/restoration-workflow-design.md` — "修复图片"工作流完整架构分析：CFG=1 机制、GAN+扩散互补、参数选择依据
- `references/seedvr2-versions.md` — SeedVR2 fork 版 (lihaoyun6) vs 原版 (numz v2.5.x) 参数差异与 color_correction
- `references/rh-comfyui-extraction.md` — 通过 Kimi WebBridge 从 RH 提取工作流数据
- `scripts/sync_links.py` — 同步并验证 links 数组与节点端口引用
