---
name: cron-ops
description: "cron 投递失败/调度机制疑问/编辑已投递消息时用。Hermes cron 调度机制与投递运维。"
---

# Cron 调度与投递运维

Hermes cron 的调度机制、投递排障、已发消息编辑。覆盖 cron-monitor（job 创建与格式）之外的**机制与运维层**。

## 调度机制（2026-08-07 源码查证）

- gateway 进程内每 60s 一次 tick 检查到期 job；到期 job 用 **ThreadPoolExecutor 并行**执行（日志 `Running N job(s) in parallel (max_workers=...)`）
- 并行度优先级：环境变量 `HERMES_CRON_MAX_PARALLEL` > config.yaml `cron.max_parallel_jobs` > 默认**无限制**
- **唯一串行例外**：带 `workdir` 的 job 走单线程队列（workdir 改进程级 `TERMINAL_CWD`，并行会互相污染）——同刻到点的多个无 workdir job 完全并行，不用担心拥堵
- 防重三件套（at-most-once）：文件锁（同时只一个 tick）→ next_run_at 提前推进 → `_running_job_ids` 在飞判重（同 job 还在跑不重复触发）
- **状态诊断签名（2026-08-10 实测）**：`last_run_at` 停在旧日期 + `next_run_at` 已跳过本次计划时间（每日任务 last=昨天、next=明天）= job **启动后被中断**（gateway 崩溃/API 超时被杀），不是没触发——at-most-once 在 job 启动时提前推进 next_run，last_run 只在完成时写回。判断「没跑」还是「跑一半死了」必须先看 agent.log 有没有 `cron.scheduler: Running job '<名>'` 行
- 手动 `cronjob run` 在当前会话进程直接跑 `run_one_job`（不走 gateway tick 并发池）——**改了源码/装了补丁后手动 run 不生效**，定时触发才走 gateway 进程（需重启 gateway 加载新模块）

## 健康检查（2026-08-10 伏妖记审读 cron 实测）

**只看 `last_status=ok` 会被骗**——job 可能实际启动后中断（API 超时/gateway 崩溃），状态没写回 jobs.json 但 last_status 还是 ok。完整检查链：

1. **jobs.json 三字段交叉**：`last_run_at`（上次完成）+ `next_run_at`（下次）——last 停 N 天前但 next 已跳过中间几次 = 中间那次没跑成但调度器已推进，需查日志
2. **agent.log 是真实执行证据**：`grep -E "2026-08-XX 09:" logs/agent.log | grep cron.scheduler`——看到 `Running job '<名>'` 才是真启动；再 grep 该 job 的 session id（`cron_<jobid>_<timestamp>`）看是否有 `Turn ended` + `delivered`，没有 = 中断无投递
3. **gateway 崩溃会吞掉运行中的 job**：`logs/gateway.log` 查 `exited UNCLEANLY` / `SIGKILL / OOM`；`gateway-exit-diag.log` 的 `previous_unclean_exit` 记录崩溃点；崩溃时正在跑的 cron job 直接中断（API 调用刚发出就被杀），last_run 不更新、无投递——但 at-most-once 已推进 next_run_at，**下次定时自动补跑，无需手动干预**
4. **手动 run 更新基线/状态的连锁**：同一天先手动 `cronjob run` 再定时 run，定时那次对比的是新基线 → 判定「无更新」是**正常时序不是故障**（2026-08-10 实测：21:37 手动审读更新基线 → 22:05 定时判定无更新，行为正确）。给 cron 加新 prompt/配置后，用户默认「等触发就行」不手动验证——手动 run 会产生群推送噪音+基线连锁
5. **重任务 job（备份/上传/打包）禁止手动 run 验证（2026-08-11 实测）**：备份类 job 手动 `cronjob run` 会与定时触发**双跑**——实测同一备份脚本被 cron 手动触发 + 直接跑各拉起一份，两份同时打包 2.7GB、抢同一个百度网盘上传，互相拖慢（用户问「这么慢吗」）。且 agent 对超时命令会空转多轮 API 解读输出（实测 12+ 轮、26 分钟还在查进程）。**正确验证法**：①看脚本自身日志是否出现「开始执行/打包完成」记录（证明路径修好、能启动）即可；②或直接跑一次脚本看能否启动，跑通就停；③绝不手动 run 等它完成。判断「修复生效」的证据 = 从「can't open file 找不到文件」变成「正常执行但耗时长」——性质完全不同

## 节假日静默模式（script 参数 + 三态判定，2026-08-11 伏妖记审读 cron 实测）

需要「工作日才跑、法定节假日和周末静默、调休补班周末照跑」时，不用改 schedule 也不用手动 pause——用 cron 的 `script` 参数做前置判定：

1. **schedule 设每天**：`30 8 * * *`（脚本全权判定哪天跑，schedule 只定时间）
2. **script 输出三态**（相对路径解析到 `HERMES_HOME/scripts/`）：
   - `WORKDAY` → 上班日（普通工作日 + 调休补班的周末），agent 继续
   - `HOLIDAY` → 法定放假日，agent 回 `[SILENT]` 完全静默
   - `WEEKEND` → 普通周末，agent 回 `[SILENT]` 静默
3. **prompt 开头加判定指令**：看到 WORKDAY 才继续，HOLIDAY/WEEKEND 直接回复 `[SILENT]` 结束（不审读/不评论/不改基线/不投递）
4. **数据文件** `cn_holidays.json`：holidays=放假日（连休全部日期）、workdays=调休上班日（补班周末）；每年 11 月国务院公布次年安排后加年份 key；未配置年份脚本退化为基础周判定（不阻断）
5. **实现**：脚本 `cn_holiday_check.py` + 数据 `cn_holidays.json` 已在 `HERMES_HOME/scripts/`（2026 年数据 = 国办发明电〔2025〕7号，33 放假日 + 6 调休日）
6. **源码确认**（cron/scheduler.py `_run_job_script`）：相对/绝对路径都校验须在 scripts 目录内（防路径穿越），用 `sys.executable` 执行；`.sh`/`.bash` 走 bash，其余走 python

**适用边界（2026-08-11 用户拍板分类原则）**：节假日静默只该用于**工作类** cron（设计团队协作：审读/每日摘要/健康检查等投递团队群的任务）。**维护类** cron（备份/巡检/token 检查/版本简报/技能同步）和用户自己的 cron **每天触发、不排除节假日**——系统维护不等人，token 过期不会因放假就不过期。维护类用纯 schedule（`30 8 * * *`），不挂节假日脚本。所有 cron 时间统一早上 8:30（用户偏好）。

**坑**：git-bash 终端直接 `python scripts/xxx.py` 可能因 MSYS 路径混入报错（`C:\c\Users\...`）——cron 调度器用 sys.executable 不受影响；测试时用绝对路径（`"C:/Users/.../scripts/xxx.py"`）或先 cd 到 scripts 目录。

### script 执行链路 bug：errors 参数冲突（2026-08-12 实测修复）

**现象**：agent 简报里出现 `subprocess.run() got multiple values for keyword argument 'errors'`——挂 script 的 cron（伏妖记审读/飞书每日摘要）的节假日判定脚本**从未真正执行过**，agent 拿不到 WORKDAY/HOLIDAY 标记，只能自己猜工作日，节假日静默机制形同虚设（周末/节假日可能误推）。

**根因**：cron/scheduler.py `_run_job_script` 的 `subprocess.run(...)` 显式传了 `errors="replace"`，同时 Windows 分支的 `popen_kwargs = {"creationflags": ..., "encoding": "utf-8", "errors": "replace"}` 里又放了一份——`**popen_kwargs` 展开时关键字重复 → TypeError。属 2026-08-08「28 处 subprocess 硬化」的遗留尾巴（那次给调用点加了 errors，但没注意到 kwargs 里已有一份）。

**修复**：删掉 `popen_kwargs` 里的 `errors`（保留显式参数那份，行为不变）。本地 commit 1034b96e6（只动 scheduler.py 一行）。hermes update 覆盖源码后需重打。

**⚠️ 2026-08-15 复发教训：修复必须同步进补丁正本**。1034b96e6 只改了源码、没加进 hermes-local-patches.diff，hermes update 覆盖后复发（`popen_kwargs` 的 errors 被官方源码带回），表现为周末照常推送但 agent 简报里没有 WORKDAY/HOLIDAY/WEEKEND 标记行（脚本静默失败，agent 无感知）。判定方法：`_run_job_script` 直调返回 `Script execution failed: subprocess.run() got multiple values for keyword argument 'errors'`；或查 cron 输出文件里有无三态标记行。修复已并入补丁正本（scheduler.py 第二个 hunk，删 popen_kwargs 的 errors），重打一次到位。

**验证（不用跑整个 job）**：直接调用函数最省——`python3 -c "from cron.scheduler import _run_job_script; print(_run_job_script(r'C:/Users/HMSJ/AppData/Local/hermes/scripts/cn_holiday_check.py'))"` 应返回 `(True, 'WORKDAY ...')`。注意：**改 cron 调度器源码后必须重启 gateway 才生效**（调度器住在 gateway 进程内，手动 `cronjob run` 走的是当前会话进程、加载的是旧模块——见「调度机制」末尾）。重启法：`taskkill /F /PID <gateway_pid>` + `schtasks /Run /TN "Hermes_Gateway"`（MSYS 下 taskkill/schtasks 用单斜杠，`//F` 会报 Invalid argument）；gateway 是 venv 启动器 + runtime 双进程结构（8644 由 runtime 子进程监听），等 gateway.log 出现 `Gateway running with N platform(s)` 即就绪。

## Cron prompt 内脚本路径写法（MSYS 坑，2026-08-11 实测修复）

cron job 的 prompt 里让 agent 用 terminal 跑脚本时，**路径写法直接决定成败**——cron 的 bash 环境（git-bash/MSYS）会对路径做转换：

| 写法 | 结果 |
|---|---|
| `python3 ~/AppData/.../xxx.py`（波浪号） | ❌ MSYS 把 `~` 解析成 `/c/Users/...` 再被 python 拼成 `C:\c\Users\...` 报错 |
| `python3 C:\Users\...\xxx.py`（反斜杠） | ❌ bash 吞反斜杠 → `UsersHMSJDocuments...` 报错 |
| `python3 'C:/Users/.../xxx.py'`（**正斜杠+单引号**） | ✅ 实测可用 |

**铁律**：cron prompt 里所有脚本路径一律写 `python3 'C:/Users/...'` 正斜杠+单引号；改完必须手动 `cronjob run` 触发验证（看简报 + jobs.json last_run 是否更新），不能只看配置改对。

## Hermes cron vs Windows 计划任务（用户问「排程任务没有这个」时）

两套调度系统，别混淆：
- **Hermes cron** = 业务任务（审读/摘要/备份/巡检），配置在 `~/AppData/Local/hermes/cron/jobs.json`，由 **gateway 进程内调度器**每 60s tick 执行——Windows 任务计划程序里永远看不到它们，用 `/cron` 或 agent 查
- **Windows 计划任务（Task Scheduler）** = 机器级守护，只有 5 个 Hermes 相关：Hermes_Gateway（自启）、Hermes_Gateway_Watchdog（每5分钟守护）、HermesDashboard（9120）、HermesRemoteServe（9119）、Hermes-HideHindsightWindow（隐藏弹窗）
- 用户说「排程任务没有这个是为什么」→ 解释业务 cron 在 Hermes 内部，不在 Windows 计划任务

## 投递排障

### 99992402 field validation failed（post + thread_id，2026-08-07 实测）

- **根因**：job `deliver=origin` 且创建时在飞书**话题/主题群聊**里 → origin 快照带 `thread_id`（omt_xxx）→ 投递时 adapter 用 `receive_id_type=thread_id` 创建消息 → **post 类型被飞书 API 拒 99992402**，且 fallback 正则只匹配 "content format of the post type is incorrect"，99992402 不匹配 → 无兜底直接失败、消息丢弃
- **判别**：其他 job 全用显式群地址（无 thread）正常，唯独 deliver=origin 的挂 → 查 jobs.json 的 `origin.thread_id`
- **修法**：deliver 改为显式 `feishu:oc_xxx`（不带 thread）。上游 issue #81169；本地补丁（adapter.py `send()` 剥离 thread 路由重试）在 scripts/patches，hermes update 后需重打
- 同源：audio 消息已有 fallback（`_send_uploaded_file_message`），post 漏了

### 投递内容污染（File-mutation verifier 噪音混入简报，2026-08-07）

- agent 执行中 write_file 被校验拒绝时，verifier 警告文本可能被模型吞进最终回复（如 c1~c6.json 写入失败段出现在投递的简报末尾）——cron 投递内容原样进群，工具噪音直接暴露给用户
- **防**：job prompt 加「最终回复防噪音铁律」——最终回复=纯简报，禁止 File-mutation verifier / NOT modified / git status 建议 / write_file 拒绝提示等任何工具输出，写完自查
- **已发消息补救**：见下方 SDK 编辑

## 飞书消息查询/编辑（lark-cli 未封装）

- lark-cli `im messages` 只有 delete/forward/merge_forward/read_users/urgent_*——**无 list 无 update**；`+messages-search` 需 search:message scope（user 身份，未授权）
- 用 lark_oapi SDK 直连（hermes-agent venv 自带）：凭据读 `%LOCALAPPDATA%/hermes/.env` 的 `FEISHU_APP_ID`/`FEISHU_APP_SECRET`（Hermes bot 应用）；lark-cli 自己的 `~/.lark-cli/config.json` 是另一个 app 别混
- 完整实操（ListMessageRequest sort_type 坑 / UpdateMessageRequest request_body / post payload 重建）→ `references/feishu-sdk-message-edit.md`
- 撤回：`lark-cli im messages delete --message-id <om_> --as bot --yes`（高危操作，须用户确认后才能加 --yes）

## 推理配置漂移防护（#44585，2026-08-12 实测）

**现象**：全局 provider/model 切换后，部分 cron job 报 `SKIPPED — global inference config drifted since creation`，last_status=error，但没有任何推理调用发生（fail-closed，防意外花钱）。

**机制**：job 创建时对未钉住的推理轴做快照（jobs.json 的 `provider_snapshot`/`model_snapshot`）。运行时若该轴未钉住（job 级 `provider`/`model` 为空）且当前全局值 ≠ 快照 → 跳过并报错。老 job（快照字段为 None，back-compat）不受影响；钉住的 job 不受影响；`cron.model`/`cron.model_provider` 显式默认也不触发。

**判定**：`python3 -c "import json; [print(j['id'], j['name'], j.get('provider_snapshot'), '/', j.get('model_snapshot'), '| pinned:', j.get('provider'), j.get('model')) for j in json.load(open(r'C:/Users/HMSJ/AppData/Local/hermes/cron/jobs.json', encoding='utf-8'))['jobs']]"`

**修复**：给受影响 job 显式钉住 `provider`+`model`（当前全局值，如 opencode-go / deepseek-v4-flash）。⚠️ **cronjob 工具的公开 schema 不暴露 model/provider 参数**——直接传会被静默丢弃（工具签名有但 schema 没有）。**可靠做法：直接编辑 jobs.json**（内置 scheduler 每 tick 重读 jobs.json，无需重启 gateway）：备份 → 改 `model`/`provider` 字段 → 验证 JSON 合法。改完不要手动 run（会推群噪音+更新基线），等下次定时触发自然验证。

**⚠️ 高危坑：cronjob update 的 `prompt` 参数会整体覆盖原 prompt**——想传 `provider=`/`model=` 时若误放进 prompt 字段，原 prompt 被覆盖且不可从工具回滚。恢复方法：`cron/output/<job_id>/<timestamp>.md` 是每次运行的完整输出快照，内含 `## Prompt` 段（skill 内容+job prompt 全文），从其中提取 `你是…` 起始到 `## Error` 前的部分即为原 prompt，用 `cronjob action=update job_id=<id> prompt=<完整原文>` 恢复（此调用只传 prompt 不传 model/provider 即可）。改完必须核对 jobs.json 里 prompt 长度与关键段落齐全。

### 全局跟随模式（关守卫 + 解钉，2026-08-12 用户拍板）

用户需求「cron 跟随全局模型 + 兜底链」——切全局模型后 cron 自动跟着走、不再被漂移守卫拦截。**当前用户的 cron 舰队即此模式，勿擅自重开守卫**：

1. **关守卫**：`hermes config set cron.model_drift_guard false`（config.py:4601 只有字面 `false` 才关闭；缺失/非布尔仍 fail-closed）。这是用户刻意关闭——防意外花钱的保险让位给全局跟随
2. **解钉**：jobs.json 里把 job 级 `model`/`provider` 字段清空为 null（快照字段保留无妨，守卫已关不再触发）
3. **兜底自动继承**：`fallback_providers`（config.yaml）是全局配置，cron 运行时 `get_fallback_chain`（scheduler.py:4023）自动逐级生效——**不用为 cron 单独配兜底**，主 provider 认证失败自动切
4. **生效无需重启 gateway**：scheduler 每次 run_job 时 `load_config()`（scheduler.py:3391），jobs.json 每 tick 重读——配置改动即时生效
5. **代价（诚实标注）**：守卫当初为 $7.73 事故设计（切到付费模型时未钉 cron 静默烧钱）。关闭后切昂贵全局模型，cron 会跟着用——用户已知情拍板，两害相权选了跟随

验证：`python3 -c "import yaml; c=yaml.safe_load(open(r'C:/Users/HMSJ/AppData/Local/hermes/config.yaml',encoding='utf-8')); print(c['cron'].get('model_drift_guard'), [e['provider'] for e in c.get('fallback_providers',[])])"`

## 与 cron-monitor 的关系

cron-monitor 管 job 创建/输出格式/渠道规则；本 skill 管调度机制/投递排障/消息编辑。重叠处（99992402 坑）两边都有，待 curator 合并。

## 飞书 Drive 文件夹监控模式（2026-08-14 伏妖记审读 cron 实测）

监控「飞书云文档里的项目文件夹」变化（新增/改动文档），LLM cron 定期对比文件夹快照：

- **身份/scope 分工（关键坑）**：
  - `lark-cli drive +search --query "关键词"` 必须 `--as user`（bot 缺 `search:docs:read` scope，报 99991672 access denied）
  - `lark-cli drive files list --params '{"folder_token":"xxx"}' --format json` 必须 `--as bot`（user 缺 `space:document:retrieve` scope）——**user 搜、bot 列，两身份互补**
- **基线对比**：每次运行列文件夹→提取 {token: name/type/modified_time}→与基线 JSON 对比（新 token=新增文档，modified_time 变=有改动）→写回基线。基线放 `HERMES_HOME/cron/output/`（例：fuyaoji_folder.json）
- **多文件夹输出拼接解析**：多个 `files list --format json` 输出 `>` 追加进同一文件是多个 JSON 对象拼接，`json.load` 报 "Extra data"——用 `json.JSONDecoder().raw_decode` 循环流式解析（逐个切出对象），勿先 json.load
- **改动文档分流**：剧本正本改动→完整审读+挂评论；其他文档改动（项目文档/设定方案）→fetch 全文提炼新决策要点进简报、交叉核对一致性，不挂评论
- **正本原则**：监控目标=飞书云文档文件夹（正本权威源），Obsidian 归档可能已落后——用户明确要求盯飞书、不盯 Obsidian（2026-08-14 伏妖记案例：Obsidian 已落后很多）
