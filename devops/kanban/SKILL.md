---
name: kanban
description: "Multi-agent Kanban board: orchestrator decomposition playbook and worker pitfalls for Hermes Kanban."
version: 3.0.0
platforms: [linux, macos, windows]
environments: [kanban]
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, routing, collaboration, workflow]
    related_skills: []
---

# Kanban — Multi-Agent Work Queue

Hermes Kanban is a durable SQLite board for multi-profile / multi-worker collaboration. This skill covers both roles: the **orchestrator** who decomposes work and routes tasks, and the **worker** who executes cards and hands off results.

---

## Orchestrator — Decomposition Playbook

> The core worker lifecycle is auto-injected via `KANBAN_GUIDANCE`. This section is the deeper playbook for orchestrator profiles.

### Profiles are user-configured — not a fixed roster

Before fanning out, discover which profiles actually exist on this machine:

- `hermes profile list` — prints available profiles
- `kanban_list(assignee="<name>")` — sanity-check a single name (returns empty list for unknown)
- Just ask the user

The dispatcher silently fails to spawn unknown assignees — a card assigned to a nonexistent profile sits in `ready` forever.

### When to use the board (vs. just doing the work)

Create Kanban tasks when:
1. **Multiple specialists needed** — research + analysis + writing
2. **Work should survive a crash** — long-running, recurring, or important
3. **User might want to interject** — human-in-the-loop
4. **Multiple subtasks can run in parallel** — fan-out for speed
5. **Review/iteration expected** — reviewer loops on drafter output
6. **Audit trail matters** — board rows persist in SQLite

If none apply — small one-shot task — use `delegate_task` instead.

### The anti-temptation rules

- **Do not execute the work yourself.** Create a task and assign it.
- **For any concrete task, create a Kanban task.** Every single time.
- **Split multi-lane requests before creating cards.** One card per independent lane.
- **Run independent lanes in parallel.** Link only true data dependencies.
- **Never create dependent work as independent ready cards.** Use `parents=[...]` in `kanban_create`.
- **If no specialist fits, ask the user.** Don't invent profile names.
- **Decompose, route, and summarize — that's the whole job.**

### Decomposition Steps

**Step 1 — Understand the goal.** Ask clarifying questions if ambiguous.

**Step 2 — Sketch the task graph.** Draft it out loud before creating anything:
1. Extract lanes from the request
2. Map each lane to an existing profile
3. Decide independent vs. gated dependencies
4. Create independent lanes as parallel cards
5. Create synthesis/review cards with parent links

Show the graph to the user before creating cards.

**Step 3 — Create tasks and link:**

```python
t1 = kanban_create(title="research: costs", assignee="<profile-A>", body="...")[*** body="..."][task_id"]  # waits for t1+t2
```

`parents=[...]` gates promotion — children stay in `todo` until every parent reaches `done`.

**Step 4 — Complete your own task:**

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 research lanes in parallel, 1 synthesis, 1 draft",
    metadata={"task_graph": {"T1": {"assignee": "<profile-A>", "parents": []}, ...}},
)
```

**Step 5 — Report back** with a plain-prose summary naming actual profiles used.

### Common patterns

- **Fan-out + fan-in:** N research cards (no parents) → 1 synthesis card (parents = all N)
- **Parallel implementation + validation:** implementer + explorer in parallel, reviewer gated on both
- **Pipeline with gates:** `planner → implementer → reviewer`, each with `parents=[previous]`
- **Same-profile queue:** N tasks, same profile, no dependencies — dispatcher serializes
- **Human-in-the-loop:** Any task can `kanban_block()` to wait for input

### Goal-mode cards (persistent workers)

For open-ended cards where one turn rarely finishes:

```python
kanban_create(
    title="Translate the full docs site to French",
    body="Acceptance: every page translated, no English left.",
    assignee="<translator-profile>",
    goal_mode=True,        # judge re-checks after each turn
    goal_max_turns=15,
)[task_id]
```

Write the body as explicit acceptance criteria — the judge evaluates against title + body.

### Recovering stuck workers

When a worker keeps crashing or hallucinating:
1. **Reclaim** — `hermes kanban reclaim <task_id>` — abort and reset to `ready`
2. **Reassign** — `hermes kanban reassign <task_id> <new-profile> --reclaim`
3. **Change profile model** — `hermes -p <profile> model`, then Reclaim

---

## Worker — Pitfalls and Examples

> You're seeing this because the dispatcher spawned you as a worker. The lifecycle (orient → work → heartbeat → block/complete) is auto-injected via `KANBAN_GUIDANCE`.

### Workspace handling

| Kind | What it is | How to work |
|------|-----------|-------------|
| `scratch` | Fresh tmp dir, yours alone | Read/write freely; GC'd when archived |
| `dir:<path>` | Shared persistent directory | Other runs will read what you write |
| `worktree` | Git worktree at resolved path | If `.git` missing, run `git worktree add <path> ${HERMES_KANBAN_BRANCH:-wt/$HERMES_KANBAN_TASK}` |

### Tenant isolation

If `$HERMES_TENANT` is set, prefix memory entries with the tenant to prevent context leakage.

### Good summary + metadata shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, 14 tests pass",
    metadata={"changed_files": ["rate_limiter.py"], "tests_passed": 14,
              "decisions": ["user_id primary, IP fallback"]},
)
```

**Coding task needing review:**
```python
kanban_comment(body="review-required handoff:\n" + json.dumps({...}, indent=2))
kanban_block(reason="review-required: rate limiter shipped, 14/14 tests pass — needs eyes")
```

**Research task:**
```python
kanban_complete(
    summary="3 libraries reviewed; vLLM wins on throughput",
    metadata={"sources_read": 12, "recommendation": "vLLM"},
)
```

**Review task:**
```python
kanban_complete(
    summary="reviewed PR #123; 2 blocking issues found",
    metadata={"pr_number": 123, "findings": [...], "approved": False},
)
```

### Claiming cards you created

If your run produced new kanban tasks, pass their ids in `created_cards`:

```python
c1 = kanban_create(title="remediate SQL injection", assignee="security-worker")
kanban_complete(summary="Review done; spawned remediations.",
                created_cards=[c1[task_id"]])
```

**NEVER invent ids.** Only list ids captured from successful `kanban_create` return values.

### Block reasons that get answered fast

Bad: `"stuck"` — no context.

Good: one sentence naming the specific decision needed. Leave longer context as a comment:

```python
kanban_comment(body="Full context: user IPs from Cloudflare but NAT causes false positives.")
kanban_block(reason="Rate limit key choice: IP (simple, NAT-unsafe) or user_id (requires auth)?")
```

### Heartbeats worth sending

Good: `"epoch 12/50, loss 0.31"`, `"scanned 1.2M/2.4M rows"`
Bad: `"still working"`, empty notes, sub-second intervals

### Retry scenarios

If `kanban_show` shows prior runs, you're a retry:
- `timed_out` — chunk the work or shorten it
- `crashed` — OOM, reduce memory footprint
- `spawn_failed` — profile config issue, ask human via `kanban_block`
- `blocked` — check unblock comment in thread

### DO NOT

- Call `delegate_task` as substitute for `kanban_create`
- Call `clarify` — use `kanban_comment` + `kanban_block` instead
- Modify files outside `$HERMES_KANBAN_WORKSPACE`
- Create follow-up tasks assigned to yourself
- Complete a task you didn't finish — block it instead

### CLI fallback

Every tool has a CLI equivalent:
- `kanban_show` ↔ `hermes kanban show <id> --json`
- `kanban_complete` ↔ `hermes kanban complete <id> --summary "..."`
- `kanban_block` ↔ `hermes kanban block <id> "reason"`
- `kanban_create` ↔ `hermes kanban create "title" --assignee <profile>`

Use tools from inside an agent; CLI exists for the human at the terminal.

### Pitfalls

- **Task state can change between dispatch and startup.** Always `kanban_show` first.
- **Workspace may have stale artifacts.** Read the comment thread for context.
- **Don't rely on CLI in containers.** The `kanban_*` tools work everywhere; `hermes kanban` CLI may not be installed in Docker/Modal/SSH.
