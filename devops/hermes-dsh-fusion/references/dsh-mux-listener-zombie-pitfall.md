# DSH mux listener zombie 进程问题（2026-08-20）

> 现场：commit `2630cfc` 修了 `dsh_mux_listener.py` 兜底分支（未登记 session 默认桌面留痕），
> commit 干净、`git status` 干净、commit hash 对——但**用户实际提问仍按旧逻辑推到了飞书妖玉 DM**。
> 根因是 **zombie 长驻进程**。

## 现象与时间线

```
[10:02:01] hermes-mux-listener.log  # 新进程拉起（commit 后）
[10:04:36] hermes-84d606e3 → [路由] 未登记会话 → 默认桌面留痕  ✅ 新代码行为
```

但**之前** 08:46 的提问堆到了妖玉 DM——是另一个老进程 PID 54676 推的（08:47:01 启动，
commit `2630cfc` 是 10:00+ 之后才落盘的，老进程加载的是更早的代码）。

```
PID   StartTime         CommandLine
------ ----------------- -------------------------------------------------
26308 2026/8/20 10:02:01 dsh_mux_listener.py --once     # 新进程（commit 后）
54676 2026/8/20 08:47:01 dsh_mux_listener.py --once     # zombie（commit 前）
```

## 根因：--once + check_alive() 不感知代码版本

`scripts/dsh_mux_listener.py:275-301` 的保活逻辑：

```python
def check_alive():
    sock = socket.socket(...)
    sock.settimeout(2)
    try:
        sock.connect(("127.0.0.1", 8080))
    except Exception:
        return "dsh-down"
    finally:
        sock.close()
    for line in os.popen('wmic process where "name=\'pythonw.exe\'" get commandline').read().splitlines():
        if "dsh_mux_listener" in line:
            return "alive"     # ← 只看命令行是否含关键词
    return "not-running"

def main():
    if "--once" in sys.argv:
        st = check_alive()
        if st == "alive":
            return 0         # ← 跳过，进程退出
        if st == "dsh-down":
            return 1
        sys.exit(run_forever())  # ← 启动常驻
```

**问题**：
1. `check_alive()` 只检查「pythonw.exe + 命令行含 dsh_mux_listener」
2. **不看进程加载的代码版本**——老进程没死就一直被当 alive
3. 老进程启动时走了 `not-running` 分支 → `sys.exit(run_forever())` → 进程**常驻 ws 监听**
4. 后续每次 `--once` 计划任务看到 alive → return 0 → 老进程不死
5. 磁盘代码 commit 之后，老进程仍按旧代码处理 mux 帧

**触发场景**：
- listener 启动后 DSH 服务端是 up 状态
- 没有别的 listener 进程
- `--once` 走 `not-running` 分支 → 进程常驻
- 之后用户改 listener 代码 commit，老进程不感知

## 诊断口诀

**「修复没生效，先 ps 看 listener 进程的 StartTime 是 commit 之前还是之后；之前就是 zombie。」**

```powershell
# 看 listener 进程
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
  Where-Object {$_.CommandLine -like '*dsh_mux_listener*'} |
  Select-Object ProcessId, CreationDate, CommandLine | Format-Table -AutoSize

# 对比 commit 时间
git log -1 --format="%ai" scripts/dsh_mux_listener.py
# → 2026-08-20 09:55:00 +0800
```

`CreationDate < commit 时间` = zombie，必须 kill。

## 修法：手动 kill 老进程

```powershell
$pid = (Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
  Where-Object {$_.CommandLine -like '*dsh_mux_listener*'} |
  Select-Object ProcessId).ProcessId
Stop-Process -Id $pid -Force
```

等下一分钟计划任务跑 `--once` → `check_alive()` 看不到 alive → 走 `not-running` → `run_forever()` 启动新进程 → 加载新代码。

新进程 `CreationDate` 必然 > commit 时间 → 行为按新代码走。

## 根治方向（未来再修，未做）

`check_alive()` 应该**比对代码 mtime 或 commit hash**，发现代码变了就强制重启进程：

```python
# 伪代码
def check_alive():
    current_mtime = os.path.getmtime("scripts/dsh_mux_listener.py")
    sock = socket.socket(...)
    try:
        sock.connect(("127.0.0.1", 8080))
    except: return "dsh-down"
    finally: sock.close()
    for proc in get_listener_processes():
        if proc.mtime < current_mtime:
            log(f"zombie listener detected, killing PID {proc.pid}")
            proc.kill()
            return "not-running"  # 让本任务启动新进程
        if proc.alive():
            return "alive"
    return "not-running"
```

**当前没做**的根因：进程无内置的 mtime 字段，需 `psutil` 或 WMI 扩展查进程的 file handle，复杂度高。
当前接受「commit 后手动 kill 老进程」的纪律。

## 审计纪律

**改 listener 类长驻进程的代码 → commit 之后立即查进程 StartTime**，必要时主动 kill 而不是等自然过期。

- **DSH_Watchdog 守护的是 DSH web 进程（node，8080），不是 listener（pythonw）**
- listener 没人替它做热重启
- **不要假设**「代码改了下次自然 reload」——`--once` 守护机制只看进程存在性

## 真实日志证据

```
$ tail -5 .hermes/dsh-mux-listener.log
[2026-08-20 09:55:40] [路由] 无 source → cwd 判定飞书，推妖玉 DM: ✓    # 老进程 PID 54676 行为
[2026-08-20 09:58:58] [路由] 无 source → cwd 判定飞书，推妖玉 DM: ✓    # 老进程
[2026-08-20 10:02:01] [保活检查] DSH=not, 监听器=not-running             # 老进程已被 kill
[2026-08-20 10:02:01] 连接 ws://127.0.0.1:8080/api/events.mux?token=...   # 新进程 PID 26308 启动
[2026-08-20 10:04:36] [路由] 未登记会话 → 默认桌面留痕                    # ✅ 新代码行为
```

## 关联

- SKILL.md 坑 22（zombie listener）+ 坑 23（source 硬性 warn）
- `scripts/dsh_mux_listener.py:275-301`（保活 + 启动逻辑）
- `references/dsh-reverse-channel-source-missing.md`（v3 全表退化修复路径 C）
- 提交 2630cfc（路径 C：未登记默认留痕）
- 提交 078f407（桥 CLI source 缺失硬性 warn）
- 计划任务 `\DSH_Mux_Listener_Polling`（每分钟 `--once` 守护，原名 `\Hermes_DSH_Inbox_Watcher` 已弃用——见下方「命名陷阱」）

## 计划任务命名陷阱（2026-08-20 实测连踩两次）

**问题**：旧任务叫 `Hermes_DSH_Inbox_Watcher`，名字让人以为跑的是 `dsh_inbox_watcher.py`（已弃用），而实际跑的是 `dsh_mux_listener.py`。

**后果**：agent 在推理时反复判断错「监听器状态」——误以为 listener 撤了、inbox 插件在跑；事实正好相反。**同一会话被纠正两次**才找到真相（"插件不是已经拿掉了" / "监听器不是撤了吗"）。

**根因分析**：
- `Hermes_DSH_Inbox_Watcher` 这个名字**误导在三个维度**：
  1. `Hermes_*` 前缀暗示这是 Hermes 自己的任务，但实际是监听 DSH 事件
  2. `*_Inbox_*` 暗示是收件箱/通知相关，但实际跑的是 events.mux 反向通道
  3. `_Watcher` 后缀暗示是只观察不行动，但实际跑的是常驻 ws + 飞书推送
- 看 schtasks 命令列 `TaskName: \Hermes_DSH_Inbox_Watcher` + `Task To Run: pythonw dsh_mux_listener.py` —— **名字与实际脚本严重错位**

**改法（已落地 2026-08-20）**：
1. schtasks /Query 导出原任务 XML
2. Python 改 URI（保留 UTF-16 LE BOM）：
   ```python
   xml_str = xml_bytes.replace(b'\\Hermes_DSH_Inbox_Watcher', b'\\DSH_Mux_Listener_Polling')
   ```
3. 写文件：`\xff\xfe` BOM + `xml_str.encode('utf-16-le')` —— schtasks /Create 要 UTF-16 LE BOM 才认
4. schtasks /Create /XML 创 + schtasks /Delete /TN old /F 删

**命名约定**（从今往后）：
- **计划任务名 = 实际跑的脚本去掉 .py 后缀 + `_Polling`/`_Watchdog`/`_Health`/`_Cleanup` 后缀表明行为**
- **不要混用 Inbox/Watcher/Listener 这些让人推断错的词**——它们各自代表不同的功能边界
- 例：`DSH_Mux_Listener_Polling`（polling = 每分钟拉一次保活）/ `DSH_Watchdog`（watchdog = 守护 DSH web 进程）/ `HermesDashboard`（具体应用名）
- **创建计划任务后立即核对**：`schtasks /Query /TN <name> /V /FO LIST | grep "Task To Run"` —— 名字与实际命令必须对得上