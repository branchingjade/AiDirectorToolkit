---
name: comfyui-image-restoration
description: "ComfyUI image restoration workflows — CFG=1 unconditional diffusion, GAN+diffusion two-stage restoration, SeedVR2 parameters, turbo model sampling. Use when the user asks about fixing degraded/over-edited images, upscaling for restoration (not just enlargement), or SeedVR2 configuration."
version: 1.0.0
---

# ComfyUI Image Restoration

Restore images degraded by multi-round AI editing (GPTImage, NanoBanana, etc.)
using ComfyUI workflows. Covers restoration-specific techniques that differ from
general image generation or creative upscaling.

## When to Use

- User asks to fix images degraded by repeated AI editing
- Texture waxing, JPEG compression artifacts, color shifts from VAE round-trips
- SeedVR2 node configuration and model selection
- Choosing samplers for turbo/distilled checkpoints
- Understanding why a specific workflow works better than alternatives

## Core Technique: CFG=1 Unconditional Diffusion

The most effective pattern for restoring multi-edit degradation:

```
Checkpoint (e.g., z-image-turbo-bf16-aio)
  → CLIPTextEncode: EMPTY prompt
  → PixelKSampleUpscalerProvider:
       cfg = 1         # DISABLE classifier-free guidance
       denoise = 0.25  # Keep 75% original, fix 25%
       steps = 3       # Turbo checkpoints need 1-4 steps
       scheduler = sgm_uniform (try karras)
       sampler = dpmpp_2m (not SDE variant at CFG=1)
```

**Why CFG=1 with empty prompt:** Multi-edit damage (texture waxing, DCT blocks)
deviates from the model's training distribution of natural images. Unconditional
diffusion (CFG=1, no prompt) simply projects the input BACK onto the natural-image
manifold. It doesn't "generate new detail" — it undoes distribution-level damage.

Adding a prompt or raising CFG introduces semantic guidance that competes with
the restoration goal, producing synthetic-looking compromise textures.

**Denoise threshold:** 0.25 is the sweet spot. 0.15 = too little, compression
noise survives. 0.40+ = too much, hallucinated content replaces real structure.
At CFG=1, higher denoise doesn't mean "better restoration" — it means random
infilling without guidance.

## Two-Stage Restoration: GAN + Diffusion

The best single-path pattern chains RealESRGAN with SD diffusion:

```
Image → ImageScale (nearest-exact, conservative) 
      → RealESRGAN_x4plus (GAN 4× upscale)
      → PixelKSampleUpscalerProvider (CFG=1, denoise 0.25)
           → IterativeImageUpscale (upscale_factor=1.5)
```

**Stage 1 (RealESRGAN):** Injects high-frequency texture. Goes from ~1MP to 4×.
Uses a high-order degradation pipeline trained on 1000+ random degradation combos
(blur + noise + compression + downscale). Matches multi-edit damage patterns.
Weakness: GAN produces "plastic" faces and ringing artifacts — sharp but fake.

**Stage 2 (SD diffusion, CFG=1, denoise 0.25):** Projects GAN output back onto
the natural image manifold. The 25% denoise is just enough to smooth GAN artifacts
without creating new content. RealESRGAN provides the textures; SD validates them.

**Why both are needed:** GAN alone = sharp fake textures. SD alone from blurry
interpolation = not enough denoise budget. GAN + SD = textures validated.

## SeedVR2

See `references/seedvr2-parameters.md` for the complete parameter reference
covering v1.5.x (fork) and v2.5.x (main), including all DiT models, BlockSwap,
and the critical `color_correction` parameter.

Quick version guide:
- **v1.5.x (fork):** Monolithic `SeedVR2` node + `SeedVR2BlockSwap`. No color correction.
- **v2.5.x (main):** Modular: `SeedVR2VideoUpscaler` + `SeedVR2LoadDiTModel` +
  `SeedVR2LoadVAEModel`. Adds `color_correction` (lab/wavelet/hsv/adain/none).
  "Sharp" DiT variants available for better high-frequency retention.

For single-image restoration, the key upgrade in v2.5.x is `color_correction=lab`
— corrects the color shift that diffusion unavoidably introduces. Without it,
SeedVR2 alone often produces worse results than the iterative upscale path.

## Sampler Selection for Turbo/Distilled Models

Turbo checkpoints (z-image-turbo, LCM-distilled) are trained with specific noise
schedules. Matching the sampler to the distillation method matters:

| Priority | Sampler | When |
|:--------:|---------|------|
| 1 | `lcm` | LCM-distilled models — best match for training schedule |
| 2 | `euler` | Simplest deterministic, stable at low step counts |
| 3 | `dpmpp_2m` | Second-order, no SDE noise injection |

**Avoid SDE variants at CFG=1.** SDE samplers inject stochastic noise each step.
At normal CFG (7-8), text guidance pulls the noise back on track. At CFG=1, there
is no guidance — injected noise is pure random perturbation that degrades output.

## Pitfalls

1. **Vision model hallucinates parameter values.** Screenshot-based analysis
   frequently misreads slider numbers (e.g., 0.25 read as 0.65, 3 read as 8).
   ALWAYS extract parameters programmatically via `app.graph._nodes` from the
   ComfyUI iframe when available. Vision analysis is for layout and node types,
   not numeric values.

2. **RunningHub uses GetNode/SetNode for I/O.** GetNode(name) pulls the uploaded
   image by name; SetNode(name) declares the output. Both must be present.
   LoadImage is the upload widget and must connect to SetNode.

3. **Node `type` field must match NODE_CLASS_MAPPINGS key, not Python class name.**
   Example: Python class `RH_ICCustom_Sampler` → registered type `"RunningHub ICCustom Sampler"`.

4. **Workflow JSON requires synced port references.** The `links` array AND
   each node's `inputs[i].link` / `outputs[i].links` must agree. Run a sync pass
   after any programmatic JSON generation.

5. **IterativeImageUpscale is not a processing node — it's a post-scale step.**
   The real work happens in PixelKSampleUpscalerProvider. Set `upscale_factor=1.0`
   if no additional enlargement is needed.

## Overlap

This skill overlaps with the bundled `comfyui` skill (setup, execution, node
types) and its `references/upscale-model-guide.md` (model comparisons). This
skill specializes in restoration-specific patterns and SeedVR2; the bundled
skill covers general ComfyUI operations.
