# SeedVR2 完整参数参考

## 版本对比

| | Fork 版 (v1.5.x) | 主线版 (v2.5.x) |
|---|---|---|
| 节点 | `SeedVR2` (一体化) | `SeedVR2VideoUpscaler` + 加载器 |
| BlockSwap | 独立节点 `SeedVR2BlockSwap` | DiT 加载器内置参数 |
| ExtraArgs | 独立节点 `SeedVR2ExtraArgs` | 各参数分散到各加载器 |
| 新增功能 | — | `color_correction`, `input_noise_scale`, `latent_noise_scale`, `max_resolution`, `uniform_batch_size`, `temporal_overlap`, `prepend_frames` |

## Fork 版 SeedVR2 参数

### SeedVR2 节点

| 参数 | 类型 | 默认 | 范围 | 说明 |
|------|------|------|------|------|
| images | IMAGE | — | — | 输入图像/帧 |
| model | COMBO | auto | — | 模型下拉，自动下载 |
| seed | INT | 100 | 0–2³² | 随机种子 |
| control_after_generate | — | fixed | fixed/randomize | 种子的复用策略 |
| new_resolution | INT | 1072 | 16–4320, step=16 | 输出短边像素 |
| batch_size | INT | 5 | 1–2048, step=4 | 帧批大小（推荐 4n+1） |

### SeedVR2BlockSwap

| 参数 | 默认 | 说明 |
|------|------|------|
| blocks_to_swap | 0 | 前 N 层 Transformer 在 GPU/CPU 间交换 |
| use_non_blocking | true | 异步传输（几乎必须开） |
| offload_io_components | false | IO 组件（VAE/文本编码器）参与交换 |

### SeedVR2ExtraArgs（硬编码默认值，不连时使用）

| 参数 | 默认 | 说明 |
|------|------|------|
| tiled_vae | true | VAE 分块编解码 |
| vae_tile_size | 512 | 分块尺寸 |
| vae_tile_overlap | 64 | 分块重叠 |
| preserve_vram | false | 极端显存保护 |
| cache_model | false | 跨运行缓存模型 |
| enable_debug | false | 调试日志 |
| temporal_overlap | 0 | 时间帧重叠（0=单帧模式） |

## 主线版 SeedVR2VideoUpscaler (v2.5.x)

### 主节点参数

| 参数 | 默认 | 范围 | 说明 |
|------|------|------|------|
| image | — | — | 输入图像/帧 batch |
| dit | — | — | 接 SeedVR2LoadDiTModel |
| vae | — | — | 接 SeedVR2LoadVAEModel |
| seed | 42 | 0–2³² | 无 fixed/randomize，手动设 |
| resolution | 1080 | 16–16384, step=2 | 输出短边，偶数 |
| max_resolution | 0 | 0–16384 | 长边上限（0=不限制） |
| batch_size | 5 | 1–16384, step=4 | 单图设 1 |
| **color_correction** | lab | lab/wavelet/wavelet_adaptive/hsv/adain/none | 🔴 色彩修正 |
| input_noise_scale | 0.0 | 0.0–1.0 | 编码前加噪 |
| latent_noise_scale | 0.0 | 0.0–1.0 | 扩散中加噪 |
| offload_device | cpu | none/cpu/cuda:X | 中间张量存放 |
| enable_debug | false | — | 调试日志 |
| uniform_batch_size | false | — | 视频：补齐末批 |
| temporal_overlap | 0 | 0–16 | 视频：帧重叠 |
| prepend_frames | 0 | 0–32 | 视频：预置帧 |

### SeedVR2LoadDiTModel

| 参数 | 默认 | 说明 |
|------|------|------|
| model | auto | DiT 模型下拉 |
| device | cuda:0 | 推理设备 |
| blocks_to_swap | 0 | 同旧版，0=关闭 |
| swap_io_components | false | 同旧版 offload_io_components |
| attention_mode | sdpa | 🔴 选 sdpa（唯一确定兼容 RH） |
| cache_model | false | 跨运行缓存 |

### SeedVR2LoadVAEModel

| 参数 | 默认 | 说明 |
|------|------|------|
| model | auto | VAE 模型下拉 |
| device | cuda:0 | 推理设备 |
| encode_tiled | false | VAE 编码分块 |
| encode_tile_size | 1024 | 编码分块尺寸 |
| encode_tile_overlap | 128 | 编码分块重叠 |
| decode_tiled | false | VAE 解码分块 |
| decode_tile_size | 1024 | 解码分块尺寸 |
| decode_tile_overlap | 128 | 解码分块重叠 |

## DiT 模型选择

| 模型 | 精度 | 显存 | 推荐度 |
|------|------|:--:|:--:|
| seedvr2_ema_7b_sharp_fp8_mixed | fp8混合 | ~12G | 🥇 首选 |
| seedvr2_ema_7b_fp8_mixed | fp8混合 | ~12G | 🥈 备选 |
| seedvr2_ema_7b_fp16 | fp16 | ~20G | 🥉 高质量但吃显存 |
| seedvr2_ema_7b_sharp_fp16 | fp16 | ~20G | sharp+满精度 |
| seedvr2_ema_3b_fp8 | fp8 | ~6G | 轻量默认 |
| 各种 GGUF 量化 | Q4/Q8 | 3-7G | 省显存，丢质量 |

"sharp" = 高频偏向训练，纹理更锐利。"mixed" = 前 35 层 fp16 + 其余 fp8。

## 竖线故障排查

SeedVR2 单图推理出现可见竖线：

1. **BlockSwap 关闭**：`blocks_to_swap=0`。CPU↔GPU 传输精度漂移是主因。
2. **宽度对齐 64**：DiT 内部 patch 处理要求宽度是 64 的倍数。用 ImageScale 强制。
3. **VAE tiling 关闭**：`tiled_vae=false` 或 `encode_tiled=false, decode_tiled=false`。
4. **换 fp16 模型**：fp8 列向量化可能存在舍入偏差累积。
