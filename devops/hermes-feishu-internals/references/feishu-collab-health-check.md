# 飞书三渠道健康度检查脚本（feishu-collab-health.py）

> 脚本位置：`~/AppData/Local/hermes/scripts/feishu-collab-health.py`（主工作区之外，非 git 仓库，`hermes update` 不覆盖）
> 调用：`python3 scripts/feishu-collab-health.py [hours]`（默认 48h）
> 输出：结构化文本报告（供 cron / 人工巡检）

## 1. 三渠道健康度模型（2026-09-03 改造口径）

飞书协作渠道在 `state.db` 中按数据源分三档：

| 渠道 | 过滤键 | 数据来源表 | 关键字段 |
|---|---|---|---|
| **私聊 DM** | `source='feishu' AND session_key LIKE 'feishu:dm:%'` | `sessions` | `user_id` (=open_id) / `message_count` |
| **群聊 group** | `source='feishu' AND session_key LIKE 'feishu:group:%'` | `sessions` | `chat_id`（从 `session_key` 提取） |
| **文档评论** | `sessions` 中 `source='comment'`（**不是** `feishu`） | `sessions` + `messages`（session_id=`comment-doc:<file_type>:<file_token>`） | `title`（文档标题）/ `user_id`（评论发起人 open_id） |

**关键陷阱**（旧版脚本读错的口径）：
- 评论渠道**不是** `source='feishu'`——侧边栏独立平台按 `source='comment'` 过滤
- 评论历史**不是** `Obsidian Vault/_hermes/评论会话/comment_*.json`——2026-09-03 起迁入 `state.db messages` 表
- 群聊**不是** `chat_type='group'` 单独判——它是 `source='feishu'` + `session_key LIKE 'feishu:group:%'`（**而且** `chat_type` 字段也常为 `group` 但有 15 条历史为 NULL，**双判才稳**）

## 2. 脚本核心函数（解释为什么改）

### 2.1 `im_activity(since_ts)` — DM 私聊
- 读 `sessions` 表 `source LIKE '%feishu%'` 且 `session_key LIKE 'feishu:dm:%'`
- 按 `user_id` (=open_id) 聚合
- 收集所有 `chat_key` 用于 `route_coverage`（路由表覆盖检查）

### 2.2 `group_activity(since_ts)` — 群聊（2026-09-03 新增）
- 读 `sessions` 表 `chat_type='group' AND started_at > ?`
- 提取 `chat_id`（从 `session_key` 切 `:group:` 后取下一段）
- 列出**所有历史活跃群**（不限 HOURS 时间窗，state.db 全量去重）
- 配合 `group_whitelist_coverage` 报警"已知活跃群未在 group_rules 登记"

### 2.3 `comment_activity(since_ts)` — 评论（2026-09-03 改口径）
- ❌ 旧：扫 `_hermes/评论会话/comment_*.json`（2026-09-03 之前实现，gateway 重启 = 历史丢）
- ✅ 新：`messages` 表 `session_id LIKE 'comment-doc:%'`
- 按 session_id 分组，**user_id 从第一条 user 消息 content 里的 `ou_xxx` 提取**（评论事件 payload 在 user 消息里带 open_id）
- 适用「评论 channel 活跃成员」归到对应用户

### 2.4 `route_coverage(keys)` — 路由覆盖
- DM 渠道的 chat_key 必须登记进 `Obsidian Vault/_hermes/会话路由.json`
- 群聊/评论渠道**不**走路由表（前者靠 group_rules，后者靠 rules 文件 project 字段）

### 2.5 `group_whitelist_coverage()` — 群聊白名单（2026-09-03 新增）
- 从 `state.db sessions WHERE chat_type='group'` 查所有历史活跃 `chat_id`
- 对比 `config.yaml` `platforms.feishu.group_rules` 显式登记
- **没**登记的群 → 报警"走全局默认 `require_mention=true`"——这是 2026-09-03 开工群 17 天停摆的根因
- 修复：每个已确认协作活跃的群必须**显式** `hermes config set platforms.feishu.group_rules.<chat_id>.require_mention false`

### 2.6 `profile_coverage()` — 画像覆盖
- 成员名单.json（12 人）vs 成员画像/目录 .md 文件
- 报告缺画像 / 空模板（待沉淀）

### 2.7 `profile_injection_counts(since_ts)` / `profile_lifecycle()` / `profile_time_match()` — 画像使用率
- gateway.log grep `Profile injected for <名>` 计数
- 画像 mtime > 14d 算 stale（活跃成员） / > 30d 算 cooling（非活跃）

## 3. 输出节段对照

| 段 | 数据源 | 何时看 |
|---|---|---|
| 【1】成员活跃度（IM + 评论） | sessions + messages | 找活跃成员 |
| 【2】路由覆盖 | `会话路由.json` | 新 DM 群没响应 |
| 【3】画像覆盖 | `成员画像/*.md` | 新成员 / 画像系统 |
| 【3b】画像使用率 | gateway.log | 画像注入是否生效 |
| 【3c】画像生命周期 | 文件 mtime | 哪些画像需要更新 |
| 【3d】画像时效匹配 | sessions + mtime | 画像滞后于活动 |
| 【4】项目记忆 | （已迁 Hindsight） | 永远显示「已迁」 |
| 【5】评论线程 | state.db messages | 评论渠道活跃度 |
| 【5b】群聊渠道 + 白名单 | state.db + config.yaml | 群消息停摆时第一查 |

## 4. 实战用法

### 日常巡检（cron 周日 8:30 已配置）
```bash
cd ~/AppData/Local/hermes
python scripts/feishu-collab-health.py 168   # 一周视角
```

### 排障时
- 「群里 @bot 没反应」→ 看【5b】白名单覆盖 → 没登记 = 走全局 require_mention=true → 修 `hermes config set platforms.feishu.group_rules.<chat_id>.require_mention false`
- 「侧边栏飞书评论没新会话」→ 看【5】评论线程（state.db messages）→ 没数据 = gateway 没加载新代码 / feishu_comment.py 旧版还跑着 → 跑 `tail -20 logs/gateway.log | grep "Comment session saved"` 看是不是新持久化层
- 「成员活跃度不对」→ 看【1】 + 【3b】组合——会话在但画像没注入 = log tag 变了

### 修改脚本注意事项
- 脚本在 `scripts/` 目录（HERMES_HOME 下，不在 git 仓库）
- 改后**不需要** git commit，但**必须**重启时同步改 `cron-monitor.py`（如果有定时调用）
- 不要把 `chat_type='group'` 改成只读 `chat_type='dm'` 之类——`chat_type` 字段历史有 15 条 NULL，必须**双判**（`source='feishu' AND session_key LIKE 'feishu:group:%'` 是更稳的兜底）

## 5. 历史归档

`Obsidian Vault/_hermes/评论会话/archive/` 下 23 个旧 JSON 文件（2026-09-03 之前实现留下的）——保留**原文证据**，不删不导。新机制不走这条路。
