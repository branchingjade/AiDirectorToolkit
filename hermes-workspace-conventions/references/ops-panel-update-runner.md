# ops-panel 更新执行器（ops-update-runner.py）停机陷阱与恢复（2026-08-09 实测）

桌面 app 触发一键更新（或试运行）时，`Documents\Hermes\scripts\ops-update-runner.py` 以 detached 方式启动并接管更新流程。**关键坑：启动即停全部后台服务，且超时退出时不恢复——gateway 会保持停机（飞书断线）。**

## 触发与状态文件

- 触发：ops-panel 插件的 `/update/prepare` → detached 启动 runner（父进程退出后独立跑）
- 标记文件：`~/AppData/Local/hermes/state/ops-panel-update.json`
  ```json
  {"phase": "waiting-app-close", "ts": ..., "updated_at": "13:26:55", "mode": "dryrun",
   "stopped": {"watchdog": "stopped", "remote-serve": "stopped", "guard": "stopped", "gateway": "stopped"},
   "countdown": 10}
  ```
  - `mode`: `dryrun`（演练，模拟 8 秒不真更新）| `real`（真跑 `hermes update`）
  - `phase`: waiting-app-close → updating → restoring → done/failed
  - **`stopped` 全为 stopped = 服务真被停了**（实测 gateway 8644 掉线）
- 主日志：`~/AppData/Local/hermes/state/ops-panel-update.log`
- 状态查询：`python ops-update-runner.py --check`

## 流程（读代码 2026-08-09）

```
启动 → 读标记文件 → wait_app_close()（轮询 Hermes.exe，最长 10 分钟）
     → 超时: mark("failed", error="等待 app 退出超时"); return 1   ← 不 restore！
     → app 退出: mark("updating") → run_update(mode)   # dryrun=睡 8 秒模拟
     → patches_check_and_restore()   # 补丁反向 check，丢失才正向恢复
     → mark("restoring") → restore_services()   # 恢复 gateway/serve
     → mark("done"/"failed")
```

**陷阱核心（代码 208-210 行）**：`wait_app_close()` 超时直接 `return 1`——**restore_services() 不会执行**。用户正在用桌面 app 时触发更新 = runner 等 10 分钟 → 超时 failed 退出 → gateway 一直停着。dryrun 也一样停服务。

## 恢复流程（实测成功，2026-08-09）

```powershell
Start-ScheduledTask -TaskName 'Hermes_Gateway'
Start-Sleep 15   # gateway 冷启动约 12-15 秒
netstat -ano | grep ':8644' | grep LISTENING   # 应出现 0.0.0.0:8644 LISTENING
tail -5 ~/AppData/Local/hermes/logs/gateway.log  # 看 "Press Ctrl+C to stop" / housekeeping 正常
```
gateway 任务 LogonType=S4U → 拉起无窗口。恢复后可顺带检查：serve（9119）、watchdog、guard 是否也被停（`Get-NetTCPConnection -LocalPort 9119`），按需 `Start-ScheduledTask HermesRemoteServe` / `Hermes_Gateway_Watchdog` / `Hermes-HideHindsightWindow`。

## 判定要点

- 飞书突然断线 + 桌面 app 最近点过更新 → 先看 `state/ops-panel-update.json` 的 `stopped` 字段
- runner 进程存在（`Get-CimInstance Win32_Process` 查 `ops-update-runner`）+ phase=waiting-app-close + app 在跑 = 10 分钟后必 failed，别等它，直接手动恢复服务
- runner 走完 done 后 restore_services 会检测端口——手动已恢复的服务不会被重复拉起（端口已在即跳过）
- 本文件对应的用户可读记录：Obsidian 日志 2026-08-09
