# Hermes extras → package mapping

When running `uv sync` with explicit `--extra` flags, use this to determine which extras your instance needs.
Check what's currently installed to decide:

```bash
/venv/Scripts/python.exe -c "
import importlib.metadata
dists = {d.name: d.version for d in importlib.metadata.distributions()}
print(f'Total: {len(dists)} packages')
"
```

## Core dependencies (always installed)

No `--extra` needed. These are in `pyproject.toml` → `[project].dependencies`.

## Extras groups

| --extra flag | Key packages installed | When needed |
|-------------|----------------------|-------------|
| `all` | agent-client-protocol, google-api-python-client, simple-term-menu, youtube-transcript-api, sse-starlette (mcp transitive), fastapi/uvicorn (web) | Always include — safe subset, no linux-only deps |
| `feishu` | lark-oapi, qrcode | Feishu gateway |
| `bedrock` | boto3, botocore | AWS Bedrock provider |
| `wecom` | defusedxml | WeChat Work callback |
| `messaging` | aiohttp, python-telegram-bot, discord.py, slack-bolt, slack-sdk, brotlicffi, tornado, pynacl | Telegram/Discord/Slack messaging |
| `mcp` | mcp, starlette (already in `all` + `web`) | MCP tool servers |
| `web` | fastapi, uvicorn, starlette, python-multipart (already in `all`) | Hermes dashboard |
| `google` | google-api-python-client, google-auth, google-auth-httplib2, google-auth-oauthlib, httplib2, uritemplate (already in `all`) | Google Workspace integration |

## Typical sync command

For a Windows desktop user with Feishu + Bedrock + WeCom + messaging:

```bash
UV_PROJECT_ENVIRONMENT=venv uv sync --extra all --extra feishu --extra bedrock --extra wecom --extra messaging
```

## Extras that DON'T work on Windows

- `matrix` — depends on `python-olm` (Linux-only wheels, no build path on Windows)
- These are NOT in `[all]` for this reason

## Extras that ARE in `[all]`

cron, cli, pty, mcp, homeassistant, sms, acp, google, web, youtube

So `--extra all` covers these 10 groups. Add platform-specific extras on top.
