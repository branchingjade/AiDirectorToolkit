---
name: dsh-feishu-jobs
description: "把定时/常驻任务跑在 DSH 上、并把结果以飞书富文本（交互卡片 / 评论富元素）投递出去。覆盖 dsh-headless 无头运行器、Windows 计划任务编排、lark-cli 投递、以及从 Hermes cron 迁移的完整流程与全部实测坑。Use when: 要做定时任务/日报推送/cron、要迁移 Hermes cron、要让 bot 回飞书评论、要发飞书卡片或富文本、dsh 无头运行报错、计划任务里 dsh 找不到或报 profile 不存在、飞书回复 @不到人、卡片显示请升级客户端。"
---

# DSH 定时任务与飞书富文本投递

DSH **没有系统级 cron**（`dsh-schedule` 只是会话内 after/at/fixed-rate 提醒）。所以定时能力的正确拼法是：

```
Windows 计划任务          ← 调度
  → wscript 隐藏窗口       ← 避免弹控制台
    → run-agent-job.ps1    ← 编排
      → dsh --profile headless "<指令>"   ← 执行；stdout = 最后一条 assistant 文本
        → lark-cli（水铅）投递飞书          ← 交付，交互式卡片
```

参考实现（可直接复用）：

```
C:\Users\HMSJ\Documents\DSH\hermes-migration-20260914\
├── bin\run-agent-job.ps1          任务运行器（无头运行 + 卡片投递）
├── bin\run-job-hidden.vbs         计划任务用的隐藏启动器
├── bin\poll-comments.ps1          飞书评论响应器（轮询式）
├── bin\poll-comments-hidden.vbs
├── tasks\<job-id>.txt             各任务提示词（ASCII 文件名）
├── tasks\_job-names.json          job id → 卡片展示名
├── comment\config.json            评论器配置（监视文档/人员/dryRun）
└── logs\                          运行日志
```

## 八个必须知道的坑

全部为实测踩过，每一条都写进了脚本注释。

| # | 坑 | 现象 | 解法 |
|---|---|---|---|
| 1 | **dsh 入口不能走 PATH** | 裸计划任务环境解析到 `~\.local\bin\dsh.bat`，那是 Hermes 的壳（`hermes -p dsh %*`），报 `Profile 'dsh' does not exist` | glob `%APPDATA%\DSH Desktop Beta\host-commands\desktop\generations\*\bin\dsh.cmd` 取最新一代；PATH 仅兜底 |
| 2 | **长提示词经命令行传参会静默截断** | ~2500 字带 XML 的提示词送达时正文丢失，agent 回「没收到原文」；~1400 字正常 | 命令行只传一句「请读取 <路径> 并执行」，让 agent 自己读文件 |
| 3 | **JSON 内联传参被 PowerShell 吞引号** | `accepts 2 arg(s), received 9` / `--params invalid format` | `--data` **和** `--params` 都走 `@file` |
| 4 | **身份自动解析成 user** | 发消息报 `230027 access denied` | 显式 `--as bot` |
| 5 | **PS 5.1 默认按 ANSI 读文件** | 中文提示词变乱码，agent 答非所问 | `Get-Content -Raw -Encoding UTF8` |
| 6 | **原生命令 stderr 触发 Stop** | 一条无害 DeprecationWarning 就中断整个脚本 | stdout/stderr 分流到文件，或局部降级 `ErrorActionPreference` |
| 7 | **lark-cli 无 im 发消息命令** | `im.messages` 只有 delete/forward/patch/read_status/urgent | 走原始 API `POST /open-apis/im/v1/messages` |
| 8 | **卡片 schema 2.0 在部分租户不可用** | 返回 `ok:true` 但客户端降级成「请升级至最新版本客户端」，**表面成功实际看不到** | 用旧版 `config/header/elements` + `lark_md` |

> 约定：本机所有 `.ps1` / `.vbs` / `.cmd` **一律 ASCII-only**。cmd.exe 与 wscript 按 ANSI 读脚本，中文注释会把 `REM` 行冲垮。

## 新建一个任务

1. 写提示词到 `tasks\<job-id>.txt`（**ASCII 文件名**，中文走 `_job-names.json` 映射）
2. 补 `_job-names.json`：`"<job-id>": "中文展示名"`
3. 注册计划任务：

```powershell
$action = New-ScheduledTaskAction -Execute "wscript.exe" `
  -Argument "`"<...>\bin\run-job-hidden.vbs`" <job-id> `"<...>\tasks\<job-id>.txt`" <chat_id>"
$trigger = New-ScheduledTaskTrigger -Daily -At (Get-Date -Hour 8 -Minute 30 -Second 0)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
  -ExecutionTimeLimit (New-TimeSpan -Minutes 20) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "HMSJ" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName "DSH_Job_<Name>" -Action $action -Trigger $trigger `
  -Settings $settings -Principal $principal -Force
```

4. 实跑一次并看 `logs\<job-id>.log` 的 `RUN` / `DELIVER` 行

**`-StartWhenAvailable` 必开**：错过的时间点会被补跑，否则休眠/关机就永久丢一次。

## 飞书投递的两种形态

- **IM 投递 → 交互式卡片**：标题栏 + markdown 分节 + 分隔线。`lark_md` **不支持标题语法**，`## 标题` 会被运行器转成 `**粗体**` 的 `div`，分节用 `{tag:'hr'}`。
- **评论回复 → 富元素**：`text` / `mention_user` / `link` 三种扁平元素，裸 URL 自动转链接。

细节见：
- [`references/feishu-rich-text.md`](references/feishu-rich-text.md) — 评论富元素与卡片的**准确字段格式**（照直觉写会静默失败）
- [`references/headless-runner.md`](references/headless-runner.md) — `dsh --profile headless` 的搭建、能力边界与限制
- [`references/hermes-cron-migration.md`](references/hermes-cron-migration.md) — 从 Hermes cron 迁移的完整流程

## 评论响应器（常驻）

Hermes 的评论回复靠事件订阅；DSH 侧**不能**照做，原因见 references。采用**轮询**：

```
计划任务（每 2 分钟）→ poll-comments.ps1
  → 对监视文档列表跑 lark-cli drive +list-comments
    → 与状态文件比对 → 新评论交给 dsh headless 生成回复
      → lark-cli drive +add-reply 富元素回帖
```

四道安全阀，缺一不可：

| 机制 | 作用 |
|---|---|
| `dryRun` | 默认 true。只落盘「将要回什么」，不发帖。**对同事可见的回复必须先看样本再开闸** |
| 新鲜度闸门 | 只处理「最后一条回复晚于 `lastPollAt`」的线程，避免首次运行把历史评论全翻出来刷屏 |
| `handled` / `seen` 双记录 | 以 `reply_id` 为键。即使 self-id 识别失效，bot 也不可能回复自己形成死循环 |
| `maxPerRun` | 单次轮询上限 |

过滤规则：跳过 `is_whole`（整篇评论不接受回复）、`is_solved`、最后发言是 bot 的、不在 `allowedUsers` 的。

**bot 自身标识**：评论线程里 bot 的 `user_id` 是**该 app 维度下的 bot open_id**（不是 app_id）。

## 任务提示词的写法

- 结尾明确「**你的最终回复就是交付内容本身**，不要工具调用、不要结束语、不要写文件」
- 需要免打扰的场景：约定一个哨兵词（如 `SKIP`），运行器识别后跳过投递
- 提示词要自带硬约束（风格、篇幅、禁忌），无头运行没有追问的机会
- 长任务给足 `-ExecutionTimeLimit`；实测日报类 60-180 秒

## 相关技能

- `lark-doc` / `lark-drive` / `lark-im` — 飞书 API 的命令面与 skill 前置要求
- `hermes-workspace-conventions` — 工作区目录约定（本技能的参考实现在 `Documents\DSH\` 下，不在 Hermes 工作区）
