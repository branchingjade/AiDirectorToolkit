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
