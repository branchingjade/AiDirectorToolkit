---
name: openclaw-setup
description: Install, configure, and manage OpenClaw on Windows — gateway, Feishu plugin, dashboard, and background service.
triggers:
  - openclaw install
  - openclaw feishu plugin
  - openclaw gateway
  - openclaw dashboard
  - openclaw background
  - openclaw no window
---

# OpenClaw Setup & Management (Windows)

## Install OpenClaw

```bash
npm install -g openclaw
openclaw --version
```

⚠️ `npx openclaw` works for one-off commands but `@larksuite/openclaw-lark install` requires `openclaw` in PATH. Always do a global install first.

## Install Feishu Plugin

```bash
# Step 1: Install the lark plugin
npx -y @larksuite/openclaw-lark install

# Step 2: Also install the feishu dependency (listed as config warning)
openclaw plugins install @openclaw/feishu
```

⚠️ **QR Code requirement**: The install command displays a QR code that must be scanned with the Feishu mobile app. This CANNOT be done headlessly — the user must run this command in their own terminal and scan with their phone. Do NOT run from a remote/headless session expecting it to complete.

⚠️ **Plugin chain**: Both `openclaw-lark` AND `@openclaw/feishu` are needed. The config warning `plugins.entries.feishu: plugin not installed` means the second one is missing.

## Gateway Management

```bash
openclaw gateway start          # Start (Scheduled Task)
openclaw gateway stop           # Stop
openclaw gateway health         # Health check
openclaw gateway status         # Full status overview
openclaw status                 # System-wide status
```

## Dashboard

- URL: `http://127.0.0.1:18789/`
- Auth: token-based (required on first connect)
- Get token from config:
  ```bash
  cat ~/.openclaw/openclaw.json | python3 -c "import sys,json; print(json.load(sys.stdin)['gateway']['auth']['token'])"
  ```
- Also available via `openclaw config get gateway.auth.token` (but output is masked)

## Run Gateway Hidden (No CMD Window) with Auto-Restart

The default Scheduled Task shows a visible CMD window. To hide it AND ensure auto-restart on crash:

### Problem: VBS + direct cmd loses process tracking

The naive approach (VBS → `gateway.cmd` → node) fails because:
1. VBS runs cmd with `False` (no wait), so it exits immediately
2. The Scheduled Task marks itself "Ready" (complete) while node runs orphaned
3. When node crashes, nothing restarts it — the task already "finished"

**Symptom**: Gateway dies silently, Scheduled Task shows `State: Ready`, port 18789 refuses connections.

### Solution: Watchdog script

1. Create watchdog at `~/.openclaw/gateway-watchdog.cmd` (see `templates/gateway-watchdog.cmd`):
   ```cmd
   @echo off
   rem OpenClaw Gateway Watchdog - auto-restart on crash
   set "HOME=C:\Users\<user>"
   set "TMPDIR=C:\Users\<user>\AppData\Local\Temp"
   set "OPENCLAW_GATEWAY_PORT=18789"
   :loop
   echo [%date% %time%] Starting OpenClaw Gateway...
   "C:\Program Files\nodejs\node.exe" "C:\Users\<user>\AppData\Roaming\npm\node_modules\openclaw\dist\index.js" gateway --port 18789
   echo [%date% %time%] Gateway exited with code %errorlevel%, restarting in 5s...
   timeout /t 5 /nobreak >nul
   goto loop
   ```

2. Update VBS wrapper at `~/.openclaw/gateway-hidden.vbs` to call watchdog:
   ```vbs
   Set WshShell = CreateObject("WScript.Shell")
   WshShell.Run "cmd /c C:\Users\<user>\.openclaw\gateway-watchdog.cmd", 0, False
   ```

3. Run: `wscript.exe "C:\Users\<user>\.openclaw\gateway-hidden.vbs"`

4. For auto-start on boot, register as Scheduled Task (admin cmd needed):
   ```cmd
   schtasks /create /tn "OpenClaw Gateway" /tr "wscript.exe \"C:\Users\<user>\.openclaw\gateway-hidden.vbs\"" /sc onlogon /rl highest /f
   ```

### Verify watchdog works

```bash
# Find gateway PID
netstat -ano | grep "18789.*LISTENING" | awk '{print $5}'
# Kill it
taskkill //PID <pid> //F
# Wait 8s, then check — should be back at 200
sleep 8 && curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18789/
```

### Pitfalls

- ⚠️ `openclaw gateway restart` works from external terminal only — gateway caches config at startup
- ⚠️ Scheduled Task `RestartCount: 999` / `RestartInterval: PT1M` only works if the task's own process exits non-zero. With the VBS approach the task "finishes" immediately, so those settings are useless — the watchdog loop is what actually provides restart.
- ⚠️ Don't use `openclaw gateway start` while the watchdog is running — it will detect "gateway already running" and fail. Use `openclaw gateway restart` instead.

## Config File

- Location: `~/.openclaw/openclaw.json`
- Contains: plugins, channels (feishu credentials), gateway auth, tool permissions
- Backups: `openclaw.json.bak`, `.bak.1`, etc.
- Last known good: `openclaw.json.last-good`

## Uninstall & Full Cleanup

To completely remove OpenClaw (config, gateway, scheduled task, all data):

### Step 1: Stop the gateway and scheduled task

```bash
openclaw gateway stop        # Stops the Scheduled Task
openclaw gateway uninstall   # Attempts full removal (may warn "still loaded")
```

### Step 2: Kill the gateway node process

The gateway node process holds SQLite files locked even after the scheduled task is stopped. Find and kill it:

```bash
# Find PID listening on gateway port
netstat -ano | grep "18789.*LISTENING" | awk '{print $5}'
# Kill it (MSYS double-slash syntax)
taskkill //f //pid <PID>
```

⚠️ **SQLite lock pitfall**: `rm -rf ~/.openclaw` will fail silently on `state/openclaw.sqlite` and `memory/main.sqlite` (plus -shm/-wal) if the gateway node process is still running. Kill the process FIRST, then delete.

### Step 3: Delete the scheduled task

```bash
cmd.exe /c "schtasks /delete /tn \"OpenClaw Gateway\" /f"
```

### Step 4: Remove all data

```bash
rm -rf ~/.openclaw
```

### Step 5: Verify

```bash
ls ~/.openclaw 2>&1    # Should say "No such file or directory"
netstat -ano | grep 18789  # Should be empty (no LISTENING)
```

## Useful Commands

```bash
openclaw plugins list           # List all plugins and status
openclaw channels status        # Connected messaging accounts
openclaw logs --follow          # Live gateway logs
openclaw doctor --fix           # Auto-repair common issues
```
