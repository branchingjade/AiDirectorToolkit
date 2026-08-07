---
name: runninghub-workflows
description: RunningHub 工作流编写、分析、调试。RH 节点生态、工作流 JSON 结构、从浏览器提取数据的方法。
version: 1.0.0
---

# RunningHub 工作流

在 RunningHub 云平台上编写、分析、调试 ComfyUI 工作流。

## 触发条件

- 用户要求在 RunningHub 上写/改/分析 **ComfyUI 工作流**（节点画布，非导演台）
- 用户分享 RH 工作流链接要求解析
- 需要在 RH 画布里操作节点
- 对比 RH 节点与本地 ComfyUI 节点的差异

> ⚠️ 如果用户提到「导演台」「HyperFrames」「3D 场景」「假人」「分镜」——那不是 ComfyUI 工作流，是 RunningHub 的另一个产品。见 `runninghub` skill 的「导演台 / HyperFrames」节。

## 核心架构

RH 节点体系 = 标准 ComfyUI 核心 + 社区插件 + HM-RunningHub 官方封装 + RH 平台特有节点。

## RH 平台特有节点

| 节点 | 作用 |
|------|------|
| `GetNode` | 上传图片引用。`widgets_values: ["原图"]`，多路共享同一上传图 |
| `SetNode` | 中间路由直通，`IMAGE→IMAGE` |
| `ModelSamplingAuraFlow` | RH 封装采样器 |
| `ImageScaleToTotalPixels` | 按总像素数缩放 |

## 从浏览器提取工作流数据

当用户在浏览器里打开了 RH 工作流页面，可以用 Kimi WebBridge 进 ComfyUI iframe 提取：

```javascript
const iframe = document.querySelector('iframe');
const app = iframe.contentWindow.app;
const graph = app.graph;

// 所有节点
Object.values(graph._nodes).map(n => ({
  id: n.id, type: n.type, title: n.title,
  widgets: n.widgets?.map(w => ({name: w.name, value: w.value}))
}));

// 所有连线 [link_id, from_node, from_slot, to_node, to_slot, type]
graph.serialize().links;

// 完整序列化（editor format，可直接导入 RH）
graph.serialize();
```

## 工作流 JSON 结构

RH 使用 editor-format JSON（`nodes` + `links` 数组）。导入方式：画布右上角菜单 → 导入工作流，或直接拖入。

每个节点关键字段：`id`, `type`, `pos`, `size`, `mode`(0=normal, 4=output), `widgets_values`, `inputs`, `outputs`, `properties`, `order`。

连线格式：`[link_id, from_node, from_slot, to_node, to_slot, type]`。

## HM-RunningHub 官方封装

GitHub: https://github.com/HM-RunningHub (34 repos)

所有 `ComfyUI_RH_*` 仓库统一结构：`nodes.py` + `rh_config.json`。节点类 `CATEGORY` 使用 `"RunningHub/XXX"` 命名空间。

图像修复相关：
- **ICCustom** (36⭐): `RH_ICCustom_Loader` + `RH_ICCustom_Sampler`。Sampler 有 `ref_image` 输入（img2img），适合修复场景。
- **Qwen-Image** (92⭐): `RH_QwenImageGenerator`。⚠️ 纯 t2i，无图输入，不适合修复。
- **ZImageI2L** (64⭐): 图生 LoRA，提取个性化权重。
- **OminiControl** (142⭐): 主体驱动生成。

详见 `references/runninghub-ecosystem.md`。

## ICCustom 节点参考

```
RH_ICCustom_Loader: 无必填参数 → RHICCustomPipeline
RH_ICCustom_Sampler:
  slot 0: pipeline (RHICCustomPipeline, link)
  slot 1: ref_image (IMAGE, link, ⭐ img2img 输入)
  slot 2: prompt (STRING)
  slot 3: num_inference_steps (INT, default 25)
  slot 4: guidance (FLOAT, default 40.0)
  slot 5: true_gs (FLOAT, default 3.0)
  slot 6: seed (INT, default 20)
  slot 7: target_image (IMAGE, optional)
  slot 8: target_mask (MASK, optional)
  → IMAGE
```

## 陷阱

1. **视觉分析不可靠**：截图 OCR 可能误读参数值（实际 denoise=0.25 被读成 0.65）。必须用 `app.graph._nodes` 提取 widget 值确认。
2. **Qwen-Image 是 t2i 不是 img2img**——修复场景用 ICCustom。
3. **节点名含特殊字符**（如 `Image Comparer (rgthree)`），必须原样保留。
4. **ICCustom Sampler 的 ref_image 是 slot 1，pipeline 是 slot 0**——连线注意槽位。
5. **RH 导出的是 editor format**，不是 API format。导入时 RH 自动转换。
6. **导入后节点报红**（class_type not found）→ 该自定义节点未在 RH 云端部署，换方案。
7. **RH 节点 type 不是 Python class 名。** 必须用插件 `__init__.py` 中 `NODE_CLASS_MAPPINGS` 的 key。例如 `RH_ICCustom_Loader`（class）→ `"RunningHub ICCustom Loader"`（type）。
8. **Windows 下 write_file 写大 JSON 可能静默失败。** 文件 0 字节时改用 `terminal python3` 写。
9. **截图视觉分析会幻觉参数值。** 用 `app.graph._nodes[].widgets` 编程提取。

## 生成工作流 JSON

从已验证的完整模板生成变体时：

1. **每个节点必须有完整的 `inputs`/`outputs` 端口定义。** 克隆节点用 `copy.deepcopy()` 保持端口完整。缺端口 = UI 不显示连线。
2. **`links` 数组必须与节点端口 link 引用同步。** 生成后跑 sync：遍历 links 数组，设置 `source.outputs[slot].links` 和 `target.inputs[slot].link`。
3. **校验三件事。** (a) link 的 from/to 节点存在，(b) slot 索引不越界，(c) 端口 link 引用与 links 数组一致。
4. **模板策略。** 用 `copy.deepcopy()` 克隆用户验证过的节点 → 只改 `widgets_values`/`id`/`pos` → 增删节点用集合操作 → sync → validate。
5. **工作流三件套必须齐全。** GetNode + SetNode + LoadImage，每个 RH 工作流缺一不可。
6. **SetNode 可不连接任何东西（输出 link 为空），但必须存在。**

## SeedVR2

详见 `references/seedvr2-reference.md`。

两个版本共存于 RH：
- **Fork 版（v1.5.x, lihaoyun6）**：一体 `SeedVR2` + `SeedVR2BlockSwap` + 可选 `SeedVR2ExtraArgs`
- **主线版（v2.5.x, numz）**：模块化 `SeedVR2VideoUpscaler` + `SeedVR2LoadDiTModel` + `SeedVR2LoadVAEModel`

v2.5.x 关键新增：`color_correction` (lab/wavelet/hsv/adain/none) 修正扩散超分的色彩偏移。

DiT 模型选择：`7b_sharp_fp8_mixed` > `7b_fp8_mixed` > `3b_fp8`。`attention_mode` 固定 `sdpa`（RH 唯一确定兼容）。

### 竖线故障

单图出现竖线，优先级排查：
1. **BlockSwap**：`blocks_to_swap=0` 关闭，CPU↔GPU 精度漂移是最常见原因
2. **宽度未对齐 64**：DiT 内部 patch 要求。强制输入宽为 64 倍数
3. **fp8 量化**：列向舍入累积。换 fp16 模型
