# Kanban 协作机制细节（评论工具实测沉淀，2026-08）

## board slug 规则

- slug 只允许：1-64 字符，小写字母数字 / 连字符 / 下划线，**不能以 `-` 或 `_` 开头**
- 中文项目名直接当 board 传会 `ValueError: invalid board slug`
- 现有约定：中文项目用拼音 slug + `--name 中文`（伏妖记→fuyuji、犬子无双→quanzishuang、手心人→shouxinren）
- 解析顺序（评论 kanban 工具的 `_resolve_board_slug`）：先按 `list_boards()` 的 `name` 精确匹配 → 再按 slug 正则判断直用
- 查现有板：`hermes_cli.kanban_db.list_boards()` 返回 `[{slug, name, ...}]`

## create_task 状态语义（关键）

```python
kb.create_task(conn, title=..., assignee=..., triage=True)  # → triage（待审/待分解）
kb.create_task(conn, title=..., assignee=...)               # → ready（无 parent 时）
kb.create_task(conn, ..., initial_status="blocked")         # → blocked（等人处理）
```

- `VALID_INITIAL_STATUSES = {"running", "blocked"}`——running 是 dispatcher 自动执行语义
- **triage 任务的坑**：`claim_task` 只接受 `ready`（ready→running）。triage 任务认领/完成都失败——协作"派任务给人"必须默认创建（落 ready），不要 triage
- `complete_task` 接受 `running|ready → done`

## dispatcher 行为（自动执行 vs 人工认领）

dispatcher（gateway 内嵌，`kanban.dispatch_in_gateway: true`，默认 60s tick）：
1. `recompute_ready`：todo→ready 提升
2. 对每个 `ready` 且 `claim_lock IS NULL` 的任务 spawn：`hermes -p <assignee> chat -q ...`
3. **关键豁免**：assignee 不是真实 Hermes profile（如成员 open_id `ou_xxx`）→ **跳过，永不自动 spawn**。代码注释明确：这类任务"are pulled by terminals via claim_task directly and should NEVER auto-spawn"——这就是人协作 lane
4. running 无 run_id 的任务只补 task_runs 记录（心跳管理），不 spawn

**推论**：人协作任务用成员 open_id 作 assignee 即天然隔离自动执行。唯一风险场景：assignee 恰好等于真实 profile 名（如 "default"）——评论工具里 `resolve_assignee` 只接受 `ou_` 开头或成员名单名字（映射回 open_id），不会落到 profile 名。

## 评论 kanban 工具的角色控制

- 身份从 thread-local 取：`collab.get_commenter()`（feishu_comment.py 的 `_run_comment_agent` 在 agent 运行前 `set_commenter`）
- create 仅 admin（`collab.is_admin`），member 被拒：`只有项目管理员（妖玉）可以派任务。`
- claim/complete 允许 member（认领人=自己，claim_task 的 claimer 参数）
- assignee 中文名自动解析：`collab.resolve_assignee('杨璇')` → open_id（先匹配成员名单名字，`ou_` 开头直通）

## 测试方法

用 venv python 直接调 handler（不经过事件流）：
```python
import importlib; importlib.import_module('tools.feishu_comment_kanban_tools')
from tools.feishu_comment_kanban_tools import _handle_kanban_create, _handle_kanban_claim
from plugins.platforms.feishu import feishu_comment_collab as collab
collab.set_commenter('ou_xxx'); collab.set_project('伏妖记')
_handle_kanban_create({'board': '伏妖记', 'title': 't', 'assignee': '杨璇'})
```
注意 `tool_result(字符串)` 返回的是 JSON 字符串字面量（`"..."`），直接当文本看，不要 json.loads 后 .get。

清理测试任务：`conn.execute("DELETE FROM tasks WHERE id=?", ...)`（triage 任务 complete 不了，只能删）。
