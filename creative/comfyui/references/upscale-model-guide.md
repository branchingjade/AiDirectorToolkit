# Super-Resolution Model Guide — ComfyUI & Beyond

Comprehensive reference for choosing and chaining upscale models in ComfyUI workflows and adjacent tools. Covers 23+ open-source models, 8 closed-source tools, and 10+ ComfyUI nodes. Updated 2026-06-26.

---

## Quick-Reference Cheat Sheet

### Architecture 4-way

| Architecture | Speed | Quality | Blind Restore | VRAM | Best For |
|-------------|:-----:|:-------:|:------------:|:----:|----------|
| **GAN** (ESRGAN, Real-ESRGAN) | ⚡ Fast | Sharp, artifacts possible | ★★★★ | 2-4G | General, batch, video |
| **Transformer** (SwinIR, HAT) | 🐢 Slow | Highest PSNR | ★★ | 4-12G | Pixel-precision, denoise |
| **Diffusion** (SUPIR, DiffBIR) | 🐌 Very slow | Most photorealistic | ★★★★★ | 12-24G | Severe degradation, creative |
| **Light CNN** (SPAN) | ⚡ V.fast | Acceptable | ★★ | <1G | Real-time, mobile |

### Model Quick-Pick

| Scenario | 1st Choice | Fallback |
|----------|-----------|----------|
| Generic 4x upscale | `4x-UltraSharp.pth` (ESRGAN) | `4x_NMKD-Superscale.pth` |
| Real-world photos | Real-ESRGAN `x4plus` | DiffBIR |
| Anime / illustration | Real-ESRGAN `x4plus_anime_6B` | Real-CUGAN |
| Video (temporal) | Real-ESRGAN `anime-v3` / SeedVR2 | Topaz Video AI |
| Face close-ups | CodeFormer + ESRGAN | SUPIR |
| Severe degradation | DiffBIR | SUPIR |
| Speed-critical | SPAN | Real-ESRGAN-ncnn |
| Old film restoration | DiffBIR Stage1 only | StableSR |
| Creative high-ratio (8-16x) | Magnific AI (commercial) | — |

---

## Complete Model Directory

### GAN Family

| Model | Stars | Scale | Speed | VRAM | Blind | Key Strength | Key Weakness |
|-------|:-----:|:-----:|:-----:|:----:|:-----:|-------------|--------------|
| **Real-ESRGAN** | ★35.9k | 4x | ⚡1-3s | 2-4G | ★★★★ | Degradation pipeline; ncnn backend | Face plastic-look; ringing artifacts |
| **ESRGAN (base)** | — | 4x | ⚡ | 2-3G | ★ | RRDB block; perceptual loss | Bicubic-only training |
| **BSRGAN** | ★1.4k | 4x | ⚡ | 3-5G | ★★★★ | Shuffled degradation (broader) | Less stable artifacts |
| **SRGAN** | — | 4x | ⚡ | 2G | ★ | Pioneered perceptual SR | Heavy artifacts; outdated |

**Community ESRGAN models (OpenModelDB, 669+ entries):**

| Model | Arch | Scale | Best For | Notes |
|-------|------|:----:|----------|-------|
| `4x-UltraSharp` | ESRGAN | 4x | General | Sharpest, may over-sharpen |
| `4x_NMKD-Superscale` | ESRGAN | 4x | Games/photos | Balanced texture |
| `4x_foolhardy_Remacri` | ESRGAN | 4x | Photos | Rich detail, grain |
| `4x-AnimeSharp` | ESRGAN | 4x | Anime | Sharp lines |
| `StarSample V2.0 HQ` | HAT-L | 2x | Cartoon | HAT architecture, high precision |
| `Adore` | Real-CUGAN | 2x | Anime | Bilibili-optimized |

### Transformer Family

| Model | Stars | Scale | Speed | VRAM | Key Innovation | Weakness |
|-------|:-----:|:-----:|:-----:|:----:|---------------|----------|
| **SwinIR** | ★5.5k | 2-4x | 🐢3-5x ESRGAN speed | 4-8G | Swin Transformer + residual; multi-task unified | No blind restore; window boundaries |
| **HAT** | ★1.6k | 2-4x | 🐢≈SwinIR | 6-12G | 3-attention hybrid; activates more pixels | Large model slow; no blind restore |
| **Restormer** | ★2.6k | 2-4x | 🐢 | 4-8G | Linear-complexity Transformer; multi-task | Not SR-specialized |
| **DAT** | ★533 | 2-4x | 🐢 | 4-8G | Dual aggregation paths | Low community adoption |

### Diffusion Family

| Model | Stars | Venue | Scale | Speed | VRAM | Key Innovation | Weakness |
|-------|:-----:|:-----:|:-----:|:-----:|:----:|---------------|----------|
| **SUPIR** | ★5.6k | 2024 | Any | 🐌30-90s | 16-24G | SDXL+LLaVA text-guided; merged to ComfyUI core | Extreme VRAM; hallucinates detail |
| **DiffBIR** | ★4.1k | ECCV'24 | 4x | 🐌20-60s | 12-16G | 2-stage: SwinIR→SD prior | Speed; invents textures |
| **StableSR** | ★2.7k | IJCV'24 | 4x | 🐌≈DiffBIR | ~12G | Frozen SD + trainable encoder | SD style shift |
| **ResShift** | ★1.4k | NeurIPS'23 | 4x | 🐢15 steps | 8-12G | Residual shift diffusion; 15 steps vs 100+ | Less photorealism than SUPIR |
| **InvSR** | ★1.4k | CVPR'25 | 4x | 🐢→⚡ | 8-12G | Arbitrary-step diffusion inversion | Still maturing |
| **TSD-SR** | ★232 | CVPR'25 | 4x | ⚡1-step | 8-12G | One-step diffusion via distillation | Research-stage |
| **OSEDiff** | ★647 | NeurIPS'24 | 4x | ⚡1-step | 8-12G | One-step effective diffusion | Ecosystem immature |
| **DiT4SR** | ★252 | ICCV'25 | 4x | 🐢 | 12G+ | DiT replaces U-Net for SR | Flux-level VRAM needed |
| **AdcSR** | ★281 | CVPR'25 | 4x | 🐢 | 8-12G | GAN+diffusion hybrid | Experimental |

### Face Restoration Specialists

| Model | Stars | Key Feature | Best Use |
|-------|:-----:|-------------|----------|
| **GFPGAN** | ★37.5k | GAN + StyleGAN2 prior | Fast face fix, pip install |
| **CodeFormer** | ★18.0k | Codebook Lookup Transformer | Robust blind face restore, fidelity slider |
| **VQFR** | ★355 | VQGAN dictionary + parallel decoder | Texture quality, ECCV Oral |

### Lightweight / Specialized

| Model | Stars | Scale | Speed | VRAM | Best For |
|-------|:-----:|:-----:|:-----:|:----:|----------|
| **SPAN** | — | 2-4x | ⚡5-10x ESRGAN | <1G | Real-time, mobile |
| **Real-CUGAN** | — | 2-4x | ⚡ | 1-2G | Anime anti-aliasing |
| **Waifu2x** | ★28.2k | 2x | ⚡ | <0.5G | Legacy, ultra-low-spec |

### 2025 Cutting-Edge (Research, not production-ready)

| Model | Venue | Stars | Direction |
|-------|:----:|:-----:|-----------|
| **4KAgent** | NeurIPS'25 | ★810 | LLM Agent orchestrates multi-model pipeline |
| **DP2O-SR** | NeurIPS'25 | ★83 | Preference optimization replaces L1/L2 loss |
| **AESOP-SR** | CVPR'25 | ★92 | Auto-encoded supervision for perceptual quality |

---

## ComfyUI Upscale Node Directory

### Core Built-in

| Node | What It Does | Key Param |
|------|-------------|-----------|
| `UpscaleModelLoader` | Load .pth model (ESRGAN/SwinIR/SPAN etc.) | `model_name` from `models/upscale_models/` |
| `ImageUpscaleWithModel` | Execute upscale | Fixed scale of loaded model |
| `ImageScale` | Traditional interpolation | Method: nearest/bilinear/bicubic/lanczos |

### Key Third-Party Nodes

| Node | Stars | Underlying Model | VRAM | Best For |
|------|:-----:|-----------------|:----:|----------|
| **SUPIR** | ★2.3k | SDXL img2img + ControlNet | 16-24G | Photorealistic quality ceiling |
| **Ultimate SD Upscale** | ★1.5k | SD tile diffusion + ControlNet | 4-24G | Flexible tile upscale, any checkpoint |
| **SeedVR2 Video** | ★2.6k | Video diffusion model | 16G+ | Video with temporal coherence |
| **NNLatentUpscale** | ★270 | SD latent space | Low | Fast latent upscale |
| **Face Detailer** (Impact Pack) | ★3.2k | GFPGAN/CodeFormer | 2-6G | Post-upscale face fix |
| **ControlNet Aux** | ★4.1k | ControlNet preprocessors | — | Tile/Canny prep for Ultimate SD |
| **WAS Node Suite** | ★1.8k | 210+ utility nodes | — | Image blend, model load variants |
| **flux-tiled-upscaler** | ★7 | Flux + multi-ControlNet | 24G+ | Experimental Flux-quality upscale |

### SUPIR Node Details

```
Type: SDXL img2img + LLaVA-guided ControlNet
Models needed: SUPIR-v0Q.ckpt (or v0F) + SDXL checkpoint
Key params:
  - scale_by: 1.0 (pre-scale input externally)
  - num_steps: 20-50 (higher = more detail, slower)
  - cfg_scale: 4-7 (prompt adherence)
  - control_scale: ControlNet grip on structure
  - sampler: DPM++ 2M SDE recommended
Memory: 24G native, ~10G with fp8 unet
  System RAM: 32GB+ recommended
Note: Now merged into ComfyUI core (PR #13250)
```

### Ultimate SD Upscale Details

```
Principle: Tile image → SD img2img each tile → seam fix
Key params:
  - tile_width/height: match SD native (512 SD1.5, 1024 SDXL)
  - padding: 32-64 (eliminates seams)
  - denoise: 0.15-0.5
    0.15 = subtle detail enhancement
    0.35 = balanced
    0.5  = creative restyling
  - steps: 15-25 per tile
  - seam_fix: band pass / half tile
VRAM floor: ~4GB (tiles keep memory low)
Supports: Any SD checkpoint + ControlNet Tile + LoRA
```

---

## Workflow Templates

### A: Maximum Quality (poster/keyframe)

```
Load Image
  → ImageScale (2x, lanczos)              # Pre-scale to intermediate
  → SUPIR (steps:30, cfg:5, text prompt)   # Diffusion super-resolution
  → Ultimate SD Upscale                    # Tile refinement
       (denoise:0.2, tile:1024, ControlNet Tile strength:0.6)
  → Face Detailer (CodeFormer)             # Face restoration
  → Save Image (PNG/TIFF 16bit)
```

VRAM: ≥16GB | Time: 2-5 min/image | For: posters, stills, hero shots

### B: Batch Efficiency (video frames)

```
Load Image Batch                              # Pre-extracted frames
  → UpscaleModelLoader (4x-UltraSharp)        # Or any .pth model
  → ImageUpscaleWithModel
  → Save Image
```

VRAM: 2-4GB | Time: 0.5-3 sec/frame | For: video frame batches
⚠ Warning: Frame-independent upscale causes temporal flicker

### C: Low-VRAM (<8GB)

```
Load Image
  → Ultimate SD Upscale
       (tile:512, denoise:0.3, SD1.5, ControlNet Tile strength:0.6)
  → Save Image
```

VRAM: ≥4GB | For: constrained hardware

### D: Creative Stylized

```
Load Image
  → ImageScale (2x)
  → Ultimate SD Upscale
       (denoise:0.5, SD1.5 style checkpoint, tile:768)
       + IP-Adapter (style reference)
       + ControlNet Tile (structure:0.7)
  → Save Image
```

For: artistic reinterpretation during upscale

### E: Video (temporal-safe)

```
Load Video (VHS Video Loader)
  → Batch → SeedVR2                        # Temporal coherence
  → VHS Video Combine
```

VRAM: ≥16GB | For: video with temporal stability

---

## Closed-Source Tools Comparison

| Tool | Type | Price | Video | Scale | Quality | Unique Advantage |
|------|------|-------|:----:|:-----:|:-------:|------------------|
| **Topaz Video AI** v6 | Video SR | $299 1-time | ✅ | 4x | ★★★★ | Temporal coherence — unbeatable |
| **Topaz Gigapixel** v8 | Image SR | $99 1-time | ❌ | 6x | ★★★★ | Face Recovery Gen 2 |
| **Magnific AI** | Creative SR | $39/mo | ❌ | 16x | ★★★★★ | Creativity slider; 8-16x unmatched |
| **Krea AI** | Real-time+SR | $30/mo | ❌ | 4x | ★★★ | Real-time preview |
| **NVIDIA VSR** | Playback SR | Free | ✅ | 4x | ★★★ | Only real-time solution |
| **Adobe Super Res** | RAW SR | CC sub | ❌ | 4x | ★★★ | RAW-stage upscale (14-bit data) |
| **ON1 Resize AI** | Print SR | $70 1-time | ❌ | 10x | ★★★ | Print-optimized DPI |
| **Resolve Super Scale** | NLE-integrated | Studio $295 | ✅ | 4x | ★★★ | Seamless NLE integration |
| **Pixelmator ML SR** | Mac SR | $50 1-time | ❌ | 3x | ★★★ | Apple Silicon optimized |

### When to Pick Closed-Source

| Scenario | Why Closed-Source Wins |
|----------|----------------------|
| Video 1080p→4K production | Topaz temporal coherence still unbeaten by open-source |
| Creative 8-16x upscale | Magnific's high-ratio quality unmatched |
| RAW photo→large print | Adobe's RAW-stage processing + ON1's print optimization |
| Real-time playback | NVIDIA VSR — only truly real-time option |
| Non-technical user | Topaz/Upscayl drag-and-drop vs ComfyUI learning curve |

---

## Decision Matrix by Scenario

### Video: 1080p → 4K
🥇 Topaz Video AI — temporal coherence, one-stop
🥈 SeedVR2 (ComfyUI) — open-source, temporal-aware
🥉 Real-ESRGAN anime-v3 — free but frame-flicker risk
4. Resolve Super Scale — most convenient, lowest quality

### Poster/Still: → 8K/16K
🥇 SUPIR (ComfyUI) — photorealism ceiling, text-guidable
🥈 Magnific AI — 16x unmatched, creativity slider
🥉 SUPIR → Ultimate SD (chained) — diffusion + tile refinement
4. Topaz Gigapixel — simplest, Face Recovery

### Old Film Restoration
🥇 Topaz Video AI (Iris model) — optimized for degraded sources
🥈 DiffBIR → Topaz — open-source denoise + commercial SR
🥉 SUPIR → SeedVR2 — all open-source pipeline

### AI Art Upscale
🥇 Magnific AI — creativity slider + prompt for artistic freedom
🥈 Ultimate SD Upscale (style checkpoint) — any checkpoint + LoRA
🥉 SUPIR + style LoRA — text + LoRA dual guidance

### Budget $0
🥇 ComfyUI: Real-ESRGAN + Ultimate SD Upscale
🥈 Upscayl — drag-drop, models fixed
🥉 Real-ESRGAN-ncnn CLI — C++ runtime, no Python

---

## VRAM Budget Table

| Model | 1080p→4K | 4K→8K (tiled) |
|-------|----------|---------------|
| SPAN | <1 GB | <2 GB |
| ESRGAN compact | ~2 GB | ~3 GB |
| Real-ESRGAN x4plus | ~3 GB | ~4 GB |
| SwinIR | ~4 GB | ~6 GB |
| ESRGAN large (HAT-L) | ~6 GB | ~8 GB |
| ResShift | ~8 GB | ~10 GB |
| DiffBIR | ~14 GB | ~20 GB (tiled) |
| SUPIR (fp8) | ~10 GB | ~14 GB |
| SUPIR (fp16) | ~20 GB | ~24 GB+ |

---

## Pitfalls

1. **Temporal flicker** — Frame-by-frame upscale without temporal smoothing causes shimmer/flicker. Use SeedVR2, Real-ESRGAN anime-v3, or Topaz for video. Never chain frame-independent upscale for final delivery.

2. **Hallucinated detail** — Diffusion models (SUPIR, DiffBIR) may invent textures not in the original. For film restoration/archival work, prefer conservative settings (low denoise, high control_strength) or skip the diffusion stage entirely.

3. **Upscale before color grade** — SR models perform best in linear/near-linear space. Apply color grading AFTER upscaling.

4. **Tile seams** — At aggressive tile sizes or low padding, Ultimate SD Upscale may show visible seams. Increase padding to 64 or use seam_fix: "half tile".

5. **Model format confusion** — `.pth` files go in `models/upscale_models/`, `.safetensors` checkpoints in `models/checkpoints/`. Wrong directory = model not found.

6. **SUPIR RAM hunger** — SUPIR needs 32GB+ system RAM in addition to VRAM. OOM errors may be system-RAM, not VRAM.

7. **Face over-polishing** — Real-ESRGAN can produce "plastic" faces. Always follow with CodeFormer or GFPGAN for close-ups.

8. **Fixed-scale models** — ESRGAN/SwinIR/SPAN models are trained for specific scales (2x/4x). Don't chain two 4x models expecting 16x — use a single model at the target scale or use diffusion-based (SUPIR/Ultimate SD) for arbitrary ratios.

## Model Sources

- **OpenModelDB**: https://openmodeldb.info — 669+ community models, rated and tagged
- **Real-ESRGAN**: https://github.com/xinntao/Real-ESRGAN/releases
- **SUPIR pruned models**: https://huggingface.co/Kijai/SUPIR_pruned
- **ComfyUI Manager** → Install Models → search "upscale" / "ESRGAN"
