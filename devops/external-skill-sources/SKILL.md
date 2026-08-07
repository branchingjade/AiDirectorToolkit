---
name: external-skill-sources
description: Manage external GitHub repos as Hermes skill sources — install, sync, pin, and patch skills from third-party repos. Use when the user wants to add skills from a GitHub repo, keep them updated, or handle .skill ZIP format repos.
---

# External Skill Sources

Install skills from any public GitHub repo and keep them auto-updated via cron.

## Quick Reference

| Step | Command |
|------|---------|
| Add tap | `hermes skills tap add <repo-url>` |
| Install from tap | `hermes skills install <identifier> -y` |
| Pin skill | `hermes curator pin <name>` |
| List taps | `hermes skills tap list` |

## Installing Skills

### Normal method (preferred)

```bash
hermes skills tap add https://github.com/owner/repo
hermes skills install "https://raw.githubusercontent.com/owner/repo/main/path/to/SKILL.md" -y
```

### Fallback: clone + copy

When `hermes skills install` times out or hits API rate limits, clone and copy:

```bash
git clone --depth 1 <repo-url> /tmp/skills-tmp
# For repos with SKILL.md directories:
cp -r /tmp/skills-tmp/skills/<category> "$HOME/AppData/Local/hermes/skills/<prefix>-<category>"
# For repos with .skill ZIP files:
cd /tmp/skills-tmp
for f in *.skill; do
    name="${f%.skill}"
    mkdir -p "$name" && unzip -o "$f" -d "$name"
    # Copy SKILL.md to appropriate target directory
done
```

Skills are at `$HOME/AppData/Local/hermes/skills/` on Windows, `~/.hermes/skills/` on Linux/Mac.

After copying, `/reload-skills` or start a new session.

## Auto-Sync with Cron

Create a sync script and schedule it:

```bash
# 1. Write sync script to $HOME/AppData/Local/hermes/scripts/sync-skills.sh
# 2. Create cron:
cronjob(action='create', name='Sync skills', schedule='0 9 * * *',
         script='scripts/sync-skills.sh', no_agent=true, deliver='origin,feishu')
```

Scripts go under `~/AppData/Local/hermes/scripts/` (Windows). Use `no_agent=true` so the script's stdout is delivered verbatim without LLM processing.

## Handling .skill ZIP Files

Some repos (e.g. branchingjade/AI-Skills) distribute skills as `.skill` files (ZIP archives containing SKILL.md). Extract with `unzip` and map to target directories:

```bash
unzip -o "$f" -d "$tmpd"
case "$name" in
    SkillName-*)
        dst="$SKILLS_DST/target-dir"
        mkdir -p "$dst"
        cp "$tmpd/SKILL.md" "$dst/"
        ;;
esac
```

## Custom Patches on Synced Skills

When a synced skill needs permanent modifications (e.g. narrowing triggers), add a `sed` patch in the sync script after the copy step. This ensures the patch survives future syncs:

```bash
cp "$tmpd/SKILL.md" "$dst/"
sed -i 's/original text/replacement text/' "$dst/SKILL.md"
```

### Dedicated sync script for customized skill sets

When a skill set is isolated purely by `skills.disabled` (no local customization — original names, no gates), it can still be kept updated via a **dedicated sync script** rather than the generic tap/yaml sync, so the cron job controls exactly what happens:

1. `git clone --depth 1` the repo
2. Copy each skill dir to `skills/` **under its original repo name** (no rename, no gate re-application — the disabled list is the only isolation)
3. Idempotently ensure the set's names stay in `config.yaml` `skills.disabled` (watch out: a dir name may differ from its frontmatter `name`, e.g. `mv-subtitle-skill-confirmed` dir → `music-video-subtitle-generator` frontmatter name; disabled matches on frontmatter name)
4. Cron: **extend the existing sync job's prompt** with a step to run this script (never create a second cron); the LLM-driven job reports its JSON output alongside the generic sync

Full working example (H3 set, MiniMax-H3 repo): see `references/h3-synced-setup.md`.

## Delivery Targets

- `origin` — current chat
- `feishu` — Feishu home channel (set via `/sethome` in Feishu DM)
- `origin,feishu` — both

## Evaluating Skills Before Installing

Before installing a skill from an unfamiliar repo, evaluate it first. See `references/evaluating-design-skills.md` for the full methodology (search strategy, evaluation checklist, known landscape, red flags). Quick rules:

- Always read the SKILL.md (not just README) to assess actual depth
- Prefer zero-dependency skills over ones requiring npm/Node.js
- Skip persona/role-play templates — look for executable workflows
- Check the coverage gap: does this skill fill a missing phase or duplicate existing ones?

## Trigger Isolation — Hard Disable (config.yaml)

When installed skills may interfere with existing ones (trigger-word overlap, generic names like `MV`/`video prompt`), soft gates **do not work**: editing the description to say "ONLY use when…" or renaming the skill directory with a prefix cannot stop the model from matching on the skill **name** (a name containing `music-video`/`paper-collage` still triggers on those words), and long description gates get truncated by the system-prompt's 57-char window.

The only reliable gate is the hard disable: disabled skills are **removed from the system prompt entirely** — the model never sees the name, so zero false triggers.

```yaml
# config.yaml
skills:
  disabled:
    - h3-prompt-writing
    - h3-3d-animation-short-generator
```

Mechanism: `agent/skill_utils.py::get_disabled_skill_names()` reads it; `prompt_builder.py` skips disabled skills when building the system prompt.

**Hard gate on ALL paths** — disabled skills cannot be loaded any way:
- Auto-trigger: name never enters the system prompt, model never sees it
- `skill_view` tool: `skills_tool.py` `_is_skill_disabled()` returns "Skill is disabled" error
- `/skill <name>` slash command: `skill_commands.py` scan skips disabled; explicit load treats it as missing

To use a disabled skill, re-enable it first: `hermes skills config` (interactive) or edit `skills.disabled` in config.yaml.

### Single-session use WITHOUT re-enabling (preferred)

`read_file` on the skill's on-disk files bypasses the disabled gate entirely — disabled only blocks `skill_view` and `/skill`, not direct file reads. To use a disabled skill for one session only:

1. `read_file ~/AppData/Local/hermes/skills/<skill-dir>/SKILL.md`
2. `read_file` any `references/*` needed (e.g. `references/base-en.txt`)
3. Work with the content in context; it's discarded when the session ends — zero global changes, no re-enable needed.

This is the answer to "how do I temporarily load this disabled skill" — the user prefers this over toggling global config.

Edit config.yaml via python read-modify-write (preserves structure; confirm the file has no comments first, since `yaml.safe_dump` drops them):

```python
import yaml
cfg = yaml.safe_load(open('config.yaml', encoding='utf-8'))
skills = cfg.setdefault('skills', {})
skills['disabled'] = sorted(set(skills.get('disabled', [])) | {names})
yaml.safe_dump(cfg, open('config.yaml','w',encoding='utf-8'), allow_unicode=True, sort_keys=False)
```

Verify statically: `hermes skills list` shows `disabled` = confirmed out of the system prompt (code-level guarantee). Do NOT verify by looping N `hermes chat -q` cases — every `-q` creates a session record and pollutes the session list (60-session mess from one stress test). If dynamic verification is truly needed, run at most one query with a `--source <tag>` marker and delete it afterwards.

Cleanup test sessions (SQLite):

```python
import sqlite3, os
db = os.path.expanduser('~/AppData/Local/hermes/state.db')
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT id FROM sessions WHERE source LIKE 'stress-test%'")
ids = [r[0] for r in cur.fetchall()]
if ids:
    ph = ','.join('?'*len(ids))
    cur.execute(f'DELETE FROM messages WHERE session_id IN ({ph})', ids)
    cur.execute(f'DELETE FROM messages_fts WHERE rowid NOT IN (SELECT rowid FROM messages)')
    cur.execute(f'DELETE FROM session_model_usage WHERE session_id IN ({ph})', ids)
    cur.execute(f'DELETE FROM sessions WHERE id IN ({ph})', ids)
conn.commit()
```

### Router skill — keep a disabled set wakeable (signpost pattern)

Hard-disabling a whole set makes it undiscoverable — the model has no idea the files exist, and **memory is not a reliable wake-up line** (it gets cleaned/compressed). The robust pattern: one small **enabled** generic router skill ("signpost", `external-skill-access`) that carries the pattern + on-disk paths, and instructs `read_file` to load any disabled skill's content on demand. It is **generic**, not per-suite — one router serves all disabled sets (H3 was the first case).

```yaml
# skills/devops/external-skill-access/SKILL.md
name: external-skill-access
description: "Use when user mentions a disabled skill needing content."
---
# 唯一用途：用户提到被 disabled 禁用的技能时，
# 用 read_file 读取（skill_view 会被 disabled 拒绝）：
# - C:\Users\HMSJ\AppData\Local\hermes\skills\<技能目录>\SKILL.md
# - 按需读取同目录 references\*、templates\*
```

Design rules:
- The router is **enabled** (it must be in the system prompt), the content set stays **disabled**
- Paths/pattern are written **in the SKILL.md**, not memory — the router is self-contained, survives memory cleanup
- Session-scoped use only: content loads via `read_file` into the current session, discarded on session end, no re-enable, no config change
- The disabled set keeps **original repo names** — no local content customization (no prefix renaming, no description gates). Customization is redundant: disabled removes the skills from the system prompt, so the model never sees their names or descriptions; stress tests proved content-level gates cannot stop name-based false triggers anyway. Isolation = disabled list only.

This gives three-layer resilience: router skill (always in system prompt) → on-disk files (always readable) → memory (optional, not required).

### Verify with subagents, not hermes chat -q

Dynamic verification of skill-routing behavior should use `delegate_task`, not `hermes chat -q`:
- Subagents run in isolated contexts, **never create session records** (no session-list pollution)
- They can read config, list skills, and reason about which skills they'd load — same model, same system-prompt mechanics
- Test pattern: one adversarial case ("Seedance 视频prompt" → router must NOT load) + one positive case ("MiniMax H3" → router MUST load), ask the subagent to state which skills it would load and why, based only on what's actually visible in its system prompt

### Pitfall: gateway/config rewrites can silently clear skills.disabled

The desktop gateway holds an in-memory config copy and may rewrite `config.yaml` on restart, dropping hand-edited `skills.disabled` entries. If disabled skills suddenly show as enabled, re-apply the disabled list (or set it via `hermes skills config` interactive, which goes through the controlled save path).

## Pitfalls

- `hermes skills install` may time out on slow networks — use clone+copy as fallback
- `hermes skills install` uses GitHub API; unauthenticated limit is 60/hr. Set `GITHUB_TOKEN` in `.env`
- After copying skills manually, run `/reload-skills` or restart session
- Sync scripts use `no_agent=true` — stdout is the delivered message, keep it clean
- On Windows, skill paths use `$HOME/AppData/Local/hermes/skills/`
- Description gates / rename-with-prefix cannot stop model matching on skill name — only `skills.disabled` is reliable
- Skill descriptions are truncated to 57 chars + "..." in the system prompt; long gate text is invisible to the model
- Batch `hermes chat -q` is a session-list polluter — plan the cleanup path before running any dynamic verification
- External skills' `trigger-words` is a Hub-ecosystem field (MiniMax `hub_*` tools); Hermes ignores it, don't rely on it for isolation
