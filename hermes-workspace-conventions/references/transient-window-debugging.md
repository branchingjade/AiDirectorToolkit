# 一闪而过窗口排查方法论（2026-08-09 实测）

用户报「总有一闪而过的窗口」时的完整排查链。本机所有弹窗源及其特征。

## 已知弹窗源清单（按嫌疑排序）

| 源 | 特征 | 状态 |
|----|------|------|
| 计划任务 Execute=python.exe 跑 .py | 每 N 分钟闪一次（看 Triggers.Repetition.Interval） | Hermes_Gateway_Watchdog 已修（→pythonw） |
| pythonw 内部 AllocConsole 自建窗口 | conhost 黑窗，标题含 pythonw 路径，类名 ConsoleWindowClass | 守卫 Hermes-HideHindsightWindow 处理，但见第四坑 |
| **守卫 MARKER 路径漂移** | hindsight daemon 跑在 `.hermes-runtime\python\generation-<hash>\...\pythonw.exe`，守卫 MARKER 是 `venv\Scripts\pythonw.exe` → 匹配不到 → 周期弹窗（daemon `--idle-timeout 300` 反复拉起） | 2026-08-09 排查中，修法待验证 |
| ops-update-runner.py（python.exe） | 运维面板更新执行器，一次性/手动触发，启动即停全部服务 | 见 ops-panel-update-runner.md |
| 系统 hpatchmonTask（Monitoring 任务，cmd.exe） | Windows 自带硬件补丁监控，Boot/Logon/Time 触发，RunLevel=Highest+ServiceAccount | 系统任务，不动 |

## 排查命令（实测有效）

### 1. 计划任务枚举（找 python.exe/cmd.exe 执行者 + 触发频率）
```powershell
# 全部任务 + 执行程序 + 参数
Get-ScheduledTask | Where-Object {$_.State -ne 'Disabled'} | Select-Object TaskName, @{n='Exec';e={$_.Actions[0].Execute}}, @{n='Args';e={$_.Actions[0].Arguments}} | Format-Table -AutoSize -Wrap
# 单任务详情（触发器间隔 / 运行级别 / 登录类型）
$t = Get-ScheduledTask -TaskName '<名>'; $t.Actions | Format-List Execute, Arguments, WorkingDirectory; $t.Triggers | Format-List CimClass, StartBoundary, Repetition; $t.Principal | Format-List RunLevel, LogonType
# 上次运行结果
Get-ScheduledTaskInfo -TaskName '<名>' | Select LastRunTime, LastTaskResult, NextRunTime
```
- `Repetition.Interval = PT5M` = 每 5 分钟触发（高频=高频弹窗）
- `LogonType = S4U` 的 GUI 进程窗口不显示在用户桌面（gateway 就是 S4U，不弹窗）

### 2. 进程树（谁拉起了谁 + 启动时间）
```powershell
Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|cmd' } | ForEach-Object {
    $parent = Get-CimInstance Win32_Process -Filter "ProcessId=$($_.ParentProcessId)" -ErrorAction SilentlyContinue
    Write-Output ('PID=' + $_.ProcessId + ' | PPID=' + $_.ParentProcessId + ' (' + $parent.Name + ') | ' + $_.Name + ' | Started=' + $_.CreationDate)
    Write-Output ('    CMD: ' + $_.CommandLine)
}
```
父进程 + 启动时间对得上用户报告弹窗的时刻 = 实锤。成对出现的 python+pythonw 常是启动器链（serve → hindsight daemon）。

### 3. 事件日志（通常断路，别指望）
- `Microsoft-Windows-TaskScheduler/Operational` **默认未启用**（`Get-WinEvent -ListLog *TaskScheduler*` 看 IsEnabled=False）
- System 日志 `ProviderName='Microsoft-Windows-TaskScheduler'` 通常 0 条
- 历史路径常断 → 直接上抓现行（第 4 步）

### 4. 抓现行：窗口监控脚本
高频轮询 EnumWindows，记录新出现的 ConsoleWindowClass/python/cmd 窗口标题 + 精确时间，后台跑 10-15 分钟等下次弹窗：

```python
"""抓现行：高频轮询可见窗口，记录新出现的 python/cmd/conhost 窗口。"""
import ctypes, time, datetime
from ctypes import wintypes
LOG = r"C:\Users\HMSJ\AppData\Local\Temp\window_flash_log.txt"
user32 = ctypes.windll.user32
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
GetWindowThreadProcessId = user32.GetWindowThreadProcessId
IsWindowVisible = user32.IsWindowVisible
GetWindowTextW = user32.GetWindowTextW
GetClassNameW = user32.GetClassNameW
seen = set()
def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'[{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]}] {msg}\n')
def enum_cb(hwnd, lparam):
    if IsWindowVisible(hwnd):
        title = ctypes.create_unicode_buffer(512); GetWindowTextW(hwnd, title, 512)
        cls = ctypes.create_unicode_buffer(128); GetClassNameW(hwnd, cls, 128)
        pid = wintypes.DWORD(); GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if cls.value == 'ConsoleWindowClass' or 'python' in title.value.lower() or 'cmd' in title.value.lower():
            key = (pid.value, cls.value, title.value)
            if key not in seen:
                seen.add(key); log(f'NEW pid={pid.value} class={cls.value} title="{title.value[:100]}"')
    return True
cb = EnumWindowsProc(enum_cb); log('=== 监控启动 ===')
deadline = time.time() + 900
while time.time() < deadline:
    user32.EnumWindows(cb, 0); time.sleep(0.2)
log('=== 监控结束 ===')
```
单次枚举当前可见窗口（无监控）：
```python
# 只列当前所有 ConsoleWindowClass/python/cmd 可见窗口——查是否有残留黑窗
# 用上面的 enum_cb 逻辑跑一次 EnumWindows，打印 pid + 进程路径 + 标题
# 进程路径: OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION=0x1000) + QueryFullProcessImageNameW
```

## bash + PowerShell 转义地狱（本会话三次翻车）

- 内联 `powershell -Command "..."` 多层嵌套引号/反引号必炸：backtick 触发 bash 命令替换（`unexpected EOF`）、嵌套 ForEach 的 `$_` 覆盖外层变量（TaskName 显示为空）、中文输出 GBK 乱码（`gateway δ����`）
- **正确姿势：write_file 写临时 .ps1/.py 脚本 → `powershell -ExecutionPolicy Bypass -File <脚本>` 执行**。零转义、可复用、输出干净
- PowerShell 输出中文乱码时，判据改用 ASCII/英文（如 `'gateway 未起来'` 换成端口存在性判断）
- 进程/窗口判断一律用 PID + 端口 + 启动时间，别依赖中文输出文本

## 修法要点

- 计划任务跑 .py → Execute 改 pythonw.exe（见主 SKILL.md 弹窗章节）
- pythonw AllocConsole → 守卫脚本隐藏（MARKER 匹配标题）
- **守卫 MARKER 必须与进程实际路径一致**——hindsight 从 venv 迁到 .hermes-runtime 后守卫静默失效（2026-08-09 第四坑）；改 MARKER 前先 `Get-CimInstance Win32_Process` 确认 pythonw 真实路径
