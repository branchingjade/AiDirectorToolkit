---
name: runninghub
description: RunningHub 云 ComfyUI 平台 + 导演台 HyperFrames——写工作流、分析节点、HM-RunningHub 模型生态、3D分镜工具、高级假人。触发词：RunningHub、RH、runninghub.cn、RH工作流、RH节点、在RH上搭工作流、RH导演台、HyperFrames。
version: 1.0.0
---

# RunningHub

RunningHub (runninghub.cn / runninghub.ai) 是一个云端 ComfyUI 平台，提供 GPU 分级计算（Lite/Standard/Plus）、工作流市场、以及 25+ 官方模型封装插件。

## 节点生态

```
标准 ComfyUI  ───→ LoadImage, KSampler, CLIPTextEncode, CheckpointLoaderSimple, ...
社区插件      ───→ Impact Pack, rgthree, LayerUtility, easy-use, ...
RH 平台特有   ───→ GetNode, SetNode, ModelSamplingAuraFlow, SeedVR2, SeedVR2BlockSwap
HM-RunningHub ───→ 25+ 模型封装（Qwen-Image, ZImageI2L, DreamID-V, FramePack ...）
```

- 用户提到 RunningHub、RH、runninghub.cn
- 需要在 RH 平台上写/改/分析工作流
- 询问 RH 有哪些可用模型和节点
- 需要从 RH 工作流页面提取节点数据
- 对比 RH 与本地 ComfyUI 的差异

## 参考文件

- `references/hm-runninghub-repos.md` — HM-RunningHub 全部 34 个仓库清单及功能分类
- `references/rh-api-services.md` — RH API 市场（模型API/AI应用API），非工作流、直接 HTTP 调用的服务封装（如火山字幕擦除）

## RH 平台特有节点

| 节点 | 作用 |
|------|------|
| `GetNode` | **输入图片的唯一入口**。工作流必须用它引用用户上传的图片，不能用标准 `LoadImage`。标题 `Get_<名称>`，输出 `IMAGE`。 |
| `SetNode` | 中间路由/直通节点。输入 `IMAGE` → 输出 `IMAGE`。 |
| `ModelSamplingAuraFlow` | RH 封装的 AuraFlow 采样。输入 `model`、`shift` → 输出 `MODEL`。 |
| `ImageScaleToTotalPixels` | 按目标像素数缩放 |

## RH 导演台（HyperFrames）

RH 还有一个独立的 **导演台（Director's Desk / HyperFrames）**——3D 分镜/视频创作工具，与 ComfyUI 工作流完全分离：

- URL: `https://rhtv.runninghub.cn/projects/canvas/<id>`
- 功能：3D 场景编辑、分镜设计、打光、镜头机位
- 内置 **高级假人**（红/蓝 3D 可动人形模型），可直接拖入场景摆姿势
- 左侧功能栏：资产 / 工作流 / 历史 / 导演台 / 评论 / 剪辑
- 资产库含：素材库（视频/全景/场景/服装/宠物）、虚拟人像库、我的资产、团队资产
- **无公开 API**——无法通过 MCP 或代码操控，只能手动在浏览器中操作

导演台示例工程可见"保卫处"等预制场景，含室内场景+可动假人。适合快速搭建带人物的分镜预览，但不适合需要程序化控制的管线。

## HM-RunningHub 模型封装（34 个仓库）

官方 GitHub：https://github.com/HM-RunningHub

每个仓库结构统一：`nodes.py` + `__init__.py` + `rh_config.json` + `workflows/`。

### 图像生成/编辑（与修复/放大最相关）

| 仓库 | ⭐ | 模型 | 用途 |
|------|:--:|------|------|
| Qwen-Image | 92 | 通义万相 | 文生图，24GB 可跑完整版 |
| QwenImageI2L | 80 | Qwen-Image i2L | 图生 LoRA，从参考图提取个性化权重 |
| ZImageI2L | 64 | 通义 Z-Image | 同上，替代方案 |
| OminiControl | 142 | FLUX+Control | 主体驱动生成，空间控制 |
| ICCustom | 36 | TencentARC | 图像定制/风格化（对修复场景有潜力） |
| SeedXPro | 64 | Seed-X-PPO-7B | 种子驱动编辑 |
| UNO / USO | 55/54 | UNO/字节 | 主体保持生成 |
| Step1XEdit | 25 | Step1X | 图像编辑 |
| ACE-Step | 12 | ACE-Step 1.5 | 加速生成 |

### 视频生成

DreamID-V (208⭐), FramePack (195⭐), Ovi (47⭐), Univideo (37⭐),
VideoAsPrompt (21⭐), Void (18⭐)

### 音频/语音

VoxCPM (76⭐), FlashTalk (31⭐), SoulX-Singer (17⭐), DMOSpeech2 (12⭐)

### 基础设施

APICall (284⭐), LLM_API (127⭐), OpenAPI (106⭐), RH_CLI (9⭐)

## 写 RH 工作流

### 规则

1. **输入图片必须用 `GetNode`**，不能用标准 `LoadImage`
2. **节点名称**——标准 ComfyUI 和社区节点保持原名，RH 封装节点用 RH 命名
3. **工作流 JSON** 为标准 ComfyUI API 格式（字符串键 ID + `class_type` + `inputs`）
4. **GPU 分级**：Lite/Standard 适合轻量工作流，Plus 适合 SeedVR2、DreamID-V 等大模型

### 分析现有工作流

用 Kimi WebBridge 从 RH 页面的 ComfyUI iframe 提取完整节点数据：

```js
// 提取节点类型+标题+参数值+连线
const app = document.querySelector('iframe').contentWindow.app;
const nodes = Object.values(app.graph._nodes);
nodes.map(n => ({
  id: n.id, type: n.type, title: n.title,
  widgets: n.widgets ? Object.fromEntries(n.widgets.map(w => [w.name, w.value])) : {},
  inputs: n.inputs ? Object.fromEntries(n.inputs.map(i =>
    [i.name, i.link ? {link: i.link} : (i.widget?.value ?? i.value ?? '?')]
  )) : {}
}))
```

详见 kimi-webbridge skill 的 `references/runninghub-workflow-extraction.md`。

## 已知工作流模式

### 图像修复双路径（已分析的工作流 ID: 2071458564530597889）

```
GetNode ──→ LoadImage ──→ ScaleToPixels ──→ IterativeImageUpscale ──→ SaveImage
              │              (1MP)              │ (×1.5, tile 512)        │
              │    PixelKSampleUpscalerProvider                          ├── ImageComparer
              │    (denoise 0.25, steps 3, CFG 1)                       │   (A/B 对比)
              │    ckpt: z-image-turbo-bf16-aio                          │
              │    upscale: RealESRGAN_x4plus                             │
              │                                                           │
GetNode ──→ SetNode ──→ ScaleByAspectRatio ──→ SeedVR2 ──→ SaveImage ───┘
                           (shortest 1024,        (fp8, 2048 res)
                            lanczos, to 2160)
```

关键参数：迭代放大 denoise=0.25, CFG=1（空 prompt），极其保守的纹理修复。
SeedVR2 路径 target 2048px。两路输出独立保存并并排对比。

## 陷阱

### 视觉分析会误读参数
不要依赖截图+vision_analyze 读 ComfyUI 画布上的参数数字。实测视觉模型将 `denoise: 0.25` 误读为 `0.65`，`steps: 3` 误读为 `8`。参数值必须通过代码提取（`app.graph._nodes[].widgets[]`）。

### 导演台无 API
RH 导演台是独立 3D 创作平台，**没有公开 API**，不能通过代码操控。如需程序化控制可动 3D 角色，用 Blender Rigify（见 blender-mcp skill）替代。

### RH 节点名与本地不同
在 RH 上写工作流时，`GetNode`/`SetNode`/`ModelSamplingAuraFlow` 等 RH 特有节点在本地 ComfyUI 不存在。不能直接拿本地 JSON 导入 RH——需要替换输入节点为 `GetNode`。

### HM-RunningHub 仓库更新频率
大多数模型封装仓库最后更新在半年前到一年前。Qwen-Image 和 FramePack 是近期较活跃的。不是所有模型都保持最新版本。
