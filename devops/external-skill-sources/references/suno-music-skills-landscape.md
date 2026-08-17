# Suno Music Skills Landscape (evaluated 2026-08)

An evaluated case study for the skill-evaluation methodology. Method used: GitHub API repo search + `raw.githubusercontent.com` reads of every candidate's SKILL.md (not just README) + stars/recency/license/dependency check.

## Candidates (all read from SKILL.md bodies)

| Repo | Stars / Activity | Size & depth | Dependencies | Verdict |
|---|---|---|---|---|
| bitwize-music-studio/claude-ai-music-skills | ★417, active 2026-08, CC0-1.0 | 53 SKILL.md + 60+ reference files. Full production line: lyric → suno-engineer → mastering → release. `reference/suno/` (structure-tags, v5-best-practices, genre-list, pronunciation-guide, voice-tags) is the hard asset | Own MCP server (bitwize-music-mcp), Claude Code ecosystem | Best-in-class DEPTH. Too heavy to install whole; steal `reference/suno/` content |
| NuNaught/suno-songwriting-skill | ★23, 2026-05, Apache-2.0 | 13KB main + 63 files total. Writing layer: clarifying interview, lyric/style instructions, vocal coordinate system, translation, genre guardrails | Zero-dependency, pure knowledge | BEST for lyric/style craft merge. Star count underrates it — content is systematic |
| nwp/suno-song-creator-plugin | ★37, 2026-01, MIT, v1.1.0 | 55KB main + subagents (research-artist, review-song) + character-count utils | Python/Node for count scripts | Notable ideas: LLMs can't count chars → script verification; artist-research subagent; copyright-safe style descriptions |
| frankxai/claude-skills-library → free-skills/suno-ai-mastery | ★28 (repo), v2.0.0 2025-12 | 14KB, v4.5+ platform feature reference (Persona/Replace/Covers/8-min songs, colon syntax, 5-tier hierarchy) | Zero-dependency | Useful as v4.5+ feature cheat sheet; shallow on craft |
| RooikeCAO/suno-music-skill | ★1, 2026-03, MIT | 14KB operational: MCP calls, credit protection, cost table | Suno MCP + AceData API (third-party, contains referral link) | Skip — third-party API + referral link = low trust |

## Key findings

1. **anthropics/skills official repo has NO music skill** — checked full tree; no suno/music entry. Music skills live in the community.
2. **All candidates are Claude Code ecosystem** (frontmatter `model:`/`allowed-tools:`/`argument-hint:`). Direct install into Hermes causes trigger conflicts — evaluate for content merge, not wholesale install.
3. **Red flags spotted**: third-party paid API + referral links (RooikeCAO), 55KB+ monolithic SKILL.md (nwp), persona/role-play inflation (bitwize's researchers-* set).
4. **What's worth merging from NuNaught** (user approved this plan 2026-08-13): clarifying-interview flow, dual style-prompt formulas, vocal coordinate system + lightweight phrases, tag embedding rule (`[Section - Cue]`), length heuristics, translation priorities, genre fusion guardrails. NOT merged: genre catalogs ×10 (~60KB), vocal profile/prompt files ×18 (~160KB — research-grade over-engineering), tag superlists.
5. **Vocal direction insight**: a strong Suno vocal prompt is a coordinate bundle (range/tessitura/weight/timbre/phonation/register/vibrato/ornamentation/diction/rhythmic feel/emotional stance), expressed via 5-8 chosen dimensions — not just "male/female singer".

## Useful search angles for future music-skill evaluations

- GitHub API: `q=suno+skill`, `q=claude+skill+music`, `q=ai+music+production+skill`
- Marketplaces: skillsmp.com, eliteai.tools (both mirror community skills with SKILL.md previews)
- Always read the raw SKILL.md; marketplace descriptions overstate quality
