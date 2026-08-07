# HM-RunningHub 仓库完整清单

34 个仓库，来源：https://github.com/HM-RunningHub，最后更新：2026-06-30。

## 图像生成/编辑

| 仓库 | ⭐ | 模型 | 用途 |
|------|:--:|------|------|
| ComfyUI_RH_Qwen-Image | 92 | 通义万相 Qwen-Image | 文生图，24GB 可跑完整版 |
| ComfyUI_RH_QwenImageI2L | 80 | Qwen-Image i2L | 图生 LoRA |
| ComfyUI_RH_ZImageI2L | 64 | 通义 Z-Image Turbo | 图生 LoRA（替代方案） |
| ComfyUI_RH_OminiControl | 142 | FLUX + OminiControl | 主体驱动生成/空间控制 |
| ComfyUI_RH_SeedXPro | 64 | Seed-X-PPO-7B | 种子驱动编辑 |
| ComfyUI_RH_UNO | 55 | UNO | 图像生成 |
| ComfyUI_RH_USO | 54 | 字节 USO | 主体驱动生成 |
| ComfyUI_RH_ICCustom | 36 | TencentARC IC-Custom | 图像定制/风格化 |
| ComfyUI_RH_Step1XEdit | 25 | Step1X | 图像编辑 |
| ComfyUI_RH_ACE-Step | 12 | ACE-Step 1.5 | 加速生成 |

## 视频生成

| 仓库 | ⭐ | 模型 |
|------|:--:|------|
| ComfyUI_RH_DreamID-V | 208 | 字节 DreamID-V |
| ComfyUI_RH_FramePack | 195 | lllyasviel FramePack |
| ComfyUI_RH_Ovi | 47 | 视频+音频联合 |
| ComfyUI_RH_Univideo | 37 | KlingTeam UniVideo |
| ComfyUI_RH_VideoAsPrompt | 21 | 视频作 prompt |
| ComfyUI_RH_Void | 18 | Netflix void-model |
| ComfyUI-WanVideoWrapper | 1 | Wan Video 封装 |

## 音频/语音

| 仓库 | ⭐ | 模型 |
|------|:--:|------|
| ComfyUI_RH_VoxCPM | 76 | VoxCPM 语音合成 |
| ComfyUI_RH_FlashTalk | 31 | SoulX FlashTalk |
| ComfyUI_RH_SoulX-Singer | 17 | AI 歌声合成 |
| ComfyUI_RH_DMOSpeech2 | 12 | DMOSpeech2 |

## 多模态/其他

| 仓库 | ⭐ | 模型 |
|------|:--:|------|
| ComfyUI_RH_DreamOmni2 | 80 | dvlab DreamOmni2 |
| ComfyUI_RH_FlashHead | 38 | SoulX FlashHead |
| ComfyUI_RH_MOVA | 22 | OpenMOSS MOVA |
| ComfyUI_RH_Dreamid-Omni | 11 | DreamID-Omni |
| ComfyUI_RH_mammothmoda | 7 | 字节 MammothModa2 |
| ComfyUI_RH_Helios | 4 | 北大 Helios |
| ComfyUI_RH_OneReward | 13 | — |

## 基础设施

| 仓库 | ⭐ | 用途 |
|------|:--:|------|
| ComfyUI_RH_APICall | 284 | 本机 ComfyUI 调用 RH 工作流 |
| ComfyUI_RH_LLM_API | 127 | ComfyUI 内嵌 OpenAI API |
| ComfyUI_RH_OpenAPI | 106 | RH 标准 API |
| OpenClaw_RH_Skills | 110 | OpenClaw 技能包 |
| RH_CozeSDK | 16 | Coze 平台集成 |
| RH_CLI | 9 | 命令行工具 |

## 仓库结构模式

每个 ComfyUI_RH_* 仓库统一结构：
```
├── nodes.py          ← 节点定义（INPUT_TYPES, RETURN_TYPES, CATEGORY）
├── __init__.py        ← 插件注册
├── rh_config.json     ← RH 平台特有配置
├── requirements.txt
├── LICENSE
├── README.md
└── workflows/         ← 示例工作流
```

CATEGORY 命名规则：`"RunningHub/<ModelName>"`，如 `"RunningHub/ZImageI2L"`。
