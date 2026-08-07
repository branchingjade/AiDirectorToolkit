# SeedVR2 Parameter Reference

SeedVR2 is a video diffusion upscaler from ByteDance, wrapped for ComfyUI.
Two major versions exist: the fork (`lihaoyun6`, v1.5.x) and the original
(`numz`, v2.5.x).

## Version Architecture

| | v1.5.x (fork) | v2.5.x (main) |
|---|---|---|
| Main node | `SeedVR2` (monolithic) | `SeedVR2VideoUpscaler` |
| Model loading | Built-in dropdown | `SeedVR2LoadDiTModel` + `SeedVR2LoadVAEModel` |
| BlockSwap | `SeedVR2BlockSwap` (separate) | Built into DiT loader |
| Extra args | `SeedVR2ExtraArgs` (optional) | All params first-class |
| TorchCompile | N/A | `SeedVR2TorchCompileSettings` |

## v1.5.x: SeedVR2 (fork — lihaoyun6, commit f4de6e2)

### Main node

| Parameter | Default | Range | Notes |
|-----------|:-------:|-------|-------|
| `images` | — | — | Input image/video batch |
| `model` | auto | dropdown | 3B/7B models |
| `seed` | 100 | 0–2³² | Diffusion noise seed |
| `new_resolution` | 1072 | 16–4320, step 16 | Output shortest edge; multiple of 16 required |
| `batch_size` | 5 | 1–2048, step 4 | Video-only; use 1 for single image |

### Implicit defaults (ExtraArgs, when not connected)

| Setting | Default |
|---------|:-------:|
| `tiled_vae` | true |
| `vae_tile_size` | 512 |
| `vae_tile_overlap` | 64 |
| `preserve_vram` | false |
| `cache_model` | false |
| `temporal_overlap` | 0 (single-image mode) |

### BlockSwap

| Parameter | Default | Range |
|-----------|:-------:|-------|
| `blocks_to_swap` | 0 | 0–36 (7B) / 0–32 (3B) |
| `use_non_blocking` | false | Async GPU↔CPU |
| `offload_io_components` | false | Also swap I/O embeddings |

## v2.5.x: SeedVR2VideoUpscaler (main — numz, up to v2.5.23)

### Main node

| Parameter | Default | Range | Notes |
|-----------|:-------:|-------|-------|
| `image` | — | — | Input (RGB or RGBA) |
| `dit` | — | — | From `SeedVR2LoadDiTModel` |
| `vae` | — | — | From `SeedVR2LoadVAEModel` |
| `seed` | 42 | 0–2³² | |
| `resolution` | 1080 | 16–16384, step 2 | Renamed; must be EVEN |
| `max_resolution` | 0 | 0–16384, step 2 | Cap any edge; 0 = no cap |
| `batch_size` | 5 | 1–16384, step 4 | 4n+1 pattern |

### NEW parameters (not in v1.5.x)

| Parameter | Default | Options | Purpose |
|-----------|:-------:|---------|---------|
| `color_correction` | lab | lab/wavelet/wavelet_adaptive/hsv/adain/none | Corrects diffusion color shift |
| `input_noise_scale` | 0.0 | 0.0–1.0 | Pre-encoding noise injection |
| `latent_noise_scale` | 0.0 | 0.0–1.0 | In-diffusion noise injection |
| `offload_device` | cpu | none/cpu/cuda:X | Intermediate tensor storage |
| `uniform_batch_size` | false | — | Video-only |
| `temporal_overlap` | 0 | 0–16 | Video-only |
| `prepend_frames` | 0 | 0–32 | Video-only |
| `enable_debug` | false | — | Console logging |

### DiT Loader

| Parameter | Default | Purpose |
|-----------|:-------:|---------|
| `model` | `3b_fp8` | DiT selection |
| `device` | cuda:0 | Inference device |
| `blocks_to_swap` | 0 | 0 = off |
| `swap_io_components` | false | |
| `offload_device` | none | Swap target |
| `cache_model` | false | Cross-run cache |
| `attention_mode` | sdpa | sdpa/flash_attn/xformers |

### VAE Loader

| Parameter | Default | Purpose |
|-----------|:-------:|---------|
| `model` | `ema_vae_fp16` | Only one VAE shipped |
| `device` | cuda:0 | |
| `encode_tiled` | false | |
| `encode_tile_size` | 1024 | |
| `encode_tile_overlap` | 128 | |
| `decode_tiled` | false | |
| `decode_tile_size` | 1024 | |
| `decode_tile_overlap` | 128 | |

## DiT Model Registry

### 7B (recommended for quality)

| File | Precision | VRAM ~ |
|------|-----------|:------:|
| `seedvr2_ema_7b_sharp_fp8_mixed_block35_fp16` | fp8 mixed | 12 GB |
| `seedvr2_ema_7b_sharp_fp16` | fp16 | 20 GB |
| `seedvr2_ema_7b_fp8_mixed_block35_fp16` | fp8 mixed | 12 GB |
| `seedvr2_ema_7b_fp16` | fp16 | 20 GB |

### 3B (lighter)

| File | Precision | VRAM ~ |
|------|-----------|:------:|
| `seedvr2_ema_3b_fp8_e4m3fn` (default) | fp8 | 6 GB |
| `seedvr2_ema_3b_fp16` | fp16 | 10 GB |

"Sharp" variants optimize noise schedules for high-frequency retention —
better for restoring degraded images. "Mixed block35 fp16" keeps the first
35 transformer blocks at fp16, rest at fp8 — near-fp16 quality at fp8 VRAM.

## Key insight for single-image use

The critical upgrade from v1.5 to v2.5 is `color_correction`. SeedVR2
diffusion unavoidably shifts colors; v1.5 cannot fix this, v2.5 can.
All video-specific parameters are irrelevant for single-image restoration.

## Sources

- Fork: https://github.com/lihaoyun6/ComfyUI-SeedVR2_VideoUpscaler
- Main: https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler
- Original: https://github.com/ByteDance-Seed/SeedVR
