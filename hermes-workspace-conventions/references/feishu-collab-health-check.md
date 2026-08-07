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

### 面 3：项目记忆沉淀状态
- `_hermes/项目记忆/<项目>.md` 文件数量、最近更新、每文件记忆条数
- 空目录 ≠ 机制坏：沉淀钩子（`OBSERVATION:`/`PROJECT_MEMO:` 标记行）在 gateway/run.py，**gateway 重启后才生效**——重启前的历史观察需手动从 cron 输出补齐
- 验证钩子在位：`grep -n "OBSERVATION\|PROJECT_MEMO" gateway/run.py`

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

## 常见发现与判据

| 发现 | 判定 | 处置 |
|---|---|---|
| 路由登记率低 | 活跃会话数 >> 路由表条目 | 报告给用户，路由机制需人工登记或识别写入未触发 |
| 评论通道不在每日摘要 | digest 脚本只查 sessions 表 | 已知局限，报告即可 |
| 画像留空成员多 | 成员名单有但画像无观察 | 正常（无观察不编造），非缺陷 |
| 项目记忆为空 | 目录只有 README | 查钩子在位 + 是否 gateway 重启后；重启前需手动补齐 |
| 沉淀停更 | 画像/项目记忆 updated 字段陈旧 | 查 gateway 是否运行、钩子是否被 hermes update 覆盖 |

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

输出五面：①成员活跃度（IM+评论合并，按人）②路由覆盖（未登记列表，支持豁免keys）③画像覆盖 ④项目记忆（文件+每日每项目≤5条限额告警）⑤评论线程明细。已有每周日 22:00 cron「飞书协作健康检查」跑 168h 窗口，异常告警到妖玉 DM。

### 每日摘要 cron 补评论通道

每日摘要 cron（88ab7ff66681）原只查 IM（feishu-daily-digest.py 查 sessions 表），评论通道活动永远进不了摘要。修复：prompt 增加步骤 2——用 Python 读 `_hermes/评论会话/comment_*.json` 的 last_access 过滤近 24h 线程，纳入摘要（发言人标 `[评论:真名]`）；评论线程内容直接读 json 文件，不用 session_search。

### 索引文件名并行改名坑（2026-08-07 实测）

并行会话可能给索引文件改名（实测：项目记忆 `README.md` → `索引.md` → `项目记忆.md`）。健康脚本的排除列表必须跟上新文件名，否则索引文件被误算成项目记忆条目。当前排除：`README.md`/`索引.md`/`项目记忆.md`（`feishu-collab-health.py` memo_status 函数）。改文件名后：全库 grep 旧引用同步（`grep -rn "旧路径" --include="*.md" .`）+ 重启 Obsidian（图谱缓存旧索引）。

### 历史档案归属：行为匹配不可靠，用户拍板是唯一真相

多人同项目（如陈强系列三人协作）行为高度同质，agent 按行为特征猜映射会错（实测 70% 置信度的判断仍被用户推翻）。正确姿势：①调出各人提交的**原始提示词内容样本**（state.db 提取 user 消息按人分档）给用户认人——内容风格比抽象特征更有辨识度；②归属由用户拍板，agent 不自行定稿；③画像中身份信息带来源（「2026-08-07 妖玉确认：XX 是《魔王》导演」）；④归位后档案文件标注真名、画像并入完整内容（逐条展开非概要）、索引同步、git 提交。
