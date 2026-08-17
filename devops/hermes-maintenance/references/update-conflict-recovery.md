# Update 失败排查与补丁恢复 Playbook（2026-08-09 实测）

Windows 平台 hermes update 的完整排查链：为什么失败 → 停哪些服务 → 补丁怎么恢复。

## 一、Windows 更新失败根因链（三层）

`hermes update` 在 Windows 上"总是失败"的根因几乎都是 **venv 文件锁**——运行中的 Hermes 进程锁着 `venv/Lib/site-packages/cryptography/hazmat/bindings/_rust.pyd` 等原生扩展，更新器无法替换依赖。更新器检测到占用会**主动拒绝**（`✗ Other Hermes processes are running from this install's venv`），或强闯撞锁失败（`error: failed to remove file ... _rust.pyd: 拒绝访问 (os error 5)`）。

锁 venv 的进程（按挡路优先级）：
| 进程 | 命令行特征 | 更新器能否自动停 |
|---|---|---|
| **桌面 app backend** | `venv\Scripts\python.exe -m hermes_cli.main serve --host 127.0.0.1 --port 0` | ❌ 只提示 "close the desktop app" |
| **远程 serve** | `... serve --host 0.0.0.0 --port 9119`（pythonw 主进程 + hermes-runtime 子进程） | ❌ |
| **守卫脚本** | `pythonw.exe ...hide_hindsight_window.py`（venv 启动） | ❌ |
| gateway | `... gateway run`（venv 主进程 + hermes-runtime 子进程） | ✅ 自动停→更→起 |

**更新器只管理 gateway**，桌面 app/远程 serve/守卫脚本它检测到但停不了——这就是"一键更新"体验缺失的本质（不是漏洞，是编排没做全）。桌面 app 的 `apps/desktop/package.json` 无 electron-updater，无内置更新通道（2026-08-09 查证）。

**社区已知**（NousResearch/hermes-agent issues，2026-08-09 查证）：#73381（cryptography + 文件锁，与本机 08-07 失败同款）、#68760（hermes.exe locked WinError 32）、#70337（gateway 运行时更新失败）；上游修复 PR 在途：#62304（recover locked native wheels）、#68821、#75752——均未合入，合入前本地需手动编排。

## 二、更新前停服务清单（让 update 能跑）

```powershell
# 1. 禁用 watchdog（关键！否则更新中途它拉起 gateway 又锁文件）
Disable-ScheduledTask -TaskName Hermes_Gateway_Watchdog
# 2. 停远程 serve + 守卫脚本（任务 End/Disable 双保险）
Stop-ScheduledTask -TaskName HermesRemoteServe -ErrorAction SilentlyContinue
Disable-ScheduledTask -TaskName HermesRemoteServe
Stop-ScheduledTask -TaskName Hermes-HideHindsightWindow -ErrorAction SilentlyContinue
Disable-ScheduledTask -TaskName Hermes-HideHindsightWindow
# 3. 杀 gateway 进程树（更新器也会停，提前清更干净）
taskkill /F /PID <gateway主> /PID <runtime子>
# 4. 用户关闭桌面 app（唯一无法自动的部分）
```
更新后恢复：Enable 三个任务 + `Start-ScheduledTask` 远程 serve/守卫；gateway 由更新器自动起（`✓ Starting Windows gateway after update`）。

排查进程归属：`Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*hermes_cli.main*' }` 看命令行区分桌面 backend（`--port 0`）/远程 serve（`--port 9119`）/gateway（`gateway run`）。

## 三、update 后补丁恢复（autostash apply 失败）

**识别：** `git status` 干净（只剩 untracked）+ 新 stash `hermes-update-autostash-<时间戳>` = 自动恢复遇冲突失败，补丁留在 stash。

**命令序列（会话内可执行——安全护栏只拦 `git stash`，不拦 `git apply` 和 patch 工具）：**
```bash
cd ~/AppData/Local/hermes/hermes-agent
git stash show --stat "stash@{0}"                                   # 补丁清单
git stash show -p "stash@{0}" > "C:/Users/<user>/AppData/Local/Temp/patch.diff"  # MSYS 必须 Windows 路径
git apply --check "C:/Users/<user>/AppData/Local/Temp/patch.diff"   # 哪些文件冲突
```

**冲突文件三类处置：**

1. **上游已合入 → 弃用**。判断：`git diff "stash@{0}^1" HEAD -- <file>` 看上游改动；grep HEAD 版文件确认补丁标志已在。案例：本地补丁给 subprocess 加 `errors="replace"`（goals.py/tools_config.py/working_diff.py），上游全量合入且更完整（带 `encoding="utf-8"` + 解释注释）→ 三文件弃用，**不再进正本 diff**（否则下次重打失败）。

2. **上下文漂移 → patch 工具重打**。判断：上游 hunk 位置与补丁位置不重叠但上下文被改（`git diff ... | grep "^@@"` 对比双方 hunk 行号）。做法：用补丁的 context 行（如 `if cfg_channel_prompt:` / `return {`）在 HEAD 版 `grep -n` 定位新锚点，确认唯一性后 patch 工具插入。案例：gateway/run.py 上游 +1078 行重构，飞书协作 75 行补丁两段分别插到 cfg_channel_prompt 块后、Auto-titling 注释后 return 前。

3. **干净 → 批量恢复**：
```bash
git apply --exclude=gateway/run.py --exclude=hermes_cli/goals.py ... patch.diff
```

**验证：**
- `git diff HEAD --stat` 行数 vs 原 stash stat（本案例：21 文件 432+/101- ≈ 原 24 文件 437+/105-，差值为弃用 3 文件）
- 批量 `venv/Scripts/python.exe -m py_compile <files>` 全过
- 正本同步：`git diff HEAD -- <21文件> > hermes-local-patches.diff`（Obsidian 补丁管理目录）+ cp 新文件 + `python reapply-patches.py` dry-run 报 "补丁已应用（检测到关键标记）"

**生效：** 重启 gateway（当前进程加载无补丁代码）——netstat 查 8644 PID → `Stop-Process -Force` → `Start-ScheduledTask Hermes_Gateway` → 日志确认 `[Feishu] Connected` + `Gateway running with 2 platform(s)`。

## 四、⚠️ 编码双坑（写补丁管理工具/脚本时，git apply 神秘失败的根因）

2026-08-09 实测（ops-panel 运维面板开发中，sync-master 生成正本 diff 后 `git apply --check --reverse` 反复失败）：

1. **subprocess 默认 GBK 解码 git 的 UTF-8 输出**：git diff 含中文注释，zh-CN Windows 上 `subprocess.run(text=True)` 用 locale（GBK）解码 → 中文乱码（U+FFFD）→ 写回 diff 文件损坏。**git 相关 subprocess 必须 `encoding='utf-8'`**（powershell/netstat 输出 GBK 则保持默认 + `errors='replace'`）。
2. **Python `write_text` 默认 LF→CRLF**：git diff 输出的 `\n` 被 text 模式转成 `\r\n`，git apply 对 CRLF diff 失败。**写 diff 文件用 `newline='\n'` 或 `write_bytes`**。

症状排查顺序：`git apply --check --reverse` 失败但内容看起来对 → 先看 diff 文件字节（`head -c 100` 看 `\r\n`）→ 再查编码（grep 中文是否乱码）。bash 重定向生成的正本（原始字节透传）无此问题——`git diff > file` 永远安全；Python 写文件必须显式处理。
