---
name: hermes-maintenance
description: "Keep Hermes Agent running: diagnose ImportError after updates, restart gateway, check process state."
version: 1.1.0
platforms: [windows, linux, macos]
---

# Hermes Maintenance

Operational patterns for keeping Hermes Agent healthy — updating, restarting components, and diagnosing common post-update failures.

## Trigger

- Hermes throws `ImportError` or `AttributeError` for things that clearly exist in the source on disk
- After running `hermes update` or `git pull` in the hermes-agent repo
- Gateway responses are stale or erroring while the desktop app works fine
- **Quick health check after any fix:** see `references/quick-health-check.md` for the verification checklist
- **Hindsight 记忆 recall 报 localhost:8888 拒绝连接 / memory status 全绿但记忆不工作:** see `references/hindsight-port-mismatch.md` — mode 与 daemon 端口不匹配根因 + 诊断 + 修复 + **端到端实测配方（HindsightEmbedded client 三连：拉起→health→memories.list 真读记忆，用户问「确认无误？」时必须跑）** + client API 坑（recall/search 都不存在，正确入口是 `memories.list`）
- **Feature discovery / config audit:** user asks what features they're not using, or post-upgrade "what's new" review — see `references/config-audit-feature-discovery.md` for the parallel-command workflow and analysis framework

## Diagnostic: `hermes` CLI fails with uv trampoline error

**Symptom:** Every `hermes` command — even `hermes --version` — fails with:

```
error: uv trampoline failed to canonicalize script path
```

The `hermes.exe` in the venv's `Scripts/` dir is a PE32+ executable (uv-generated console-script launcher), not a plain Python script.

**Root cause:** uv's trampoline mechanism can't resolve the script path. Observed with uv 0.11.25 on Windows after updates or path changes. The venv Python itself (`venv/Scripts/python.exe`) still works fine — only the trampoline wrapper executables are affected.

**Workaround — invoke via Python directly:**

The entry point is `hermes_cli.main:main`. All CLI commands work when invoked through Python:

```bash
# Gateway restart (or any hermes subcommand)
cd ~/AppData/Local/hermes/hermes-agent
./venv/Scripts/python.exe -c "
import sys
sys.path.insert(0, r'C:\Users\<user>\AppData\Local\hermes\hermes-agent')
from hermes_cli.main import main
sys.argv = ['hermes', 'gateway', 'restart']
main()
"
```

**Pitfall:** If the Python invocation fails with `ModuleNotFoundError: No module named 'hermes'`, add `sys.path.insert(0, ...)` pointing to the hermes-agent source directory (editable install). The `__editable__.hermes_agent-*.pth` file in `venv/Lib/site-packages/` confirms the editable install but the finder may not activate for `-c` invocations.

**Permanent fix — reinstall editable package:**

The trampoline launchers are corrupted/misaligned with the venv state. A full editable reinstall rebuilds them:

```bash
cd ~/AppData/Local/hermes/hermes-agent
uv pip install -e . --reinstall
```

This also updates any stale transitive dependencies (starlette, uvicorn, etc.) that may have drifted. After this, `hermes --version` and all subcommands work normally.

**Verify the fix:**

```bash
hermes --version
hermes gateway status
```

**Pitfall: `hermes gateway restart` may exceed 30s timeout.** The command waits for the new process to fully initialize (including connecting to all messaging platforms like Feishu). The actual restart happens — check with `hermes gateway status` to confirm the new PID. For faster restarts, use:

```bash
hermes gateway stop && sleep 2 && hermes gateway start
```

**Pitfall: `hermes doctor` can hang (>15s).** Not suitable for quick triage. Use targeted checks instead:
- `hermes --version` — basic CLI health
- `hermes gateway status` — gateway liveness
- Direct Python import check for specific errors (see diagnostic above)

**Pitfall: venv rebuild race condition during desktop startup.** If the desktop bootstrap triggers a `uv sync` or venv repair, transient `ImportError` can occur on the first 1-2 backend launch attempts. The Electron boot loader has built-in retry logic — don't panic if the first launch fails. Check `desktop.log` for the pattern:
```
ImportError: cannot import name 'load_dotenv' from 'dotenv' (unknown location)
→ backend exited (1) → retrying → eventually succeeds
```

**Verify the workaround (fallback when `hermes` CLI is dead):**

```bash
./venv/Scripts/python.exe -c "
import sys; sys.path.insert(0, r'C:\Users\<user>\AppData\Local\hermes\hermes-agent')
from hermes_cli.main import main; sys.argv=['hermes','gateway','status']; main()
"
```

## Diagnostic: 全局 pip 装包撕坏 Hermes venv（cryptography ImportError，实测 2026-08-06）

**Symptom:** `hermes` 命令突然全崩——任何子命令都报 `ImportError: cannot import name 'hashes' from 'cryptography.hazmat.primitives' (unknown location)`。venv 里 cryptography 包文件被撕了一半（只剩 hazmat/x509 子目录，`cryptography/__init__.py` 和 `hashes.py` 等核心文件缺失），pip 也消失（`No module named pip`）。同时 requests 报 `RequestsDependencyWarning: Unable to find acceptable character detection dependency (chardet or charset_normalizer)`。

**Root cause:** 在 bash 会话里跑**全局** Python 的 pip（如 `pip install openviking`）装包时，当前 shell 的 `PYTHONPATH` 指向 Hermes venv——全局解释器启动时也加载了 venv 的 site-packages，pip 在解析/卸载依赖时**把 venv 里的 cryptography、charset_normalizer 当冲突包卸载了**。表象像 venv 损坏，真凶是全局 pip + 污染的环境变量。

**修复（按序）：**
```bash
# 1. 恢复 pip（venv 里 pip 被删了）
cd ~/AppData/Local/hermes/hermes-agent
venv/Scripts/python.exe -m ensurepip

# 2. 重装被撕坏的包（cryptography 是核心；charset_normalizer 看 requests 警告）
venv/Scripts/python.exe -m pip install --force-reinstall cryptography
venv/Scripts/python.exe -m pip install --force-reinstall charset-normalizer

# 3. 验证
venv/Scripts/python.exe -c "import cryptography; print(cryptography.__version__); from cryptography.hazmat.primitives import hashes; print('hashes OK')"
hermes memory status   # 无 warning 即恢复
```

**预防（装任何全局包前）：**
- 检查 `echo $PYTHONPATH` ——非空则 `unset PYTHONPATH` 再跑全局 pip
- 或显式用干净环境：`env -u PYTHONPATH /c/Users/<user>/AppData/Local/Programs/Python/Python312/python.exe -m pip install <pkg>`
- 装的是给 Hermes 用的包 → 直接用 `venv/Scripts/python.exe -m pip install <pkg>`，绝不用全局 pip 碰 venv 依赖
- 触发教训：本会话 `pip install openviking`（外部记忆插件）→ 装完 openviking 本身成功但 venv 崩了——装大依赖树的外部包前先想清楚它会不会动共享依赖（pydantic/cryptography/requests 系）

## Diagnostic: read_file 误判 binary（UTF-8 中文 .md）——根因+本地补丁

**Symptom:** `read_file` 读 UTF-8 中文 .md（Obsidian 知识库文件普遍如此）返回 `is_binary=True` / "Binary file - cannot display as text"，但 terminal 里 `cat`/`grep` 完全正常。

**Root cause（2026-08-06 实测定位，不是 CRLF）：** `tools/file_operations.py::read_file` 用 `head -c 1000` 采样判断 binary。1000 字节边界精确截断——如果第 1000 字节落在 UTF-8 多字节字符中间（中文文件极大概率），解码产生 **1 个 U+FFFD**。旧判定 `if "\ufffd" in content_sample[:1000]: return True` 见 1 个就判 binary。`\r`（CRLF 的 CR）在 non-printable 检查里被排除（`c not in '\n\r\t'`），所以 CRLF 本身不触发——表象是"CRLF 文件读不了"，真凶是截断采样。真解码失败（如 GBK 读 UTF-8）会产生几十个 U+FFFD。

**Fix（本地补丁）：** `_is_likely_binary` 的 U+FFFD 检查改为计数：

```python
if content_sample[:1000].count("\ufffd") > 1:
    return True
```

**验证数据：** 中文文件 1 个 U+FFFD → 放行 ✓；GBK 解码模拟 73 个 → 拦截 ✓；随机二进制 432 个 → 拦截 ✓（防 mojibake 写回的保护零削弱）。

**⚠️ 生效与覆盖：** 补丁需重启 Hermes 桌面应用（进程内已 import 的模块不热加载）；`hermes update` 会覆盖补丁，升级后需重打。升级后若仍报 binary，临时读法：terminal `tr -d '\r' < 文件` 管道。该 bug 值得上报上游——判定注释假设"合法 UTF-8 文本永远不含 U+FFFD"在截断采样场景下不成立。

## 更新 hermes-agent 代码（保留本地修改）

hermes-agent 仓库位于 `~/AppData/Local/hermes/hermes-agent/`，是 git 仓库。桌面端更新或手动 `git pull` 前，先检查本地是否有未提交的修改：

```bash
cd ~/AppData/Local/hermes/hermes-agent
git status
```

**有本地修改时的安全更新流程：**

```bash
git stash          # 暂存本地修改
git pull           # 拉取远程最新
git stash pop      # 恢复本地修改
```

**常见本地修改来源：** 之前调试飞书适配器、网关配置等时手动改的文件（如 `adapter.py`、`config.py`）。这些修改通常没有 commit，`git stash` 可以安全保存。

**Pitfall：** 用户可能不理解 git 术语（"未推送的修改"、"未暂存的更改"等）。用简单语言解释："你之前改过的文件还在，更新前先存起来，更新后恢复回来。"

### `hermes update` 内置的自动 stash 机制（实测 2026-08-07）

`hermes update`（`hermes_cli/update_cmd.py:1085 _stash_local_changes_if_needed`）**不用手动 stash**——它自动执行 `git stash push --include-untracked` → `git pull` → `git stash apply`：

- **本地改动不会直接丢**（含 untracked 新文件，`--include-untracked` 覆盖）
- **但可能冲突**：官方版本若改了同一文件（run.py / feishu_comment.py 等高频率文件），`stash apply` 报冲突，改动停在 stash 里（`git stash list` 可找回），需手动合并
- 先 unmerged index 检查（`git ls-files --unmerged`）→ `git reset` 清冲突标记再 stash

**✅ 标准保险做法：补丁存档 + 重打脚本**（`~/Documents/Hermes/scripts/patches/`，2026-08-07 实测全流程）：

1. `git diff > hermes-local-patches.diff`（修改文件）+ `cp` 新文件到同目录（untracked 的 .py 不进 diff）
2. 写 `reapply-patches.py`：dry-run（`git apply --check`）→ `--apply`（`git apply` + 复制新文件 + `py_compile` 验证）；**自带「已应用检测」**——grep 关键补丁标记字符串（如 run.py 里的注释），已应用则跳过，避免对已打补丁文件重复 apply 报错
3. 覆盖后恢复：`python reapply-patches.py`（检测）→ `python reapply-patches.py --apply`
4. 冲突时：`git apply --3way <diff>` 或对照 diff 逐块合并

注意 MSYS 路径坑：Windows 原生 python 跑脚本要传 Windows 路径（`python "C:/Users/.../reapply-patches.py"`），`~/...` 会被解析成 `/c/Users/...` 而报 `can't open file`。

### Diagnostic: 中断的 update 留下「每次 CLI 调用都重装依赖」循环（实测 2026-08-07）

**Symptom:** 任何 `hermes <子命令>` 首次调用都先打印 `⚠ A previous hermes update was interrupted mid-install — finishing dependency installation now...`，然后 `error: Failed to install: cryptography-48.0.1 ... failed to rename file ... _rust.pyd: 拒绝访问 (os error 5)`，最后 `✗ Could not auto-recover the interrupted install.`——但**命令本身仍正常执行**，gateway 也正常。

**Root cause:** 上次 update 中断在依赖安装中途；每次 CLI 启动都会尝试补完安装，而 gateway 进程正占用 `venv/Lib/site-packages/cryptography/hazmat/bindings/_rust.pyd`（Windows 文件锁），rename 失败。**cryptography 实际可用**（`import cryptography` 正常，version 48.0.1）——这是「安装流程未完成」≠「包坏了」。

**处理：**
- 不影响功能（cryptography import OK、gateway 正常）→ 可以不管，等下次真正 update 时一并清理
- **⚠️ 修复死锁（2026-08-07 实测）：桌面 app 进程也锁 `_rust.pyd`。** 之前以为 `hermes gateway restart` 腾出锁就能修——实际**当前 Hermes 桌面 app 进程同样持有文件锁**，agent 会话内跑 pip 重装必失败（WinError 5）。彻底修复必须在**关闭所有 Hermes 窗口（桌面 app + gateway）后**手动跑修复脚本——本 skill 自带 `scripts/fix_cryptography.py`（部署到 `~/AppData/Local/hermes/scripts/fix_cryptography.py` 后执行；自动：检查无 Hermes 进程 → 备份 cryptography → 删损坏 dist-info → 重装 48.0.1 → 验证 import）。脚本无法在会话内执行——这是死锁，需用户手动两步。
- **⚠️ 损坏的 dist-info 让 pip 直接跳过包**：中断 update 留下的 `cryptography-48.0.1.dist-info` / `cryptography-50.0.0.dist-info` **缺 RECORD + METADATA 无效**，pip 会 `WARNING: Skipping ... due to invalid metadata entry 'name'` 而**不重装**。必须先手动删掉这两个 dist-info 目录（fix 脚本第 2 步做），`--force-reinstall --no-deps cryptography==48.0.1` 才生效。
- 排查时别被 `error: Failed to install` 吓到——先验证 `venv/Scripts/python.exe -c "import cryptography; print(cryptography.__version__)"` 是否正常，正常就只是循环噪音

## Diagnostic: stale process after code update

**Symptom:** `ImportError: cannot import name 'X' from 'agent.module'` — the constant/function exists in the source file on disk but the running process can't find it.

**Root cause:** The gateway is a persistent background process. It loads Python modules once at startup. When source code is updated on disk (via `hermes update`, `git pull`, or desktop auto-update), the running gateway still holds the pre-update bytecode in memory. Restarting the desktop app does NOT restart the gateway.

**Verify:** Check if the constant exists in the source and can be imported from a fresh Python:

```bash
cd ~/AppData/Local/hermes/hermes-agent  # Windows
./venv/Scripts/python.exe -c "from agent.prompt_builder import PARALLEL_TOOL_CALL_GUIDANCE; print('OK')"
```

If that succeeds but Hermes still fails → stale gateway process.

**Fix:**

```bash
hermes gateway restart
```

If restart fails (e.g., Scheduled Task doesn't recover), try stop then start:

```bash
hermes gateway stop
hermes gateway start
```

Verify:

```bash
hermes gateway status
# Should show: ✓ Gateway process running (PID: N)
```

Then check logs for absence of the error:

```bash
grep "ImportError" ~/AppData/Local/hermes/logs/gateway.log | tail -5
```

## Gateway 自愈看门狗（watchdog，2026-08-07 建成实测）

**触发场景**：gateway 挂了要自动拉起 + 告警（飞书/其他渠道不因 gateway 死亡而失联）。

**核心架构约束：cron 住在 gateway 进程里——gateway 挂了 cron 也停。** 任何「Hermes 内部」的定时检查（cron/kanban dispatcher/webhook 平台）都无法在 gateway 死亡时工作。自愈检测必须**外置**：Windows 计划任务跑独立脚本，与 Hermes 进程零依赖。

### 组件（已部署）

| 组件 | 位置/形式 |
|---|---|
| watchdog 脚本 | `~/AppData/Local/hermes/scripts/gateway_watchdog.py`（独立 Python，跑完即退无常驻） |
| 计划任务 | `Hermes_Gateway_Watchdog`，每 5 分钟，`StartWhenAvailable` + 2min 执行时限 |
| 标记文件 | `~/AppData/Local/hermes/state/gateway_outage.json`（停机窗口 + 防风暴记录） |
| 告警信道 | `lark-cli`（Node 独立 CLI，用自己的 OAuth——**gateway 死了它照样能发**）→ 管理员 DM |

### 检测逻辑（关键：别只看进程名）

- **硬信号**：`Get-CimInstance Win32_Process` + CommandLine 匹配 `hermes_cli.main gateway`。必须匹配命令行而非进程名——`python.exe` 有子代理/其他服务（Eagle 插件等）混淆。
- **软信号**：gateway.log mtime 超 10 分钟 = 疑似卡死（housekeeping 60s 有日志，10min 阈值不误报）。
- **防风暴**：标记文件 `last_restart_at`，30 分钟冷却期内不重复拉起。

### ⚠️ CLI 命令会杀 gateway（2026-08-07 实测两次）

`hermes gateway status` / `hermes cron list` / `hermes gateway start` 可能触发**中断的 update 恢复流程**（pip 补装 cryptography），恢复失败时连带停 gateway——日志特征 `Received UNKNOWN as a planned gateway stop` + `Shutdown context: signal=UNKNOWN`。当日 10:56 和 14:39 两次宕机都是此因。**修 cryptography 前别跑这些命令**；watchdog 防风暴要扛住「gateway 起来又被命令弄停」的反复横跳。

### 计划任务注册要点（Windows）

```powershell
$action = New-ScheduledTaskAction -Execute '<venv>\Scripts\python.exe' -Argument '<scripts>\gateway_watchdog.py'
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 2)
Register-ScheduledTask -TaskName 'Hermes_Gateway_Watchdog' -Action $action -Trigger $trigger -Settings $settings -Force
```

**坑**：`RepetitionDuration` 用 `([TimeSpan]::MaxValue)` 报 XML 校验错（0x80041318）——用 365 天上限。暂停/恢复：`Disable-ScheduledTask` / `Enable-ScheduledTask -TaskName Hermes_Gateway_Watchdog`。

### 设计决策：自动补消息 cron 不做（用户拍板）

watchdog 把宕机窗口从小时级压到 5-10 分钟 → 漏消息量极小 → 让用户重发成本低。LLM 自动给真人发补回复有答非所问风险（比不回更糟）。补消息保持手动：需要时走 feishu-outage-recovery skill 全流程（拉窗口消息→看内容→人工把关回复）。

### 两个 webhook 别混淆（2026-08-07 实测纠正）

推理「gateway 挂了谁能发告警」时容易把两种 webhook 混为一谈，被用户纠正过：

| | 归属 | gateway 挂了会怎样 |
|---|---|---|
| **Hermes 自带 webhook 平台**（`gateway.platforms.webhook`，监听 8644 端口，是 gateway 的一个 platform，日志 `Gateway running with 2 platform(s)` 里的一个） | gateway 进程内 | 随 gateway 一起死 |
| **飞书群自定义机器人 webhook**（`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`） | 飞书服务器，与 Hermes 零依赖 | 照常可推——gateway 死后唯一能出去的告警信道 |

**结论**：gateway 死后推送只能走外部信道（飞书群机器人 webhook，或本机已部署的 lark-cli——Node 独立 CLI 用自己的 OAuth，gateway 死了照样发）。Hermes 自带的 webhook 平台（8644）不是兜底信道。

## Gateway lifecycle

The gateway runs as a Scheduled Task (`Hermes_Gateway`) on Windows, or a systemd user service on Linux/macOS. It persists across desktop app restarts.

| Action | Command |
|--------|---------|
| Status | `hermes gateway status` |
| Start | `hermes gateway start` |
| Stop | `hermes gateway stop` |
| Restart | `hermes gateway restart` |
| Logs | `tail -f ~/AppData/Local/hermes/logs/gateway.log` |

## Remote gateway access: 另一台电脑的 Hermes 连本机

**触发场景：** 用户问"你的远程网关 URL"/"让外部设备连进来"/"另一台电脑的 Hermes 直接用这台的 Hermes"——不是聊天接入，是 **Hermes 实例间互联**。Hermes 本身没有"远程网关 URL"这种东西，网关跑在本地，外部设备通过官方远程模式接入。

**官方机制：** Hermes 桌面版 **"Connect to existing Hermes"**（远程网关模式，`apps/desktop/README.md`）。B 机桌面 UI 显示，但 agent 工具/终端命令/文件操作全部跑在 A 机——*"the gateway host is the execution boundary"*。A 机暴露 `hermes serve`（headless JSON-RPC/WebSocket 后端，`hermes_cli/web_server.py`），默认 `127.0.0.1:9119`，支持 `--host`/`--port`。会话/记忆/技能跟随 A 机（同一 HERMES_HOME）。桌面版自带 serve 是 `--host 127.0.0.1 --port 0`（随机端口），另起对外 serve 无冲突。

**⚠️ 2026-06 安全加固（勿用旧知识）：** `--insecure` 已失效，不再绕过鉴权（hermes-0day MCP-persistence 漏洞后修复）。鉴权真值表（`should_require_auth`，web_server.py:472）：
- host == loopback（127.0.0.1/localhost/::1）→ 免鉴权（本地可信）
- host 非 loopback（**包括局域网 IP**——RFC1918 按 PUBLIC 处理，同 LAN 恶意设备就是威胁模型）→ **强制 auth provider**：OAuth 或内置密码插件，否则拒绝绑定

**密码鉴权配置（内置 `dashboard.basic_auth` 插件，无需 OAuth IDP）：**
- config.yaml `dashboard.basic_auth.username` + `password_hash`（scrypt，首选，不存明文）或 `password`（明文，加载时内存哈希）
- 生成 hash：`python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"`
- `secret` = 会话 token 的 HMAC 签名密钥（32+ 随机字节，留空则随机 per-process，重启失效）；`session_ttl_seconds` 默认 12h
- env 覆盖（env 非空时优先）：`HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `_PASSWORD_HASH` / `_PASSWORD` / `_SECRET` / `_TTL_SECONDS`
- username 留空 = 插件 no-op（不注册密码鉴权）

**启动对外服务：**
```bash
hermes serve --host 0.0.0.0 --port 9119   # 非回环绑定，必须已配 auth provider
```
Windows 防火墙需放行 hermes.exe 入站（通常已有规则）。B 机连接：桌面版首次启动 → Connect to existing Hermes → `http://<A机IP>:9119` + 用户名/密码。

**异地连接选型（无公网服务器时 Tailscale 最优）：**

| 方案 | 前提/代价 |
|------|-----------|
| **Tailscale**（推荐） | 免费个人版，WireGuard 加密，NAT 穿透自动，免公网服务器；登录需访问 login.tailscale.com（国内需代理） |
| ZeroTier | 同类备选，中继质量不如 Tailscale |
| cloudflared | 需域名 + Cloudflare 账号 |
| frp | 需一台公网 IP 服务器 |
| 路由器端口映射 | 国内家宽基本 CGNAT 无公网 IPv4，不通 |
| 花生壳等商业穿透 | 实名 + 免费版限速限流 |

**Tailscale 安装（Windows）：**
```bash
winget install --id Tailscale.Tailscale --accept-source-agreements --accept-package-agreements --silent
powershell -NoProfile -Command "Start-Service Tailscale"
"/c/Program Files/Tailscale/tailscale.exe" up
```
- `tailscale up` 生成一次性登录 URL 并**阻塞等待登录**；登录 URL 超时作废，重跑 up 生成新的
- ⚠️ 实测坑（2026-08-06）：up 经管道/后台跑时 **stdout 全缓冲，poll 拿不到 URL**——改用前台 `tailscale status`（打印 `Log in at: <url>`）拿链接，或让用户走系统托盘 GUI（tailscale-ipn 进程）点 Sign in
- ⚠️ 装完可能报 `timeout waiting for Tailscale service to enter a Running state`（exit 1）→ `powershell -NoProfile -Command "Restart-Service Tailscale -Force"` 后重跑 up
- ⚠️ 给用户登录链接：直接给文本 URL 让用户复制到自己浏览器（open_preview 预览窗格打开外部登录页实测不可靠，用户反馈"没打开"）
- ⚠️ 用户口头确认"好了"≠授权成功：`tailscale up` 阻塞到授权完成才退出；`tailscale status` 显示 Logged out = 只登录了官网、没点设备 Connect，需重新授权

详细配置流程与源码定位：`references/remote-gateway-access.md`

## Gateway 中断自动恢复机制（crash recovery，实测 2026-08-06）

Hermes 内置了中断会话自动恢复：gateway 意外关闭后重启，会**自动续跑**中断的渠道会话（飞书/微信/Telegram 等全部渠道通用），并在恢复时向模型注入系统提示说明中断原因。用户问"意外关闭后能否自动继续"——答案是有，但要分清两条路径：

### 路径一：优雅重启/关闭（`hermes gateway restart`、`/restart`、`hermes update`）

- 停机前 drain 阶段调用 `mark_resume_pending(session_key, "restart_timeout"/"shutdown_timeout")`（run.py:12774），在 drain 等待前就把 durable 标记写入——即使 drain 中被杀也能恢复
- 启动时 `_schedule_resume_pending_sessions()`（run.py:10396）自动恢复所有 resume_pending 会话
- 日志证据：`Scheduled auto-resume for N restart-interrupted session(s)`

### 路径二：异常退出（SIGKILL / 断电 / OOM / VM death）

- 优雅退出会写 `.clean_shutdown` 标记；异常退出没有 → 启动时检测到标记缺失 → 调 `suspend_recently_active(max_age_seconds=120)`（session.py:2850）把**最近 120 秒内活跃**的会话标记为 resumable（reason=`restart_interrupted`）
- 非正常退出检测由 lifecycle_ledger（NS-608）负责：`state/gateway.lifecycle.json` sentinel + 30s 心跳，下次启动时日志出现 `exited UNCLEANLY (SIGKILL / OOM / VM death)`，详情落 `gateway-exit-diag.log`
- 恢复时 `build_resume_recovery_note()`（run.py:1002）注入系统提示："The previous turn was interrupted by a gateway restart/shutdown/interruption; the gateway is now back online"——模型恢复后第一句就会向用户说明中断原因
- 防重启循环：restart_loop_guard 检测连续 SIGTERM 重启中断，超阈值跳过 auto-resume 一次（防御 3，#30719）

### 排查命令

```bash
LOG_DIR="$(dirname "$(hermes config path)")/logs"
grep "Scheduled auto-resume" "$LOG_DIR/gateway.log" | tail     # 恢复是否发生
grep "exited UNCLEANLY" "$LOG_DIR/gateway.log" | tail          # 是否异常退出过
grep "skipping session suspension" "$LOG_DIR/gateway.log"      # 上次是否优雅退出
grep "previous_unclean_exit" "$LOG_DIR/gateway-exit-diag.log"  # 异常退出详情（含 last_heartbeat_at）
```

### 已知限制（诚实告知用户）

1. **桌面端会话不在覆盖范围**：resume_pending 机制只作用于 gateway 渠道会话。桌面 app（desktop 会话）是独立进程，app 意外关闭后不自动恢复——需重开 app 后手动从会话列表继续（`/continue`）
2. **异常退出只恢复 120 秒内活跃的会话**：`max_age_seconds=120` 是硬编码默认，空闲超过 2 分钟的会话不自动续跑（但下次发消息仍从原历史继续，不丢上下文）
3. 恢复是全局的（按 session_key），不区分平台——用户说"不只是飞书渠道"时，直接确认：所有 gateway 渠道同一机制

## Diagnostic: Hindsight daemon 黑窗口（uv venv pythonw console stub，2026-08-07 根因）

**Symptom:** 桌面上出现一个黑窗口，标题是 `C:\...\hermes-agent\venv\Scripts\pythonw.exe`。
它是 Hindsight 记忆服务的 daemon（`hindsight_api.main --daemon --idle-timeout 300 --port 9177`），
由 Hermes 网关（`hermes_cli.main serve`）拉起，空闲 5 分钟自退、再次调用时重启 → 窗口反复重现。

**Root cause（复现实验坐实，不是 AllocConsole 假说）：** uv 创建的 venv 里
`Scripts/pythonw.exe` 是 **console 子系统 launcher stub**（`file Scripts/pythonw.exe` 显示
`PE32+ executable (console)`，真 GUI pythonw 应显示 GUI subsystem）。进程链：

```
gateway(9664) → venv\Scripts\pythonw.exe(9468, console stub)
  → hermes-runtime\...\python.exe(51064, console)  ← stub 用 __PYVENV_LAUNCHER__ 把 venv 上下文传给 base 解释器后 exec 出的还是 console python
    → conhost.exe  ← 黑窗口宿主（窗口标题=进程路径，但 HWND 属于 conhost，不是 pythonw）
```

`daemon_embed_manager._windows_gui_interpreter()`（site-packages/hindsight_embed/daemon_embed_manager.py）
注释声称 pythonw "never allocates a console"——该假设对 uv venv 不成立。`DETACHED_PROCESS` /
`CREATE_NO_WINDOW` 启动 flags 管不到 stub 内部 exec，所以只能程序层治本或事后隐藏。

**程序层修复（已写入 daemon_embed_manager.py，+97 行，2026-08-07 端到端验证通过）：**
1. `_pe_subsystem(exe)`：读 PE 头 subsystem 字段（PE32 magic 0x10B / PE32+ 0x20B → **Subsystem 都在 Optional Header 偏移 +68**，+88 是数据目录、曾写错；2=GUI / 3=console）
2. `_find_gui_pythonw()`：按优先级搜真 GUI pythonw.exe——preferred_dir → sys.executable 旁 → pyvenv.cfg home → PATH，只收 subsystem==2
3. `_windows_gui_interpreter()` 重写：先拒 console stub，只返回 GUI subsystem 的 pythonw；console stub 保留为最后兜底
4. **`__PYVENV_LAUNCHER__` 注入**（`_start_daemon_locked` 的 Popen 前）：`env["__PYVENV_LAUNCHER__"] = str(Path(sysconfig.get_path("scripts")) / "python.exe")`——真 base pythonw 没有 venv 上下文，缺失此变量则 sys.prefix 错、site-packages 的 pywintypes 等 import 失败

**验证结果（2026-08-07 实测）：** 补丁后 daemon 单进程 pythonw.exe、无 python.exe 子进程、无 conhost、无窗口，health 200。验证方法：复刻 `_start_daemon_locked` 的 env（`os.environ.copy()` + `HINDSIGHT_API_LLM_API_KEY` 从 Hermes .env 的 `HINDSIGHT_LLM_API_KEY` 读——**hindsight config.json 里没有 key**）+ 独立端口启动 + 轮询 `/health` + EnumWindows 确认无可见窗口。

**⚠️ 覆盖风险：** 补丁在 site-packages（`hindsight_embed/daemon_embed_manager.py`），`hermes update` / pip 升级 hindsight-embed 会覆盖，需重打。完整补丁代码与验证步骤见 windows-shell skill 的 `references/console-stub-rootcause.md`。**生效条件：需重启 Hermes**（gateway 进程内存里是旧模块）。过渡期守卫脚本 `C:\Users\HMSJ\Documents\Hermes\scripts\hide_hindsight_window.py` + 计划任务 `Hermes-HideHindsightWindow`（ONLOGON，schtasks 注册，详见 windows-shell skill）。

**诊断技巧：** 黑窗口按 PID 找不到归属（conhost 持有 HWND）——用 `Get-CimInstance Win32_Process`
查命令行建进程树，或枚举顶层窗口按标题匹配。排查端口归属：`netstat -ano | grep <port> | grep LISTENING`。

## Diagnostic: Hindsight recall 连不上 daemon（status 全绿但端口不匹配，2026-08-07 根因）

**Symptom:** `hindsight_recall` 报 `Cannot connect to host localhost:8888`，但 `hermes memory status` 全绿（Provider: hindsight + Plugin: installed ✓ available ✓ active ✓）。**状态全绿 ≠ 记忆可用**——status 只查插件安装/本地 runtime，不验证 daemon 连通性，必须实测。

**Root cause:** `$LOCALAPPDATA/hermes/hindsight/config.json` 的 mode 与 daemon 实际状态脱节：
- mode=`local_external` 且未配 `api_url` → 插件客户端默认连 `localhost:8888`（`plugins/memory/hindsight/__init__.py:57 _DEFAULT_LOCAL_URL`）
- 但 daemon 实际跑在**动态端口**（本机 9177）——命名 profile（hermes）不走固定 8888：`hindsight_embed/profile_manager.py _resolve_ports` 对无显式端口/legacy metadata 的命名 profile 调 `_allocate_port` 随机分端口；只有 default profile 固定 8888
- 佐证：`logs/hindsight-embed.log` 里 `Daemon Started (hermes @ :9177)` 是 `local_embedded` 路径的产物——daemon 由嵌入式管理器启动，config 却是 `local_external`，两边不一致

**Mode 语义（决定修法）：** `local_embedded` = Hermes 自动拉起/空闲关闭/动态端口自动发现（**推荐**）；`local_external` = 用户自管 daemon，必须手动配 `api_url`（缺省 8888）；`cloud` = 云端 api.hindsight.vectorize.io。**额外陷阱：`idle_timeout: 300`** = daemon 空闲 5 分钟自退，local_external 模式没人拉起 → 配好 api_url 也会间歇性失联。

**⚠️ 桌面 App 设置面板没有 local_embedded 选项（2026-08-07 用户实测「选项中没有local_embedded」）：** 桌面「记忆与上下文」→ Hindsight settings 的 Mode 下拉框**只有 Cloud 和 Local External 两个选项**——桌面面板用 `hermes-agent/plugins/memory/hindsight/config_schema.py` 渲染，它只声明这两个 options；`local_embedded` 只存在于插件内部 schema（`__init__.py` 的 `_CONFIG_SCHEMA`）。**结论：UI 上无法选 local_embedded，只能手动编辑 `$LOCALAPPDATA/hermes/hindsight/config.json` 改 mode**；UI 可行路径 = Mode 选 Local External + API URL 填 `http://localhost:<实际端口>` + API key 留空（本机服务不要 key，黄标「API key not set」可忽略）。

**端口可预测（hash 而非纯随机）：** 命名 profile 的 daemon 端口由 `_allocate_port` = `8889 + (sha256(profile_name) % 1000)` 算出（`profile_manager.py:513`），**同一 profile 名端口固定**（hermes → 9177），重启不变——除非 .env 显式覆盖或 legacy metadata 里存了旧端口。所以修 local_external 时直接写死 `http://localhost:9177` 即可，不用担心 daemon 重启后变。

**修复（按用户能操作的程度排序）：** ① UI 上 Mode 选 Local External + API URL 填实际端口（用户可自助，无需动文件）；② 手动改 config.json mode 为 `local_embedded`（需改文件，但一劳永逸——Hermes 自动管理 daemon 生命周期 + 端口自动发现）；③ 保持 local_external + 加 `"api_url": "http://localhost:<端口>"`——daemon 需手动常驻，且 idle 5 分钟会退，不推荐。

**用户沟通偏好（排障解释必须大白话）：** 用户两次「看不懂」后才定稿——第一轮解释要用比喻（「记忆库管家住 9177 号房，Hermes 记成 8888 敲错门」），再给技术细节（mode/api_url/端口）。先给结论「配好了/没配好」，再讲为什么。

完整诊断命令与源码定位：`references/hindsight-port-mismatch.md`

## Diagnostic: cron jobs all fail with "config drifted"

**Symptom:** All (or most) cron jobs fail with `last_status: error`. Manual `cronjob action=run` returns:

```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted since this job was created (provider 'deepseek' -> 'xiaomi'; model 'deepseek-v4-pro' -> 'mimo-v2.5-pro'), and this job is unpinned.
```

**Root cause:** The global inference config (provider/model) was changed (e.g. switching models for debugging). Cron jobs created before the change have `provider_snapshot`/`model_snapshot` frozen to the old config. When the scheduler detects the drift and the job has no explicit `model`/`provider` pinned, it blocks the run as a safety measure.

**Fix — clear snapshots permanently (recommended):**

**User preference:** Cron jobs MUST NOT pin model/provider. The user frequently switches global models for debugging. Jobs should seamlessly follow whatever the current global config is. Always clear snapshots rather than pinning.

Setting snapshots to `None` disables drift detection entirely — jobs follow the global config forever, no maintenance needed on model switches:

```python
import json
path = 'C:/Users/HMSJ/AppData/Local/hermes/cron/jobs.json'  # Windows
with open(path) as f:
    d = json.load(f)
for j in d['jobs']:
    j['provider_snapshot'] = None
    j['model_snapshot'] = None
with open(path, 'w') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
```

Verify with `cronjob action=run job_id=<any_id>` — should return `execution_success: true`.

**Alternative — update snapshots to current values (not recommended):**

If you want drift detection to remain active (blocking unexpected expensive model changes), update snapshots instead of clearing them:

```python
j['provider_snapshot'] = '<current_provider>'  # e.g. 'xiaomi'
j['model_snapshot'] = '<current_model>'         # e.g. 'mimo-v2.5-pro'
```

⚠️ This re-breaks on every future model switch.

**Pitfall:** The `cronjob action=update` API does NOT accept empty model/provider — `model=''` returns `"No updates provided"`. You must edit jobs.json directly. The API also can't clear snapshots; only direct JSON editing works.

**Pitfall:** `cronjob action=run` dispatches jobs **sequentially** (one at a time). The scheduled tick dispatches in parallel by default (`max_workers=None` = unbounded thread pool, configurable via `cron.max_parallel_jobs` or `HERMES_CRON_MAX_PARALLEL` env var). Don't judge cron speed by manual `run` — scheduled execution is much faster for multi-job batches.

**Pitfall:** jobs.json uses `id` (not `job_id`) as the key field. The `cronjob` API exposes it as `job_id` but internally it's `id`.

## MoA (Mixture of Agents) configuration & troubleshooting

MoA (`/moa`) runs reference advisors in parallel behind an aggregator model.
When it silently doesn't work, the cause is almost always one of these three:

- **Provider for reference/aggregator has no API key.** MoA's preset slots
  (`reference_models[*].provider`, `aggregator.provider`) are **not validated
  against credentialed providers**. If a preset says `openrouter` and
  `OPENROUTER_API_KEY` is missing, every MoA turn fails silently.
- **Flat keys under `moa:` are ignored when presets exist.** The legacy
  `moa.reference_models`, `moa.aggregator`, etc. are only promoted to the
  default preset when there are **no presets** at all. If `moa.presets:`
  has even one entry, every flat key under `moa:` is dead — the config
  parser never looks at them.
- **`hermes config set` can't write nested lists/dicts cleanly.**
  Schema-valid keys like `moa.presets.default.reference_models` require
  YAML sequences; the CLI serialiser can't round-trip them. The fix is
  direct YAML editing (Python `yaml.safe_load`/`yaml.dump`) as shown below.

Use `/moa <prompt>` for a single fire-and-forget MoA turn (model is
auto-restored after). Select a MoA preset from `/model` to apply it
for the whole session.

### Quick diagnosis

```bash
# 1. Check what presets exist (parsed *after* legacy promotion)
python -c "
import yaml; c=yaml.safe_load(open('$LOCALAPPDATA/hermes/config.yaml',encoding='utf-8'))
moa=c.get('moa',{})
print('presets:', list(moa.get('presets',{}).keys()))
print('default_preset:', moa.get('default_preset',''))
print('flat keys ignored:', [k for k in moa if k not in ('presets','default_preset','active_preset','save_traces','trace_dir')])
"
# 2. Check providers referenced vs credentials available
python -c "
import yaml,json
c=yaml.safe_load(open('$LOCALAPPDATA/hermes/config.yaml',encoding='utf-8'))
a=json.load(open('$LOCALAPPDATA/hermes/auth.json'))
creds=set(a.get('credential_pool',{}).keys())
for pn,p in c.get('moa',{}).get('presets',{}).items():
    ref_provs=set(r.get('provider','') for r in p.get('reference_models',[]))
    agg_prov=p.get('aggregator',{}).get('provider','')
    missing=ref_provs|{agg_prov} - creds
    if missing: print(f'  {pn}: MISSING {missing}')
    else: print(f'  {pn}: all providers credentialed ✓')
"
# 3. Available providers on this machine
python -c "
import json
a=json.load(open('$LOCALAPPDATA/hermes/auth.json'))
for p,entries in a.get('credential_pool',{}).items():
    print(f'  {p}: {len(entries)} key(s)')
"
```

### Fix recipe

```python
import yaml
path = 'C:/Users/HMSJ/AppData/Local/hermes/config.yaml'
c = yaml.safe_load(open(path, encoding='utf-8'))
moa = c.setdefault('moa', {})

# 1. Remove stray flat keys (dead — ignored when presets exist)
for stray in ['reference_models','aggregator','max_tokens','fanout','enabled']:
    moa.pop(stray, None)

# 2. Rebuild presets using ONLY providers you have keys for
presets = moa.setdefault('presets', {})
presets['default'] = {
    'enabled': True,
    'reference_models': [
        {'provider': 'deepseek', 'model': 'deepseek-v4-pro'},
        {'provider': 'xiaomi', 'model': 'mimo-v2.5-pro'},
    ],
    'aggregator': {'provider': 'deepseek', 'model': 'deepseek-v4-pro'},
    'max_tokens': 4096,
    'fanout': 'per_iteration',
}
moa['default_preset'] = 'default'
moa.pop('active_preset', None)

with open(path, 'w', encoding='utf-8') as f:
    yaml.dump(c, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
```

Then `/reset` (or restart session) to pick up the change. Full details
including the config schema, legacy backward-compat rules, and the slash
command lifecycle are in `references/moa-config-deep-dive.md`.

## Browser toolset: dependency on agent-browser

The `browser` toolset (`browser_navigate`, `browser_click`, etc.) is powered by the `agent-browser` CLI (https://github.com/vercel-labs/agent-browser), installed globally via npm.

**Symptom:** `[WinError 2] 系统找不到指定的文件。` or `agent-browser: command not found` when using any browser tool.

**Root cause:** `agent-browser` is not installed, or was uninstalled. Hermes's `tools/browser_tool.py` calls `agent-browser` as a subprocess — it's not bundled with Hermes.

**Verify:**

```bash
which agent-browser
npm ls -g agent-browser
```

**Fix:**

```bash
npm install -g agent-browser
```

After install, a `/reset` (new session) may be needed for the tool to register the binary path.

**Architecture note:** `agent-browser` manages Chromium download and lifecycle. The Hermes browser tools are a Python wrapper around its CLI. Cloud backends (Browserbase, Browser Use) bypass `agent-browser` but require paid API keys (see `hermes tools` → browser plugins).

## Browser: Windows `--session` hang + CDP workaround

**Symptom:** All Hermes browser tools (`browser_navigate`, `browser_snapshot`, etc.) hang indefinitely on Windows. The agent session freezes until timeout.

**Root cause:** Hermes's `browser_tool.py` calls `agent-browser` with `--session <name>` for local mode. `agent-browser --session` spawns a daemon process that uses Unix-domain-socket IPC — this hangs on Windows (observed in every version through 0.30.1). `agent-browser` standalone (without `--session`) and `agent-browser --cdp <port>` both work fine.

**Verify the hang:**

```bash
# This hangs:
agent-browser open https://baidu.com --session test --json
```

```bash
# These work instantly:
agent-browser open https://baidu.com --json
agent-browser open https://baidu.com --cdp 9222 --json
```

**Workaround — use agent-browser directly via CDP:** Start Chrome with remote debugging, then use `agent-browser --cdp 9222` for all operations:

```bash
# 1. Start Chrome with remote debug port
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile" &

# 2. Verify CDP is up
curl -s http://localhost:9222/json/version | grep webSocketDebuggerUrl

# 3. Use agent-browser with --cdp (NO --session!)
agent-browser open "https://haifanwu.com" --cdp 9222 --json
agent-browser read --cdp 9222 --json
agent-browser eval "<js>" --cdp 9222 --json
agent-browser snapshot --cdp 9222 --json
```

**Impact on Hermes:** The built-in `browser` toolset is effectively broken on Windows. It always uses `--session` mode and cannot be configured to use CDP. Until agent-browser fixes the Windows session bug or Hermes adds a CDP backend option, the browser tools should remain disabled:

```bash
hermes tools disable browser
```

**Add `--headed` for visible browser (WeChat QR login, etc.):**

```bash
agent-browser open "https://haifanwu.com" --cdp 9222 --headed
# Or set AGENT_BROWSER_HEADED=true in ~/.hermes/.env
```


## Security: dependency vulnerability patching

When a security audit (e.g. `pip-audit`) reveals vulnerable packages in Hermes's own venv, bump the pinned versions in `pyproject.toml`, regenerate the lockfile, and sync — BUT with the right extras.

### Workflow

```bash
cd ~/AppData/Local/hermes/hermes-agent

# 1. Edit pyproject.toml — bump direct dependency pins
#    Exact pins: "pkg==old" → "pkg==new"
#    Range pins: "pkg>=old,<1" → "pkg>=new,<1"
#    Transitive deps with HIGH vulns: add as explicit pins (same pattern)

# 2. Regenerate lockfile
uv lock

# 3. Sync to the actual venv (NOT a new .venv!)
UV_PROJECT_ENVIRONMENT=venv uv sync \
  --extra all \
  --extra feishu \
  --extra bedrock \
  --extra wecom \
  --extra messaging

# 4. Verify
PIPAPI_PYTHON_LOCATION=venv/Scripts/python.exe pip-audit
```

### PITFALL: `uv sync` without `--extra` flags strips optional deps

**This is the #1 pitfall.** `uv sync` with no `--extra` flag syncs ONLY the core `dependencies` list. Every package from optional extras (mcp, google-api-python-client, lark-oapi, boto3, aiohttp, qrcode, discord.py, etc.) gets **uninstalled silently**. Your Hermes instance breaks — gateway can't connect to Feishu, MCP tools won't work, cron jobs that use optional backends fail.

**Always pass `--extra` for every extras group you need.** Check `references/extras-mapping.md` for which extras your instance uses and the typical sync command.

If you accidentally stripped extras (venv went from 110 → 60 packages), re-sync with the full extras list. Don't panic — the packages are just uninstalled from the venv, not lost. `uv sync --extra ...` re-installs them from the lockfile.

### PITFALL: `--all-extras` can fail on Windows

`--all-extras` pulls in `matrix` which depends on `python-olm` (Linux-only wheels, no Windows build path). On Windows, use explicit `--extra` lists instead. The `[all]` extras group in pyproject.toml is a safe subset that excludes linux-only deps.

### PITFALL: uv creates `.venv` by default

If you run `uv sync` without `UV_PROJECT_ENVIRONMENT=venv` (or if `venv/` doesn't exist yet), uv creates `.venv/` and installs there. Hermes uses `venv/`, not `.venv/`. Always set `UV_PROJECT_ENVIRONMENT=venv` when syncing.

### Which packages to pin

| Priority | Action | Example |
|----------|--------|---------|
| Direct dep, exact pin | Bump pin in pyproject.toml | `"Pillow==12.2.0"` → `"Pillow==12.3.0"` |
| Direct dep, range pin | Tighten floor | `"python-multipart>=0.0.9,<1"` → `"python-multipart>=0.0.31,<1"` |
| Transitive dep, HIGH vuln | Add explicit pin in core deps | Add `"pyasn1==0.6.4"` with comment |
| Transitive dep, UNKNOWN/LOW | Skip — not worth the pin overhead | click, httplib2, pygments |

### Transitive dep tracking

After `uv lock`, check whether transitive deps resolved to patched versions:
```bash
grep -A2 'name = "<pkg>"' uv.lock | head -4
```
If not updated, the parent dep(s) have upper bounds preventing the bump. For HIGH-severity vulns, add an explicit pin in pyproject.toml (core `dependencies` list).

## Release monitoring: automated version tracking

When you need to stay informed about Hermes updates without manually checking.

### Shallow clone caveat

The hermes-agent repo at `~/AppData/Local/hermes/hermes-agent` is a **shallow clone** (depth=1). `git log HEAD..origin/main` only shows the top-level merge commit, not individual feature commits. Verify with `git rev-list --count HEAD` (returns 1). Use the **GitHub Compare API** to get the full commit list: `https://api.github.com/repos/NousResearch/hermes-agent/compare/<old_sha>...<new_sha>` → parse `commits[].commit.message`. See `cron-monitor` skill's `references/shallow-clone-github-compare.md` for details.

### Approach: LLM-driven (required) vs no_agent script (deprecated)

**LLM-driven (required):** `no_agent=False` cron job → LLM fetches releases via terminal/curl → understands, translates, and interprets content → formats Chinese report with analysis + 🔴🟡⚪ recommendation levels → delivered via normal cron delivery to Feishu DM. Advantage: handles translation, summarization, and user-specific recommendations natively. Cost: ~500-2000 output tokens per run (negligible with 98%+ caching).

**no_agent script (deprecated):** Python script fetches GitHub Releases API → regex parsing → delivery via direct platform API call. DO NOT USE for new setups. The Windows cron `subprocess.run` cannot capture stdout from Python scripts on this platform, making stdout-based delivery impossible.

### LLM-driven prompt template

```
你是 Hermes 版本简报助手。每次运行：

1. 拉取最新 releases（curl GitHub API）
2. 对比 ~/.hermes/hermes_monitor_last_tag.txt，只处理新版本
3. 输出中文简报，每条用自己的理解解释"对你意味着什么"，不是直译
4. 加推荐评级：🔴必更 🟡建议 ⚪可选
5. 跳过无关平台（Discord/Slack/Docker/Nix/macOS-only 等）和纯重构内务

用户画像：Windows 桌面，deepseek 模型，飞书网关，Hermes 桌面 GUI + TUI

输出格式用 markdown 排版但不要整篇塞进一个 ``` 代码块：
- 标题用 ##，列表用 -，重点用 **粗体**
- 分类用 emoji 标记（🔴🟡⚪）
- 末尾加 💡 升级建议

务必把所有条目翻译为中文。飞书投递，简洁有力，每条 ≤1 行。
```

### Cron job creation (LLM-driven)

```bash
cronjob action='create' \
  name='Hermes 版本简报' \
  schedule='0 9 * * 1' \
  deliver='feishu:oc_CHAT_ID' \
  no_agent=false
```

### Config: disable cron header wrapper

By default, cron deliveries wrap output with English header/footer ("Cronjob Response: ..."). Disable:

```bash
hermes config set cron.wrap_response false
```

### Filtering philosophy

Hermes releases are dense (~1000+ commits, multi-thousand-line release notes). Full delivery is noise. **Default to minimal:**

| Priority | What | When |
|----------|------|------|
| 🚨 Breaking | Regex `BREAKING\|⚠️` in list items | Always include |
| 🔒 Security | Security section items | Always include |
| 🪟 Windows | Windows section (user on Windows) | Always include |
| 📌 Relevant | Desktop, CLI/TUI, tools/MCP, Feishu | ≤2 items each |
| ⏭️ Skip | Discord/Slack/Telegram/iMessage, Docker/Nix, pure refactoring (`extracted\|reorganized\|refactor`) | Never include |

Key rules:
- ≤2 items per category, ≤120 chars per item
- Include release tagline (first bold text in body)
- Skip draft releases
- Track last seen tag in `~/.hermes/last_hermes_release.txt`

### lark-cli upgrade briefings & post-upgrade verification

**Filtering**: the user's lark-cli usage is Feishu docs/base/drive/calendar/im workflows. When reporting lark-cli changelogs (or any tool upgrade), filter to those domains, mark the top 2-4 high-value items, and explicitly say what's skipped (slides/approval/OKR/Miaoda-apps are irrelevant to this user unless asked). The user asks "有哪些特别有用的" — lead with the few that matter, not the full changelog.

**Post-upgrade verification checklist** (after `lark-cli update`):
- `lark-cli --version` — confirm target version
- `lark-cli whoami --as bot` and `lark-cli whoami --as user` — both should reach `tokenStatus: ready` (user shows `needs_refresh` until the first API call auto-refreshes it)
- Send a test message per identity: `lark-cli --as bot im +messages-send --user-id <ou_xxx> --text "..."` → expect `ok: true`
- Probe scopes on key commands: `drive +search` needs `search:docs:read`; `calendar +agenda` needs `calendar:calendar.event:read`. Missing scope → `lark-cli auth login --scope "<scope>"` split-flow (user authorizes in browser)
- **Syntax quirk (1.0.82+)**: `auth status` no longer accepts `--as` — identity checks use `whoami --as user|bot`; `auth status` only shows the current/default identity. Also verify subcommand names with `--help` — they change between versions (`+list` → different names, etc.)
- **Scope flag (1.0.82+)**: `lark-cli auth login --scope` takes MULTIPLE scopes space-separated in ONE flag (`--scope "search:docs:read calendar:calendar.event:read"`). Repeating `--scope` flags errors with `unknown flag`. Use `--no-wait --json` → give user the verification URL/QR → after they confirm, run `lark-cli auth login --device-code <code>` yourself.

### Breaking change detection

Only items that are both (a) in a list and (b) contain `BREAKING` or `⚠️`. Filter out false positives: items with "optimization"/"only"/"default" but no "removed"/"no longer"/"must"/"break" are NOT breaking.

### Cron job template (LLM-driven)

```bash
cronjob action='create' \
  name='Hermes 版本简报' \
  schedule='0 9 * * 1' \
  deliver='feishu:oc_CHAT_ID' \
  no_agent=false
```

Set the prompt via `cronjob action='update' job_id=... prompt='...'` with the template above.

### Delivery targets

- **Feishu DM:** Use `feishu:oc_CHAT_ID` format. Find DM `oc_` chat_id by sending a test via `lark-cli --as bot im +messages-send --user-id ou_xxx --text "test"` — response includes `chat_id`.
- **Home channel:** `deliver='feishu'` (no chat_id) uses the home channel set via `/sethome`.

### Feishu formatting: markdown structure, not code block

When delivering markdown to Feishu via cron:
- ✅ Use `##` headings, `-` bullets, `**bold**`, emoji — Feishu renders these
- ❌ Do NOT wrap the entire message in ``` (triple backticks) — it becomes one monospace block
- ❌ Do NOT use box-drawing chars like `───` — Feishu may render as code
- Keep structure flat: headings → bold section labels → bullet items

### Reply channel discipline

Hermes TUI questions → answer in TUI. Feishu questions → answer in Feishu. Cron auto-push → Feishu. Never cross channels.

### Cron delivery error [230002] "Bot/User can NOT be out of the chat"

**Symptom:** cron jobs show `last_status: ok` but `last_delivery_error: "Feishu send failed: [230002] Bot/User can NOT be out of the chat"`.

**Diagnosis order (don't assume config is broken):**
1. **Gateway reconnect window is the most common cause** — the gateway disconnected/reconnected (check `gateway.log` for "[Feishu] Disconnected" / "Connected" timestamps) and a cron batch fired during the offline window. Jobs fired after reconnect deliver fine — compare timestamps.
2. **Verify the bot can actually reach the chat** with a direct send: `lark-cli --as bot im +messages-send --user-id <ou_xxx> --text "test"` → `ok: true` + returns the `oc_` chat_id. If direct send works, the bot is in the chat and the error was transient.
3. Only if direct send ALSO fails → bot is genuinely not in that chat (app switched / chat membership lost) — re-add the bot or update `deliver` targets.

**User preference:** 检查+提醒型任务必须同时做"自动修"——单次投递失败不代表要重配 cron，先验证连通性再动手。

### Windows cron no_agent Python stdout capture failure

**Symptom:** A Python script runs correctly (debug logs confirm it detected new data, called `print()`, and updated state), but the scheduler logs `"empty stdout — silent run"` and skips delivery. `execution_success: true` but no message arrives.

**Root cause:** On Windows, the `_run_job_script` function in `cron/scheduler.py` uses `subprocess.run(capture_output=True, text=True)` with a sanitized environment. The encoding path on Windows can silently drop stdout from Python scripts — even a trivial `print("HELLO")` produces empty output. This is NOT caused by `redact_sensitive_text` (verified by adding debug-file logging before/after the print calls — the script's `print()` executes, but the parent process receives empty stdout).

**Diagnosis technique:** Add file-based debug logging inside the script (e.g., write to `~/.hermes/hermes_monitor_debug.log`) to confirm the script actually executes and detects new data. If debug logs show everything works but the scheduler says empty stdout → this bug.

**Workaround:** Don't rely on cron stdout delivery. Instead, have the script send messages directly via `lark-cli` (Feishu) or another platform-specific CLI. Set the cron job's `deliver=local` and handle delivery from within the script:

```python
import subprocess
# After generating the report, send directly
result = subprocess.run([
    'lark-cli', '--as', 'bot', 'im', '+messages-send',
    '--user-id', 'ou_xxx',  # or --chat-id oc_xxx for group
    '--text', report_text,
], capture_output=True, text=True)
```

For Feishu DM, find the user's `ou_` ID from `state.db` → `sessions` table → `user_id` column where `source='feishu'`. Then verify the DM `oc_` chat_id by sending a test message via `lark-cli` — the response includes the `chat_id` field.

**Tested delivery method:** `lark-cli --as bot im +messages-send --user-id ou_xxx --text "..."` works reliably from cron scripts and returns the `oc_` chat_id for future use.

- **Desktop restart ≠ gateway restart.** The gateway is a separate process. If you `hermes update` or the desktop auto-updates, you MUST restart the gateway separately.
- **`.pyc` cache is not the issue.** Deleting `__pycache__` won't help — the stale bytecode is in the running process's memory, not on disk. Only a process restart fixes it.
- **`sourceMode: false` in `desktop-build-stamp.json`** is normal for the desktop app build. It means the desktop was built from a specific commit, not that it's running stale code. The agent process reads from the source tree at runtime.
- **agent-browser `--session` hangs on Windows.** Do not use `--session` mode on Windows. Use `--cdp <port>` instead (see Browser section above).
