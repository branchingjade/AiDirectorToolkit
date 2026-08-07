# 飞书文档评论处理管线（Hermes 侧）

评论 @ bot 的完整链路与排查手册。实测 2026-08-06。

## 事件流

```
飞书评论/回复 @ bot
  → drive.notice.comment_add_v1 (WebSocket 长连接推送)
  → plugins/platforms/feishu/adapter.py:3635 _on_drive_comment_event
  → plugins/platforms/feishu/feishu_comment.py handle_drive_comment_event
```

关键过滤（feishu_comment.py）：
- from == bot 自己的 open_id → 跳过（自触发）
- `to_open_id` != bot → 跳过（**必须 @ bot**，@ 是路由不是内容）
- notice_type 必须是 add_comment / add_reply

处理流程：解析 → OK reaction（已读回执）→ 并行拉文档 meta + 评论详情 → 按 is_whole 分支（全文评论拉全部全文评论做时间线 / 划词评论拉评论线程）→ 构建 prompt → AIAgent 生成 → 投递（whole 用 add_whole_comment，local 用 reply_to_comment，1069302 时 fallback 全文评论）→ 删 reaction。

## ⚠️ 最高频坑：@ bot 不回复 = 访问控制拒绝

**症状**：用户在文档评论里 @ bot，bot 没任何反应。

**根因**：评论访问控制默认 `policy=pairing`（配对制）。`~/.hermes/feishu_comment_rules.json` 和 `feishu_comment_pairing.json` 都不存在时，**所有用户被拒**——这是安全设计（防陌生人 @ bot 触发文档读取）。

**排查**（gateway.log）：
```
[Feishu-Comment] Event: notice=add_comment ... from=ou_xxx
[Feishu-Comment] User ou_xxx denied (policy=pairing, rule=top)
```
看到 `denied (policy=pairing, rule=top)` 即命中。`rule=top` 表示无文档级规则，落到顶层默认。

**修复**（两条路，推荐 members）：
1. **members 策略（团队协作推荐）**：创建 `~/.hermes/feishu_comment_rules.json`：
   ```json
   {"enabled": true, "policy": "members", "allow_from": [], "documents": {}}
   ```
   成员名单.json 里的所有人自动放行（含未来新成员），陌生人照拒。policy 三档：`allowlist`（显式白名单）/ `pairing`（配对）/ `members`（成员名单跟随）。
2. **配对单个用户**（热加载无需重启 gateway）：
   ```bash
   cd ~/AppData/Local/hermes/hermes-agent
   ./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules pairing add <open_id>
   # 验证
   ./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules status
   ./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules check docx:<token> <open_id>  # → ALLOWED
   ```

**⚠️ 生效时序坑**：规则文件是 mtime 热加载，但 `is_user_allowed` 的策略分支（如 members）是**代码**——改代码必须重启 gateway。若规则文件先改为新策略而 gateway 还在跑旧代码，旧代码不认识新策略会**拒绝所有用户**（比原来更严）。顺序：改代码 → 重启 → 再改规则文件，或同时完成后重启。

**被拒的评论不会事后补处理**——修复后需用户重新 @ 一次。

规则文件三级回退：`exact:docx:<token>` > `wiki:<token>` > `*` 通配 > 顶层。每个字段独立回退（enabled/policy/allow_from/project——project 字段可给文档指定项目归属，最高优先级）。规则文件 mtime 热加载。

## 评论会话机制（协作接入后）

- session key：`comment:{项目}:{from_open_id}`（未路由到项目时 `comment:doc:{type}:{token}:{open_id}`）——**按项目+人隔离**，多用户不串台
- 持久化到 `Obsidian Vault/_hermes/评论会话/<percent编码key>.json`（重启不丢；2026-08-07 起迁入 vault），TTL 1h、50 条
- 与聊天会话（state.db）完全隔离：不进会话列表、不触发聊天路由、不出现在桌面端
- 评论 agent：admin（妖玉）`skip_memory=False` 加载全局记忆；member `skip_memory=True` 隔离防泄露；`skip_context_files=True` 恒开（项目上下文走手动注入）

## 2026-08-06 协作接入改造（已实施）

评论 @ 接入多用户协作体系，新增：

| 文件 | 作用 |
|---|---|
| `plugins/platforms/feishu/feishu_comment_collab.py` | 路由/成员/画像/项目上下文/会话持久化/观察沉淀/thread-local commenter+project/Obsidian 访问层 |
| `tools/feishu_comment_obsidian_tools.py` | Obsidian 笔记搜索/读取（admin 全 Vault；member 仅项目目录+剧本库；路径穿越防护在 `resolve_note_path`） |
| `toolsets.py` | 注册 `feishu_comment` toolset（obsidian 2 工具） |

**⚠️ kanban 工具已于同日摘除**（用户拍板「kanban 归 AI，人协作走飞书原生 @」）：`feishu_comment_kanban_tools.py` 已删除，`resolve_assignee`/`member_directory` 已删。评论链路只保留知识/内容能力（项目问答/检索/生产），不做流程中介。完整最终形态见 [`comment-collab-architecture.md`](comment-collab-architecture.md)。

行为变化：
- prompt 注入：成员真名（时间线显示名字而非 open_id）+ 画像 + 项目主文档/复盘（截断 6000 字符）+ 角色规则
- 项目路由：rules 文件 `project` 字段 > `会话路由.json` documents 映射 > 项目词典标题匹配（命中自动写回 `documents: {file_token: {project, space: "文档评论"}}`）
- 回复自动 @ 发起人（local: person element；whole: mention_user element）；投递重试 3 次（间隔 2s）
- 评论里发「评论状态/会话状态/协作状态」→ 直接返回状态报告（不走 agent）
- 画像沉淀：prompt 指示 agent 输出 `OBSERVATION: <事实>` 行，代码剥离并写入 `成员画像/<真名>.md`（低频去重，每天 ≤2 条）
- 并发锁：per-session-key asyncio.Lock（同文档连发 @ 串行处理）

## 自检发现并修复的坑（2026-08-06）

1. **会话文件 key 碰撞**：`_safe_key` 不能只替换非法字符为 `_`（中文项目名全变同形 `_`，「伏妖记」「犬子无双」同用户会话互相覆盖）。正确：`urllib.parse.quote(key, safe="").replace("%", "_pct_")`——percent 编码防碰撞。
2. **kanban 中文 board 名报错**：`kb.connect(board='伏妖记')` ValueError（slug 限小写字母数字/连字符/下划线）。工具内 `_resolve_board_slug`：先按 list_boards 的 `name` 匹配 → 再按 slug 直用。
3. **triage 状态认领断链**：`create_task(triage=True)` 落 triage，`claim_task` 只认 ready → 协作流程卡死。**派活必须用默认 create（落 ready）**，triage 只用于审核流。
4. **状态指令分支跳过 reaction 清理**：早期 `return` 直接退出会跳过文件尾部 `delete_comment_reaction`，OK 回执残留。改为 status_report 标志 + 统一投递路径。
5. **member 开全局记忆泄露风险**：admin 的评论回复发在**公开评论**里，prompt 注入"不得泄露内部配置/凭据/记忆原文"防护。
6. **tool_result(字符串) 测试坑**：`tool_result("文本")` 返回 JSON 字符串字面量（`"文本"`），测试代码 `json.loads` 一次解包得到 str，不要 `.get()`。

## 工具开发注意

- 工具发现机制：`tools/` 目录自动扫描 + `registry.register(name, toolset, schema, handler, check_fn, ...)`（`tools/registry.py`，有 discovery cache 按 mtime 重建）
- 评论 agent 的工具 client 注入：`tools.feishu_doc_tool.set_client/get_client`（thread-local）；角色/项目上下文用 `collab.set_commenter/set_project`（thread-local，agent 工具 handler 同线程可读）
- ⚠️ 改的是 hermes-agent 源码：`hermes update` 会覆盖，升级后需重打补丁（feishu_comment*.py、feishu_comment_obsidian_tools.py、toolsets.py 的 feishu_comment toolset 四处）

## 评论 API 侧知识（lark-cli）

- `drive +list-comments --comment-scope whole/partial`、`--solved-status all`
- 全文评论（is_whole=true）和已解决评论**不支持回复**（1069302）
- `--content` 的 reply_elements 支持 text / mention_user（@人，open_id）/ link（仅飞书云文档 URL）；text 总长 ≤10000 字符
- docx 评论定位：`drive +list-comments --need-relation` 返回 `relation.relation.positionInfo.blockID`，可映射到 `docs +fetch --detail with-ids`
