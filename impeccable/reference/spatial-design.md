# Spatial Design

Spacing systems, grids, visual hierarchy. Spacing is the cheapest way to change perceived quality — consistent rhythm reads as craft.

## The 8pt grid

- All spacing, padding, margins, and sizes are multiples of 8 (4px steps allowed for compact density)
- Rationale: 8 divides evenly at 1x/2x/3x DPR — alignment stays stable across densities (Material/IBM Carbon/Fluent consensus)
- Component heights: default 40px controls, compact 32px, dense tables 28-36px rows

| Step | Use |
|---|---|
| 4px | Compact density stepping only |
| 8px | Tight pairing, icon-to-label gaps |
| 16px | Default component padding |
| 24px | Card/panel padding, section gaps |
| 32px | Section separation |
| 48-64px | Page-level spacing, empty-state breathing |

## Grid

- Content region: 12 columns; tool panels 4-8 columns
- Wide dual-pane tools: content 60-75%, parameters 25-40% (not 50/50)
- Max content width for reading: 60-75ch; for tools: fluid up to screen edge
- Breakpoints for tools: full three-pane ≥1440px, drawer 1024-1439px, single-pane <1024px — but detect physical resolution via JS on 4K + Windows scaling (CSS media queries misfire, see accessibility reference)

## Visual hierarchy via space

- Proximity: related controls sit together, unrelated apart — Gestalt proximity law
- Grouping: ≤5-7 groups per screen, ≤7-9 items per group (Miller's law)
- Space beats borders: separate sections with whitespace first, borders only when space is ambiguous
- Alignment: one consistent vertical rhythm per column; avoid centering data-heavy layouts

## Dark mode spatial notes

- Elevation via luminance, not shadow (shadows invisible on dark)
- Surface stack: base → surface-variant → surface-container, each a luminance step up
- Focus: outline/halo, not box-shadow (WCAG 2.4.7)

## Anti-slop checklist

- ❌ Random spacing values (13px, 21px) everywhere
- ❌ Everything centered
- ❌ Card piles with 8px gaps and 40px gutters interchangeably
- ❌ Borders on everything to fake separation
- ✅ One grid, one rhythm, hierarchy from space first

## Sources

- Material Design 3 — layout, density, elevation
- Gestalt proximity principle (Wertheimer et al.)
- Miller 7±2 (1956)
- WCAG 2.2 — 2.4.7 focus visible
