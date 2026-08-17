---
name: cron-monitor
description: "通用定时监控推送框架——采集数据→LLM加工→格式化推送。支持多源配置，飞书推送。所有定时报告类 cron 的统一入口。"
version: 1.1.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, monitor, notification, feishu, release, rss]
---

# Cron Monitor — 通用定时监控推送

所有定时报告类 cron job 的统一规范入口。覆盖 LLM 驱动监控、脚本采集推送、格式约定、渠道规则。

## 现有 Cron 任务

| Job ID | 名称 | 频率 | 类型 | 说明 |
|--------|------|------|------|------|
| `491b6b1d28f3` | Hermes 版本简报 | 周一 9:00 | LLM | 本地 vX → GitHub latest，对比差距 + 中文简报 |
| `e14576c54fcf` | 外部技能同步（统一） | 每天 9:00 | LLM（terminal 调脚本） | 自动发现所有 tap + yaml 配置的源，格式自检测，JSON 输出→LLM 智能判断报告 |
| `7c3df411d075` | 备份 | 每天 8:00 | LLM（terminal 调脚本） | Hermes+Obsidian → 坚果云 WebDAV |
| `d89acf50b8a2` | lark-cli OAuth token 检查+自动续期 | 每天 9:00 | LLM（terminal 调脚本+lark-cli） | 过期前自动触发续期（lark-cli whoami），refresh token 已过期时提醒手动授权 |
| `9cd411f36430` | GitHub 项目日报 | 每天 8:30 | LLM（terminal 调脚本） | GitHub Search API 采集→LLM 筛选分领域简报，脚本做增量标注（is_new/stars_gain） |
| `33a66b9983b6` | GitHub 项目周报 | 周日 8:30 | LLM（terminal 调脚本） | 同上，weekly 窗口 |
| `795383fd8a53` | GitHub 项目月报 | 每月1日 8:30 | LLM（terminal 调脚本） | 同上，monthly 窗口 |

全部 LLM 驱动（`no_agent=false`，不配 `script` 字段），推送到飞书 DM。无更新也报告。

## GitHub 项目侦察模式（scripts/github_watch.py）

每日/周/月「GitHub 值得关注项目」日报的标准做法（2026-08-11 建立）：

- **数据源**：GitHub Search API（`/search/repositories`），非官方 trending API 已挂（gitterapp 404），trending 页面是 JS 渲染抓不到——官方 Search API 是唯一稳路
- **认证**：未认证限 10 req/min；本机 gh 已认证（branchingjade），脚本自动 `gh auth token` 带上（30 req/min）。脚本勿写死 token
- **查询结构**：通用新星（`created:>窗口 stars:>阈值`）+ 四领域（AI影视工具/Agent框架/前端工具/飞书生态，`关键词 pushed:>窗口 stars:>阈值`）——pushed 窗口让老项目新动态也进候选（用户拍板：不限于新项目）
- **⚠️ Search API 422 坑**：`in:name,description,topics` 里 OR 关键词**超过约5个就 422 Unprocessable Entity**（实测 9 个 OR 必挂，4 个 OK）。每个领域必须拆成 ≤4 OR 的子查询。`in:readme` 匹配太宽会混入无关大项目（flutter 被标成飞书生态），用 name,description,topics 即可
- **限流保护**：查询间 sleep 1.2s（5+8 个查询 ≈ 30 req/min 上限内）
- **增量标注**：脚本维护 `scripts/.github_watch_state.json`（gitignore），记录上次报告的项目名→stars。输出时标 `is_new`（首次出现）/`prev_stars`/`stars_gain`——LLM 据此判断旧项目是否值得重复推（日报≥500/周报≥2000/月报≥5000 或确实值得再看）。用户允许重复推，但要理由
- **LLM 筛选**：每领域精选 2-3 个宁缺毋滥，按领域分组输出中文简报，英文描述翻译，项目名保留英文
- **分类原则**：GitHub 日报属「用户自己的 cron」——每天触发、**不挂节假日检测**（cn_holiday_check 只挂工作类）

## 快速开始（新增监控源）

**方式一：加进 sources.yaml**（适合 GitHub Releases / RSS / API）
1. 编辑 `~/.hermes/hermes_monitor_sources.yaml`
2. 按模板加一条源
3. state 文件自动管理（`~/.hermes/hermes_monitor_<name>.txt`）

**方式二：脚本采集 + LLM 格式化**（适合复杂采集逻辑）
1. 写脚本采集数据→print 到 stdout
2. 创建 cron job，prompt：`用 terminal 执行 <脚本>，读取输出格式化为中文简报作为最终回复。`
3. 脚本存 `~/.hermes/scripts/`

## 监控源配置（sources.yaml）

```yaml
sources:
  - name: hermes-agent           # 唯一标识
    type: github-release         # github-release | rss | custom-command
    repo: NousResearch/hermes-agent
    enabled: true
    llm_level: 3                 # 1=纯翻译 2=+解释 3=+评级+建议
    include_categories:          # 只报告这些分类
      - security
      - windows
      - desktop
      - cli
      - tools
      - core
    exclude_keywords:            # 过滤关键词
      - discord
      - slack
      - docker
    max_items: 2                 # 每分类最多条数
```

## 输出格式约定

**LLM 驱动格式：**
```
## 🆕 v0.17.0 — 覆盖范围大扩展
一句话概括。

[一个 ``` 代码块包裹所有更新条目，分类+emoji+评级]

> 💡 升级建议：具体、指明优先级
```

**格式要点（来自调试实战）：**
- 更新条目放一个 ``` 内，标题和概述在外面
- 每条解释 10 字以内
- 评级 🔴🟡⚪ 在码块内生效
- 6-8 条覆盖全部分类
- 升级建议写具体：优先级、避坑

## 通用公约

1. **中文输出**：不允许英文。`cron.wrap_response: false` 必须设
2. **LLM prompt 关键句**："最终回复就是简报正文，不要工具调用，不要结束语"
3. **变更报告**：对比上次状态，报告增量
4. **无变更也要报告**：即使没有新内容，也要输出简洁状态（如"无更新""已是最新"）。用户不想猜"是没跑还是没变化"
5. **渠道规则**：cron 自动推→飞书；Hermes TUI 手动问→TUI 回。不跨渠道
6. **自检清单**：新增/修改后必须 `cronjob run` 验证

## LLM 加工级别

| 级别 | 做什么 |
|------|--------|
| 1 | 纯翻译 英→中 |
| 2 | + 解释对用户的影响 |
| 3 | + 评级（🔴🟡⚪）+ 升级建议 |

## 调度机制（2026-08-07 源码查证）

- **并行执行**：gateway 内每 60s 一次 tick（`cron/scheduler.py` 的 `tick()`），到期 job 丢进 `ThreadPoolExecutor` 并发跑；并行度 = `HERMES_CRON_MAX_PARALLEL` 环境变量 > config `cron.max_parallel_jobs` > **默认无限制**（`HERMES_CRON_MAX_PARALLEL=1` 可恢复旧串行）
- **唯一串行例外**：带 `workdir` 的 job 走单线程队列——workdir 会改进程级 `os.environ["TERMINAL_CWD"]`，并行会互相污染
- **防重**：tick 文件锁（同一时刻只有一个 tick）+ `next_run_at` 提前推进 + `_running_job_ids` 在飞判重（同 job 运行中不重复触发）
- **手动 vs 定时**：手动 `cronjob run` 在当前会话进程直接跑 `run_one_job`（不走 gateway tick 池）；定时触发在 gateway 进程。改源码后手动 run 不生效，需重启对应进程

## 陷阱

- **投递内容污染（File-mutation verifier 噪音混入简报，2026-08-07 实测）**：agent 执行中 write_file 被校验拒绝时，verifier 警告文本可能被模型吞进最终回复（c1~c6.json 写入失败段出现在投递的简报末尾）——cron 投递内容会原样进群，工具噪音直接暴露给用户。修法：①投递前检查最终回复是否含 `File-mutation verifier`/`NOT modified this turn` 等工具噪声（截断或重写）；②已发消息可用 `im.v1.message.update` 编辑（lark-cli 未封装，用 SDK：`UpdateMessageRequest` + `_build_markdown_post_payload` 重建 post payload）
- **deliver=origin + 飞书话题 → 99992402 投递失败（2026-08-07 实测）**：job 创建时若在飞书**话题/主题群聊**里，origin 快照带 `thread_id`（omt_xxx），投递时 adapter 用 `receive_id_type=thread_id` 创建消息，**post 类型被飞书 API 拒 99992402 且无 fallback**（adapter 只对 post 的 "content format of the post type is incorrect" 错误降级 text，99992402 不匹配）。修法：deliver 显式指定 `feishu:oc_xxx`（不带 thread），别用 origin。上游 issue #81169，本地补丁在 scripts/patches（剥离 thread 路由重试）。⚠️ **手动 `cronjob run` 在当前会话进程执行**（模块可能旧，改了源码不生效）；定时触发在 gateway 进程（重启 gateway 才加载新模块）
- **LLM 输出陷阱**：deepseek 容易把报告写入文件（response_len=26→"已完成"）而非最终文本。prompt 必须写"最终回复就是简报正文，不要工具调用，不要结束语"
- **LLM 静默陷阱**：LLM 只调工具不输出文本→cron 视为 [SILENT] 不投递。必须引导 LLM 把报告作为最终回复
- **`***` 写入陷阱**：memory 中 masked 的凭据（`***`）会被 `write_file` 当成字面文本写入 Python 字符串，导致语法错误。脚本里凭据用 `startswith("PREFIX=")` 匹配，禁止包含 `***`
- **cron.wrap_response**：必须 false，否则英文 "Cronjob Response" 头尾污染
- **格式平衡**：整篇塞 ```→代码块、无码块→纯文本。正确：标题在外+一个码块包裹条目
- **HERMES_CRON_TIMEOUT**：cron job 的 inactivity 超时，默认 600s。**但这不是根因修复的优先选项**——如果已配置 fallback_providers，正确做法是给主 provider 配短 `request_timeout_seconds`（如 `hermes config set providers.deepseek.request_timeout_seconds 120`），让挂起请求快速失败→触发重试→切兜底模型。若只调大 cron 超时，API 挂起仍会干等（SDK 默认 600s read timeout 与 cron 600s inactivity 恰好相等，cron 先杀 job，兜底链永远不触发）
- **兜底模型不生效的诊断**：fallback 只在 API 明确报错（429/5xx/空响应）时触发；请求**挂起不返回**（`waiting for non-streaming API response` + `idle for 600s` 超时）时兜底链不触发。根因是 provider 未配 request_timeout_seconds。改 config.yaml 受保护，必须用 `hermes config set providers.<name>.request_timeout_seconds <秒>`，写 .env 也受保护
- **手动 vs 定时**：Windows 上 manual `cronjob run` 无法捕获 LLM 最终回复（SILENT），但定时触发正常。测试只能用定时触发或 lark-cli 直推
- **飞书 DM chat_id**：用 `lark-cli --as bot im +messages-send --user-id ou_xxx --text "..."` 测试可获取 oc_ 格式 chat_id
- **首次运行**：无 state 文件→全量报告。手动初始化 state 为最新值
- **版本对比对象**：对比本地安装版本（`hermes --version`），不是 last-seen tag。本地 vX 对比 GitHub latest→报告差距
- **LLM 驱动禁 script 字段**：`no_agent=false` + `script` 字段时 cron 先跑脚本→Windows 上 stdout 丢失→SILENT。正确做法：不配 `script`，让 LLM 自己 `terminal` 执行脚本
- **渠道不跨**：TUI 问→TUI 回，飞书问→飞书回，cron→飞书
- **HERMES_HOME 路径**：手动测试用 `~/.hermes/`，cron 用 `AppData/Local/hermes/`。脚本内优先读 `HERMES_HOME` 环境变量，fallback 检查两个路径
- **凭据读取**：cron 子进程 env 被 sanitize，脚本不能靠 `os.environ` 读飞书密钥。必须从 `.env` 文件直接 `startswith("FEISHU_APP_ID=")` 匹配
- **版本检查方式**：首选 `git -C ~/AppData/Local/hermes/hermes-agent log HEAD..origin/main` 显示本地真正缺少的提交。但 repo 是 shallow clone（depth=1）时只显示顶层合并提交，不显示具体功能提交——需 fallback 到 GitHub Compare API：`curl -s "https://api.github.com/repos/NousResearch/hermes-agent/compare/<old_sha>...<new_sha>"` → 解析 `total_commits` 和 `commits[].commit.message` 获取完整列表。`old_sha` 从 fetch 输出 `1c4cc00f7..5445e42b8` 提取前半段
- **`hermes --version` 格式**：输出含 `upstream <sha> · local <sha> (+N carried commit)`，需解析出 N 为落后提交数
- **shallow clone 陷阱**：Hermes Agent 仓库是 shallow clone（depth=1），`git log HEAD..origin/main` 只显示顶层合并提交。验证：`git rev-list --count HEAD` 返回 1。需用 GitHub Compare API 获取完整提交列表，或先 `git fetch --unshallow`（耗时较长）
