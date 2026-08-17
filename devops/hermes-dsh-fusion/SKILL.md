---
name: hermes-dsh-fusion
description: 用 DSH 跑长任务/批量活时用——桥驱动、轨迹回流、无感呈现。
whenToUse: 任务适合独立执行（长任务/批量处理/重工具活）时，或用户点名 DSH 时
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [DSH, DeepSeek-Harness, 融合, 执行引擎, 批量任务]
    related_skills: [hermes-workspace-conventions]
---

# Hermes × DSH 无感融合

**原则：不是"外包"，是一个增强的 Hermes。** 用户在 Hermes 里说话，Hermes 判断怎么干——适合 DSH 执行形态的活自动落到 DSH（其会话 cwd 长在 Hermes 项目目录，规范/知识/资产天然同源），思考链路回流 Hermes 对话流，用户在对话里看到完整推理过程，无从感知也不需感知"这是 DSH 干的"。

**默认策略：默认用 DSH，失败自动降级。** 收到任务先默认考虑 DSH 引擎参与（全部场景开放，没有禁区）。**降级护栏**：桥不可用/首次调用报错 → 自动降级 Hermes 本机执行，不阻塞用户，并在回复里说明一句（不夸大、不掩饰）。用户不需要点名"用 DSH"——默认就在用。

## When to Use

- **默认：全部场景开放。** 收到任务默认考虑 DSH 引擎参与——工程执行（长任务/批量/文件/分析/脚本）+ 创作推敲（剧本/歌词/分镜，DSH 读知识库+项目文档参与） + 协作起草（回复/文档，DSH 起草或审读）+ 渠道辅助（简报生成/记忆整理，DSH 产出 Hermes 落库）
- 用户点名「用 DSH」
- 唯一保留：渠道工具的**最终执行**（飞书发送、cron 调度、Hindsight 写入、MCP 配置）由 Hermes 完成——DSH 没有这些渠道工具；但能力输出（起草/分析/审读/生成）可以来自 DSH

## 桥（唯一的交接点，用户无感）

`scripts/dsh_bridge.py`——封装 DSH web /api 网关（127.0.0.1:8080，已实测）：

```bash
# 跑一个任务（自动路由：同 cwd+同主题+30分钟内 → 复用会话，否则新开）
python scripts/dsh_bridge.py run "<cwd>" "<任务>" [--topic <主题>] [--new] [--timeout 秒]

# 查看会话注册表
python scripts/dsh_bridge.py list
```

前提：DSH web 在 8080 运行（`Projects/deepseek-harness` 下 `node --import tsx/esm apps/cli/src/bin.ts web --port 8080`）；OPENCODE_GO_API_KEY 由桥从 LOCALAPPDATA/hermes/.env 自动读取，无需手设。

## 什么时候用桥（默认用，全部场景开放）

**默认值 = 用 DSH。** 判断句是"这活怎么用上 DSH 引擎干得更好"——没有禁区。创作推敲时 DSH 在共享工作区读知识库/项目文档参与（规范/术语纪律经任务模板注入）；协作起草时 DSH 出初稿 Hermes 定稿；渠道辅助时 DSH 产出 Hermes 落库。用户感知始终是一个更强的 agent。

**同源机制**：DSH 会话 cwd 在共享工作区，AGENTS.md 和 .agents/skills 自动生效——它干活时天然遵守项目规范、能读知识库（含创作类知识库）。无墙：执行形态（一次投喂、长时间独立干）和交互形态（来回对话）都可用 DSH 引擎参与，由 Hermes 按场景编排。

## 任务模板（保证轨迹质量 + 结构化总结）

投给 DSH 的任务文本建议结构（Hermes 组装，不用写文件交接）：

```
【背景】<项目/目录一句背景，必要时附相关知识库路径提示，如 妖玉知识库在 <path>，需要时自己读>
【任务】<具体任务，讲清目标、范围（允许动哪些文件/禁止动哪些）>
【要求】完成后用一行 JSON 总结（不要 markdown 代码块，直接输出这行）：
{"changes":"改了什么","verification":"怎么验证","leftovers":"遗留问题"}
```

**范围声明很重要**：明确"只许动 X，不许动 Y"；DSH 干完 Hermes 要按此对 diff。

## 无感呈现（关键）

桥返回的轨迹是结构化文本（🔧 工具调用 / ↳ 结果 / 💬 推理 / ── 回合）。Hermes 把轨迹**直接贴回对话流**，用户看到的就是 Hermes 在干活的样子——不要加"这是 DSH 干的"之类的话，保持无感（除非用户问起）。

```markdown
> 已开始处理：<任务一句话>
> 🔧 pwsh: Get-ChildItem ...
> 💬 推理：...
> （轨迹精简展示，太长的工具结果截断）
> ✅ 完成：<结果摘要>；文件已落在 <路径>
```

两个规则：
1. 轨迹**精简展示**：推理/工具行全保留，工具结果只留摘要（详细可让用户要求展开）
2. 结构化总结（changes/verification/leftovers）**必须消化后转述**，不贴原始 JSON

## 验收与归位（Hermes 的责任，不进对话也要做）

DSH 报告"完成"只当线索。Hermes 独立验证：

1. **diff 对照范围**：`git diff --stat` 对照任务范围声明，越界改动即 FAIL
2. **测试/检查**：涉及代码跑测试或语法检查；纯文件任务核对产物清单
3. **归位**：验收通过 → `git add <产物> && git commit`（中文、单逻辑）→ 重要结论写回项目文档 → 值得记住的结论 retain 进 Hindsight

**git 唯一写者 = Hermes**：命令里不带 git 操作给 DSH（桥不传 git 任务除非明确要求）。

## 会话管理（内部机制，用户无感）

- 同 cwd + 同主题 + 30 分钟内 → **复用**（DSH 记得前面的上下文，省 token 省重述）
- 语义切换（新任务主题）→ **换 topic 参数**（桥按 topic 判新开）
- 需要干净重试 → **--new** 强制新开
- 跨目录任务 → cwd 不同自然新开
- DSH 内置自动压缩兜底（长会话不爆，无需担心轮数；具体阈值以 DSH 实测为准，不写死假设）

registry 文件：`.hermes/dsh-registry.json`（可查可删，删了即重置路由）。

## 坑

1. **会话 id 冲突**：桥已处理（同 id 复用/忙时换新 id）；手工调 API 时牢记"create 一次，prompt 永远同 id"
2. **任务文本里别带 git 指令**（唯一写者纪律）；要 DSH 分析 git 历史可以（只读）
3. **超时**：任务超过 timeout 会打印警告但会话保留，下次同主题投喂可续；超长任务给足 --timeout
4. **DSH web 重启**（8080 进程没跑）→ 桥报连接失败，先确认服务在跑；会话存磁盘可 resume
5. **轨迹里 assistant/chunk 是 token 级流**：桥用 assistant/message（完整消息），不要逐 chunk 展示
6. **Windows 路径**：cwd 用 `C:\...` 格式（桥接受），DSH 内工具用 pwsh（PowerShell 语法）