# 飞书协作健康度巡检流程（五面检查）

2026-08-07 实测定稿。触发词：「检查协作健康度」「协作体系缺点」「巡检」。核心原则：**双通道统计**（IM + 评论），不贴通道标签。

## 五面检查清单

### 面 1：画像库完整性
- 成员名单（`_hermes/成员名单.json`）↔ 画像文件（`成员画像/<真名>.md`）一一对照
- 检查点：每人在名单里有画像文件、frontmatter open_id 与名单一致、留空成员（无观察）符合「待沉淀」规则
- 留空 ≠ 缺失：无观察成员留空是正常的，不编造

### 面 2：会话路由表健康
- `_hermes/会话路由.json`：项目词典 / 路由 / documents 三块
- 检查点：词典覆盖活跃项目；无旧应用 open_id 残留；**路由登记率**（近 48h 活跃会话数 vs 路由表条目数——实测 28 会话 vs 4 条路由 = 登记率严重不足，多数私聊未进路由表）

### 面 3：项目记忆（⚠️ 2026-08-08 起已迁移，不再检查 Obsidian）

- ~~`_hermes/项目记忆/<项目>.md` 文件数量、最近更新、每文件记忆条数~~ **已废弃**：`_hermes/项目记忆/` 已于 2026-08-08 删除（Hindsight 取代，见 `hindsight-ops-diagnostics.md`「删除落地三件套」）
- 健康脚本 `feishu-collab-health.py` 的【4】项目记忆块已改为固定输出「已迁移 Hindsight 外部记忆，Obsidian 侧不再维护」，`memo_status()` 返回空列表（保留签名防 NameError），汇总不再报「项目记忆为空」
- cron prompt（飞书协作健康检查 4da8374c0b69）同步移除「项目记忆为空→检查沉淀钩子」指引——**改脚本后必须同步改 cron prompt，否则 cron 继续让 agent 按旧逻辑解读**

### 面 4：cron 每日摘要执行
- 输出目录 `~/AppData/Local/hermes/cron/output/88ab7ff66681/*.md`（飞书每日摘要）
- 检查点：最近一次 22:00 运行文件存在、`cron/executions.db` status=completed
- 已知局限：摘要只查 IM（feishu-daily-digest.py 查 sessions 表）——**评论通道活动进不了每日摘要**，评论为主的成员会被遗漏

### 面 5：双通道活跃度（合并统计）
- IM：state.db sessions 表，`source LIKE '%feishu%' AND started_at > now-48h GROUP BY user_id`
- 评论：`_hermes/评论会话/comment_*.json`
  - 文件名 URL 编码：`_pct_3A`=冒号、`_pct_E4...`=中文——解码 `core.replace('_pct_','%')` 再 `urllib.parse.unquote`
  - 内容：`messages` 长度 + `last_access` 时间戳；Commenter 从 user 消息 `Commenter: (\S+)` 提取
- 合并输出：成员 × IM会话/IM消息/评论线程/最后活动 表
- ⚠️ 只看 IM 会漏掉评论为主成员（实测杨璇：IM 0 会话但评论 1 线程）——**禁止贴「走XX通道」标签**
- ⚠️ **评论会话文件是 TTL 短时缓存，不是长期归档（2026-08-08 查证）**：`feishu_comment_collab.py` 的 `SESSION_TTL_S = 3600`——超过 1 小时未访问的文件在下次 `load_session_history` 读时被 `path.unlink()` 自动删除。文件名叫"评论会话"且放在 git 归档目录里，但**设计语义是维持线程上下文的临时缓存**。✅ **2026-08-08 已修复**：TTL 超时不再删除，改为移入 `评论会话/archive/` 子目录（带时间戳防重名 + `archived_at` + `original_key`），缓存失效但原始评论证据永久保留——画像勘误"反查原始评论来源"有据可查。健康检查【5】同步加归档统计（`📦 历史归档: N 个评论线程`）。IM 会话（state.db）是内核自动永久留档（session_search 可查），评论会话是手动实现——两者机制不同，评论的原文留档靠 archive/ 目录。手动归档存量文件：从文件名反推 key 不可靠（`_pct_` 干扰 unquote），直接读文件内容 + 手动执行归档分支（构造 archive 路径 + `_atomic_write_json` + unlink）。

## 常见发现与判据

| 发现 | 判定 | 处置 |
|---|---|---|
| 路由登记率低 | 活跃会话数 >> 路由表条目 | 报告给用户，路由机制需人工登记或识别写入未触发 |
| 评论通道不在每日摘要 | digest 脚本只查 sessions 表 | 已知局限，报告即可 |
| 画像留空成员多 | 成员名单有但画像无观察 | 正常（无观察不编造），非缺陷 |
| 项目记忆为空 | ~~目录只有 README~~ | **已废弃（2026-08-08）**：项目记忆迁移 Hindsight，脚本不再检查、不再误报 |
| 沉淀停更 | 画像 updated 字段陈旧 | 查 gateway 是否运行、OBSERVATION 钩子是否被 hermes update 覆盖（画像沉淀保留，仅项目记忆已停） |

## 输出格式

最终报告按面分节：✅ 正常面（每面给证据数字）+ ⚠️ 待处理面（列出问题 + 处置建议）。收尾带 git 状态核对（并行会话可能同时写 vault，git add -A 会带走别人未提交改动——commit 前检查并如实披露）。

## 修复层（巡检发现问题后的处置，2026-08-07 实测）

### 路由表修复：DM chat_id 归属必须反查，不能凭路由表已有登记猜

**根因案例**：路由表曾把 `feishu:dm:oc_a856f8...` 登记为「个人工作区 owner 妖玉」——实际这是**魏宁馨的 DM**（state.db sessions 表按 user_id 反查 ou_94566a=魏宁馨）。这个误标导致后来创建「项目看板日报」cron 时投递目标被设成 `feishu:oc_a856f8...`，日报每天投到魏宁馨 DM。

正确流程：
1. 路由表某 chat key 的归属存疑 → `SELECT DISTINCT user_id, chat_type FROM sessions WHERE session_key LIKE '%oc_xxx%'` 反查，别信路由表 owner 字段
2. 核对 cron 投递目标：`cronjob list` 检查每个 job 的 deliver，确认目标 chat 归属（本机约定：**cron 只投妖玉 DM `oc_f7b91a...`**，不投其他成员——用户明确「不需要给我以外的人 cron 消息」）
3. 路由表里 DM 按「单项目成员绑项目 / 多项目成员豁免」分流

### 多项目成员 DM 豁免机制

`resolve_project_for_session`（feishu_comment_collab.py）逻辑：**路由命中固定 project 就直接返回，不会降级到词典匹配**。所以把多项目成员（如魏宁馨=魔王导演但也做其他项目）的 DM 绑定单项目，会导致她聊其他项目时误加载魔王上下文。

处置：路由表加 `规则.豁免keys` 数组（如 `["feishu:dm:oc_a856f8..."]`），这些 DM **故意不登记**固定项目，走 `_match_dictionary` 按消息内容识别（聊魔王命中魔王词、聊别的命中别的词）。健康脚本 `route_coverage()` 同步读豁免keys，豁免的 key 不报未登记。

### 话题级 key 两种后缀

session_key 去掉 `agent:main:` 前缀后，话题级 key 后缀有 **`:omt_` 和 `:om_x` 两种**（群话题 vs DM 话题）。查路由/统计时都要剥：`for sep in (":omt_", ":om_"): if sep in base: base = base.split(sep)[0]`。

### 统一健康检查脚本

`~/AppData/Local/hermes/scripts/feishu-collab-health.py`（IM+评论双通道）：

```bash
python3 ~/AppData/Local/hermes/scripts/feishu-collab-health.py [hours]  # 默认 48h
```

输出五面：①成员活跃度（IM+评论合并，按人）②路由覆盖（未登记列表，支持豁免keys）③画像覆盖 ④项目记忆（**2026-08-08 起固定显示「已迁移 Hindsight」，不再扫描文件**）⑤评论线程明细。已有每周日 22:00 cron「飞书协作健康检查」跑 168h 窗口，异常告警到妖玉 DM。脚本语法自检：`python -c "import ast; ast.parse(open('scripts/feishu-collab-health.py',encoding='utf-8').read())"`。

### 画像检查升级：空模板检测（2026-08-08 用户要求「cron 加强成员画像」）

`profile_coverage()` 返回 `(missing, empty_templates)` 二元组：

- **missing**：成员名单中无画像文件的人（原有逻辑）
- **empty_templates**：有画像文件但内容为空模板的人——只有 frontmatter + 注释占位符，无实际观察沉淀

**空模板判定必须排除三类行**（否则模板骨架被误判为实质内容，实测前两版判定全部漏报）：
1. 注释 `<!-- ... -->`（`re.sub(r"<!--.*?-->", "", body, flags=re.S)`）
2. 占位行（"待沉淀"、"成员名单.json 登记"、"NAS"、"共享账号"等初始建库占位语）
3. 结构行（`#`标题、`>`回链、`##`章节名）

判定：`meaningful = [ln for ln in stripped.splitlines() if ln.strip() and not ln.lstrip().startswith(("#", ">", "---")) and not any(w in ln for w in placeholder_words)]`，`meaningful` 为空 → 空模板。汇总里空模板记为 `⚠️ 画像空模板 N 人（待沉淀）`——**是正常待沉淀状态不是故障**，健康检查的职责是让它可见，不是报警；cron prompt 解读指引同步写「空模板→等每日摘要沉淀，无需干预」。

### 画像设计收敛：四问定调（2026-08-08 用户四个反问确立）

用户质疑画像质量方案的过度设计，四问定调：
- **画像字段**：三章节够（沟通偏好/擅长领域/协作备注），观察记录独立拆章=过度设计——协作备注本身就是事件流水
- **陈旧提示**：没用，砍——画像记的是稳定偏好，30 天未更新不失效；活跃度是健康检查【1】的事，画像不需要自己的时效机制
- **画像是实时记录**：理论实时（gateway OBSERVATION 钩子）、实际 cron（每日摘要批量）——「让实时通道真正跑起来」才是画像时效的答案，见下节
- **来源标注**：定位=排查用（画像正确忽略来源，画像错反查定位问题），只保留「档案归位」粗标注，bot 观察默认不标；`（cron 观察 2026-08-05）` 统一为 `（观察 2026-08-05）`

### 实时通道修复（2026-08-08 用户拍板「要让实时通道真正跑起来」）

画像沉淀双通道：**实时**（gateway/run.py 每轮飞书回复后剥离 `OBSERVATION:` 标记 → `record_observation()` 写画像）+ **cron 批量**（每日摘要步骤6）。实测实时通道零触发（日志 `Observation recorded` 无命中、10 条飞书回复无一条带标记）——修三处：

1. **`OBSERVATION_DAILY_MAX` 源码未同步**：值还是 2，用户 08-07 已拍板「不设条数上限」——改成 999（feishu_comment_collab.py 常量，改一行即可）
2. **提示词无示例不触发**：gateway/run.py 的 `combined_ephemeral` 注入段原措辞「如果体现了稳定偏好就加一行」太弱——agent 默认认为自己没观察到。强化为：明确可观察类别（沟通风格/格式偏好/工作方式/擅长领域/项目角色）+ 两个示例行 + 「宁可多写不要漏」
3. **IM 读侧缺失**：评论通道有 `=== 成员画像 ===` 注入（feishu_comment.py `get_profile`），IM 通道完全没有——画像写了 bot 读不到。在 gateway/run.py FEISHU 分支回复前注入 `get_profile(user_id)`，空模板跳过（复用与健康检查相同的占位词过滤逻辑）。**画像用途定调**：让 bot 更了解成员、更好协作；来源标注=排查用（画像正确忽略来源，画像错反查定位），只保留「档案归位」粗标注，bot 观察默认不标。
4. **公共函数统一**（2026-08-08 用户「不只是IM通道」纠正）：空模板过滤逻辑从 IM 注入处内联版抽为 `collab.get_profile_meaningful(open_id)` 公共函数（collab 模块，与健康检查脚本同判定：排除注释/占位词/结构行后无实质内容→返回 ''），IM（gateway/run.py）和评论（feishu_comment.py）两通道共用——避免两份过滤逻辑漂移。占位词清单要覆盖建库初始信息（"待沉淀"、"NAS SMB 共享账号"、"共享账号用户"等——实测漏了 NAS 行导致空模板误判为有内容）。kanban worker 不注入画像（AI worker 非人类成员）。

### 每日摘要 cron 自动建画像（2026-08-08）

每日摘要 cron（88ab7ff66681）步骤6 原规则「画像文件不存在则跳过」→ **新成员首次协作的观察会丢**。改为：画像文件不存在则按 `成员画像/_模板.md` 自动创建 `<真名>.md`（open_id 从成员名单.json 查，查不到留空）再写入观察。与「成员首次出现→自动追加成员名单+建画像」规则对齐。

### 每日摘要 cron 补评论通道

每日摘要 cron（88ab7ff66681）原只查 IM（feishu-daily-digest.py 查 sessions 表），评论通道活动永远进不了摘要。修复：prompt 增加步骤 2——用 Python 读 `_hermes/评论会话/comment_*.json` 的 last_access 过滤近 24h 线程，纳入摘要（发言人标 `[评论:真名]`）；评论线程内容直接读 json 文件，不用 session_search。

### 索引文件名并行改名坑（2026-08-07 实测）

并行会话可能给索引文件改名（实测：项目记忆 `README.md` → `索引.md` → `项目记忆.md`）。健康脚本的排除列表必须跟上新文件名，否则索引文件被误算成项目记忆条目。⚠️ **2026-08-08 起此坑已失效**：`memo_status()` 改为 no-op（返回空列表），不再遍历 `_hermes/项目记忆/`，排除列表无意义——改脚本时该函数的排除逻辑可直接删（保留函数签名防调用点 NameError）。

### 历史档案归属：行为匹配不可靠，用户拍板是唯一真相

多人同项目（如陈强系列三人协作）行为高度同质，agent 按行为特征猜映射会错（实测 70% 置信度的判断仍被用户推翻）。正确姿势：①调出各人提交的**原始提示词内容样本**（state.db 提取 user 消息按人分档）给用户认人——内容风格比抽象特征更有辨识度；②归属由用户拍板，agent 不自行定稿；③画像中身份信息带来源（「2026-08-07 妖玉确认：XX 是《魔王》导演」）；④归位后档案文件标注真名、画像并入完整内容（逐条展开非概要）、索引同步、git 提交。
