---
name: hermes-remote-gateway
description: "Use when 远程网关/异地连 Hermes——另一台 Hermes 远程接入（serve/Tailscale）。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hermes, remote, gateway, serve, tailscale, dashboard-auth]
---

# Hermes 远程网关（远程接入）

场景：另一台电脑的 Hermes 桌面版**直接使用本机 Hermes**——界面显示在 B 机，agent 工具/终端/文件操作全部在 A 机执行。这是官方远程网关模式（桌面版 "Connect to existing Hermes"），不是聊天接入（那是 messaging platform 的事），是 Hermes 实例互联。

## 核心机制

- A 机跑 headless `hermes serve`（JSON-RPC/WebSocket 后端，默认端口 9119）
- B 机桌面版首次启动选 **Connect to existing Hermes** → 输入 `http://<A机IP>:9119` + 用户名/密码 → 探测 token/OAuth 后保存连接（后续启动免配）
- 远程模式下 gateway host 是执行边界（apps/desktop/README.md 原文）：B 机看到的会话/记忆/技能全是 A 机的
- 桌面版自带 serve（`--host 127.0.0.1 --port 0` 随机端口）与额外起的对外 serve 可并存，互不影响

### 为什么是桌面版远程网关（其他互联机制定位，调研结论）

| 机制 | 是什么 | 为什么不用它做"B 用 A 的 Hermes" |
|---|---|---|
| 桌面版 **Connect to existing Hermes** | B 机 UI = A 机完整 agent（工具/终端/文件全跑 A） | ✅ 唯一正解 |
| `hermes mcp serve` | stdio-only MCP server，暴露 10 个渠道桥工具（会话/消息），**原生不支持跨机器**（跨机器需另起 HTTP 适配器） | 只借 A 的消息渠道，不是通用执行 |
| API Server adapter（gateway 平台） | OpenAI 兼容端点，B 机配 `model.base_url` 指向 A | B 只是借 A 的模型/凭据后端，A 的 agent 本体不参与 |
| `terminal.backend: ssh` | B 的 Hermes 把终端/文件操作跑在 A 机 | 借的是 A 的机器环境，B 的 agent 能力（技能/记忆）还在 B；且 A 需装 OpenSSH Server |

## A 机配置步骤

1. **先配鉴权**：2026-06 安全加固后，非回环绑定（0.0.0.0 / 局域网 IP / Tailscale IP）**强制要求 auth provider**（OAuth 或内置密码 provider）；`--insecure` 已失效（只打警告不绕过）。loopback 绑定免鉴权。
   - 密码 provider：config.yaml `dashboard.basic_auth.username` + `password_hash`（scrypt，不存明文）
   - 生成哈希（用 hermes 自带 venv）：
     ```bash
     cd ~/AppData/Local/hermes/hermes-agent && venv/Scripts/python.exe -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('密码'))"
     ```
   - 写入配置——**agent 不能直接 patch config.yaml**（安全保护报 "Refusing to write to Hermes config file"），必须用 CLI：
     ```bash
     hermes config set dashboard.basic_auth.username hermes
     hermes config set 'dashboard.basic_auth.password_hash' 'scrypt$16384$8$1$...'
     ```
     ⚠️ scrypt 哈希含 `$`，bash 里必须单引号包住，否则被展开
   - 也可用环境变量覆盖（env 非空时优先）：`HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `_PASSWORD_HASH` / `_PASSWORD` / `_SECRET` / `_TTL_SECONDS`

2. **启动对外服务**：
   ```bash
   hermes serve --host 0.0.0.0 --port 9119
   ```

3. **防火墙**：Windows 放行 hermes.exe 入站（默认已有规则）或 9119 端口。

4. **开机自启**（可选）：计划任务**直接执行 `pythonw.exe`** + 参数 + 起始于（WorkingDirectory）。**不要包 `cmd /c` 壳、不要用 `python.exe`**——两者都会弹黑窗口且常驻（2026-08-07 实测：cmd /c 壳登录自启即弹「选择 C:\WINDOWS\system32\cmd.EXE」窗口，serve 长驻进程让窗口永不消失）。schtasks /create 无 WorkingDirectory 参数，用 PowerShell 建：
   ```powershell
   $action = New-ScheduledTaskAction -Execute "C:\Users\<用户>\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe" -Argument "-m hermes_cli.main serve --host 0.0.0.0 --port 9119" -WorkingDirectory "C:\Users\<用户>\AppData\Local\hermes\hermes-agent"
   Register-ScheduledTask -TaskName "HermesRemoteServe" -Action $action -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Principal (New-ScheduledTaskPrincipal -UserId "<用户>" -LogonType Interactive -RunLevel Highest) -Force
   ```
   - RunLevel **必须 Highest**（serve 以管理员运行；窗口守卫也要同级才能操作它的窗口，见下）
   - 验证：`Start-ScheduledTask -TaskName HermesRemoteServe` → sleep 10 → `netstat -an | grep ":9119.*LISTENING"`；失败查任务状态/Last Run Result
   - 已跑着的 serve 要换启动方式：杀旧进程树（cmd 壳 + pythonw + 其子进程）→ Start-ScheduledTask 重拉 → 端口恢复即成功

#### ⚠️ 弹黑窗口三层根因链（2026-08-07 实测，完整排障记录见 references/windows-console-popup-and-uipi.md）

1. **cmd /c 壳窗口**：cmd 是控制台程序，登录自启即显示窗口，且因 serve 是长驻进程、cmd 等它退出，窗口常驻 → 任务动作直接 pythonw.exe 解决
2. **pythonw 内部 AllocConsole 自建窗口**：serve 的 pythonw 进程内部某 C 扩展/launcher 调 AllocConsole，自建 conhost 黑窗口（标题「选择 <pythonw.exe 完整路径>」、类名 ConsoleWindowClass、内容 = serve 的 stdout）——**启动 flags 挡不住进程内部自建窗口**，只能用守卫脚本轮询隐藏
3. **UIPI 权限隔离（守卫失效根因）**：serve 以 Highest（高完整性）运行，其窗口属高完整性进程；若窗口守卫以 Limited（普通）权限运行，`GetWindowText`/`ShowWindow` 被 UIPI 拦截——守卫枚举得到窗口但**读不到标题**（匹配不上标记），隐藏无效。**守卫任务 RunLevel 必须 = Highest**（实测：Limited 守卫只隐藏了它自己的窗口，serve 窗口纹丝不动；改 Highest 后立即可隐藏）
- **治理**：本机 `scripts/hide_hindsight_window.py` 守卫（每 2 秒轮询隐藏标题含 `hermes-agent\venv\Scripts\pythonw.exe` 的可见窗口，ShowWindow SW_HIDE），计划任务 `Hermes-HideHindsightWindow` 登录时触发；Hindsight daemon 与 serve 共用（同 pythonw 路径，一个守卫全盖）
- **诊断要点**：`Get-Process | Where {$_.MainWindowTitle -ne ''}` 定位可见窗口归属进程；`Get-CimInstance Win32_Process` 查命令行/父进程/SessionId；确认守卫「是否真在干活」用决定性测试——脚本 SW_SHOW 故意显示目标窗口 → 等一个轮询周期 → 查是否被重新隐藏（是=守卫正常，否=守卫有权限/枚举问题）

## 验证鉴权（实测流程）

- **`/api/health` 不鉴权**（永远 200）——不能用它验证 auth 是否生效
- 登录换 session cookie（JSON 必须带 `provider` 字段，缺了报 422）：
  ```bash
  curl -c cookies.txt -X POST http://127.0.0.1:9119/auth/password-login \
    -H "Content-Type: application/json" \
    -d '{"provider":"basic","username":"hermes","password":"密码","next":""}'   # → 200
  ```
- 受保护端点验证：`curl -b cookies.txt "http://127.0.0.1:9119/api/fs/list?path=C:/Users/HMSJ"` → 200（带 cookie）；无 cookie → 401
- **HTTP Basic auth 头（curl -u）不适用**——Hermes 用登录端点换 session cookie，不是 Basic auth

## 跨网络（异地）连接

推荐 **Tailscale**：免费、WireGuard 加密、自动 NAT 穿透，无公网服务器时的最优解（Hermes 官方文档也推荐 "bind to 127.0.0.1 and reach it over an SSH tunnel / Tailscale"）。

- 安装：`winget install --id Tailscale.Tailscale --accept-source-agreements --accept-package-agreements --silent`
- 登录两条路：
  - 托盘图标 → Sign in（GUI 在跑时最顺）
  - 或 `tailscale up` 打印一次性登录 URL（10 分钟窗口），用户复制到自己浏览器打开（浏览器走 Clash 代理）
- 登录后 `tailscale ip -4` 拿 A 机 Tailscale IP（100.x），B 机连 `http://<100.x>:9119`
- B 机同样装 Tailscale 登录同一账号，才能进同一 tailnet

### Tailscale 坑（实测）

- **后台进程 stdout 缓冲**：`tailscale up` 放 background 时登录 URL 迟迟不出现——别干等，另开终端跑 `tailscale status`（会打印 "Log in at: ..."），或轮询 process log
- **TUN 驱动失败**：服务日志报 `Failed to setup adapter (problem code: 0x1F, ntstatus: 0xC00002F0): 系统找不到指定的文件` 且无限循环重试 → 是驱动注册后**需要重启电脑**（0xC00002F0 与系统待重启状态相关）。重启后服务自动恢复；`tailscale up` 报 "timeout waiting for Tailscale service to enter a Running state" 时先 `Restart-Service Tailscale` 再重试
- `tailscale up` 等待认证期间前台 `tailscale status` 可能超时挂起——别误判为进程冲突，杀掉多余 tailscaled 前先确认进程树（主进程 + /subproc 子进程是正常的）
- 国内网络：tailscaled 不走系统代理，控制平面连接可能慢；日志在 `/c/ProgramData/Tailscale/Logs/tailscale-service-*.txt`

### 替代方案对比（无公网服务器时 Tailscale 最优）

| 方案 | 前提 | 代价 |
|---|---|---|
| Tailscale | 无 | 登录需访问官网（走代理） |
| ZeroTier | 无 | 中继质量/控制台国内更差 |
| cloudflared | 需域名+CF 账号 | 国内到 CF 边缘节点慢 |
| frp 反向代理 | 必须有公网 IP 服务器 | 没有就不可行 |
| 路由器端口映射 | 公网 IPv4 | 国内家宽 CGNAT 基本无公网 IP |
| 花生壳等商业穿透 | 实名 | 免费版限速限流 |

## B 机步骤

1. 装 Hermes 桌面版（prebuilt installer 或源码构建）
2. 首次启动选 **Connect to existing Hermes**
3. 输入 `http://<A机 Tailscale/局域网 IP>:9119` + 用户名/密码
4. 连接后一切操作跑在 A 机

### B 机连上后"页面不一致"是正常的（实测结论）

用户常见疑问：B 机连上后置顶会话/会话排序/侧栏折叠和 A 机不一样。**这是设计如此，不是连错了**：

- 置顶会话、会话排序、侧栏折叠、右栏 tab 等 UI 状态是**每台机器本地存储**（桌面 app `src/store/layout.ts` 的 `persistentAtom`，如 `$pinnedSessionIds`），不随远程网关走。B 机全新安装 → 置顶为空、排序为默认
- 历史会话**内容**来自 A 机 `state.db`，两边一致
- 若历史会话本身少了（不只是置顶/排序），检查 B 机侧栏的 **Project/工作区选择**和筛选器是否与 A 机一致——Project 是 workspace 抽象，停在不同 Project 会看到不同会话集

### 发配置提示词给 B 机

桌面 app 渲染怪癖（实测 2026-08-07）：````text```` 语言标记的长代码块不渲染成代码块样式（显示为普通文本、无深色底/边框）——发长代码块用 `python` 或 `markdown` 标记代替即可（同内容同长度实测：text 不渲染、python 正常）。给 B 机的自包含配置提示词要包含：Tailscale 账号、A 机地址、用户名/密码、全部踩坑预埋（驱动重启、登录代理、GUI 最后一步）。

## 远程连接验证（B 机连上后，A 机侧确认）

```bash
# 1. 活跃远程连接：对端应为 100.x（Tailscale 网段），有 ESTABLISHED
netstat -an | grep ":9119" | grep ESTABLISHED

# 2. tailnet 双设备在线 + direct 直连（不是 DERP 中继）
"/c/Program Files/Tailscale/tailscale.exe" status
#   期望看到 B 机设备 "active; direct <公网IP>:<port>, tx ... rx ..."

# 3. 执行边界确认（agent 实际跑在哪台机器）
hostname    # 应为 A 机主机名——无论用户从哪台设备看界面，agent 都跑在 A 机
```

传输量（tx/rx）持续增长 = 会话确实在走远程通道。

## 安全须知

- 密码鉴权只挡 dashboard 访问；传输是明文 HTTP——**跨公网必须套加密隧道**（Tailscale / SSH / HTTPS 反代），同局域网可信环境才可裸连
- 绑 0.0.0.0 暴露所有网络接口；若路由器有公网端口映射会直接暴露公网，务必确认没有
- 保守替代：serve 绑 127.0.0.1 + SSH 隧道（需 A 机装 OpenSSH Server，Windows 可选功能默认未装，`Get-WindowsCapability -Online -Name OpenSSH.Server*` 查）
