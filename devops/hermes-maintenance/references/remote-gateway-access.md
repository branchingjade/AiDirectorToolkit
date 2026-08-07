# Remote Gateway Access — 详细配置与源码定位

让另一台电脑（B）的 Hermes 桌面版远程连接本机（A）的 Hermes。实测于 2026-08，Hermes 桌面版 + Windows 10。

## 机制全景

```
B 机桌面版 ──HTTP/WebSocket──> A 机 hermes serve（headless JSON-RPC/WS 后端）
                                  │
                                  ├─ 工具/终端/文件操作 → 在 A 机执行（执行边界）
                                  ├─ 会话/记忆/技能 → A 机的 HERMES_HOME（state.db 等）
                                  └─ gateway 渠道（飞书等）→ A 机 gateway 进程
```

桌面版 README 原文：*"In remote mode the gateway host is the execution boundary: agent tools, terminal commands, and file operations run against the remote Hermes host, not the computer displaying the Desktop UI."*（`apps/desktop/README.md`）

## 相关进程架构（A 机现状）

| 进程 | 命令行 | 作用 |
|------|--------|------|
| `hermes serve --host 127.0.0.1 --port 0` | 桌面版自带 headless 后端 | 服务本机桌面 UI，随机端口 |
| `hermes gateway run` | gateway 服务 | 消息平台（飞书）连接 |

另起一个对外 serve（固定端口）与桌面版自带 serve 并存无冲突——都读写同一 state.db（SQLite WAL）。

## 鉴权机制（2026-06 加固后的真值表）

源码 `hermes_cli/web_server.py`：

- `should_require_auth(host)`（:472）——`host not in _LOOPBACK_HOST_VALUES` 即强制鉴权。**RFC1918/CGNAT/link-local 都算 PUBLIC**（注释原文：*"a hostile device on the same LAN is exactly the threat model the gate is designed for"*）
- `--insecure`（allow_public）**已失效**（:17465 附近 warning：*"--insecure no longer bypasses dashboard authentication. A non-loopback bind now ALWAYS requires an auth provider (OAuth or the bundled password provider). Configure one — or bind to 127.0.0.1 and reach it over an SSH tunnel / Tailscale."*）
- `_ws_client_is_allowed`（:14579）——loopback bind 只放行 loopback peer（`?token=` 是唯一鉴权）；非 loopback bind 放行任意 peer（Host/Origin guard 防 DNS-rebinding）
- 鉴权方案：loopback/`--insecure` 模式用 `?token=<_SESSION_TOKEN>`（`HERMES_DASHBOARD_SESSION_TOKEN` env 或自动生成的 token_urlsafe(32)）；gated 模式（auth_required=True）走 OAuth gate + single-use ticket

**结论：** 想免 OAuth 让 B 机连进来，两条路：
1. 配 basic_auth 密码插件 + 非回环绑定（局域网直连/Tailscale 直连）
2. 保持 loopback 绑定 + SSH 隧道 / Tailscale SSH（SSH 提供传输层认证加密，Hermes 侧不触发鉴权门）——但 Windows 默认没装 OpenSSH Server，需先启用

## basic_auth 密码插件完整配置

config.yaml（`dashboard.basic_auth`，默认值见 `hermes_cli/config_defaults.py` :1350）：

```yaml
dashboard:
  basic_auth:
    username: ""            # 留空 = 插件 no-op
    password_hash: ""       # scrypt$...（首选，不存明文）
    # password: ""          # 明文兜底，加载时内存哈希
    secret: ""              # token 签名 HMAC 密钥；留空 = 随机 per-process（重启后会话失效）
    session_ttl_seconds: 0  # 0 → 插件默认 12h
```

生成 password_hash：

```bash
cd ~/AppData/Local/hermes/hermes-agent
./venv/Scripts/python.exe -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"
```

env 覆盖（非空时优先）：`HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `_PASSWORD_HASH` / `_PASSWORD` / `_SECRET` / `_TTL_SECONDS`。

## serve 启动与验证

```bash
# 前台（验证用）
hermes serve --host 0.0.0.0 --port 9119

# 后台常驻（Windows 用后台进程或计划任务）
# 防火墙：放行 hermes.exe 入站（通常已有规则），或 netsh advfirewall firewall add rule name="Hermes 9119" dir=in action=allow protocol=TCP localport=9119
```

验证：
```bash
netstat -an | grep ":9119"          # LISTENING
curl -s http://127.0.0.1:9119/api/health   # 本机自检
# 局域网/Tailscale 端验证（B 机或另一终端）：
curl -s http://<A机IP>:9119/api/health
```

B 机桌面版连接：首次启动 → Connect to existing Hermes → `http://<A机IP>:9119` + 用户名/密码。探测通过后连接保存（加密存在桌面配置），后续启动自动重连。

## Tailscale 异地方案（实测 2026-08）

```bash
winget install --id Tailscale.Tailscale --accept-source-agreements --accept-package-agreements --silent
powershell -NoProfile -Command "Start-Service Tailscale"   # 服务可能启动慢，等几秒
"/c/Program Files/Tailscale/tailscale.exe" up             # 生成一次性登录 URL
```

坑（全部实测 2026-08-06）：
- **up 输出缓冲**：`tailscale up` 经管道/terminal background 跑时 stdout 全缓冲，process poll 拿不到 URL（等几十秒都没有）——改用**前台 `tailscale status`** 拿登录链接（输出 `Logged out. Log in at: https://login.tailscale.com/a/xxxx`），或让用户直接操作系统托盘 GUI（tailscale-ipn 进程在跑即有图标）点 Sign in
- **服务未就绪**：装完立即 up 报 `timeout waiting for Tailscale service to enter a Running state`（exit 1）——`Restart-Service Tailscale -Force` 后恢复 Running，再重跑 up
- **open_preview 打开登录页不可靠**（用户反馈"没打开"）：直接把文本 URL 给用户复制到自己浏览器打开
- 登录 URL **一次性**：up 超时/作废后重跑 up 生成新 URL
- **用户口头确认≠授权成功**：`tailscale up` 阻塞到授权完成才退出（授权成功前进程一直 running）；`tailscale status` 显示 `Logged out.` = 只登录了官网、没在设备授权页点 Connect——需重跑 up 拿新 URL 再授权
- Tailscale 登录需访问 login.tailscale.com（用户有 Clash Verge 代理时可过）
- serve 绑定建议 0.0.0.0（Tailscale IP 可能变）；传输走 Tailscale WireGuard 加密 + basic_auth 密码 = 双保险

## 常见问题

| 症状 | 原因 | 处理 |
|------|------|------|
| `--insecure --host 0.0.0.0` 连不上 | 2026-06 加固，--insecure 已失效 | 配 basic_auth 或 OAuth |
| B 机连接被拒 | A 机 serve 绑定 127.0.0.1 | 改绑 0.0.0.0 或局域网/Tailscale IP |
| 防火墙拦截 | Windows 防火墙无入站规则 | 放行 hermes.exe 或 9119 端口 |
| serve 端口占用 | 9119 被占 | 换端口（`--port 9120`） |
| 登录 URL 打不开/已过期 | 一次性 URL 超时 | 重跑 `tailscale up` 拿新 URL |
