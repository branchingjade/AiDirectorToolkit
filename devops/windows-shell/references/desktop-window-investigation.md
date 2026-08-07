# Desktop Window Investigation (Windows)

当需要调查 Windows 桌面上某个窗口的来源时使用 — 结合 Python ctypes 枚举窗口、
截图、视觉分析的三步法。

## 为什么不用 PowerShell

PowerShell 通过 git-bash 传递命令时，中文输出有 GBK/UTF-8 编码问题，导致
`subprocess` 解码失败。直接用 Python ctypes 调用 Win32 API 最可靠。

## 三步法

### 1. 枚举所有可见窗口

```python
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

windows = []

def enum_callback(hwnd, lParam):
    if user32.IsWindowVisible(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            
            cls_buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cls_buf, 256)
            cls = cls_buf.value
            
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            x, y = rect.left, rect.top
            w, h = rect.right - rect.left, rect.bottom - rect.top
            
            if w > 0 and h > 0:
                windows.append({
                    'title': title, 'class': cls,
                    'x': x, 'y': y, 'w': w, 'h': h, 'hwnd': hwnd
                })
    return True

user32.EnumWindows(WNDENUMPROC(enum_callback), 0)

# 按位置排序，左上角优先
windows.sort(key=lambda w: (w['y'], w['x']))

# 筛选特定区域的窗口
for w in windows:
    if w['x'] < 200 and w['y'] < 200 and w['w'] > 30 and w['h'] > 30:
        print(f"'{w['title']}' ({w['class']}) @ ({w['x']},{w['y']}) {w['w']}x{w['h']}")
```

### 2. 截取桌面（全屏或局部）

```python
from PIL import ImageGrab
# 全屏
img = ImageGrab.grab()
img.save('/tmp/desktop.png')

# 裁剪左上角 500x500
img = ImageGrab.grab(bbox=(0, 0, 500, 500))
img.save('/tmp/corner.png')
```

如果没有 PIL，`mss` 是备选：
```python
import mss
with mss.mss() as sct:
    sct.shot(output='/tmp/desktop.png')
```

### 3. 用 vision_analyze 检查截图

截完图后用 `vision_analyze` 查看，配合精准问题描述。

## 获取更多窗口细节

```python
# 获取窗口样式（判断是否为弹窗/工具窗口/分层窗口）
style = user32.GetWindowLongW(hwnd, -16)   # GWL_STYLE
ex_style = user32.GetWindowLongW(hwnd, -20) # GWL_EXSTYLE

WS_VISIBLE = 0x10000000
WS_POPUP = 0x80000000
WS_EX_TOOLWINDOW = 0x80      # 不在任务栏显示
WS_EX_LAYERED = 0x80000      # 分层窗口（常见于叠加层/悬浮窗）
WS_EX_TRANSPARENT = 0x20     # 透明窗口（点击穿透）

print(f"Visible: {bool(style & WS_VISIBLE)}")
print(f"Popup: {bool(style & WS_POPUP)}")
print(f"ToolWindow: {bool(ex_style & WS_EX_TOOLWINDOW)}")
print(f"Layered: {bool(ex_style & WS_EX_LAYERED)}")
```

## 根据窗口标题查找进程来源

```python
# 根据窗口标题找进程
hwnd = user32.FindWindowW(None, "窗口标题")
if hwnd:
    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    # 然后用 PowerShell 查进程路径
    # Get-Process -Id <pid> | Format-List Path,Company
```

## 常见自启窗口来源

用 PowerShell 检查注册表自启项（注意 `\$` 转义）：
```bash
powershell -NoProfile -Command "Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' | Format-List"
```

常见"意想不到"的自启窗口来源：
- Eagle（素材管理）：`--hidden` 参数有时无效，在左上角留下 480×440 的深色窗口
- CC Switch（桌面切换工具）：在 (0,0) 留下 15×15 的微小叠加层
- 各种 Electron 应用（飞书、豆包、Kimi 等）的辅助窗口

## 控制台黑窗口陷阱：窗口属于 conhost.exe，不是进程本身

**症状**：pythonw.exe 启动的进程（GUI 子系统，本不该有控制台）却出现一个空控制台黑窗口，
标题 = 可执行文件完整路径（如 `C:\...\hermes-agent\venv\Scripts\pythonw.exe`）。

**根因（两层，先诊断再修）**：
- **A. 进程内部某 C 扩展调用 `AllocConsole`**（winloop / onnxruntime / Rust/Cython 库）——
  启动 flags（`DETACHED_PROCESS` / `CREATE_NO_WINDOW`）挡不住进程内部自建窗口，只能事后隐藏。
- **B. uv venv 的 `Scripts/pythonw.exe` 是 console 子系统 launcher stub（2026-08-07 实测）**。
  用 `file Scripts/pythonw.exe` 验证：真 pythonw 应显示 `PE32+ (GUI)`，uv venv 的 stub 显示
  `PE32+ (console)`。stub 通过 `__PYVENV_LAUNCHER__` 环境变量把 venv 上下文传给 base 解释器，
  exec 出的还是 base `python.exe`（console 子系统）→ Windows 强制分配 conhost 黑窗口。
  启动 flags 管不到 stub 内部 exec——**只能程序层治本**：PE subsystem 检测（2=GUI/3=console）
  找到真 GUI pythonw.exe 绕过 stub，并注入 `__PYVENV_LAUNCHER__=<venv>\Scripts\python.exe`
  保持 venv 上下文。排查方法：`Get-CimInstance Win32_Process` 查命令行 → 父子链
  （pythonw stub → base python.exe → conhost.exe）即见真相。

**排查陷阱**：控制台窗口的 HWND 属于 **conhost.exe**，不是所属进程。因此：
- `GetWindowThreadProcessId(hwnd)` 按 pythonw 的 PID 找窗口 → 找不到（返回空）
- PowerShell `Get-Process -Id <pid> | Select MainWindowHandle` → 返回 0

正确做法：枚举**所有**顶层窗口，按**标题**（= 进程路径）匹配，再取 pid 交叉验证。

```powershell
Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public class W {
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  public delegate bool EnumWindowsProc(IntPtr h, IntPtr l);
}
'@
$found = @()
[W]::EnumWindows({ param($h, $l)
  $sb = New-Object System.Text.StringBuilder 512
  [W]::GetWindowText($h, $sb, 512) | Out-Null
  if ($sb.ToString() -like '*pythonw*') {
    $script:found += ('hwnd=' + $h + ' title=[' + $sb.ToString() + ']')
  }
  return $true
}, [IntPtr]::Zero) | Out-Null
$found
```

## 隐藏窗口（一次性）

找到 hwnd 后直接 ShowWindow SW_HIDE（cmd=0）：

```powershell
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class W3 {
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
}
'@
[W3]::ShowWindow([IntPtr]<hwnd>, 0) | Out-Null
[W3]::IsWindowVisible([IntPtr]<hwnd>)   # False = 已隐藏
```

## 常驻守卫脚本（防重启复发）

daemon 有 idle-timeout 自退 + 被网关重新拉起时，窗口会反复重现。部署 pythonw 轮询守卫：

1. 写 `hide_hindsight_window.py`（2 秒轮询，ctypes EnumWindows 匹配标题标记后 SW_HIDE）：
```python
import ctypes, ctypes.wintypes as wt, time
user32 = ctypes.windll.user32
SW_HIDE = 0
ENUM_PROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
MARKER = "hermes-agent\\venv\\Scripts\\pythonw.exe"   # 精确锁定，防误伤其他 pythonw

def _hide_pass():
    def callback(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            if MARKER in buf.value:
                user32.ShowWindow(hwnd, SW_HIDE)
        return True
    user32.EnumWindows(ENUM_PROC(callback), 0)

while True:
    try: _hide_pass()
    except Exception: pass
    time.sleep(2)
```

2. 用 pythonw.exe 运行（自身无窗口）+ schtasks 开机自启：
```bash
schtasks /Create /TN "Hermes-HideHindsightWindow" \
  /TR "\"$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/pythonw.exe\" \"C:\\...\\hide_hindsight_window.py\"" \
  /SC ONLOGON /RL LIMITED /F
schtasks /Run /TN "Hermes-HideHindsightWindow"   # 立即验证
```
注意：git-bash 里 schtasks 用**单斜杠** `/Create`（`//Create` 双斜杠报"无效参数/选项"）；
成功输出是 GBK 乱码（�ɹ�），正常编码噪音，看退出码即可。

**实战案例（Hindsight daemon）**：Hermes 网关（`hermes_cli.main serve`）拉起的
`hindsight_api.main --daemon --idle-timeout 300 --port 9177`（Hindsight 记忆服务）会造
黑窗口。守卫脚本 `C:\Users\HMSJ\Documents\Hermes\scripts\hide_hindsight_window.py` +
计划任务 `Hermes-HideHindsightWindow`（ONLOGON）已部署。卸载：`schtasks /Delete /TN "Hermes-HideHindsightWindow" /F`。
