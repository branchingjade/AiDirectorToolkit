# DaVinci Resolve 21: Native Format Support (Lottie / SVG / HTML)

Research compiled 2026-07-15. Source: Blackmagic "What's New" page, YouTube tutorials, MCP tool capabilities.

---

## Lottie (.json / .lottie) — ✅ NATIVE (Resolve 21+)

**New in Resolve 21.** Both Free and Studio.

- Drag `.json` and `.lottie` files directly into **Media Pool**
- Treated as fully rendered animation clips with alpha channel
- Use on timeline as stingers, lower thirds, transitions, titles
- Inspector has **OGraf settings** for customization (loop, etc.)
- **Import only** — no Lottie export/render target

Verbatim from Blackmagid:
> "Native support for OGraf HTML graphics and Lottie animations means that you can now drag .json and .lottie files directly into the media pool, where they will be treated like fully rendered animation clips. Alpha channels are recognized."

> "When placed on a timeline, the file is treated as a rendered animation with maintained transparency, so you can use Lottie graphics as stingers, lower thirds, transitions and titles."

### Practical notes
- `.lottie` (dotLottie) is the newer container format — preferred over raw `.json`
- LottieFiles.com is the main free source
- No Fusion generator for Lottie — it's a Media Pool / timeline feature
- Previous advice "Lottie 手写 JSON 黑屏" was correct for R19 and earlier; R21 has proper native rendering

---

## OGraf HTML Graphics — ✅ NATIVE (Resolve 21+)

**Also new in Resolve 21.**

- Blackmagic's proprietary HTML/CSS-based motion graphics format
- Works identically to Lottie: drag into Media Pool, alpha channel maintained
- Inspector panel has OGraf customization controls
- **Not** arbitrary HTML pages — must be OGraf-spec templates
- **Import only** — no HTML export

This is what the "HTML Graphics" in the "Cut and Edit" section refers to — it's OGraf, not general HTML/CSS.

---

## SVG (.svg) — ❌ NOT in Media Pool (Fusion only)

SVG has **never** been a Media Pool import format, and Resolve 21 did not change this.

- **Fusion page**: Import SVG via Fusion tools (sPolygon node, vector tools)
- Workflow: Open Fusion page → import SVG → composite with MediaIn → back to timeline
- Not drag-and-drop to timeline — requires Fusion composition
- This predates Resolve 21 (tutorials from 2+ years ago exist)
- The Krokodove toolset (now native in R21 Fusion) provides additional vector tools

### SVG → Fusion workflow summary
1. Open clip in Fusion page (or create Fusion comp)
2. Add sPolygon or other vector import tool
3. Load SVG file
4. Connect to Merge node over MediaIn
5. Back to Edit page — renders as part of the Fusion comp

---

## Krokodove Motion Graphics (Fusion — R21)

Resolve 21 now includes the Krokodove toolset natively in Fusion. Over 70 tools described as:
- "utility tools that improve productivity"
- "essential vector and data tools"
- "customizable 2D and 3D graphic templates"

Not a Lottie/SVG/HTML renderer, but complements vector graphics workflows.

---

## Render / Export: None of these are export targets

The Delivery page only offers standard video/image codecs (H.264, H.265, ProRes, DNxHR, DPX, EXR, etc.).

- You **cannot** export/render to Lottie, SVG, or HTML
- These are **import-only** formats
- When you render your timeline normally, Lottie/OGraf clips are rasterized into the output video just like any other clip

---

## Version checklist

| Feature | R18 | R19 | R21 |
|---------|:---:|:---:|:---:|
| Lottie in Media Pool | ❌ | ❌ | ✅ |
| OGraf HTML in Media Pool | ❌ | ❌ | ✅ |
| SVG in Fusion (sPolygon) | ✅ | ✅ | ✅ |
| Krokodove in Fusion | ❌ | ❌ | ✅ |
| SVG in Media Pool | ❌ | ❌ | ❌ |
