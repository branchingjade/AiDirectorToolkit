@echo off
rem OpenClaw Gateway Watchdog - auto-restart on crash
rem Copy to ~/.openclaw/gateway-watchdog.cmd and update paths for your user
set "HOME=C:\Users\HMSJ"
set "TMPDIR=C:\Users\HMSJ\AppData\Local\Temp"
set "OPENCLAW_GATEWAY_PORT=18789"

:loop
echo [%date% %time%] Starting OpenClaw Gateway...
"C:\Program Files\nodejs\node.exe" "C:\Users\HMSJ\AppData\Roaming\npm\node_modules\openclaw\dist\index.js" gateway --port 18789
echo [%date% %time%] Gateway exited with code %errorlevel%, restarting in 5s...
timeout /t 5 /nobreak >nul
goto loop
