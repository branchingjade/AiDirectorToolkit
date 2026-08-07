# Agent-Browser on Windows: CDP mode instead of --session

## Problem

`agent-browser --session <name>` hangs indefinitely on Windows (both `--json` and
interactive modes). The command never returns — Hermes browser tools depend on
this mode, so they freeze the entire session.

## Root Cause

Agent-browser's `--session` flag spawns a daemon process + Unix socket for IPC.
The daemon startup or socket communication path fails silently on Windows.

## Solution: CDP mode

Use `agent-browser --cdp <port>` instead, connecting to a Chrome instance with
remote debugging enabled. This bypasses agent-browser's daemon/session
management entirely.

### Step 1: Launch Chrome with remote debugging

```bash
# Kill any running Chrome first
taskkill /F /IM chrome.exe 2>/dev/null

# Launch with debug port (use default profile for persistent login state)
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  "https://target-site.com"
```

**Critical:** Do NOT use `--user-data-dir <tmp>` — use the default profile
(`C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\`) so cookies
and login state persist across sessions. If Chrome was already running with
the default profile, kill it first; two Chrome instances can't share a profile.

### Step 2: Verify CDP is up

```bash
curl -s http://localhost:9222/json/version | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('Browser'))"
# → Chrome/149.0.7827.155
```

### Step 3: Use agent-browser with --cdp

```bash
# Navigate
agent-browser open "https://example.com" --cdp 9222 --json

# Read page content (text/html fallback)
agent-browser read --cdp 9222 --json

# Snapshot (aria snapshot — prefer read for most cases)
agent-browser snapshot --cdp 9222 --json

# Execute JavaScript
agent-browser eval "(function(){...})()" --cdp 9222 --json

# Click by text content (find often fails; eval is more reliable)
agent-browser eval \
  "(function(){var els=document.querySelectorAll('*');for(var el of els){if(el.textContent.trim()==='登录 / 注册'){el.click();return 'clicked';}}return 'not found';})()" \
  --cdp 9222 --json
```

## Finding form inputs

`agent-browser find` is unreliable on complex SPAs. Use `eval` to enumerate:

```bash
agent-browser eval \
  "(function(){var inputs=document.querySelectorAll('input');var result=[];inputs.forEach(function(inp,i){result.push(i+':'+inp.type+':'+inp.placeholder+':'+inp.name);});return JSON.stringify(result);})()" \
  --cdp 9222 --json
```

Then fill via eval:

```bash
agent-browser eval \
  "document.querySelectorAll('input')[6].value='13800138000';'ok'" \
  --cdp 9222 --json
```

## Headed mode

The Chrome window launched with `--remote-debugging-port` is visible by
default (headed). The user can interact with it directly (scan QR codes,
type verification codes, etc.) while agent-browser reads/interacts via CDP.

## Hermes integration status

Hermes `browser_tool.py` hardcodes `--session` mode (line 2089). Until
patched, Hermes browser tools are **unusuable** on Windows. Use the raw
agent-browser CLI + CDP approach as the workaround.

## Pitfalls

- `agent-browser find` — often fails with "Element not found" or "covered by overlay". Prefer `eval` with direct JS.
- `agent-browser read --cdp` reads the active tab's **text** content, not aria snapshot. Use `snapshot` for aria tree if needed.
- Each `agent-browser open --cdp` opens a NEW tab. Use `eval` to click links within the existing page instead.
- `agent-browser --cdp <ws_url>` (WebSocket URL) vs `--cdp <port>` — the port version auto-discovers the active page; the WS URL version targets a specific page. Prefer port unless you need explicit page targeting.
