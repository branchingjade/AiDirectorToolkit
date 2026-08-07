# 飞书文档评论链路架构（2026-08 实测落地）

文档评论 @ bot 是协作体系的**附加入口**（主入口仍是聊天）。能力：项目上下文问答、Obsidian 检索、成员画像个性化、内容生产。**流程类能力（派活/认领）已摘除**——kanban 归 AI，人协作走飞书原生 @（见 feishu-multi-user-collab skill 第 3 章）。

## 入口矩阵

| 入口 | 通道 | 能力 |
|---|---|---|
| 飞书私聊/群/话题 | 成员主入口 | 路由/画像/kanban 只读 |
| 桌面会话 | 妖玉入口 | 全量 |
| 文档评论 @ bot | 评审现场附加入口 | 项目上下文/画像/Obsidian 检索/内容生产 |

## 事件流与源码

```
drive.notice.comment_add_v1 (WebSocket)
  → adapter.py _on_drive_comment_event
  → plugins/platforms/feishu/feishu_comment.py handle_drive_comment_event
      1. 过滤：self-reply / to_open_id（必须 @ bot）/ notice_type
      2. 访问控制：feishu_comment_rules.json（exact doc > wildcard > top 三级）
      3. 成员解析：collab.get_member → 真名/角色（is_admin）
      4. 项目路由：rule.project > 路由表 documents > 标题词典匹配（持久化）
      5. 拉时间线（whole=全文评论 / local=划词评论）
      6. 注入：身份+画像+项目主文档+复盘+角色规则+观察指令
      7. 状态指令检测（「评论状态/会话状态/协作状态」→ 直答不跑 agent）
      8. AIAgent 运行（per-session 并发锁）→ 剥离 OBSERVATION 行写画像
      9. 投递（重试3次，回复 @ 发起人，统一尾部 reaction 清理）
```

## 协作层模块（feishu_comment_collab.py）

- 成员：`成员名单.json`（open_id→{name,role}），`is_admin` / `display_name`
- 路由：`resolve_project(type, token, title)`——rules project 字段 > `会话路由.json documents[token].project` > 项目词典标题匹配并持久化
- 项目上下文：`load_project_context(project)` 读 `<项目>/<项目>.md` + `<项目>复盘.md`，各半共 6000 字符
- 画像：`成员画像/<真名>.md` 注入 + `record_observation` 沉淀（agent 输出 `OBSERVATION: <事实>` 行，代码剥离后写入；日限 2 条去重）
- 会话：`comment:{project}:{open_id}`（未路由降级 `comment:doc:{type}:{token}:{open_id}`），磁盘持久化 `Obsidian Vault/_hermes/评论会话/`（TTL 1h、50 条；文件名 percent-encode 防中文/冒号碰撞；2026-08-07 起从 `~/.hermes/comment_sessions/` 迁入 vault）
- Obsidian 访问：`resolve_note_path`（防穿越 + 权限范围）、`search_notes`

## 权限边界（实测）

| 操作 | admin（妖玉） | member |
|---|---|---|
| 全局记忆（skip_memory） | 加载（prompt 含泄露防护提示） | 隔离 |
| Obsidian 全库 | ✅ | ❌ |
| Obsidian 项目目录 + 剧本库 | ✅ | ✅ |
| 成员画像目录 | ✅ | ❌ |
| 路径穿越 | ❌ | ❌ |
| 访问策略 | `feishu_comment_rules.json` `policy: members`（成员名单自动放行，陌生人拒绝） | 同左 |

## 源码文件清单（⚠️ hermes update 会覆盖，需重打）

> **重打工具（2026-08-07 建）**：`~/Documents/Hermes/scripts/patches/reapply-patches.py`
> - 存档：同目录 `hermes-local-patches.diff`（5 个修改文件 diff）+ `feishu_comment_collab.py`/`feishu_comment_obsidian_tools.py`（2 个新文件备份）
> - 用法：`python reapply-patches.py`（dry-run 检测）→ `python reapply-patches.py --apply`（应用+语法验证）
> - 自带「已应用检测」：检测到关键标记（run.py 的 OBSERVATION 剥离注释/collab 的 record_project_memory）即跳过
> - update 机制实证：`hermes update` 会自动 `git stash push --include-untracked`（改动不丢）→ `git pull` → `git stash apply`；官方更新若改动同一文件会冲突，此时用本脚本恢复或 `git apply --3way`


- `plugins/platforms/feishu/feishu_comment.py`（主流程改造）
- `plugins/platforms/feishu/feishu_comment_collab.py`（新建，协作层；**SESSIONS_DIR 已改为 `VAULT_ROOT/_hermes/评论会话`**——2026-08-07 评论会话记忆迁入 Obsidian，重打时记得同步此改动；**另含 `record_project_memory`/`resolve_project_for_session`**——IM 消息管线项目记忆实时沉淀函数，同批加入）
- `gateway/run.py`（**feishu IM 实时沉淀钩子**——2026-08-07 加两处：①prompt 注入 OBSERVATION:/PROJECT_MEMO: 指令 ②final_response 剥离标记并写 Obsidian 成员画像/项目记忆；重打时记得同步）
- `plugins/platforms/feishu/feishu_comment_rules.py`（project 字段 + members 策略）
- `tools/feishu_comment_obsidian_tools.py`（新建，obsidian_search/read）
- `toolsets.py`（feishu_comment toolset：obsidian 2 工具）

## kanban 边界（AI 系统，非人待办）——2026-08 用户拍板

- dispatcher 每 60s 对 **ready 任务** spawn `hermes -p <assignee> chat -q` 自动执行
- **assignee 非真实 Hermes profile 的 ready 任务被跳过不 spawn**（人工 lane 安全，kanban_db.py 注释明确：terminal lane "should NEVER auto-spawn"）
- claim_task 只接受 **ready**；triage 状态任务认领不了（create_task 默认落 ready；triage=True 会卡死人工流程）
- board slug 只限小写英文 1-64 字符（中文项目用拼音 slug + `--name` 中文：伏妖记→fuyuji）
- 工具注册：新工具放 `tools/` 下 `registry.register(name, toolset, schema, handler, check_fn...)`，toolsets.py 加 toolset 条目，自动扫描发现（tool_discovery_cache.json 缓存）
- 验证：`python -m plugins.platforms.feishu.feishu_comment_rules status|check docx:<token> <open_id>`
