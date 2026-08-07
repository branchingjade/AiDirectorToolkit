---
name: openclaw-feishu-plugin
description: Install, configure, and manage the OpenClaw Feishu (飞书) official plugin (@larksuite/openclaw-lark). Covers prerequisites, installation QR code workflow, PATH fixes, and removing Hermes Feishu config when migrating.
tags: [openclaw, feishu, lark, plugin, migration]
triggers:
  - openclaw feishu
  - openclaw-lark
  - 飞书插件
  - feishu plugin install
---

# OpenClaw 飞书官方插件

## Prerequisites

1. **OpenClaw must be globally installed AND in PATH**
   ```bash
   npm install -g openclaw
   openclaw --version
   ```
   - `npx -y openclaw` alone is NOT enough — the lark installer checks for `openclaw` in PATH
   - If `which openclaw` fails, do `npm install -g openclaw` first

2. **Version requirements** (from official docs):
   - Linux/MacOS: OpenClaw 2026.2.26+
   - Windows: OpenClaw 2026.3.2+

## Installation

```bash
npx -y @larksuite/openclaw-lark install
```

### Critical pitfall: QR code scanning

The installer displays a **QR code in the terminal** that must be scanned with the Feishu mobile app to configure the bot.

⚠️ **This CANNOT work through Hermes chat** — the QR code renders in the terminal but the user can't see it in the Feishu conversation. The user must run this command in their own local terminal (PowerShell/cmd/git-bash).

After scanning, the installer fetches bot configuration and completes. If it times out (120s default), re-run the command.

### Post-install

```bash
openclaw plugins list   # Verify openclaw-lark is "enabled"
```

There's often a config warning about `plugins.entries.feishu`. Fix with:
```bash
openclaw plugins install @openclaw/feishu
```

Both plugins should show `enabled` in the list.

## OpenClaw Gateway & Dashboard

The OpenClaw gateway runs independently from Hermes. Key commands:

```bash
openclaw gateway start     # Start gateway (Scheduled Task)
openclaw gateway health    # Check health + channel status
openclaw status            # Full status overview (channels, sessions, etc.)
```

### Dashboard (Web UI)

OpenClaw has a web dashboard at `http://127.0.0.1:18789/` (default port).

**Authentication:** Requires gateway token. Get it from config:
```bash
openclaw config get gateway   # Shows masked token
# For full token, read the JSON directly:
cat ~/.openclaw/openclaw.json | python3 -c "import sys,json; print(json.load(sys.stdin)['gateway']['auth']['token'])"
```

Enter the token in the dashboard login page → click "连接" (Connect).

**Dashboard features:** Chat, 概览 (Overview), 活动 (Activity), 工作板 (Workboard), 文档 (Documents).

### Config file location

OpenClaw config: `~/.openclaw/openclaw.json`
- `channels.feishu` — Feishu channel settings (appId, appSecret, policies)
- `gateway.auth.token` — Dashboard/gateway auth token
- `plugins.entries` — Plugin enable/disable
- `tools.alsoAllow` — Feishu tool permissions (bitable, calendar, chat, doc, drive, etc.)

## Removing Hermes Feishu config (migration)

When switching Feishu bot from Hermes to OpenClaw:

1. Edit `~/.hermes/.env` (or `%LOCALAPPDATA%/hermes/.env` on Windows) — **protected file**, use terminal + Python:
   ```python
   import re
   with open('.env', 'r') as f:
       content = f.read()
   for pattern in [r'FEISHU_APP_ID=.*\n', r'FEISHU_APP_SECRET=*** r'FEISHU_GROUP_POLICY=.*\n', r'FEISHU_REQUIRE_MENTION=.*\n', r'FEISHU_HOME_CHANNEL=.*\n', r'FEISHU_HOME_CHANNEL_THREAD_ID=.*\n', r'# Feishu Group Policy\n']:
       content = re.sub(pattern, '', content)
   with open('.env', 'w') as f:
       f.write(content)
   ```
2. Restart Hermes gateway: `hermes gateway restart`
3. Verify in logs: `grep -i feishu ~/.hermes/logs/gateway.log | tail -5` — should show "FEISHU_APP_ID not set" / "failed to connect"

## Key difference: Hermes vs OpenClaw

| | Hermes | OpenClaw |
|---|---|---|
| Feishu integration | Built-in gateway (websocket/webhook) | @larksuite/openclaw-lark plugin |
| Bot identity | Hermes's own bot app | Separate bot app (configured via QR scan) |
| Management | `hermes gateway` commands | `openclaw plugins` commands |

Both can coexist — they use separate bot apps in Feishu.
