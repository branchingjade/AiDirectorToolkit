# 评论协作扩展设计（2026-08-06 实施）

把飞书文档评论 agent 从全隔离状态接入多用户协作体系。用户拍板：全部七层思路都做，会话维度选「项目+人」隔离。

## 改动文件清单

| 文件 | 动作 | 内容 |
|---|---|---|
| `plugins/platforms/feishu/feishu_comment_collab.py` | 新增 | 协作接入层（核心） |
| `plugins/platforms/feishu/feishu_comment.py` | 改 | 主流程接入 collab、会话/记忆/投递改造 |
| `plugins/platforms/feishu/feishu_comment_rules.py` | 改 | 加 `project` 字段 + `members` 策略 |
| `tools/feishu_comment_kanban_tools.py` | 新增 | 评论 kanban 工具（4 个） |
| `toolsets.py` | 改 | 注册 `feishu_comment` toolset |
| `~/AppData/Local/hermes/feishu_comment_rules.json` | 新建 | `{enabled: true, policy: "members"}` |

## 数据源（Obsidian Vault）

- `_hermes/会话路由.json`：`项目词典[]` + `路由{chat_key: {...}}` + 新增 `documents{file_token: {project, space}}`
- `_hermes/成员名单.json`：`admin: ["真名"]` + `成员{open_id: {name, role, note}}`
- `成员画像/<真名>.md`：frontmatter(open_id/角色/专长/参与项目) + 沟通偏好/擅长/协作备注
- 项目目录：`<项目>/<项目>.md`（主文档）+ `<项目>复盘.md`（复盘）

## 会话模型（用户选定 B）

```
有项目: comment:{项目}:{用户_open_id}
无项目: comment:doc:{类型}:{token}:{用户_open_id}
```

- 按人隔离：多用户评论不串台（原实现按文档共享，跨用户上下文互相可见）
- 磁盘持久化：`Obsidian Vault/_hermes/评论会话/<percent-encoded-key>.json`（2026-08-07 起迁入 vault；此前 `~/AppData/Local/hermes/comment_sessions/`），TTL 1h，上限 50 条
- 文件 key 必须 percent-encode（`:` 非法 + 中文防塌缩）

## 路由解析顺序

1. 规则文件 `documents["<type>:<token>"].project`（exact doc 级）
2. 路由表 `documents[file_token].project`
3. 项目词典最长词匹配文档标题 → 自动登记写回路由表
4. 都未命中 → 无项目上下文，降级按文档回答

## 权限分级

- admin（妖玉）：全局记忆开（`skip_memory=False`）、kanban create 可用、prompt 提示可管理动作
- member（团队成员）：记忆隔离（`skip_memory=True`）、kanban list/claim/complete、只读协作
- 陌生人：访问控制直接拒绝（members 策略下不在成员名单即拒）
- admin 回复公开发布在评论里 → prompt 注入防泄露指令

## 画像沉淀机制

- prompt 末尾要求 agent：观察到明确稳定偏好时输出 `OBSERVATION: <事实>` 行
- 代码剥离该行 → `record_observation`：去重（同文本跳过）、低频（一天≤2条）、追加到画像「协作备注」段

## 实施顺序建议（分批自检）

1. 第一批：collab 模块 + 主流程接入（真名/画像/路由/项目记忆/会话隔离/记忆开关）
2. 第二批：kanban 工具 + toolset 注册 + 角色校验
3. 第三批：沉淀/通知/富文本（通知与富文本评估后暂缓）

## 测试方法

```bash
cd ~/AppData/Local/hermes/hermes-agent
# 访问控制
./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules check docx:<token> <open_id>
# collab 函数（成员/路由/画像/会话）
./venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'.'); from plugins.platforms.feishu import feishu_comment_collab as c; ..."
# kanban 工具全流程（临时任务，测完 DELETE 清理）
./venv/Scripts/python.exe -c "import importlib; importlib.import_module('tools.feishu_comment_kanban_tools'); ..."
```

⚠️ 端到端只能靠真实飞书评论验证；模块层测试用 `collab.set_commenter(open_id)` 模拟 thread-local。

## 遗留项（诚实声明）

- 私聊通知：派任务后通知 assignee（需 im API 集成到工具层，未做）
- 富文本回复：评估后暂缓（飞书评论渲染能力有限）
- gateway 重启后才能生效（代码改动非热加载）
