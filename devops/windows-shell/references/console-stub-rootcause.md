# Console 子系统 stub → 黑窗口：根因与程序层治本（2026-08-07 实测）

## 场景

uv venv 的 `Scripts/pythonw.exe` 实际是 **console 子系统** launcher stub（`file` 输出
`PE32+ executable (console)`）。daemon 启动链：

```
gateway (hermes_cli.main serve)
  └─ venv\Scripts\pythonw.exe (launcher stub, console 子系统)
      └─ base python.exe (hermes-runtime, console 子系统) ← stub 用 __PYVENV_LAUNCHER__ 拉起
          └─ conhost.exe ← 黑窗口宿主
```

`daemon_embed_manager._windows_gui_interpreter` 假设 pythonw 是 GUI 子系统（注释声称
"never allocates a console"）——**uv venv 下这个假设是错的**：stub 是 console，
exec 出的还是 console 进程，Windows 强制分配 conhost。

## 诊断链（复现路径）

1. 进程树：`Get-CimInstance Win32_Process` 按命令行过滤 `*hindsight_api*`，看父子链。
2. 窗口归属：控制台窗口属于 **conhost.exe** 不是进程本身——对 pythonw 的 PID 做
   `GetProcess.MainWindowHandle` 返回 0；必须 EnumWindows 全部顶层窗口按标题匹配
   （标题 = 进程路径）。
3. PE 子系统判定（关键证据）：`file` 命令看 console vs GUI；或用 Python 读 PE 头。
4. 复现实验：用 `subprocess.Popen([venv_pythonw, "-m", ..., "--daemon", ...])` +
   `_HINDSIGHT_DAEMON_CHILD=1` 环境，观察 spawn 出的子进程是 base python.exe
   （console）→ 坐实 stub 行为。

## PE subsystem 解析（正确写法）

Subsystem 字段位于 Optional Header 偏移 +68（PE32 和 PE32+ 相同；+88 是数据目录，
曾经踩坑写错）。magic 在 pe_off+24。

```python
def _pe_subsystem(exe_path: str) -> int | None:
    import struct
    with open(exe_path, "rb") as f:
        mz = f.read(0x40)
    if len(mz) < 0x40 or mz[:2] != b"MZ":
        return None
    pe_off = struct.unpack("<I", mz[0x3C:0x40])[0]
    with open(exe_path, "rb") as f:
        f.seek(pe_off)
        if f.read(4) != b"PE\x00\x00":
            return None
        f.seek(pe_off + 24)
        magic = struct.unpack("<H", f.read(2))[0]
    if magic not in (0x10B, 0x20B):  # PE32 / PE32+
        return None
    with open(exe_path, "rb") as f:
        f.seek(pe_off + 24 + 68)
        return struct.unpack("<H", f.read(2))[0]  # 2=GUI, 3=console
```

## 治本补丁（daemon_embed_manager 三件套）

1. **`_pe_subsystem(exe)`**：如上，返回 2/3/None。
2. **`_find_gui_pythonw(preferred_dir)`**：按序扫候选，只收 subsystem==2 的真 GUI
   pythonw：
   - `preferred_dir/pythonw.exe`（若 GUI）
   - `Path(sys.executable).with_name("pythonw.exe")`（若 GUI）
   - pyvenv.cfg `home =` 指向的 base 目录 `pythonw.exe`
   - PATH 上的 `pythonw.exe`（GUI 才收）
   - 去重，返回第一个 GUI 的。
3. **`__PYVENV_LAUNCHER__` 注入**（Popen 前）：
   ```python
   if sys.platform == "win32" and cmd and cmd[0].lower().endswith("pythonw.exe"):
       venv_python = Path(sysconfig.get_path("scripts")) / "python.exe"
       if venv_python.exists():
           env["__PYVENV_LAUNCHER__"] = str(venv_python)
   ```
   缺失此变量时 base 解释器 sys.prefix 指向自己、找不到 venv site-packages，
   import pywintypes/hindsight_api 失败（报 ModuleNotFoundError）。

改完 `_windows_gui_interpreter` 仍保留 console stub 作为最后兜底（有窗口总比起不来强）。

## 验证（必须做，含 env 注入）

```python
# 复刻 _start_daemon_locked 的 env：os.environ.copy() + LLM key 注入
# HINDSIGHT_API_LLM_API_KEY 来自 Hermes .env 的 HINDSIGHT_LLM_API_KEY
# （hindsight config.json 里没有 key！）
# 启动后轮询 http://127.0.0.1:<port>/health 直到 200
# 再 EnumWindows 确认无 pythonw 标题的可见窗口；netstat 确认进程形态：
#   单进程 pythonw.exe（不再有 python.exe 子进程）
```

## 生产生效注意

- 补丁在 site-packages（`hindsight_embed/daemon_embed_manager.py`），**hermes update
  会覆盖，需重打**。
- 已运行的 gateway 进程内存里是旧模块——**必须重启 Hermes 才生效**，重启前
  守护脚本/一次性隐藏继续用。
- 守卫脚本只治标（隐藏窗口），本方案治本（窗口根本不产生）。
