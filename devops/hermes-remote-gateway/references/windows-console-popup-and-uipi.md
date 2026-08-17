# Windows 计划任务弹黑窗口排障记录（Hermes serve / Hindsight 案例）

2026-08-07 本机实测。现象：Hermes 远程网关（`hermes serve --port 9119`）登录自启后，
桌面常驻一个黑 cmd 窗口；修掉一个又冒出一个。完整根因链与验证方法如下。

## 现象

窗口标题两种形态（都是「选择」开头，来源不同）：
1. `选择 C:\WINDOWS\system32\cmd.EXE` —— 任务动作里的 cmd 壳
2. `选择 C:\...\hermes-agent\venv\Scripts\pythonw.exe` —— serve 进程内部自建控制台

窗口内容 = serve 的 stdout（`HERMES_BACKEND_READY port=9119` / `Hermes backend listening on 0.0.0.0:9119`）。

## 根因链（三层，逐层修）

### 层 1：cmd /c 壳窗口
计划任务动作写成 `cmd /c cd /d ... && venv\Scripts\pythonw.exe -m hermes_cli.main serve ...`。
cmd 是控制台程序，登录（onlogon）触发时窗口显示；serve 是长驻进程，cmd 等它退出 → 窗口常驻。

**修**：任务动作直接执行 pythonw.exe 全路径 + `-m hermes_cli.main serve ...` 参数 +
`WorkingDirectory` 起始于 hermes-agent 目录（schtasks /create 没有 WorkingDirectory 参数，必须用
`New-ScheduledTaskAction -WorkingDirectory` + `Register-ScheduledTask`，或用 `Set-ScheduledTask -Action` 改已有任务）。

### 层 2：pythonw 内部 AllocConsole 自建窗口
pythonw.exe 是 GUI 子系统程序，本不该有控制台。但 hermes launcher 内部某 C 扩展/launcher
调用了 `AllocConsole`，凭空创建 conhost 黑窗口。**启动 flags 挡不住进程内部自建窗口**——
start 参数（SW_HIDE 等）只影响进程启动时的窗口，管不了运行中自建的。

窗口特征：类名 `ConsoleWindowClass`，标题 `选择 <pythonw.exe 完整路径>`，owner pid = pythonw 进程。

**修**：只能靠守卫脚本轮询隐藏（见下）。

### 层 3：UIPI 权限隔离（守卫失效的隐蔽根因）
守卫脚本（枚举窗口 + 标题匹配 + `ShowWindow(SW_HIDE)`）逻辑正确、能被高权限进程正常执行，
但以普通权限（RunLevel=Limited）跑时**对 serve 窗口无效**：
- serve 以 RunLevel=Highest（管理员，高完整性）运行 → 其窗口属高完整性进程
- 守卫以 Limited（中完整性）运行 → `GetWindowText`/`ShowWindow` 被 UIPI（用户界面特权隔离）拦截
- 现象：守卫枚举到了窗口但**读不到标题**（返回空/受限），MARKER 匹配不上 → 不隐藏
- 反证：守卫自己的窗口（同完整性）能正常隐藏——所以守卫「部分生效」，极具迷惑性

**修**：守卫任务 RunLevel 也改为 Highest（`New-ScheduledTaskPrincipal -RunLevel Highest`）。

## 排查工具链（按序用）

```powershell
# 1. 哪些进程有可见窗口 + 标题（定位弹窗进程）
Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Select Id,ProcessName,MainWindowTitle

# 2. 进程详情：命令行 / 父进程 / SessionId（判断来源、会话、父子链）
Get-CimInstance Win32_Process | Where-Object {$_.ProcessId -in <pid列表>} | Select ProcessId,ParentProcessId,SessionId,CommandLine | fl

# 3. 计划任务定义（动作/触发器/权限）
(Get-ScheduledTask -TaskName X).Actions
(Get-ScheduledTask -TaskName X).Principal   # LogonType / RunLevel / UserId
(Get-ScheduledTask -TaskName X).Triggers

# 4. 当前进程是否管理员（判断自己能否操作高完整性窗口）
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```

窗口枚举（ctypes，诊断脚本模式）：
- 枚举可见顶层窗口：`EnumWindows` + `IsWindowVisible` + `GetWindowTextLengthW/W` + `GetWindowThreadProcessId`
- 看窗口类名区分宿主：`ConsoleWindowClass`=传统 conhost（AllocConsole 产物）、`CASCADIA_HOSTING_WINDOW_CLASS`=Windows Terminal 宿主
- **两阶段模式**：先 EnumWindows 收集全部候选，再循环 ShowWindow——不要在 callback 里直接做操作
  （单阶段在 callback 内 ShowWindow 是守卫脚本的写法，曾干扰判断；两阶段诊断更干净）

## 守卫「是否真在干活」的决定性测试

轮询型守卫（每 N 秒隐藏一次）「进程在跑」≠「在干活」。验证：
1. 用脚本找到目标窗口，`ShowWindow(hwnd, SW_SHOW)` 故意显示它
2. 等 > 守卫轮询周期 × 2
3. 查 `IsWindowVisible(hwnd)`：被重新隐藏 = 守卫正常；仍可见 = 守卫有权限/枚举/匹配问题

实测案例：守卫自己（Limited）只重新隐藏了它自己的 WT 窗口，serve 的 conhost 窗口 5 秒后仍可见；
改 Highest 后两个窗口都被重新隐藏。一次测试直接定位 UIPI 根因。

## 守卫脚本治理（本机现状）

- 脚本：`C:\Users\HMSJ\Documents\Hermes\scripts\hide_hindsight_window.py`
  - 每 2 秒轮询，隐藏标题含 `hermes-agent\venv\Scripts\pythonw.exe` 的可见窗口（ShowWindow SW_HIDE）
  - 匹配子串不区分窗口来源 → Hindsight daemon 与 serve 共用（同 pythonw 路径）
- 任务：`Hermes-HideHindsightWindow`，触发器 LogonTrigger（登录时），RunLevel=Highest（2026-08-07 修正）
- pythonw 运行脚本本身无窗口；脚本内 print 在 pythonw 下 sys.stdout=None 会抛异常——隐藏动作在 print 前执行不受影响，但 startup 无 try 包裹处的 print 若抛异常会崩，注意保持隐藏动作先于任何可能失败的 IO

## 相关命令速查

```powershell
# 改已有任务的动作（换 pythonw + WorkingDirectory）
$action = New-ScheduledTaskAction -Execute "C:\...\pythonw.exe" -Argument "-m hermes_cli.main serve --host 0.0.0.0 --port 9119" -WorkingDirectory "C:\...\hermes-agent"
Set-ScheduledTask -TaskName "HermesRemoteServe" -Action $action

# 改任务的 RunLevel（守卫权限）
$p = New-ScheduledTaskPrincipal -UserId "HMSJ" -LogonType Interactive -RunLevel Highest
Set-ScheduledTask -TaskName "Hermes-HideHindsightWindow" -Principal $p

# 无缝重启服务并换启动方式
Stop-Process -Id <旧cmd壳>,<旧pythonw>,<旧子进程> -Force
Start-ScheduledTask -TaskName "HermesRemoteServe"
# 验证：netstat -ano | grep ":9119.*LISTENING"；Get-Process cmd 无新可见窗口
```

git-bash 注意：taskkill/schtasks 的 `/参数` 会被 MSYS 转义（`//PID` 也不认），一律用
PowerShell `Stop-Process` / `Start-ScheduledTask` 代替。
