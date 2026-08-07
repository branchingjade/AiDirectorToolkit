# Evaluating External Design Skills

How to discover and judge frontend design skills from GitHub, as of 2026-07.

## Search strategy

Run parallel GitHub API searches with different angles:

```bash
# Hermes-specific
curl -s "https://api.github.com/search/repositories?q=hermes+skill+design&sort=stars&order=desc&per_page=10"

# Claude Code / Codex design skills (often Hermes-compatible)
curl -s "https://api.github.com/search/repositories?q=claude+skill+design+html+css&sort=stars&order=desc&per_page=10"

# General awesome-skills collections
curl -s "https://api.github.com/search/repositories?q=awesome+skills+ai+design+frontend&sort=stars&order=desc&per_page=10"
```

## Evaluation checklist

For each candidate, check in order:

1. **Hermes compatibility** — does SKILL.md mention Hermes in compatibility list? If not, can the format be adapted?
2. **Read SKILL.md directly** (not just README) — `curl -s "https://raw.githubusercontent.com/owner/repo/main/SKILL.md"`
3. **Command/feature coverage** — map against the gap. Is it filling a missing phase or duplicating?
4. **Dependencies** — does it need npm, Node.js, Python packages, or other binaries? Prefer zero-dependency.
5. **License** — Apache 2.0, MIT are fine. Avoid restrictive licenses.

## Known landscape (design skills)

### Installed (internal)
- `claude-design` — creation process + taste
- `popular-web-designs` — 54 brand design systems
- `sketch` — rapid variant exploration
- `design-md` — token spec authoring

### Gap: evaluation + refinement
No installed skill covers design critique, accessibility audit, polish, or browser live-iteration.

### Best external candidate
`DevvGwardo/impeccable` (★10, Apache 2.0) — 23 design commands, Hermes-compatible. Fills the entire evaluation+refinement gap.

### Other candidates evaluated
- `peixl/ifq-design-skills` (★24, v3.0.0) — template-driven, requires Node.js
- `taffy-owo/codex-skill-awesome-design-md` (★12) — 73 DESIGN.md templates, overlaps with popular-web-designs
- `bienhoang/design-clone` (★5) — screenshot-based cloning, npm package
- `pato-gonzalez/design-system-stack` (★4) — 4-skill bundle
- `itgoyo/hermes-skills` (★36) — 310+ skills, design ones mostly persona role-play, skip

### Red flags when evaluating
- Large repos with many skills but design ones are persona/role-play templates, not executable workflows
- Skills that require npm/Node.js without clear benefit over zero-dependency alternatives
- Skills whose description doesn't match actual SKILL.md depth (always read the SKILL.md)
