# HM-RunningHub 模型节点目录

来自 https://github.com/HM-Runninghub 的 34 个仓库。每个仓库封装一个开源 AI 模型为 ComfyUI 节点。

## 图像处理（与修复/放大相关）

| 节点类型 | 仓库 | ⭐ | 输入 | 输出 |
|---------|------|:--:|------|------|
| `RH_ICCustom_Loader` | ComfyUI_RH_ICCustom | 36 | pipeline→ | `RHICCustomPipeline` |
| `RH_ICCustom_Sampler` | ComfyUI_RH_ICCustom | 36 | pipeline, ref_image(IMAGE), prompt, steps, guidance, true_gs, seed | IMAGE |
| `RH_QwenImageGenerator` | ComfyUI_RH_Qwen-Image | 92 | pipeline, prompt, width, height, steps, cfg, seed | IMAGE |
| `RH_QwenImagePromptEnhancer` | ComfyUI_RH_Qwen-Image | 92 | prompt | enhanced_prompt |
| `RunningHub_ZImageI2L_Loader` | ComfyUI_RH_ZImageI2L | 64 | - | `RH_ZImageI2LPipeline` |
| `RunningHub_ZImageI2L_LoraGenerator` | ComfyUI_RH_ZImageI2L | 64 | pipeline, training_images, seed | lora_name, lora_path |

## 视频生成

| 节点类型 | 仓库 | ⭐ |
|---------|------|:--:|
| DreamID-V 相关 | ComfyUI_RH_DreamID-V | 208 |
| FramePack 相关 | ComfyUI_RH_FramePack | 195 |
| Ovi 相关 | ComfyUI_RH_Ovi | 47 |
| UniVideo 相关 | ComfyUI_RH_Univideo | 37 |
| Void 相关 | ComfyUI_RH_Void | 18 |

## 音频/语音

| 节点类型 | 仓库 | ⭐ |
|---------|------|:--:|
| VoxCPM 相关 | ComfyUI_RH_VoxCPM | 76 |
| FlashTalk 相关 | ComfyUI_RH_FlashTalk | 31 |
| SoulX-Singer 相关 | ComfyUI_RH_SoulX-Singer | 17 |
| DMOSpeech2 相关 | ComfyUI_RH_DMOSpeech2 | 12 |

## 其他

所有节点 CATEGORY 前缀为 `RunningHub/` 或 `Runninghub/`。

### ICCustom Sampler 参数
- `ref_image` (IMAGE, required) - 参考图输入，这是 img2img 的关键
- `prompt` (STRING, default "") - 可选提示词
- `num_inference_steps` (INT, default 25)
- `guidance` (FLOAT, default 40.0)
- `true_gs` (FLOAT, default 3.0)
- `seed` (INT, default 20)

### ICCustom Loader
- 无输入参数，自动下载模型

### Qwen-Image Generator 参数
- pipeline (QWEN_PIPELINE)
- prompt (STRING, multiline)
- width/height (INT, 512-2048, step 64)
- num_inference_steps (INT, default 20)
- true_cfg_scale (FLOAT, default 4.0)
- seed (INT)
- aspect_ratio (COMBO: custom/1:1/16:9/9:16/4:3/3:4)

注意：Qwen-Image 是纯 t2i，无图输入，不适合图像修复场景。
