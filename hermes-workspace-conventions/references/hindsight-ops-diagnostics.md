# Hindsight 运维诊断（2026-08-07 实测）

外部记忆 Hindsight 的**运行诊断**层——安装见 `memory-providers.md`，本文件管"装好之后怎么验证、recall 不到怎么办"。

## 关键路径 / 端口速查

| 项目 | 位置 |
|---|---|
| 插件配置 | `~/AppData/Local/hermes/hindsight/config.json`（bank_id / recall_budget / recall_types / retain_every_n_turns 等） |
| 环境变量 | `~/.hindsight/profiles/hermes.env`（LLM 配置；`HINDSIGHT_API_PORT=9177`） |
| **服务日志（诊断主入口）** | `~/.hindsight/profiles/hermes.log`（retain / recall / consolidation 全量记录） |
| 嵌入式 PG 数据 | `~/.pg0/instances/hindsight-embed-hermes/data` |
| API 健康检查 | `curl http://localhost:9177/health` → `{"status":"healthy","database":"connected",...}` |
| embed 服务 | 127.0.0.1:8475（`netstat -ano | grep 8475`） |
| Hermes 侧 provider 激活日志 | `~/AppData/Local/hermes/logs/agent.log`：`Memory provider 'hindsight' activated` |

## 核心诊断原则：recall 搜不到 ≠ 没 retain

**实测案例（2026-08-07）**：用飞书专属词（收购谈判/圣晶石/萧烬/古堡）recall，返回的全是桌面会话内容，一度误判"飞书渠道没接 Hindsight、内容没存进去"。逐层排查后真相：

1. **飞书 agent 其实激活了 Hindsight**：state.db 里多个飞书 session 在 agent.log 有 `Memory provider 'hindsight' activated` 记录
2. **飞书内容其实 retain 进 bank 了**：`hermes.log` 的 `Document:` 列表里明确出现飞书 session id（如 `20260805_092346_40d2d5eb` 工友鼓掌、`20260807_095447_ed7f6d22` 神域的真相）
3. **搜不到的真因 = consolidation 积压**：recall 配置 `recall_types="observation"`——**只召回已提炼成 observation 的事实**；retain 写入的是原始会话内容，要等后台 consolidation 用 LLM 提炼成 observation 后才能被 recall 命中。积压期间 recall 表现像"失忆"

### 诊断顺序（从快到慢）

```bash
# 1. 渠道是否激活了 provider
grep "Memory provider.*activated" ~/AppData/Local/hermes/logs/agent.log

# 2. 内容是否已 retain（对照 state.db 的 session id）
grep "Document:" ~/.hindsight/profiles/hermes.log | sort -u

# 3. retain 了但 recall 不到 → 查 consolidation 进度
grep -E "CONSOLIDATION|slow llm call|STUCK|processed=|empty message" ~/.hindsight/profiles/hermes.log | tail -20
#   看 processed=X/129 的进度与每条耗时

# 4. API 健康
curl -s http://localhost:9177/health
```

## consolidation 性能坑（DeepSeek 后端实测）

- 单条记忆提炼 3~23s，批量 LLM 调用 38~146s（日志标 `slow llm call`）
- 还有 `Provider returned empty message content` 空响应，触发 attempt 1/4 重试，进一步拖慢
- **consolidation 是持续追赶不是一次清完**（2026-08-08 实测）：新 retain 持续进队，积压数会反复波动（129→119→54→297→12），「等它消化完」是移动靶——判断「记忆是否生效」用**数据层 API**（memories/list 关键词命中）而非等积压归零
- 加速选项：`HINDSIGHT_API_LLM_MODEL` 换更快模型 / 调大 batch / 临时放宽 `recall_types`
- **判断"记忆没生效"前必须先看 consolidation 进度 + 数据层 API 双确认**，别拿一次默认工具 recall 结果下结论

## 其他故障症状

- `Hindsight retain failed: Cannot connect to host localhost:8888`（agent.log）→ Hindsight daemon 未起或刚重启，retain 全部失败；窗口期内内容丢失不可恢复。**注意：8888 是旧配置残留，实际 API 端口是 9177**——errors.log 里连 8888 的报错是 daemon 未起/刚重启的症状，不是端口配错了
- `hindsight-embed.log` 里 `Daemon startup failed: 'NoneType' object has no attribute 'splitlines'` → embed daemon 启动失败，配置变更（config.json 重写）会触发 daemon 重启，重启失败则服务不可用
- **`[STUCK?]` 标记 ≠ 真死**：worker poller 日志 `[STUCK?] age=900s+` 是长 LLM 调用（DeepSeek consolidation 单次可达 100s+）被标记，任务会 age 归零重新拉起，属于慢不是死——看到 STUCK 先查 `stage=` 是否在推进，别急着重启
- **`batch_retain payload_null=1`**：一个 retain 任务 payload 丢失挂队列，不影响主流程，可忽略
- **cron 结果桌面/CLI 会话收不到**：桌面/CLI/TUI 会话无 live-delivery 通道，cron 输出只存记录（deliver=local，`cronjob action='list'` 可查）；要自动推送需设 gateway 连接渠道（如 `deliver='feishu:...'`）

## 架构事实：飞书 → Hindsight 天生打通（2026-08-07 确认）

- 同一个 `memory.provider=hindsight` 全局配置，**gateway 创建的飞书 agent 自动挂载 Hindsight provider**（agent/agent_init.py），turn 完成后 `memory_manager.sync_all → provider.sync_turn` 自动 retain（run_agent.py）
- gateway 的 `OBSERVATION:`/`PROJECT_MEMO:` 钩子（gateway/run.py）写 Obsidian 是**并行的另一条沉淀通道**（成员画像/项目记忆文件），不是 Hindsight 的替代品
- **结论：打通飞书与 Hindsight 不需要写任何代码**——管线天生就是通的；若要"纯事实条目双写进 Hindsight"也只是增强，不是必需

## 记忆体系分层速记（与 Obsidian 的关系）

- Hindsight = agent 自己的语义记忆（自动 retain/recall，不产生可管理文件）
- Obsidian `_hermes/` = 团队协作数据层（成员画像/路由/名单/评论会话，git 归档）——多用户访问控制、结构化映射、可审计归档，Hindsight 替代不了
- 桌面会话项目记忆 → Hindsight 已完全胜任；飞书协作记忆 → 保留 Obsidian 层

## 数据层验证 API（recall 之外的最硬证据，2026-08-08 实测）

recall 是语义检索（相关性排序 + token 预算截断），**返回结果受排序影响，不能当作"内容是否存在"的判据**。要确证内容在不在 bank 里，直接查数据层（API 端口 9177）：

```bash
# 1. bank 统计：total_documents / pending_consolidation / nodes_by_fact_type
curl -s http://localhost:9177/v1/default/banks/hermes/stats

# 2. 记忆列表直查（内容是否入库的最硬证据）——关键词 grep 命中的 text 字段
curl -s "http://localhost:9177/v1/default/banks/hermes/memories/list?limit=50" | python -c "import sys,json; d=json.load(sys.stdin); items=d if isinstance(d,list) else d.get('memories',d.get('items',d.get('results',[]))); [print(json.dumps(it,ensure_ascii=False)[:200]) for it in items if '关键词' in json.dumps(it,ensure_ascii=False)]"

# 3. 原始 recall API（绕开工具层截断，加大 limit 看全量排序）
curl -s -X POST http://localhost:9177/v1/default/banks/hermes/memories/recall -H "Content-Type: application/json" -d '{"query":"关键词","limit":60}' | python -c "import sys,json; [print(f\"[{i}] {r.get('text','')[:120]}\") for i,r in enumerate(json.load(sys.stdin).get('results',[]))]"
```

**坑**：curl 直接 `-d '{中文 JSON}'` 可能报 `{"detail":"There was an error parsing the body"}`（shell 引号/编码）——用 Python urllib 或 `--data-binary @文件` 发 body。响应结构 `{"results":[...], "entities":[...]}`，每条含 `text/type/scores.final`。

## 架构结论（2026-08-08 验证定稿：Hindsight 可靠，项目记忆层可降级）

**验证过程教训（重要）**：2026-08-07 曾因 consolidation 未消化完 + 默认工具 recall 只显前几条，**过早下结论「recall 收益有限、Obsidian 保留不砍」并写进记忆**——用户纠正「等验证后在做决定」。次日验证推翻：consolidation 消化完（297→12）+ `limit=60` 全量 recall 后，**飞书内容明确可召回**（[6]萧烬/金玄/神域、[10]魔王/收购命中，返回 11 条中 2 条飞书内容）。

**定稿结论**：
- **飞书项目记忆可靠 Hindsight**：recall 可召回（排第 6/10 位=排后面不是搜不到，前 5 名被桌面内容占是语义排序+token 截断的常态，不是故障）
- **Obsidian `_hermes/项目记忆/` 已于 2026-08-08 直接删除**（用户拍板「那就只是删掉吧，项目记忆这个」，非降级保留）——伏妖记.md/魔王.md/项目记忆.md 全部 `git rm`（git 历史仍在）
- **画像/路由/名单仍留 Obsidian**：Hindsight 单 bank 无用户隔离，多用户维度（访问控制/确定性映射/人可读）替代不了

**删除落地三件套（2026-08-08 实测，删 Obsidian 目录必做）**：
1. **删目录**：`git rm -r _hermes/项目记忆/`（git 历史保留）
2. **停写它的代码钩子**——⚠️ 这是最容易被漏的：`record_project_memory()`（feishu_comment_collab.py:379）内部 `path.parent.mkdir(parents=True, exist_ok=True)` **会静默重建已删目录**。只删目录不删钩子 = 下次飞书协作沉淀时目录自动复活。正确做法：函数入口加 early-return（保留签名、log 一条 disabled 说明），一处改动覆盖 IM + 评论两个调用点
3. **移除 agent 提示模板里的标记指令**：`PROJECT_MEMO: <事实>` 的提示文案在 feishu_comment.py:1175 + gateway/run.py:4453 各一处（`combined_ephemeral` 拼接），不删则 agent 继续输出无意义标记行；剥除逻辑（run.py:5733 起）保留无害
4. 同步 MOC 引用（记忆MOC.md/飞书协作记忆MOC.md/MOC.md 改为「→ Hindsight」）+ 补丁存档（`scripts/patches/` 的 diff + collab.py 备份 + reapply-patches.py 注释）

**推论（别再犯）**：
1. **验证未完不下定论**——评估类任务（能否砍/是否打通）未验证完之前：不删监控设施（cron）、不把结论写死进 memory。用户原话「等验证后在做决定」
2. **子代理/cron 自报不可信**——cron 自动验证报告「打通成功」也要独立复验（本会话 cron 报告属实但早期工具 recall 显示前几条全桌面，直到 limit=60 才确认）。验证链：数据层入库（memories/list）→ 全量 recall（limit=60）→ 才下结论
3. 遇到「Hindsight 搜不到 X」先走诊断流程（激活→retain→consolidation→数据层 API），别急着下"没打通"的结论，更别为此建打通代码——管线天生是通的
4. 评估「能否砍 Obsidian 记忆层」时，区分「记忆」（Hindsight 能管）与「非记忆」（结构化数据/人可读文件/多用户权限——Hindsight 管不了）
