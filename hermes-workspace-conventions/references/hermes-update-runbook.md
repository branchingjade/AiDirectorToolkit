# Hermes 更新完整流程（hermes update runbook，2026-08-20 实测）

> 本文覆盖 **CLI 方式完整更新**（`hermes update`）的全流程与全部已知坑。
> ops-panel 桌面版一键更新的停机陷阱见同目录 `ops-panel-update-runner.md`（2026-08-09）。

## 一、更新前准备（缺一不可）

### 1. 补丁正本一致性验证（最重要，2026-08-20 踩坑）

**背景**：本地补丁正本 = `Documents/KnowledgeBase/Obsidian Vault/_hermes/补丁管理/hermes-local-patches.diff`（Obsidian 仓库，正本唯一）。**如果正本与实际工作区不一致，update 后重打补丁会把已废弃的改动加回去**（2026-08-20 实测：正本含 8-18 的 DSH 桥补丁，实际 8-19 已解耦，若直接 update 会复活废弃代码）。

```bash
cd ~/AppData/Local/hermes/hermes-agent
git diff > /tmp/live.diff                    # 当前实际补丁
git apply --check --reverse hermes-local-patches.diff   # 通过 = 正本与实际一致
```

**不一致时**：先备份旧正本（`.bak-<日期>`），用 `git diff` 重新生成正本，再验证。

### 2. 检查更新会触及的本地补丁文件

```bash
git fetch origin
git diff --name-only HEAD origin/main > /tmp/upstream.txt   # 上游 370 commits 触及的文件
git diff --name-only > /tmp/local.txt                        # 本地补丁文件
# 交集 = update 时 autostash 可能冲突的文件（2026-08-20 实测 11/24 重叠）
```

### 3. 关闭占用进程（Windows 必须）

**坑（2026-08-20 实测）**：桌面 app、gateway、dashboard、serve、hindsight daemon 都在运行时，`hermes update` 依赖同步会报 `os error 32`（文件被占用）。

```powershell
# 停计划任务（注意：Stop-ScheduledTask 只停任务状态，不一定杀进程！）
Stop-ScheduledTask -TaskName 'Hermes_Gateway','Hermes_Gateway_Watchdog','Hermes_Hindsight_Daemon','HermesRemoteServe','HermesDashboard','Hermes-HideHindsightWindow','DSH_Watchdog','DSH_Mux_Listener_Polling'
# 杀残留进程（watchdog 会自动拉起 gateway，必须连 watchdog 一起停）
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*hermes-agent*' -and $_.Name -like 'python*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
# 优雅关闭桌面 app（主进程是 Electron 主窗口那个，杀子进程没用）
Stop-Process -Id <Hermes主进程PID> -ErrorAction SilentlyContinue
```

**验证无进程占用**：
```powershell
Get-Process -Name Hermes,hermes -ErrorAction SilentlyContinue   # 应为空
Get-NetTCPConnection -LocalPort 8644,9119,9120,9177 -State Listen -ErrorAction SilentlyContinue  # 应为空
```

**坑（2026-08-20 实测）**：并行会话可能在跑 `hermes skills install` 等命令，也会持有 hermes.exe 锁——更新前 `Get-Process hermes` 检查，有就等它结束或先沟通。

## 二、执行更新

```bash
hermes update --yes
```

- `--yes`：跳过交互提示（config migration / stash restore 确认）
- 正常输出 `✓ Update complete! [main @ <commit>]`
- **Windows 提示 `hermes.exe cannot replace itself` 是正常现象**（把手交给 venv python 继续），不是失败

## 三、更新后验证（必做，2026-08-20 实测 autostash 只恢复 15/24）

**坑（最严重）**：`hermes update` 的 autostash 恢复**不保证完整**——2026-08-20 实测 370 commits 大更新后 24 个补丁文件只恢复 15 个，9 个被上游覆盖丢失（gateway/run.py、hermes_state.py、hermes_cli/ 下 7 个）。**必须逐文件验证，不能信 update 输出的 "Local changes were restored"。**

```bash
cd ~/AppData/Local/hermes/hermes-agent
git apply --check --reverse hermes-local-patches.diff   # 通过 = 全部在位
git status --short | grep '^ M' | wc -l                  # 应等于正本文件数
```

**丢失时恢复**（正本白名单只打缺失文件）：
```bash
git apply --include=gateway/run.py --include=hermes_state.py <...其余丢失文件...> hermes-local-patches.diff
git apply --check --reverse hermes-local-patches.diff    # 恢复后必须通过
python venv/Scripts/python.exe -m py_compile <重打文件>   # 语法验证
```

## 四、恢复服务

```powershell
Start-ScheduledTask -TaskName 'Hermes_Gateway'           # gateway 冷启动约 12-15 秒
Start-Sleep 15
Get-NetTCPConnection -LocalPort 8644,8642 -State Listen   # 验证监听
Start-ScheduledTask -TaskName 'Hermes_Gateway_Watchdog','Hermes_Hindsight_Daemon','HermesRemoteServe','HermesDashboard','Hermes-HideHindsightWindow','DSH_Watchdog','DSH_Mux_Listener_Polling'
```

hindsight daemon 由 watchdog 5 分钟轮询拉起，无需手动等。

## 五、清理 update 残留（⚠ 危险区，2026-08-20 误删桌面 app 教训）

update 会在 hermes-agent 根目录生成：
- `*.hermes-update-old`（旧文件/目录备份，含**编译产物**）
- `*.hermes-update-staging`（新文件暂存）

**⚠ 致命坑**：`apps.hermes-update-old/` 目录里是**桌面 app 的编译产物**（`release/win-unpacked/Hermes.exe`）——它**不被 git 跟踪、不进回收站、无法从任何备份恢复**。2026-08-20 实测把 `apps.hermes-update-old/` 当普通备份删掉 → 桌面 app 整个消失（"找不到 hermes"），只能 `hermes desktop --build-only` 重建（5-10 分钟，npm install 1292 包 + electron-builder 打包）。

**清理安全规则**：
1. **`apps*`、`release*`、`win-unpacked` 相关备份一律不删**——是编译产物，删了要重建
2. 只删确认是源码/临时文件的 `.hermes-update-old`（单个 `.py`/`.md`/`.json` 文件备份）
3. 删除前 `Get-ChildItem <备份> -Recurse | Measure-Object` 看内容性质
4. 删完必须验证桌面 app 仍在：`Test-Path apps/desktop/release/win-unpacked/Hermes.exe`
5. 如果误删了：`hermes desktop --build-only` 重建（唯一恢复途径），重建后快捷方式可能指向旧版，需修正：
   ```powershell
   $ws = New-Object -ComObject WScript.Shell
   $lnk = $ws.CreateShortcut('C:\Users\Public\Desktop\Hermes.lnk')
   $lnk.TargetPath = 'C:\Users\HMSJ\AppData\Local\hermes\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe'
   $lnk.Save()
   ```

**另一个遗留**：`git stash list` 里的 `hermes-update-autostash-*` 是历次更新快照——先核对内容（`git stash show -p 'stash@{N}'`）确认没有正本外的补丁再清。

## 六、更新后补丁归档标注

- 被上游吸收的补丁（`git show HEAD:<文件> | grep -c <关键内容>` 命中）→ 从正本移除，记录到 `补丁管理/补丁归档标注.md`
- 上游未吸收的本地补丁 → 保留正本，README 同步文件数
- 提交 Obsidian 仓库（补丁管理目录）并 push 到 knowledge-base 正本

## 判定速查

| 现象 | 原因 | 处理 |
|------|------|------|
| update 报 `os error 32` / `failed to remove ... hermes.exe` | 进程占用 | 停全部服务+桌面 app 后重试 |
| update 后行为异常 | autostash 只恢复部分补丁 | `git apply --check --reverse` 验证，丢失的用正本重打 |
| 桌面 app 消失（找不到 hermes） | 误删 `apps.hermes-update-old` | `hermes desktop --build-only` 重建 |
| 补丁重打后 DSH 桥/废弃代码出现 | 正本含已解耦补丁 | 更新前先同步正本 |
