"""高频窗口监控探针 — 抓"一闪而过"的弹窗现行（2026-08-09 弹窗排查实证）。

用法（后台运行）：
    <python> window-flash-capture.py [日志路径] [时长秒]
    默认日志 C:\\Users\\<user>\\AppData\\Local\\Temp\\flash_capture.txt，默认跑 1200 秒

记录对象：可见的 ConsoleWindowClass（控制台黑窗）或标题含 python/cmd 的窗口。
每 0.05s 轮询 EnumWindows，记录 NEW（新窗口出现，含 PID/类名/标题）、
TITLE-CHANGE（标题变化）、GONE（窗口销毁，含存活时长）。

弹窗排查链（配合本脚本，2026-08-09 实战顺序）：
1. 计划任务枚举：Get-ScheduledTask 找 Execute 含 python/cmd 的任务 + 触发器 Repetition.Interval（PT5M=每5分钟，高频弹窗嫌疑）
2. 进程树父子关系：Get-CimInstance Win32_Process 查 CommandLine/ParentProcessId（找 re-exec 出的 .hermes-runtime python）
3. 静态窗口枚举：EnumWindows 数 ConsoleWindowClass == 0 才干净
4. 本脚本抓现行：记录每次弹窗的标题+PID+出现时刻，标题直接指向源进程
5. 官方源码取证：grep hermes-agent 源码注释（如 gateway_windows.py 的 DETACHED_PROCESS/CREATE_NO_WINDOW 说明）

已知根因（2026-08-09 定案）：
- venv\\Scripts\\pythonw.exe 是 console stub（exec 控制台 python.exe）→ 用它启动任何进程都弹窗；真无窗口用 .hermes-runtime\\python\\generation-*\\cpython-*\\pythonw.exe
- DETACHED_PROCESS | CREATE_NO_WINDOW 组合：MSDN 规定 DETACHED_PROCESS 在场时 CREATE_NO_WINDOW 被忽略
"""
import ctypes
import datetime
import os
import sys
import time
from ctypes import wintypes

user32 = ctypes.windll.user32

EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
GetWindowThreadProcessId = user32.GetWindowThreadProcessId
IsWindowVisible = user32.IsWindowVisible
GetWindowTextW = user32.GetWindowTextW
GetClassNameW = user32.GetClassNameW
IsWindow = user32.IsWindow

LOG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.environ.get("LOCALAPPDATA", r"C:\Users\Public"), "Temp", "flash_capture.txt")
DURATION = int(sys.argv[2]) if len(sys.argv) > 2 else 1200

seen = {}  # hwnd -> (first_seen, last_title)


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f'[{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]}] {msg}\n')


def enum_cb(hwnd, lparam):
    if IsWindowVisible(hwnd):
        title = ctypes.create_unicode_buffer(512)
        GetWindowTextW(hwnd, title, 512)
        cls = ctypes.create_unicode_buffer(128)
        GetClassNameW(hwnd, cls, 128)
        pid = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        t, c = title.value, cls.value
        if c == "ConsoleWindowClass" or "python" in t.lower() or "cmd" in t.lower():
            now = time.time()
            if hwnd not in seen:
                seen[hwnd] = (now, t)
                log(f'NEW hwnd={hwnd} pid={pid.value} class={c} title="{t[:100]}"')
            elif t != seen[hwnd][1]:
                log(f'TITLE-CHANGE hwnd={hwnd} pid={pid.value} old="{seen[hwnd][1][:80]}" new="{t[:80]}"')
                seen[hwnd] = (seen[hwnd][0], t)
    return True


cb = EnumWindowsProc(enum_cb)
log(f"=== 高频监控启动 (0.05s) 时长 {DURATION}s ===")
deadline = time.time() + DURATION
while time.time() < deadline:
    user32.EnumWindows(cb, 0)
    now = time.time()
    # GONE：窗口销毁才记录（隐藏≠销毁——IsWindow 仍为 True，勿据此误判）
    gone = [h for h, (ts, _) in seen.items() if now - ts > 3 and not IsWindow(h)]
    for h in gone:
        ts, t = seen.pop(h)
        log(f"GONE hwnd={h} lived={now-ts:.1f}s title=\"{t[:80]}\"")
    time.sleep(0.05)
log("=== 监控结束 ===")
