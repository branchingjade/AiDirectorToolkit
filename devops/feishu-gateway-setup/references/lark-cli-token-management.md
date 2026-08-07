# lark-cli Token Management

## Token Lifetimes

| Token | Default | Maximum | Where to change |
|-------|---------|---------|-----------------|
| access_token | ~2 hours | Fixed | Cannot change |
| refresh_token | 7 days | 180 days | 飞书开发者后台 → 安全设置 → 授权有效期 |

## Auto-Refresh

lark-cli auto-refreshes `access_token` on every API call when expired. No manual intervention needed.

Refresh token validity:
- Expires after 7 days (default) of inactivity
- Must re-authorize (scan QR code) if refresh_token expires
- Every successful API call resets the inactivity timer

## Required Scopes

### `im:message.send_as_user`

**NOT included by `--recommend` flag.** Must be explicitly requested:

```bash
lark-cli auth login --recommend --scope "im:message.send_as_user" --no-wait --json
```

Without it: `lark-cli --as user im +messages-send` fails with `missing_scope`.

## Architecture

```
Hermes adapter.py  →  Feishu WebSocket + REST  (bot-level, all messaging)
lark-cli --as user →  OAuth user_access_token  (only when user identity needed)
```

lark-cli is a supplementary tool, NOT a dependency of Hermes Feishu messaging.
Do NOT install OpenClaw or lark-* skills — Hermes has built-in Feishu tools.
