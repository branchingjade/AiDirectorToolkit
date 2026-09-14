---
name: hermes-feishu-internals
description: "飞书端工程任务必先加载本 skill（用户 2026-09-03 拍板「飞书端都走」）——覆盖：评论 agent 事件链/访问控制/协作扩展/kanban 工具、群聊 require_mention 排查、侧边栏会话显示、state.db 会话持久化、会话路由/成员画像。触发词：评论@没反应、群不回消息、侧边栏没会话、群聊、群消息停摆、feishu 评论、feishu 工程、飞书端。"
version: 2.0.0
tags: [feishu, hermes, comment, kanban, internals, group, sidebar, session, gateway]
---

# Hermes 飞书内部机制 v2.0（2026-09-04 真流量验证通过）

飞书端工程任务的总入口（用户 2026-09-03 拍板「飞书端都走」）。

> **本版本是真流量验证版本**（2026-09-04 10:28 飞书 APP 测试通过：bot 读了全文、出了 3 版润色方案、成功投递）。之前所有"已部署 2026-09-03"的描述均为写文档时的幻觉（与 MEMORY 9/03 警告的"Creative work 章节已固化"是同一种模式），已全部删除。

---

## 1. 评论事件处理链（已验证）

```
飞书 WebSocket 推送 drive.notice.comment_add_v1
  → adapter.py → handle_drive_comment_event
  → feishu_comment.py（主流程）
```

主流程：解析事件 → 过滤（self-reply / 必须 @ bot / notice_type）→ 访问控制 → 加 OK reaction → 并行取文档元数据+评论详情 → 分支（whole / local）→ **意图路由**（`_detect_creative_intent`）→ `_run_creative_agent`（含 retry）或 `_run_comment_agent` → 投递/冷暴力兜底 → 清理 reaction。

**日志前缀 `[Feishu-Comment]`**：所有关键步骤有日志，排障第一动作 grep。

---

## 2. 访问控制（评论 @ 没反应的常见根因）

规则文件 `feishu_comment_rules.json`（mtime 热加载，无需重启）+ 配对文件 `feishu_comment_pairing.json`。三种策略：`allowlist` / `pairing`（默认） / `members`（推荐团队场景）。

```bash
./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules status
./venv/Scripts/python.exe -m plugins.platforms.feishu.feishu_comment_rules check docx:<token> <open_id>
grep "Feishu-Comment" logs/gateway.log | tail
```

⚠️ 改代码后必须重启 gateway（规则文件是热的，代码改动不是）。

---

## 3. 评论 agent 事件处理核心逻辑

### 3.1 会话持久化（state.db 双表，2026-09-03+04 落地）

每次 `_save_session_history` 双写：
1. `messages` 表：role+content+timestamp，session_id=评论 key
2. `sessions` 表：id=key, source='comment', title, user_id, message_count, started_at, last_activity_at（UPSERT，started_at 保留首次值）

**`source='comment'`** 是桌面侧边栏"飞书评论"平台的过滤键——**仅当 sessions 行写入成功，侧边栏才显示评论会话**。

### 3.2 评论 agent 配置（`_run_creative_agent`，2026-09-04 真流量验证通过）

```python
agent = AIAgent(
    model=model,                          # MiniMax-M3（评论独立模型）
    system_message=prefilled_system,       # ← 注入 feishu-comment-creative SKILL.md 全文
    conversation_history=history,          # 历史（stale 消息已过滤）
    quiet_mode=True,
    skip_context_files=True,
    skip_memory=True,
    max_iterations=25,                     # 创作型用 25 步（普通 agent 15 步）
    enabled_toolsets=["feishu_doc", "feishu_drive"],  # ← 含 4 个改正文工具
)
```

**AIAgent.run_conversation 真实签名**（2026-09-03 实战踩坑）：
```python
run_conversation(user_message, system_message=None, conversation_history=None, ...)
# ⚠️ 不支持 prefill_messages 参数（之前自吹的"prefill_messages 注入"是幻觉）
```

### 3.3 意图路由（`_detect_creative_intent`，5 步漏斗）

2026-09-03 反转白名单为黑名单+漏斗：

1. 空输入 → REPLY
2. 关键创作动词（润色/重写/扩写/续写/改写/接着写/改一下...）→ **CREATIVE**（升级兜底）
3. ≤6 字符 + 无创作动词 → REPLY（防"嗯/好的"误入）
4. 非创作黑名单（状态查询/闲聊/知识问句/业务管理）→ REPLY
5. 老白名单命中 → CREATIVE
6. **fall-through 默认 CREATIVE**（误报 cost < 漏报 cost）

**判断方法**：grep `[Feishu-Comment] Intent detected as` 日志——CREATIVE=走创作 agent，REPLY=走普通 agent。

### 3.4 强制 retry（`_run_creative_agent`，2026-09-04 落地）

检测逻辑：若 `actual_tool_calls == 0`（LLM 没调工具）且没有 3 版方案标记（"方案一/版本一/①"等）→ 强制 retry + system 加强提示"必须先调 feishu_doc_read"。

日志：`[Feishu-Comment] _run_creative_agent: RETRY with reinforced prompt` 即命中。

### 3.5 stale history 过滤（2026-09-04 落地）

- **stale history 过滤（2026-09-04 落地）**：历史消息中含"不可用"/"not available"/"调不通"的 assistant 消息被过滤（`_run_creative_agent` 用 `stale_keywords` 元组匹配）——防止 LLM 被旧错误答案"传染"（直接复制粘贴旧拒绝话术）。

日志：`[Feishu-Comment] filtered X stale history messages`。

### 3.6 冷暴力兜底（2026-09-03 落地，2026-09-04 真流量验证通过）

**铁律**：任何评论事件必须有一份投递——禁止空回复/NO_REPLY/静默退出。`cold-shoulder fallback` 触发器在 `handle_drive_comment_event` Step 5。

- Prompt 层：`_COMMON_INSTRUCTIONS` 硬约束"NEVER reply with empty text or NO_REPLY silently"
- Dispatcher 层：agent 返回空/NO_REPLY → 强制改写为"上下文不足,请贴原文 / 文档正文 @bot 重试"可见回执 → 强制投递

---

## 4. feishu_doc_tool.py 工具集（2026-09-04 落地）

### 4.1 跨线程 client fallback（2026-09-04 落地）

原 `threading.local()` 在 worker thread 拿不到 client → 修为 3 层回退：

1. thread-local `_local.client`
2. 进程全局 `_GLOBAL_CLIENTS[thread_ident]`
3. `_FALLBACK_CLIENT`（最后一个 set 的 client）

**诊断口诀**：bot 调了 `feishu_doc_read` 但报"client not available" → 先看 gateway.log 是否有 `set_client` 调用（应该有）。

### 4.2 feishu_doc_update（2026-09-04 落地）

改正文工具，包装 `lark-cli docs +update`（白名单 command：str_replace / block_delete / block_insert_after / block_replace / overwrite / append）。

**铁律**：创作型 agent 里**默认不调**这个工具（只出候选方案，用户挑了再改）。若 bot 主动改文档，需检查 system_message 硬约束是否仍含"不要直接调 feishu_doc_update"。

---

## 5. 群聊 require_mention（2026-09-03 落地）

```yaml
group_rules:
  oc_685820...（开工群）:
    require_mention: false    # 群内不 @ 也响应
  oc_b7396f...:
    require_mention: false
  oc_984e2c...:
    require_mention: true     # 保持默认
```

默认 `require_mention: true`，只有显式登记的群才开放——防止未知群被误触达。

---

## 6. 健康度检查脚本

`scripts/feishu-collab-health.py`（2026-09-03 改）：
- 评论线程：从 `state.db messages` 表查（不再是 `_hermes/评论会话/` 目录）
- 群聊维度：新增【5b】群聊渠道明细 + `group_whitelist_coverage()`
- 群白名单覆盖检查：已知活跃群是否在 group_rules 显式登记

---

## 7. 测试覆盖（2026-09-03 真实落盘）

- `TestDetectCreativeIntent`：15 case（续写 bug 复现、老白名单不退化、极短误伤、闲聊/状态/知识/业务/元问句→REPLY、多文本 OR 逻辑、fall-through）
- `TestColdShoulderFallback`：2 case（prompt 硬约束 + _NO_REPLY_SENTINEL 保留）

---

## 8. 通用坑

- **Windows 文件名**：会话 key 含 `:` 和中文报 WinError 123。percent-encode 后 `%` → `_pct_`
- **成员名单.json**：`admin: ["真名"]` + `成员: {open_id: {name, role}}`
- **工具发现机制**：`tools/` 目录自动扫描注册（带 `tool_discovery_cache.json`），新工具文件无需手动挂载

---

## 参考

- `references/comment-session-persistence.md` — 双写 state.db 设计
- `references/comment-creative-routing-misses.md` — 意图路由漏词实战
- `references/feishu-collab-health-check.md` — 三渠道健康检查脚本
- [feishu-gateway-setup](../feishu-gateway-setup/SKILL.md) — 网关配置/群聊 require_mention
- [feishu-multi-user-collab](../feishu-multi-user-collab/SKILL.md) — 多用户协作业务规则
