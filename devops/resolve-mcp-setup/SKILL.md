---
name: resolve-mcp-setup
description: Install and configure the davinci-resolve-mcp server for Hermes Agent on Windows. Covers npm-managed install, config.yaml wiring, Python venv path fixing, env vars, and common gotchas (YAML args serialization, PYTHONHOME crash). Also applicable for configuring other npm-based MCP servers into Hermes.
version: 1.0.0
tags: [davinci-resolve, mcp, windows, configuration, install]
---

# Resolve MCP Server Setup for Hermes

Install and wire the `davinci-resolve-mcp` server into Hermes Agent. The same pattern applies to any npm/Python-based MCP server that needs a managed venv.

## Prerequisites

- DaVinci Resolve **Studio** 18.5+ (free edition has no scripting API)
- Resolve: Preferences → General → "External scripting using" set to **Local**
- Node.js + npm available
- Python 3.10–3.12 in PATH (3.13+ works on Resolve 20.3.2, may fail on older builds)

## Install

```bash
npx davinci-resolve-mcp setup --clients manual
```

This installs a managed copy under `%LOCALAPPDATA%\davinci-resolve-mcp\` with its own venv. The `--clients manual` flag prints config snippets instead of auto-configuring. Hermes is NOT in the auto-configure list, so manual wiring is required.

Note the printed paths:
- `command`: `<managed_dir>\venv\Scripts\python.exe`
- `args`: `<managed_dir>\src\server.py`
- `env`: RESOLVE_SCRIPT_API, RESOLVE_SCRIPT_LIB, PYTHONPATH, PYTHONHOME

## Wire into Hermes config.yaml

Use `hermes config set` for each key (dot notation for nested keys):

```bash
hermes config set mcp_servers.davinci-resolve.command "<venv python path>"
hermes config set mcp_servers.davinci-resolve.timeout 180
hermes config set mcp_servers.davinci-resolve.connect_timeout 60
hermes config set mcp_servers.davinci-resolve.env.RESOLVE_SCRIPT_API "<api path>"
hermes config set mcp_servers.davinci-resolve.env.RESOLVE_SCRIPT_LIB "<lib path>"
hermes config set mcp_servers.davinci-resolve.env.PYTHONPATH "<modules path>"
hermes config set mcp_servers.davinci-resolve.env.PYTHONHOME "<python home>"
```

## Critical: Fix YAML args formatting

`hermes config set` serializes the `args` array as a **JSON string** instead of a YAML list:

```yaml
# WRONG (hermes config set produces this):
args: '["C:\...\server.py"]'

# RIGHT (must be a YAML list):
args:
  - C:\...\server.py
```

Fix it with Python after all keys are set:

```python
import yaml
with open(config_path, 'r') as f:
    cfg = yaml.safe_load(f)
# Replace string with proper list
cfg['mcp_servers']['davinci-resolve']['args'] = [r'<full server.py path>']
with open(config_path, 'w') as f:
    yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
```

## Verify

1. Start DaVinci Resolve Studio
2. Restart Hermes (`/reset` or restart app — MCP tools discovered at startup only; use `/reload-mcp` to hot-reload without restarting the whole session)
3. **Run `hermes mcp list`** — this is the authoritative check for whether the MCP server actually connected and its tools are registered
4. In new session: call `mcp_davinci_resolve_resolve_control(action="get_version")`

Check logs on failure:

```bash
# Windows: logs live under %LOCALAPPDATA%\hermes\logs\ (use hermes config path to confirm)
tail "$LOCALAPPDATA/hermes/logs/mcp-stderr.log"    # MCP subprocess errors
tail "$LOCALAPPDATA/hermes/logs/agent.log"          # Connection/discovery messages
```

## Windows-specific

- `PYTHONHOME` env var is **required** on Windows for Resolve 20.3+ to prevent multi-Python crashes
- The managed venv has no `pip` (stripped for install size) — use the system Python for pip operations
- Hermes config.yaml lives at `%LOCALAPPDATA%\hermes\config.yaml`. **Do not edit `~/.hermes/config.yaml`** — on Windows these are two separate directories, and Hermes only reads the `%LOCALAPPDATA%` one. Use `hermes config path` to confirm the active config location.
- Path escaping: use raw strings (`r'C:\...'`) or forward slashes (`C:/...`) in Python fix script
- Use `hermes mcp list` as the single source of truth for which MCP servers are connected — don't rely on reading config.yaml directly

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| MCP tools not appearing after restart | `args` in config is a JSON string, not a YAML list | Run the Python fix script above |
| `ModuleNotFoundError: No module named 'src'` | Wrong working directory when testing | Always run from managed dir root |
| Resolve API returns None | Resolve not running, or external scripting not set to Local | Check Resolve prefs + restart Resolve |
| Py bridge fails on Python 3.13+ | Older Resolve builds don't support 3.13+ | Use 3.10–3.12 interpreter |
| Gateway setup wizard hangs on Windows PTY | Known Windows terminal issue | Configure platform manually via env vars |
| MCP tools appear in one Hermes session but not another | Editing wrong config file — `~/.hermes/config.yaml` is NOT the active config on Windows | Run `hermes config path` to find the real config at `%LOCALAPPDATA%\hermes\config.yaml` |
| `hermes mcp list` shows no servers despite config | MCP server failed to connect, or config file is in wrong location | Check `hermes config path`, verify server process, check logs under `%LOCALAPPDATA%\hermes\logs\` |

## Reference

- `references/resolve-color-workflow.md` — Color grading analysis pattern: evidence base → boundary report → probe → sample → decide
