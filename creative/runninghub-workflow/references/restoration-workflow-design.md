# 图像修复工作流设计原理

基于已验证有效的"修复图片"工作流（RunningHub ID 2071458564530597889）深度分析。

## 工作流架构

双路径独立输出 + 并排对比：

```
GetNode("原图") → ScaleToPixels(1MP,nearest) → RealESRGAN×4 → PixelKSampleUpscalerProvider → IterativeUpscale(×1.5) → Save
                                    ↑
                    Checkpoint: z-image-turbo-bf16-aio
                    CLIP: 空 / CFG:1 / denoise:0.25 / steps:3 / sgm_uniform

GetNode("原图") → ScaleToPixels → SeedVR2(7B,fp8,2048) → ScaleByAspectRatio(2160,lanczos) → Save
                                    ↑
                    BlockSwap: blocks=16, non_blocking

→ Image Comparer 并排对比，用户选优。不合成。
```

## 核心机制：CFG=1 + 空 prompt

不是"根据 prompt 生成细节"，而是"把偏离自然图像分布的像素拉回来"。

多轮编辑损伤的三类问题：
- **纹理蜡化**：VAE 编解码累积 → SD 无条件先验投影回自然流形
- **压缩噪声**：JPEG DCT 块效应 → 扩散去噪拒绝非自然模式
- **结构保持**：tile 512 + denoise 0.25 → 局部修正不越界

CFG=1 时模型退化为**无条件扩散**，只判断"这像素像不像训练集里的自然图像"。不像 → 去噪修正；像 → 保留。

## 为什么 denoise=0.25 是最优的

| denoise | CFG=1 时的行为 |
|:--:|------|
| 0.15 | 几乎不动，噪声残存 |
| 0.25 | 保留 75% 结构，刚好抹平伪影 |
| 0.40 | 开始随机填充（无 prompt 引导方向） |
| 0.65 | 大量随机填充，引入新人工痕迹 |

## Turbo checkpoint + steps=3

Z-Image Turbo 是蒸馏模型，1-4 步收敛。3 步完成 denoise=0.25 的去噪。多步无益——噪声调度被蒸馏到前几步。

## RealESRGAN_x4plus 的位置

不作为最终输出，而是 PixelKSampleUpscalerProvider 的 `upscale_model_opt`——**预放大引擎**。

GAN 提供高频起点（哪怕是假的高频），SD 扩散修正 GAN 伪影（塑料感、振铃、过度锐化）。两者互补：
- 单走 GAN → 假纹理和噪声无人修正
- 单走 SD 扩散 → 从模糊插值开始，0.25 去噪量不够

## SeedVR2 路径的局限性

7B 扩散视频超分模型，用在单图上属于跨界。优势是 7B 容量带来丰富纹理先验。劣势是无 ControlNet 锁结构、无 tile 保局部一致性。对结构复杂的图可能过度平滑。

**SeedVR2 v2.5.x（numz 原版）新增 `color_correction` 参数**：解决扩散超分的色彩偏移问题，可能提升效果。见 `seedvr2-versions.md`。

## 适用场景

- 多轮 AI 编辑后的劣化修复（VAE 编解码 → 纹理退化、JPEG 压缩 → 噪声累积）
- 对"偏离自然分布"的损伤有效
- 对原图就糊（对焦不准、低分辨率）效果有限

## 不适用场景

- 需要大幅超分（1.5× 太小，需改 upscale_factor）
- 需要保留原图所有细节的档案修复（扩散模型有随机性）
- 人脸特写修复（需额外接 CodeFormer/GFPGAN）
