---
name: windows-service-watchdog
description: 本地服务常驻/自愈看门狗，计划任务+端口检测+冷却防风暴。触发词：XX挂了、常驻、开机自启、自动拉起。
version: 1.2.0
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

⚠️ **TCP-only 健康检查有三盲区**（2026-08-20 DSH 解耦收尾实测）：
1. **端口被抢**：其他程序占目标端口 → `socket.create_connection` 通过 → 判"健康"，DSH 永不起
2. **boot 失败但 listen**：进程已绑端口但内部初始化失败 → TCP 通过 → 判"健康"，永远不复活
3. **半开/挂起进程**：进程僵死但 listen 不退 → TCP 通过 → 判"健康"

**升级路径**：HTTP 探测（curl `/` HTTP 200，超时 ≤4s）+ 进程命令行校验（`Get-CimInstance Win32_Process` 找带 `--max-old-space-size` + `apps/cli/src/bin.ts` + `web` + `--port <PORT>` 四段子串的 node.exe）。DSH 升级版 commit `515f726` 是完整参考实现。

⚠️ **冷却反模式**（2026-08-20 实测）：原版冷却只判断"距上次拉起 < N 分钟"，**没考虑上次进程是否还活着**。双崩集群场景（DSH 拉起后 30 秒内又死）会因冷却而**整整 10 分钟不复活**，期间 5 分钟轮询都白跑。

**修法**：state 里跟踪 `last_pid` + `last_pid_started_at`：
- **冷却期内但 PID 已死** → 跳过冷却立即拉起（自愈失败场景）
- **拉起后存活 ≥ 5 分钟** → 重置 `last_restart_at` 为 null（健康重生，防双崩推迟）

基础要点：
- 健康判据：`netstat -ano` 端口 LISTENING（基础版）/ `curl /` HTTP 200 + 命令行校验（升级版）
  - 中文 Windows netstat 输出是 GBK → subprocess 加 `errors="replace"` 容错解码
- 拉起：`subprocess.Popen(..., creationflags=subprocess.CREATE_NO_WINDOW)`（防弹空白控制台窗），stdout/stderr 重定向到服务地盘 logs/
- 冷却防风暴：state json 记录 last_restart_at，10 分钟内不重复拉起（升级版带 PID 存活追踪）
- 端口检测异常 → 视为存活（检测不了别乱动，避免误杀/误拉起）
- CLI 参数：`--status` 只查不动作 / `--force` 跳冷却（调试用）

⚠️ **PowerShell 嵌入式子进程必须走 .ps1 文件**（2026-08-20 实测）：从 Python 调 `subprocess.run(["powershell", "-Command", f"Get-CimInstance ..."])` 时，命令字符串里的 `$env`、`$_`、单/双引号经 f-string 拼接 + subprocess 数组展开后，bash 不参与也会被 Python 字符串处理吃掉部分引号——看似工作但 WMI 输出字段解析失败，结果 `pid = None` → watchdog 误报"进程不存在"。**修法**：write_file 把 powershell 脚本写到 .ps1（带 UTF-8 BOM），再 `subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_path], ...)` 调用。详见 `windows-shell` "复杂逻辑一律写 .ps1 文件执行"节。

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
- **被启动进程是 Hermes 桌面 terminal 的孙子进程，桌面关掉服务即亡**（2026-08-20 DSH 解耦验证实测）：用 Hermes 桌面 terminal 工具后台启的 node 进程（PID 15916），父进程链是 `bash → python.exe (Hermes terminal) → node.exe (DSH)`——Hermes 桌面关掉 → python 父进程被杀 → node 子进程成孤儿被杀。**唯一可靠的常驻路径**：计划任务（schtasks）拉起，让祖先变成 `svchost.exe` 而非桌面进程。本机 Hermes `DSH_Watchdog` 计划任务已配置
- **TCP-only 健康检查三盲区**：端口被抢 / boot 失败但 listen / 半开进程——一律判健康 → 永远不复活。修法见上文"脚本要点"
- **冷却反模式**：双崩集群下 10 分钟盲等。修法见上文"脚本要点"
- **PowerShell 嵌入式子进程必走 .ps1**：详见上文 + `windows-shell` 技能
- taskkill 报 Access denied → 回落 `powershell -Command "Stop-Process -Id PID -Force"`
- 服务经 pnpm 启动有 ~30s 依赖解析+供应链检查 → watchdog 直接调实际入口（如 `node --import tsx/esm apps/cli/src/bin.ts web --port 8080`）秒起
- 默认端口起不来先查 Hyper-V/WSL 排除段（3001-3100 常见被占）：`netsh interface ipv4 show excludedportrange`

## 参考资料
- `references/dsh-case.md` — DeepSeek Harness 常驻实例全记录（2026-08-14 部署）
