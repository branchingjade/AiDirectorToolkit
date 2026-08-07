---
name: feishu-comment-collab
description: "Use when 飞书文档评论不回复/评论@/评论权限/评论会话/评论协作功能排障与扩展。"
version: 1.0.0
tags: [feishu, comment, collab, kanban, obsidian, gateway]
---

# Hermes 飞书文档评论协作功能

飞书文档里 @ bot 会触发 Hermes 评论处理管线（`drive.notice.comment_add_v1` 事件），2026-08 起已接入多用户协作体系。本 skill 覆盖该子系统的架构、配置、诊断与扩展。

## 架构（模块图）

```
飞书文档评论 @bot
  → WebSocket 事件 drive.notice.comment_add_v1
  → adapter.py:3635 → _on_drive_comment_event → handle_drive_comment_event
  → feishu_comment.py       # 主流程：过滤/权限/时间线/prompt/投递
  → feishu_comment_rules.py # 访问控制规则解析（独立 leaf 模块）
  → feishu_comment_collab.py# 协作层：成员/路由/画像/项目上下文/会话持久化
  → tools/feishu_comment_kanban_tools.py    # kanban 4 工具
  → tools/feishu_comment_obsidian_tools.py  # Obsidian 2 工具
```

关键点：
- **事件入口已在 adapter.py 订阅**，不需要开发者后台额外配事件（WebSocket 模式自动收）
- 过滤条件：self-reply 跳过、`to_open_id` 必须是 bot（评论里 @ bot 才有）、notice_type ∈ {add_comment, add_reply}
- agent 配置：`skip_context_files=True`；`skip_memory` 按角色——admin 加载全局记忆、member 隔离；toolsets = feishu_doc + feishu_drive + feishu_comment

## 访问控制（最常见排障点）

规则文件 `~/AppData/Local/hermes/feishu_comment_rules.json`（**mtime 热加载，改完不用重启**；但代码分支改动需重启）：

```json
{ "enabled": true, "policy": "members", "allow_from": [], "documents": {} }
```

三档解析：exact `docx:<token>` > wildcard `*` > top-level。每字段独立回退。

三种策略：
| policy | 行为 |
|---|---|
| `allowlist` | 仅 `allow_from` 列出的 open_id |
| `pairing` | 配对名单（`feishu_comment_pairing.json`） |
| `members` | **成员名单.json 里的所有人自动放行**（新成员加入自动生效，团队协作默认） |

**默认值坑**：规则文件不存在时 policy 默认 `pairing` 且名单为空 → **所有用户被拒**。症状：日志 `[Feishu-Comment] User ou_xxx denied (policy=pairing, rule=top)`，用户评论 @ bot 无回复。

配对 CLI：
```bash
cd ~/AppData/Local/hermes/hermes-agent
./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules pairing add <open_id>
./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules status   # 看配置+配对名单
./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules check <type:token> <open_id>  # 模拟访问检查
```

诊断命令（`check` 模拟 + gateway.log 的 `[Feishu-Comment]` 日志）是排查"评论不回复"的第一动作：事件有没有到（START 日志）→ 有没有被拒（denied）→ agent 跑没跑（Step 4）→ 投递成没成（Step 5）。

## 会话模型

- key：`comment:{项目}:{open_id}`（按项目+人隔离）；未路由到项目时降级 `comment:doc:{type}:{token}:{open_id}`
- **磁盘持久化**：`Obsidian Vault/_hermes/评论会话/<percent-encoded-key>.json`（重启不丢；2026-08-07 起迁入 vault，此前 `~/AppData/Local/hermes/comment_sessions/`）
- TTL 1h 无活动过期；最多 50 条 user/assistant 消息
- 同一文档同一人连续 @ 有上下文；不同项目/不同人完全隔离

## 协作层（feishu_comment_collab.py）

- **项目路由**：rules 文件 `project` 字段 > 会话路由.json `documents` 映射 > 项目词典标题匹配（命中自动持久化）
- **项目上下文注入**：路由命中后加载 `Obsidian Vault/<项目>/<项目>.md` + `<项目>复盘.md`（共 6000 字符截断）
- **成员/画像**：成员名单.json（open_id→名字/角色）注入 prompt；成员画像 md 注入；回复可点名
- **观察沉淀**：prompt 指示 agent 输出 `OBSERVATION: <事实>` 行，代码剥离后按克制规则写入画像（同文本去重、每天≤2 条）
- **权限分级**：admin（妖玉）全量（记忆开关开、能派任务）；member 只读+认领（记忆隔离）
- **指令直答**：评论含"评论状态/会话状态/协作状态"→ 不跑 agent，直接回状态报告

## 工具集（feishu_comment toolset，6 个）

- kanban：create（**仅 admin**，中文负责人名自动解析）/ list / claim / complete
- Obsidian：search / read（**权限分级**，见 references/obsidian-note-tools.md）

工具身份通过 thread-local 传递：`collab.set_commenter(open_id)` + `set_project(project)`（feishu_comment.py 在 agent 运行前设置，handler 读取做角色校验）。

## Pitfalls

- **Windows 文件名坑**：会话文件名不能含 `:`，中文若替换成 `_` 会碰撞（伏妖记/犬子无双 同用户互相覆盖）——必须 percent-encode
- **kanban 中文 board 名直接报错**：slug 只允许小写英文数字连字符下划线，中文项目用拼音 slug（伏妖记→fuyuji）+ `--name 中文`。评论 kanban 工具已做名字→slug 自动映射
- **triage 任务认领断链**：`create_task(triage=True)` 落 triage 状态，`claim_task` 只接受 ready → 协作任务必须默认创建（落 ready）
- **dispatcher 不会动人工任务**：kanban dispatcher 每 60s spawn ready 任务（`hermes -p <assignee>`），但 assignee 非真实 Hermes profile（如成员 open_id）的任务**永不自动 spawn**——人协作任务天然隔离，详见 references/kanban-collab.md
- **`hermes update` 会覆盖所有源码改动**（feishu_comment*.py / toolsets.py / tools/*）——升级后需重打补丁
- **规则文件热加载 ≠ 代码热加载**：改 `feishu_comment_rules.py` 代码（如新增策略）必须重启 gateway；规则文件本身（JSON）不用

## 相关

- [kanban 协作机制细节](references/kanban-collab.md) — dispatcher 行为、slug 规则、状态机
- [Obsidian 笔记工具权限模式](references/obsidian-note-tools.md) — 范围表、路径穿越防护
