# 飞书 open_id → 真名解析（sender name resolution）

## 核心结论（2026-08-05 实测）

| 身份 | 命令 | 结果 |
|---|---|---|
| bot | `lark-cli contact +get-user --user-id ou_xxx --as bot` | 只返回 open_id/union_id，**无 name 字段**（应用未开通讯录权限时） |
| user | `lark-cli contact +search-user --user-ids ou_1,ou_2 --as user` | 返回 `localized_name` 真名，**稳定可用** |

## Hermes adapter 自带解析（但受权限限制）

`plugins/platforms/feishu/adapter.py`：
- `_resolve_sender_name_from_api`（约 4174 行）调 `contact.v3.user.get`（GetUserRequest）解析真名，取 `name` / `display_name` / `nickname` / `en_name`
- 结果缓存于 `_sender_name_cache`（约 1509 行定义，TTL 过期）
- 失败静默（logger.debug），不阻塞消息管线
- 应用无 `contact:user.base:readonly` 权限 → bot 身份拿不到 name → `sessions.display_name` 回退为 chat_id（DM）/ 群名（group）

## 症状（摘要 cron 显示「用户 A/B/C/D」）

- `state.db` sessions 表：DM 会话 `display_name` = chat_id（oc_xxx），群聊 = 群名（如「开工」）
- `channel_directory.json`：同样只有 chat_id / 群名，无用户真名
- 摘要类 cron（如「飞书每日摘要-其他人对话」job 88ab7ff66681）SQL 只 SELECT `user_id`（=open_id）、`chat_type`、`title`、`preview`——LLM 没有真名可用，只能编「用户 A/B/C/D」

## 修复模式：cron 里批量反查

1. SQL 查 sessions 表拿 `user_id`（open_id）列表
2. 加一步：`lark-cli contact +search-user --user-ids <逗号分隔 open_id> --as user` 批量反查（注意 user 身份，不是 bot）
3. 输出 `[真名] 摘要` 替换「用户 A/B/C/D」

实测映射示例（2026-08-05）：
- ou_88d69f… → 全志越（白泽刺字）
- ou_c86a9… → 施文皓（梦魇战斗场景）
- ou_5373d… → 苑津铭（工友鼓掌/日常问候）
- ou_68719… → 徐学环（伏妖记剧本评估）
- ou_94566… → 魏宁馨（绿联NAS邀请链接）

## 根治方案

飞书开发者后台给应用开 `contact:user.base:readonly`（**仅企业自建应用可开**，商店应用拿不到）→ adapter 自动解析并缓存真名，`display_name` 自动变真名，所有下游（channel_directory、cron）受益。

**开通后验证**：`lark-cli contact +get-user --user-id ou_xxx --as bot` 返回 `data.user.name` 非空即生效。需 `hermes gateway restart`；历史会话 display_name 不回填，只有新消息触发解析。

## 权限开通后仍有个别用户「用户+N」脱敏（2026-08-05 实测）

即使权限全开、可用范围=所有员工，个别用户 bot 身份仍返回 `name: "用户133976"`。这是**账号资料问题**（该用户 `name` 字段未设置，真名在 `localized_name`），不是权限问题。判别链：

1. 同群其他成员 bot 全部正常、唯独此人「用户+N」→ 非权限问题
2. user 身份 `+search-user` 返回 `localized_name: "魏宁馨"` vs bot `+get-user` 返回 `name: "用户133976"` → 字段差异实锤

关键事实：`localized_name` 只有 `contact/search/user` 接口返回，**仅 user 身份可用**（bot 报 `--as bot is not supported, this command only supports: user`）；原生 `contact/v3/users/batch_get`、`/users/batch` 均 404 不存在；`user_profiles batch_query` 同样仅 user 身份。

治本：让该用户补全飞书姓名资料。治标：脚本对「用户+N」保持原名不误标。

## 应用权限优先的最终实现（摘要 cron 用 bot 身份反查）

用户原则「能应用权限做的就不要走用户权限」——cron 反查优先 bot 身份。独立脚本 `~/AppData/Local/hermes/scripts/feishu-daily-digest.py`（2026-08-05 落地，job 88ab7ff66681 已切换）：

1. SQL 查 `state.db` sessions 表，`WHERE source LIKE '%feishu%' AND user_id != '<自己 openId>' AND started_at > now-86400`
2. 去重 open_id 列表 → **bot 身份**逐个 `lark-cli.cmd contact +get-user --user-id <ou_> --as bot` 反查 `data.user.name`（间隔 0.15s 防 5 QPS 限流）
3. 输出 JSON：session_id / user_id / user_name / chat_type / title / msg_count / preview
4. cron prompt 规则：有 user_name 用真名 `[全志越]`；group 无真名用 `[群聊用户]`；dm 无真名用 `[用户X]`

要点：
- **Windows 下 subprocess 调 lark-cli 必须用 `.cmd`**（`shutil.which("lark-cli.cmd")`），sh 脚本 CreateProcess 无法执行
- **排除条件必须用当前 openId**（`lark-cli auth status --json --verify` 的 `identities.user.openId`），换应用后会变——旧 openId 会导致自己的会话被当成「其他人对话」混入摘要
- 群聊内系统通知（如 NAS 邀请链接转发）显示为「用户+数字」是正常的——系统账号非真人

## 坑

- `+search-user` 是 **user 身份专属**；bot 身份用 `+get-user`，但权限不足时返回无 name
- open_id 是 app-scoped：换应用后 open_id 全变，需重新反查（见 SKILL.md「换应用后 user openId 会变」）
- 反查结果建议缓存（SQLite/JSON），避免每日重复调用；飞书自定义 bot 限速 5 QPS / 100 QPM（见 `references/rate-limits.md`）
