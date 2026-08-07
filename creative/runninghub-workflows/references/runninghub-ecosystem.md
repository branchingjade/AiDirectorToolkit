# RunningHub 生态详情

补充 SKILL.md，记录 HM-RunningHub 仓库分类、节点名称清单、ICCustom 完整接口。

## HM-RunningHub 全部 34 个仓库

GitHub: https://github.com/HM-RunningHub

### 图像生成/编辑

| 仓库 | ⭐ | 底层模型 | 用途 | 节点类 |
|------|:--:|------|------|------|
| Qwen-Image | 92 | 通义万相 | 文生图，24G可跑完整版 | `RH_QwenImageGenerator`, `RH_QwenImagePromptEnhancer` |
| QwenImageI2L | 80 | Qwen-Image i2L | 图生LoRA，提取个性化权重 | - |
| ZImageI2L | 64 | 通义 Z-Image | 同上替代方案 | `RunningHub_ZImageI2L_Loader`, `...LoraGenerator`, `...Saver` |
| OminiControl | 142 | FLUX+Control | 主体驱动生成，物品乾坤大挪移 | - |
| ICCustom | 36 | TencentARC | 图像定制/风格化，img2img修复 | `RH_ICCustom_Loader`, `RH_ICCustom_Sampler` |
| SeedXPro | 64 | Seed-X-PPO-7B | 种子驱动图像编辑 | - |
| UNO | 55 | UNO | 图像生成 | - |
| USO | 54 | 字节 USO | 主体驱动生成 | - |
| Step1XEdit | 25 | Step1X | 图像编辑 | - |
| ACE-Step | 12 | ACE-Step 1.5 | 加速图像生成 | - |

### 视频生成

| 仓库 | ⭐ | 底层模型 |
|------|:--:|------|
| DreamID-V | 208 | 字节 DreamID-V |
| FramePack | 195 | lllyasviel FramePack |
| Ovi | 47 | 视频+音频联合生成 |
| Univideo | 37 | KlingTeam UniVideo |
| VideoAsPrompt | 21 | 视频作提示词 |
| Void | 18 | Netflix void-model |
| WanVideoWrapper | 1 | Wan 视频 |

### 音频/语音

| 仓库 | ⭐ | 底层模型 |
|------|:--:|------|
| VoxCPM | 76 | VoxCPM 语音合成 |
| FlashTalk | 31 | SoulX FlashTalk |
| SoulX-Singer | 17 | AI歌声合成 |
| DMOSpeech2 | 12 | 语音合成 |

### 多模态/其他

DreamOmni2(80⭐), FlashHead(38⭐), MOVA(22⭐), Dreamid-Omni(11⭐), mammothmoda(7⭐), Helios(4⭐), OneReward(13⭐)

### 基础设施

APICall(284⭐), LLM_API(127⭐), OpenAPI(106⭐), OpenClaw_RH_Skills(110⭐), RH_CLI(9⭐), RH_CozeSDK(16⭐)

## 从"修复图片"工作流提取的已知节点

### 标准 ComfyUI
`LoadImage`, `CLIPTextEncode`, `CheckpointLoaderSimple`, `SaveImage`, `ImageScaleToTotalPixels`

### 社区插件
- Impact Pack: `PixelKSampleUpscalerProvider`, `IterativeImageUpscale`
- rgthree: `Image Comparer (rgthree)`
- Easy Use: `easy cleanGpuUsed`
- LayerUtility: `LayerUtility: ImageScaleByAspectRatio V2`
- WAS Suite: `Upscale Model Loader`
- KJNodes: `GetNode`, `SetNode`

### RH 专用
- SeedVR2: `SeedVR2`, `SeedVR2BlockSwap`
- `ModelSamplingAuraFlow`
- `StringToInt`

## ICCustom 完整接口

源文件：`HM-RunningHub/ComfyUI_RH_ICCustom/rh_iccustom_nodes.py`

```python
class RH_ICCustom_Loader:
    INPUT_TYPES: {"required": {}}  # 无参数，自动下载模型
    RETURN_TYPES: ("RHICCustomPipeline",)

class RH_ICCustom_Sampler:
    INPUT_TYPES:
        required:
            pipeline: RHICCustomPipeline     # slot 0, link
            ref_image: IMAGE                 # slot 1, link (img2img输入)
            prompt: STRING                   # slot 2, widget
            num_inference_steps: INT (25)    # slot 3, widget
            guidance: FLOAT (40.0)           # slot 4, widget
            true_gs: FLOAT (3.0)             # slot 5, widget
            seed: INT (20)                   # slot 6, widget
        optional:
            target_image: IMAGE              # slot 7, optional link
            target_mask: MASK                # slot 8, optional link
    RETURN_TYPES: ("IMAGE",)
```

## 工作流 JSON 连线格式

```json
[link_id, from_node, from_slot, to_node, to_slot, type_string]
```
例如：`[533, 292, 0, 309, 0, "IMAGE"]` = 节点292输出0 → 节点309输入0，类型IMAGE。

## 视觉分析陷阱案例

截图 OCR 误读 `PixelKSampleUpscalerProvider` 参数：
- 实际 denoise=0.25，误读为 0.65
- 实际 steps=3，误读为 8
- 实际 CFG=1，误读为 7
- 实际 `Image Comparer`（并排对比），误读为 `Image Composite`（混合）

**结论：永远用代码提取 widget 值，不要依赖截图视觉分析。**
