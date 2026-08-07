# Projects vs Worktrees: Design Intent & Practical Difference

> From 2026-07-20 session — source code inspection + official docs research.

## Projects (`projects.db`)

**Schema:**
```
projects: id, slug, name, primary_path (flat — no parent_id)
project_folders: project_id, path (multi-path support)
sessions: NO project_id column (no direct session→project mapping)
```

**Design intent:** Desktop UI session filtering. Sidebar grouping only.

**What it ISOLATES:** Nothing.
- Skills: `%LOCALAPPDATA%/hermes/skills` — global
- Memory: `~/.hermes/MEMORY.md` — global
- Config: `config.yaml` — global
- Sessions: `state.db` — global

**What it DOES:**
- Groups sessions in the sidebar by project tag
- Sets working directory on project switch
- Loads `AGENTS.md` / `CLAUDE.md` / `.cursorrules` from project path

**Key insight:** Creating a project entry does NOT create an isolated work environment. It is a label, not a sandbox.

**This user's setup:** Works from a single Hermes directory with global skills/memory. Splitting project entries would break skill access and memory continuity. The correct approach for session categorization is a static Markdown file (`会话分类.md`), not database-level project entries.

---

## Worktrees (`.worktrees/`)

**What it is:** Hermes wrapper around `git worktree add`. Creates separate file trees sharing the same `.git` repo.

**Design intent:** Git conflict avoidance during multi-agent concurrent editing. When Hermes spawns sub-agents that modify files simultaneously, each gets its own working copy.

**What it ISOLATES:** File system only.
- File tree: ✅ (each worktree has own files)
- Git: partially (shared `.git`, separate HEAD/index)
- Hermes state: ❌ (same state.db, skills, memory)

**When NOT needed:** Single-agent operation. MoA does NOT use worktrees — MoA is a model-routing layer, not a subagent-spawning mechanism.

**User's `.worktrees/blender/` and `.worktrees/eagle/`:** Historical stubs (1 file each), created Jul 2-3, 2026 by earlier subagent operations. Not relevant to current work.

---

## Methodology Lesson

The assumption "project switch → isolated skills/memory" was made by analogy to IDE workspaces (VS Code, JetBrains), without checking Hermes internals. It was wrong. The correct sequence is:

1. Check schema: `sqlite3 state.db "PRAGMA table_info(sessions)"`
2. Verify paths: `ls %LOCALAPPDATA%/hermes/skills/`
3. Read config: `cat config.yaml | grep -i project`
4. THEN conclude.

Never infer Hermes behavior from other tools' conventions.
