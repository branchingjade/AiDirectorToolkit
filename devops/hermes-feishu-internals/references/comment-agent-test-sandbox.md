# 飞书评论 agent 真流量验证沙箱（lark-cli 实战坑）

> 用途：当需要"真链路验证"评论 agent 路由/投递时，记录哪些 lark-cli 操作能触发 bot 事件、哪些不能，以及触发后的清理动作。

## 铁律（2026-09-03 实测）

**`lark-cli drive +add-comment --as user/bot` 都不能触发 bot 事件链。** 唯一真流量路径是用户在飞书 APP 内手动 @bot 发评论。

### 三个不能触发的原因叠加

| 限制 | 说明 |
|---|---|
| WebSocket 只推 `is_mentioned=true` | 飞书事件链只在评论里 @bot 时推 `drive.notice.comment_add_v1` |
| CLI 评论默认无 mention 元素 | lark-cli 默认的 content 只有 `type:text`,不构造 `mention_user` 元素 |
| bot 自己发被 self-reply filter drop | `--as bot` 发的评论事件 `from_open_id == self_open_id`,handler 直接 return |

即使用 `--as user` 发评论,**没 @bot 也不会触发 bot 处理**。

### 怎么确认 bot 处理路径正确

唯一可行的"接近真链路"验证方式——**手动构造一个被解析为 mention_user 的 content**，但 lark-cli 没有直接 API；**或者直接调用飞书 REST API 自己拼元素**（需自写 curl/requests）。绝大多数情况下不值得这个代价。

**实战姿势**:部署后让用户在飞书 APP 发一条原文评论 @bot,grep 日志:

```bash
grep "Intent detected" ~/AppData/Local/hermes/logs/gateway.log | tail -5
```

期望看到 `Intent detected as CREATIVE`（而非 `REPLY`），并且 `Loaded creative skill` + `api_calls>=2`（含 feishu_doc_read 调用）。

## lark-cli 操作实战坑（修复期 + 补给期踩到）

| 命令 | 坑 | 实测正确姿势 |
|---|---|---|
| `+add-comment` content JSON 结构 | 不接受 `{"elements":[...]}`` 嵌套（报错 "cannot unmarshal object into Go value of type []drive.commentReplyElementInput"） | 必须用顶层数组：`[{"type":"text","text":"..."}]` |
| `+add-reply` `--yes` 标志 | 不接受 `--yes`（"unknown flag --yes, did you mean --as?"）| 直接省略,命令本身就是写操作 |
| `+resolve-comment` `--yes` 标志 | 同样不接受 `--yes` | 同上,直接省略 |
| `+resolve-comment` `--as bot` 清理 user 评论 | bot 身份不能 resolve 自己没创建的评论 | 该场景下,改用 `lark-cli drive file.comment.replys` raw API（若 lark-cli 不可用,留给用户手动处理） |
| 评论 thread reply 后 `reply_id` 取值 | reply API 返回的 reply_id 直接来自 `data.reply_id`,**不是从 list-replies 再查** | 用 `lark-cli drive +add-reply` 返回的 `data.reply_id` 字段即可

## 测试评论清理纪律（用户 user-owned MEMORY 拍板）

bot 在测试期间发的任何顶层评论 / reply,**测试完必须清理**：
- reply 用 `lark-cli drive +delete-reply --reply-id <id> --comment-id <cid> --as bot`
- 顶层评论优先用 `lark-cli drive +resolve-comment --as bot` 标 solved（删除命令不一定开放给所有 doc）

**副作用清理由测试发起方负责**——不留垃圾评论、不污染文档评论历史、不留未配对的 bot 事件。

## 真流量验证 vs 单测 vs 灰盒

| 验证手段 | 覆盖率 | 成本 | 何时用 |
|---|---|---|---|
| **单测**（`unittest tests.gateway.test_feishu_comment`） | 意图路由 / prompt 拼装 / dispatcher fallback 逻辑 | 几秒 | 每次改 `feishu_comment.py` 后必跑 |
| **冒烟测**（`execute_code` 调内部函数 + 已知输入） | 复杂 case 边界（多文本签名、字符串拼接） | 1-2 分钟 | 加新关键词时/反转规则时 |
| **灰盒**（lark-cli 发测试评论看 webhook 触发） | 飞书 API 联通性 + dispatcher 主流程 | 5-10 分钟 | 部署后首次集成测试 |
| **真流量**（用户 APP 内发评论） | 端到端 WebSocket + 路由 + agent + 投递 | 用户动手 | 重大路由改动后首次确认**（不可替代）** |

**节奏**:改完代码 → 单测全绿 → 冒烟测新增 case → 重启 gateway → 灰盒发 1 条"纯文本看 reaction" "（确认事件链通）→ 让用户真发 1 条创作评论 → 看 Intent/Creative skill loaded/agent 调用次数 终态。

## 历史实战记录

- **2026-09-03 续写 bug 修复**：灰盒测 = lark-cli 发 bot/user 评论 → bot 没回执 → 真流量验证受限 → 落地双层防御（prompt + dispatcher fallback）+ 单测覆盖 26 case