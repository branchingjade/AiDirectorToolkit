# Multi-User Memory Isolation

**⚠️ CRITICAL (2026-07-02): The "Selective Write via SOUL.md Personality Gating" approach documented below does NOT work.** `~/.hermes/SOUL.md` is not loaded by Hermes — zero references in hermes-agent source code. The file is dead. Do NOT rely on it for memory write gating.

### Working alternatives (use ONE)

| Method | Strength | Your DM can write? | Injection path |
|--------|----------|:---:|----------------|
| `hermes tools disable memory --platform feishu` | Hard block | ❌ | Toolset disabled at platform level |
| `agent.system_prompt` in config.yaml | Soft (personality) | ✅ | `_load_ephemeral_system_prompt()` → `combined_ephemeral` → `ephemeral_system_prompt` → AIAgent. **Universal — injects into ALL sessions (CLI + feishu + every platform).** Agent can see `**User:** 妖玉` / `**Session type:** Multi-user` from `build_session_context_prompt()` and gate writes accordingly. |
| `display.platforms.feishu.system_prompt` | Soft (personality) | ✅ | Injected via display config path. **Feishu-only.** |
| Separate profile | Hard isolation | ✅ (own profile) | `hermes profile create feishu-bot --clone-from default --clone` |

**Recommended for trusted-team single-profile**: `agent.system_prompt` — injects once, works everywhere. Set via:
```bash
hermes config set agent.system_prompt "# 记忆写入规则

仅当系统提示中「**User:**」行显示为「妖玉」且「**Session type:**」不包含 Multi-user 时，方可调用 memory 工具写入记忆。其他用户或群聊均禁止写入。

记忆读取不受此限制——所有会话均可引用已有记忆和用户画像。"
hermes gateway stop && hermes gateway start
```

The SOUL.md sections below are kept for historical reference only. They describe a mechanism that was assumed to work but never actually did.
The SOUL.md sections below are kept for historical reference only. They describe a mechanism that was assumed to work but never actually did.

---

When the Feishu bot is added to group chats or accepts DMs from multiple users, memory isolation becomes a concern. Hermes has **session-level isolation** but **profile-level memory sharing**.

## The Problem

- **Sessions are isolated**: `group_sessions_per_user: true` (default) ensures each user's conversation is in its own session — messages don't leak between users
- **Memory is NOT isolated**: `MEMORY.md` and `USER.md` are profile-level files injected into EVERY session, regardless of which user triggered the session
- If user B DMs the bot and the agent saves a memory ("user prefers Python 3.13"), that memory appears in user A's sessions too
- User profile (`USER.md`) is also shared — the agent can't distinguish "who the user is" between multiple Feishu users

## Solutions (ranked by cleanliness)

### 1. Separate Profile (cleanest)

Create a dedicated profile for the Feishu bot:

```bash
hermes profile create feishu-bot
# Configure gateway on this profile
# This profile's memory is completely isolated from your personal profile
```

Pro: Complete isolation. Con: Two profiles to manage.

### 2. Disable Memory on Feishu Profile

Keep one profile but disable memory for gateway sessions:

```bash
hermes config set memory.memory_enabled false
hermes config set memory.user_profile_enabled false
```

Pro: Simple. Con: You lose memory benefits even for your own Feishu messages.

### 3. Feishu App Visibility Restriction (source blockage)

In [Feishu Developer Console](https://open.feishu.cn/) → Your App → Security Settings:
- Set visibility to "仅应用管理员可见" (app admin only) or specific personnel
- Prevents other users from finding/adding the bot in the first place

Pro: Zero code changes, blocks at the source. Con: Can't share bot intentionally.

### 4. External Memory Providers (partial)

Hermes supports 8 external memory backends. Two support native per-user isolation:

- **Honcho**: Multi-agent user modeling, cross-platform identity mapping (`observeMe: true, observeOthers: false`)
- **Mem0**: Per-memory `user_id` field, scoped retrieval/storage

**CRITICAL PITFALL**: External providers run ALONGSIDE built-in memory, not instead of it. Built-in `MEMORY.md`/`USER.md` remain profile-level and shared. External providers only solve their own portion of the isolation problem.

### 5. Feishu App Permission Scope

Restrict bot permissions in Feishu console:
- Only enable `im:message` for specific chat scopes
- Don't enable `im:message.p2p` if DMs should be blocked
- Use `im:message:send_as_user` carefully — it gives the bot access to your personal identity

## Memory Architecture: Two Independent Layers

Hermes memory has TWO independent layers that can be controlled separately:

| Layer | What | Controlled by |
|-------|------|--------------|
| **Injection (READ)** | MEMORY.md + USER.md → system prompt at session start | `memory.memory_enabled` / `memory.user_profile_enabled` in config.yaml |
| **Tool (WRITE)** | `memory` tool — agent can add/replace/remove entries | `memory` toolset per-platform (`hermes tools disable memory --platform feishu`) |

These are decoupled. Disabling the `memory` toolset for a platform:
- Memory IS still injected into the system prompt ✅ (agent knows your preferences)
- Memory CANNOT be written ❌ (agent has no tool to call)

This enables the read-only memory pattern without config changes.

```bash
# Read-only memory for feishu platform
hermes tools disable memory --platform feishu
hermes gateway restart

# Verify
hermes tools list --platform feishu | grep memory
# → ✗ disabled  memory

# CLI still has full memory access
hermes tools list --platform cli | grep memory
# → ✓ enabled  memory
```

### Per-Platform Tool Control

Tools can be enabled/disabled per gateway platform. The `--platform` flag accepts: `cli`, `feishu`, `telegram`, `discord`, `slack`, etc. Changes take effect after gateway restart.

## Selective Write via SOUL.md Personality Gating

Keep `memory` toolset ENABLED for feishu but gate writes with personality instructions in `~/.hermes/SOUL.md`. Relies on the Feishu adapter injecting user identity into the system prompt:

- **DM sessions**: `**User:** <display_name>` in system prompt — exact match to gate writes
- **Group sessions**: `**Session type:** Multi-user session` — blanket block, no per-message filtering needed

**Key insight**: The gate is on SESSION TYPE, not per-message sender. A DM with `**User:** 妖玉` gets full write; any `Multi-user session` (group) gets zero write regardless of who sends the message. This is simpler and safer than per-message prefix checking.

Create `~/.hermes/SOUL.md` (plain markdown, not YAML config):

```markdown
# 记忆写入规则

仅当系统提示中当前会话满足以下条件时，方可调用 memory 工具（add/replace/remove）：
- DM 会话且 `**User:**` 行显示为「妖玉」
  （备选：若显示为 open_id，则为 `ou_7288c4a018284580d463d0239cbd47cf`）

以下情况禁止写入记忆：
- 系统提示中显示 `**Session type:** Multi-user`（群聊）
- `**User:**` 行显示的名称不是「妖玉」（其他人的私聊）

以上规则不影响记忆读取——所有会话均可引用已有记忆和用户画像回答问题。
```

After creating/editing SOUL.md, restart gateway: `hermes gateway restart`

### Pitfall: Check existing memory before adding new constraints

Before creating SOUL.md rules, check existing memory (via `memory` tool entries) for already-established preferences. In this session, the format rule "post格式md" was already in memory (`回复规则：无推理/无进度/无底栏，中文简洁，post格式md`). The SOUL.md format section was redundant — the memory entry was the canonical constraint all along. Memory is durable; SOUL.md is supplementary. Don't recreate what memory already covers.

### Combined SOUL.md (Memory Isolation + Format)

The final working SOUL.md combines both memory write gating AND Feishu markdown format in one file:

```markdown
# 记忆写入规则

仅当系统提示中当前会话满足以下条件时，方可调用 memory 工具（add/replace/remove）：
- DM 会话且 `**User:**` 行显示为「妖玉」
  （备选：若显示为 open_id，则为 `ou_7288c4a018284580d463d0239cbd47cf`）

以下情况禁止写入记忆：
- 系统提示中显示 `**Session type:** Multi-user`（群聊）
- `**User:**` 行显示的名称不是「妖玉」（其他人的私聊）

以上规则不影响记忆读取——所有会话均可引用已有记忆和用户画像回答问题。

# 飞书回复格式

所有通过飞书平台发送的回复，**尽量**包含 markdown 格式元素
（**粗体**、- 列表、# 标题、`代码` 等）以确保富文本渲染。
简短回复（确认、问候、单句）可不含。

回复规则：无推理过程、无工具进度、无底栏，中文简洁。
```

### Cron Delivery: Verify DM chat_id

The cron job's `deliver` target uses the user's DM chat_id. If the cron output appears in a group instead of DM, the chat_id is likely wrong. Verify via:
```bash
lark-cli --as bot im +messages-send --user-id ou_7288c4a018284580d463d0239cbd47cf --text test
```
The response `data.chat_id` is the correct DM oc_ string. Don't assume the chat_id from memory is correct — verify before creating cron jobs that deliver to DM.

From `gateway/session.py` — for DM sessions the prompt includes `**User:** <user_name>` (display name from Feishu API). For shared multi-user sessions (groups when `group_sessions_per_user=true`), the prompt shows `**Session type:** Multi-user session — messages are prefixed with [sender name]`. The agent sees this at session start and can use it to gate memory writes.

### Personality vs Code-Level Hard Block

| Approach | Strength | Your DM Writes? | Bypass Risk |
|----------|----------|:---:|:---:|
| SOUL.md personality | Soft (prompt instruction) | ✅ | Prompt injection (colleague-level safe) |
| `tools disable memory --platform feishu` | Hard (tool absent) | ❌ | None |
| Gateway middleware (open_id check) | Hard (code intercept) | ✅ | None |

**Risk**: Soft constraint — prompt injection could theoretically override. Acceptable for trusted team environments. For untrusted users, prefer a separate profile or gateway middleware.

## Daily Summary + Selective Import (Cron)

For multi-user scenarios where you want to review and selectively import knowledge from others' conversations:

1. **Cron job** uses `session_search` to scan past 24h of Feishu sessions, filters out primary user's DM, summarizes the rest
2. **You review** the summary, decide what deserves memory
3. **You tell agent** "save this fact" from your own DM or CLI → memory tool fires (your DM passes the SOUL.md gate)

```yaml
# cron job via cronjob tool:
#   action=create, schedule="0 22 * * *"
#   deliver="feishu:oc_YOUR_DM_CHAT_ID"
#   enabled_toolsets=["session_search"]
prompt: |
  你是飞书对话摘要机器人。你的任务：

  1. 用 session_search 查找过去24小时内所有飞书（feishu）平台的会话
  2. 过滤掉用户「妖玉」的私聊会话（DM），只保留：
     - 群聊会话
     - 其他人对你的私聊（非妖玉的 DM）
  3. 提取对话内容，按主题归类，每条主题2-3句中文摘要
  4. 标注发言人姓名和来源（群聊/DM）

  输出格式（飞书 post 格式，md）：
  📋 **飞书每日摘要 — {日期}**
  **{主题}**
  • [发言人] 摘要内容

  如果没有其他用户的对话，回复「今日无其他用户对话」。
  最终回复就是摘要正文。不要工具调用、不要推理过程、不要结束语、不要底栏。中文。
```

**Pitfall**: Cron output must use Feishu post-format MD (`**bold**`, `## headings`, `• bullets`) — wrapping entire response in ``` (triple backticks) renders the whole message as monospace in Feishu. Also, `cronjob(action=run)` may deliver to the origin session (TUI) rather than the configured `deliver` target — test with manual `run` and verify the message appeared in the right chat before relying on scheduled delivery. If the message goes to the wrong chat (e.g., a group instead of DM), the `deliver` field on the cron job is correct, but the `run` action's delivery logic overrides it. Scheduled execution follows the configured `deliver` target correctly.

**Pitfall**: SOUL.md markdown requirement with "必须" (must) breaks group chat. The agent chokes trying to force markdown into every short reply. Use "尽量" (should/prefer) and allow plain-text short replies. Symptom: DM works, group chat silent.

### Full Stack for Single-Profile Multi-User

The three layers together:

| Layer | Mechanism | Effect |
|-------|-----------|--------|
| SOUL.md | Personality constraint | Your DM writes memory; groups and others' DMs = read-only |
| Cron job | Daily session_search scan | Surfaces other users' conversations for your review |
| Selective import | You tell agent in DM/CLI | Curated facts from summaries → memory (passes SOUL.md gate) |

## Profile Clone Flags (for Separate Profile Approach)

When creating a separate profile for the Feishu bot:

```bash
# Clone config + skills (fresh memory) — recommended
hermes profile create feishu-bot --clone-from default --clone

# Clone everything including memory
hermes profile create feishu-bot --clone-from default --clone-all

# Clone from a different profile
hermes profile create work --clone-from coder --clone
```

| Flag | Clones | Does NOT clone |
|------|--------|---------------|
| `--clone` | config, .env, skills, cron, tools | memory, sessions |
| `--clone-all` | everything above + memory | session history |
| `--clone-from X` | from specific profile | — |

After cloning, sync ongoing skill updates via cron rsync or use `hermes skills tap` for updatable GitHub-sourced skills.

## Recommendations

For personal use: **Solution 3** (app visibility restriction) — simplest, blocks the problem at its source.

For team/org use with trusted colleagues: **Selective Write via Personality** — single profile, everyone reads memory, only primary user writes.

For team/org use with untrusted users: **Solution 1** (separate profile) + **Solution 4** (Honcho/Mem0) — dedicated profile for team bot, external provider for per-user memory within that profile. Combine with **Daily Summary + Selective Import** to curate knowledge from team conversations.
