# `dsh --profile headless` 无头运行器

DSH 官方提供的一次性任务运行器，是把 agent 接进任何自动化管道的入口。

## 它做什么

`@deepseek-ai/dsh-headless`（"The dsh one-shot bundle"）—— 直接叠在 `dsh-base` 之上，提供编码 persona 与工具模式、关闭 HMR、挂载 Code Mode worker，并插入 `headless-runner` 插件。**不挂载任何 Host、HTTP server、Web runtime 或浏览器插件，不监听端口。**

行为：
1. 创建一个全新的**持久化** Agent
2. 把任务作为普通用户消息提交
3. 等待完全停稳
4. 把该区间内**最后一条非空 assistant 文本**写到 stdout
5. 成功退 0，失败退 1（code 与 message 写 stderr）

只提交一个任务，没有交互式后续输入的 surface。

## 建 profile

```powershell
$env:DSH_HOME = 'C:\Users\HMSJ\.dsh'
dsh plugin --profile headless --help          # 首次运行即初始化该 profile
```

初始化会生成 `profiles\headless\package.json`，其中 bundles 已经是正确的：

```json
{
  "name": "dsh-profile-headless",
  "private": true,
  "dependencies": {},
  "dsh": { "profile": { "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless"] } }
}
```

**不要再 `pnpm add @deepseek-ai/dsh-headless`**：公网 npm 上该包不完整（会 404 在 `@deepseek-ai/dsh-code-runtime-worker`）。本机 `.dsh\profiles\node_modules\@deepseek-ai\` 下已有全套包，profile 经父级 node_modules 即可解析。

## 调用

```powershell
dsh --profile headless "<任务文本>"
```

任务文本就是位置参数，多个词用空格连接。

### 用哪个 dsh 可执行文件

**不要依赖 PATH。** Desktop 只把 `host-commands` 目录注入自己派生的进程，因此：

| 环境 | PATH 解析结果 | 结果 |
|---|---|---|
| 交互式 shell（Desktop 的子进程） | `...\host-commands\desktop\generations\<hash>\bin\dsh.cmd` | ✅ |
| 裸计划任务环境 | `~\.local\bin\dsh.bat` = `hermes -p dsh %*` | ❌ `Profile 'dsh' does not exist` |

正确做法是 glob 取最新一代：

```powershell
$genRoot = "$env:APPDATA\DSH Desktop Beta\host-commands\desktop\generations"
$dsh = Get-ChildItem $genRoot -Directory |
  Sort-Object LastWriteTime -Descending |
  ForEach-Object { Join-Path $_.FullName 'bin\dsh.cmd' } |
  Where-Object { Test-Path $_ } | Select-Object -First 1
```

路径含 build hash，**每次 DSH 升级都会变**，所以必须每次运行重新解析，不能写死。

## 能力边界

| 项 | 说明 |
|---|---|
| **模型选择** | ❌ 无 `--model` / `--provider` 参数。模型取全局 `agent-default-model`（`.dsh\settings.yaml`）。要换模型需另建 profile 并在其 `cordis.patch.yml` 里覆盖该插件配置 |
| **工具** | 继承 `dsh-base`：文件读写、bash/pwsh、搜索等。**没有**飞书相关工具，投递要靠外部的 lark-cli |
| **stdout** | 只有最终 assistant 文本；dsh 会在 **stderr** 打一条 `fs.Stats constructor is deprecated` 的 `DEP0180` 警告 → **不要用 `2>&1` 合并流** |
| **提示词长度** | 命令行传参有实际长度上限（实测 ~2500 字带 XML 会静默截断，~1400 字正常）。**长提示词一律让 agent 自己读文件** |
| **会话** | 每次运行新建持久化 Agent 与 Session，不会污染已有会话 |

## 运行器侧的最小骨架

```powershell
$instr = "请用文件读取工具读取 UTF-8 文本文件 $TaskFile ，并严格按照其中的任务执行。你的最终回复就是交付内容本身。"
$outFile = Join-Path $env:TEMP ("_o_" + [guid]::NewGuid() + ".txt")
$errFile = Join-Path $env:TEMP ("_e_" + [guid]::NewGuid() + ".txt")
$prev = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
try   { & $dsh --profile headless $instr 1>$outFile 2>$errFile; $code = $LASTEXITCODE }
finally { $ErrorActionPreference = $prev }
$output = (Get-Content $outFile -Raw -Encoding UTF8).Trim()
```

## 与 DSH 内建调度器的区别

`dsh-schedule` 的定位是 *"Agent-scoped durable after, at, and fixed-rate reminders **over the session event log**"* —— **会话内提醒**，不是系统级 cron。跨会话、跨重启的定时必须交给操作系统调度器（Windows 计划任务）。

同理，`dsh-jobs` / `dsh-tool-jobs` 是**进程内后台作业注册表**（job_output/job_list/job_kill），也承担不了 cron 职责。
