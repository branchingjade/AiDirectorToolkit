# Silent-Drop & Orphan Detection — 实战档案（2026-08-27）

把 SKILL.md 第六、七节落地的具体补丁、命令和验证步骤集中在这里，避免下次会话每次都从头摸索。

## 1. Adapter patch（提升 silent drop 可见性）

文件：`hermes-agent/plugins/platforms/feishu/adapter.py`

三处 `logger.debug` → `logger.info` 改动，标记惯例 `# [HERMES_FIX 2026-08-27 silent-drop-visibility]`：

| 位置 | 旧日志 | 新日志 |
|---|---|---|
| `_handle_message_event_data` 第 ~2652 行（_is_duplicate 之前） | `Dropping duplicate/missing message_id: %s` | `Dropping duplicate/missing message_id: %s`（提到 INFO，message_id 缺失时打 `<missing>`） |
| `_handle_message_event_data` 第 ~2657 行（_admit 拒绝后） | `dropping inbound event: %s` | `dropping inbound event: %s (message_id=%s chat_type=%s)`（带上下文） |
| `_process_inbound_message` 第 ~3380 行（空文本 guard） | `Ignoring empty text message id=%s` | `Ignoring empty text message id=%s (mention-only wake, no payload)` |

**验证步骤**：

1. `netstat -ano | grep ":8644.*LISTENING"` 拿 gateway PID
2. `taskkill /PID <pid> /F`（如需重启让 patch 加载）
3. 清空 `~/AppData/Local/hermes/logs/gateway.log` 备份后截断
4. 触发一条 silent drop（群消息只 `@bot` 不带文字；或对 bot 发起一条会被 `group_policy_rejected` 的群消息）
5. `grep "[Feishu] dropping inbound event" gateway.log | tail -5` → 应看到新格式 INFO 行

实测确认 patch 已生效（2026-08-27 09:35 重启后的 gateway PID 14232）：
```
2026-08-27 10:00:04 ... [Feishu] dropping inbound event: group_policy_rejected (message_id=om_x100b67cdecfaa4acc34ae810ea8b91f chat_type=group)
2026-08-27 10:01:58 ... [Feishu] dropping inbound event: group_policy_rejected (message_id=om_x100b67cde7958c80c4c8d6211ff8f92 chat_type=group)
```

## 2. 孤儿检测脚本

路径（用户已落档）：`~/AppData/Local/hermes/scripts/feishu-orphan-messages.py`

调用范式：

```bash
python3 'C:/Users/HMSJ/AppData/Local/hermes/scripts/feishu-orphan-messages.py' \
    --window-minutes 35 \
    --chats oc_b7396f845a84a3aebdb1bf38c872e37a,oc_f7b91a21f9a134dec23959b9af54e6bb
```

- 窗口 35 分钟 > cron 调度 30 分钟：重叠 5 分钟防漏
- 默认监控 chat：`oc_b7396f...`（天有答辫群）+ `oc_f7b91a21f9...`（徐学环 DM）
- 输出 JSON：`{window_minutes, api_messages_seen, inbound_logged, orphans:[], errors:[]}`
- exit code：0=无孤儿，1=有孤儿

**已知 false-positive 陷阱**：

1. **command 类型消息**（`/new` `/status` `/kanban` 等）走 inbound 后被 bot 拒——脚本必须过滤 `text.startswith("/")`。2026-08-27 实测未过滤前报 2 条假孤儿（`om_x100b67cd018d70b0b1f910ab082f37c` 和 `om_x100b67ccbc2dacb8b4b03f851b3b1b0` 都是 `/new`）
2. **msg_type != text**（post / share / interactive）的 content 是 JSON 字符串——需 `json.loads(content).get('text')` 再判断 `/` 前缀

**配套已注册的 cron job**（2026-08-27 10:13 创建）：

```
job_id: 1b140a071247
schedule: every 30m
deliver: origin（prompt 内指定"无孤儿静默退出；有孤儿调 lark-cli im +messages-send 推天有答辫群"）
next_run_at: 2026-08-27T10:44:53
skills: [feishu-message-verification]
```

## 3. 版本校验铁律（防"看错文档"事故）

事故：2026-08-27 用户给了 URL `https://ucn8khyb55ax.feishu.cn/docx/Q1tBdNPMRoNQqcxzE0NcvdpHnGI`，我误以为是 `K5d3d03KhoAhoOxv3TMc873tncf`（飞书正本），跑了一套基于本地 `_work/fuyaoji/script.md`（v2.1）的锐评——但 `script.md` 实际是 v2.0 杨编精撰阶段的本地镜像，且 token 完全不同。

教训清单（每次处理飞书正本项目必走）：

```bash
# 1. 拿 outline + revision（不是 fetch 整篇——快）
lark-cli docs +fetch --doc "<飞书正本URL>" --as bot --scope outline --max-depth 2

# 2. 看三个东西：
#    a. document_id（应等于 URL 末段 token）
#    b. revision_id（应等于项目台账登记的最新 revision）
#    c. outline h1 列表（应与本地镜像头部的 h1 序列一致）

# 3. 比对
#    - 本地 _work/<proj>/script.md 头部 <title> 是否匹配
#    - 本地台账（_work/<proj>/project_doc.md）的「文档权威与同步台账」段记录的 revision
#    - 任何一项不一致 → 不能直接基于本地镜像下结论
```

具体案例：

| 项 | URL `K5d3...73tncf`（v2.1 飞书正本） | URL `Q1tBd...dpHnGI`（v2.0 杨编精撰） |
|---|---|---|
| revision | 5332 | 20492 |
| 开场 h1 | `宫阙 日 内` | `仙阙宫顶 日 外` |
| 打镜妖的人 | 陆母+暮云亭+白双双 | 陆行舟+白双双 |
| 反派别名 | 素鸢=镜妖=沈秋阑 | 镜妖 |
| 第 41 场占位批注 | 有【这里的要改 先将就看】 | 没有 |

锐评前**必须**先 fetch 在线版定锚——不要靠本地镜像猜。

## 4. lark-cli 实测坑（额外补充第四节）

- `lark-cli docs +fetch --doc <url> --scope outline --max-depth 2` 返回结构最外层 `data.document.content` 是 XML fragment string，要 `lxml` 或正则提取 `<h1>` 才拿到 h1 列表
- `lark-cli drive +add-comment --block-id <id>` 必须配合 `--type docx`（token 是 docx 时），否则找不到 block
- `+add-comment --content @./file.json` 文件必须在 cwd 相对路径下；MSYS/git-bash 上 `/tmp` 是 bash 虚拟路径会报 `must be a relative path`
- `+add-comment` 的 `text` 元素必须是纯文本字符串，嵌套 `{"text":{"content":"..."}}` 报错 `cannot unmarshal object ... field text of type string`
- `+add-comment` 不接受独立 `mention` 元素；用 reply 段独立 `mention_user` 元素：`{"type":"mention_user","mention_user":"<open_id>"}`，其中 `mention_user` 字段是字符串
- 主评论用纯 text 不会真触发 @ 通知；要触发 @ 必须 `+add-reply` 加一条独立 `mention_user` reply
- `+list-comments` 返回的 items 字段扁平、`reply_list` 嵌套结构与 `+batch-query-comments` 不同；验证评论是否真挂上去必须用 `+batch-query-comments --comment-ids <id1>,<id2>,...`

## 5. 2026-09-03 实战：DM 活 / 群死（SDK dispatcher 故障）

### 现象

- 飞书后台：事件与回调显示「长连接模式 + im.message.receive_v1 已订阅 + 全部权限已开通」——配置 100% 正确
- gateway 日志：`Connected in websocket mode (feishu)` + `✓ feishu connected` —— adapter 视角连接正常
- **DM 通道**：11:09:17 入站图片（chat_id `oc_a856f8f1...`，sender `ou_94566a9...`），11:14:08 入站文字+图片——**正常 dispatch 并 `Inbound dm message received`**
- **群通道**：11:05 用户 `@Hermes 测试`、10:54/10:55 陈星艳两次 `@Hermes 把这个文档放入伏妖记文件夹的新建一个美术子文件夹中`、11:17 陈星艳再次 `@Hermes`——**全部静默**，grep message_id 在 gateway.log 零结果

### 诊断过程（复用第六节排查步骤）

1. **初次排查：重启 gateway**（PID 59324 → 61596），11:03 重启后 11:04 `Connected in websocket mode`——**无效**
2. **怀疑配置**：用 `drive +inspect` 验证两条 URL（docx / wiki）指向同一文档 `XmEv...sonNe`；用 `lark-cli im +chat-search --query "天有答辩"` 拿 chat_id `oc_b7396f845a84a3aebdb1bf38c872e37a`；手动用用户账号在群里 reply 一条「（系统自检，非本人消息）」——群消息 gateway 零入站日志
3. **判定飞书后台 OK**：让用户浏览器爬 `https://open.feishu.cn/app/cli_aafaf3e37ef89cc2/event`，确认订阅方式是「长连接」（不是 webhook）、`im.message.receive_v1` 已订阅、所需权限（`im.message.receive_v1` 相关 4 项）全部「已开通」
4. **adapter 源码定位**：`hermes-agent/plugins/platforms/feishu/adapter.py:2626` `_handle_message_event_data` 和 `:4371` `_admit`，handler 注册完整（line 1700-1726 EventDispatcherHandler.builder().register_p2_im_message_receive_v1(...)）
5. **DIAG patch**：给 `_handle_message_event_data` 入口 + `_admit` 拒绝分支加 `logger.warning("[Feishu-DIAG] ...")`，捕获 `chat_id` / `chat_type` / `mentions` / `text`。重启 gateway（PID 61596），让用户在群里 @Hermes 测试
6. **DIAG 结果**：
   - 群 reply 类型消息 → `[Feishu-DIAG] Inbound candidate: msg_id=om_xxx chat_id=oc_b7396... chat_type='group'` + `ADMIT REJECTED: reason=group_policy_rejected ... mentions=[]`
   - **群 post 类型消息（纯文本 @Hermes 含 mention 标签）→ 完全没产生 Inbound candidate 日志**
   - DM 通道 → 不受影响，照常 dispatch

### 根因定位

**「DM 活 / 群死」指纹 + 「reply 进 pipeline / post 不进」分裂** 共同指向：

**`lark_oapi.ws.client.Client._handle_data_frame`（SDK 文件 `venv/Lib/site-packages/lark_oapi/ws/client.py:291`）的反序列化路径**对群消息有 bug——具体表现：
- **post 类型（msg_type=post，含 mention_user 元素）的群消息**：frame 收到，但 `event_handler._do_without_validation(pl)` 反序列化时**要么识别不到 event type、要么 mention 字段解析失败**，事件被 SDK 内部吞掉，根本没调到 hermes adapter 的 `p2_im_message_receive_v1` handler
- **reply 类型群消息**：反序列化成功但 `message.mentions` 字段被 SDK 置空，导致 hermes `_admit` 走 `require_mention=True` + `_mentions_self` 返回 False → `group_policy_rejected`

Hermes adapter 改不出来。**根因 5**（SDK dispatcher 不推）。

### 临时修复（治标）

`_handle_message_event_data` 入口 + `_admit` 拒绝时打 WARNING 级 `[Feishu-DIAG]` 日志，含 `chat_id` / `chat_type` / `mentions`（结构化列表）/ `text` 前 120 字。验证：

```bash
grep "Feishu-DIAG" ~/AppData/Local/hermes/logs/gateway.log | tail -10
# 2026-09-03 11:39:57 WARNING [Feishu-DIAG] Inbound candidate: ... chat_type='group'
# 2026-09-03 11:39:57 WARNING [Feishu-DIAG] ADMIT REJECTED: reason=group_policy_rejected ... mentions=[]
```

**注意**：`# [Feishu-DIAG]` 标记替代了原 `# [HERMES_FIX 2026-08-27 silent-drop-visibility]` 标记。两者并存不冲突。

### 永久修复（治本候选）

- **A. 升级 lark-oapi**：`pip install -U lark-oapi`，查 PyPI changelog 找群消息 mentions / protobuf 解析修复（**优先级最高**）
- **B. webhook 模式回退**：`.env` 加 `FEISHU_CONNECTION_MODE=webhook`，飞书后台事件与回调切「将事件发送至开发者服务器」+ 配 `FEISHU_VERIFICATION_TOKEN` 或 `FEISHU_ENCRYPT_KEY` 二选一
- **C. adapter 加 fallback mention detection**：`if not message.mentions: parse content for @bot_name and reconstruct mentions`——治标不治本

### 配套脚本改造建议

`scripts/feishu-orphan-messages.py` 当前只检测 `sender_type=='user'` 消息的 inbound 缺失。**对根因 5 增强**：

- 输出增加 `orphan_pattern: 'DM_OK_GROUP_FAIL'` 字段——区分「单消息单会话孤儿」vs「全群消息孤儿（SDK dispatcher）」
- 检测方法：窗口内若有 DM 入站日志但同窗口群消息全孤儿 → `DM_OK_GROUP_FAIL=True`
- 触发该 pattern 时 cron prompt 自动建议升级 lark-oapi（或查 hermes-feishu-internals 是否有已知 SDK 兼容矩阵）

## 6. DM 通道 vs 群通道的诊断指纹（2026-09-03 提炼）

`gateway.log` 里 grep `Received raw message` 或 `Inbound (?:dm|group) message received`，按 chat_type 拆开统计：

| 模式 | 根因定位 |
|---|---|
| DM ≥ 1 + 群 = 0 | **SDK dispatcher 不推群消息**（根因 5）——查 lark-oapi 版本 + 升级 |
| DM = 0 + 群 = 0 | gateway 整体 inbound 没起 / 没收到任何 raw event——查 SDK 连接 + 后台订阅配置 |
| DM ≥ 1 + 群 ≥ 1 但消息不回 | agent 侧问题（agent run 没跑 / LLM provider 异常 / skill 加载失败）——不在 silent drop 范围 |
| 群 ≥ 1 但 inbound 比 raw 少得多 | adapter 决策层 silent drop（根因 1-4）——开 DIAG 看 reason |

**`DM ≥ 1 + 群 = 0` 是 SDK dispatcher 故障的指纹**——单凭这一条就能跳过配置层排查，直接进 SDK 版本/源码比对。