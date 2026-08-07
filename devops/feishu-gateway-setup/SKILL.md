---
name: feishu-gateway-setup
description: "Configure Feishu (飞书) as a messaging platform in Hermes gateway — lark-cli installation, identity binding, auth, display formatting, and autonomous reply settings."
version: 1.6.0
tags: [feishu, lark, gateway, setup, display, messaging]
---

# Feishu Gateway Setup for Hermes

Complete workflow for setting up Feishu (飞书) as a messaging platform in Hermes gateway with clean, concise message formatting.

## Architecture

```
┌─────────────┐     WebSocket + REST      ┌──────────────┐
│   Hermes    │ ◄──────────────────────► │  飞书 API    │
│ adapter.py  │   bot-level operations    │              │
│             │   (消息/文档/评论/群组)    │              │
└─────────────┘                           └──────────────┘
                                             ▲
┌─────────────┐   OAuth user_access_token    │
│  lark-cli   │ ────────────────────────────┘
│  --as user  │   仅在需要「以用户身份」操作时使用
└─────────────┘   (发消息/日历/邮箱/个人文档)
```

**Hermes adapter.py** handles all bot-level Feishu operations natively — messages (WebSocket), docs, comments, groups. Does NOT depend on lark-cli, OpenClaw, or any lark-* skills.

lark-cli is a lightweight supplementary tool used ONLY when you need to operate as your user identity (send messages as yourself, access personal calendar/mail). lark-cli is NOT involved in bot messaging at all.

See `references/lark-cli-token-management.md` for token lifetimes, auto-refresh behavior, and required OAuth scopes.

## Document Operations

lark-cli can read and export Feishu documents without needing a browser login — use this when the user asks about content in their Feishu docs.

**Read a doc:** `lark-cli drive +inspect --url <url>` → get token + type
**Export for analysis:** `lark-cli drive +export --token <t> --doc-type docx --file-extension markdown --output-dir . --overwrite`

Full reading workflow and gotchas: `references/feishu-doc-reading.md`

**Edit/write a doc (block-level API):** Use `lark-cli api` to GET block structure, DELETE old blocks, POST new blocks — no browser needed. Covers block types (heading, bullet, text), link creation, and Python subprocess calling patterns.

Full editing workflow and pitfalls: `references/feishu-doc-editing.md`

**Enriching docs with external data**: When a Feishu doc contains links that don't preview (e.g. Bilibili space URLs), pull the data via public APIs to build structured content directly. For Bilibili-specific API access patterns (mobile UA bypass, Googlebot UA, WBI signing): `references/bilibili-api-access.md`.

**文档评论 @ bot**（右侧划词 / 底部全文评论）：Hermes 原生处理 `drive.notice.comment_add_v1` 事件（adapter → `plugins/platforms/feishu/feishu_comment.py`）。完整管线、访问控制三策略（allowlist/pairing/members）、评论会话机制见 `references/feishu-comment-pipeline.md`；2026-08-06 协作接入最终形态（collab 层/项目路由/角色分级/Obsidian 检索/权限边界/**kanban 已摘除归 AI**/升级覆盖文件清单）见 [`references/comment-collab-architecture.md`](references/comment-collab-architecture.md)。最高频坑：评论 @ bot 无反应 → gateway.log 找 `denied (policy=pairing, rule=top)` → **团队协作场景直接建 `feishu_comment_rules.json` 设 `policy: members`**（成员名单自动放行，新成员免维护）；单用户临时用 `python -m plugins.platforms.feishu.feishu_comment_rules pairing add <open_id>`（配对后无需重启 gateway，但被拒评论不会补处理，需用户重新 @ 一次）。⚠️ members 分支是代码——改代码必须重启 gateway，否则旧代码遇到 members 策略会误拒全员。

## Prerequisites

- Feishu app with Bot capability enabled (App ID + App Secret from https://open.feishu.cn)
- Hermes installed and running

## Step 1 — Install lark-cli (for OAuth only)

```bash
npm install -g @larksuite/cli
```

lark-cli is needed ONLY for user-level OAuth authorization (Steps 4-5). Hermes core (bot messaging, WebSocket, doc reading) uses its own built-in `adapter.py` — does NOT depend on lark-cli.

**Do NOT install lark-* skills or OpenClaw.** Hermes has built-in Feishu tools (`feishu_doc_tool.py`, `feishu_drive_tool.py`).

## Step 2 — Ask Identity

Present the user with two options:
- **以机器人身份** (bot-only) — robot identity, suitable for group chats and shared docs
- **以用户身份** (user-default) — user identity, requires OAuth authorization

Include this warning for user-default:
> **⚠️ 如果你选「以用户身份」：请勿将此机器人分享给他人或拉入群聊中使用 —— 它能访问你的个人飞书数据。**

## Step 3 — Configure .env

Add to `~/.hermes/.env`:
```
FEISHU_APP_ID=<app_id>
FEISHU_APP_SECRET=<app_secret>
FEISHU_CONNECTION_MODE=websocket
FEISHU_GROUP_POLICY=open
```

Note: `FEISHU_GROUP_POLICY=open` is REQUIRED for group messages to work. The feishu adapter reads this from env vars, NOT from config.yaml. Without it, all group messages are silently rejected.
The secret redaction feature may obscure displayed values — use `wc -c` to verify correct length instead of reading the value.

**切换应用时**：更换到新的飞书应用（如从商店应用切换到企业自建应用）时，必须在 `.env` 中更新 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`，然后重启 gateway。同时需要重新执行 Step 4（bind）和 Step 5（auth login），因为 strict-mode 和 token 都与旧应用绑定。

**企业自建应用 vs 商店应用**：企业自建应用权限更高——管理员直接在后台勾选开通 scope，无需飞书官方审核。权限池也更大（通讯录批量读、部门管理等商店应用拿不到的权限）。切换时在开发者后台开通 scope 这一步远比商店应用快。

**完整迁移清单**：从旧应用切换到新应用涉及 10 个步骤（含 cron job 批量更新、bot 权限清单等），详见 `references/app-migration.md`。

## Step 4 — Bind Identity

```bash
lark-cli config bind --identity <bot-only|user-default>
```

If multi-account error: show candidates from `error.hint`, let user pick, then:
```bash
lark-cli config bind --identity <IDENTITY> --app-id <chosen_app_id>
```

**⚠️ `bot-only` bind 的副作用**：`bot-only` 绑定会自动将 strict-mode 设为 `bot`，此后 Step 5 的 `auth login` 会报错 `"strict mode is \"bot\", only bot-identity commands are available"`。如果你需要 user 身份，必须在 Step 5 之前执行：

```bash
lark-cli config strict-mode off
```

切换到 `off` 后 bot 和 user 两种身份均可使用。`user-default` bind 不受此影响。

## Step 5 — Auth Login (user-default only)

Skip for bot-only.

First call — get auth URL with required scopes:
```bash
lark-cli auth login --recommend --scope "im:message.send_as_user" --no-wait --json
```

**⚠️ `im:message.send_as_user` must be explicitly requested.** The `--recommend` flag alone does NOT include it. Without this scope, `lark-cli --as user im +messages-send` fails with `missing_scope`.
Extract `verification_url` from JSON output. Send to user as markdown autolink: `<https://...>`.
**Never** open the URL yourself (sandbox browser can't complete auth).
Save `device_code` for next step.

After user confirms authorization:
```bash
lark-cli auth login --device-code <device_code>
```

See `references/lark-cli-oauth-lifecycle.md` for token lifetime, auto-refresh mechanism, and the reminder cron setup.

## Step 6 — Verify

```bash
lark-cli auth status
```

Check: `identity` matches, `tokenStatus` is `valid` or `needs_refresh` (not `expired`).

## Step 7 — Enable Gateway Platform

```bash
hermes config set platforms.feishu.enabled true
pip install websockets   # required for websocket mode
```

## Step 8 — Clean Display Format (CRITICAL)

**The user prefers clean, OpenClaw-like responses — no tool progress, no reasoning, no footer.**

```bash
hermes config set display.platforms.feishu.tool_progress false
hermes config set display.platforms.feishu.interim_assistant_messages false
hermes config set display.platforms.feishu.show_reasoning false
hermes config set display.platforms.feishu.require_mention true
hermes config set display.platforms.feishu.system_prompt "始终使用中文回复。简洁直接，不要冗长。"
```

Runtime footer is global; disable it:
```bash
hermes config set display.runtime_footer.enabled false
```

## Step 9 — Autonomous Reply in Specific Groups

**CRITICAL**: `free_response_channels` does NOT work for the Feishu platform. Use `group_rules` instead.

### 9a — Bridge `group_rules` in gateway/config.py (APPLIED 2026-07-15)

The feishu adapter reads per-group rules from `extra.get("group_rules")`, but the config bridge does not forward `group_rules`. This fix was applied on 2026-07-15. If upgrading Hermes, verify the bridge is still present. Add to `~/.hermes/hermes-agent/gateway/config.py`, after the `group_user_allowed_commands` bridge:

```python
if "group_rules" in platform_cfg:
    bridged["group_rules"] = platform_cfg["group_rules"]
```

Without this fix, `hermes config set platforms.feishu.group_rules.oc_XXX.require_mention false` has NO effect — the adapter never sees the setting and always falls back to the global `require_mention`.

### 9b — Set per-group rules

For groups that should get free responses (no @mention needed):

```bash
hermes config set platforms.feishu.group_rules.oc_CHAT_ID.require_mention false
hermes config set platforms.feishu.require_mention true    # other groups still need @
```

For per-channel prompts:
```bash
hermes config set platforms.feishu.channel_prompts.oc_CHAT_ID "始终使用中文回复，简洁直接。"
```

### Why `free_response_channels` doesn't work on Feishu

The Feishu platform adapter reads its per-group rules from `extra.get("group_rules")`, not from `free_response_channels`. The `free_response_channels` value **is** bridged to the platform config (gateway/config.py line 1207-1208) but is never processed into group rules by the feishu adapter (zero references to `free_response_channels` in adapter.py). This is different from Discord/Slack where `free_response_channels` is explicitly handled.

## Step 10 — Markdown Rendering

Messages are sent as `post` type (markdown-capable) ONLY when they contain markdown syntax. Plain-text messages are sent as `text` type (no rendering). The gateway's `_build_outbound_payload` uses `_MARKDOWN_HINT_RE` to detect markdown (headings, lists, bold, links, code fences, etc.) — if no markdown syntax is present, the message degrades to plain text.

**Workaround**: Add a per-platform system prompt that instructs the agent to use markdown (see below). See `references/markdown-rendering-fix.md` for the full code analysis and trigger patterns.

### System prompt format requirement (THE ACTUAL WORKING METHOD)

**⚠️ `~/.hermes/SOUL.md` is NOT loaded by Hermes** (verified 2026-07-02: zero references in hermes-agent source code). The correct way to inject format instructions is the per-platform system prompt:

```bash
hermes config set display.platforms.feishu.system_prompt "始终使用中文回复。简洁直接，不要冗长。回复尽量包含 markdown 格式元素（**粗体**、- 列表、## 标题等）。无推理过程、无工具进度、无底栏。"
hermes gateway restart
```

This is already set up in Step 8. Verify with `hermes config show` (check display.platforms.feishu.system_prompt). No separate file needed.

### Verified working (tested 2026-06-24)

| Feature | Status |
|---------|--------|
| Bold, italic, strikethrough | ✅ |
| Links (inline + in tables) | ✅ |
| Headings, lists, blockquotes | ✅ |
| Tables (3+ columns, links in cells) | ✅ (fixed 2026-07-10 — _MARKDOWN_TABLE_RE force-text block removed from _build_outbound_payload in adapter.py) |
| Code blocks (fenced, with language) | ✅ |
| Inline code | ✅ |
| Multi-paragraph messages | ✅ (after `_build_markdown_post_rows` fix — see `references/markdown-rendering-fix.md`) |
| Columns / multi-column layout | ❌ (need card messages) |
| Buttons / interactive elements | ❌ (need card messages) |

### Strategy

- **Normal messages**: post+md — covers all standard Markdown
- **Interactive needs** (buttons, multi-column): fall back to Feishu card messages
- Transition trigger: auto-detect when post+md can't express the required component

### Pitfall: entire message in code block

If the assistant wraps the entire response in ``` (triple backticks), Feishu renders the WHOLE message in monospace. Instead:
- Use `##` headings, `-` bullets, `**bold**` for structure — these render correctly in Feishu post format
- Only use ``` for actual code snippets within the message
- Never put structure/headings inside code fences

## Step 11 — Set Home Channel & Restart

In the Feishu DM/group, send `/sethome` to set the home channel. Then:

```bash
hermes gateway restart
```

### ⚠️ 反复提示「No home channel is set for Feishu」= home_channel 位置迁移坑（实测 2026-08-06）

**症状**：用户已发过 `/sethome`、cron 推送也正常，但飞书每个新会话第一条消息仍收到「📬 No home channel is set for Feishu」提示。

**根因**：主频道配置位置迁移未完成——旧版写 `gateway.home_channel`（裸 chat_id 字符串，`hermes config set gateway.home_channel <chat_id>`），当前版本代码只读 `platforms.<platform>.home_channel`（HomeChannel dict：platform/chat_id/name/user_id/thread_id）。旧值躺在废弃位置，读取端永远读不到。

代码位置：`gateway/run.py`（触发条件：非本地/非webhook 平台 + 新会话第一条消息 `not history`）→ `gateway/config.py:1022 get_home_channel()` 只读 `platforms.<p>.home_channel`。写入端 `/sethome` → `persist_home_channel()`（config.py:466）写 `platforms.<p>.home_channel`。

**「在用」的假象**：cron 投递走显式 deliver 目标（`feishu:oc_xxx`），不依赖 home_channel，所以日常推送正常——只有新会话检查每次误判。

**排查**：`grep -n -A 6 "home_channel" config.yaml`——若 `platforms.feishu.home_channel` 缺失、只有 `gateway.home_channel`，即命中此坑。

**修复**：目标聊天重新发 `/sethome`（写入位置与 chat_id 自动正确），验证 `get_home_channel` 可读，`hermes gateway restart`。

Wait ~10s, verify connection:
```bash
# Use hermes config path to find logs portably (avoids ~/.hermes/logs which doesn't exist on Windows GUI installs)
LOG_DIR="$(dirname "$(hermes config path)")/logs"
grep "feishu connected" "$LOG_DIR/gateway.log" | tail -1
```

## Step 12 — Multi-User Memory Isolation (CRITICAL)

If the Feishu bot is added to group chats or open to DMs from multiple users, **built-in memory (MEMORY.md + USER.md) is SHARED across all users of the same profile**. Sessions are isolated per user, but memory is profile-level — a memory saved during another user's conversation will appear in your sessions too.

**⚠️ SOUL.md personality gating does NOT work.** `~/.hermes/SOUL.md` is not loaded by Hermes (zero references in source code, verified 2026-07-02). The "Selective Write via SOUL.md" approach documented in `references/multi-user-memory-isolation.md` is invalid.

### Working solutions (ranked)

1. **Restrict bot visibility** — In Feishu Developer Console → Security Settings, set visibility to "仅应用管理员可见". Blocks at the source. Zero code changes.

2. **Disable memory toolset on feishu** — Hard block, your own feishu DM also can't write:
   ```bash
   hermes tools disable memory --platform feishu
   hermes gateway restart
   ```

3. **`agent.system_prompt` (soft, universal)** — Inject memory write rules into ALL sessions via config.yaml. Agent sees `**User:**` / `**Session type:**` from `build_session_context_prompt()` and gates writes:
   ```bash
   hermes config set agent.system_prompt "# 记忆写入规则\n\n仅当系统提示中「**User:**」行显示为「妖玉」且「**Session type:**」不包含 Multi-user 时，方可调用 memory 工具写入记忆。其他用户或群聊均禁止写入。\n\n记忆读取不受此限制——所有会话均可引用已有记忆和用户画像。"
   hermes gateway stop && hermes gateway start
   ```
   **How it works**: `_load_ephemeral_system_prompt()` in `gateway/run.py` reads `agent.system_prompt` → combined with session context from `build_session_context_prompt()` (which includes `**User:** 妖玉` or `**Session type:** Multi-user session`) → injected as `ephemeral_system_prompt` into AIAgent. Universal across all platforms, not just feishu.

4. **`display.platforms.feishu.system_prompt` (soft, feishu-only)** — Same personality approach but scoped to feishu platform only. Set via Step 8 command. Less universal than `agent.system_prompt`.

5. **Separate profile** — `hermes profile create feishu-bot --clone-from default --clone`. Complete isolation.

Full breakdown of all strategies: `references/multi-user-memory-isolation.md`

## Pitfalls

- **⚠️ 查询类 CLI 命令也可能误杀 gateway（实测 2026-08-07 两次）**：`hermes gateway status` / `hermes cron list` 在「上次 hermes update 中断」残留时，会触发自动恢复流程（pip install），cryptography 因文件被运行中进程占用报 `os error 5 拒绝访问`，随后 gateway 以 `signal=UNKNOWN` 的「planned gateway stop」退出——**跑一个只读查询命令就把 gateway 弄停了**。**排查**：执行 hermes CLI 命令后顺手 `tail -3 gateway.log` 看是否出现 `Gateway stopped`。**根治**：关闭所有 Hermes 窗口后在终端跑 `cd hermes-agent && venv/Scripts/python.exe -m pip install -e ".[all]"`。**自愈**：gateway 不会自动重启，需外置 watchdog（见 `references/self-healing-watchdog.md`）。
- **⚠️ 飞书突然全部不回消息 = 先查 gateway 进程是否活着（实测 2026-08-07）**：飞书所有会话集体无响应时，第一排查是 gateway 进程本身已退出——`hermes gateway status` 看进程状态，`tail -20 <LOG_DIR>/gateway.log` 看最后一行。实测 gateway 在 10:56 静默退出（日志 `Received UNKNOWN as a planned gateway stop — exiting cleanly`）后**不会自动重启**，飞书消息堆积数小时无人处理，期间 adapter/配置全正常。常见诱因：中断的 `hermes update`。恢复：`hermes gateway status` 会自动触发中断安装的恢复流程（可能因 cryptography 文件被运行中进程占用报 `os error 5 拒绝访问`——不影响启动，收尾需关掉所有 Hermes 窗口后在终端跑 `cd hermes-agent && venv/Scripts/python.exe -m pip install -e ".[all]"`）；起来后确认日志 `✓ feishu connected`（websocket 模式）即恢复。排查顺序铁律：**先进程，后日志，再配置**——不要一上来改适配器/渠道配置。**停机期间用户发的消息不会自动补推**——手动拉回流程（`+chat-messages-list --start/--end`、字段 `data.messages` 非 `data.items`、bot 身份限制、230002 判定）见 `references/gateway-outage-message-recovery.md`。
- **⚠️ 渠道兜底模型 = 全局 fallback_providers，所有渠道统一继承（实测 2026-08-07）**：gateway 创建 agent 时对所有渠道传同一个兜底链（gateway/run.py `_refresh_fallback_model()`），`platforms.feishu.model`/`provider` 渠道覆盖**不影响**兜底链——飞书无需单独配 fallback。**`fallback_active: false`（state.db sessions.model_config.gateway_runtime）是正常状态**：只表示主模型从未「重试耗尽」，不代表兜底链没装。deepseek 日常抖动（APIConnectionError）大多被 `api_max_retries: 3` 重试救回（agent.log 只有 `attempt 1/3` → Retrying），真正切兜底要 `attempt 3/3` 仍失败。验证兜底是否生效：`grep 'API call failed' agent.log` 看 attempt 级别——只有 1/3 = 重试救回无需动作；出现 3/3 后应跟 fallback 切换日志。配置注意：①fallback 条目缺 `model` 字段会被 `_iter_fallback_entries` **静默过滤**（不报错不生效）；②兜底链里与主 provider 相同的条目（deepseek→deepseek）在 provider 整体宕机时是废条目——真兜底必须看不同 provider（如 xiaomi）。
- **⚠️ 飞书视觉模型健康检查（实测 2026-08-07）**：用户问「飞书视觉还好吗」= 查 auxiliary.vision（全局配置，xiaomi/mimo-v2.5，独立于 deepseek 主链路——deepseek 抖动不影响看图）。快速验证：跑 `scripts/vision-health-probe.py`（构建 client + 1x1 PNG data URL 推理）。坑：reasoning 模型（mimo-v2.5）在 max_tokens=20 时返回**空 content**（推理 token 吃掉预算，实测 34 reasoning tokens / 20 预算），探针必须 max_tokens≥200。
- **⚠️ 文档评论 @ bot 无回复 = 默认 pairing 配对制拦截（实测 2026-08-06）**：Hermes feishu adapter 原生支持文档评论回复（订阅 `drive.notice.comment_add_v1`，处理在 `plugins/platforms/feishu/feishu_comment.py`：解析→加 OK reaction→拉文档元数据+评论详情→按 `is_whole` 分支→AIAgent 生成回复→whole 全文评论用 add_comment 底部追加、local 局部评论用 reply_to_comment）。**但访问控制默认 `policy=pairing`**：`feishu_comment_rules.json` 与配对文件都不存在时，所有用户被拒——gateway.log 标志性日志 `[Feishu-Comment] User ou_xxx denied (policy=pairing, rule=top)`。**排查**：`grep -i comment <LOG_DIR>/gateway.log | tail`。**修复**：`cd ~/AppData/Local/hermes/hermes-agent && ./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules pairing add <open_id>`；规则/配对文件 mtime 热加载，**无需重启 gateway**。**验证**：`... feishu_comment_rules status`（看配对名单）；`... check <fileType:fileToken> <open_id>`（模拟访问检查，Result: ALLOWED）。事件过滤要点：`to_open_id` 必须等于 bot open_id（评论里 @ bot 才触发，没 @ 直接跳过）；`from==self` 跳过；notice_type 限 `add_comment`/`add_reply`；**被拒的评论不会事后补处理**——修复后需用户重新 @ 一次。规则文件三层覆盖（exact 文档 > wildcard `*` > top-level），enabled/policy/allow_from 三字段独立回退，支持 `allowlist` 或 `pairing` 两种策略。
- **⚠️ 飞书会话人显示三层链路（实测 2026-08-06）**：回答「Hermes 能显示飞书会话人吗」——agent 上下文 `**User:**` 行 ✅（依赖 contact:user.base:readonly，adapter.py:4174 反查）；state.db sessions.display_name ⚠️（写入用 source.chat_name 而非 user_name，session.py:1821，**私聊落 chat_id 不是真名**，历史不回填）；桌面端 UI ❌（侧边栏只显示 AI 标题 sessionTitle，聊天区不标发送人）。完整诊断模型+代码位置+排查命令见 `references/feishu-sender-display-layers.md`。
- **⚠️ 反复提示「No home channel is set for Feishu」= home_channel 配置位置迁移（实测 2026-08-06）**：用户在飞书里设过主频道、cron 推送也正常，但每个新会话第一条消息仍弹「📬 No home channel is set for Feishu」。**根因**：版本升级后 home_channel 读取位置迁移——旧版写 `gateway.home_channel`（裸 chat_id 字符串，已不被读取），新版只读 `platforms.<platform>.home_channel`（HomeChannel dict：platform/chat_id/name/thread_id/user_id/scope_id）。旧值不会自动迁移。**为什么「在用」却提示**：cron 投递走显式 deliver 目标（feishu:oc_xxx），不依赖 home_channel 字段，所以日常推送不受影响，只有新会话检查误判。**排查**：`grep -A 30 "^  feishu:" config.yaml` 看 `platforms.feishu.home_channel` 是否存在（旧值可能躺在 `gateway.home_channel` 下）；`.env` 的 `FEISHU_HOME_CHANNEL` 需为未注释状态。**修复**：在目标聊天重新发 `/sethome`（写入新位置，chat_id 自动正确），或手动写入 `platforms.feishu.home_channel`（HomeChannel dict 格式）。**代码位置**：读取端 run.py:17227（`not history` 时检查）→ gateway/config.py:1022 `get_home_channel`；写入端 slash_commands.py:2843 `_handle_set_home_command` → config.py:466 `persist_home_channel`。
- **⚠️ Sender 真名解析依赖 `contact:user.base:readonly` 权限（实测 2026-08-05）**：feishu adapter 的 `_resolve_sender_name_from_api`（adapter.py:4174）用 `contact.v3.user.get` 解析发送者姓名，注入会话上下文 `**User:** <name>` 行。**权限未开通时该调用静默失败**（返回 None，日志仅 debug 级），`sessions.display_name` 落的是 chat_id 而非真名，会话里 `**User:**` 行缺失。开通链接格式：`https://open.feishu.cn/page/scope-apply?clientID=<appId>&scopes=contact:user.base:readonly`（企业自建应用后台勾选即生效，无需审核）。验证：`lark-cli contact +get-user --user-id ou_xxx --as bot` 返回的 `data.user.name` 非空即生效。**注意**：user 身份即使没开此权限也能用 `+search-user --user-ids` 反查姓名（依赖 `contact:user:search`），但按「应用权限优先」原则优先开 bot 权限。权限开通后需 `hermes gateway restart` 生效；历史会话 display_name 不回填，只有新消息触发解析。
- **⚠️ Windows 下 Python subprocess 调 lark-cli 必须用 .cmd**：`lark-cli` 在 `~/AppData/Local/hermes/node/` 下是 POSIX sh 脚本，Windows Python 的 `CreateProcess` 无法直接执行（FileNotFoundError）。脚本里用 `shutil.which("lark-cli.cmd")` 或显式路径 `.../node/lark-cli.cmd`。
- **换应用后 user openId 会变，cron 排除条件同步失效**：摘要类 cron 若硬编码排除「自己」的 openId，应用迁移后自己的会话会被当成「其他人对话」混入摘要。当前妖玉 openId：`ou_68719743e59a5576420e32bb2ea024e1`（`lark-cli auth status --json --verify` 的 `identities.user.openId`）。排查/修复时同时检查所有硬编码 openId 的 cron/脚本。
- **⚠️ 「用户+N」格式姓名的根因判断（实测 2026-08-05）**：bot 反查返回 `用户133976` 这类脱敏名时，先对照 IM 群成员列表（`im +chat-members-list --as bot`）——如果 IM 显示名也是「用户+N」，说明是**该账号资料本身未设置姓名**（飞书默认名），不是权限/可见性问题（可用范围所有员工也无效）。此时 user 身份 `+search-user` 的 `localized_name` 字段可能有真名（如魏宁馨），但 bot 可用的 `contact.v3.user.get` 只返回 `name` 字段；search 接口和 `user_profiles batch_query` 均不支持 bot 身份。判断链：①对照 IM 显示名 → ②看其他成员是否正常（正常则排除全局权限问题）→ ③确认该账号 name 字段为系统默认。处理：让该用户补全飞书资料即自然恢复，脚本保持「拿到什么显示什么」不误标。
- **Don't use browser to access Feishu docs**: Feishu doc URLs redirect to a login page in CDP/headless browsers (captcha + QR code). The agent cannot complete this login. Use `lark-cli drive +export` (see Document Operations above and `references/feishu-doc-reading.md`) instead — it uses existing OAuth tokens and works instantly.
- **⚠️ 飞书 open_id → 真名解析：bot 身份拿不到 name，user 身份可以（实测 2026-08-05）**：Hermes feishu adapter 自带发送者真名解析（`plugins/platforms/feishu/adapter.py` `_resolve_sender_name_from_api`，调 `contact.v3.user.get`，缓存于 `_sender_name_cache`），但应用未开通通讯录权限（`contact:user.base:readonly`）时，bot 身份调用只返回 open_id/union_id、**无 name 字段**，解析静默失败——`state.db` 的 `sessions.display_name` 回退为 chat_id（DM）或群名（group）。需要真名时用 **user 身份**批量反查：`lark-cli contact +search-user --user-ids ou_1,ou_2 --as user`（返回 `localized_name`，实测稳定可用）。典型症状：摘要类 cron 从 `state.db` sessions 表只 SELECT `user_id`（=open_id），LLM 无真名可用，输出「用户 A/B/C/D」。修复：cron 脚本加一步 user 身份批量反查 open_id→真名，再喂给 LLM。根治：开发者后台给应用开 `contact:user.base:readonly`（仅企业自建应用可开）。详见 `references/feishu-user-name-resolution.md`。
- **⚠️ bot 反查返回「用户+N」脱敏名 = 账号资料问题，不是权限问题（实测 2026-08-05）**：即使 `contact:user.base:readonly` 已开通、应用可用范围=所有员工，个别用户 bot 身份 `+get-user` 仍返回 `name: "用户133976"` 这类默认名。根因：该用户飞书账号的 `name` 字段本身未设置/资料不完整，真名存在 `localized_name`（本地化名称）字段。**判别链**：①同群其他成员 bot 全部正常、唯独此人「用户+N」→ 非权限问题；②user 身份 `+search-user --user-ids <ou_>` 返回 `localized_name: "魏宁馨"` 而 bot 的 `+get-user` 返回 `name: "用户133976"` → 字段差异实锤。**关键事实**：`localized_name` 只有 `contact/search/user` 接口返回，该接口**仅 user 身份可用**（`--as bot is not supported, this command only supports: user`）；原生批量接口 `contact/v3/users/batch_get`、`/users/batch` 均 404 不存在；`user_profiles batch_query` 同样仅 user 身份。**修复**：让该用户补全飞书姓名资料（治本）；脚本对「用户+N」降级处理——不误标真名，保持原名（治标）。
- **群成员列表是批量姓名映射的替代数据源（bot 身份可用）**：`lark-cli im +chat-members-list --chat-id <oc_> --as bot` 一次性返回群内全部成员真名 + open_id（`users[].name`、`users[].member_id`，含 `bot_total`），无需逐个 `+get-user` 反查。摘要 cron 若需批量显示群成员姓名，优先用此接口建映射表；「用户+N」成员同样暴露资料不完整问题，与 `+get-user` 结果一致。群名（如「开工」）是 group 的 chat_name，与会话 `display_name` 落群名一致。
- **⚠️ FEISHU_GROUP_POLICY IS AN ENV VAR, NOT CONFIG**: The feishu adapter reads `FEISHU_GROUP_POLICY` from environment variables (default: `"allowlist"`) at line 1527 of `adapter.py`, NOT from `platforms.feishu.group_policy` in config.yaml. If this env var is not set to `"open"`, ALL group messages are silently rejected with the rejection reason `"group_policy_rejected"`. This was the root cause of "群里不回消息" after all other settings were correct. Fix: `echo "FEISHU_GROUP_POLICY=open" >> ~/.hermes/.env` then restart gateway. Even if `platforms.feishu.group_policy: open` is in config.yaml, the code ignores it.
- **config.yaml NOT .env**: `hermes config set` writes to config.yaml. For env vars (FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_GROUP_POLICY), manually write to .env via terminal.
- **Secret redaction**: The security.redact_secrets feature obscures displayed secret values. Use character count (`wc -c`) to verify correctness instead of reading values.
- **Gateway restart timing**: `hermes gateway restart` may report "no process detected after 6s" — this is often a false alarm; check logs for actual connection.
- **WS disconnected after restart**: The gateway cleanly disconnects and reconnects; the old session in Feishu may show "disconnected" briefly. Wait 10-15s.
- **`final_response_markdown` is CLI-only**: The `display.final_response_markdown` config setting (`render` / `strip` / `raw`) only affects the CLI/TUI terminal output, NOT the gateway. Changing it will have zero effect on Feishu message formatting. If Feishu messages aren't rendering Markdown, the issue is in the Feishu adapter's `_build_outbound_payload`, not this config setting.
- **Config changes need restart**: Any platform or display config changes require `hermes gateway restart` to take effect.
- **`hermes config unset` does not exist**: Hermes CLI has no `unset` subcommand. To remove a config key (e.g. `channel_overrides`), edit `config.yaml` directly via Python `yaml.safe_load`/`yaml.dump`. The `patch` tool also refuses to write to `config.yaml` — use terminal Python as the workaround for both.
- **Gateway restart/stop may timeout**: `hermes gateway stop` and `hermes gateway restart` can hang for 30s+ when the gateway process is stuck (e.g., agent in infinite API wait). Force-kill: `powershell.exe -Command "Stop-Process -Id <PID> -Force"` then `hermes gateway start`.
- **pip 安装到错误的 Python 环境**：系统有两个 Python——系统 Python 3.12（`C:\Users\HMSJ\AppData\Local\Programs\Python\Python312\`）和 Hermes venv Python 3.11（`C:\Users\HMSJ\AppData\Local\hermes\hermes-agent\venv\`）。`which pip` 指向系统 Python 的 pip，但 Hermes gateway 使用 venv。直接 `pip install` 会装到系统 Python，gateway 看不到。**正确做法**：用 venv 的 python.exe -m pip 安装——`/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pip install <package>`。安装后用 venv 的 python 验证版本：`venv/Scripts/python.exe -c "import importlib.metadata; print(importlib.metadata.version('<package>'))"`。
- **lark-oapi SDK 版本**：当前使用 lark-oapi（飞书官方 Python SDK）。检查版本：`/c/Users/HMSJ/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "import importlib.metadata; print(importlib.metadata.version('lark-oapi'))"`。更新时必须用 venv 的 pip（见上条）。GitHub 无 CHANGELOG，版本对比用 `https://github.com/larksuite/oapi-sdk-python/compare/vX.Y.Z...vA.B.C`。
- **`LOG_LEVEL=DEBUG` in .env does NOT affect gateway**: The gateway's log verbosity is controlled by CLI flags (`-v`/`-vv` on `hermes gateway run`), not environment variables. To debug feishu message admission/dropping: stop background service → `hermes gateway run -vv --force 2>&1` → trigger the issue → inspect stderr output. The log file only records INFO and above during normal `hermes gateway start` runs.
- **`free_response_channels` doesn't work on Feishu**: The feishu adapter reads per-group rules from `platforms.feishu.group_rules`, NOT from `free_response_channels`. Use `hermes config set platforms.feishu.group_rules.<chat_id>.require_mention false` instead. This was discovered via source-code inspection of `adapter.py:_admit()` and `_require_mention_for()` — they use `self._group_rules` (populated from `extra.get("group_rules")`), never from `free_response_channels`.
- **`group_rules` bridge (FIXED 2026-07-15)**: `gateway/config.py` bridge 函数漏掉了 `group_rules` 的转发，导致 config.yaml 中 `platforms.feishu.group_rules.<chat_id>.require_mention: false` 永远传不到 adapter。adapter 只能用全局 `require_mention: true`，所有群消息（含话题回复）没 @ 都被拒。修复：在 bridge 函数 `group_user_allowed_commands` 块后添加 `if "group_rules" in platform_cfg: bridged["group_rules"] = platform_cfg["group_rules"]`。如果此问题复现，检查 config.py 是否有这行 bridge。
- **Feishu sessions hidden from Desktop sidebar**: The Desktop GUI's session list in `cli.py:_list_recent_sessions` hardcodes `source="cli"` and `include_all_sources=False`, which hides all gateway-originated sessions (including feishu) from the sidebar and `/sessions` slash command. Fix: change to `include_all_sources=True` and remove the `source="cli"` filter. After this fix, `/sessions` shows all sessions including feishu ones. The Desktop sidebar's "Messaging" section (fed by `refreshMessagingSessions()` in `desktop-controller.tsx`) already includes feishu but in a separate collapsed section — users may need to expand it.
- **Audio sending via lark-cli**: The `--audio` flag rejects WAV files with "file type
  does not match the type of message being sent" (code 230055). Use `--file` instead
  to send audio as a downloadable file attachment. The recipient can click to play.
- **飞书不支持原生语音气泡**：`msg_type="audio"` 本质是文件附件（带播放按钮的音频文件），不是 Telegram/Discord 那种内联语音条。这是平台限制，非 Hermes 问题。详见 `references/voice-audio-capabilities.md`。
- **Bot can't DM users**: If the bot hasn't been added to a user's P2P chat,
  sending via `--as bot --chat-id <p2p_chat_id>` fails with "Bot/User can NOT be
  out of the chat" (code 230002). The user must initiate the DM first, or use
  `--as user` (requires `im:message.send_as_user` scope).
- **⚠️ `oc_` 开头不一定是群聊**：bot 与用户的 p2p 私聊会话 chat_id 同样以 `oc_` 开头（用户纠正过"cron 不是发到群聊，是私发给我自己"）。区分方法：`lark-cli im +chat-list --types=p2p --as user`，看 `p2p_target_type: bot` + `name`（常为应用名）。bot 身份无法列 p2p 会话（隐私保护，报 invalid_argument），必须用 user 身份。`chats get` 对 p2p 返回的 `bot_count: 0` 不可靠，不能据此判断 bot 不在会话里——实测发送为准。
- **Cron 投递 230002 系统诊断链（实测 2026-08-04）**：cron job 报 `[230002] Bot/User can NOT be out of the chat` 时，别假设会话坏了，按序排查：
  1. **实测会话**：`lark-cli im +messages-send --chat-id <oc_> --as bot --msg-type text --text "test"`。能发 = 会话与 bot 都正常，问题在投递侧配置或凭据窗口期。
  2. **查凭据**：`grep -c "^FEISHU_APP_ID" ~/AppData/Local/hermes/.env` 确认是否新旧凭据并存（应=1）；`lark-cli auth status --json --verify` 对比 appId 一致。
  3. **对时间线**：`grep "230002" <logdir>/errors.log` 看失败时刻 vs user token `grantedAt`（auth status 输出）。应用迁移窗口期内旧凭据会导致整批 job 失败，迁移收尾重新授权后自愈——失败是历史窗口期，无需改配置。
  4. **验证恢复**：`cronjob(action=run)` 手动触发一个轻量 job（如 token 检查），返回里 `last_delivery_error: null` 即恢复；历史 job 的旧错误记录会在下次自动运行时刷新。注意 `cronjob run` 可能投递到 origin session，以 errors.log 是否新增 230002 为准。
- **⚠️ `bot-only` bind 锁定 strict-mode 导致 auth login 失败**：`lark-cli config bind --identity bot-only` 会自动将 strict-mode 设为 `bot`，此后 `auth login` 报错 `"strict mode is \"bot\", only bot-identity commands are available"`。**症状**：`auth login --no-wait --json` 返回 `failed_precondition` 而非 `verification_url`。**修复**：`lark-cli config strict-mode off` 后再执行 auth login。`user-default` bind 不受此影响。Step 4 已包含此警告。
- **⚠️ 换应用后 user openId 会变**：每个应用下同一用户有不同的 openId。换到新应用后，旧 openId（如 `ou_7288...`）会变成新的（如 `ou_6871...`）。**影响范围**：cron job 的 `deliver` 目标、`lark-cli --user-id` 参数、`channel_overrides` 中使用的 openId 都需要更新。**排查命令**：`lark-cli auth status --json --verify | grep openId` 查看新旧 openId。
- **⚠️ 换应用后需重新 /sethome**：home_channel 绑定到应用实例，不是永久绑定到群。切换到新应用后，即使群没变，也必须在群里重新发 `/sethome` 才能让 gateway 知道 home channel。
- **切换飞书应用需同时更新 lark-cli 和 .env**：更换 App ID/Secret 时，两步缺一不可：(1) `echo "<secret>" | lark-cli config init --app-id <id> --app-secret-stdin --brand feishu --force-init` 更新 lark-cli 配置；(2) 更新 `~/.hermes/.env` 中的 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`。仅更新一侧会导致 gateway 和 lark-cli 使用不同应用的凭据。更新后需重新 bind（Step 4）和 auth login（Step 5）。

- **⚠️ .env 中旧凭据需手动清理**：用 `>>` 追加新凭据到 `.env` 时，旧凭据不会自动移除，导致新旧两套 `FEISHU_APP_ID`/`FEISHU_APP_SECRET` 并存。gateway 读取环境变量时取决于变量定义顺序（通常取最后定义的值），但显式清理更安全。**清理命令**：用 Python 删除旧凭据行后重写文件（`.env` 受 write_file 保护，必须用 terminal python）。
- **`im:message.send_as_user` scope not included by default**: The `--recommend` flag in
  `lark-cli auth login` does NOT request this scope. Must add `--scope "im:message.send_as_user"`.
  Symptom: `lark-cli --as user im +messages-send` fails with error `missing_scope`.
  Fix: re-run OAuth with the scope flag, get a new verification URL, scan QR, poll the device code.
- **Multi-user memory leakage**: Built-in MEMORY.md/USER.md are profile-level — shared by all Feishu users who talk to the same bot on the same profile. Sessions are isolated, memory is NOT. Fix: separate profile, disable memory, or restrict bot visibility. See Step 12 and `references/multi-user-memory-isolation.md`.\n- **Custom bot rate limits (5 QPS / 100 QPM)**: The Feishu custom bot has hard platform-level rate limits of **5 requests/second** and **100 requests/minute** per bot per tenant. Exceeding either triggers HTTP 429. Message/group APIs can NOT be upgraded. Avoid sending at round-hour/half-hour times (e.g. 10:00, 17:30) which may trigger system-level 11232 throttling. Full rate limit tiers and handling strategy: `references/rate-limits.md`.\n- **Finding DM chat_id for cron delivery**: To get a DM's `oc_` format chat_id
  (needed for cron `deliver=feishu:oc_xxx`), send a one-shot test via lark-cli:
  `lark-cli --as bot im +messages-send --user-id ou_xxx --text test`
  The response JSON contains `data.chat_id` as the `oc_` string. The `ou_`
  open_id can be found from `sqlite3 state.db` querying sessions table.
- **Cron delivery: verify target first**: Don't trust the DM chat_id from memory blindly. If cron output shows up in a group, verify with the lark-cli test above. Also note that `cronjob(action=run)` may deliver to the origin session rather than the configured target — test before relying on scheduled delivery.
- **Cron 投递 230002 系统诊断流程（2026-08-04 实测）**：多 job 同时报 `[230002] Bot/User can NOT be out of the chat` 时按顺序排查：① `lark-cli --as bot im +messages-send --chat-id <oc_xxx> --text test` 实测会话——成功则会话/bot 本身没坏，问题在投递机制；② 对比 `.env` 的 `FEISHU_APP_ID` 与 `lark-cli auth status` 的 appId 是否一致（不一致=新旧凭据并存或应用迁移未完成）；③ 看错误起始时间——应用迁移窗口期（旧 appId 失效到重新授权完成之间）投递会持续失败，这是预期中的；④ 重新授权后 `cronjob(action=run)` 手动触发任意 job，若 `last_delivery_error` 清空为 null 且 errors.log 无新增 230002，通道即恢复；其余 job 的历史错误会在下次自动运行时自动刷新。

- **⚠️ SOUL.md is NOT loaded by Hermes**: `~/.hermes/SOUL.md` has zero references in the hermes-agent source code (grep-verified 2026-07-02). Any instructions placed there — format rules, memory write gating, reply style — are NEVER injected into any session. This file is dead weight. Use `agent.system_prompt` (config.yaml → universal injection, see `references/agent-system-prompt-injection.md` for full trace), `display.platforms.feishu.system_prompt` (Step 8, feishu-only), or `display.platforms.feishu.channel_prompts.<chat_id>` (Step 9b, per-channel).
- **话题/引用回复中的 @提及检测（实测 2026-08-04 已正常）**：飞书话题 (topic/thread) 回复和引用回复的消息带有 `parent_id`。早期版本飞书 API 不在此类消息的 `mentions` 中填充 @提及，导致 `require_mention: true` 时话题消息被静默丢弃。**当前版本实测正常**——话题中 @Bot 可正常触发回复，会话 key 正确包含 `omt_` 话题ID。如果遇到话题中 @Bot 没反应，先检查 gateway 日志中是否有 `dropping inbound event`，再用 `-vv` 前台运行诊断。
- **心跳消息两层区分（实测 2026-08-06）**：①Hermes 通知层——agent 运行超过 `gateway_notify_interval`（默认180s）时发送 "⏳ Working — X min" 心跳消息，**可关闭**：`hermes config set agent.gateway_notify_interval 0`（关闭后 agent 长时间运行不再发任何心跳）。②飞书协议层——lark_oapi SDK 的 `_ping_loop` 每 120 秒发 WebSocket ping frame（`venv/Lib/site-packages/lark_oapi/ws/client.py`），这是飞书长连接保活机制，**不可关闭**（SDK 注释明确 "user-facing overrides are intentionally not exposed"，取消会被服务端判定断连）。Hermes 的 `platforms.feishu.ws_ping_interval` 只能调间隔不能设 0。排查"心跳"问题先分清是哪一层；用户说"取消心跳"通常指①。
- **心跳消息在话题模式下自建子话题**：当 agent 运行超过 `gateway_notify_interval`（默认180s），gateway 发送 "⏳ Working — X min" 心跳消息。该消息的 metadata 包含 `thread_id`（话题ID）和 `reply_to_message_id`（原消息ID）。飞书 adapter 的 send 逻辑（adapter.py:4620-4665）检测到两者都存在时，用 `reply` API + `reply_in_thread=True` 发送——在飞书话题群里这会**创建一个新的回复线程**（子话题），而不是发到当前话题里。**根因**：心跳消息应该用 `create` API + `thread_id` 作为 `receive_id` 直接发到话题，而不是用 `reply` API。**临时修复**：`hermes config set agent.gateway_notify_interval 0` 关闭心跳通知。**代码位置**：run.py:19687-19691 的 `_notify_adapter.send()` 调用，以及 adapter.py:4624-4635 的 reply 优先逻辑。
- **Gateway 重启后话题回复发到群主聊天（丢失 thread_id）**：当 gateway 在处理话题消息期间被重启（手动或 crash），auto-resume 恢复 session 时丢失了 session key 中的 `omt_` 话题ID。结果：响应发到群主聊天 `oc_xxx` 而非话题 `omt_xxx`，表现为"agent 自己新建了话题"。**诊断**：日志中 `Sending response (N chars) to oc_xxx` 后面没有话题/thread 信息。**根因**：session key `feishu:group:{chat_id}:{thread_id}` 中的 thread_id 在 auto-resume 路径中未被提取传递给 send 逻辑。**缓解**：处理话题消息期间避免重启 gateway；如果必须重启，用户需在原话题重新发消息触发新 session。**日志关键词**：`Scheduled auto-resume` + 后续 `Sending response to oc_xxx`（无 thread 后缀）。
- **⚠️ 异常退出恢复机制验证方法（实测 2026-08-06）**：gateway 的自动恢复三层：①优雅重启/关闭 → 停机前 `mark_resume_pending(session, "restart_timeout"/"shutdown_timeout")`（run.py 的 pre-drain 路径）；②异常退出（SIGKILL/OOM/断电）→ 启动时检测无 `.clean_shutdown` 标记 → `suspend_recently_active(max_age_seconds=120)` 把**最近 120 秒内活跃**的 gateway 会话标记 `resume_pending=True` + `resume_reason="restart_interrupted"`（session.py:2850）；③恢复时 `build_resume_recovery_note()` 注入系统提示说明中断原因（"previous turn was interrupted by a gateway restart/shutdown/interruption"）。**验证方法**：grep gateway.log 关键词——`Marked N in-flight session(s) as resumable`（标记成功）+ `Scheduled auto-resume for N restart-interrupted session(s)`（触发恢复）；`Previous gateway exited cleanly — skipping session suspension` = 优雅退出正确跳过。**判断陷阱**：异常退出后**没有**恢复日志 ≠ 机制坏了——可能当时无 120s 内活跃的 gateway 会话（`suspended=0` 不打日志，代码只在 `if suspended:` 时记录）。查证用 `~/AppData/Local/hermes/sessions/sessions.json`（gateway 会话存储，`resume_pending`/`resume_reason`/`suspended` 字段）+ state.db sessions 表 `last_activity_at` 对照中断时间点。**限制**：①桌面端会话（source=desktop）不走此机制——桌面 app 是独立进程，意外关闭后需手动从会话列表继续；②`max_age_seconds=120` 硬编码——空闲超 2 分钟的会话不自动续跑，但下次发消息仍从原历史继续（不丢上下文）。
- **话题消息可能完全不被推送**：部分话题回复消息在 gateway 日志中完全没有记录（连 "Received raw message" 都没有），说明飞书 WebSocket 根本没有推送该事件。这可能是飞书侧的权限或事件订阅问题，与 adapter 代码无关。如果日志中找不到任何 trace，检查飞书开发者后台的事件订阅配置。
- **`md` element single-paragraph constraint**: Feishu's post message `md` tag supports only ONE paragraph per element. Multi-paragraph content in a single `md` element → entire element renders as plain text. The fix in `_build_markdown_post_rows` (`_make_rows()` splits on blank lines) is applied in hermes-agent source code. If multi-paragraph messages render as plain text after a fresh install, verify the fix is present. See `references/markdown-rendering-fix.md` for details.
- **飞书不支持原生语音气泡**：`msg_type="audio"` 本质是文件附件（带播放按钮的音频文件），不是 Telegram/Discord 那种内联语音条。这是平台限制，非 Hermes 问题。详见 `references/voice-audio-capabilities.md`。
- **`hermes config set` 并发写入冲突**：用 `&&` 串联多个 `hermes config set` 时，后一个命令可能在前一个还未释放 config.yaml 文件锁时尝试写入，导致 `PermissionError: [WinError 5] 拒绝访问。`。**修复**：每个 `hermes config set` 单独执行（各一个 terminal 调用），不要用 `&&` 连写。\n- **Stale assumptions about Feishu capabilities**: Code comments and historical memory entries may claim certain features don't work (e.g. "tables forced to text mode"). Feishu's post+md renderer evolves — always verify against live Feishu or source code before concluding something is unsupported. The `_MARKDOWN_TABLE_RE` force-text block was left in adapter.py for months based on an outdated comment; tables actually work fine now. **Lesson**: when a reference doc claims a fix is applied, verify by reading the actual source — the doc may be ahead of reality (as happened 07-01 doc claim vs 07-10 actual fix).
- **Agent 卡死导致所有消息被"⚡ Interrupting"**: 当 agent 卡在长时间 API 调用上（如 MiMo 流式响应超时），`interrupt()` 只设软标志位 `_interrupt_requested`，agent 永远到不了检查点。结果：agent 永远 busy → 每条新消息都走 `_handle_active_session_busy_message` → 全部触发"⚡ Interrupting current task"但排队的消息永远不会被处理。**诊断**：群里连续收到多条"⚡ Interrupting"回复。**立即修复**：群里发 `/stop` 强制终止卡死的 agent。**长期缓解**：减小 `agent.gateway_timeout`（默认 1800s），或在 channel_prompt 中加超时放弃指引。详见 `references/interrupt-stuck-agent.md`。
- **⚠️ "⚡ Interrupting" 但 agent 没在忙别的任务 = 同会话 busy 判定没释放或 reaction 误触发（实测 2026-08-07）**：会话独立≠不会发 interrupt。两个非"真忙"根因：①回复的流式投递最终确认没收到（日志 `Queued follow-up ... final stream delivery not confirmed`）→ 会话**保持 busy 状态 10+ 分钟**，后续任何消息都触发 interrupt ack；②**飞书点赞/取消赞被 adapter 构造成 TEXT 消息**（`adapter.py` reaction 路由 → `MessageEvent(text="reaction:added:THUMBSUP", message_type=TEXT)` → `_handle_message_with_guards`）→ 一个点赞触发一次完整 agent 运行（实测 50.1s、1 次 LLM 调用），第二条 reaction 进来即 busy。**排查**：`grep -n "<chat_id>" gateway.log | tail` 追时间线，找 `final stream delivery not confirmed` 与 `Routing reaction` 行。**消除**：`display.busy_ack_enabled: false`（彻底静默，消息照常处理）/ `busy_input_mode: queue`（不打断+换「⏳ Queued」提示）/ 改 adapter 让 reaction 不进对话管线（源码改动会被 update 覆盖）。详见 `references/reaction-events-and-busy-ack.md`——同一文件也含「之前关掉过的心跳检查？」排查用的 **gateway 心跳/检查类机制全景**（loop heartbeat / watchdog 日志新鲜度 / scale_to_zero 空闲缩容 / Hindsight idle_timeout / streaming.enabled 投递确认 / `/heartbeat` 会话定时提醒 / auto-continue 断线自动继续（interrupted_turns.json）/ cron ticker 心跳 / 通知层与协议层心跳），可关性对照表见文内。排查「心跳检查」先分清层次：`/heartbeat status` 查会话定时提醒、`grep state_meta` 查是否用过、`state/gateway.heartbeat` mtime 查 loop 存活、`cron/ticker_heartbeat` 查 cron 调度器。
- **Group events stop after gateway restart**:
## 飞书会话的 Skill 加载机制（全渠道平级，2026-08-06 实测澄清）

**结论：飞书会话和桌面客户端会话在 skill 层面本来就是平级的**——不是"飞书渠道没资格带创作类 skill"。

机制（源码验证 `agent/prompt_builder.py` / `agent/skill_utils.py`）：

1. **skill 索引全渠道共享**：所有会话（desktop/feishu/其他）注入同一份 skill 目录+描述（`_load_skills_snapshot`）
2. **平台匹配 = 操作系统，不是渠道**：`skill_matches_platform` 匹配 macos/linux/windows（`skill_utils.py:251`）——飞书和桌面在同一平台，不被区分
3. **`skills.disabled` 全局生效**：禁用即所有渠道都禁，不在禁用列表里的 skill 所有渠道都能看到
4. **agent 按任务相关性主动加载**：系统提示只有 skill 目录+一行描述，完整内容靠 agent 判断任务命中描述后 `skill_view` 加载

**实证**：飞书 DM 里"优化提示词"类请求稳定触发 AI提示词助手 加载（2026-07-07~14 多次），"查项目进度"类请求只加载工作区约定 skill——**差异是任务性质决定，不是平台限制**。

**教训**：判断"飞书回复为什么没带某 skill"时，先看**这条消息触发了哪个 skill 描述**，不要归因于渠道能力不足。飞书渠道的创作类问题同样能加载 AI电影编剧 等创作 skill 并触达其 references 知识库。

## 宕机/不回消息排查

**优先看 `feishu-outage-recovery` skill**（2026-08-07 实战沉淀）：飞书不回消息 → 查 gateway 进程/日志 → 重启 → 拉停机窗口消息（`data.messages` 字段）→ 批量补回复。

**本机已部署自动自愈**（2026-08-07）：
- `~/AppData/Local/hermes/scripts/gateway_watchdog.py` + 计划任务 `Hermes_Gateway_Watchdog`（每 5 分钟）：gateway 进程死/日志超时 → 自动拉起 + 写 `state/gateway_outage.json` + lark-cli DM 告警
- 停机窗口消息不会自动补推（WebSocket 断连不重推），gateway 恢复后需手动按 feishu-outage-recovery 流程补消息（目前无自动补消息 cron——人工把关质量，防自动回错）
- `scripts/fix_cryptography.py`：`hermes update` 中断损坏 cryptography 时，关掉 Hermes 后手动运行修复
- ⚠️ Hermes CLI 命令（`hermes gateway status/start`）可能触发 update 恢复流程并连带停 gateway——疑似宕机时先看 gateway.log 再动

## Reply Channel Discipline

**Hermes TUI 里问 → TUI 回。飞书里问 → 飞书回。Cron 自动推送 → 推飞书。禁止跨渠道回复。**

This prevents confusion where the user asks in one channel but receives the answer in another.

## Step 13 — Per-Channel Model & Sub-Agent Delegation

### 13a — Override model per group/channel

Use `channel_overrides` to assign different models to different groups:

```bash
hermes config set platforms.feishu.channel_overrides.oc_CHAT_ID.model deepseek-v4-flash
hermes config set platforms.feishu.channel_overrides.oc_CHAT_ID.provider deepseek
```

To remove an override (no `hermes config unset`), use Python:
```python
import yaml
with open(r'C:\Users\HMSJ\AppData\Local\hermes\config.yaml') as f:
    c = yaml.safe_load(f)
c['platforms']['feishu'].pop('channel_overrides', None)
with open(r'C:\Users\HMSJ\AppData\Local\hermes\config.yaml', 'w') as f:
    yaml.dump(c, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
```

### 13b — Sub-agent delegation model

Sub-agents inherit the parent model unless pinned globally. To use a different model for delegated tasks:

```bash
hermes config set delegation.model deepseek-v4-pro
hermes config set delegation.provider deepseek
```

### 13c — Auto-delegation prompt

Add a channel prompt to make the agent automatically delegate complex tasks:

```bash
hermes config set platforms.feishu.channel_prompts.oc_CHAT_ID \
  "始终使用中文回复，简洁直接。遇到以下情况使用 delegate_task 委托子代理异步处理：1) 需要多轮工具调用（3+轮）的复杂任务 2) 预计耗时超过 30 秒的任务 3) 需要深度分析/计算的任务。委托后主会话立刻简短回复「收到，处理中，稍后反馈」，不等子代理结果。"
```

### 13d — `thread_sessions_per_user` (话题模式)

Controls whether topic/thread replies get per-user session isolation:

```bash
hermes config set platforms.feishu.thread_sessions_per_user false
```

- `false` (default): All users share one session per topic → bot 能看到跨用户上下文全貌，但任何人发消息都会打断当前任务（⚡ Interrupting）。**适合多人协作讨论同一话题**。
- `true`: Each user gets own session per topic → 不互相打断，但 bot 看不到跨用户的讨论上下文（A 让 bot 总结时只看到 A 自己说的话）。**适合各人各问各的**。

同一用户在同一话题中连发消息仍会打断（隔离的是不同用户之间）。此设置与 `group_sessions_per_user`（默认 `true`）正交。

**Session key 构建逻辑**（gateway/session.py:871-959）：

| 场景 | Session Key |
|------|------------|
| 私聊 | `feishu:dm:{chat_id}` |
| 私聊+话题 | `feishu:dm:{chat_id}:{thread_id}` |
| 普通群聊 | `feishu:group:{chat_id}:{user_id}` |
| 话题模式（共享） | `feishu:group:{chat_id}:{thread_id}` |
| 话题模式（隔离） | `feishu:group:{chat_id}:{thread_id}:{user_id}` |

**话题模式的故障隔离**：每个话题独立 session，一个话题的 agent 卡死不影响其他话题。`/stop` 只终止当前话题。详见 `references/interrupt-stuck-agent.md`。
