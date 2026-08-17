---
name: hermes-feishu-internals
description: "飞书评论agent内部机制：事件链、访问控制排障、协作扩展、kanban评论工具。触发词：评论@没反应。"
version: 1.0.0
tags: [feishu, hermes, comment, kanban, internals]
---

# Hermes 飞书内部机制（评论 agent / 协作扩展）

Hermes 飞书平台除聊天消息外还有一套独立的**文档评论 agent** 管线。本 skill 记录其架构、排障方法和协作扩展设计。评论功能相关的一切调试从这里开始。

## 1. 评论事件处理链

```
飞书 WebSocket 推送 drive.notice.comment_add_v1
  → plugins/platforms/feishu/adapter.py:3635（事件分发）
  → _on_drive_comment_event → handle_drive_comment_event
  → plugins/platforms/feishu/feishu_comment.py（主流程）
```

主流程：解析事件 → 过滤（self-reply / 必须 @ bot / notice_type）→ **访问控制** → 加 OK reaction → 并行取文档元数据+评论详情 → 分支（whole 全文评论拉时间线 / local 划词评论拉线程）→ 构建 prompt → 独立 AIAgent 生成回复 → 投递（whole 追加评论 / local 回复线程，1069302 回退）→ 清理 reaction。

**日志前缀 `[Feishu-Comment]`**：所有关键步骤有日志，排障第一动作就是 grep。

## 2. 访问控制（评论 @ 没反应的常见根因）

规则文件 `~/AppData/Local/hermes/feishu_comment_rules.json`（**mtime 热加载，无需重启**）+ 配对文件 `feishu_comment_pairing.json`。三级回退：exact doc > wildcard `*` > 顶层默认。默认配置（无规则文件）= `policy: pairing`，**所有未配对用户被拒**——这是"@ 了没回复"的头号原因。

三种策略（`is_user_allowed`）：
- `allowlist`：`allow_from` 列出的 open_id 放行
- `pairing`：配对名单（CLI 管理：`./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules pairing add <open_id>`）
- `members`（推荐团队场景）：**成员名单.json 里的所有人自动放行**，新成员自动获得权限，陌生人照拒

排障命令：
```bash
cd ~/AppData/Local/hermes/hermes-agent
./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules status   # 看策略/配对/规则
./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules check docx:<token> <open_id>  # 模拟访问判定
grep "Feishu-Comment" <logdir>/gateway.log | tail   # 事件有没有到、被谁拦了
```

**⚠️ 改代码后必须重启 gateway**：规则文件是热的，但 `is_user_allowed` 等代码改动不是——重启前新规则文件可能被旧代码全部拒绝（比原来更严）。

**⚠️ policy 静默回退 pairing（hermes update 抹补丁后遗症，2026-08-13 实测）**：规则文件写着 `members`、成员名单里有该用户，但日志却报 `denied (policy=pairing, rule=top)`——根因不是规则配置，是 **`hermes update` 把本地补丁代码覆盖了**：`feishu_comment_rules.py` 的 `_VALID_POLICIES` 不含 `members` 时，`load_config()` 把未知 policy 静默回退成 `pairing`（`if policy not in _VALID_POLICIES: policy = "pairing"`），所有未配对用户全被拒。诊断三步：①CLI `check docx:<token> <open_id>` 实测显示 ALLOWED 但 gateway 日志 denied = 进程内代码旧（同机同文件，CLI 用新代码、常驻进程用旧代码）；②对比 `feishu_comment_rules.py` mtime 与 gateway 启动时间——代码 mtime > 启动时间 = 运行中进程加载的是旧代码；③`git status` 查 UU 冲突文件（update 中断残留，`MERGE_HEAD` 可能已不在）。修复：`reapply-patches.py --apply` 重打（整体失败用 `git apply --3way` 手动解冲突）+ 恢复被删文件 + 重启 gateway，再 `check` 实测 ALLOWED 才算完。⚠️ 其他 agent 声称"已更新 skill"必须 grep 验证，self-report 不算数。

## 3. 评论 agent 特性（与聊天 agent 完全隔离）

- 独立 AIAgent：`quiet_mode=True`、`skip_context_files=True`、工具集 `feishu_doc`/`feishu_drive`/`feishu_comment`
- **`skip_memory` 按角色**：admin 加载全局记忆（用户明确要求），member 保持隔离防泄露——评论回复是公开的，团队成员都能看到
- **会话 key**：`comment:{项目}:{用户}`（协作模式）/ `comment:doc:{类型}:{token}:{用户}`（未路由降级）——按人隔离，多用户不串台
- 会话**磁盘持久化**（`Obsidian Vault/_hermes/评论会话/`，2026-08-07 起迁入 vault；此前 `~/AppData/Local/hermes/comment_sessions/`），重启不丢，TTL 1h，上限 50 条；TTL 后归档到同目录 `archive/`（不删，原始对话保留）
- **评论会话不进 state.db、客户端侧边栏不可见**（2026-08-10 实测）：评论 agent 是独立 AIAgent（`quiet_mode=True`），会话只写 `_hermes/评论会话/*.json`，**完全不写 state.db sessions 表**。侧边栏「FEISHU」分类（读 `GET /api/profiles/sessions` / list_sessions_rich，只含聊天会话）永远看不到评论会话——这是数据管线隔离，不是显示 bug。用户问「评论会话在客户端哪能看到」先答根因（数据不在 state.db），看评论会话只能去 Obsidian 目录；若要让其进 Hermes UI，需插件后端直接读 JSON 目录（如 channel-sessions 加评论视图），不能靠侧边栏
- **文件名编码格式与解码**：会话 key = `comment:{项目}:{open_id}`（**两个冒号**），percent-encode 后 `%` → `_pct_`，文件名形如 `comment_pct_3A_<编码项目>_pct_3Aou_xxx.json`；归档文件在 open_id 后追加 `_YYYYMMDD_HHMMSS` 时间戳后缀。解码三步：① regex 剥离归档时间戳（`_\d{8}_\d{6}$`）② `_pct_` 还原成 `%` ③ `unquote` 后 `split(":")`（≥3 段且 parts[0]=="comment"，open_id 可能含 `:` 用 join 兜底）。⚠️ 两个实测坑：**不能切固定前缀 `comment_pct_3A_` 再解码**（会把首个 `%` 标记切残，项目名乱码如 `pct_E4��妖记`）；**不剥时间戳则归档会话 open_id 被污染**、真名反查失败。channel-sessions 插件 `service.py` 的 `_decode_comment_key` 是现成实现
- **消息结构（展示时拆三段）**：user 消息 = 完整 prompt 文本，含 `The user added a reply in "<doc>"`（或 comment）/ `Current user comment text: "<text>"` / `Original comment text: "<text>"`（可选）/ `Quoted content: "<text>"`（可选）+ timeline + 系统指令；assistant 消息 = 纯 markdown 回复。展示拆「在哪个文档评论 + 评论正文 + 引用原文」三段；JSON **不存单条消息时间**，只能按消息序从 `last_access` 倒推（60s/条）。解析实现参考 channel-sessions `service.py` 的 `_parse_comment_message`
- 回复自动 @ 评论发起人（person/mention_user element）
- 状态指令：评论里发「评论状态/会话状态」→ 直答不跑 agent
- 画像沉淀：prompt 指示 agent 输出 `OBSERVATION: <事实>` 行 → 代码剥离并写入成员画像（低频去重，一天≤2条）
- **并发模型：per-session 锁排队（2026-08-11 确认，无 interrupt/steer）**：`feishu_comment.py` `_session_locks`（`Dict[str, asyncio.Lock]`），`handle_drive_comment_event` 在 `async with lock` 内跑 agent（`run_in_executor`）。同 key（`comment:{项目}:{open_id}`）事件**串行排队**——agent 忙时新评论等锁，不丢不打断；不同 key（跨项目/跨用户/未路由文档）**并行**。与聊天 agent 的 gateway busy_input 三态（interrupt/queue/steer）完全无关——评论是事件驱动独立 agent 实例，无常驻会话可注入，天然 queue 语义。用户拍板「评论排队就行」不改（2026-08-11）

## 4. 评论协作扩展（接入多用户协作体系）

新增 `plugins/platforms/feishu/feishu_comment_collab.py`：成员身份（成员名单.json）、项目路由（规则文件 project 字段 → 路由表 documents → 词典匹配自动登记）、画像注入、项目上下文注入（`<项目>/<项目>.md` + `<项目>复盘.md`）、观察沉淀、持久化会话。详细设计与文件清单见 `references/comment-collab-design.md`。

## 5. kanban 评论工具（tools/feishu_comment_kanban_tools.py）

评论 agent 可派任务/认领/完成，工具注册在 toolset `feishu_comment`（toolsets.py）。要点：

- **绕过 dispatcher gate**：kanban_tools.py 的现成工具被 `HERMES_KANBAN_TASK` 环境变量门控（只在 dispatcher 派生的 agent 生效），评论 agent 用不了。自建工具直接调 `hermes_cli.kanban_db`（`connect(board)` + `create_task/list_tasks/claim_task/complete_task`）即可绕过
- **board slug 规则**：`[a-z0-9][a-z0-9_-]{0,62}`——中文项目名（伏妖记）不是合法 slug！现有 board 用拼音 slug + 中文 name（`fuyuji`/`quanzishuang`/`shouxinren`）。工具需按 name 查 `list_boards()` 映射 slug
- **create_task 状态机**：默认落 `ready`（可认领）；`triage=True` 落 triage（**无法 claim**——claim 只接受 ready→running）；`initial_status` 只允许 running/blocked
- **assignee 中文名解析**：成员名单.json 里名字→open_id 映射（`resolve_assignee`），agent 只需传中文名
- 角色校验：create 限 admin（thread-local commenter + `is_admin`），list/claim/complete 全员
- **`tool_result(字符串)` 返回 JSON 字符串字面量**（`'"文本"'`），测试时 `json.loads` 一次解包得 str，不是 dict——别用 `.get()`

## 6. 通用坑

- **Windows 文件名**：会话 key 含 `:` 和中文会报 WinError 123。percent-encode 后替换 `%`（`quote(key, safe="").replace("%", "_pct_")`）——简单替换非 ASCII 为 `_` 会让「伏妖记」和「犬子无双」**塌缩成同形文件名互相覆盖**
- **状态指令分支控制流**：任何提前 `return` 的分支都会跳过函数尾部的 reaction 清理——用统一投递流程（status_report 变量 + 尾部统一处理）
- **成员名单.json**：`admin: ["真名"]` + `成员: {open_id: {name, role}}`——妖玉=徐学环=ou_6871...（admin）。判断 admin 用 role 字段或真名在 admin 列表
- 项目文档命名规律：`<项目>/<项目>.md` 主文档 + `<项目>复盘.md` 复盘
- 工具发现机制：`tools/` 目录自动扫描注册（带 `tool_discovery_cache.json`），新工具文件无需手动挂载

## 参考

- `references/comment-collab-design.md` — 协作扩展完整设计（会话模型/路由/权限/测试方法）
- [feishu-gateway-setup](../feishu-gateway-setup/SKILL.md) — 网关配置与聊天消息层坑
- [feishu-multi-user-collab](../feishu-multi-user-collab/SKILL.md) — 多用户协作业务规则（user-owned）
- [lark-drive](../../lark-drive/SKILL.md) — 评论 CRUD 的 CLI 操作
