# Feishu / Lark Gateway Setup

## Manual Configuration (bypass interactive wizard)

The interactive `hermes gateway setup` wizard can hang on Windows PTY sessions.
Use manual env-var configuration instead.

### 1. Create Feishu App

1. Open developer console: https://open.feishu.cn/ (Feishu) or https://open.larksuite.com/ (Lark)
2. Create a new app
3. Copy **App ID** and **App Secret** from Credentials & Basic Info
4. Enable the **Bot** capability

### 2. Set Environment Variables

Add to `~/.hermes/.env`:

```bash
FEISHU_APP_ID=<your_app_id>
FEISHU_APP_SECRET=<your_app_secret>
FEISHU_CONNECTION_MODE=websocket   # recommended: no public URL needed
```

### 3. Install Dependencies

```bash
pip install websockets
```

For webhook mode (requires public endpoint), also install:
```bash
pip install aiohttp
```

### 4. Start Gateway

```bash
hermes gateway run       # foreground
hermes gateway install   # install as service
hermes gateway start     # start service
```

## Connection Modes

| Mode | When to use | Requirement |
|------|-------------|-------------|
| `websocket` | Laptop, workstation, private server (recommended) | `websockets` package |
| `webhook` | Hermes behind a public HTTP endpoint | `aiohttp` package |

## Behavior

| Context | Behavior |
|---------|----------|
| Direct messages | Responds to every message |
| Group chats | Responds only when @mentioned |
| Shared group chats | Session isolated per user by default |

Control shared-chat behavior in config.yaml:
```yaml
group_sessions_per_user: true   # default: isolated per user
```

## Webhook Mode Customization

```bash
FEISHU_WEBHOOK_HOST=127.0.0.1
FEISHU_WEBHOOK_PORT=8765
FEISHU_WEBHOOK_PATH=/feishu/webhook
```

## Setting the Home Channel

The home channel is where cron jobs and cross-platform messages are delivered by default when no specific target is given.

### Method 1: `/sethome` (recommended)

In the Feishu group chat or DM where you want to set as home, send:
```
/sethome
```
The gateway auto-captures the `oc_xxx` chat_id. Instant and reliable.

### Method 2: Environment variable (from CLI/session)

If you can't send `/sethome` directly, set in `~/.hermes/.env`:
```bash
FEISHU_HOME_CHANNEL=oc_xxx        # the group/DM chat_id
FEISHU_HOME_CHANNEL_NAME=开工      # human-readable display name
```
Then restart the gateway: `hermes gateway restart`

**Finding the chat_id:** Run `send_message(action='list')` from any session — it lists all known Feishu targets with their `oc_xxx` IDs.

### Method 3: config.yaml (dict format)

Under `platforms.feishu.home_channel`:
```yaml
platforms:
  feishu:
    enabled: true
    home_channel:
      platform: feishu
      chat_id: oc_xxx
      name: 开工
```

### Pitfall

The top-level `gateway.home_channel` key in config.yaml is **not** the right place — it accepts a platform name string for routing hints, not the per-platform home channel config. Use one of the three methods above instead.
