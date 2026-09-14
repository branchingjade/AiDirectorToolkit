# DSH/Hermes 桌面解耦实战笔记（2026-08-20）

## 场景
Hermes 桌面关掉不能拖累 DSH web 服务；DSH 崩也不能拖累 Hermes 桌面。
两个独立进程的存活路径完全不交叉。

## 已验证的解耦机制
`Documents/Hermes/scripts/dsh_watchdog.py`（计划任务 DSH_Watchdog 每 5 分钟触发）：
- 用 `subprocess.Popen + DETACHED_PROCESS` 拉 DSH node 进程
- 父 python 进程退出后，node 进程的 PPID 漂走 = Win32 孤儿
- 验证：`Get-CimInstance Win32_Process -Filter "ProcessId=<PID>"` 看 PPID 查不到 = 解耦成功
- ⚠️ 别用 Linux 思维找 svchost 父节点——Windows 孤儿进程的 PPID 停在已死的父 PID 上

## 解耦失败的常见模式（避免）
- `terminal background=true` 起的 node → bash → python → node 三层链，Hermes 桌面进程链
- 任何从 Hermes 桌面 terminal/IDE 起的服务，父进程都是桌面进程链
- **杀 bash 不一定杀 DSH**：bash 被信号干掉时，子进程若已 detach 会继续跑；验证端口存活用 `curl 127.0.0.1:8080` 看 HTTP 200，不要相信 `tasklist | grep node`（可能看到的是孤儿）

## state.json 路径分裂（历史变迁残留）
DSH watchdog 现状有两份 state 文件：

| 写者 | state 路径 |
|---|---|
| `Documents/Hermes/scripts/dsh_watchdog.py`（计划任务 DSH_Watchdog 指向）| `HERMES_ROOT/.hermes/dsh_watchdog_state.json`（无 reason 字段）|
| 外部一次性写入（grep 全文件系统找写者失败——DSH 源码、~/.dsh/、Hermes 工作区、Hermes 用户目录、Hermes-web-tools、cordis bundle 都搜不到 `preview-url-restart` 字符串；最可能是历史残留被人工追加）| `Projects/deepseek-harness/dsh_watchdog_state.json`（带 reason 字段）|

**当前实现的取舍**：DSH watchdog 用 `.hermes/` 路径（HERMES 依赖弱——只读绝对路径、不引 Hermes 模块）。**洁癖整改路径**：state.json + log 落 `Projects/deepseek-harness/.watchdog/`（项目地盘）。

**注**：`references/dsh-case.md` 表格里的「状态/冷却：`Projects/deepseek-harness/dsh_watchdog_state.json`」是 **8-18 清理前**旧 watchdog 的产物（脚本已删）；当前 watchdog 写 `.hermes/dsh_watchdog_state.json`。两份 state 文件并存是历史变迁残留。

## 冷却逻辑反例（2026-08-20 实测病态信号）
DSH watchdog 现状：拉起后 10 分钟内再死不复活。state 日志里能看到 14:14→14:24、03:24→03:34 这种「恰好相隔 10 分钟」的复活对——双崩集群里第二次复活被推迟整整冷却时长。

**修复方向**：拉起后只要端口存活就**不重置**冷却（让 10 分钟是上次拉起后整个窗口的禁入期）。