# Product Register

Product surfaces — app UI, dashboards, tools — are where users do real work. The register changes everything about what "good" means: density is virtue, drama is liability, and the interface must get out of the way.

## Register

Brand: marketing pages sell a promise; they can be bold, cinematic, sparse.
Product: dashboards and tools keep a promise. Users live here for hours. What reads as "premium" on a landing page reads as "noise" in a tool.

## What changes

| Dimension | Brand instinct | Product rule |
|---|---|---|
| Density | White space is luxury | Information density wins; default to expanded, not collapsed |
| Hierarchy | One hero moment | One primary action per screen; everything else recedes |
| Color | Palette as identity | Neutrals do the work; accent reserved for the single primary action and states |
| Motion | Cinematic entrances | Purposeful only: feedback, spatial continuity, causal narration (100-300ms) |
| Tone | Voice and personality | Clarity beats cleverness; users are mid-task |
| State | Rarely shown | Four states always designed: loading / empty / error / success |

## Dark mode is the default for tools

- Dark themes suit long-session, screen-focused work (color grading, monitoring, code) — NN/g 2020
- Extreme dark (near-black) but not pure black; layer surfaces by luminance, not borders — Material Elevation
- Contrast floors: body text 4.5:1, large text and UI components 3:1 — WCAG 1.4.3 / 1.4.11
- Disabled states are exempt from contrast requirements — WCAG

## Layout defaults for tools

- Two columns (content 60-75% + parameters 25-40%) or three (nav ≤240px + content + parameters 280-360px)
- Parameters always visible by default; collapse is a user action, not a design default
- 8pt grid; compact density may step at 4px
- Splitter interaction: double-click resets, arrow keys nudge 10px, hit area ≥16px (Fitts), content min 320px / parameter min 240px max 480px
- Persist layout state (column widths, collapse) per user per view — Nielsen #6 recognition over recall
- Remember the user's last view, filters, and search terms — recognition over recall

## Tables (the workhorse of tools)

- Freeze headers on scroll; hover-reveal row actions; batch action bar appears on selection
- Sort/filter in place, no page jumps; key columns first, not all equal width
- 28-36px row height for data-dense tables

## Anti-slop checklist (product)

- ❌ Gradient text on metrics
- ❌ Glassmorphism just because
- ❌ Everything animating simultaneously
- ❌ Two primary buttons per screen
- ❌ Collapsed-by-default parameters
- ❌ Empty states that just say "No data"
- ✅ One sharp accent, committed density, clear hierarchy, honest states

## Sources

- NN/g — dark mode research (2020), table/list studies, Nielsen heuristics #1/#6/#7/#8
- Material Design 3 — elevation, density, data tables
- WCAG 2.2 — 1.4.3 / 1.4.11 / 2.4.7
- Fitts' law (1954) for hit-target sizing
