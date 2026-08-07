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
- 129 条积压时需数小时消化，期间 recall 严重漏召回
- 加速选项：`HINDSIGHT_API_LLM_MODEL` 换更快模型 / 调大 batch / 临时放宽 `recall_types`
- **判断"记忆没生效"前必须先看 consolidation 进度**，别拿一次 recall 结果下结论

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

## 架构结论（2026-08-07 用户拍板：Obsidian 层保留，不砍）

**实测结论**：飞书内容虽 retain 进 Hindsight（document 列表可查），但 recall 收益有限——consolidation 极慢（129 条积压数小时）+ 语义排序偏向桌面内容（飞书内容难进前 10，BM25 命中 16 个候选但 top 10 全被桌面内容占）。**用户据此拍板：Obsidian `_hermes/` 架构（项目记忆/画像/路由）合理弥补 Hindsight 短板（多用户维度、人可读、确定性查找），维持现状不砍**。

**推论（别再犯）**：
1. 遇到「Hindsight 搜不到 X」先走诊断流程（激活→retain→consolidation），**别急着下"没打通"的结论**，更别为此去建打通代码——管线天生是通的
2. 评估「能否砍 Obsidian 记忆层」时，区分「记忆」（Hindsight 能管）与「非记忆」（结构化数据/人可读文件/多用户权限——Hindsight 管不了）
3. 验证 recall 用目标渠道专属词（飞书内容用魔王世界观词），返回全是桌面内容 ≠ 没 retain，是 consolidation 未消化 + 排序问题
