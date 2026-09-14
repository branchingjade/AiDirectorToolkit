---
name: feishu-message-verification
description: "Use when 核实飞书消息事实——某人真的发了N次吗、bot是否重复回复、补推重放排查、消息被 adapter silent drop 但 API 有（孤儿消息检测）、DM 活但群死（SDK dispatcher 故障）。"
version: 1.4.0
tags: [feishu, gateway, message, forensics, replay, dedup, silent-drop, orphan, sdk-dispatcher, channel-health, group-require-mention]
updated: 2026-09-03
---

# 飞书消息事实核实与补推重放排查

当用户质疑「某人是不是真的重复发了消息」「bot 是不是重复回复了」「这条回复到底是谁发的/我补的还是对方重发的」时，用本流程。**核心原则：gateway 日志和 bot 自己的描述都不是事实，飞书 API 历史才是事实**——一切结论以 `lark-cli im +chat-messages-list` 返回的 message_id 为准。

2026-08-07 实战验证：叶子「重复发三次」案例——最终查明叶子实际发了 4 次（3 次在停机窗口内），bot 的「这是第三次发了」回复是被**补推重放**触发的假象。

## 一、消息事实的三层证据链（从弱到强）

| 层级 | 来源 | 可信度 | 说明 |
|---|---|---|---|
| 1 | bot 回复内容自称（「这段是第三次发了」「给过三次成品了」） | ❌ 不可信 | bot 只会按自己收到的入站事件数数，不知道补推重放，也不知道用户实际发了几次 |
| 2 | gateway.log 的 `inbound message` / `Sending response` | ⚠️ 半可信 | 能证明 gateway 处理了多少次，但**补推重放会被误记为「新消息」**——收到次数 ≠ 用户真实发送次数 |
| 3 | `lark-cli im +chat-messages-list` 返回的真实消息历史（含 message_id） | ✅ 事实 | 飞书服务端记录，用户真实发送/撤回的全部消息都在这里 |

**判定「某人真的发了 N 次」只能信第 3 层**——数 API 历史里该用户（`sender.sender_type == 'user'`）的同类内容消息条数。

## 二、补推重放陷阱（核心坑）

**现象**：gateway 停机（WebSocket 断连）期间用户发的消息，会在恢复后**数小时**以「补推」形式重新进入 gateway——实测停机 10:56-14:18，11:43/11:51/14:00 的旧消息在 15:05/18:48/18:56/18:57 才到达，且 **message_id 仍是旧消息的 id**。

**危害**：gateway 没有按 message_id 去重，补推消息被当新消息处理 → 对同一素材重复回复（实测对同一段提示词回了 3 次，每次还自称「这是第三次发了」）。

**识别方法**：gateway 日志入站消息的 message_id，如果在 API 历史里对应的是**更早时间**的消息 → 这是重放，不是新消息。

```bash
# gateway 日志里的入站 message_id（含完整 id）
grep "Inbound dm message received" ~/AppData/Local/hermes/logs/gateway.log | grep "2026-08-07 1[5-9]:"
# → id=om_x100b6863086954a8c278d9842e40348  ← 尾部 42e40348 与 API 历史 14:00 那条消息 id 吻合

# API 历史里的真实消息（含 message_id、sender_type、deleted 标志）
lark-cli im +chat-messages-list --chat-id <oc_xxx> --as bot --order desc --page-all
```

**对比方法**：把 gateway 日志入站 id 的尾部（如 `42e40348`）与 API 历史各消息 id 尾部匹配——命中旧消息 = 重放。也可看 bot 回复消息的 `reply_to` 字段指向哪条 user 消息：若指向几小时前的旧消息，说明这次回复是被补推触发的。

**对宕机恢复流程的影响**：⚠️ 恢复后**不要急着把停机窗口消息手动补发**——消息可能已被补推重放处理过，再补就重复了。先查重放，再决定补不补。这与 feishu-outage-recovery skill 里「停机消息不会自动补推」的说法矛盾（2026-08-07 实测证明会补推，只是延迟数小时）——若该 skill 已 adopt 修正，以新版本为准。

## 三、核实步骤（完整流程）

1. **收集 bot 侧处理记录**：
   ```bash
   grep "oc_c9469b68b96284d358a1be43185d692b" ~/AppData/Local/hermes/logs/gateway.log | grep "2026-08-07"
   ```
   记录每次 `inbound message`（入站）和 `Sending response`（出站）的时间与 id。

2. **拉取 API 真实历史**（bot 身份，勿用 user 身份——实测 `--as user` 对该会话返回 0 条）：
   ```bash
   lark-cli im +chat-messages-list --chat-id <oc_xxx> --as bot --order asc --page-all --page-limit 30
   ```
   - **输出可能带 warning 行**（如 `warning: reactions_partial_failed: ...`）在 JSON 前面——解析时先 `raw.find('{')` 再 `json.loads`。
   - 消息结构：`content` 在顶层（不是 body.content）；`msg_type`（text/post）；`sender.sender_type`（`app`=bot / `user`=人）；`create_time`；`deleted`（True=已撤回）；`reply_to`（回复指向的消息 id）。
   - content 可能是 JSON 字符串（post 类型）——`json.loads(content).get('text')` 才拿得到正文。

3. **数真实发送次数**：过滤 `sender_type=='user'`，按内容归类统计。注意相同素材可能带/不带「生成提示词：」前缀（长度差 6），要按去前缀后的正文比对。

4. **判定重复回复**：数 bot（`sender_type=='app'`）的同类回复条数 + 查每条 `reply_to` 指向的 user 消息时间。reply_to 全部指向旧消息 = 全是补推重放触发，用户并没有再发。

5. **汇报时给出完整时间线表格**：用户消息（真实次数）→ bot 回复（每条对应哪条 user 消息）→ 指出哪些是重放触发。用户会追问证据，把 message_id 尾部列出来。

## 四、lark-cli 实测坑速查

| 坑 | 现象 | 处理 |
|---|---|---|
| `--as user` 返回 0 条 | 同一会话 user 身份拉不到消息（权限/可见性） | 改用 `--as bot` |
| warning 行混入输出 | `reactions_partial_failed` 等 warning 在 JSON 前 | `raw[raw.find('{'):]` 再 json.loads |
| content 解析为空 | post 类型消息 content 是 JSON 字符串 | `json.loads(content).get('text')` |
| 消息数对不上 | 分页/时间窗参数问题 | 用 `--order asc --page-all --page-limit 30` 拉全量，再过滤日期 |
| 想数 bot 发了多少 | 只看 `Sending response` 不够 | 用 API 历史里 `sender_type=='app'` 条数 |
| `docs +fetch` 不接受 `--url` | 只接 `--doc <url_or_token>` | 改用 `--doc` |
| `drive +list-comments` 返回 `items=[]` / 字段不在顶层 | list-comments 返回结构扁平、字段名差异大 | 验证用 `+batch-query-comments --comment-ids <id>` 拿嵌套 reply_list |
| `--content @<file>` 必须 cwd 相对路径 | `/tmp/...` 报 `must be a relative path`（MSYS/git-bash 上 /tmp 是 bash 虚拟路径） | 把 JSON 文件 cp 到 hermes 根或 `~/AppData/Local/hermes/` 再 `@./file` |
| `+add-comment` 的 `text` 字段必须是字符串 | 嵌套 `{"text":{"content":"..."}}` 报 `cannot unmarshal object ... field text of type string` | `{"type":"text","text":"纯字符串"}` |
| `+add-comment` 不接受独立 `mention` 元素 | `type=mention` 报 `unsupported type`；`mention_user` 独立元素报 `requires text or mention_user`（误导） | 用 reply 段 + `{"type":"mention_user","mention_user":"<open_id>"}`（`mention_user` 字段是字符串）|
| 主评论 + reply 的 @ 触发通知差异 | reply 里 `mention_user` 独立元素才会真触发 @ 通知 | 主评论用纯 text；  ` 要 @ 另加一条 reply 用独立 `mention_user` |

## 五、报告格式（用户认可）

结论先行（「叶子真的发了 4 次，不是 3 次」），然后：时间线表格（每条含时间/内容首 40 字/message_id 尾部）、bot 回复与 user 消息的对应关系（reply_to 链）、补推重放识别依据、根因总结（如「3 次撞停机窗口没回复，她反复重发；bot 后两次回复是补推误触发」）。最后给修复建议（gateway 应对入站 message_id 去重/打重放标记）。

## 六、Silent Drop Visibility（adapter 决策层丢消息）

**与补推重放的区别**：重放是消息「到了 gateway gateway 两次」；silent drop 是「飞书 WebSocket 推到 adapter，adapter 收到原始事件但拒绝派发 inbound」——用户消息在飞书 API 历史里存在，bot 没看见。

**典型根因**（2026-08-27 实战）：
1. **mention-only wake**：群消息只有 `@bot` 没有 payload，`_strip_edge_self_mentions` 剥成空字符串 → `_process_inbound_message` 第 4 步判定无内容 → 丢弃
2. **`_admit` 拒绝**：`group_policy_rejected` / `bot_not_mentioned` / `dm_policy_rejected` / `self_echo` / `bots_disabled` / `self_ids_unknown` 之一
3. **`_is_duplicate`**：message_id 已在 dedup 缓存里（TTL 内，常见 30 分钟）
4. **malformed event**：`message`/`sender` 缺失

**新增根因（2026-09-03 实战）——SDK dispatcher 不推**：
5. **lark_oapi SDK 根本没把群消息 frame 推到 handler**：`gateway.log` 里完全没有 `Received raw message` 也没有 `Inbound ... message received`——比根因 1-4 更深一层，**根因不在 hermes adapter，在上游 `lark_oapi.ws.client.Client._handle_data_frame` → `event_handler._do_without_validation(pl)` 的 protobuf → Event 反序列化路径**。Hermes adapter 改不出来。

**新增根因（2026-09-03 实战）——群聊 `require_mention` 误伤**：

6. **config 侧 `require_mention` 把群聊全部静默**：用户在群里发消息没 @bot → adapter `_admit` 命中 `require_mention and not self._mentions_self(message)` → `group_policy_rejected`。日志指纹：`[Feishu-DIAG] ADMIT REJECTED: reason=group_policy_rejected chat_type='group' mentions=[]` ——**`mentions=[]` 是关键特征**。DM 完全不受影响（DM 走 `if not is_group` 分支，只看 `_allow_all_dm`/`_allowed_group_users`）。代码位置 `hermes-agent/plugins/platforms/feishu/adapter.py:4521`。
   - **与根因 5 区分**：根因 5 = DM 活群死 + 完全没 `Received raw message` 日志（SDK 层）；根因 6 = 有 `Inbound candidate` + `ADMIT REJECTED reason=group_policy_rejected mentions=[]`（adapter 决策层），gateway 收到事件但被策略拒。
   - **排查步骤**：①`grep "group_policy_rejected" logs/gateway.log | tail` 看是不是只群消息被拒、DM 正常；②`grep -B1 -A5 "group_rules\|require_mention" config.yaml` 看 `platforms.feishu.group_rules[oc_xxx]` 该群是否有独立 rule；③若无独立 rule，看全局 `platforms.feishu.require_mention` 是否为 `true`——是则默认要求 @bot。
   - **修复**：给目标群加 `platforms.feishu.group_rules[oc_xxx].require_mention: false`（per-group 关闭）或全局改 `platforms.feishu.require_mention: false`。
   - **用户认知错位陷阱**：MEMORY 里写「用户在群 @Hermes 或 DM 都可」是设计预期，但实际团队习惯不在群 @bot。`group_policy: open` 配 `require_mention: true` 等于关掉了所有群协作——**必须二选一**（要 open 群协作就关 require_mention；要 require_mention 就接受群内几乎不会被触发）。修 config 时同步改 MEMORY 协作预期，避免后续误判。

**诊断指纹**：DM 通道工作正常（11:09/11:14 入站图片/文字 DM 正常 dispatch），但群消息全部静默——这种「DM 活 / 群死」**高度指向 SDK dispatcher bug**，不是 hermes 配置或策略问题。

**致命设计坑**：以上五类 silent drop 中，根因 1-4 全部走 `logger.debug`（INFO 级看不见），gateway.log 在默认级别下完全空白——只看到 `Received raw message type=text message_id=...` 一行就停。**根因 5 更狠——这一行也没有**（消息根本没到 adapter 的 `_extract_message_content`），grep message_id 完全 0 结果。

**排查步骤**（用户问"消息为什么没回"）：

1. 拿到用户可疑消息的 message_id（飞书 API 历史查）
2. `grep "<message_id>" ~/AppData/Local/hermes/logs/gateway.log`
   - **完全没日志** → 飞书 WebSocket 根本没推到 adapter（根因 5，SDK dispatcher bug）→ 升级 lark-oapi 或 fallback 到 webhook 模式
   - **只看到 `Received raw message`** → adapter 收到事件但没派发 inbound → silent drop，**根因在 adapter 决策层**（根因 1-4）
   - **看到 `Inbound ... message received`** → 已派发，问题是 agent 没回（不是 silent drop）
3. **临时打开 DEBUG 看真实原因**（仅当 grep 有 `Received raw` 但没 `Inbound`）：
   - 编辑 adapter.py 给 `_handle_message_event_data` 入口加 `logger.warning("[Feishu-DIAG] Inbound candidate: msg_id=%s chat_id=%s chat_type=%r", ...)` 和 `_admit` 拒绝时加 `logger.warning("[Feishu-DIAG] ADMIT REJECTED: reason=%s ... mentions=%s text=%r", ...)`——带 chat_id + chat_type + mentions 列表 + text 前 120 字
   - 重发那条消息复现，看 `ADMIT REJECTED reason=...` 的具体 reason
   - 标记惯例：`# [Feishu-DIAG]` 前缀（区别于旧版 `# [HERMES_FIX 2026-08-27 silent-drop-visibility]` 标记）
4. **永久修复**（推荐）：把 adapter 三处 `logger.debug` 提到 `logger.info`——
   - `Ignoring empty text message id=...` → `Ignoring empty text message id=... (mention-only wake, no payload)`
   - `Dropping duplicate/missing message_id: ...`
   - `dropping inbound event: <reason>` → 加 `(message_id=... chat_type=...)` 上下文

   标记惯例：`# [Feishu-DIAG]`（2026-09-03 起新约定）。**适配器代码位于 `hermes-agent/plugins/platforms/feishu/adapter.py`**——不是 skill 维护目录，而是 Hermes 主仓库源码；改完不必重启 gateway 但要保证下次 gateway 启动加载到（gateway.py 内部 import adapter）。验证：清空 `logs/gateway.log`，触发一条 silent drop，看到 INFO/WARNING 行 = 生效。

**根因 5（SDK dispatcher）的修法候选**：
- **A. 升级 lark-oapi**（最高 ROI）：`pip install -U lark-oapi`，查 PyPI changelog 是否有群消息 mentions/protobuf 解析修复。**前提**：必须用与 hermes-agent 同 python 环境的 pip（hermes venv 通常不在 system pip 里）
- **B. 强制 webhook 模式回退**：环境变量 `FEISHU_CONNECTION_MODE=webhook`，飞书后台事件与回调也切到「将事件发送至开发者服务器」+ 配置 `FEISHU_VERIFICATION_TOKEN` 或 `FEISHU_ENCRYPT_KEY`（二者至少一）。验证 webhook 模式不受 SDK dispatcher bug 影响
- **C. 在 hermes adapter 加 fallback mention detection**：如果 `message.mentions` 是空，从 `message.content` 里 grep `@bot_name` 字符串补 mentions。治标不治本，workaround 视角

**主动防御**：注册 cron `feishu-orphan-messages`（`scripts/feishu-orphan-messages.py` 已配套，每 30 分钟跑窗口 35 分钟），发现孤儿立刻推群报警——不要等用户问"消息为什么没回"才查。**对根因 5 还要加一条**：孤儿检测 cron 跑出「群消息孤儿但 DM 正常」模式时，自动标记 `likely_cause=SDK_DISPATCHER` 提示升级 lark-oapi。

## 七、孤儿消息检测（API 有 / gateway log 没有 inbound）

**与补推重放/silent drop 都不同**：定义明确——「API 历史中存在 message_id 末 12 位的 user 消息，最近 N 分钟 gateway.log 里没有对应的 `Inbound ... message received`」。脚本流程：

1. 调 `lark-cli im +chat-messages-list --chat-id <oc_xxx> --as bot --order desc --page-limit 30` 拉最近入站
2. 过滤 `sender_type=='user'` + `deleted==false` + 不是 `/` 开头 command（command 走 inbound 拒了不是孤儿——这是脚本易踩的误判点）
3. 扫 `~/AppData/Local/hermes/logs/gateway.log` 收集窗口内所有 `Inbound ... message received` 的 message_id（正则 `[Feishu] Inbound (?:dm|group) message received: id=(om_[0-9a-z]+)`）
4. 差集 = 孤儿

**regex 字符类铁律（2026-09-04 实战教训）**：飞书 message_id 形如 `om_x100b66a0062af4a4b113e01ccb3acbf`——`om_` 后第 1 个字符是 `x`（base32 包含 `x`），但用 `[0-9a-f]` 字符类会**完全错过**所有以 `om_x` 开头的消息（实测量大）。原脚本踩此坑 → **把所有 inbound 算成 0** → 把 API 看到的所有消息全判孤儿 → 误报率高（同时因为相同 bug 把 inbound 也判 0，反而"无孤儿"假象）。**修复**：统一用 `[0-9a-z]+` 或 `om_\w+`。本机 gateway 默认所有消息 ID 都是 `om_x` 形式——这是关键事实。

**实测踩坑**（2026-08-27 + 2026-09-04）：
- `/new` / `/status` / `/kanban` 等 command 也会进 API 历史但走 inbound 后被拒——脚本必须过滤 `text.startswith("/")`，否则 false positive
- `lark-cli docs +fetch` 拉到的消息如果 msg_type != text（post / share / interactive），content 是 JSON 字符串——`json.loads(content).get('text')` 再判断

**部署范式**（用户已采用）：
- 脚本：`hermes-agent/scripts/feishu-orphan-messages.py`（已落档）
- cron：`hermes cronjob create ... --schedule "every 30m"`，prompt 里写明"无孤儿静默退出；有孤儿调 `lark-cli im +messages-send` 推『天有答辫』群"
- 关键细节：窗口长度 > 调度间隔（35 分钟 vs 30 分钟），重叠 5 分钟防漏；`deliver=origin` 让 cron 输出回流本会话；如不想每轮回流可改为 `deliver=local`（孤儿报警走 prompt 内 `im +messages-send` 主动发群）

**版本校验铁律**（2026-08-27 实战教训）：用户给的飞书 doc URL 是 `Q1tBdNPMRoNQqcxzE0NcvdpHnGI` 还是 `K5d3d03KhoAhoOxv3TMc873tncf`？两个完全不同文档，**本地镜像（`_work/fuyaoji/script.md`）未必是用户当前指的那个**。必查：
1. `lark-cli docs +fetch --doc <url> --scope outline --max-depth 2` → 拿 document_id + revision_id
2. 比对本地台账的 revision
4. 比对 `script.md` 头部 `<title>` 是否一致
三处任一不一致 → 锐评前先 fetch 在线版本，不凭本地镜像下结论。

## 相关 skill

- [feishu-outage-recovery](../feishu-outage-recovery/SKILL.md) — 宕机恢复主流程（user-owned；其中「停机消息不补推」表述已被本 skill 实测推翻，待 adopt 后修正）
- [lark-im](../../lark-im/SKILL.md) — `+chat-messages-list` 完整参数参考
- [feishu-gateway-setup](../feishu-gateway-setup/SKILL.md) — `references/topic-thread-debugging.md` 含 silent-drop 决策树（被六节引用）
- [feishu-comment-collab](../feishu-comment-collab/SKILL.md) — 评论 API 鉴权/字段名实测细节（参考七节 lark-cli 坑）
- 配套脚本：`scripts/feishu-orphan-messages.py`（孤儿检测探测，cron 触发）

## 八、三渠道健康度诊断（2026-09-03 实战方法学）

**新增根因 6**（2026-09-03 实战，群聊 `require_mention` 误伤）已加在六节末尾。完整方法学见 `references/channel-health-triage.md`，含：

- 三渠道数据落点对照表（state.db / log / 实际持久化层差异）
- 六个根因的诊断指纹速查（DM/group/comment × 健康/挂）
- **评论会话"挂"的真相**：日志里"Session saved" = 内存 `_session_cache` dict 写入（feishu_comment.py:1000-1044），TTL 1h，**gateway 重启即清零**——`state.db sessions` 表里**永远不会有 comment session**（独立 AIAgent 数据管线隔离）。SKILL 里"磁盘持久化"描述与实际实现矛盾，待 `feishu-comment-collab` / `hermes-feishu-internals`（user-owned）adopt 后同步修订。
- 三渠道三角验证最小命令集（state.db + log + config.yaml，秒级跑完）
- `feishu-collab-health.py` 指标定义偏差清单（不能直接信脚本输出）

**何时读 references/channel-health-triage.md**：
- 用户问"飞书协作建康度/某个渠道挂没挂/为什么 0 活跃"
- 跨渠道诊断时（DM + group + comment 同时排查）
- 接手 `feishu-collab-health.py` cron 改造（指标口径需重设）
- 排查"评论会话上下文丢失"（几乎一定是这个根因，不是别的）

**何时读 references/channel-health-remediation.md**（2026-09-03 实战补充）：
- triage 文档已确诊根因后，准备改代码落地修复
- 需要代码骨架（feishu_comment.py 持久化双写、feishu-collab-health.py 改口径、config.yaml group_rules 改法）
- 需要单测骨架 + 生产实测步骤 + 三件套验证铁律
