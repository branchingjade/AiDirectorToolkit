# 评论意图路由漏词陷阱（2026-09-03 实战）

## 现象

用户在飞书文档评论里发创作指令，bot 不回复 / 静默 / reaction 加完又删掉（最终用户视角：评论发出去没反应）。

## 真因家族（两种互不相同的根因）

| 类型 | 真因 | 触发条件 | 修复层级 |
|---|---|---|---|
| **A. 软提示陷阱**（3.6 节） | `_COMMON_INSTRUCTIONS` 第 873 行「if not enough, use feishu_doc_read」是软提示，LLM 跳过读全文直接出方案 | 创作指令**已成功路由到 CREATIVE agent**，但 agent 跳过必读步骤 | 代码层硬化 prompt（路径 A）|
| **B. 意图路由漏词**（3.7 节） | `_detect_creative_intent` 是关键词白名单，未列出的创作动词被路由到普通回复 agent → 普通 agent 看到引用段读不到上下文 → `NO_REPLY` → 静默 | 创作指令**没路由到 CREATIVE agent**（连读全文的机会都没给）| 白名单 → 黑名单反转（本次已部署）|

**关键区分**：A 类日志会看到 `Intent detected as CREATIVE — dispatching to _run_creative_agent` 然后 agent 不调 feishu_doc_read；B 类日志会看到 `Intent detected as REPLY — dispatching to _run_comment_agent` 然后 `response=NO_REPLY`。**先 grep 日志看 Intent 行**，分清是 A 还是 B 再下手。

## B 类实战：2026-09-03 09:22 事件

用户评论原文：
> 结合全文进行续写,这一段要求体现陆青山一行人来到青舟渡的景象描写,三人获得关键信息,山神娶韩家女为妻。文风结合全文。逻辑完整。

意图关键词「**续写**」不在 `_CREATIVE_INTENT_PATTERNS` 16 组正则里。

**日志链**（伏妖记文档 `K5d3d03KhoAhoOxv3TMc873tncf`，comment `7681113015973858604`）：
```
09:22:08 Intent detected as REPLY — dispatching to _run_comment_agent
09:22:10 _run_comment_agent: done api_calls=1 response_len=8 response=NO_REPLY
09:22:10 Agent returned NO_REPLY, skipping delivery
```

**修复（已部署 2026-09-03）**：`_detect_creative_intent` 从「正向白名单」反转为「默认 CREATIVE + 非创作黑名单降级」。代码位置 `plugins/platforms/feishu/feishu_comment.py:929+`。

新逻辑链（5 步）：
1. 空输入 → REPLY（防御默认）
2. 命中 `_CRITICAL_CREATIVE_LEAD` 或 `_CRITICAL_CREATIVE_VERBS`（升级兜底，覆盖「续写/扩写/重写/改写/接着写」）→ CREATIVE
3. 极短文本（≤6 字符）且无创作动词 → REPLY（防止「在吗/嗯/好的」被默认路由走 25 步 agent）
4. 命中 `_NON_CREATIVE_INTENT_PATTERNS`（状态查询/闲聊/知识问句/业务管理问句/元问句 8 组黑名单）→ REPLY
5. 命中老 `_CREATIVE_INTENT_PATTERNS`（含新加的「续写/扩写/改写」）→ CREATIVE
6. **fall-through 默认 CREATIVE**（反转前的默认 REPLY 是 bug 源头）

## B 类修复要点（避免重蹈覆辙）

- **白名单设计永远会漏词**：任何「正面列举核心动词」的策略都无法穷尽（用户口语、自由组合）。**反转语义是唯一治本方案**。
- **反转后必须配套极短回复二次校验**：≤6 字符的「嗯/好的/ok/👍/收到」如果不显式排除，会把日常闲聊当创作任务送进 25 步 agent（浪费 token）。
- **测试覆盖是漏词的根因之一**：原 `tests/gateway/test_feishu_comment.py` 142 行**完全没覆盖意图识别函数**——这是「续写」漏判的直接根因。修复时一次性补 `TestDetectCreativeIntent` 类（15 case：含 bug 复现原文、老白名单不退化、极短指令不误伤、闲聊/状态/知识/业务/元问句 → REPLY、多文本签名 OR 逻辑）。
- **fall-through 默认 CREATIVE 是有意识的代价**：可能误伤「剧情推理类」问句（如「陆青山能不能打得过小白」）走 25 步 agent 浪费 token。**误报 cost < 漏报 cost**（用户原话「走真实链路不接受口头声称」），这个权衡是用户拍板走治本方案的前提。

## 真流量验证局限（重要！）

部署后**没法用 `lark-cli drive +add-comment --as user` 触发 bot 事件**——因为：
- 飞书 WebSocket 只推送 `is_mentioned=true` 的事件
- `--as user` 发评论不带 mention_user 元素 → 事件根本不到 handler
- bot 自己发评论被 self-reply filter 直接 drop（`from_open_id == self_open_id`）

**唯一的真流量验证路径**：用户在飞书 APP 内手动 @bot 发评论。看日志关键词 `Intent detected as CREATIVE`（不再是 REPLY）即确认修复生效。

## 给 agent 的执行清单（评论 agent 路由问题）

1. `grep "Intent detected" logs/gateway.log | tail -20` — 看 Intent 行是 CREATIVE 还是 REPLY
2. 若 REPLY + 评论文本含创作动词 → 走 3.7 节白名单漏词诊断
3. 若 CREATIVE + agent 不调 feishu_doc_read → 走 3.6 节软提示陷阱
4. 若 REPLY + 评论文本明显非创作（状态查询/闲聊/管理问句）→ 路由正确，问题在别处
5. 若 Agent returned NO_REPLY + Intent=CREATIVE → 检查 feishu_doc_read 调用记录，再走 3.6

## 关联

- SKILL.md 3.6 节（软提示陷阱）— A 类家族
- SKILL.md 3.7 节（白名单漏词）— B 类家族（本次）
- `feishu-comment-creative` user-owned skill — 创作工作流定义
- `feishu-comment-creative` 在 user-owned 下被禁止修改；本次代码层反转在 `feishu_comment.py` 而非该 skill 文本