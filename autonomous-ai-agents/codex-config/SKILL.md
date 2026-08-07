---
name: codex-config
description: "Configure Codex CLI agent behavior — language, AGENTS.md, config pitfalls, prompt verification."
version: 1.0.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Codex, Config, Language, AGENTS.md]
    related_skills: [codex]
---

# Codex CLI Configuration

Configure Codex CLI agent behavior beyond the basics — output language, project
instructions, config pitfalls, and prompt verification.

Load the `codex` skill for general delegation workflows; this skill covers
configuration specifics the bundled skill omits.

## Agent Output Language

`localeOverride = "zh-CN"` in `config.toml` (`[desktop]` section) only controls
the Codex **desktop app UI** (menus, buttons, chrome). It does **not** affect the
agent's output language during task execution.

To control the agent's output language, use **`AGENTS.md`** — a project-level
instructions file placed in the **git repo root**. Codex injects its contents
into the system prompt wrapped in `<INSTRUCTIONS>…</INSTRUCTIONS>` tags.

```markdown
# AGENTS.md (project root)
始终使用简体中文回复。所有输出内容、解释说明、代码注释均使用中文。
```

**Verify injection:**

```
codex debug prompt-input 2>&1 | grep "AGENTS.md"
```

## AGENTS.md Rules

- Must be in the git repo root (same directory as `.git`)
- **Project-scoped** — only takes effect when Codex runs inside that repo
- For multiple projects that need the same instructions, copy `AGENTS.md` to
  each project root
- For one-off sessions in directories without `AGENTS.md`, use `-c` overrides
  or pass language instructions directly in the prompt

## Pitfalls

### `[instructions]` in config.toml breaks config parsing

Do **NOT** add `[instructions]` to `config.toml` — it is not a valid config key
in Codex v0.146+ and will cause parse failure:

```
codex doctor → "config could not be loaded"
```

The fix: remove the `[instructions]` block and use `AGENTS.md` instead.

### `localeOverride` only affects desktop UI

Setting `localeOverride = "zh-CN"` in `[desktop]` affects menus and dialogs, not
agent behavior. The two are independent — you can have English UI with Chinese
agent output (via AGENTS.md) or vice versa.

### `terminal_visualization_instructions` feature flag is unrelated

`codex features list` may show `terminal_visualization_instructions` — this is
about terminal display, not agent language instructions.

## Useful Diagnostic Commands

```bash
# Full health check
codex doctor

# Inspect what Codex sends to the model (includes AGENTS.md if present)
codex debug prompt-input

# List feature flags
codex features list

# Verify config is parseable
codex doctor 2>&1 | grep "config"
```

## Related

- `codex` skill — general delegation workflows (exec, review, background mode)
