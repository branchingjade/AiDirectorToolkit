# SeedVR2 版本对比

## 两个分支

| | Fork 版（lihaoyun6） | 原版（numz） |
|---|---|---|
| 版本 | ~v1.5.0 / v2.0.0-modular | v2.5.x（最新 v2.5.23，git tags） |
| GitHub | `lihaoyun6/ComfyUI-SeedVR2_VideoUpscaler` (nightly) | `numz/ComfyUI-SeedVR2_VideoUpscaler` (main) |
| Commit | `f4de6e2` | `4490bd1` |
| 最后更新 | 10 months ago | 6 months ago |
| 节点 | `SeedVR2` + `SeedVR2BlockSwap` + `SeedVR2ExtraArgs` + `SeedVR2GGUF` | `SeedVR2VideoUpscaler` + `SeedVR2LoadDiTModel` + `SeedVR2LoadVAEModel` + `SeedVR2BlockSwap` + `SeedVR2ExtraArgs` + `SeedVR2TorchCompileSettings` |
| 架构 | 一体化加载 | 模块化：DiT 和 VAE 分开加载 |
| 星数 | 169 | 2.6k |

## 参数差异（原版新增）

| 参数 | 默认 | 对单图修复的意义 |
|------|:--:|------|
| **color_correction** | `lab` | 🔴 最重要——扩散超分导致色彩偏移，此参数将输出色彩拉回原图。可选：lab / wavelet / wavelet_adaptive / hsv / adain / none |
| max_resolution | 0 | 极端宽高比的显存保护，单图通常用不到 |
| uniform_batch_size | false | 视频最后批次填充，单图无用 |
| temporal_overlap | 0 | 批次间帧重叠，单图无用 |
| prepend_frames | 0 | 视频开头减伪影，单图无用 |

## 对 RunningHub 用户的建议

- RH 节点库中 `SeedVR2VideoUpscaler` 需确认是否同时部署了 `SeedVR2LoadDiTModel` 和 `SeedVR2LoadVAEModel`
- 如果 RH 封装了模块化（单节点可用）→ 换上去试 `color_correction`
- 如果 RH 没封装（需要额外加载节点）→ 需完整替换 SeedVR2 路径
- `color_correction=lab` 最可能提升单图修复效果，其他新增参数对单图无用

## 共享参数差异

| 参数 | Fork 版 | 原版 v2.5.x |
|------|---------|------------|
| seed 默认 | 100 | 42 |
| 分辨率范围 | 16-4320 | 16-16384 |
| step | 16 | 2 |
| batch_size tooltip | 4n+1 | 4n+1，明确建议匹配镜头长度 |
