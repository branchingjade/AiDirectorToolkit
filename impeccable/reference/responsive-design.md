# Responsive Design

Mobile-first, fluid design, container queries. Tools have their own responsive rules — desktop-first with graceful degradation, not mobile-first transplant.

## Tool-type responsive (the common case)

Tools are used on desktop first. Design ≥1280px, then degrade:

| Width | Behavior |
|---|---|
| ≥1440px | Three panes open; parameters always visible |
| 1024-1439px | Parameter pane collapses to a drawer (button summons it) |
| <1024px | Two panes stack to one; navigation collapses to hamburger |
| Tool floor | Even narrow: content + summonable parameters, never bare single column |

## The 4K + Windows scaling trap (verified)

CSS media queries trigger on CSS pixels, not physical pixels. On 4K with 150% Windows scaling, `@media (max-width: 1280px)` may never fire (CSS width ≈ 2560/1.5 ≈ 1707px).

Reliable approaches:
- **JS physical detection**: `screen.width * window.devicePixelRatio` to decide layout classes — use when you must know the real screen
- **rem + clamp() fluid type/spacing**: `html{font-size: clamp(14px, 12px + 0.35vw, 18px)}` covers 1080p/2K/4K
- **Container queries**: `@container` responds to container width, not viewport — good for panel-internal layouts
- devicePixelRatio values: 1.0 at 100%, 1.25 at 125%, 1.5 at 150%

## Fluid type

- Size by clamp(), never fixed px for body text on mixed-resolution setups
- Test at 100/125/150% Windows scaling, not just browser zoom

## Mobile-first vs desktop-first

- Content/landing: mobile-first, progressive enhancement
- Tools: desktop-first, graceful degradation — the complex state lives on wide screens
- Do not hide real functionality behind "more" menus on desktop to save space

## Anti-slop checklist

- ❌ Media-query-only layout that breaks on 4K + scaling
- ❌ Fixed-px type that does not scale
- ❌ Mobile-first applied to a desktop tool (degenerates to icon soup)
- ❌ Breakpoints named after devices instead of content widths
- ✅ JS physical detection + rem/clamp + container queries for tools

## Sources

- W3C — Media Queries Level 5, Container Queries
- Material Design 3 — responsive breakpoints
- Local verified notes (2026-08): CSS media query failure on 4K + Windows scaling
