---
name: windows-service-watchdog
description: 本地服务常驻/自愈看门狗，计划任务+端口检测+冷却防风暴。触发词：XX挂了、常驻、开机自启、自动拉起。
version: 1.0.0
author: Hermes (curator)
license: MIT
metadata:
  hermes:
    tags: [devops, windows, watchdog, 常驻, 自愈]
    related_skills: [hermes-maintenance, cron-ops, windows-shell]
---

# Windows 本地服务常驻看门狗

## When to Use
用户说某个本地服务「XX挂了」「要常驻」「开机自启」「自动拉起」，或要把跑在后台终端/会话里的服务变成独立存活——用本技能。

## 适用场景
任何本地服务（web UI、daemon、CLI 工具）需要：挂了自动拉起 / 开机自启 / 独立于启动它的终端存活（会话关掉服务不死）。

## 铁律：纯血原则（用户拍板 2026-08-14）
用户对独立服务要求「纯血」——**零 Hermes 依赖**：
- 运行时用系统独立安装的（系统 node `C:\Program Files\nodejs\node.exe`、系统 Python312），不借 hermes 目录里的 node / venv
- watchdog 脚本放**服务自己的项目目录**，日志/状态文件全在服务地盘（logs/、state json 在项目内）
- 不引用 HERMES_HOME / lark-cli / hermes venv / hermes logs/state
- Hermes 死活不影响该服务
⚠️ 反面案例：gateway_watchdog.py 模式（HERMES_HOME + lark-cli 飞书告警 + venv pythonw）**只用于守护 Hermes 自身**；给非 Hermes 服务照抄该模式会被用户当场纠正（「gateway_watchdog依赖hermes，我要的是纯血DSH」）。

## 标准配方（三步）
1. 写 watchdog 脚本（Python，见下节），放服务项目根目录
2. 建计划任务：每 5 分钟触发一次，跑完即退（无常驻进程）
3. 实测验证：杀当前实例 → `--force` 跑一次 → curl 验 200 → 确认进程归属

## 脚本要点（Python watchdog）
- 健康判据：`netstat -ano` 端口 LISTENING（主判据；计划任务环境可靠，不依赖读其他进程 CommandLine）
  - 中文 Windows netstat 输出是 GBK → subprocess 加 `errors="replace"` 容错解码
- 拉起：`subprocess.Popen(..., creationflags=subprocess.CREATE_NO_WINDOW)`（防弹空白控制台窗），stdout/stderr 重定向到服务地盘 logs/
- 冷却防风暴：state json 记录 last_restart_at，30 分钟内不重复拉起
- 端口检测异常 → 视为存活（检测不了别乱动，避免误杀/误拉起）
- CLI 参数：`--status` 只查不动作 / `--force` 跳冷却（调试用）

## 建计划任务
```bash
schtasks /Create /TN "任务名" /TR "\"C:\Users\...\Python312\pythonw.exe\" C:\path\to\watchdog.py" /SC MINUTE /MO 5 /F
```
- 运行器用**系统 pythonw**（GUI 无窗口、独立于 Hermes）
- /TR 引号规则：外层双引号包 pythonw 路径，脚本路径不带引号
- 查任务状态：`schtasks /query /tn 任务名 /fo LIST /v`（看 Task To Run / Next Run / Status）

## 验证流程（必须实测，不接受口头声称配好）
1. 按端口找当前实例 PID 杀掉（`netstat -ano | grep ":端口" | grep LISTEN`）
2. `python watchdog.py --force` 手动触发
3. 轮询 `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:端口/` 直到 200
4. 纯血验证：`(Get-Process -Id PID).Path` 必须是系统运行时路径

## 坑
- **pnpm/npm 包装进程被杀后子进程成孤儿**：杀 pnpm 父进程 ≠ 服务停了——node 子进程还挂端口监听（2026-08-14 实测：kill 后台 pnpm 会话后 8080 仍在 LISTEN，PID 是另一个）。先按端口找 PID 再杀
- taskkill 报 Access denied → 回落 `powershell -Command "Stop-Process -Id PID -Force"`
- 服务经 pnpm 启动有 ~30s 依赖解析+供应链检查 → watchdog 直接调实际入口（如 `node --import tsx/esm apps/cli/src/bin.ts web --port 8080`）秒起
- 默认端口起不来先查 Hyper-V/WSL 排除段（3001-3100 常见被占）：`netsh interface ipv4 show excludedportrange`

## 参考资料
- `references/dsh-case.md` — DeepSeek Harness 常驻实例全记录（2026-08-14 部署）
