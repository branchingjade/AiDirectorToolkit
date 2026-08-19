---
name: hermes-dsh-fusion
description: DSH×Hermes 无缝融合——DSH 是 Hermes 默认执行引擎（本机 127.0.0.1:8080）。全部场景默认走 DSH：工程执行/创作推敲/协作起草/渠道辅助/调研分析/插件评估，Hermes 管渠道工具最终执行。触发：DSH、bridge、融合、降级、轨迹回流、反向通道、events.mux、dsh-inbox 插件、mux-token。
whenToUse: 默认加载——收到任务先考虑是否走 DSH 引擎（除渠道工具最终执行/简单问答外）；用户未指定即按默认走 DSH。决策由 Hermes（agent）判断，桥（代码）执行。
version: 2.3.2
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [DSH, DeepSeek-Harness, 执行引擎, 融合, 默认]
    related_skills: [hermes-workspace-conventions, hermes-dsh-skill-sync]
---

# Hermes × DSH 无感融合（DSH 默认引擎版）

**原则：DSH 是默认执行引擎。** 用户面对一个更强的 agent——背后是 DSH 跑任务、Hermes 管渠道工具最终执行。任务分类边界：

- **DSH 直连读类**（Hindsight recall/统计、cron 查看、Obsidian·skill 文件）——桥 `util` 命令
- **DSH 执行类**（工程长任务/批量/调研分析/创作推敲/协作起草/插件评估/技能库维护）——桥 `run` 命令
- **Hermes 单出口**（飞书发送/cron 增改/Hindsight 写入/Obsidian 写入/git 提交）——单出口审计纪律

## When to Use

- 用户点名「用 DSH」（保留）
- 显式决定用 DSH 执行的长任务/批量/调研/分析（判据见下）
- **不再默认**：收到任务不再自动考虑 DSH 引擎参与；Hermes 自干为主（渠道工具最终执行、cron 调度、记忆写入本就归 Hermes）

## cwd 定位（同源锚的正确用法）

**cwd 按任务指向具体目录，不是固定工作区根**——它决定 DSH 的写权限范围、AGENTS.md/skills 发现、会话隔离：

| 任务类型 | cwd 指向 |
|---|---|
| 创作项目活（剧本/分场/推敲） | Vault 项目目录，如 `C:\Users\HMSJ\Documents\KnowledgeBase\Obsidian Vault\伏妖记` |
| 脚本/工具/工作区活 | `C:\Users\HMSJ\Documents\Hermes` |
| 子项目活（deepseek-harness 等） | `Projects\<项目名>` |
| 知识库/研习活 | **Vault 对应目录或 Hermes 工作区**（读 skills 用绝对路径，**cwd 不要锚在 skills 目录**——系统资产目录不该是执行基准，任务写文件会落进去） |
| 分析/报告活 | `C:\Users\HMSJ\Documents\Hermes`（产出落 分析/） |

原则：**cwd = 任务产出应该落的地方**。DSH 只能写 cwd 及以下（沙箱写权限），所以把 cwd 指到任务目录 = 天然的范围声明，也保会话按项目隔离。**系统资产目录（skills/hermes-agent 安装目录）只作只读来源，绝不作 cwd 锚**。

## 桥（唯一的交接点，用户无感）

`scripts/dsh_bridge.py`——封装 DSH web /api 网关（127.0.0.1:8080，已实测）。**会话复用键 = cwd + 活跃线程**（默认续用、--new 显式断、close 显式收尾）；label 只是可读标签，不参与匹配：

```bash
# 跑一个任务（同 cwd 2 小时内默认续活跃线程；无活跃线程则新开）
python scripts/dsh_bridge.py run "<cwd>" "<任务>" [--label <可读标签>] [--new] [--timeout 秒] [--ttl 秒]

# 任务验收收尾：显式关闭活跃线程（忘关则由 2h TTL 兜底自动冷却）
python scripts/dsh_bridge.py close <cwd>|<sessionId>|<route>|--all [--purge]

# 查看会话注册表（每线程投递/复用统计 + 总命中率）
python scripts/dsh_bridge.py list
```

**结果契约（Hermes 只认这个）**：输出末尾固定一行 `BRIDGE_RESULT {json}`：
- `status`：`done`（完成）| `need_input`（DSH 缺料，见下）| `timeout`（超时，活跃线程保留可续）| `error`
- 其他字段：`sessionId` / `reused` / `summary{changes,verification,leftovers}`
- **退出码 0 = 正常**（状态看 status）；**退出码非 0 = 桥/DSH 故障** → 降级 Hermes 本机执行，不阻塞用户

前提：DSH web 在 8080 运行；OPENCODE_GO_API_KEY 由桥从 LOCALAPPDATA/hermes/.env 自动读取，无需手设。

**DSH web 启动与保活（2026-08-19 OOM 教训固化）**：
- 启动命令**必须带 8GB heap 上限**（rc.7 升级后默认 heap 跑大任务会 OOM 崩溃）：`cd Projects/deepseek-harness && node --max-old-space-size=8192 --import tsx/esm apps/cli/src/bin.ts web --port 8080`
- **自动保活**：计划任务 `DSH_Watchdog`（每 5 分钟）→ `scripts/dsh_watchdog.py`（工作区 git 管理，检测 8080 无监听即用上述命令拉起，10 分钟冷却防风暴；日志 `.hermes/dsh_watchdog.log`、状态 `.hermes/dsh_watchdog_state.json`）。看门狗失效排查：脚本文件丢失（曾因清理误删导致任务空转）或进程退出——重建脚本 + `schtasks /change /tn DSH_Watchdog /tr "pythonw <scripts路径>"`。

## 什么时候用桥（默认用，精确判据）

**决策纪律（收到任务的强制第一步）**：
1. 收到任务 → **先过走桥判据**（下方），显式决定「走桥 / 自干」
2. **自干必须命中全部 6 条自干判据**；任何一条不满足 → 走桥
3. **拿不准 → 走桥**（串线/漏用 DSH 的代价 > 一次桥调用成本）
4. **「我本地有现成资料可以直接答」不是自干理由**——调研/推荐/评估类任务（即使资料在手）属于「多步+需判断」，该走桥让 DSH 产出并留痕；Hermes 本地资料可作任务书背景注入，不是替代 DSH 执行
5. 走桥结果回 Hermes 验收转述（无感呈现）

**默认方向 = 走桥。** 判据单位是**任务/目标**，不是单个工具调用——50个"读配置"合起来就是 workflow，该走桥。

**走桥**（满足任意一条即走）：
1. **步骤≥2** 且存在依赖或分支（需编排）
2. **有歧义/需规划/需权衡**（非指令即动作）
3. 单步≥5s 或总时长≥30s（长任务/后台/无人值守）
4. 结果>10KB 或需读后分析/总结（隔离主上下文）
5. 需重试/回退/多策略错误处理
6. 高影响面（生产配置/skill/桥本身/git正本/飞书正本）需独立验收
7. 需并行 fan-out / 多源聚合
8. 需**留痕审计**的探索（桥天然留轨迹）

**Hermes 自干**（需同时满足全部）：
1. 单步（1次工具调用，无需分解）
2. 确定性（指令完整指定动作与目标，无判断空间）
3. 只读或低影响可逆（失败可安全重来）
4. 结果小（<10KB，不污染上下文）
5. 延迟<5s（真正的秒级即时）
6. 失败处理=简单上报（无需重试逻辑）

**兜底（保默认方向）：** 判据拿不准、任务落在灰区 → **走桥**。这是「默认用DSH」的实体化。

**易误判的场景（看似轻但该走桥）：**
- 批量轻步骤聚合（50个单步=workflow）
- "读配置"但需判断改哪、影响谁（=诊断）
- "API探测"但需搞清schema/报错原因（=多步试错）
- 改skill/改桥/改git正本（自指修改+高影响，blast radius大）
- 有副作用的"读"（触发token刷新/状态变更）

## 任务模板（保证轨迹质量 + 结构化总结）

投给 DSH 的任务文本建议结构（Hermes 组装，不用写文件交接）：

```
【背景】<项目/目录一句背景，必要时附相关知识库路径提示，如 妖玉知识库在 <path>，需要时自己读>
【任务】<具体任务，讲清目标、范围（允许动哪些文件/禁止动哪些）>
【要求】完成后用一行 JSON 总结（不要 markdown 代码块，直接输出这行）：
{"changes":"改了什么","verification":"怎么验证","leftovers":"遗留问题"}
```

**范围声明很重要**：明确"只许动 X，不许动 Y"；DSH 干完 Hermes 要按此对 diff。

**需要补充/校正时**（模板固定加这句）：`【补充约定】如果缺关键信息、需要确认口径、或发现方向需要校正——不要瞎猜硬干，在最终回答里输出【NEED_INPUT】+ 具体需要什么，等补充后继续。`

## 中途补充回路（层级 0 反馈信道）

DSH 干到一半缺料时，桥会返回：

```
[状态] 需要补充（活跃线程已保留，同 cwd 续投即可继续，勿 --new）
[请求] <DSH 原话：缺什么/要校正什么>
```

Hermes 处理流程：

1. 解读 `[请求]`——补上 DSH 要的信息（记忆召回/项目文档/规范/用户确认）
2. **同 cwd 再调一次桥，勿 --new**（活跃线程会自动续用原会话）：
   ```
   python scripts/dsh_bridge.py run "<同 cwd>" "【补充信息】<补的内容>。请继续完成之前的任务。"
   ```
3. DSH 会话上下文保留 + 新信息注入 = 增量补充，DSH 接着干
4. 循环直到 BRIDGE_RESULT 的 `status: done`（或用户喊停）

需要用户拍板的信息：Hermes 把问题转述给用户 → 用户答复 → 按上面续投。

## 无感呈现（关键）

桥返回的轨迹是结构化文本（🔧 工具调用 / ↳ 结果 / 💬 推理 / ── 回合）。Hermes 把轨迹**直接贴回对话流**，用户看到的就是 Hermes 在干活的样子——不要加"这是 DSH 干的"之类的话，保持无感（除非用户问起）。

```markdown
> 已开始处理：<任务一句话>
> 🔧 pwsh: Get-ChildItem ...
> 💬 推理：...
> （轨迹精简展示，太长的工具结果截断）
> ✅ 完成：<结果摘要>；文件已落在 <路径>
```

两个规则：
1. 轨迹**精简展示**：推理/工具行全保留，工具结果只留摘要（详细可让用户要求展开）
2. 结构化总结（changes/verification/leftovers）**必须消化后转述**，不贴原始 JSON

## 验收与归位（Hermes 的责任，不进对话也要做）

DSH 报告"完成"只当线索。Hermes 独立验证：

1. **diff 对照范围**：`git diff --stat` 对照任务范围声明，越界改动即 FAIL
2. **测试/检查**：涉及代码跑测试或语法检查；纯文件任务核对产物清单
3. **归位**：验收通过 → `git add <产物> && git commit`（中文、单逻辑）→ **有远程的仓库必须 `git push` 到正本**（GitHub 正本才是归档完成）→ 重要结论写回项目文档 → 值得记住的结论 retain 进 Hindsight
4. **关线程（可选提前收尾）**：`python scripts/dsh_bridge.py close <cwd>`——任务线结束显式关；**不关也安全：TTL 2h 超期自动 close、7 天后自动清理注册表**

**收尾六面以 hermes-workspace-conventions 为唯一本体**（Obsidian/Git/Skill/记忆/污染/DSH close）——本 skill 只列 DSH 相关的归位要点，规范变更改本体、不在本 skill 重复定义（2026-08-19 规范漂移教训：两处各写一份会改一处漏一处）。DSH 会话在 Hermes 工作区干活时，默认遵守工作区 `AGENTS.md` 注入的铁律 + 加载 hermes-workspace-conventions。

**git 唯一写者 = Hermes**：命令里不带 git 操作给 DSH（桥不传 git 任务除非明确要求）。

## DSH 直接会话的收尾三件套（用户直接在 DSH web 指挥，非桥投递）

桥投递的任务由 Hermes 验收归位（见上节）。但**用户直接打开 DSH web 会话发任务**时（无桥，轨迹不自动回流 Hermes），DSH 会话自己承担收尾——结果必须**主动落到 Hermes 侧**，对话里说完不算（Hermes 看不到）。2026-08-19 用户质疑「hermes侧返回的结果呢」后固化：

1. **git commit + push 正本**：有远程的仓库（技能库 → AiDirectorToolkit）commit 后必须 push，只 commit 不算归档
2. **Obsidian 日志**：写当日日志 `日志/<年-月>/W<周>/<日期>.md`（frontmatter tags/date/related + 主题小节），记录任务/根因/修复/提交号
3. **Hindsight retain**（Hermes 记忆层，recall 可达）：
   - `POST http://localhost:9177/v1/default/banks/hermes/memories`，body `{"items": [{"content": "<结论>", "tags": ["DSH", ...]}]}`
   - item 字段是 **`content`**（不是 text）；**超时给足 120s+**（首次嵌入计算慢，20s 必超时）
   - 验证：`python scripts/dsh_bridge.py util hindsight recall "<关键词>" --limit 3` 能命中
   - ⚠️ hindsight daemon 空闲自动停（idle-timeout）：retain 报不可达时先让 Hermes 跑一次 retain/recall 拉起 daemon 再重试

顺序做完三件套才算任务完成（对照工作区 AGENTS.md 铁律 + hermes-workspace-conventions 收尾六面）。

## 会话管理（活跃线程 + 路由键，内部机制，用户无感）

**心智模型：默认续、显式断、按任务线路由。**

**路由键（--route）= 任务线 ID ——「新消息该推给哪个会话」的实现**：
- **语义判断在 Hermes**：给每条投递打 route（该消息所属任务线的稳定 ID）
- **确定性执行在桥**：同 `(cwd, route)` 必同会话，不同 route 必隔离（并行不串线）
- 规则：
  - 同一逻辑任务线的多轮投递（含补充/校正/继续）用**同一 route** → 同会话（上下文连续 + 前缀缓存命中）
  - 不同任务线并行用**不同 route** → 各自独立会话
  - 任务线结束 `close <route>`；同任务线想重来 → `--new` + 同 route
  - **拿不准属于哪条线 → 新 route**（宁开新不串线：串线污染上下文 > 新开会话成本）
  - 不带 route → 回退同 cwd 最近活跃（兼容简单场景）
- **route 命名**：稳定任务线名（如 `cron-github-daily`、`fuyaoji-review`、`dsh-fusion-refactor`），**不要带时间/轮次等易变后缀**（v1 命中率≈0 的病根就是键随任务变化）
- **判断流程**：新消息 → 它延续哪条任务线？→ 用该线 route 调桥；无对应线 → 新 route

- 开新线：**--new**（旧活跃线程标记关闭，保留历史统计）
- 任务收尾：**close**（任务线结束显式关；**忘关由桥自动兜底**：TTL 2h 超期自动 close + 7 天后自动清理，不膨胀）
- 跨目录任务：cwd 不同自然新开
- label 只是可读标签，**不参与复用判定**（路由只看 cwd + route）
- **会话归组（DSH UI 不再「未分组」）**：新会话自动归入 cwd 对应工作区（桥 create 带 workspaceId）；历史/残留未分组会话用 `python scripts/dsh_bridge.py util attach "<cwd>"` 或 `util attach --disk`（扫描磁盘全部残留）批量归组

registry 文件：`.hermes/dsh-registry.json`（`list` 可查投递/复用统计与命中率；`close --purge` 清历史）。

## 上下文用量管理（单会话变满时）

**事实（已查 DSH 源码证实 2026-08-19）**：DSH 有原生自动压缩（`compaction-basic` 插件默认装载、默认开启）——上下文到模型 contextWindow 的 **80%** 时在回合边界自动触发，把早期内容折叠成 checkpoint 摘要（模板含决策/理由/约束/未决问题/后续所需数据），保留尾部继续会话。桥会标注压缩轨迹并返回 `compacted: true`。

**两档处理（不是二选一，是同一机制的两档）**：

1. **任务还在跑、活跃工作集为主 → 交给 DSH 自动压缩（默认零成本）**
   - 无需 Hermes 干预，压缩后会话继续（一次缓存全量重算，换后续 N 轮稳定命中）
   - ⚠️ 压缩丢细节可能导致后续走偏——收到 `compacted: true` 且结果可疑时，回退到档 2
2. **阶段完成/要验收/要跨天/要并行 → Hermes 受控整理（白盒、可审计）**
   - 让 DSH 把当前阶段写成摘要文件（含已完成/结论/待办/关键细节）→ Hermes 验收 + 关键结论 retain Hindsight（写类，归 Hermes）→ 桥 `--new` 同 route 重开，新任务书引用摘要文件
   - 等价于「手动 checkpoint」，但摘要内容 Hermes 验收过，可审计

**触发线（经验值）**：会话轮次 ≥ ~40 轮或预计 10 轮内将满窗口时，Hermes 主动判断走哪档；以实际压缩事件（`compacted: true`）为准。

## 监测与迭代优化（投入使用后）

**数据源**：
- `python scripts/dsh_bridge.py list` — 会话状态 + 汇总：命中率 / 失败·超时次数 / 压缩次数（每线程也有）
- `.hermes/dsh-bridge.log`（JSONL 追加）— 每次 run 一条：ts / cwd / route / reused / status / duration_s / compacted
- `python scripts/dsh_bridge.py util log [--tail N]` — 快速看最近运行记录

**迭代时看什么**：
- **命中率低** → route 命名不稳定（带易变后缀）或投递没带 route——回查 log 的 route 分布修正
- **失败/超时集中在某 route** → 该任务线类型有问题（任务书不清/范围过大/DSH 能力不足）——优先优化
- **压缩频繁**（compacted 多）→ 任务太长，该走「上下文用量管理」档 2 分段
- **duration_s 异常大** → 任务书是否够薄、DSH 是否在低效试探

## 资源访问边界（读类直连 / 写类经 Hermes）

「用 Hermes 的 X」≠「调用 Hermes agent」——cron/飞书/skill/Obsidian/Hindsight 是 Hermes 背后的**资源**。DSH 直连读类（知情自取），写类仍归 Hermes（保持单出口审计纪律，2026-08-17 已裁定「不建反向桥」）：

**DSH 读类直连（不走 Hermes，省一次往返）**：
- Hindsight 记忆召回：`python scripts/dsh_bridge.py util hindsight recall "<query>" [--limit N]`
- Hindsight 健康/统计：`python scripts/dsh_bridge.py util hindsight stats`
- Hermes cron 任务列表：`python scripts/dsh_bridge.py util cron list`
- Obsidian / skill：文件系统直接 glob/read（Vault = `C:\Users\HMSJ\Documents\KnowledgeBase\Obsidian Vault`）
- ⚠️ Hindsight daemon 空闲自动停（idle_timeout）：recall 报不可达时，让 Hermes 先 retain/recall 拉起，或降级问 Hermes

**写类渠道仍归 Hermes（DSH 不碰，审计边界 + git 唯一写者纪律）**：
- 飞书发送、cron 新增/修改、Hindsight 写入、Obsidian 写入、git —— 全部由 Hermes 执行；DSH 需要这些动作时经 BRIDGE_RESULT / NEED_INPUT / 收尾 check 回流给 Hermes

## Skill 共享与写权限纪律（两边的 skills 是共用的）

**skills = Hermes × DSH 共享资产**（同一文件体系，如 `C:\Users\HMSJ\AppData\Local\hermes\skills`）：

- **读**：DSH 任务可读任何 skill（知识库/参考/规范），用绝对路径，**不需要 cwd 锚定**
- **写（维护）**：DSH 可维护 skill 文件（尤其融合相关：hermes-dsh-fusion 等）——**只精确编辑目标文件本身，不产生散落文件**
- **物理工作区限制（防扩散核心）**：
  - cwd 永远锚「任务产出目录」，**绝不锚系统资产目录**（skills/安装目录）——见 cwd 定位表
  - 写 skill 是**特例授权**（明确维护意图时才动），不是默认写范围
  - 任务产出落 cwd；skill 改动只落目标 skill 文件；临时文件用完即删
- **自指高影响**：改 skill = 改执行指令层，**执行权在 DSH、验收在 Hermes**（改后独立 diff 验收）

## 坑

1. **会话 id 冲突**：桥已处理（同 id 复用/忙时换新 id）；手工调 API 时牢记"create 一次，prompt 永远同 id"
2. **任务文本里别带 git 指令**（唯一写者纪律）；要 DSH 分析 git 历史可以（只读）
3. **超时**：BRIDGE_RESULT 返回 `status: timeout`，活跃线程保留，同 cwd 续投可续；超长任务给足 --timeout
4. **DSH web 重启**（8080 进程没跑）→ 桥退出码非 0，Hermes 降级本机执行；会话存磁盘可 resume
5. **轨迹里 assistant/chunk 是 token 级流**：桥用 assistant/message（完整消息），不要逐 chunk 展示
7. **Windows 路径**:cwd 用 `C:\...` 格式(桥接受),DSH 内工具用 pwsh(PowerShell 语法)
8. **别续「上次超时未收尾」的旧线程**:可能再次等待——换线时用 --new
9. **inline 任务文本会被 bash 改写**(2026-08-19 实测两次,两次不同失败模式):
   - **A. 命令替换**:任务文本里出现反引号 / `$()` / `{}`/JSON 段,bash 把它当命令执行,stderr `xxx: command not found`,桥 5 分钟到点返回 timeout 124。**标志**:bridge 日志没记录 prompt 成功 / DSH 收到的是字面 `--task-file` 这种"参数名当任务"。
   - **B. 凭空虚构参数**:CLI 不存在 `--task-file` 这种参数——`run --help` 只支持位置参数 `<cwd> <task>` + `--route/--label/--new/--timeout/--ttl`。任何"为了绕开 shell 转义"加的自定义 flag,都会被 bash 当成任务文本传给桥。
   - **唯一稳的姿势**:**任务文本写到文件 + 用 Python 脚本调 `run_task()`**。不要相信任何"smart quoting" / `--task-file` / `eval $()`。Python `urllib` 把字符串变成 JSON payload 发给 `/api/session.prompt`,完全绕开 shell:
     ```python
     # scripts/_dispatch.py
     import sys
     sys.path.insert(0, r"C:/Users/HMSJ/Documents/Hermes/scripts")
     import dsh_bridge as br
     task = open(r"C:/Users/HMSJ/AppData/Local/Temp/dsh_task.md", encoding="utf-8").read()
     print(br.run_task(cwd=r"C:/.../cwd", task=task, route="...", force_new=True, timeout_s=480))
     ```
   - 跑这种脚本用 `terminal(background=True, notify_on_complete=True)`——桥可能阻塞 5+ 分钟,前景 terminal 会在 300s 截断。
   - **诊断口诀**:bridge `timeout` + stderr 是 shell 报错 = 任务没投出去,DSH 那边可能正"自己找事做";`timeout` + stderr 干净 = DSH 真在跑,只是慢。

10. **超时 ≠ 没在干,更不等于任务丢了**(2026-08-19 二次踩坑)。`status: timeout` 只代表"桥轮询超 deadline";DSH 会话本身可能还在磁盘活跃(注册表 active 字段=True)、可能根本没收到任务、可能在跑大活。**`status: timeout` 永远要读 `session.jsonl.zstd` 才能定因**:
    - 路径:`~/.dsh/sessions/<projectKey-escaped>/<sessionId>/session.jsonl.zstd`(.zstd 用 `zstandard` Python 库解压;系统无 zstd CLI)
    - 看 `type=user/message` 的 seq 是否包含你的任务文本——包含 = 任务已投,DSH 在干,bridge 只是等了不到 turn/end;不包含 = 任务根本没进会话
    - 看 `type=assistant/message` 的 reasoning 第一句——DSH 是不是在自言自语"我没收到任务/我在探测环境"。这种就是任务丢失,要 `--new` 重投
    - **决策树**:
      - 任务文本进了 + DSH 在干真活 → 同 cwd 同 route 续投(不加 `--new`),告诉 DSH「继续」
      - 任务文本没进 + 活跃会话空转 → **`force_new=True` 开干净新线**,别续旧(它已经被污染)
      - 任务文本进了 + DSH 卡死/无 tool 活动 5 分钟+ → `kill` 旧会话(`process kill` 或 close 后 force_new),别续
    - 这一切**不是用户问起才做**——`timeout` 一回,自动跑这套诊断脚本(`scripts/diag_bridge_timeout.py` 见参考)。

11. **不要预支"DSH 在干"的声明**。bridge 返回 sessionId 不代表 DSH 开始读源码——它要先走 create→permissions→inbox→title→context 初始化(可能 5-15 秒),看到首个 `tool/call` 事件才算真开干。对话流里说"DSH 收到任务书、桥在跑"是 OK;说"DSH 在改 service.py"是预支——用户当场就会抓(2026-08-19 用户原话「我看到这个 msg,思考 5 秒,想到点:DSH 没在干,刚刚才派给它」)。纪律:**桥 timeout/创建中** 阶段只说「派发已发出」;**首个 tool/call 出现后** 才说「DSH 开始改 X」。

12. **Cordis Service 双重注册阻断 session.create（2026-08-19 实测，两种独立根因）**。session.create 返回 `agent-preset-invalid`、错误码带 `Service already registered`——两种独立路径都会触发，**必须分别修复**：

   **根因 A：skill-filesystem 23 个分类目录双重注册**。DSH 的 `creator` preset 在 `~/.dsh/.agent-presets/creator/agent.cordis.yml` 里有 skill-filesystem 块列出 23 个分类子目录（`devops/`、`scriptwriting/`、`妖玉影视/` 等）；**机器级 patch** `~/.dsh/cordis.patch.yml` 也列同样 23 个目录。DSH 启动时两层都执行 → 每个 skill 的 cordis Service provider key 报 `already registered` → preset 加载失败。

   **根因 B：`tool-cordis` 与 `WorkspaceRegistry` 争 cordis `Service` key**。`packages/workspace/workspace/src/index.ts` 里 `WorkspaceRegistry extends Service`——DSH 启动时它先占用 cordis 内置 inspection provider key `Service`。preset `creator` / `hermes-cordis` 里也声明 `tool-cordis` 插件（`@deepseek-ai/dsh-tool-cordis`）——它也要注册同 key `Service` → `already registered`。**重启后才会出现**（首次启动 WorkspaceRegistry 可能没初始化占位）。

   **修复**：
   - 根因 A：删 preset 层 23 个分类目录块，只留 `process.getBuiltinModule('node:url').fileURLToPath(new URL('skills/', baseUrl))`（preset 自带目录 cordis-plugin-development + editing-cordis-compositions）；分类目录由 cordis.patch.yml 机器级统一负责。两份要立即同步。
   - 根因 B：**注释掉 preset 里的 tool-cordis**（让 `creator` / `hermes-cordis` 两份 agent.cordis.yml 都把 `- id: tool-cordis` 注释掉）。副作用：DSH agent 失去 self-modification runtime 能力——本机生产用 OK，自我修改走 Obsidian + git 路径。
   - **DSH 升级可能复发这两根因**——升级后跑一次 session.create 验证，复发就重新执行两条修复。

   **诊断口诀**：`session-not-found` + 8080 监听正常 + DSH 启动无明显报错 = 八成 cordis 双重注册。`netstat -ano | grep :8080 | grep LISTENING` 先确认 DSH 在跑（避免误判为桥问题），再 `curl -X POST .../api/session.create` 看响应里有没有 `agent-preset-invalid`；错误详情里 `Service already registered` 出现几次 / 引用哪个文件路径区分根因 A 或 B。

13. **cwd 必须是 Windows 原生路径，桥要规范化（2026-08-19 实测）**。从 bash 拿到的 cwd 形如 `/c/Users/HMSJ/Documents/Hermes`（MSYS 缩写）；DSH 把它当字面值存进数据库 = `C:\c\Users\HMSJ\Documents\Hermes`，创建伪工作区、session 错位、后续 prompt 全 `session-not-found`。**桥必须在 `_ensure_workspace()` 内部把 `/[a-z]/...` 改成 `[A-Z]:\...`**（参见 `references/DSH-bridge-cwd-normalization.md` 完整诊断）。session.create **永远优先传 workspaceId**（桥 v2.1 已是这个设计），让 DSH 按 workspace 的 path 字段而非请求 cwd 决定归属，规避路径规范化歧义。**任何 cron prompt / 任务书 / shell 脚本传 cwd 给桥时都得走 `_normalize_cwd()`**——直接传 POSIX 路径等于把坑挪到调用方。

14. **DSH 没有真"挂起提问"协议，靠启发式检测（2026-08-19 实测）**。DSH web UI 显示"提问·等待回答"+ 候选弹弹——**这是 DSH web 客户端的渲染效果，不是 server-side 协议**。实测证据：`session.history` 最新事件是 `turn/end`（已完成），没有 `ask/pending/need_user` 类型事件；`ask_user_question` 工具虽在 DSH 工具清单里（toolList），但**调用它不产生外部可监听事件**——桥/Hermes/飞书渠道收不到通知。
   - DSH web UI 检测到 assistant 文本里有结构化候选（数字列表 + 触发词），把它显示成弹窗让你手动点选。
   - **反向通道实现（scripts/dsh_inbox_watcher.py）**：扫描所有最近更新的 session → 拉 `maxMessages:30` 的 history → 检测 assistant 文本里有数字/字母/圆圈编号开头的列表 + 触发词（「请选择/确认/推荐/建议/首选/选哪个/哪个好」等14个）→ agent 仲裁（技术性确认→代答；其他→推用户）→ 双渠道推送。
   - **DSH 升级可能改 ask 触发事件 schema**——升级后跑一次 watcher 端到端验证：喂 DSH 一个"按格式给出三个候选"的 prompt，看 watcher 检测 + 推送是否正常。
   - **桥脚本调用 lark-cli 不要走 wrapper**：`lark-cli` 在 Windows 是 shell wrapper（`/c/Users/HMSJ/AppData/Local/hermes/node/lark-cli`），subprocess 直接调它报 `WinError 193 %1 不是有效的 Win32 应用程序`。**直连 node + run.js**：
     ```python
     cmd = ["node", LARK_CLI_RUNJS, "im", "+messages-send",
            "--as", "bot", "--chat-id", CHAT_ID, "--text", msg]
     ```
     `LARK_CLI_RUNJS = C:/Users/HMSJ/AppData/Local/hermes/node/node_modules/@larksuite/cli/scripts/run.js`。**私聊频道 ID 是 `oc_xxx`（chat-id），不是 `ou_xxx`（user-id）**——直接传 `oc_f7b91a...` 当 user-id 会报 `invalid user ID format`。

15. **双向同步 DSH 侧修改 + 桥 cwd 修复要同步进 Obsidian 知识库（2026-08-19 实测）**。今天修了 `~/.dsh/.agent-presets/{creator,hermes-cordis}/agent.cordis.yml`（注释 tool-cordis）。**DSH 升级会覆盖这两个文件**（preset 是官方组件，升级会重建）。坑 12 修复注释必须留在**两处**：
    - preset 文件内（注释 + 注释说明，作为 in-file 提醒）
    - skill 坑 12 的修复段落（升级后执行依据）
    两个地方不重复写——同段说明两处各贴一份。**升级 DSH 后第一时间**：跑一次 `session.create` → 复发就重新打注释；不复发说明 DSH 已修。

16. **workspace.json 坏工作区清理要全栈更新（2026-08-19 实测）**。修复 cwd 规范化后，磁盘上可能残留坏工作区（path=`C:\c\...` 这种）。**只删 `tables.workspaces[id]` 不够**——还要删 `global.workspaceIds` 数组里的 ID。DSH boot 校验严格：`WorkspaceRegistry.validateStoredState` 报 `registry order references missing workspace '<id>'` 直接拒绝启动。完整清理路径：
   1. 停 DSH web（kill node 进程）
   2. 备份 `~/.dsh/storages/workspace.json`
   3. 删 `tables.workspaces[bad_id]`
   4. 删 `global.workspaceIds` 数组里的 `bad_id`
   5. 写回 + 重启 DSH 验证
   6. **桥端到端跑一次**（`scripts/dsh_bridge.py run`）→ 新会话应归入正确工作区而非新建伪工作区
   `session_projcache.json`（199KB）也清——它可能藏着"已注册 Service"等过期缓存（虽然不是根因，但删了不亏）。

17. **turn/end reason.kind P0 洞——已修复 2026-08-19**。桥原本只数"有没有 turn/end 事件"不解析 `data.reason.kind`——导致 `aborted` / `interrupted` / `max-tokens` / `error` 全部被报 done。**已通过 ds `_turn_end_kind()` + `_TURN_END_KIND_TO_STATUS` 映射表修复**，BRIDGE_RESULT 新增 `turnEndReason` 字段携带原始 kind，6 个状态常量在位（单测 18 项全过：`reason.kind` 提取 + 状态映射 + 常量存在性）。今天 r2（产物没落盘被当完成）+ r3（30 秒中断被当完成转述）两个事故的**共同根因**已消除。

   **DSH 源码确认的 reason.kind 值域**（packages/core/session/src/types.ts 的TurnEndReasonMap）：`completed` / `aborted` / `blocked` / `max-tokens` / `error` / `interrupted`。`disposed` 是会话级销毁事件不进 turn/end——本节不涉及。

   **桥改法落地版**（scripts/dsh_bridge.py，已 commit）：
   - 状态常量区（第61-83行）：新增 4 个 `STATUS_MAX_TOKENS / STATUS_INTERRUPTED / STATUS_ABORTED / STATUS_BLOCKED` + 映射表 `_TURN_END_KIND_TO_STATUS` + 提取函数 `_turn_end_kind(event)`
   - 轮询判定（第481-494行）：取首个 turn/end 事件的 `data.reason.kind` 存 `end_kind`，缺 kind 也按 error 兜底，break 出循环
   - 收尾分支（第532-535行）：`completed=True` 时按 `end_kind` 映射状态，不再无脑 STATUS_DONE
   - `_finish` / `_emit`（第349-379行 / 第320-364行）：新增 `turn_end_reason` 参数透传到 `_log` 日志和 `BRIDGE_RESULT`；为 4 个新状态各补一行人读文案（aborted/interrupted/blocked 显式标"产物不可信"）

   **状态映射表**（已落地，DB 唯一来源：`dsh_bridge.py` 的 `_TURN_END_KIND_TO_STATUS`）：
   - `completed` → `done`（正常完成，进验收）
   - `max-tokens` → `max_tokens`（达到 token 上限，产物可能截断，验收必须数镜/数行）
   - `interrupted` → `interrupted`（崩溃孤儿回合被持久化层关闭，产物不可信）
   - `aborted` → `aborted`（取消请求打断，产物不可信，**不自动重试**）
   - `blocked` → `blocked`（被阻塞，等解除后同会话重投）
   - `error` → `error`（回合失败，瞬时重试，结构错误上报）
   - 缺失/未知 → `error`（兜底，事件不可信按最坏处理）
   - 无 turn/end（轮询超时）→ `timeout`（会话保留可续，**不带 turnEndReason**——此字段仅在已收到 turn/end 时填）

   **Hermes 端验收 gate 必须独立于 BRIDGE_RESULT**（2026-08-19 确立）：
   - `status=done` 只是触发器——接到后强制验产物文件：①路径存在 ②字节数 ≥ 契约下限 ③sentinel grep 命中
   - `turnEndReason` 非 completed 时直接判 verified_failed（即使产物文件存在也不当交付物，可抢救到 `partial/目录`保留）
   - 桥只负责"DSH 说自己完成"，产物对不对是 Hermes 的责任

   **续投决策树**（叠加在坑 10 之上）：
   - `completed` → 同 route 续投补全剩余 / 走验收
   - `aborted` → 不自动重试——abort 可能是有意中止，等人工确认
   - `interrupted` → 续投一次失败则 `force_new=True` 开干净新线（崩溃前内存状态不可知）
   - `max_tokens` → 同 route 续投"从 X 节继续"（产物可能部分可用，先抢救 partial 再续）
   - `blocked` → 排查工具权限 / preset 配置，**不续投**
   - `error` 中的瞬时类（传输/网络/busy）自动重试同 route；结构性错误（任务书非法/依赖缺失）上报不重试

18. **DSH 长回答 stdout 截断规律——必须强制落盘（2026-08-19 实测三次）**。桥返回的实时 stdout（DSH 在 turn 内的文本输出）在 Hermes 侧**稳定截到 1500-1700 字节**（`stdout_bytes_captured: 1488/1719/2588` 三次实测），DSH 长回答的后半段全丢。**桥的 stdout ≠ DSH 完整产物**——只能当"过程"线索，不能当"答案"交付。

   **硬约束**（何时必须强制落盘）：
   - DSH 任务书回答预计 > 1500 字节（典型：5 节方案 / 长代码段 / 完整提示词成品）
   - 任务是"DSH 给方案/成品/答案"而非"DSH 改文件"（改文件任务产物在磁盘，不需要走 stdout）
   - 用户明确要"看看 DSH 怎么想"（语义层面要拿到完整思考）

   **强制落盘姿势**（坑 9 的扩展——从"防 shell 改写"升级到"防 stdout 截断"）：
   - 任务书末尾写硬约束：「**这次任务的硬约束：必须调 write_file / create_file 工具把答案写到磁盘**，不能只在对话里说。文件路径：`X.md`」
   - DSH 写完后再在对话里回报文件路径 + 字节数（**DSH 自带 Test-Path/Get-Item 验证**）
   - Hermes 直接 `read_file` 读物理文件——不走 stdout，不依赖 history API

   **栈选择**：
   - 首选 `Temp/<任务线>_<日期>.md`——Hindsight 不入库，不污染 Vault
   - 次选 cwd 下 `<项目>/.dsh_polish/日期-场次.md`（坌子型任务）——任务产出归属项目
   - 避免 cwd 锚到 skills/hermes-agent 安装目录（沙箱写范围会把产物塞进系统资产目录）

19. **zstd 落盘机制——不能用字节数判 DSH 干活没（2026-08-19 DSH 源码核实）**。DSH session 持久化是事件日志，append 走软 flush——**只有 turn/end（回合结束）+ 会话销毁才是强制 commit 点**（`session-projection-cache` 源码注释：mandatory write points = turn/end and session disposal）。回合进行中的事件**只缓存在内存视图**（`session.history` API 能实时读到），磁盘 `session.jsonl.zstd` 只有上次 commit 的内容 + header frame。

   **直接后果**：
   - 看到 DSH 跑完 11 步推理但 zstd 只有 167B 是**正常行为**——回合没结束、未到强制 commit 点
   - 不能用 zstd 文件大小判断 DSH 干活没（今天我因此误判"DSH 落盘模块坏了"被打回）
   - `session.history` 在回合进行中可能 events=0（同上原因，未 commit 不进 history 列表）——**不是 RPC 接口坏了**
   - 判断 DSH 真活干了 = 看桥轨迹里的 `📥 任务:` 行（user/message 进内存视图了）+ `tool/call` 事件序列——**不要靠 zstd 字节数和 history events 数判活**

   **压缩比异常现象**：430KB zstd 解压只有 167B——DSH zstd stream 用了高重复 dictionary 编码，不是 bug，是高效存储。如果以后看到 zstd 文件解压远小于压缩前，**别当"DSH 丢数据"判**。

   **坑 17/18/19 共同根因（记到治理思路）**：桥把"DSH 说自己完成"当成了"DSH 真完成"——坑 17=不信完成质量；坑 18=不信对话输出；坑 19=不信磁盘内容。**Hermes 永远是验收者，不是转述者**。BRIDGE_RESULT 是 DSH 自评，不是 Hermes 给用户的交付。**任何 DSH 任务的最终交付必须独立验产物文件**——存在性 + 字节数 + 内容完整性 + 锁定项 + 不可删词。

   完整代码修复 / 状态映射表 / 续投决策树 / 栈选择表见 `references/turn-end-reason-and-stdout-truncation.md`。

20. **端到端测试 dsh_bridge 的 monkeypatch 必须改 `__dict__['rpc']`（2026-08-19 实测坑 4 个）**。给 `scripts/test_dsh_bridge_p0.py` 写姐妹测试 `test_dsh_bridge_p0_e2e.py` 时踩了 4 个坑（DSH 审查 M1 critical 的修复）：
    1. **monkeypatch 目标必须是 `br.__dict__['rpc']`**——`run_task` 内部裸调 `rpc(...)` 走 module global namespace，改 attribute 不触发裸调用。`assert br.__dict__['rpc'] is fake_rpc` 硬保证生效。
    2. **stateful fake 不依赖队列深度**——run_task 轮询 `session.history` 次数不确定（5-10 次），队列 pop 模式在第 5+ 次返回空 → 假 timeout。用 `hist_call_count = [0]` 状态计数：第 1 次返回空（base_evs，让 `last_seq=0`），第 2+ 次返回带 turn/end 的事件流。
    3. **`base_evs` 必须返回空 events**——`run_task` 第 481 行 `last_seq = max(seq in base_evs)`，如果 base_evs 含带 seq=N 的 turn/end，后续 `cur_new = [e for e in evs if seq > N]` 永远过滤掉 turn/end → 永久 timeout。
    4. **fake 必须返回解包后的 RPC schema**——`workspace.create` 返回 `val["workspace"]["workspaceId"]`（嵌套一层）；`session.history` 返回 `val["events"]`；`session.create` 返回 `val["sessionId"]`。**不要包 result 包装**——桥代码 `rpc(...).["xxx"]` 是直接索引，包 `{"result": {...}}` 会 KeyError。

    另外**`run_task` 不返回值**——所有信息走 stdout 末尾的 `BRIDGE_RESULT {json}` 行。测试用 `contextlib.redirect_stdout(buf)` + 解析 BRIDGE_RESULT JSON。

    **验收标准**：测试套件必须 7/7 全过 + 把代码回退到修复前测试必须红（S7 反证）。跑法：`python scripts/test_dsh_bridge_p0_e2e.py`（退出码 0 = 全过）。详细实现见 `references/turn-end-reason-and-stdout-truncation.md` "端到端测试的关键技巧" 节。

## 反向通道（DSH 提问 → 回到发起人所在渠道，「哪来的会哪去」）

**v3（2026-08-20 终态）：事件驱动 + 来源路由 + 原生回答通道**

**设计原则（用户拍板）**：DSH 会话有来源，提问就该回到来源去——谁发起的会话，DSH 缺料时问谁，不统一推到某个固定地方。原会话出，原会话进。

**架构（三件套）**：
1. **桥带来源元数据**：`dsh_bridge.py run --source desktop|feishu|cron --owner <open_id>` 写入 registry（`source` + `owner` 字段）。Hermes 在飞书会话派活时传 `--source feishu --owner <发起人 open_id>`；桌面派活传 `--source desktop`；cron 传 `--source cron`（cron 不涉及提问，路由表无此分支）。
2. **事件驱动监听器 `scripts/dsh_mux_listener.py`**（常驻，计划任务 `Hermes_DSH_Inbox_Watcher` 每 N 分钟 `--once` 保活）：
   - 连 `ws://127.0.0.1:8080/api/events.mux?token=<~/.dsh/.mux-token>`（mux-token 机制 8-19 打通）
   - 实时收 `question/requested` 帧（DSH agent 调 ask_user_question 的原生推送，apiproxy 推 mux 队列——api-proxy.ts:1363）
   - 查 registry 该 session 的 source/owner 路由：`feishu+owner → 飞书 DM 推给发起成员本人`（`--user-id ou_xxx`）；`feishu 无 owner → 妖玉 DM`；`desktop → 就地（web 弹窗已显示）仅留痕`；无 source → 按 cwd 回退
   - 收 `question/resolved` → 清理 pending
3. **原生回答通道**：成员回复 → `dsh_inbox_reply.py --sid <id> --pick N/--text` → **`POST /api/respond`**（ClientResponse 信封：`type='client-response'` + `rpcId` + `result.value{sessionId, answer.answers[{id, selected}]}`，api-proxy.ts:3633）→ DSH 继续。比 session.prompt 干净（rpcId 精确应答，answers 数必须等于 questions 数，selected 用选项 label）。

**respond 信封（实测锁定 2026-08-20）**：
```json
{"type": "client-response", "rpcId": "<echoed question rpcId>",
 "result": {"ok": true, "value": {"sessionId": "<sid>",
   "answer": {"answers": [{"id": "<question id>", "selected": ["<选项 label>"]}]}}}}
```
- HTTP body 就是 ClientResponse 本身（**不是**包在 payload 里；type 是 `client-response` 不是 `client-request`）
- 答案数必须 = 问题数；id = 提问时声明的 question id；selected = 选项 **label**（单选一个）
- 响应 `{"accepted": true}` = 成功；`not-pending` = 提问已过期；`bad-response` = 信封/schema 错

**事件驱动 vs 轮询/插件的取舍（用户拍板「哪来的会哪去」，2026-08-20）**：
- v1 轮询 watcher（dsh_inbox_watcher.py，文本启发式检测）与 v2 桌面插件（dsh-inbox 统一推桌面 toast）**均留档**（`desktop-plugins-archive/dsh-inbox`、脚本保留）
- 插件方案的根本错误：把「提问送到人面前」做成了「在桌面弹通知」——假设用户生活在桌面 app，而实际在 DSH web + 飞书；且单向无闭环（看到了还得回 web 答）
- 轮询的根源问题：skill 坑 14「DSH 没有真挂起提问协议，靠启发式检测」——漏检/误检/有延迟
- **事件驱动唯一正确**：原生帧即来即走；web GUI 会话天然不走 mux（前端 UI 就地弹窗，互不打扰）；cron 不提问无需处理

**验证（2026-08-20 实测全过）**：
- 桥带 source/owner 投递 → registry 记录 ✓
- DSH ask_user_question → events.mux 实时推 question/requested ✓
- 监听器按 owner 路由 → 真实推送到杨璇飞书 DM（`--user-id ou_7c8f...`）✓
- reply --pick → /api/respond → accepted:true → DSH 回复「已收到您的选择」→ turn/end completed ✓

16. **DSH 跑长任务时不要凭工程量大小 abort（2026-08-19 实测教训）**

**关键纪律**：DSH agent 在跑一个**改自己核心代码**的长任务时，**不要因为"工程量看起来太大"就 inject 停掉它**——它在改自己的核心模块（trust.ts、index.ts 等）跑 17+ 个 edit 是正常工作量。**用户视角**：DSH 改自己 = "它最了解怎么修自己"，让它跑完。

**触发场景**：
- 任务涉及 DSH 核心模块（trust / 协议 / 持久化 / 配置）
- 任务在 5-10 分钟还没完
- 工具调用计数 30+ 还在涨
- 已经改了 N 个相关文件

**反模式（亲历）**：
1. 用户："DSH 不是还在跑吗？" → 我意识到之前 inject 了 abort prompt 让 DSH 停
2. 当时我说"工程量太大（4-6小时）"想换 Hermes 主进程代理方案——**错误的工程量估计**
3. 实际 DSH 用了 ~13 分钟跑完 17+ edit，**真的写完了 mux-token 机制**，并且改完重启 DSH 端到端可用

**正确做法**：
1. 看到 DSH 长任务**不立即 abort**——先 poll `session.history` 看 tool_calls 增量、文件修改痕迹、step 数
2. **如果工具调用数稳定 + 文件改对了路径**（如 trust.ts / mux-token.ts 新建了）→ 信任它，**让它跑完**
3. **真正需要 abort 的信号**（不是工程量）：
   - DSH 陷入**重复 cycle**（同样 tool call 反复出现 N 次）
   - DSH 改的文件**和任务无关**（如在改 client/UI 而不是 connection/trust）
   - 用户**显式说停**（"停"是保留词）
4. abort 后**有损失**——DSH 已写的部分代码就丢失了，下次接 task 要重写

**对话原文（用户纠正）**：当时我说"abort → 工程量太大 → 换 A 方案"，你回 "DSH 不是还在跑吗？" —— 这一问让我意识到我**凭工程量判断而不看实际进度**。下次同类场景（"DSH 还在跑长任务，agent 觉得耗时太长"），先看 DSH 实际写到了哪一步再决定。

**何时仍然该 abort**：
- 用户说"停"（无条件的）
- 工具调用 cycle（同一 read/edit 循环 10+ 次）
- DSH 改的文件明显和任务不相关（如改桌面 app 而不是 trust.ts）
- DSH 输出明确说"做不动/有 blocker"

## 完整修复路线（DSH 融合解耦后重新接入的 8 步）

> 2026-08-19 实测路线。DSH 解耦后（commit 238d139）如果需要恢复默认引擎铁律，
> 完整 8 步（每步都可能独立失败，按顺序排查）：

1. **恢复桥 + 看门狗**：`git show 238d139^:scripts/dsh_bridge.py` + `:scripts/dsh_watchdog.py` 反向捞回
2. **恢复 .hermes.md DSH 铁律 + 收尾六面**（DSH 会话 close 挪回 skill）
3. **修 cordis 双重注册根因 A**（skill-filesystem 23 行）—— 不修 session.create 直接报 agent-preset-invalid
4. **修 cordis 双重注册根因 B**（tool-cordis 注释）—— 重启后才会触发
5. **修桥 cwd 规范化**（见 pitfall 13）—— 不修 session 落伪工作区
6. **重建 DSH_Watchdog 计划任务**为每5分钟（解耦期可能被改 One Time Only + Disabled）
7. **挂 hermes-dsh-fusion skill 到分析类 cron**（hermes cron edit `<job_id>` --add-skill hermes-dsh-fusion，不是 update——update 不存在）
8. **从 Obsidian 还原分析/ 目录 + 建 Hermes_DSH_Inbox_Watcher 计划任务**（git 历史不一定全；commit message 列了 3 份但实际只 1 份进 git——git 历史是工作产物的辅助，Obsidian 才是）
   额外：建 `Hermes_DSH_Inbox_Watcher` 计划任务（每分钟跑 `scripts/dsh_inbox_watcher.py`）——反向通道监听器

**端到端验证**：`scripts/dsh_bridge.py run "<cwd>" "hi" --route verify-fusion` → DSH 回 "hi" + BRIDGE_RESULT status=done + 复用同 sessionId（reused:true）。