---
name: hermes-delegate
description: 双向桥·DSH 把任务交给 Hermes 执行的操作指南——DSH 会话内用 scripts/hermes_api.py 调用 Hermes api_server（127.0.0.1:8642）：任务委派（chat）、会话共享（sessions/messages）、上下文共享（--session 续投）。触发词：让 Hermes 干、交给 Hermes、发飞书、归档 Obsidian、改 cron、双向桥、hermes_api。
version: 1.0.0
metadata:
  hermes:
    tags: [dsh, hermes, 双向桥, delegate, interop]
    related_skills: [hermes-dsh-fusion, hermes-dsh-skill-sync]
---

# hermes-delegate：DSH → Hermes 委派

双向桥的 DSH 侧用法。机制/判据/审计纪律与 `hermes-dsh-fusion` skill 同源，本 skill 只写操作。

## When to Use

- 任务需要 Hermes 侧能力：写类渠道（飞书发送 / cron 增改 / Obsidian 写入 / git 提交）
- 需要 Hermes 专属能力（记忆 recall、kanban、Hermes 侧上下文延续）
- 需要 Hermes 会话历史/上下文的任务（会话共享 + 上下文共享）
- 用户在 DSH 会话里点名"让 Hermes 去做 X"

## 调用（DSH 会话内 pwsh）

```powershell
python C:\Users\HMSJ\Documents\Hermes\scripts\hermes_api.py chat "<任务>" [--session <Hermes会话id>] [--timeout 秒]
python C:\Users\HMSJ\Documents\Hermes\scripts\hermes_api.py sessions [--limit N]        # 会话共享
python C:\Users\HMSJ\Documents\Hermes\scripts\hermes_api.py messages <session_id> [--limit N]  # 会话共享
```

- 首次 chat 响应返回 session id（形如 `api-xxxxxxxx`），后续带 `--session` 续 Hermes 上下文（省 ~34K tokens/轮）
- 输出末尾固定 `HERMES_RESULT {json}`：status（done/error）、session、reused、token 用量
- 退出码 0 = 正常；非 0 = 桥/服务故障

## 纪律

- **写类单出口**：写类动作（飞书/git/Obsidian/cron）由 Hermes 执行，DSH 只投任务文本，不绕开
- **任务文本要求**：讲清目标、范围（允许/禁止动哪些），必要时加【补充约定】防瞎猜
- **UTF-8**：必须走 hermes_api.py（脚本显式 UTF-8）；PowerShell 直发中文会乱码
- **失败处理**：timeout 不重开新线，同 session 续投"继续"；结果可疑时用 messages 读会话历史核查

## 验证

- 投递成功：HERMES_RESULT status=done
- Hermes 真实执行：messages <session_id> 看 Hermes 侧工具调用记录；渠道类动作以渠道实况为准（如飞书消息 id）
