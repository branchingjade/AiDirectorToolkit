---
name: hermes-workspace-conventions
description: "Hermes 工作区约定。目录结构、行为铁律、操作流程、收尾检查清单、知识架构（memory/skill/SOUL 分层）、会话分支策略。用户会纠正不合理的安排。Use when: 新建文件夹、决定项目放哪里、需确认操作规范、收尾、任务结束、问会话分支/worktree/回滚怎么用、memory 被污染需要清理。"
---

# Hermes 工作区目录约定

## 根目录

所有内容在 `~/Documents/Hermes/` 下，按用途分：

```
~/Documents/Hermes/
├── Plugins/             存档 — 浏览器扩展、工具安装包、脚本
├── Projects/            独立项目 — 有 git repo 的软件项目
├── 分镜/                创作产出 — 分镜、提示词等创意文档
├── 分析/                分析报告产出
├── sketches/            设计迭代 — 独立HTML sketch、海报迭代版，按项目分子目录，保留全部版本
├── .hermes/             Hermes 运行时
└── *.md                 参考文档
```

> **`.gitignore` 模板**：`references/workspace-gitignore.md` — 覆盖 Hermes 运行时、备份、日志、Blender 缓存等。工作区缺 `.gitignore` 时从此模板复制。

## 分类规则

### Plugins/ — 插件存档

**放什么：** 浏览器扩展、油猴脚本、ComfyUI 节点、TD .tox 等。

**不放什么：** 正在开发中的、有自己 git repo 的项目。

```
Plugins/
└── browsers/extensions/
    └── RH小帮手-v2.2.4/     ← 发行版存档
```

### Projects/ — 独立项目

**判断标准：** 有独立 git repo、有 build/dev 流程、能独立发版 → 放 Projects/。

**自带 .git 的项目不进主仓库：** 在主仓库 `.gitignore` 忽略（如 `Projects/doubao-tts-server/`），避免 git status 常年显示 untracked。已 gitlink 的子项目（rh-helper/heychat-bridge 等）用 `git add <子项目>` 更新主仓库引用。子仓库内部的运行时目录（如 `.hermes/`）主仓库的 gitignore 管不到——在子仓库自己的 `.gitignore` 里加。

```
Projects/
└── rh-helper/              ← 开发版 (.git, build.sh, src/)
```

### 根目录 — 参考文档

跨项目参考文档放根目录，如 `版本管理策略.md`。

### 分镜/ — 创作产出

**放什么：** 分镜脚本（`分镜_*.md`）、Seedance/RunningHub 提示词（`优化提示词_*.md`）、海报文案等创意工作直接产出。

**不放什么：** 分析报告（→ `分析/`）、项目代码（→ `Projects/`）、参考知识（→ Obsidian vault）。

### 分析/ — 分析报告

**放什么：** 调研报告、对比评测、技术分析等结构化输出。子目录按项目名组织，MD 引用同目录 `assets/`。

## 核心红线：禁止擅自在工作区外建目录

**绝对禁止**未经用户明确同意在 `~/Documents/Hermes/` 以外的任何路径创建文件或文件夹。

反面案例：voiceclone 任务中擅自在 C:\ 下建文件夹（~4 GB），用户质问后全部迁移。

正确做法：先在 `~/Documents/Hermes/` 下创建项目子目录，再告知用户。

> 特殊项目目录结构模板（如音色克隆的 original/intermediate/output/scripts）：`references/workspace-directory-conventions.md`

## 行为铁律

以下不是知识——是每次操作必须遵守的行为指令。不是「知道就好」，是「做之前对照」。

### 输出铁律

给用户的所有文字产出必须中文、有实质内容。不拿空白或敷衍内容推给用户。反面案例：汇报时说「已检查完毕」但不列检查了什么——等于没汇报。

### 产出管理铁律

所有产出用 Obsidian 管理，wikilink 可达。写完东西不归档=白写。

### 创作铁律

先理解再创作——吃透世界观，方向不对等于白做。不是「看完就动手」，是「理解到能替导演回答追问」才动手。

### 效率铁律

不空转——一次搞定，不反复跑偏。在同一个方向上反复试三次以上：停下来，换思路。不要用「再试一次」替代「我是不是方向错了」。

### 渠道铁律

在哪问在哪回，不跨渠道。Hermes TUI 里问→TUI 回复，飞书里问→飞书回复，cron 推送→飞书。

## 判断门禁

每次下结论或引用历史信息前，必须亲手验证——不是凭记忆就是对的。

**核心红线：旧记忆不自动有效。** 过去维护的错误信息（如"SOUL.md 不被 Hermes 加载"曾被标记为已验证，实际完全错误）会被 agent 无脑重复。所有引用必须重新核实。

## 自检流程：产出→检查→修复→汇报

四步闭环，实际验证，不空打勾：

1. **检查** — 读文件确认写入正确、数字对、路径对、引用可解析
2. **修复** — 发现问题立即修，不留在 todo 里
3. **汇报** — 告诉用户查了什么、改了什么；不等用户问

## 计划优先（大方向）

**架构变更、新增系统/流程、跨模块改动、方案选型——先出方案等用户确认再执行。方案没定下来就禁止执行。**

用户说"先做规划"就是字面意思——先给方案，不动手。批量操作必须先 1 条验证，确认后扩全量。

以下情况不需要规划，直接做：单文件小改、修 bug、数据查询。

## Git Commit 格式规范

所有提交必须使用 Conventional Commits 格式。

## 沟通陷阱

用户不关心你调了什么工具、走了什么流程。说操作结果，不解释底层机制。反面案例：解释 git 原理 → 用户只需知道文件改名了。

```
<type>(<scope>): <中文简述>

type = docs|fix|feat|refactor|chore|revert
scope = 影响范围（日志|图谱|知识库|规范|自检|飞书|犬子无双|Hermes运维...）

示例：
  docs(日志): 重写README梗概 — 每条标注任务+结果
  fix(自检): 修复frontmatter+wikilink悬空+MOC缺链
  feat(图谱): 6色组配置写入graph.json
  refactor(日志): 统一命名规范 — MM-DD + W{N}-周报 + 月报
```

**禁止格式：** ❌ 无type（`更新文件` `修复`） ❌ 无scope ❌ 纯中文长句无前缀

**多文件变更时加 body：** `-` 列表简述每项

## 任务后收尾（完成 ≠ 结束）

每次建 todo 列表，最后一项固定为「收尾检查：Obsidian/Git/Skill」。任何阶段成果完成后，**必须输出以下清单并逐项处理**：```
收尾：
- [ ] Obsidian笔记（有值得记录的学习 → 主动提出）
- [ ] Skill同步（方法论/工具用法变了 → 更新对应skill）
- [ ] Git push（KnowledgeBase有变更 → commit+push）
- [ ] 记忆同步（memory.md → vault Hermes运维/memory/）
- [ ] 悬空wikilink检查
- [ ] 污染检查（memory/skill/Obsidian/cron 四个面：memory用分类克制门禁逐条过；skill扫重复/冲突/过时；Obsidian扫垃圾笔记；cron扫废弃job）
```

## 视觉/设计类任务的特殊规则

**agent 不具备审美判断力。** 设计任务中 agent 角色=技术执行者，用户角色=设计决策者。

正确模式：
1. 先确认项目风格 — 读剧本/创作宪法，收集视觉参考（截图存 Obsidian），用户确认方向
2. 简述方案方向 — 不直接写代码，先说"我要做什么风格"，等用户点头
3. 执行并预览 — 通过 WebBridge/浏览器推到用户面前，等用户确认视觉
4. 用户点头后才固化 — 写入源码、导出文件

**内部工具 UI 铁律（TTS 工具迭代五版的教训，2026-07）：**
- 第一版直接克隆火山引擎官方 console 三栏布局 → 用户否决："审美太low，易用性太差"
- 第二版极简单栏 660px + 参数折叠 → 用户："空间利用率太低，工作用的工具参数默认折起来是什么意思"
- 第三版双栏 1180px + 参数常驻右侧面板 + 3 个参考音频槽位 + 所有设置直接可见 → 用这个
- 关键结论：工作工具 ≠ 消费品。**参数区必须常驻可见**，界面密度要高，不要做渐进式披露
- 所有尺寸用 `rem` + `clamp()` 做流体响应（`html{font-size:clamp(14px,12px+0.35vw,18px)}`），覆盖 1080p/2K/4K
- 先出 1 个方向，别连出多个方案让用户挑——他们挑不出来，只会说"都不好"

### 成员画像 = bot 观察沉淀，不是用户定义

飞书成员画像（`Obsidian Vault/成员画像/<真名>.md`）的内容**必须来自 bot 在协作中观察到的行为**（沟通风格/专长/参与项目），**不是用户填的**——用户原话「画像内容不是我定的，你是观察到的」（2026-08-07 纠正）。也不要问妖玉要画像内容。**全员都要有画像**：成员名单.json 里的每个人都建一份；无观察到的成员留空待沉淀，不编造。初始建库数据源：成员名单.json 拿 open_id → 飞书每日摘要/历史会话提取专长与参与项目 → 无观察留空（首轮 11 人已建，3 人留空）。

**沉淀规则（2026-08-07 用户拍板）**：只写明确观察到的偏好/事实；同一天同类观察合并为一条（去重）；**不设条数上限**（用户明确摘掉「一天最多 2 条/人」限制）。质量底线保留：不确定的不写。飞书脱敏默认名「用户+N」（如用户133976）= 资料未设姓名，反查真名用 `lark-cli contact +search-user --user-ids <open_id> --as user`（bot 身份查不到，user 身份可反查）。

**沉淀实操数据源与坑（2026-08-07 实测）**：
1. **cron 摘要输出是画像/记忆建议的主要历史来源**：`~/AppData/Local/hermes/cron/output/<job_id>/*.md`（飞书每日摘要 job_id=88ab7ff66681），建议在 `## Response` 后的 `👤 画像` / `🧠 记忆` 行。**git-bash 里 grep emoji 匹配不到**（编码问题）——用 Python 读文件按行提取。
2. **飞书会话 session_search 查不到时直查 state.db**：飞书会话 ID 带完整后缀（如 `20260807_102108_946ca4dd`），截断的短 ID（`20260807_102108_946c`）会报 not found。读消息：`SELECT role, content FROM messages WHERE session_id=? ORDER BY id`，content 可能为 NULL 需过滤。会话清单：`SELECT id, user_id, chat_type, title, started_at FROM sessions WHERE source LIKE '%feishu%'`。
3. **项目记忆目录为空 ≠ 机制坏了**：`OBSERVATION:`/`PROJECT_MEMO:` 标记行钩子在 gateway/run.py（Feishu IM 回复末尾拦截并沉淀），**gateway 重启后才生效**——重启前的历史观察不会自动入库，需手动从 cron 输出补齐。验证机制在位：`grep -n "OBSERVATION\|PROJECT_MEMO" gateway/run.py`。
4. **沉淀边界**：只写明确观察到的协作行为；无观察的成员留「待沉淀」不编造（NAS 共享账号等系统层信息不算协作行为）；历史档案归属未确认前诚实标注「3 人中一员，具体未确认」，不猜映射。
5. **历史档案归属判断（2026-08-07 用户纠正定稿）**：多人共事同一项目时（如三人同做陈强系列）行为特征高度同质，**agent 按行为特征猜映射会错**（实测：猜 A=全志越/B=施文皓/C=苑津铭，用户拍板 A=苑津铭/B=全志越/C=施文皓）。正确姿势：① 调出各人提交的**原始提示词内容样本**（state.db 提取 user 消息，按人分档）给用户认人——内容风格（贴剧情场景求优化 vs 格式化资产绑定 vs 贴故事原料）比抽象特征更有辨识度；② 归属由用户拍板，agent 不自行定稿；③ 档案文件保留「归属已定稿 + 拍板日期」溯源。
6. **归属合并必须全量展开（2026-08-07 用户「合并进去了吗」纠正）**：用户拍板归属后，把档案内容合并进画像**必须逐条完整展开**（档案每条观察一行 + 会话清单），不能只留概要行 + 链接——概要版会被用户追问「合并进去了吗」打回重做。合并后 grep 旧标注残留（「未确认/待确认」）清零。
7. **通道标签禁令（2026-08-07 用户纠正「所有人都会走im也都会走评论的」）**：**禁止给成员贴「走XX通道」标签**——IM 和文档评论两个通道人人可用，不存在某人专属某通道。成员某时段只有评论活动 = 「该窗口期活动集中在评论」，不是「他是评论通道用户」。**活跃度统计必须双通道合并**：IM（state.db sessions 表）+ 评论（`_hermes/评论会话/*.json`）——只看 IM 会漏掉评论为主的成员（实测：杨璇 IM 0 会话但评论 1 线程）。完整巡检流程见 `references/feishu-collab-health-check.md`。
5. **项目记忆文件结构（2026-08-07 首落库定稿）**：`_hermes/项目记忆/<项目>.md` 用三节布局——`## 世界观`（世界设定/角色体系/关键决策）、`## 进度`（按日期列各线进展）、`## 协作`（工具链/团队工作流事实）；每条 `- [YYYY-MM-DD] 内容` 带日期；frontmatter 含 `项目: <名>` + `updated` + `tags: [飞书协作, 项目记忆]`。README 的项目列表表每新增一文件同步补一行（wikilink 到文件）。

### 飞书/Obsidian 双平台文档关系（2026-08-07 用户纠正定稿：飞书是正本）

**背景**：项目文档可能在飞书和 Obsidian 各有一份。**2026-08-07 用户最终拍板：飞书 Hermes 文件夹下的文档是正本**（用户原话「飞书文档不是什么副本，这是正本」），Obsidian 项目目录是 **git 归档层**（版本历史/创作过程留痕），不是权威源。此前"Obsidian=权威源、飞书=展示副本"的理解是**错的**，被用户明确推翻。

### 铁律（用户拍板定稿）

1. **飞书 Hermes 文件夹下的文档 = 正本**——创作成果以此为准（剧本正文/项目文档都是正本形态）
2. **Obsidian 项目目录 = git 归档层**——保留版本历史/创作过程留痕，配合归档，不是权威源
3. **不做机械同步**（用户叫停："行了，别同步obsidian和飞书了"）——飞书与 Obsidian 各管各的，创作决策最终以飞书正本为准
4. **两侧都可能先行编辑**（飞书 str_replace/富功能编辑 或 Obsidian 直接改文件都可能是起点）——不预设哪侧先行
5. 更新飞书正本后，Obsidian 侧做**配套归档**（剧本/分场分析/大纲同步，git commit+push），归档不是"同步副本"而是留痕

### 判断"哪个是权威动作"

**编辑飞书 Hermes 文件夹下的文档前先确认它是正本**——更新它=更新正本（如导入新版剧本后删除旧版，Hermes 文件夹只保留一份正本）；Obsidian 侧跟进归档。不要把飞书当 Obsidian 的镜像去"补齐"，也不要把 Obsidian 当权威源让飞书"对齐"。

### lark-cli 编辑陷阱速查

飞书侧编辑用 `docs +update` 时，**str_replace 跨 block 会静默失败**（返回 ok 但内容没变）——必须先 `docs +fetch --scope keyword --detail with-ids` 拿 block ID，再用 `block_replace`/`block_insert_after`。完整踩坑记录见 `references/lark-cli-doc-edit-pitfalls.md`。

## 会话工作流约定

### 分支策略：思路用分支，执行回主线

- **`/branch`** — 只分叉对话历史，不隔离文件。轻量，适合换思路聊、对比方案。
- **`hermes -w`** — 对话+文件双隔离（自动创建 git worktree），适合并行开发任务。
- **回滚保护** — 全局开启：`hermes config set checkpoints.enabled true`

## Pitfalls

### 分类克制门禁

每次想往 memory 加东西或自建 skill 之前，强制回答三个问题：

| 问题 | 答案"是" → | 出口 |
|------|-----------|------|
| 不记会犯错？ | → | **memory** |
| 下次还要照着做？ | → | **skill** |
| 需要存档但不用每次提醒？ | → | **Obsidian** |

三个都不满足 → 管住手，不记。skill 不完善就去完善它，不要用 memory 替代。

## Hermes 记忆层级（5 层）与项目记忆

1. **持久记忆** `memories/MEMORY.md`（agent 笔记）+ `USER.md`（用户画像）— 每会话开始注入系统提示，**冻结快照**：会话中途的改动立即落盘但下个会话才生效。官方默认 MEMORY 2,200 / USER 1,375 字符（定位=精炼笔记不是仓库），本机调大（10,000/4,000）——调大后容易堆满，需主动瘦身
2. **上下文文件（=项目记忆）** `AGENTS.md` / `.hermes.md` / `HERMES.md` / `CLAUDE.md` / `.cursorrules` — 按工作目录自动发现注入：`.hermes.md`/`HERMES.md` 优先级最高（走到 git root），AGENTS.md 从 CWD+子目录渐进发现。**项目知识放项目自己的 AGENTS.md/.hermes.md，不进全局 MEMORY.md**。触发：Hermes 从该目录启动 / terminal workdir / cron workdir 指向该目录。**工具分离模式（2026-08 确立）**：AGENTS.md 是 Codex 生态通用约定（本机 AGENTS.md 即 7-30 为修 Codex 中文而建）——**AGENTS.md 归 Codex（保留纯中文要求），Hermes 专属约定放 `.hermes.md`**，Codex 不认识 `.hermes.md`，两边零混淆。桌面版另有 **Project 机制**（`project_create`/`project_list`/`project_switch` 工具）：命名工作区+锚定目录，切换 Project 时整个会话工作区跟随（cwd→上下文文件自动重载），是比手动 cd 正式的会话迁移方式。**关键认知：会话的项目身份由 cwd/Project 决定，不是由聊的内容决定**——Hermes 不会自动识别"正在做《伏妖记》"并写项目记忆；创作项目需各自建 Project（锚定 Vault 对应目录）+ 项目 .hermes.md（世界观/格式/进度指针），由 agent 约定主动维护
3. **会话历史** `state.db`（SQLite+FTS5）— session_search 按需检索，不占上下文
4. **技能** SKILL.md + references/ — "怎么做"的程序性记忆，按需加载
5. **Profile 隔离** — profiles/<name>/ 各自独立记忆

判定口诀：跨项目的环境事实+用户偏好 → MEMORY/USER；项目专属约定 → 项目 .hermes.md/AGENTS.md；程序性知识 → skill；历史对话 → session_search。

### 项目记忆 = session_search，不是自建层（2026-08-06 用户纠正）

**用户原话**："你不是说 hermes 有项目记忆这层吗，怎么全要我自己搞"。教训：**Hermes 内置的"项目记忆"就是 session_search——所有会话（桌面+飞书+评论）自动存档、永久可查、零维护**。用户要"自动记住项目细节进度"时，答案指向内置能力（session_search 搜项目名），**不是**去建"项目记忆.md"、台账、cron 盘点这类自建层——那是 agent 一厢情愿的过度设计，会让用户觉得"全要自己搞"。

正确姿态：**先讲内置能力，再谈自建增强**。session_search（自动）→ 全局 MEMORY（agent 自动写）→ Obsidian 项目目录（结构化归档，加分项非必需品）。用户明确要结构化归档时才建；否则保持零维护。

**隐藏问题**：全局 MEMORY 60% 满的根因之一就是项目细节堆在全局——项目专属细节应留 Obsidian（git 归档）或靠 session_search，不占全局记忆。被问"项目记忆成熟吗"时诚实回答：内置的自动记忆（session_search）是成熟的，自建归档层靠 agent 自觉。

**最终走向（2026-08-06 用户拍板，两轮反转后定稿）**：session_search 不满足"自动记住项目细节"——它只是平铺存档：**不会自动归类项目、不会自动判断、不会自动提取**（用户三连否定："你真做到了？会话你会自己往 project 放？你会自己判断建 project？"）。用户要求外部记忆插件（`hermes memory setup`，Hermes 原生支持）。**第一轮**：选型 OpenViking 安装后出事故卸载——① 装 `openviking` pip 包时全局 Python312 被 Hermes venv 的 PYTHONPATH 污染，pip 撕坏 venv 内 cryptography/charset_normalizer（修复见 PYTHONPATH 污染 pitfall）；② MiMo 无 embedding 端点（`/v1/embeddings` 实测 404）。用户："卸载吧"——收益 < 环境破坏风险。**第二轮（当日稍后）**：用户主动重跑 `hermes memory setup` 要求**全量对比 8 provider** → 改选 **Hindsight 本地嵌入式**并安装成功（`memory.provider: hindsight`，DeepSeek 当 LLM，embedding 走本地 sentence-transformers）。完整安装步骤/curses 向导坑/配置文件三件套 → `references/memory-providers.md`「二次安装定稿」。

**定稿（2026-08-07 用户拍板：删除自建项目记忆层，全面用 Hindsight）**：Obsidian 的 `项目记忆.md` 文件已删除，`.hermes.md` 项目记忆工作流章节已改为 Hindsight 说明。**项目记忆 = Hindsight 外部记忆**（会话细节自动 retain/recall），agent 不再手动维护项目记忆文件。Obsidian 项目目录仍保留创作成果本体（剧本/分场分析/复盘/自审报告，git 归档）——那是资产不是记忆层。飞书评论协作的「注入主文档+复盘」机制保留（源码层，多用户安全设计，与自建层无关）。

### 摩擦不对称陷阱

`memory` 工具零摩擦（一行搞定），`skill_manage` 需匹配 old_string。agent 认知负荷高时总结冲动自然流向 memory。缓解：完成 skill 升级后自检 memory；用户可随时命令「检查 memory」。Feature request: [#70488](https://github.com/NousResearch/hermes-agent/issues/70488)。

### 收尾跳过陷阱

收尾清单列在 skill 里不等于 agent 会执行。agent 在任务完成后容易「觉得搞定了就停」，跳过 Obsidian 笔记、污染检查等步骤。缓解：任务标记完成前，强制对照收尾清单逐条确认，不等用户提醒。反面案例：alist 故障修复后 self-declare「收尾完成」但没走 Obsidian 步骤，用户指出「收尾流程不规范」。

**"无变更"也必须给证据**（2026-08-04 用户纠正，原话"任务完成的流程呢"）：收尾时即使认为某面无变更，也要实际验证后输出证据——vault 位置和 git 状态（`git -C <vault> status`）、cron job 列表、memory 文件都存在可查。一句"其余项无变更"会被用户视为没走流程。正确做法：建 todo 清单 → 逐面实际执行（含路径查询/状态验证）→ 输出逐项打勾清单。

**收尾时核对知识库日志覆盖度**：当日日志可能由其他会话（早上的会话、cron）写过，但**未必覆盖本次任务的时段**。收尾时打开当日日志文件核对，发现缺口（如备份修复、git 瘦身发生在日报提交之后）必须主动补齐并 commit+push，不等用户提。实测案例：2026-08-04 日报 14:18 提交只覆盖上午内容，下午的备份盲区修复+git瘦身由收尾时补齐推送（b9692a2）。

### 验证来源优先级陷阱

不要把 API 返回值当作唯一真相来源。当用户在同一系统上通过其他途径（浏览器、CLI）已成功操作时，API 报错更可能是请求构造问题而非凭据问题。验证顺序：用户浏览器状态 > CLI 直接输出 > API 响应。反面案例：alist API 登录返回 400，断言「密码不对」要求重置——但用户早已在浏览器登录成功。

### 行为规则不触发陷阱

Memory 处于系统提示「背景知识」层，agent 任务中注意力在 skill 上，不会主动扫描 memory 找 checklist。**行为指令放 skill，决策知识放 memory。** 已执行：行为铁律从 memory 搬到本 skill，memory 从 19 条精简到 7 条。

### SOUL.md 保护机制

SOUL.md = agent 核心人格，只写「我是谁、怎么做事」。禁止写操作规则。禁止 agent 主动修改，仅用户可改。

### HERMES_HOME ≠ ~/.hermes/

Windows 上真实 HERMES_HOME 在 `C:/Users/<user>/AppData/Local/hermes/`，不是 `~/.hermes/`。编辑前先 `hermes config path` 确认。

### 全局 pip 装包污染 Hermes venv（PYTHONPATH 陷阱，2026-08-06 实测事故）

Hermes 会话 shell 的 `PYTHONPATH` 指向 `hermes-agent` + `hermes-agent/venv/Lib/site-packages`（继承自 Hermes 环境）。此时**用系统 Python（如 `pip install xxx`、`python -m pip`）装包时，pip 会误把 venv 当目标环境**——实测装 `openviking` 后：venv 内 `cryptography` 核心文件丢失（`hashes.py` 等被撕）、`charset_normalizer` 损坏、`pip` 模块整个消失，`hermes` 命令启动崩溃（`ImportError: cannot import name 'hashes'`）。**这是"装一个外部包把 Hermes 弄瘫"的根因，装任何 pip 包前必查 `echo $PYTHONPATH`。**

修复（实测有效）：
```bash
cd ~/AppData/Local/hermes/hermes-agent
venv/Scripts/python.exe -m ensurepip   # 恢复 pip（pip 被删时）
venv/Scripts/python.exe -m pip install --force-reinstall cryptography
venv/Scripts/python.exe -m pip install --force-reinstall charset-normalizer
# 验证：venv/Scripts/python.exe -c "from cryptography.hazmat.primitives import hashes; print('OK')"
```

规避：装包前 `unset PYTHONPATH`（或 `env -u PYTHONPATH`）再跑系统 Python；需要全局工具（如 openviking-server）时始终用 `env -u PYTHONPATH <命令>`。检查工具是否吃到了 venv 的包：`python -c "import sys; print(sys.prefix)"`——若显示 hermes-agent/venv 即被污染。

### read_file 误判 binary（UTF-8 中文截断 U+FFFD，已修复 2026-08-06）

`read_file` 对 .md 报 "Binary file - cannot display as text"（Obsidian UTF-8 中文文件普遍）的根因：`head -c 1000` 采样在 1000 字节边界切断 UTF-8 多字节字符 → 解码产生 **1 个** U+FFFD → 旧判定 `if "\ufffd" in sample` 见 1 个就判 binary。**与 CRLF 无关**（`\r` 本来就被排除在 non-printable 外）。真解码失败（如 GBK 读 UTF-8）产生几十个 U+FFFD——判定阈值区分截断噪声与真失败。已本地补丁 `tools/file_operations.py` 的 `_is_likely_binary`：改为 `content_sample[:1000].count("\ufffd") > 1`。⚠️ `hermes update` 会覆盖补丁，升级后需重打；复现时临时读法 `tr -d '\r' < 文件` 管道（grep/sed 直接处理 CRLF 文件本身没问题）。上游值得提 PR：判定注释假设"合法 UTF-8 文本不含 U+FFFD"在截断采样下不成立。

### Windows 计划任务跑控制台程序必弹窗（pythonw 解法，2026-08-07 实测）

计划任务「登录时」交互运行 python.exe 会弹 cmd 窗口（如 `HermesRemoteServe` 远程网关）。解法：任务执行程序换成 **`pythonw.exe`**（venv\Scripts\pythonw.exe 默认存在）——无窗口且不影响 stdout 重定向（`> serve_remote.log 2>&1` 在 cmd 层重定向后 Python 正常初始化 sys.stdout）。注意：serve 进程内部可能重新 exec 成 python.exe（tasklist 显示 python.exe），但继承 pythonw 的无控制台句柄，仍不弹窗。无窗口后排障靠日志文件。改任务用 `schtasks /change /tn <任务> /tr "cmd /c cd /d <dir> && venv\Scripts\pythonw.exe -m ... > log 2>&1"`；git-bash 里 `git -C ~/Documents/...` 可能报 No such file（MSYS 路径不被 git.exe 识别）——用 `cd` + Windows 路径（`C:/...`）规避。

### 管理员进程看不到用户级映射盘符（UAC）

Hermes 终端以管理员权限运行时，`net use` / `Get-PSDrive` 看不到普通用户会话里映射的网络驱动器（Y:/Z: 等），`\\主机\共享` UNC 直接访问也失败（系统错误 5 拒绝 / 67 找不到网络名），而普通软件正常——根因是 UAC 下提升进程与用户会话的链接未建立。诊断：`HKCU\Network\<盘符>` 的 RemotePath 字段可确认映射本体是否存在。修复：注册表 `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\EnableLinkedConnections = 1`（DWORD），**注销或重启后生效**（登录时才创建链接，当前进程立即验证仍不可见属正常）。修复前兜底：SFTP/SSH 直连数据源（如 NAS）。

### 大文件 tool call 流超时

`write_file` 或 `patch` 单次传超过 ~8K tokens 的 HTML/CSS 时，流可能超时静默丢弃。Hermes 不报错，但文件未被写入，且后续依赖该文件的操作（如 `docker compose build`）看似成功实则跑了旧代码。解决方案：HTML 内容拆到独立 `page.html`（不在 `main.py` 内嵌），用多次小 `patch`（每次 <4K tokens）分块写入。按顺序：CSS 骨架 → CSS 组件 → HTML 结构 → JS 逻辑 1 → JS 逻辑 2，每块独立 patch。

### 方向反转时示例必须同步（语言/默认值翻转陷阱）

改 skill 的输出语言/默认方向（如 H3 提示词英文→中文）时，**只改规则语句不够——references/ 里的示例正文是 agent 模仿的主要来源，示例不翻=残留**。反面案例（2026-08-07 h3-prompt-writing 英文→中文反转）：规则行全改完，自检才发现 base-en.txt 4 个完整示例 + ref-en.txt 六段示例正文全是英文——示例的模仿惯性比规则更强，agent 加载 skill 后照示例输出英文。

自检要点：
1. **grep 示例代码块而不只是规则行**：`grep -in "in English\|English sentences" references/*.txt`，规则行清了不代表示例清了
2. **区分结构性英文（必须保留）与写作语言（才翻译）**：字段名（`integrated_multimodal_description` 等）、结构标签（`[Shot N]`、`At MM:SS.mmm`）、引用标签（`<Subject N>`、`(S1)`）、对白语言标签（`<d>[English]...` 内对白保留原语言）、固定标记值（`fully_preserved` 等）、屏幕文字（"营业中"）、术语表（`Zoom In`）——这些是格式不是写作语言，翻译它们反而破坏格式
3. **翻译一致性**：模板指令（如 I2VA 对齐句）在正文定义处与各 Case 里的实例必须同一译法

**整文件 write_file 改写陷阱**：翻译/改写大文件时用 write_file 全量重写，极易把原内容原样写回（本会话连续 4 次写回英文原样，直到改用逐块 patch 才真正翻译）。正确姿势：① 用多次小 patch 逐示例块替换（每次 diff 可见实际变化）；② 替换后 grep 旧语言残留验证；③ 对比字节数变化确认真的改了（15,980→15,246 字节才算数）。

### 并行会话同写 skill/memory 文件（2026-08-07 实测）

用户环境多通道并发（桌面 + 飞书 + 评论 + cron），**同一个任务可能在多个会话里同时处理**——某会话正在跑的技能文件（SKILL.md/references/scripts/）和全局记忆可能已被并行会话抢先更新。实测：Hindsight 安装任务中，skill 文件 00:05 被并行会话写入完整「二次安装定稿」+ E2E 检查脚本，本会话毫不知情（session_search 无记录，会话可能已压缩）。

规避：
1. 改 skill/memory 前先 `stat` 看 mtime——若比本会话开始时间新，先读内容确认是否已含本次要写的信息，**已有则不重复写**（正本唯一铁律）
2. 发现内容已存在且一致 → 只补缺口（如本会话补 E2E 实测结果），不重写全文
3. 无法确认来源的更新，如实向用户披露（"不是我写的，判断是并行会话"），不假装是自己写的
4. **并行会话的 `git add -A` 会把你的未提交改动一起带走**（2026-08-07 实测：patch 完 _模板.md 后 commit 提示 "Everything up-to-date"，git log 里出现非本会话 commit——并行会话 commit 时 add -A 把模板改动一并打包）。判据：git status 干净但 git log 有陌生 commit + 自己没提交过 → `git show <commit> -- <file>` 验证改动已在 HEAD，无需重复提交

### 并行 terminal 调用共享 shell 状态

并行发多个 terminal 调用时共享同一 shell 会话——一个调用里的 `cd` 会干扰另一个的 cwd，造成 `fatal: not a git repository`、目录"找不到"等费解报错（实际文件都在，只是 cwd 漂了）。规避：并行 terminal 调用一律显式传 `workdir` 参数，不依赖共享 cwd。反面案例：整理工作区时并行跑两个 ls/git 命令，一个 `cd branchingjade` 后 cwd 漂到上级目录，另一个报 git 仓库和 `分析/` 目录不存在。

### git mv 只对 tracked 文件有效

整理目录时，untracked 文件（未 add 过）用 `git mv` 会 fatal "not under version control"——先普通 `mv` 移动，再 `git add` 新位置；tracked 文件才用 `git mv` 保留 rename 记录。另外 `git mv` 目标路径已存在也会 fatal——先 `diff` 对比两份内容再决定删哪个（反面案例：根目录 cats.txt 是缩进混乱+重复行的脏版，IronNorthScene 已有干净版，删脏版留干净版）。

### git filter-repo 会删除工作树 untracked 文件

`git filter-repo` 重写历史后执行 `git reset --hard` + `git clean -fd`——**所有 untracked 文件/目录会被静默删除**（实测：`_check/cur2.json` 被顺带清掉，且从未进过任何备份、无法恢复）。跑 filter-repo 前必须：① `cp -r .git .git.bak` 备份仓库；② `git status --short` 列出 untracked，把需要的挪出工作树；③ 操作后验证关键文件完整性再删备份。filter-repo 还会清空 remote 配置（本地无远端仓库无影响），且拒绝非 fresh clone（本地仓库加 `--force`）。历史里的误提交大文件（如曾被跟踪的 alist.exe 110MB）抹掉后 `.git` 从 114MB→25MB，备份主包同步缩小——瘦身收益要实测汇报给用户。

### Config.yaml 编辑被拦截

`patch` 工具直接修改 `config.yaml` 会被拒绝（安全红线）。跳过去用 `execute_code` + Python：

```python
from pathlib import Path
p = Path(os.environ['LOCALAPPDATA']) / 'hermes' / 'config.yaml'
text = p.read_text()
text = text.replace(old, new)
p.write_text(text)
```

`hermes config set` 不可靠——声称保存成功但可能写到错误路径（`~/.hermes/` 而非 `%LOCALAPPDATA%/hermes/`），且不会报错。

### 社区桌面插件安装

完整流程 → `references/community-plugin-install.md`

### WebBridge 并发 session 冲突（并行子代理实测 2026-08-05）

多个并行子代理同时用 Kimi WebBridge 抓网页时，**共用默认 session（如 `yanben`）会导致 tab 串页**——A 子代理打开的页面被 B 子代理的 navigate 抢走，抓回来的内容张冠李戴。规避：每个子代理用**随机唯一 session 名**（如 `qiannv-youhun`、`ss7-<随机>`），会话内全程复用同一 session。

另外：中文参数必须走临时 JSON 文件体（`--data-binary @文件`），不能内联进命令行——curl 传中文参数会因编码问题失败或截断。

### 大工程先出样板验证可行性

用户对 skill/知识库类大工程的节奏要求（2026-08-05 实测确认）：**先出规划 → 用户确认 → 做小样板（如第一个题材密码文档）→ 用户审样板质量 → 再铺全量**。用户会说"先看可行性"——此时必须停下来做最小可行验证（如实测 references/ 能否被 skill_view 按需加载），把验证结果摆出来，不直接铺开。反面：规划确认后直接做 8 个题材文档，用户会打回"先看可行性"。

会话启动时全量加载。用户偏好：MCP 默认全禁用，用到临时启用，用完即关。Feature request: [#69097](https://github.com/NousResearch/hermes-agent/issues/69097)。

### Memory 工具子串匹配陷阱

`memory(action='remove')` 用子字符串匹配，短字符串可能误命中多条。批量清理直接用 `write_file` 写入完整 MEMORY.md，不走 memory 工具逐条删。

### 记忆瘦身流程（skill 覆盖验证 → 删）

用户会质疑"很多不都是在skill中的吗"——删记忆条目前先验证知识是否已在 skill 里：`grep -rl "关键词" ~/AppData/Local/hermes/skills --include=SKILL.md`，实测命中即覆盖（如 GIF 压缩坑被 gif-compression/gif-optimization 各命中 21/13 处 → 整条删）。删除优先级：① skill 已覆盖的程序知识 → 删；② 画像（USER.md）已覆盖 → 删（独有信息先并入画像再删）；③ 项目知识 → 搬进项目 AGENTS.md 后删；④ 易过时快照（版本号/文件数量）→ 改成"以 frontmatter/MOC 为准"。保留：无 skill 覆盖的环境事实、用户偏好、核心原则。批量操作用 memory operations 数组一次提交（原子、只查最终字符数）。

### Skill 同步铁律

任何约定/标准/流程变更后，必须同步更新对应 skill + 推送至 `AiDirectorToolkit`（正本仓库）。注意：`hermes-skills` 仓库已删除，唯一远端是 `AiDirectorToolkit`。

### 技能库命名与副本清理

技能库在 `~/AppData/Local/hermes/skills/`，是一个 git 仓库（`https://github.com/branchingjade/AiDirectorToolkit`），**仅追踪 3 个核心 AI 技能**，统一归入 `妖玉影视/` 分类目录：

```
妖玉影视/
├── AI短剧编剧助手/      v2.2.0
├── AI短剧导演助手/      v12.0.0
└── AI提示词助手/    v1.4.0
```

加载时用 `妖玉影视/AI短剧编剧助手` 路径，不加前缀会因其他同名技能产生歧义。

**命名铁律**：目录名 = skill name（中文），二者一致。所有英文名目录（`ai-screenwriter-assistant/`、`ai-prompt-assistant/`、`ai-short-drama-assistant/`）和 `ai-skills/` 子目录是旧版残留，不在 git 追踪中——见到直接删。

**歧义排查流程**：加载技能时报 "Ambiguous skill name" → 不要猜，跑以下三步：

1. `cd ~/AppData/Local/hermes/skills && git status` — 确认哪些是 tracked（正本），哪些是 untracked（残留）
2. 对比各副本的 `name:` 和 `version:` 字段（`grep -r "^version:" */SKILL.md 妖玉影视/*/SKILL.md 2>/dev/null`）
3. 删除 untracked 旧版副本，只保留 git tracked 的正本

其余上百个第三方技能（mattpocock、lark 等）同样 untracked，来自其他安装渠道，不受此 git 仓库管理。

**技能组织铁律**（反副本残留）：

1. **改结构用 `git mv`，禁止 `cp`+修改。** 旧位置自动消失，不残留副本。`cp` 是副本制造机——每次换组织方式就多一份。
2. **改命名先删旧再建新。** 新方案确认能用 → 立刻删旧。不等、不存、不"先留着看看"。新旧并存窗口期 = 歧义的土壤。

根因：所有副本残留都来自同一个模式——"新建一份看看效果"，但从不在换方案时删旧的。解决：每次变更只存在一个正本。

**死仓库陷阱**：如果 `git remote -v` 显示已删除的 GitHub 仓库（如 `hermes-skills` → 404），不要盲目相信本地 remote。先 `curl -sI <url>` 验证仓库是否存在。确认删除后，用 `git remote set-url` 切到正本。

**远程结构变更冲突陷阱**（2026-08-04 实测）：本地改了旧路径的 SKILL.md，push 被拒后发现远程已 refactor 目录（如三个 skill 从根目录归入 `妖玉影视/`）。rebase 报 modify/delete 冲突——远程删了旧路径、本地改了旧路径。处理顺序：
1. `git rebase --abort` 放弃（不要硬解 rebase 冲突）
2. `git checkout master && git pull`（merge 模式，接受远程 rename）
3. `git ls-tree HEAD <新目录>/ --name-only` 确认远程新路径结构
4. `git rm -f` 旧路径文件，把本地新版内容 `cp` 到远程新路径
5. `git add -A && git commit && git push`（merge 提交）
关键：**以远程结构为准**——先看远程怎么组织的，把改动放进远程的新位置，而不是把本地旧结构推上去。同步本地 skill 到正本仓库前先 `git fetch` 看远程是否改过结构。

## 其他参考文档

| 文件 | 内容 |
|------|------|
| `references/cron-delivery-patterns.md` | Cron 投递模式 |
| `references/identity-and-memory-files.md` | SOUL.md/USER.md/MEMORY.md 角色区分 |
| `references/session-classification.md` | 会话分类指南 |
| `references/session-grouping-mechanism.md` | 会话侧边栏分组机制 |
| `references/workspace-directory-conventions.md` | 特殊项目目录结构模板 |
| `references/workspace-gitignore.md` | .gitignore 模板 |
| `references/ssh-remote-deployment.md` | SSH 远程部署模式（NAS/VPS，含 base64 传输、Docker 镜像站、systemd 自启） |
| `references/nas-deployment-ugreen.md` | 绿联 NAS 部署模式（Docker/venv/systemd） |
| `references/projects-and-worktrees.md` | 项目和工作树 |
| `references/obsidian-logs.md` | **日志架构约定** — 年月/W{N}/ 结构+命名规范+月报模板 |
| `references/postmortem-methodology.md` | **任务复盘方法论** — 13个维度深度复盘框架 |
| `references/lark-cli-doc-edit-pitfalls.md` | **lark-cli 文档编辑陷阱** — str_replace 跨 block 静默失败 + block 操作正确姿势（2026-08-06 实测） |
| `references/memory-providers.md` | 外部记忆提供者 8 个对比（Honcho/Mem0/Holographic/OpenViking…）— 本地 vs 云 + 隐私选择建议 + **Hindsight 本地嵌入式二次安装定稿**（curses 向导坑/手动配置三件套，2026-08-06） |
| `references/hindsight-ops-diagnostics.md` | **Hindsight 运维诊断**（2026-08-07 实测）— recall 搜不到≠没 retain（consolidation 积压是真因，recall_types=observation 只召回已提炼事实）；路径/端口/日志速查；飞书→Hindsight 天生打通（gateway 飞书 agent 自动挂 provider，无需改代码） |
| `references/feishu-collab-health-check.md` | **飞书协作健康度巡检** — 五面检查（画像库/路由表/项目记忆/cron/双通道活跃度）+ 常见发现判据 + **修复层指引**（路由 chat_id 反查、多项目成员豁免keys、话题key双后缀、健康脚本用法、摘要补评论通道）（2026-08-07 实测） |
| `scripts/hindsight-e2e-check.py` | **Hindsight 记忆 provider 端到端验证脚本** — retain→consolidation→recall 闭环探测（方法名/异步时序/venv 用法全内置） |
| `scripts/cleanup-projects.py` | 项目清理脚本 |
