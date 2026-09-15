# 从 Hermes cron 迁移到 DSH

在真正停掉 Hermes 之前，逐项把能力搬过来并验证。**Hermes 的进程往往还在跑**——拆了自启不等于停掉了它。

## 第 0 步：先搞清 Hermes 到底还在做什么

```powershell
# 进程（注意：权限受限时 CommandLine/ExecutablePath 为空，按命令行匹配会漏判）
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'hermes' -or $_.ExecutablePath -match 'hermes' }
```

**教训**：只按 `CommandLine -match 'hermes'` 扫描会把 `python.exe` 的 Hermes 守护进程全部漏掉（其 `CommandLine` 因权限为空），从而误判「Hermes 没在运行」。可靠性更高的判据是 Hermes 自己写的 PID 记录：

```
<HERMES_HOME>\gateway.pid          kind / argv / hermes_home
<HERMES_HOME>\gateway_state.json   gateway_state / platforms[].state
<HERMES_HOME>\cron\ticker_heartbeat  心跳文件时间戳（秒级，最能说明"还活着"）
```

## 第 1 步：三个带 "hermes" 的路径，身份完全不同

**绝不可一刀切。**

| 路径 | 真实身份 | 处置 |
|---|---|---|
| `%LOCALAPPDATA%\hermes` | **Hermes 程序本体 + 全部数据** | 迁移目标 |
| `~\Documents\Hermes` | **用户的工作仓库**（git repo、Projects、memories、kanban、scripts/ 下几十个在用的脚本） | **绝不能删**；它在 PATH 上，PATH 项也要留 |
| `~\.hermes` | 遗留安装产物 + 某些常驻服务的 profile（如 CDP 浏览器 user-data-dir） | **不能删** |

判定方法：看目录内容与启动项引用，不要凭名字。

## 第 2 步：盘点隐蔽的「退役即断」依赖

除自启/任务/PATH/环境变量外，最容易漏的是这些：

| 依赖 | 表现 | 处理 |
|---|---|---|
| `HERMES_HOME` 环境变量 | lark-cli 一旦看到它就切到「Hermes 外部凭据提供者」，只认 Hermes 的 `.env`，**任何别的 app profile 都会 `invalid_client`** | 调用 lark-cli 时清掉（子进程内 `set "HERMES_HOME="`），或彻底移除该变量 |
| `~\.local\bin\dsh.bat` | 内容就是 `hermes -p dsh %*`，是个 Hermes 壳 | 改用 Desktop 的 `generations\*\bin\dsh.cmd` |
| PATH 里的 `<HERMES_HOME>\node`、`\bin` | lark-cli 等工具从这里解析到旧版本 | 摘除这两项，保留工作仓库的 scripts 目录 |
| `hermes_run.py` 包装器 | 提示词里要求用它加载 `.env` 凭据 | 迁移提示词时剥掉；先单独测脚本能否独立运行 |
| 计划任务指向 `<HERMES_HOME>\...` | 任务删除后 XML 要留档 | `Export-ScheduledTask` 存 XML 再删 |

## 第 3 步：取出 cron 定义

```powershell
# 结构：{ jobs: [...], updated_at }
$j = Get-Content "<HERMES_HOME>\cron\jobs.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$j.jobs | Select-Object name, schedule_display, deliver, no_agent, script, enabled
```

关键字段：`prompt`（提示词）、`schedule.expr`（cron 表达式）、`deliver`（投递目标）、`script`（辅助脚本）、`enabled_toolsets`、`skills`、`provider_snapshot`/`model_snapshot`。

**逐项导出到文件**，逐条迁移，不要批量重写。

## 第 4 步：迁移期避免双投

新旧两条链路同时间跑会各投一次。**每迁完一项就停掉 Hermes 侧对应的那条**：

```powershell
$env:HERMES_HOME = '<HERMES_HOME>'
hermes cron list
hermes cron pause <job_id>        # 可逆，保留定义
```

## 第 5 步：改造提示词

迁移不是复制粘贴。要处理：

1. **剥掉 Hermes 专属的环境加载段**（`hermes_run.py` 之类），并先验证脚本能独立运行
2. **改成文件读取模式**（长提示词命令行传参会静默截断）
3. **补硬约束**：无头运行没有追问机会，风格/篇幅/禁忌都要写在提示词里
4. **加交付约定**：「你的最终回复就是交付内容本身，不要工具调用、不要写文件」；需要静默时约定哨兵词（如 `SKIP`）
5. **核对投递目标**：换了 bot 之后，群 chat_id 不变（同一个群），但**私聊 DM 的 chat_id 会变**（open_id/chat_id 是 app 维度的），必须重新确定

## 第 6 步：逐项验证，然后才停 Hermes

验收阶梯（缺一不可）：

1. 手动运行运行器 → `RUN exit=0` 且 stdout 非空
2. **从裸环境验证计划任务**（`Start-ScheduledTask`），而不是只在交互式 shell 里跑——PATH 与凭据差异恰恰只在裸环境暴露
3. 确认飞书真的收到（看日志 `DELIVER OK`，并检查响应体没有降级标记）
4. 停掉 Hermes 对应 job
5. 全部项目通过后再停 Hermes 网关

## Hermes 的评论回复为什么不能照搬

Hermes 用自己的 Feishu app 建了独立的 WS 长连接订阅评论事件。在 DSH 侧照做会撞车：

- **同一 app 的多个长连接会被飞书随机分流事件** —— 再挂一个客户端会抢走现有 bot 的一半事件，直接搞坏它
- 现有 bot（`dsh-lark-bot`）只暴露 `ctx.larkBridge` 的 `status`/`stop`，**没有注册自定义事件处理器的接口**
- 它是 AGPL 第三方 npm 包，patch 会在升级时被覆盖

→ 改用**轮询**：零控制台改动、零冲突、不动第三方包。代价是分钟级延迟与需维护监视列表。
