# Gateway 自愈 Watchdog 设计方案（2026-08-07 深推）

背景：2026-08-07 会话中 gateway 两次宕机（10:56→14:18 停机 3.5h；14:39 又停一次），第二次由**查询类 CLI 命令触发**。本文件记录「gateway 挂了自动拉起 + 自动补消息」的完整架构论证，供落地实现时照做。

## 架构约束（为什么必须外置）

| 机制 | 归属 | gateway 挂了会怎样 |
|---|---|---|
| Hermes cron 调度器 | **gateway 进程内**（gateway/run.py 启动 scheduler） | 随 gateway 一起死——检测不到宕机 |
| Hermes webhook 平台（:8644） | **gateway 进程内**（`gateway.platforms.webhook`，是 gateway 的一个 adapter） | 随 gateway 一起死 |
| 出站 webhook（`hooks.outbound`） | 进程内，仅活态触发（on_session_end 等生命周期事件） | 进程死时无法触发 |
| 飞书群自定义机器人 webhook（`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`） | **飞书服务器，完全独立于 Hermes** | **不受影响，照常能推** |

**核心结论**：
1. 自愈机制**必须独立于 Hermes 进程存活** → Windows 计划任务（Scheduled Task）跑独立脚本。
2. 唯一能跨过「gateway 死亡」的信道 = **飞书群机器人 webhook**（直连飞书，零 Hermes 依赖）。Hermes 自身的 webhook 平台和出站 webhook 都推不了「我挂了」。

## 两层设计

```
┌─ 第1层：watchdog 脚本（独立于 Hermes，计划任务每 5 分钟）──┐
│  检测 gateway 存活 → 挂了就拉起 → 告警（飞书群机器人     │
│  webhook）→ 写停机标记文件                               │
└──────────────────────────────────────────────────────┘
┌─ 第2层：补消息 cron（gateway 恢复后自然运行，每 10 分钟）─┐
│  读停机标记文件 → 走 gateway-outage-message-recovery     │
│  流程拉消息补回复 → 清标记                               │
└──────────────────────────────────────────────────────┘
```

## 检测判据（组合投票，防误报）

| 信号 | 查法 | 判据 | 盲区 |
|---|---|---|---|
| 硬信号：进程存活 | `ps` 找 `pythonw.exe -m hermes_cli.main gateway run`（或 `Get-Process python*`） | 进程不存在 = 必拉 | 僵尸进程/双进程 |
| 软信号：日志新鲜度 | gateway.log mtime 距现在 | > 阈值（如 15 分钟）→ 疑似卡死 | 空闲时日志可能不更新 → 误报 |

**关键设计点**：日志新鲜度阈值必须 > housekeeping 间隔（gateway 有 `housekeeping interval=60s`，但空闲时不一定写日志）。**不能**用「日志 5 分钟没更新 = 死了」做主判据，要进程信号为主、日志新鲜度为辅。

## 拉起动作（防风暴）

```
if 判定宕机:
    if 标记文件存在且 30 分钟内拉过 → 跳过（防风暴，防 CLI 反复横跳）
    执行 Hermes_Gateway.cmd 拉起（或 hermes gateway start）
    写标记文件（时间戳）
    POST 飞书群机器人 webhook 告警
```

**⚠️ 必须防 CLI 横跳**：`hermes gateway status` / `hermes cron list` 在 update 中断残留时会连带停 gateway——watchdog 要能扛「起来又被命令弄停」的循环（30 分钟冷却覆盖）。

## 停机标记文件

`~/AppData/Local/hermes/state/gateway_outage.json`，结构：
```json
{"outage_start": "2026-08-07T10:56:00+08:00", "outage_end": "2026-08-07T14:18:00+08:00", "restarted_at": "..."}
```
第 2 层 cron 读完清空。

## 落地清单

- `gateway_watchdog.py`（独立脚本，~80 行，不依赖 Hermes 库——只用标准库 + urllib POST webhook）
- Windows 计划任务：每 5 分钟运行 watchdog（触发器 + 用户登录与否均可运行）
- 补消息 cron job：LLM 驱动，每 10 分钟，读标记文件 → 走 recovery 流程
- **前置条件**：飞书群自定义机器人 webhook URL（群设置 → 群机器人 → 添加自定义机器人）
