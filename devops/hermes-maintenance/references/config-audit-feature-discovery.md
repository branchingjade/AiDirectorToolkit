# Hermes 配置审计：发现未使用功能

## 什么时候用

- 用户问「我有哪些功能没用上」「Hermes 还有什么好用的」
- 新版本（v0.19+）发布后检查是否用上了新功能
- 定期优化：检查配置冗余、安全漏洞、效率机会

## 审计命令（并行执行）

一次发完下面 8 个命令，然后汇总分析：

```bash
hermes --version              # 版本号 + 上游 commit
hermes tools list             # 工具集启用状态
hermes skills list            # 已安装技能（注意总数、未使用数）
hermes cron list              # 定时任务
hermes profile list           # Profile 数量
hermes gateway status         # 网关状态
hermes mcp list               # MCP 服务器（是否 disabled？）
hermes auth list              # 凭据池
hermes curator status         # 技能生命周期管理状态
```

外加读 `config.yaml` 全文。

## 分析框架

拿到原始数据后，按以下维度交叉分析：

| 维度 | 关键指标 | 常见问题 |
|------|---------|---------|
| 安全 | `secrets.bitwarden.enabled`, `security.redact_secrets` | `.env` 明文存 key，Bitwarden 未开启 |
| 效率 | `delegation.*`, `moa.*`, `compression.*` | 子代理模型用主模型（浪费 token），MoA 未配置 |
| 功能覆盖 | toolsets disabled, skills activity=0, MCP disabled | 装了但没用过的功能 |
| 版本特性 | `hermes --version` vs v0.19.0 新功能清单 | 新功能是否配置 |
| 冗余 | `curator` 报告中的 activity=0 skills | 装了但从没用过的技能 |
| 备份 | `updates.pre_update_backup`, `hermes-backup` skill | 是否有自动备份 |

## v0.19.0 重点检查项

以下功能在该版本新增/大改，逐一检查配置状态：

- **Bitwarden/1Password 集成** — `secrets.bitwarden.enabled` / `secrets.onepassword`
- **智能审批** — `approvals.mode`（smart/manual/off）
- **子代理实时日志** — `delegate_task` 返回值中的 `live_transcripts` 路径
- **多 Profile 网关路由** — `hermes profile list` 是否 > 1
- **密码管理器集成** — 是否还在 `.env` 明文存 key
- **会话导出** — `hermes sessions export --help`
- **终端订阅管理** — `/subscription` `/topup` 命令

## 输出格式

分析完给用户：
1. 一句话总结（如「安全有缺口、效率有优化空间、5 个功能没启用」）
2. 按优先级排列的推荐清单（每项一行：功能名 + 当前状态 + 一个命令）
3. 不与用户已明确拒绝的功能纠缠（如用户说「声音需求不大」就跳过 Voice Mode）

## 插件库审计（hermes plugins list，2026-08-14 实测）

- `hermes plugins list` = ~80 个 bundled 插件全量注册表（分类清单见 `plugin-toolset-inventory.md`）
- **解析坑**：输出是 box-drawing 表格且描述列跨行折行——awk 切描述列会把折行碎片当独立行、输出稀碎。只提取名称列：
```bash
hermes plugins list 2>&1 | sed 's/\r//g' | grep -oE '│ [a-zA-Z0-9_-]+ +│ [a-zA-Z ]+ +│ [0-9.]+ +│' | awk -F'│' '{gsub(/ /,"",$2); print $2}' | sort
```
- **「not enabled」≠「没在用」**：bundled 插件注册表状态与实际启用是两回事。真正启用的插件（桌面插件 quota-panel/skill-manager/channel-sessions/ops-panel）在 config.yaml `plugins.enabled` 列表；config 驱动的功能（飞书平台、web.backend=ddgs）不走插件开关——列表显示 not enabled 但功能照常在用。判断启用状态先 grep config.yaml，别只看插件列表。

## 工具集审计（hermes tools list）

- 一次看全：已启用/禁用工具集 + MCP servers 列表
- 判读要点（本机实测）：
  - context_engine = 空壳扩展点（tools 列表为空），无实际工具，默认禁用正常
  - video_gen 工具要付费后端 key（xAI/Veo）；bfl（FLUX 3 视频）免费走 Nous gateway——用户已有外部视频管线时 video_gen 无增量
  - MCP server 的 config `enabled: false` 是用户 MCP 铁律（默认关、用完即关），不是故障，别"修"

## 候选开启项评估框架（四查，2026-08-14 确立）

用户问「XX 要不要开」时按四查评估，每条结论带证据（用户铁律：下结论必须带证据来源）：

1. **现有管线覆盖查**：该能力用户已有通道是否已覆盖？（A2A vs delegate_task 同机并行 / Tailscale 远程网关 9119 / 飞书 + API Server 8642；video_gen vs Seedance+RunningHub+ComfyUI）
2. **最小必要查**：用户偏好方案收敛、拒绝锦上添花——低价值可选默认不推（spotify、可观测性类）
3. **生态配套查**：协议类先查有没有 peer——无兼容对象 = 插座没插头，不开（A2A 案例）
4. **成本查**：免费优先（web-brave-free / ddgs / stt 本地 faster-whisper / disk-cleanup / security-guidance），付费 key 按需

## 外部框架评估（非 Hermes 生态，DeepSeek Harness 案例 2026-08-14）

用户问别的 agent 框架/工具时：
- 先抓官方仓库事实（README 中文版：开发者预览、官方明示「未来将出现破坏兼容性的变更」）
- 评估三问：①成熟度（开发者预览 = 不碰）②资产可迁移性（skills/知识库/cron/飞书集成不可迁移）③模型无关性（换框架 ≠ 换模型，当前 provider 链路无绑定）
- 结论模式：了解即可不迁移；顺带澄清它和用户在用模型的关系（dsh 是 V4 Flash benchmark 的测试框架）

## 用户追问模式（2026-08-14 实测）

「其他的呢 / 工具集呢 / A2A呢 / DS的harness」连问 = 用户要**一次给全量分类盘点**（✅建议 / ⚠️可选 / ❌不建议+一句话原因），不是逐项等确认。每轮答复覆盖该层全部候选，❌ 项也列出——用户会追问到每一类，先分类全量列出省得被追着补。
