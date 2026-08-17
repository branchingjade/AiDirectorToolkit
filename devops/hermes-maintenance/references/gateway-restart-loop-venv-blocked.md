# Gateway 反复 SIGKILL 循环 + venv-blocked 更新失败（2026-08-12 完整取证）

## 现象

一天内 gateway.log 出现多次 `exited UNCLEANLY (no exit path ran — SIGKILL / OOM / VM death)`，
每次死亡前 `state/gateway.heartbeat` 都是新鲜的（30s 心跳周期内）——**进程活着被外部强杀，不是卡死**。
watchdog 记录多次「进程不存在」并尝试拉起，但拉起常失败（gateway.log 无对应 `Starting Hermes Gateway`）。

## 三方对账定位法（核心方法）

把三个来源的时间线对齐，30 秒定位根因：

| 来源 | 内容 | 揭示什么 |
|---|---|---|
| `logs/gateway.log` | `Starting Hermes Gateway` / `exited UNCLEANLY` / `Gateway stopped` | 重启频率、死亡方式（SIGKILL vs 优雅） |
| `state/gateway_outage.json` | watchdog 检测时间 + reason + restart_attempted | 检测与拉起是否发生；拉起成功与否看有无对应 START |
| `logs/desktop.log` + `logs/update.log` | 桌面 app 自动更新活动 | update 流程是强杀 gateway 的高频凶手 |

**拉起成功判定**：watchdog 检测时间 +30s 内有 `Starting Hermes Gateway` = 成功；
检测后无任何 START（gateway.log 和 gateway-stdio.log 都无痕迹）= 拉起失败，进程启动即崩（常因 update 干扰期 venv 被锁/环境损坏，崩在打印启动横幅之前）。

## 本机根因：桌面 app 自动更新恢复循环

desktop.log 铁证链（无时间戳，但 update.log 的时间戳可对上）：

```
[hermes] [updates] venv-blocked: 2 process(es) hold the install
[hermes] [updates] error: Update aborted: another Hermes process is using this installation.
[hermes]   PID 3892  python.exe  ...\.hermes-runtime\python\generation-...\cpython-3.11
[hermes]   PID 19408 python.exe  ...\venv\Scripts\python.exe -m hermes_cli.main dashboard --host 0.0.0.0
[hermes] [bootstrap] handed off bootstrap-needed recovery to updater: hermes-setup.exe --update --branch main; exiting desktop to release app.asar
[hermes] [boot] Desktop boot failed: Hermes recovery was handed off to Hermes Setup.
```

循环机制：
1. 桌面 app 启动 → 检测到 staged updater / bootstrap 标记 → 尝试自动更新
2. 更新器扫描 venv → 发现常驻服务锁 venv → `venv-blocked` abort
3. 桌面 app 交棒 `hermes-setup.exe --update` 并退出（释放 app.asar）
4. setup.exe 更新流程 **SIGKILL gateway**（这是 gateway 反复死的直接来源）
5. 更新完成桌面重启 → 又检测到恢复标记 → 循环

期间 update.log 可能显示多次 `Already up to date!`（11:47 / 11:52 各一次）——更新本身成功了，
但桌面 app 的 recovery 交棒链让 setup.exe 反复触发，每次触发都强杀一次 gateway。

## venv-blocked 完整名单

**锁 venv 的进程 = 所有用 venv python / hermes-runtime python 跑的 Hermes 常驻进程，gateway 豁免。**

| 进程 | 命令行特征 | 备注 |
|---|---|---|
| 桌面 app backend | `serve --host 127.0.0.1/0.0.0.0 --port 0` | venv python + hermes-runtime python 两个解释器都锁 |
| HermesDashboard | `dashboard --host 0.0.0.0`（9120） | 计划任务常驻，2026-08-12 实际拦路的 |
| HermesRemoteServe | `serve --host 0.0.0.0 --port 9119` | 计划任务 |
| hide_hindsight_window.py | `pythonw ...hide_hindsight_window.py` | ONLOGON 守卫 |
| 更新 runner 自身 | `python ops-update-runner.py` | 用 venv python 跑 hermes update = 自锁 |

**豁免机制**：桌面更新器调 `hermes_cli._scan_venv_blockers.py` → `_detect_venv_python_processes()` 扫描，
`_is_pausable_gateway(cmdline)` 豁免 `gateway run` 命令行的进程——因为下游 `_pause_windows_gateways_for_update()`
能优雅停 gateway，其余进程没有 pause 机制必须拦截。手动排查时别把 gateway 当 blocker。

**更新器只能优雅停 gateway**（update.log 的 `Paused gateway profile(s): default`），
对 dashboard/serve/守卫脚本停不了 → 主动拒绝（防装一半留坏环境，是保护不是故障）。

## 历史 update.log 中的同类记录（同一病根，2026-08-07 起反复出现）

- 08-07 23:05：serve --port 0（桌面 backend）+ hermes-runtime python
- 08-09 11:43/11:45：serve 0.0.0.0 + hermes-runtime python + 裸 python.exe + hide_hindsight_window.py（4 个）
- 08-10 09:15：serve 0.0.0.0 + hermes-runtime python + 裸 pythonw.exe（3 个）
- 08-12：hermes-runtime python（桌面 backend）+ dashboard（2 个）

模式：**桌面 app 开着 + 任何常驻 Hermes python 服务 = 更新必被 venv-blocked 拦截**。

## watchdog 表现复盘（诚实结论）

- **检测职能：全勤**。6 次检测全部记录（12:05 / 12:35 / 13:10 / 13:45 / 14:15 / 15:30），reason 全为「进程不存在」，判据正确
- **拉起职能：6 次只成功 2 次**（14:15→14:16、15:30→15:30:48 = 当前进程）。12:05–13:45 四次拉起后
  gateway.log 和 gateway-stdio.log 双双无启动痕迹 → 拉起的进程启动即崩（update 恢复循环期间 venv 被锁）
- **后果**：11:53 到 14:16 约 2 小时 20 分 gateway 实际离线
- **短板**：拉起后不做存活验证；30 分钟冷却期内失败不重试（outage 记录间隔 30–35 分钟 = 冷却期）。
  补强方向：拉起后等 20s 查端口，失败立即重试而非等冷却

**注意**：outage.json 的检测间隔约 30 分钟 ≠ watchdog 每 5 分钟跑一次——5 分钟跑一次但只在
检测到异常时写记录，且 30 分钟冷却期内即使再检测到也不重试。间隔=冷却期是「异常持续」的信号。

## ops-panel 一键更新三重死锁

面板链路：`POST /update/prepare`（`$LOCALAPPDATA/hermes/plugins/ops-panel/dashboard/plugin_api.py`）
→ detached 启动 `Documents/Hermes/scripts/ops-update-runner.py`（状态机：
waiting-app-close → updating → patches-check → restoring → done|failed）。

死锁（代码实证，`ops-update-runner.py`）：
1. **等 Hermes.exe 退出 10 分钟超时**（`wait_app_close`，Get-CimInstance Name='Hermes.exe'）——桌面 app 常驻则必超时
2. **HermesDashboard 不在 runner 停/启清单**——`restore_services()` 只处理
   Hermes_Gateway_Watchdog（enable）/ HermesRemoteServe（start）/ Hermes_Gateway（start），
   没有 HermesDashboard → 更新时面板自己锁 venv → `hermes update` 必然 venv-blocked
3. ~~runner 用 venv python 跑 `hermes update` → 自己也锁~~ **不成立（2026-08-12 源码证伪）**：
   `hermes_cli/update_cmd.py:2899 _detect_venv_python_processes` 排除调用进程及祖先
   （docstring 原文 "a CLI `hermes update` itself runs from the venv python"）——runner
   用 venv python 跑 update 不会被自己拦。**无需换非 venv 解释器。**

**状态解读**：
- `state/ops-panel-update.json`：`{"phase":"failed","error":"等待 app 退出超时"}` = 上次失败留痕
- runner 日志在 `state/ops-update-runner.log`（格式 `=== ops-update-runner 启动 ===`）——与
  `logs/update.log` 区分：update.log 里没有此标记的更新不是面板触发的（如 CLI 手动 update）
- **8月9日超时真相**：当时是 dryrun 模式——前端 dryrun 不调 `/update/close-app`，桌面 app 常驻
  → runner 傻等 600s 超时。real 模式前端先 `/update/close-app`（杀 Hermes.exe）再 `/update/prepare`
  （审计日志 `state/ops-panel-audit.log` 有 `OK close desktop app | killed=[...]` 实证）

**✅ 已修复（2026-08-12 会话内落地并验证）：**
1. `service.py` SERVICES 表加 `dashboard` 条目（HermesDashboard / 9120），`_UPDATE_START_ORDER`
   加 dashboard；**`_UPDATE_STOP_ORDER` 不加**——prepare 运行在 dashboard 进程内，停自己=自杀
   （响应丢失）。dashboard 由独立 runner 停。
2. `ops-update-runner.py` 新增 `stop_dashboard()`：updating 前 Stop-ScheduledTask HermesDashboard
   + taskkill 9120 PID 兜底（死锁②根治）；`restore_services` 加 HermesDashboard start（恢复面板）。
3. `wait_app_close` 两阶段：120s 未退 → 自动杀 Hermes.exe 主进程（`_kill_hermes_main`，用户已
   在前端确认流程）→ 再等 120s（死锁①加固，上限从 600s 收紧到 240s）。
4. 生效条件：**改插件后端必须重启 HermesDashboard**（`taskkill /F /PID <9120pid>` + `schtasks /Run
   /TN "HermesDashboard"`），重启 gateway 对 dashboard 插件后端无效。
5. 验证法：`venv python -c "import sys; sys.path.insert(0, r'<插件目录>/dashboard'); from
   ops_panel.service import SERVICES, _UPDATE_STOP_ORDER, _UPDATE_START_ORDER; assert 'dashboard'
   in SERVICES and 'dashboard' in _UPDATE_START_ORDER"`——断言通过即生效。

## 排查命令速查

```bash
# 进程生命周期时间线
grep -aE "Starting Hermes Gateway|exited UNCLEANLY|Gateway stopped" "$LOCALAPPDATA/hermes/logs/gateway.log" | tail -30

# watchdog 检测记录
cat "$LOCALAPPDATA/hermes/state/gateway_outage.json"

# 桌面 app 更新活动 + venv-blocked 证据
grep -aE "venv-blocked|handed off|Update aborted" "$LOCALAPPDATA/hermes/logs/desktop.log"

# 更新历史
tail -50 "$LOCALAPPDATA/hermes/logs/update.log"

# 心跳新鲜度（死前心跳新鲜 = 外部强杀，非卡死）
stat -c '%y' "$LOCALAPPDATA/hermes/state/gateway.heartbeat"

# watchdog 拉起机制确认（cmd /c Hermes_Gateway.cmd，无 kill 逻辑）
grep -nE "start_gateway|Popen" "$LOCALAPPDATA/hermes/scripts/gateway_watchdog.py"
```

## 诊断原则

1. `exited UNCLEANLY` 本身不是故障——**计划内强杀（Stop-Process -Force 重启）也是这个痕迹**。
   判据是心跳：死前心跳新鲜 + 无干净停机 = 外部强杀；先找谁在杀，别修 gateway 自己。
2. 心跳新鲜 ≠ 进程健康——gateway 活着但心跳停 = 真卡死（watchdog 判据三件套：进程/端口 + 日志新鲜 + 心跳新鲜）。
3. 更新失败先看 venv-blocked 名单，别怀疑更新器本身——「桌面 app 开着时更新失败」是防破坏保护。
