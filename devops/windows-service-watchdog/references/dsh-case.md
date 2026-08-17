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

## 部署产物（2026-08-14）
| 项 | 位置 |
|---|---|
| watchdog 脚本 | `Projects/deepseek-harness/dsh_watchdog.py`（纯血：系统 node + 系统 Python312，零 Hermes 引用） |
| 计划任务 | `DSH_Watchdog`（每 5 分钟，系统 pythonw 运行，跑完即退） |
| 服务日志 | `Projects/deepseek-harness/logs/dsh.log` |
| 看门狗日志 | `Projects/deepseek-harness/logs/dsh_watchdog.log` |
| 状态/冷却 | `Projects/deepseek-harness/dsh_watchdog_state.json` |

## 本实例踩坑（2026-08-14 实测）
1. **后台进程随会话死**：Hermes terminal(background=true) 起的服务，会话结束进程即亡——这是最初「DSH 挂了」的根因（不是崩溃）
2. **pnpm 包装进程被杀，node 子进程成孤儿**：kill pnpm 父进程后 8080 仍 LISTEN（新 PID），需按端口再杀
3. **验证进程归属**：`powershell -NoProfile -Command "(Get-Process -Id PID).Path"` 确认是 `C:\Program Files\nodejs\node.exe`（纯血达成）

## 未决事项
- UI 跑 LLM 任务需要 `DEEPSEEK_API_KEY`（本机 LOCALAPPDATA 里有），watchdog 未注入——
  凭据操作不擅自做，用户拍板后才从本机凭据导出接上
