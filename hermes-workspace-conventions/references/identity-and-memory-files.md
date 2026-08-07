# SOUL.md / USER.md / MEMORY.md / Skill — 四层知识架构

四个载体都在 Hermes 的知识系统中，但注入层级和作用完全不同。

## 核心原则（2026-07-24 重构）

```
SOUL.md  = 人格（我是谁、怎么做事）          → 注入 stable tier
Skill    = 行为指令（做之前对照）              → 加载到注意力焦点
Memory   = 决策知识（做决策时引用）            → 注入 volatile tier
USER.md  = 用户画像（用户是谁、偏好）          → 注入 volatile tier
Obsidian = 存档（版本快照/TODO/一次性记录）    → 不注入，wikilink 可达
```

## 为什么行为规则在 memory 里不触发

Memory 在系统提示中处于「背景知识」层。agent 在任务进行中注意力集中在 skill 的当前步骤上，不会主动扫描 memory 找 checklist。**Memory 告诉 agent「我知道这个规则」——但 agent 没有执行器在关键时刻主动检索它。**

→ **行为指令放 skill，决策知识放 memory。**

## 文件对照

| 文件 | 路径 | 放什么 | 不放什么 |
|------|------|--------|---------|
| **SOUL.md** | `~/.hermes/SOUL.md` | 人格声明（诚实、直接、怎么做事） | 操作规则、行为指令 |
| **MEMORY.md** | `~/.hermes/memories/MEMORY.md` | 决策知识（不记会犯错的事实） | 行为指令、TODO、版本快照 |
| **USER.md** | `~/.hermes/memories/USER.md` | 稳定偏好（身份、沟通风格） | 项目状态、配置快照 |
| **Skill** | `~/.hermes/skills/` | 行为指令、工作流、陷阱 | 一次性教训、会过时的数据 |

## 分类门禁

写 memory 前逐条确认：

| 问题 | 答案"是" → | 出口 |
|------|-----------|------|
| 不记会犯错？ | → | **memory** |
| 下次还要照着做？ | → | **skill** |
| 需要存档但不用每次提醒？ | → | **Obsidian** |

三个都不满足 → 不记。

## USER.md vs 飞书成员画像（2026-08-07 澄清）

用户问「USER 画像是？」「成员画像呢」时混淆过这两者——注意区分：

| | USER.md（全局画像） | 飞书成员画像 |
|---|---|---|
| 归属 | 唯一用户（妖玉） | 团队每个成员一人一份 |
| 路径 | `~/AppData/Local/hermes/memories/USER.md` | `Obsidian Vault/成员画像/<真名>.md` |
| 内容 | 身份、沟通风格、稳定偏好 | frontmatter（open_id/角色/专长/参与项目/updated）+ 沟通偏好/擅长/协作备注 |
| 写入 | 由用户言行沉淀（agent 维护） | bot 观察自动沉淀（同类观察合并，不设条数上限），妖玉可审（`@bot 画像变更报告`） |
| 应用 | 全局注入每个会话 | 飞书回复前查发送者画像，个性化语气/推荐人选 |

关键点：
- **成员画像 ≠ USER.md**——USER.md 是唯一用户的全局画像，成员画像是飞书协作按人分文件
- 成员画像机制「开放」≠ 有数据——机制就绪（代码/规则/模板在位）但目录可能只有 `_模板.md`，需 bot 观察沉淀或手动建
- 成员访问权限名单在 `~/AppData/Local/hermes/feishu_comment_pairing.json`（approved），管权限不管画像

## Pitfalls

- **摩擦不对称**：`memory` 工具零摩擦（一行搞定），`skill_manage` 需匹配 old_string。agent 在认知负荷高时总结冲动自然流向 memory。Feature request: [#70488](https://github.com/NousResearch/hermes-agent/issues/70488)。
- **注意力焦点**：行为指令在 memory 里不会被主动检索——agent 注意力在 skill 上。搬到了 skill 才能被触发。
- **SOUL.md 确实被加载**：`prompt_builder.py:1876` 有 `_load_soul_file()` 函数。不要凭记忆说"不加载"。
