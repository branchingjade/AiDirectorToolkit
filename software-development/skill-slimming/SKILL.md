---
name: skill-slimming
description: Use when a SKILL.md is bloated or pruned.
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [skills, maintenance, slimming, size-limit, references]
    related_skills: [hermes-skill-management, hermes-agent-skill-authoring]
---

# Skill Slimming（SKILL.md 膨胀诊断与瘦身手术）

## Overview

Hermes enforces `MAX_SKILL_CONTENT_CHARS = 100,000` on SKILL.md. Approaching that limit triggers **context-compression pruning**: skill content loaded into a session gets cut (`[SKILL_PRUNED]` in the skill index), so agents see truncated guidance without any hard error. A bloated SKILL.md also costs tokens on every load. This skill is the surgical procedure: diagnose → relocate (never delete) → verify zero loss.

Real case (2026-08): `director-aesthetic-card/SKILL.md` was 99,499 chars (196KB bytes, Chinese 3 bytes/char). Subagents repeatedly misreported it as "知识库 SKILL.md 100K 上限" — the real culprit was this skill being pruned, not the knowledge base. Surgery cut it to 47,113 chars (~52% reduction) with zero content loss. Full step-by-step transcript (quantified blocks, execute order, verification table, reusable template): `references/director-aesthetic-card-case-2026-08.md`.

## When to Use

- Subagents report "SKILL.md 已达 100K 上限 / 无法追加" or `[SKILL_PRUNED]` in skill views
- A SKILL.md exceeds ~50-60k chars (warning zone) or ~90k (danger zone)
- A skill's guidance looks truncated when loaded (workflow steps missing)
- Before adding a new section to a large SKILL.md — measure first

**Don't use for:** creating skills (see hermes-agent-skill-authoring), publishing/versioning (see hermes-skill-management).

## Step 1: Diagnose（先搞清楚，再动手）

Never trust the report — **verify which file is actually large**:

```bash
# 1. Find all SKILL.md over 80k bytes (bytes ≠ chars for CJK: 1 中文=3 bytes)
find "$SKILLS_DIR" -name "SKILL.md" -size +80k | while read f; do echo "$(wc -c < "$f") bytes : $f"; done

# 2. Char count (the enforced limit is chars, not bytes)
python -c "print(len(open(r'<path>/SKILL.md', encoding='utf-8').read()))"
```

⚠️ **Subagents misattribute bloat**: when a subagent says "skill X hit the 100K limit", it may actually mean *its own loaded skill* got pruned (the one embedded in its context), not the skill it claims. Verify each candidate file's actual size before acting. In the real case, the knowledge base SKILL.md was a healthy 31KB; the pruned one was the research-process skill at 99.5K chars.

## Step 2: Quantify the blocks（量化冗余块）

Locate section boundaries and measure each block to find what to move:

```python
lines = open(p, encoding="utf-8").read().split("\n")
marks = {l.strip(): i for i, l in enumerate(lines, 1) if l.startswith("## ")}
def block(start, end): return sum(len(l) for l in lines[start-1:end])
```

Three classic redundancy blocks (the "move to references/" candidates):

| Block type | Why redundant | Where it goes |
|---|---|---|
| **轮次/实测日志**（"XX轮实测有效，详见 references/xxx.md"） | Each entry already points to a references/ map file — the body is a duplicate summary | `references/rounds-log.md` |
| **编号坑库**（㉟㊱㊲…㊿ 系列） | Lessons archive, high value but bulky; loaded on demand keeps the body lean | `references/pitfalls-log.md` |
| **参考登记**（119 个来源地图逐行登记） | `skill_view` linked_files **auto-lists every references/ file** — manual registry is pure duplication | `references/reference-index.md` |

Keep in SKILL.md: 定位/适用/工作流/模板/纪律 — the always-needed guidance. Target: core guidance only (the real case kept 47K of it).

## Step 3: Operate（移动不删除，零丢失）

1. **git commit a snapshot first**（保护点）: `git add -A && git commit -m "chore: <skill> 瘦身前快照（手术保护点）"` — rollback is one `git checkout` away.
2. **Extract each block verbatim** into its new references/ file (with a header explaining the move date + why + how to use). Zero rewriting — pure relocation.
3. **Rewrite SKILL.md**: keep core blocks, replace each removed block with a one-line pointer:
   - Rounds → `**历轮实测记录已归档：references/rounds-log.md**`
   - Pits → `**⚠️ 编号坑库已移入 references/pitfalls-log.md——写卡前必须先 skill_view 加载（第 0 步）**`
   - Registry → reference-index pointer + keep only the few *methodology* entries (source-mining-playbook, api recipes, verify scripts)

**⚠️ 坑可见性补偿（最关键的设计）**: the biggest risk is "pits were always in-context before, now the agent must remember to load them". Compensate by making the load a **mandatory step 0 in the workflow** — "写卡前必须先 skill_view 加载 pitfalls-log" — not a suggestion. Behavior changes from "auto-loaded" to "must-load", equivalent in effect.

## Step 4: Verify（自己测，客观评估）

Four layers, all must pass:

1. **skill_view full load**: `skill_view(name=...)` returns complete content — no truncation, all chapters present. This is the direct test of "no longer pruned".
2. **On-demand load**: `skill_view(name=..., file_path='references/pitfalls-log.md')` returns the full relocated file — proves the references mechanism works for the moved content.
3. **Zero-loss diff（逐行验证，不是抽样）**: `git show <snapshot>:<path>/SKILL.md` → compare line-by-line:
   - Every line of the removed blocks (length > 20 chars) must exist in the new references/ files
   - Every line of the kept core blocks must still exist in the new SKILL.md
   - Report counts: "历轮记录 0 行丢失 / 编号坑 0 行丢失 / 核心块 0 行丢失"
4. **Real-subagent load test**: dispatch a leaf subagent that loads the skill via skill_view and answers "is the body complete? is step 0 (load pitfalls) clear? does the pits file load?" — the closest proxy to next session's real behavior.

Also quantify the volume win: `wc -c` before/after + char counts; compare to healthy peers (8-15K chars is the target zone per authoring skill; the real case went 99.5K → 47K, still above peer zone but below the prune threshold — further slimming optional).

## Common Pitfalls

1. **Trusting the subagent's "100K" report** — verify actual file size first; the report often names the wrong file (the pruned one is *their* loaded skill, not the one they blame).
2. **Deleting instead of moving** — rounds/pits/registry content is historical evidence and validation trails; always relocate to references/, never remove. Zero-loss is the contract.
3. **Forgetting the visibility compensation** — relocating pits without a mandatory step-0 load instruction makes future agents walk into every recorded pit again.
4. **Measuring bytes instead of chars** — CJK text is 3 bytes/char; a 196KB file is only ~99K chars. The enforced limit is chars (`MAX_SKILL_CONTENT_CHARS`).
5. **No git snapshot before surgery** — the operation is structural (block relocation); a snapshot commit makes rollback trivial and diff verification possible.
6. **Registry lines are redundant** — linked_files auto-lists references/; a manual 119-line registry in SKILL.md is pure bloat. Delete it, keep one pointer line.
7. **Concurrent-write race** — check no running subagents are appending to the SKILL.md (delegation live dir freshness) before surgery.
8. **清理字面 `\n` 残留时误伤代码示例（2026-08-07 实测，曾致文件损坏回滚）**：迁移后正文常残留字面 `\n`（反斜杠+n 两字符）——清理前**先分类**：段落间残留（修复）vs **代码示例内的合法转义**（如 `re.sub(r'</p>|<br\s*/?>','\n',c)` 和 `{{noteTA\n|...}}`——这些 `\n` 是示例本身要表达的转义，必须保留）。一键 `content.replace("\\n", "\n")` 会把代码示例也破坏。修复时用**前后文唯一锚点**逐处替换（`"可交叉验证。\\n   - **jina render"` → 真换行），不用全局 replace。
9. **恢复操作也会出错——先 git checkout 回滚，别在原文件上叠加修复（2026-08-07 实测）**：误替换代码示例后，想"恢复"旧版内容时用 `old.find(end_marker)` 定位截取，可能把旧版**大段内容错插入**当前文件（文件从 47K 涨到 92K 才发现）。正确做法：`git checkout <snapshot> -- <path>` 回滚到干净手术版本，**重新做**该修复步骤（第 0 步坑库指令也需重加——它在快照之后才添加）。教训：叠加修复不可控，回滚重做是唯一可靠路径；回滚后记得重新应用快照之后、损坏之前的那些合法改动。
10. **execute_code 里 f-string 不能含反斜杠（Python 语法）**：`print(f"...{len(re.findall(r'\\n', s))}...")` 直接 SyntaxError（f-string 表达式部分不允许反斜杠）。正则/转义计数先算到变量再插值：`cnt = len(re.findall(r"\\n", s)); print(f"count: {cnt}")`——本会话同类错误踩了 3 次。

## Verification Checklist

- [ ] Before/after char counts recorded (target: < ~60K chars, ideally closer to peer zone 8-15K)
- [ ] git snapshot commit exists before surgery
- [ ] Removed blocks exist verbatim in references/ (line-by-line diff: 0 missing)
- [ ] Core guidance blocks still in SKILL.md (line-by-line diff: 0 missing)
- [ ] skill_view returns full content (no [SKILL_PRUNED])
- [ ] skill_view(file_path=...) loads relocated files
- [ ] Mandatory step-0 pitfall-load instruction present in workflow
- [ ] Real-subagent load test passed
