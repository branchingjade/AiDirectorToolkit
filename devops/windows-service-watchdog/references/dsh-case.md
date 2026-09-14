# DeepSeek Harness（DSH）常驻实例记录

## 是什么
DeepSeek 官方 agent 框架（2025-07-31 与 V4 Flash 同天发布，MIT，基于 vendored Cordis「一切皆插件」）。
评估结论（2026-08-14）：开发者预览阶段（官方明示将有破坏性变更），不迁移 Hermes 生态（100+ 技能/插件/cron 已闭环），
源码留 `Projects/deepseek-harness/` 待观察。

## 启动命令
- 完整入口：`pnpm dsh web --port 8080`（含 ~30s pnpm 依赖解析 + 供应链检查 + lefthook postinstall）
- watchdog 直接调用（秒起）：`node --import tsx/esm apps/cli/src/bin.ts web --port 8080`
  - node 要求 `^22.19 || >=24`（AGENTS.md）；系统 node v24.16.0 满足，hermes node v22.23.2 也满足
  - tsx 在项目 `node_modules/.bin/tsx`（tsx/esm 是 ESM-only source-launch 契约）
  - cwd 必须是项目根（模块解析依赖 cwd 的 node_modules）
- ⚠️ 默认端口 3080 起不来：Windows Hyper-V/WSL 把 3001-3100 划进排除端口段
  （`netsh interface ipv4 show excludedportrange` 可查）→ 用 8080

## 部署产物（2026-08-14 → 2026-08-20 升级）
| 项 | 位置 |
|---|---|
| **watchdog 脚本** | **`Documents/Hermes/scripts/dsh_watchdog.py`**（2026-08-20 迁移到 Hermes 工作区 git 管理；旧版 `Projects/deepseek-harness/dsh_watchdog.py` 在 8-18 清理时丢失） |
| 计划任务 | `DSH_Watchdog`（每 5 分钟，系统 pythonw 运行，跑完即退） |
| watchdog 日志 | `Documents/Hermes/.hermes/dsh_watchdog.log` |
| watchdog state | `Documents/Hermes/.hermes/dsh_watchdog_state.json`（含 `last_pid` / `last_pid_started_at`）|

**2026-08-20 三件套升级**（commit `515f726`）：
1. **健康检查 TCP-only → HTTP + 命令行校验**：curl `/` HTTP 200 + `Get-CimInstance` 找带 `--max-old-space-size=8192` + `apps/cli/src/bin.ts` + `web` + `--port 8080` 四段子串的 node.exe。堵三盲区（端口被抢 / boot 失败但 listen / 半开）
2. **冷却反模式 → PID 存活追踪**：state 新增 `last_pid` + `last_pid_started_at`，冷却期内但 PID 已死 → 立即拉起；存活 ≥ 5 分钟 → 重置 `last_restart_at` 为 null
3. **CLI 参数**：`--status`（打印健康+状态）/ `--force`（跳冷却立即拉起）

## 历史残留清理（2026-08-20）
`Projects/deepseek-harness/dsh_watchdog_state.json` + `Projects/deepseek-harness/logs/` 是 8-18 清理前的旧 watchdog 状态文件——脚本已删但文件残留。最后一条记录带 `reason: "preview-url-restart-request"`，DSH 自审证实是桌面 preview pane 会话 `preview_9bed48` 在 00:15:50.959 经 terminal 工具的临时写者补写的虚构 reason（DSH 无任何接受 reason 的 restart RPC，preview 写者也无法定位）。仓库根 `.gitignore` 已加 `dsh_watchdog_state.json` + `logs/` 屏蔽。

## 本实例踩坑
1. **后台进程随会话死**：Hermes terminal(background=true) 起的服务，会话结束进程即亡——这是最初「DSH 挂了」的根因（不是崩溃）。**已修复**：watchdog 通过计划任务拉起，进程祖先是 svchost 不再依赖 Hermes 桌面（2026-08-20 DSH 解耦验证实测：PID 5396 是孤儿，父进程查不到）
2. **pnpm 包装进程被杀，node 子进程成孤儿**：kill pnpm 父进程后 8080 仍 LISTEN（新 PID），需按端口再杀
3. **验证进程归属**：`powershell -NoProfile -Command "(Get-Process -Id PID).Path"` 确认是 `C:\Program Files\nodejs\node.exe`（纯血达成）

## 未决事项
- UI 跑 LLM 任务需要 `DEEPSEEK_API_KEY`（本机 LOCALAPPDATA 里有），watchdog 未注入——
  凭据操作不擅自做，用户拍板后才从本机凭据导出接上
