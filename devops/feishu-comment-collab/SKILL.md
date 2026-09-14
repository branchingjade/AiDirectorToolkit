---
name: feishu-comment-collab
description: "Use when 飞书文档评论不回复/评论@/评论权限/评论会话/评论协作功能排障与扩展（含 lark-cli drive +add-comment 字段格式实测坑）。"
version: 1.5.0
tags: [feishu, comment, collab, kanban, obsidian, gateway]
updated: 2026-09-01
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
  → tools/feishu_doc_tool.py                 # 读 + 编辑：read/fetch_blocks/str_replace/block_replace
  → tools/feishu_comment_kanban_tools.py     # kanban 4 工具
  → tools/feishu_comment_obsidian_tools.py   # Obsidian 2 工具
```

关键点：
- **事件入口已在 adapter.py 订阅**，不需要开发者后台额外配事件（WebSocket 模式自动收）
- 过滤条件：self-reply 跳过、`to_open_id` 必须是 bot（评论里 @ bot 才有）、notice_type ∈ {add_comment, add_reply}
- agent 配置：`skip_context_files=True`；`skip_memory` 按角色——admin 加载全局记忆、member 隔离；toolsets = feishu_doc + feishu_drive + feishu_comment
- **2026-08-13 起评论 agent 可改文档正文**（此前只能读+评论）——见「文档编辑」章节

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

## 创作型评论分流（2026-08-31 新增，根因修复）

评论里出现「润色/重写/改/优化/调整/做出合理改动/换个写法/再来一版」等创作意图时，**不能走默认 reply agent**——reply agent 结构上是"引用段是锚、上下文是 timeline"，而创作型需要"全文是锚、上下文是 feishu_doc_read"。两个任务不该混在同一条 prompt 路径上。

机制（详见 `feishu_comment.py` 的 `_detect_creative_intent` + `_run_creative_agent`）：

- **意图检测**：19 条关键词正则（含「节奏更紧/更利落/更狠/更冷/更准」「改这场戏」「调整对白」等变体），命中即路由到 `_run_creative_agent`
- **独立 agent**：复用 AIAgent 但 `prefill_messages` 注入 `feishu-comment-creative` skill 全文 + `_CREATIVE_AGENT_SYSTEM` 硬要求（先调 `feishu_doc_read` 才能输出、不许说"读不到"等 user 投喂上下文）
- **max_iterations=25**（高于 reply 的 15，给文档读+三关审查留余量）
- **`enabled_toolsets=["feishu_doc", "feishu_drive"]`** 与 reply 一致——工具能力相同，差别只在 prompt 与 prefill
- **skill 自动同步**：prefill 每次启动从 `~/AppData/Local/hermes/skills/feishu/feishu-comment-creative/SKILL.md` 读，**改 skill 即生效，不需要重启**（除非改意图检测正则）

**为什么不"加一行 Creative work 章节"贴 `_COMMON_INSTRUCTIONS`？** 因为 LLM 会把建议当空气。结构上：reply agent 默认 `skip_context_files` + `skip_memory`，注定拿不到创作所需的全场景上下文，必须独立 agent + 强 prefill 才能锁住工作流。

验证（2026-08-31 实测）：用真实 lark client 调 `_run_creative_agent`，agent 真调 `feishu_doc_read`、跑完三关审查、输出 3 个完整方案 + plain text 对比表——之前 reply agent 偷懒输出"读不到文档内容"的 bug 从根因消除。

**意图检测的跨分支变量坑（2026-08-31 实测，2026-09-01 补充）**：`_detect_creative_intent(current_text, target_text, root_text)` 写在主流程最后（Step 4 之前），但三个变量**只在三个 if/else 分支里各自定义**：
- whole-comment 分支（1412-1478 行）定义 `current_text`（1431）
- local-comment 分支（1494-1505 行）定义 `target_text`（1505）+ `root_text`（1505）

任何一个分支变量没初始化都会触发 `UnboundLocalError`，主流程全挂。修复用 `locals().get(name, "") or ""` 兜底，**所有三个变量**都必须用 `locals().get()` 而不是直接引用——不要只图省事留下一个。

**`if cond and 'var' not in locals(): var = ''` 反模式（2026-09-01 实测否定）**：看起来更"精确"（只在变量没定义时给空字符串），但**不安全**。Python 编译期决定变量作用域——只要函数里任何一处有 `var = ...` 赋值（包括 `var = ""` 那一行），编译器就把整个函数的 `var` 视为 local，运行到 `else` 分支访问 var 时仍抛 `UnboundLocalError`。**安全兜底两种**：
- ✅ 函数顶层 `var = ""` 默认值（必须所有路径共享默认值）
- ✅ `locals().get(name, "") or ""`（绕过编译期 local 判定）
- ❌ `if 'var' not in locals(): var = ''`（编译期已把 var 视为 local，不安全）

**类级教训**：在 `if A / else B` 分支后**新增引用任一分支变量的代码**，必须用 `locals().get()` 兜底，而不是直接引用。直接引用看起来"应该没事"（分支里都有初始化），但只在一个分支里有就够炸了。**端到端测试是唯一能发现这种 bug 的手段**——单跑那个分支测不出来。

扩展点：未来加新创作型 skill（如「飞书评论翻译」「飞书评论做诗」），仿照 `_run_creative_agent` 写 `_run_<task>_agent(prompt, ...)`，在主流程 1555 行那个 `is_creative` 后面加 `_detect_<task>_intent` 路由即可。

**feishu_doc/drive tool 跨线程 client 查找失败（2026-09-01 实测根因修复）**：`tools/feishu_doc_tool.py` 和 `tools/feishu_drive_tool.py` 用 `threading.local()` 存 lark client，handler 报错 `Feishu client not available (not in a Feishu comment context)`——**不是** tool 没注册 / prefill 没注入 / ACL 被拒，而是**跨线程**。

链路：
```
主线程 (gateway.handle_drive_comment_event)
  ↓ asyncio loop
worker thread A (loop.run_in_executor 调度 _run_creative_agent)
  ↓ set_doc_client(client) 存到 A._local.client
  ↓ agent.run_conversation
  ↓ LLM 决定调 feishu_doc_read
worker thread C (DaemonThreadPoolExecutor pool —— agent.tool_executor)
  ↓ handler _handle_feishu_doc_read
  ↓ client = get_client() 查 C._local.client → 没有 → 报错
```

`agent.tool_executor` 已用 `propagate_context_to_thread()` 传播 ContextVar，但 `set_client` 不在 turn context 里所以传不到。**临时方案（已采用）**：把这两个 tool 的 `_local = threading.local()` 改成进程全局 `dict[thread_ident] = client` + fallback（同一事件通常只有一个 in-flight client，fallback 歧义有界）。**根治方案**：把这些工具的 client 存改成 ContextVar 并在 agent 主循环的 turn context 里 `set_client`。

**诊断口诀（必记）**：bot 挂 OK reaction 但不回复 + gateway.log 看到 `[Feishu-Comment] ========== handle_drive_comment_event START` 之后突然断 + 上一行是 `Tool feishu_doc_read returned error: Feishu client not available (not in a Feishu comment context)` + 创作意图命中 `Intent detected as CREATIVE` —— **一定是这个跨线程陷阱**。修复前所有「工具不可用」「读不到文档」的退化回都是这个，不是 LLM 偷懒、不是 skill 没加载、不是 ACL 严。三层叠加坑：①LLM 偷懒不读（已修：prefill 强要求）→ ②whole-comment 变量未绑定 UnboundLocalError（已修：locals.get）→ ③跨线程 client 查不到（已修：dict[thread_ident] + fallback）。

## 文档编辑（2026-08-13 新增，两轮确认流）

评论 agent 的工具箱从「读+评论」升级为「读+评论+改正文」。**用户拍板方案 C：强制两轮确认，改前列清单等回复确认才动手**。

工具（tools/feishu_doc_tool.py，注册在 feishu_doc toolset，共 4 个）：
- `feishu_doc_read` — 纯文本读
- `feishu_doc_fetch_blocks` — 带 block_id 的 XML 读（定位/验证用）
- `feishu_doc_str_replace` — 全文精确替换（pattern 必须逐字复制自原文）
- `feishu_doc_block_replace` — 按 block_id 替换单块

**确认流（已写进 `_COMMON_INSTRUCTIONS`，不可跳过）**：
1. 用户要求改正文 → 先 fetch 定位/数次数 → 回复**编号改动清单**（位置/原文→新文/总数）→ **不动手**
2. 等用户显式确认（"确认/可以/改吧/就这么改/OK/好"）→ 才执行编辑 → 再 fetch 验证 → 回复结果
- 会话历史（session_key 跨卡片记忆）承载清单，第二轮靠 history 识别确认——两轮是跨评论完成的
- 编辑安全规则：pattern 逐字复制（差一字=静默 no-op）；空 content 删除需显式 `allow_empty=true`（工具层护栏，防误删全部匹配）；block_replace 后旧 ID 失效需重新 fetch；每次改动后必须 fetch 验证才报成功

**排障新姿势**：评论 agent 回复「我没有改正文的工具/接口」≠ 权限问题——先查工具集（`toolsets.py` 的 feishu_doc toolset 有没有写工具）再查权限。2026-08-13 实测：agent 说"只有读和评论两类接口"是工具集没挂写工具，权限层（tenant_editable）完全够。权限诊断三步法见 feishu-doc-maintenance §四·五。

## 工具集（feishu_comment toolset + feishu_doc toolset，8 个）

- kanban：create（**仅 admin**，中文负责人名自动解析）/ list / claim / complete
- Obsidian：search / read（**权限分级**，见 references/obsidian-note-tools.md）
- 文档：read / fetch_blocks / str_replace / block_replace（见上方「文档编辑」章节）

工具身份通过 thread-local 传递：`collab.set_commenter(open_id)` + `set_project(project)`（feishu_comment.py 在 agent 运行前设置，handler 读取做角色校验）。

## Pitfalls

- **Windows 文件名坑**：会话文件名不能含 `:`，中文若替换成 `_` 会碰撞（伏妖记/犬子无双 同用户互相覆盖）——必须 percent-encode
- **kanban 中文 board 名直接报错**：slug 只允许小写英文数字连字符下划线，中文项目用拼音 slug（伏妖记→fuyuji）+ `--name 中文`。评论 kanban 工具已做名字→slug 自动映射
- **triage 任务认领断链**：`create_task(triage=True)` 落 triage 状态，`claim_task` 只接受 ready → 协作任务必须默认创建（落 ready）
- **dispatcher 不会动人工任务**：kanban dispatcher 每 60s spawn ready 任务（`hermes -p <assignee>`），但 assignee 非真实 Hermes profile（如成员 open_id）的任务**永不自动 spawn**——人协作任务天然隔离，详见 references/kanban-collab.md
- **`hermes update` 会覆盖所有源码改动**（feishu_comment*.py / toolsets.py / tools/*）——升级后需重打补丁。⚠️ 2026-08-13 实测：官方源码演进后**整体 `git apply` 会失败**（上下文对不上），正确姿势是 `git apply --3way hermes-local-patches.diff`（冲突文件留 `<<<<<<<` 标记，多为官方新版编码处理已比补丁强，保留 ours 手动解），再手动复制被删的新文件（正本在 Obsidian Vault/_hermes/补丁管理/，`cp` 到 plugins/platforms/feishu/ 和 tools/），最后 py_compile 语法验证 + 重启 gateway。症状识别：规则文件 policy=members 但日志 `denied (policy=pairing)`——`_VALID_POLICIES` 里没 members 被静默回退，**成员全部被拒**
- **规则文件热加载 ≠ 代码热加载**：改 `feishu_comment_rules.py` 代码（如新增策略）必须重启 gateway；规则文件本身（JSON）不用
- **gateway 长跑后 feishu ws 会静默死亡（2026-08-31 实测）**：`gateway.run` 启动时 feishu websocket 正常连（带 `Connected in websocket mode`），但跑几小时后**进程还活着、端口 8644 还在 listen、adapter 不知道 ws 已断**——`netstat` 会显示 `CLOSE_WAIT` 状态的 outbound TCP 到 443 端口，但代码不打印任何断连日志，`reconnection watcher` 不触发。最明显的征兆是「评论 @ bot 没回复 + 进程看似正常」。诊断：看 `netstat -ano | grep <gateway_pid>` 找 `CLOSE_WAIT` 状态的 443 连接；或看 `[Feishu-Comment] ========== handle_drive_comment_event START` 日志时间间隔——超过几小时没新事件就该怀疑。临时修：杀进程后 `schtasks /Run / /TN "Hermes_Gateway"` 拉起（plan task 会干净重连，连上后会显示 `Channel directory built: 57 target(s)`）。根治：等 feishu SDK heartbeat/Ping 机制改对，或在 `shutdown_watchdog` 里加 `ws health check`（目前没做）。
- **模拟事件 / 配对测试的真实副作用（2026-09-01 叶子离职实战教训 + 2026-09-01 时间窗口补充）**：`handle_drive_comment_event(data, self_open_id)` 不只是 dry-run——它会跑完整链路：**真调飞书 API 加 reaction、写会话历史、`add_whole_comment` 真发到飞书文档**。手工构造 `SimpleNamespace` 事件对象当 from_open_id=<某人> 测试时，别人的 open_id 会被 gateway 当成真人评论发起者，bot 也会**真发评论到生产文档**。三个铁律：①**先核对人员在职状态**——`grep -i <姓名> ~/.hermes/memories/MEMORY.md` 看是否有离职/退出记录；`session_search` 看最近一次互动时间（3 个月以上没新事件 = 高概率离职）；不确定就**问用户**而不是猜（看 open_id 在文档评论历史里出现 ≠ 在职）。②**`pairing add <open_id>` 必须 `pairing remove` 配对回退**——用 `./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules pairing add/remove <open_id>`。③**测试产出的飞书评论必须删干净**——`lark-cli drive +list-comments` 找出 `reply_id`，`lark-cli drive +delete-reply --token <token> --type docx --comment-id <cid> --reply-id <rid> --as bot --yes` 删除（high-risk-write 要 `--yes`，删除不可逆）。配置备份：动 `feishu_comment_rules.json` / `feishu_comment_pairing.json` 前 `cp` 到 `~/AppData/Local/hermes/_archive/<日期>/`。

  **`+delete-reply` 时间窗口陷阱（2026-09-01 实测）**：bot 删自己刚发的 reply 时报 `code=1069301 fail` 或 `code=1069303 forbidden`——**实测可工作窗口是 reply 创建后约 30s+**（实测：2 小时前的 reply 一次成功；几秒内刚发的 reply 必失败）。冷启动后第一次尝试也容易 1069301，可能是 feishu SDK 的 reply-metadata 同步延迟。**操作模式**：先 `lark-cli drive +list-comments` 找到 reply_id，**等 30-60s 再删**，失败重试（最多 2 次）。如果反复 1069301，确认是 whole comment 还是 reply——reply 用 `+delete-reply`，whole comment 本身没有 `+delete-comment` 命令只能保留。如果 reply 是 bot **自己刚发的**且需要清理，不要尝试（飞书 API 限制），把它留在那——bot 用户看得见这条「工具不可用」是修复前的退化版，不影响后续 agent 输出（agent 输出在 reply 链之后）。
- **创作意图别走 reply agent**（2026-08-31 教训）：`_COMMON_INSTRUCTIONS` 里加"如内容不够请用 feishu_doc_read"是**建议不是要求**，LLM 会偷懒不读就输出"读不到文档内容"。创作型任务（润色/重写/改/优化/调整/做出合理改动/换个写法/再来一版）必须路由到独立 agent + 强 prefill 注入 skill——详见上方「创作型评论分流」章节
- **`lark-cli drive +add-comment` 字段格式坑**（2026-08-27 实测）：
  - `--content @./file.json` 文件必须在 cwd 相对路径——MSYS/git-bash 上 `/tmp` 是 bash 虚拟路径会报 `must be a relative path`；cp 到 hermes 根或 `~/AppData/Local/hermes/` 再 `@./file`
  - `text` 元素必须是**纯字符串**，嵌套 `{"text":{"content":"..."}}` 报 `cannot unmarshal object ... field text of type string`
  - 不接受独立 `mention` 元素；`type=mention` 报 `unsupported type`，独立 `mention_user` 元素报 `requires text or mention_user`（误导）——正确做法：用 reply 段 + `{"type":"mention_user","mention_user":"<open_id>"}`（`mention_user` 字段是字符串）
  - 主评论用纯 text 不会触发 @ 通知；要真触发 @ 必须 `+add-reply` 加一条独立 `mention_user` reply
  - 验证评论是否真挂上去：`+list-comments` 返回 items 扁平、`reply_list` 嵌套结构与 `+batch-query-comments` 不同；用 `+batch-query-comments --comment-ids <id1>,<id2>,...` 才能确认 reply_list.replies[].content.elements

## 相关

- [创作润色工作流定义](../feishu/feishu-comment-creative/SKILL.md) — 三关审查 + 多方案 + 对比表的工作流本体（prefill 注入到 `_run_creative_agent`）
- [kanban 协作机制细节](references/kanban-collab.md) — dispatcher 行为、slug 规则、状态机
- [Obsidian 笔记工具权限模式](references/obsidian-note-tools.md) — 范围表、路径穿越防护
