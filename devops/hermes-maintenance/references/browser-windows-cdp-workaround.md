# Browser Windows CDP Workaround — Full Session Notes

## Problem

`agent-browser --session <name>` hangs on Windows (tested through v0.30.1).
Hermes browser tools (`browser_tool.py`) exclusively use `--session` mode,
so all browser operations deadlock the session.

## Reproduction

```bash
agent-browser --version
# agent-browser 0.30.1

# This hangs indefinitely:
agent-browser open https://www.baidu.com --session test --json
# ^ Never returns

# These work instantly:
agent-browser open https://www.baidu.com --json
agent-browser open https://www.baidu.com --cdp 9222 --json
```

## Root cause analysis

- `--session` mode spawns a daemon process + Unix-domain-socket IPC
- Windows doesn't have native Unix sockets (agent-browser may use named pipes or WSL sockets, both unreliable)
- The daemon startup/socket handshake hangs silently

## CDP Workaround — Full workflow

### 1. Start Chrome with remote debugging

```bash
taskkill /F /IM chrome.exe 2>/dev/null
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile" &
```

### 2. Verify CDP

```bash
curl -s http://localhost:9222/json/version
# → {"Browser": "Chrome/...", "webSocketDebuggerUrl": "ws://..."}
```

### 3. Use agent-browser with --cdp (no session!)

```bash
# Navigate
agent-browser open "https://haifanwu.com" --cdp 9222 --json

# Read page content
agent-browser read --cdp 9222 --json

# Get ariaSnapshot (interactive elements with @ref)
agent-browser snapshot --cdp 9222 --json

# Execute JavaScript
agent-browser eval "(function(){...})()" --cdp 9222 --json

# Find elements
agent-browser find text "登录" --cdp 9222 --json

# Headed mode (visible browser)
agent-browser open "..." --cdp 9222 --headed --json
```

### 4. Click via JavaScript (when `find ... click` fails due to overlays)

```bash
agent-browser eval "(function(){var els=document.querySelectorAll('*');for(var el of els){if(el.textContent.trim()==='登录 / 注册'){el.click();return 'clicked';}}return 'not found';})()" --cdp 9222 --json
```

### 5. Inspect input fields

```bash
agent-browser eval "(function(){var inputs=document.querySelectorAll('input');var result=[];inputs.forEach(function(inp,i){result.push(i+':'+inp.type+':'+inp.placeholder+':'+inp.name);});return JSON.stringify(result);})()" --cdp 9222 --json
```

## Architecture context

Hermes `tools/browser_tool.py` (4005 lines):

- Line 5: "This module provides browser automation tools using agent-browser CLI"
- Line 2089: `backend_args = ["--session", session_info["session_name"]]` — local mode always uses --session
- Line 2086: `backend_args = ["--cdp", session_info["cdp_url"]]` — cloud mode uses --cdp
- Lines 2078-2089: Local vs cloud backend selection — no CDP option for local

Hermes `package.json` lists `"agent-browser": "^0.26.0"` as a dependency.

## Impact

- Hermes `browser` toolset is **non-functional on Windows** as of June 2026
- Only viable local alternative: use `agent-browser --cdp` directly (bypasses Hermes browser tools)
- Cloud backends (Browserbase, Browser Use) don't have this issue but require paid API keys
