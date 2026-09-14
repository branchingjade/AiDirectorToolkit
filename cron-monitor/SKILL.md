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

## 现有 Cron 任务（2026-09-08 实测 17 个）

全部由 `cronjob_manage list` 实拉，**清单必须随 cron 增删同步刷新**——不要靠记忆维护。

| Job ID | 名称 | 频率 | 状态 |
|--------|------|------|------|
| `e14576c54fcf` | 外部技能同步 | 每天 8:30 | ✅ ok |
| `7c3df411d075` | Hermes WebDAV 备份 | 每天 8:30 | ✅ ok |
| `491b6b1d28f3` | Hermes 版本简报 | 每天 8:30 | ✅ ok |
| `88ab7ff66681` | 飞书每日摘要-其他人对话 | 每天 8:30 + holiday check | ✅ ok |
| `d466e0d36bc2` | 知识库每日巡检 | 每天 8:30 | ✅ ok |
| `3319ff2ddaa6` | 知识库每周大维护 | 周日 8:30 | ✅ ok |
| `7875566b75f6` | 伏妖记定期审读 | 每天 8:30 + holiday check | ⚠️ 剧本 token 错（见「cron 配置审查范式」） |
| `4da8374c0b69` | 飞书协作健康检查 | 周日 8:30 | ✅ ok |
| `9cd411f36430` | GitHub 项目日报 | 每天 8:30 | ✅ ok |
| `33a66b9983b6` | GitHub 项目周报 | 周日 8:30 | ✅ ok |
| `795383fd8a53` | GitHub 项目月报 | 每月1日 8:30 | ✅ ok |
| `2ad7b042825d` | 记忆库画像类审计 | 每天 8:30 | ✅ ok（deliver=local） |
| `a87c3a295279` | 飞书 OAuth token 自动续期 | 每天 9:00 | ✅ ok（deliver=local） |
| `347fdcac76df` | 飞书渠道健康度早报 | 每天 8:30 | ✅ ok |
| `1b140a071247` | feishu-orphan-messages | 每天 8:30 | ✅ ok（deliver=origin） |
| `ebd87ff73725` | 团队 skills 共享到 OpenViking | 每天 8:30 | ⏸ **paused**（2026-08-31 起，paused_reason=null） |
| `2a92494153ca` | 月度考勤报表推送 | 每月1日 8:30 | 🆕 scheduled（**last_run_at=null，从未跑过**） |

**汇总**：15 跑 ok + 1 paused + 1 从未跑 + 1 跑 ok 但配置错（推送内容跟意图不符）。

**标准盘点命令**：
```bash
# 1. 全表
cronjob_manage(action='list')

# 2. 单 job 完整 prompt（list 不支持 job_id 过滤，必须读 jobs.json）
python3 -c "
import json
d = json.load(open('C:/Users/HMSJ/AppData/Local/hermes/cron/jobs.json'))
for j in d.get('jobs', d):
    if j.get('id') == '<job_id>':
        print(j['prompt'])  # 完整 prompt，没截断
        break
"
```

## cron 配置审查范式（2026-09-08 实战确立）

**触发场景**：用户说"顺便排查 cron"/"看 cron 有没有问题"/"这个 cron 推送为什么搞错了 X"。

**踩坑教训**：用户拍板"剧本是 K5d3... 已强调多次了"——但 cron `7875566b75f6` 的 prompt 写了 `Q1tBdNPMRoNQqcxzE0NcvdpHnGI`（杨编精撰独立版）当审读对象，**跑了 39 次**都没读过真主线。每天 8:30 输出"今日微调"推送——把 K5d3... 标成"另一版剧本"、把杨编精撰说成"主线正本"。`last_status=ok` 给了虚假安全感。

**根因三层**：

1. **cron prompt 写错对象 token**——LLM 严格按 prompt 跑，从不"猜"真实意图
2. **MEMORY 里多条 token 登记已过期**（EsMD/NSZK 当正本）——agent 加载 cron prompt 时被旧记忆同向强化
3. **用户对"正本是谁"的强调没传到 cron prompt 维护者**——cron 创建后没人复核 token 是不是变了

**完整审查五步（必走全）**：

### Step 1：拉全表 + 标基础异常

```python
cronjob_manage(action='list')
# 重点看：last_status=ok 但 last_run_at 异常（比如每天跑 last_run_at 隔了 7 天）
# 看：paused 状态的 job 和 paused_reason 是否为 null（无理由暂停 = 待排查）
# 看：last_run_at=null 但 state=scheduled（从未跑过 = 配置可能缺依赖）
```

### Step 2：取完整 prompt（list 不支持过滤，必须读 jobs.json）

```python
import json
d = json.load(open('C:/Users/HMSJ/AppData/Local/hermes/cron/jobs.json'))
for j in d['jobs']:
    print(j['id'], '|', j['name'], '|', j.get('deliver'))
    print(j['prompt'])  # 完整 prompt
    print('---')
```

**为什么必须读 disk**：`cronjob_manage list` 的 `prompt_preview` 截断到约 200 字符，**看不到 token/路径等关键身份字段**。

### Step 3：核对 prompt 内的"对象身份"与磁盘事实

对每条 cron，prompt 里如果引用了：token / URL / 文件路径 / 文档 ID / API endpoint / GitHub repo——**必须现场 fetch 或 stat 验证**：

| 引用类型 | 验证方法 |
|---------|---------|
| 飞书 docx token | `lark-cli docs +fetch --doc <token>` 看实际内容是不是 prompt 说的"正本" |
| 飞书 folder token | `lark-cli drive files list --folder-token <token> --as bot` 看子项 |
| 文件路径 | `stat` 看 mtime + `head` 看内容 |
| GitHub repo | `gh repo view <repo>` |
| API endpoint | `curl -I <endpoint>` |

**判定矩阵**：

| prompt 写的 | 现场实测 | 结论 |
|------------|----------|------|
| token A = 正本 | fetch A = 正本 | ✅ 一致 |
| token A = 正本 | fetch A = 旧版/独立版 | ⚠️ **token 写错**，必改 cron prompt |
| token A 不存在 | fetch 失败 | ⚠️ **token 已废**，cron 在白跑 |
| 文件路径 | 路径不在 | ⚠️ 路径漂移，必改 |

### Step 4：查"对象变更"和"cron 创建时间"是否对齐

cron 创建于 `created_at`（jobs.json 有），prompt 里 token 引用可能基于当时的事实。**如果 token 已有更替记录（MEMORY / OV / 飞书历史），cron prompt 没同步 = 必然错**。

**判定**：跑 `viking_search` 或 grep MEMORY 看这个 token 历史上是不是有过"已废/被替代"事件——有就说明 cron prompt 该改了。

### Step 5：产出三类修复建议

```
A. 改 cron prompt（最常见）—— 用 cronjob_manage update
B. 改 MEMORY/OV 旧登记（必要时）—— viking_remember
C. 跑 cron 验证（绝不建议手动 run）—— 等定时触发
```

**反向**：绝对不手动 `cronjob run` 验证（MEMORY 9/3 实战：手动 run 走当前会话进程走错代码路径 + 群推送噪音 + 更新基线让当天定时 run 判定无变化）。

**修 cron prompt 的范式**（伏妖记 cron 修复实战，2026-09-08）：

**首选：直改 `jobs.json`**（不走 `cronjob_manage update`，原因：长 prompt 字段传递可能丢内容/转义、update 必须把所有字段都带齐、cronjob_manage 是接口层不是 source of truth）

```bash
# 1. 改前基线（disk 三件套）
stat -c '%y %s %n' "C:/Users/HMSJ/AppData/Local/hermes/cron/jobs.json"
grep -c "<锚点 token>" "C:/Users/HMSJ/AppData/Local/hermes/cron/jobs.json"
```

```python
# 2. Python 改（用变量承载原行，避免 heredoc 转义地狱）
import json
d = json.load(open('C:/Users/HMSJ/AppData/Local/hermes/cron/jobs.json', encoding='utf-8'))
jobs = d.get('jobs', d) if isinstance(d, dict) else d
target = next(j for j in jobs if j.get('id') == '7875566b75f6')
prompt = target['prompt']

# 关键：先 repr() 看真实字节，不要凭印象拼 old_string
# >>> import re
# >>> for line in prompt.split('\n'):
# ...     if 'token_xxx' in line:
# ...         print(repr(line))   # 看清楚 \\" vs \\\"

old_segment = '<原段，从 repr() 复制字面字符串>'
new_segment = '<新段>'
assert prompt.count(old_segment) == 1, f'命中 {prompt.count(old_segment)} 次，放弃'  # 必须唯一
target['prompt'] = prompt.replace(old_segment, new_segment)
json.dump(d, open('C:/Users/HMSJ/AppData/Local/hermes/cron/jobs.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
```

```bash
# 3. 改后验证三件套（必走全）
stat -c '%y %s %n' "C:/Users/HMSJ/AppData/Local/hermes/cron/jobs.json"  # mtime 变了 + 字节数有合理 diff
grep -c "<新锚点 token>" jobs.json  # 新锚点 ≥1
grep -c "<旧锚点 token>" jobs.json  # 旧锚点 = 0（或预期的注释残留次数）
```

**Python heredoc 转义陷阱**（2026-09-08 实战卡点）：bash heredoc 嵌套 Python 字符串时，反斜杠层级会爆。`\\\\\"` 在 shell + Python 双层解析后不是 `\\\"` 而是 5 字符字面。**根治**：把要替换的段先 `repr()` 出来看真实字节，再赋值给 Python 变量，最后用 `.replace()`——全程不靠"猜转义"。

**非污染性功能验证**（不调 `cronjob run`）：
- 不要 `cronjob_manage run` 验证（会污染基线 + 群推送噪音 + 走当前会话进程非 gateway）
- 做法：从改后 prompt 里**抽那条 fetch/curl 命令**，单跑一次确认能拿到正确数据
- 验证命令不写进 cron schedule、不发群——纯诊断

**次选：`cronjob_manage update`**（适合单字段、prompt 短、不在意是否直改 disk 的场景）：
```python
cronjob_manage(action='update', job_id='7875566b75f6', prompt=<新版 prompt>)
# 不写 schedule/deliver/skills/script——只覆盖要改的 prompt
# 改完同样 disk 三件套验证
```

**配套铁律（持久化）**：

- **MEMORY/OV 里的"对象身份"声明必须有创建日期 + 失效条件**——比如"剧本正本 K5d3... 截至 2026-09-08"——避免半年后 cron prompt 维护者不知道有变更
- **每次对象变更（剧本换版 / folder 重命名 / API 迁移）必触发 cron prompt 审查**——把"对象变更"加进 cron 维护 checklist
- **审查 cron 时不只查"跑没跑通"，更查"跑得对不对"**——`last_status=ok` 是必要条件不是充分条件

## 飞书 folder 监控与登记范式

> **配套 reference**: `references/feishu-folder-registry.md`（5 步法 + 反例 + 验证清单）

飞书 folder 下的文档清单是**会动态增删**的（用户拍板 2026-09-08）。涉及飞书 folder token 的 cron prompt 必须每 N 周重盘：

1. **定位真 folder token**：用户给的 `/drive/folder/<token>` URL 是唯一权威，根目录列不全（伏妖记这次实测：根 2 个 docx + 5 子 folder；递归到底 = 19 份）
2. **递归列全树**：bot 身份可列（user 缺 `space:document:retrieve` 会 401）
3. **每份 docx 实测 fetch**：folder 列表只给 name/token/mtime，**正文必须 fetch** 才知道是不是"正本"
4. **角色身份必须标清**：主线正本 / 项目台账 / 旧版作废 / 上游素材 / 美术考据 / 测试文档——同名文件不实测 fetch 会把"独立剧集版"当"主线"（伏妖记 cron 39 次跑错根因）
5. **台账落盘 + disk 验证**：写 `Projects/<项目>/文档台账.md`，stat mtime + grep 锚点 + wc 字节三件套

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
