---
name: hermes-dsh-fusion
description: DSH 融合执行——**任何涉及 DSH 的任务**（跑长任务/批量/调研 DSH 插件与生态/推荐/分析/评估）默认走桥驱动；收到任务先按「默认用 DSH」判据决策，命中自干判据才自己干。触发词：DSH、插件推荐、生态调研。
whenToUse: 默认全部场景考虑 DSH 引擎参与——工程执行/创作推敲/协作起草/渠道辅助/调研分析/插件评估推荐；**用户点名 DSH 或任务涉及 DSH 相关话题时必用**
version: 0.3.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [DSH, DeepSeek-Harness, 融合, 执行引擎, 批量任务, 调研]
    related_skills: [hermes-workspace-conventions]
---

# Hermes × DSH 无感融合

**原则：不是"外包"，是一个增强的 Hermes。** 用户在 Hermes 里说话，Hermes 判断怎么干——适合 DSH 执行形态的活自动落到 DSH（其会话 cwd 长在 Hermes 项目目录，规范/知识/资产天然同源），思考链路回流 Hermes 对话流，用户在对话里看到完整推理过程，无从感知也不需感知"这是 DSH 干的"。

**默认策略：默认用 DSH，失败自动降级。** 收到任务先默认考虑 DSH 引擎参与（全部场景开放，没有禁区）。**降级护栏**：桥不可用/首次调用报错 → 自动降级 Hermes 本机执行，不阻塞用户，并在回复里说明一句（不夸大、不掩饰）。用户不需要点名"用 DSH"——默认就在用。

## When to Use

- **默认：全部场景开放。** 收到任务默认考虑 DSH 引擎参与——工程执行（长任务/批量/文件/分析/脚本）+ 创作推敲（剧本/歌词/分镜，DSH 读知识库+项目文档参与） + 协作起草（回复/文档，DSH 起草或审读）+ 渠道辅助（简报生成/记忆整理，DSH 产出 Hermes 落库）
- 用户点名「用 DSH」
- 唯一保留：渠道工具的**最终执行**（飞书发送、cron 调度、Hindsight 写入、MCP 配置）由 Hermes 完成——DSH 没有这些渠道工具；但能力输出（起草/分析/审读/生成）可以来自 DSH

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
6. **Windows 路径**：cwd 用 `C:\...` 格式（桥接受），DSH 内工具用 pwsh（PowerShell 语法）
7. **别续"上次超时未收尾"的旧线程**：可能再次等待——换线时用 --new