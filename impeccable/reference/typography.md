# Typography

Type systems, font pairing, modular scales, OpenType. Typography carries most of the perceived quality of an interface — weight, size, and letter-spacing values carry more visual identity than the specific font face.

## Establish a type system

| Layer | Role | Notes |
|---|---|---|
| Display | Hero moments only | Large, rare, and meaningful |
| Heading | Section structure | 2-3 sizes max |
| Body | Default reading | The workhorse size |
| Caption/Secondary | Metadata, timestamps | Smaller, lower contrast |
| Mono | Code, values, IDs | Separate stack |

## Modular scale

- Pick a ratio (1.25 minor third, 1.333 major third for display-heavy; 1.2 for dense tools)
- Base size: 16px body is the safe default; tools may set fluid base via `clamp(14px, 12px + 0.35vw, 18px)` to cover 1080p/2K/4K
- Use rem for all sizes so the base scales the whole system
- Do not scale every step — skip intermediate sizes to create contrast

## Hierarchy without theatrics

Change at least two of three: size, weight, color/luminance. Changing all three on every level is over-design (NN/g visual hierarchy).

| Level | Typical recipe |
|---|---|
| H1 | 24-28px / 600-700 / full-contrast |
| H2 | 18-20px / 600 / full-contrast |
| Body | 14-16px / 400 / full-contrast |
| Secondary | 13px / 400 / reduced contrast (~55-70% luminance) |
| Caption | 12px / 400 / further reduced |

## Font pairing

- Two families max: one for UI/headings, one optional mono
- Same-family weight contrast beats mixing families — Inter 400/500/600 covers most tools
- When a brand font is unavailable on CDN, substitute by character (see popular-web-designs font table) and preserve weight/size/tracking exactly

## Dark mode specifics

- Pure white text on dark: 4.5:1 is fine for body, but avoid full-white for large text — slight off-white (#e8eaed) reduces bloom
- Reduced-contrast layers need care: luminance steps, not opacity fades
- Mono values often read better slightly brighter than body

## Anti-slop checklist

- ❌ 7 font sizes everywhere (no system)
- ❌ Letter-spacing on body text
- ❌ All-caps for everything
- ❌ System font stack with zero customization when a brand exists
- ✅ One scale, rem-based, two families, hierarchy via 2-of-3 changes

## Sources

- NN/g — visual hierarchy research
- Material Design 3 — type scale
- WCAG 2.2 — 1.4.3 contrast for text sizes
