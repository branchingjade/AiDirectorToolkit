---
name: windows-shell
description: |
  Safe PowerShell and Windows command patterns when running through bash (MSYS/git-bash)
  on this Windows host. Covers escaping, process management, and tool installation pitfalls.
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [windows, powershell, bash, msys, git-bash, escaping]
    category: devops
---

# Windows Shell Patterns (bash → PowerShell)

On this host, the `terminal` tool runs **bash** (git-bash / MSYS), NOT PowerShell or cmd.exe.
Many Windows-native tools require PowerShell commands. Passing those through bash
introduces escaping traps that look like silent success but corrupt the command.

## The cardinal rule: `$env:VAR` → `\$env:VAR`

Bash interprets `$env` as a shell variable (expanding to empty string). When a
PowerShell variable reference passes through bash unescaped, PowerShell receives
garbage like `:USERPROFILE` and fails with misleading errors.

**Always** backslash-escape the dollar sign:

```bash
# WRONG — bash eats $env, PowerShell sees garbage
powershell -NoProfile -Command "Get-Item '$env:USERPROFILE\.foo'"

# RIGHT — bash passes $env:USERPROFILE through intact
powershell -NoProfile -Command "Get-Item \"\$env:USERPROFILE\.foo\""
```

The same applies to any PowerShell variable: `\$HOME`, `\$PWD`, `\$PROFILE`, etc.

## Safe PowerShell invocation template

```bash
powershell -NoProfile -Command "<PowerShell code with all \$ escaped>"
```

Flags:
- `-NoProfile` — skips profile scripts, faster and avoids side effects
- `-ExecutionPolicy Bypass` — only when running downloaded scripts via `iex`
- `-Command "..."` — the command string; use double-quotes so `\$` works

## Process management on Windows

```bash
# Check if a process is running
powershell -NoProfile -Command "Get-Process 'process-name' -ErrorAction SilentlyContinue"

# Kill a process
powershell -NoProfile -Command "Get-Process 'process-name' -ErrorAction SilentlyContinue | Stop-Process -Force"

# Check for scheduled tasks (auto-restart culprits)
powershell -NoProfile -Command "Get-ScheduledTask -TaskName '*pattern*' -ErrorAction SilentlyContinue"
```

## 磁盘操作权限

Windows 上所有磁盘操作（`diskpart`、`format`、分配盘符、`bcdboot`、`bcdedit /store`）**需要管理员权限**。Hermes 的 terminal 工具继承进程权限，无法在会话中提权。

获取管理员权限的唯一方式：**退出 Hermes → 右键以管理员身份运行**。重启后 terminal 即具备完整磁盘操作能力。

验证当前权限：

```bash
powershell -Command "([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')"
# True = 管理员，False = 普通用户
```

盘符冲突常见场景：

- **幽灵盘符**：`Get-PSDrive` 显示盘符存在但 `Get-Volume` 找不到对应卷 → 旧映射残留
- **盘符占用**：`diskpart assign` 报"指定的驱动器号不可用" → 换未使用的盘符
- **格式化后盘符脱落**：需重新分配

## read_file 误判 binary（UTF-8 中文 .md）— 根因与修复

Hermes 的 `read_file` 读 UTF-8 中文文件（Obsidian .md 普遍如此）时报 `Binary file - cannot display as text` 的根因：`head -c 1000` 截断采样切到 UTF-8 多字节字符中间 → 解码产生 **1 个 U+FFFD** → 旧判定逻辑 `if "\ufffd" in sample` 见 1 个就判 binary。真解码失败（如 GBK 读 UTF-8）会产生几十个 U+FFFD。

**修复**（本地补丁 `hermes-agent/tools/file_operations.py` `_is_likely_binary`）：`"\ufffd" in sample` 改为 `sample[:1000].count("\ufffd") > 1`。验证数据：截断噪声=1 个，GBK 乱码=73 个，随机二进制=432 个——阈值安全。

⚠️ `hermes update` 会覆盖此补丁需重打；升级后若 Obsidian 文件仍报 binary，临时读法：`tr -d '\r' < 文件` 管道（terminal 里，read_file 绕不开）。

## 管理员进程看不到用户映射的网络驱动器（EnableLinkedConnections）

Hermes 终端以管理员权限运行时，`net use` 列表为空、PowerShell `Get-PSDrive` 只有 C 盘——但用户资源管理器能看到 Y/Z 盘。原因：UAC 下提升进程不继承用户会话的网络驱动器映射（`HKCU\Network\<盘符>` 里映射仍存在）。

**修复**：`Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name 'EnableLinkedConnections' -Value 1 -Type DWord`，然后**注销/重启**（登录时才创建链接，当前提升进程不受影响）。映射盘符本身不用重配（注册表 HKCU\Network 记录还在）。

## Multi-step scripts

For multi-step PowerShell, assign a variable first then reference it —
fewer `\$` to sprinkle:

```bash
powershell -NoProfile -Command "\$dir = \"\$env:USERPROFILE\\.foo\"; Remove-Item -Recurse -Force \$dir -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Path \"\$dir\\bin\" -Force | Out-Null"
```

Note: `\\` for literal backslash in directory separators inside double-quoted PowerShell strings.

## 计划任务环境读不到进程 CommandLine（WMI 权限遮罩）— 2026-08-07 实测

**现象**：计划任务跑 PowerShell 检测脚本，`Get-CimInstance Win32_Process` 能枚举进程（Count 正常），但读 `CommandLine` 属性返回**空字符串** → 按命令行匹配的检测逻辑（如 `Where-Object { $_.CommandLine -match 'xxx' }`）永远匹配失败，误判「进程不存在」。

**根因**：WMI 对**非管理员/服务会话**遮罩其他进程的 CommandLine 属性。计划任务默认 `InteractiveToken` 非提权运行 = 非管理员 → 读不到。手动终端（管理员）能读到 → 同一命令两种环境结果不同。

**验证（区分「枚举失败」还是「CommandLine 遮罩」）**：写 probe 脚本落盘结果，用临时计划任务跑，分别测：
```bash
# ①进程枚举（不依赖 CommandLine）
(Get-CimInstance Win32_Process -Filter "Name like 'python%'").Count
# ②CommandLine 读取
Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Select-Object -ExpandProperty CommandLine
# ③当前权限
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```
①正常 + ②空 + ③False = WMI 权限遮罩实锤。

**修复方向**：
1. **换不依赖 CommandLine 的信号**（最可靠）：进程对应的端口监听 `netstat -ano | grep LISTENING`——不读其他进程属性，无权限依赖。中文系统 netstat 输出 GBK，subprocess 需 `errors="replace"`。
2. **计划任务提权**：`schtasks /create /xml` 重建任务，`<RunLevel>HighestAvailable</RunLevel>`（注意枚举值是 **HighestAvailable** 不是 Highest，XML 用 Highest 会报错 `(11,27):RunLevel`）。重建后 `schtasks /query /tn X /xml` 验证。

**schtasks 探测技巧**：`/tr` 参数引号地狱——用独立 .py/.cmd 文件（`/tr` 直接指 python.exe + 脚本绝对路径），不要在 `/tr` 里塞复杂引号；bash 里调 powershell 的 `$` 会被吞，用单引号包住整个 `-Command`；probe 结果落盘到文件再 `cat`，计划任务 stdout 默认不返回。

**排查思维（用户纠正）**：监控/自愈工具误报时，先验证「核心检测机制在目标运行环境下是否真能拿到信号」，别急着在坏检测上加兜底——「不是缺兜底，是工具本身就干不了活」。

## Common pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| "不支持给定路径的格式" / path format not supported | `$env` was eaten by bash; path became `:USERPROFILE\...` | Escape with `\$env:USERPROFILE` |
| Move-Item fails with "文件已存在" / file exists | Target file locked by running process | Kill the process first, then Move-Item |
| Process reappears after kill | Auto-restart mechanism (scheduled task, parent process, startup entry) | Check `Get-ScheduledTask`, `HKCU:\...\Run`, stop the parent first |
| `2>$null` redirect fails | bash interprets `2>` as its own redirect | Use PowerShell-native `-ErrorAction SilentlyContinue` instead |
| bcdedit path 反斜杠被吃掉 | bash 把 `\W` `\E` 等当作转义处理 | 用单引号：`bcdedit /set {id} path '\Windows\...'`；不要用双引号和 cmd /c |
| `bcdedit /set` path values lose backslashes | bash treats `\\` as escape char; `\\Windows` → `Windows` | Use **single quotes**: `bcdedit /set {id} path '\\Windows\\system32\\winload.efi'`. Double quotes, `\\\\`, and `cmd /c` all fail. |
| 计划任务检测脚本报「进程不存在」但进程在跑（gateway/watchdog 类） | WMI 对非管理员遮罩 CommandLine：`Get-CimInstance` 枚举正常但 `CommandLine` 返回空 → 按命令行匹配必然误判 | 改用端口监听（netstat LISTENING）作主判据，或计划任务提权 `<RunLevel>HighestAvailable</RunLevel>`（枚举值不是 Highest）；详见上方「计划任务环境读不到进程 CommandLine」节 |

## .env 文件加载（git-bash）

```bash
# 可靠方式：set -a 自动导出所有变量
set -a && source /path/to/.env && set +a

# 不可靠：单独 source（变量仅在子 shell 生效）
source /path/to/.env    # ❌

# 不可靠：直接 export KEY=value（Hermes 会脱敏）
export GH_TOKEN=xxx     # ❌ 输出被脱敏
```

脚本中用绝对路径执行，放在工作目录下。

## curl + non-ASCII content: always use file body

Windows git-bash corrupts non-ASCII characters (Chinese, emoji, etc.) in inline
`-d`/`--data` strings. The content reaches the server as `?` and is unrecoverable.

**Never inline non-ASCII JSON.** Always write to a temp file with Python (not shell
echo/heredoc, which corrupts the same way), then POST with `--data-binary @file`:

```bash
python3 -c "
import json
payload = {'key': '中文值', 'tags': ['标签1', '标签2']}
with open('/tmp/req.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False)
"
curl.exe -s -X POST http://... -H 'Content-Type: application/json' --data-binary @/tmp/req.json
```

Use `curl.exe` (not bare `curl`, which PowerShell aliases to `Invoke-WebRequest`).

This pattern applies to **any API that accepts non-ASCII content** — Eagle API,
Kimi WebBridge, Feishu, etc. — not just WebBridge.

### curl `-u` Basic Auth with non-ASCII usernames → 401

`curl -u 用户名:密码` encodes credentials via base64 internally. In MSYS/bash,
non-ASCII usernames (e.g. Chinese `妖玉`) are mangled before encoding, producing
a wrong base64 token. The server receives garbled credentials and returns 401 —
even though the password is correct.

**Verification test** (use explicit base64 encoding):

```bash
# WRONG — MSYS mangling → 401
curl -u 妖玉:Huan1120 -X PROPFIND http://localhost:5244/dav/

# RIGHT — explicit base64 with known-good encoding
curl -H "Authorization: Basic $(echo -n '妖玉:Huan1120' | base64)" \
  -X PROPFIND http://localhost:5244/dav/
```

**Windows native clients are NOT affected** — Windows credential system handles
UTF-8 Basic Auth correctly. This is purely a git-bash/MSYS `curl` issue. When
testing WebDAV auth from the terminal, always use the explicit base64 form.

## When the installer script fails

Many Windows tools ship a `irm ... | iex` one-liner installer. When it fails
(move errors, process locks), the fallback is:

1. Kill any running instances of the tool
2. Delete the tool's install directory
3. Download the binary directly with `Invoke-WebRequest -OutFile`
4. Start the daemon and run post-install commands manually

See `references/kimi-webbridge.md` for a worked example.

## 隐藏/消除 Windows 控制台黑窗口

pythonw.exe（GUI 子系统）启动的进程**本不该有控制台窗口**。黑窗口有两个层次的原因，
**先诊断是哪一种再决定修法**：

- **A. 进程内部某 C 扩展调用 `AllocConsole`**（winloop / onnxruntime / Rust/Cython 库）——
  `DETACHED_PROCESS` / `CREATE_NO_WINDOW` 启动标志都挡不住进程内部自建窗口，只能事后隐藏。
- **B. uv venv 的 `Scripts/pythonw.exe` 是 console 子系统 launcher stub（2026-08-07 实测根因）**。
  `file Scripts/pythonw.exe` 显示 `PE32+ executable (console)` 而非 GUI——stub 通过
  `__PYVENV_LAUNCHER__` 环境变量把 venv 上下文传给 base 解释器后 exec 出的还是
  `python.exe`（console 子系统）→ Windows 强制分配 conhost 黑窗口。**这种可以程序层治本**：
  用 PE 头 subsystem 字段（2=GUI / 3=console）识别真 GUI pythonw.exe，绕过 stub 直接启动
  base 的 pythonw.exe，并注入 `__PYVENV_LAUNCHER__=<venv>\Scripts\python.exe` 保住 venv
  上下文（缺失则 sys.prefix 错、site-packages 包 import 失败）。详见
  `hermes-maintenance` 的 Hindsight daemon 黑窗口诊断段。

**程序层治本（B 类，2026-08-07 已验证的完整链路）**：不要只做守卫脚本事后隐藏——改启动方
让它用真 GUI pythonw。实测可行方案：解析 PE 头 subsystem 字段区分 GUI/console 可执行文件，
拒绝 console stub，改用 base 目录（pyvenv.cfg home）的真 GUI pythonw.exe，并注入
`__PYVENV_LAUNCHER__`。验证结果：新 daemon 单进程 pythonw.exe、无 python.exe 子进程、
无 conhost、无窗口，health 检查 200。完整补丁代码（`_pe_subsystem` / `_find_gui_pythonw`
/ `__PYVENV_LAUNCHER__` 注入三件套）见 `references/console-stub-rootcause.md`。

两个关键事实：
- **控制台窗口的所有者是 conhost.exe，不是进程本身**——对 pythonw 的 PID 做
  `GetWindowThreadProcessId` / `Get-Process MainWindowHandle` 返回 0/空，找不到窗口。
  必须枚举**所有**顶层窗口并按**标题**（= 进程路径）匹配。
- 进程有 idle-timeout 自退 + 被网关重新拉起时，窗口会**反复重现**——一次性隐藏不够，
  需要常驻守卫脚本（或程序层治本）。

隐藏模式（PowerShell 一次性）：
```powershell
# 枚举标题含 'pythonw.exe' 的可见窗口，ShowWindow(hwnd, 0) 隐藏
# 完整 Add-Type 代码见 references/desktop-window-investigation.md
```

常驻守卫模式（推荐）：pythonw 跑一个 2 秒轮询的 ctypes 脚本，EnumWindows 匹配标题
标记后 `ShowWindow(SW_HIDE)`，配计划任务开机自启。模板要点：`MARKER` 用进程路径片段
（如 `"hermes-agent\\venv\\Scripts\\pythonw.exe"`）精确锁定目标窗口，不误伤其他 pythonw。

**⚠️ 反斜杠转义陷阱的精确边界（2026-08-07 实测纠正）**：**write_file 本身是安全的**——JSON 传输转义正确，`MARKER = "hermes-agent\\\\venv\\\\Scripts\\\\pythonw.exe"` 落盘后 Python 解析为单反斜杠字符串，`repr()` 显示 `'hermes-agent\\venv\\Scripts\\pythonw.exe'`，匹配真实窗口标题成功（曾误判为 `\x0b` 陷阱，用 `importlib.util.spec_from_file_location` 加载真实文件 + 打印 `repr(MARKER)` 验证过）。**真正踩坑的是在 bash 里手写 `python -c "MARKER='...\\\\venv...'"`**——bash 吃一层转义 + Python 再吃一层，`\\\\v` 变成 `\x0b`（垂直制表符），匹配永远失败且难发现。**修法：验证字符串匹配永远用「加载真实文件模块」而不是 bash 内联 python -c 手写路径**；写完守卫脚本必跑一次单轮验证打印 `repr(MARKER)` 确认无 `\x0b`。

schtasks 注册开机自启（git-bash 里用**单斜杠** `/Create`，`//Create` 双斜杠会被
schtasks 报"无效参数/选项"；成功输出是 GBK 乱码「�ɹ�」，属正常编码噪音，看退出码）：
```bash
schtasks /Create /TN "Hermes-HideHindsightWindow" \
  /TR "\"$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/pythonw.exe\" \"C:\\...\\hide_hindsight_window.py\"" \
  /SC ONLOGON /RL LIMITED /F
# 验证：schtasks /Run /TN "..." && 枚举窗口确认 visible=False
```

**Hindsight daemon 黑窗口（本机实例）**：Hermes 网关（`hermes_cli.main serve`）拉起的
`hindsight_api.main --daemon --idle-timeout 300 --port 9177`（Hindsight 记忆服务）会造
黑窗口。**已做程序层治本**：patch 了 `venv/Lib/site-packages/hindsight_embed/daemon_embed_manager.py`
（PE subsystem 识别 + 真 GUI pythonw + `__PYVENV_LAUNCHER__` 注入，详见
`references/console-stub-rootcause.md`），**需重启 Hermes 才生效**；`hermes update`
会覆盖补丁需重打。过渡期守卫脚本 `C:\Users\HMSJ\Documents\Hermes\scripts\hide_hindsight_window.py`
（2 秒轮询 EnumWindows 隐藏）+ 计划任务 `Hermes-HideHindsightWindow`（ONLOGON）。
卸载守卫：`schtasks /Delete /TN "Hermes-HideHindsightWindow" /F`。

## References

- `references/console-stub-rootcause.md` — **console stub 黑窗口根因 + 程序层治本**（PE subsystem 解析正确写法、daemon_embed_manager 三件套补丁、__PYVENV_LAUNCHER__ 注入、端到端验证步骤、生产生效注意）
- `references/desktop-window-investigation.md` — **桌面神秘窗口调查 + 隐藏**：ctypes 枚举窗口（含控制台窗口属于 conhost.exe 的陷阱、按标题匹配而非 PID）、截图识别、ShowWindow 隐藏、常驻守卫脚本模式
- `references/browser-agent-cdp-windows.md` — **Agent-Browser CDP mode**: `--session` hangs on Windows, use `--cdp <port>` with Chrome `--remote-debugging-port` instead. Covers persistent login profiles, form interaction via eval, and Hermes integration limitations.
- `references/kimi-webbridge.md` — Kimi WebBridge installation: full workflow, pitfalls, and verification
- `references/github-cli-windows.md` — GitHub CLI on Windows: config path, keyring token storage, backup workaround
- `references/desktop-window-investigation.md` — **Desktop window investigation**: enumerate visible windows via Python ctypes Win32 API, capture screenshots, and identify unknown desktop windows. Use when the user asks about a mysterious window on their desktop.
- `references/windows-esp-repair.md` — **ESP 引导修复完整工作流**: 诊断 → bcdboot（优先）→ 手动 BCD 重建（bcdboot 失败时，含安全启动陷阱、版本匹配铁律、bcdedit 反斜杠转义）。覆盖全部 pitfall。
