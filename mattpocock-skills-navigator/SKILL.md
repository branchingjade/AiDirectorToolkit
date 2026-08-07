---
name: mattpocock-skills-navigator
description: >-
  全技能导航员。当用户遇到任何工程/创作/研究/运维/生产力场景，
  根据情境推荐最适合的技能组合。覆盖全部100+技能。
  Trigger: 该用什么技能、有哪些技能可用、帮我选技能、这个场景用哪个skill。
category: mattpocock-engineering
---

# Matt Pocock 技能导航

## 决策树——一句话定位

遇到任何事情 → 说场景 → 我告诉你用什么技能。

完整技能目录见 `references/full-ecosystem.md`（含 100+ skill 的类别、用途、触发词速查）。

## 六大入口场景

### A. 有新想法、想做一个功能

| 情境 | 用 |
|------|-----|
| 有代码库，想法模糊 | `/grill-with-docs`（追问+写 CONTEXT.md） |
| 无代码库，想法模糊 | `/grill-me`（追问，无状态） |
| 需要探索多个不确定方向 | `/decision-mapping`（建决策地图，逐个消灭） |
| 追问中有东西需要跑代码验证 | `/handoff` → 新 session `/prototype` → `/handoff` 回来 |

### B. 需求已明确，准备开工

| 情境 | 用 |
|------|-----|
| 当前会话讨论充分，直接实现 | `/to-prd` → `/to-issues` → `/implement` |
| 多 session 的大型工作 | `/to-prd` → `/to-issues`（每 issue 一个新鲜 session 跑 `/implement`） |
| 实现过程中要写测试 | `/tdd`（在 implement 内部触发） |
| 实现完了要审查 | `/review`（Standards + Spec 双轴） |

### C. 收到 bug / issue / PR，需要处理

| 情境 | 用 |
|------|-----|
| Issue 进来了，不知道该怎么处理 | `/triage`（分诊：分类 → 验证 → 必要时追问 → 写 agent brief） |
| Triage 后发给 agent 实现 | `/implement` |
| Bug 很难定位 | `/diagnosing-bugs`（6 阶段：反馈循环是第一要务） |
| 修完 bug 发现架构有隐患 | `/improve-codebase-architecture` |

### D. 代码库健康检查

| 情境 | 用 |
|------|-----|
| 想看看代码哪里可以更好 | `/improve-codebase-architecture`（扫描→HTML报告→选一个深度化） |
| 讨论中术语混乱，需要统一 | `/domain-modeling`（更新 CONTEXT.md） |
| 模块接口设计讨论 | `/codebase-design`（深模块/接口/接缝词汇表） |
| 讨论中做了重要架构决策 | 问用户是否要写 ADR（domain-modeling 的一部分） |

### E. 跨 session 协作

| 情境 | 用 |
|------|-----|
| 当前窗口太长，需要换新 session | `/handoff`（压缩成文件，新 session 读文件继续） |
| 同一个 session 内，阶段间休息 | `/compact`（内置，压缩早期对话但保持同一窗口） |
| 需要分支出去做原型 | `/handoff` 出去 → 新 session `/prototype` → `/handoff` 回来 |

### F. 基础设施 / 一次性设置

| 情境 | 用 |
|------|-----|
| 新项目首次使用这套技能 | `/setup-matt-pocock-skills`（配置 issue tracker, labels, domain docs） |
| 保护 git 误操作 | `git-guardrails-claude-code` |
| 设置 pre-commit hooks | `setup-pre-commit` |
| 写技能/改技能 | `writing-great-skills`（方法论参考） |

## 技能间调用关系

```
grill-with-docs
  ├── 调用 grilling（追问引擎）
  └── 调用 domain-modeling（同步更新术语/ADR）

grill-me
  └── 调用 grilling（追问引擎，无状态）

improve-codebase-architecture
  ├── 依赖 codebase-design（架构词汇）
  ├── 调用 grilling（深度化追问）
  └── 调用 domain-modeling（同步术语）

decision-mapping
  ├── 调用 grilling + domain-modeling（每个 ticket）
  └── 调用 prototype（Research/Prototype 类型 ticket）

triage
  ├── 调用 grilling + domain-modeling（追问 request）
  └── 读取 CONTEXT.md + ADRs（了解上下文）

to-prd / to-issues / implement / review
  └── 都读取 CONTEXT.md + ADRs（用项目术语）
```

## 技能不能用来做什么

| 不能用 | 原因 |
|--------|------|
| `/triage` 处理 `/to-issues` 产出的 issue | 那些已经是 agent-ready，不需要再分诊 |
| 在一个 `/implement` 窗口做多个 issue | 每个 issue 应该新鲜 session，避免上下文污染 |
| 实现时代码审查看 `/review` 之外的东西 | review 是双轴（Standards + Spec），不要混在一起评 |
| `/grill-with-docs` 在中途 `/compact` | 追问需要完整上下文才能保持一致性 |

---

# 完整技能体系导航 (All Skills)

## 影视/AI 创作管线

| 场景 | 用 |
|------|-----|
| AI 图像/视频生成 (SD/Flux/Wan) | `comfyui` — 本地或云端，全流程脚本化 |
| AI 音乐生成 (Suno 替代) | `heartmula` (开源本地) 或 `songwriting-and-ai-music` (Suno 云端) |
| 3Blue1Brown 风格数学/算法动画 | `manim-video` — 纯 Python 动画 |
| TouchDesigner 实时视觉 | `touchdesigner-mcp` — MCP 直接控制 TD |
| 写作去 AI 味 | `humanizer` — 29 种模式检测+重写 |
| 剧本创作管线 | `AI短剧编剧助手` → `AI短剧导演助手` → `AI提示词助手` |

## 自动化编程代理

| 场景 | 用 |
|------|-----|
| 委托 Claude Code 写代码 | `claude-code` (print 模式 `-p` 或 tmux 交互) |
| 委托 Codex CLI 写代码 | `codex` |
| 委托 OpenCode 写代码 | `opencode` |
| Hermes 自身配置 | `hermes-agent` |

## 开发方法论

| 场景 | 用 |
|------|-----|
| 写实现计划 | `plan` — 写到 `.hermes/plans/` |
| 快速验证可行性 | `spike` — 一次性实验 |
| 系统化调试 (禁止猜) | `systematic-debugging` — 4 阶段 |
| TDD (标准版) | `test-driven-development` |
| TDD (Matt Pocock 版) | `tdd` — 纵向切片, 深模块, CONTEXT.md |
| 代码审查 (平行 sub-agent) | `review` (Matt Pocock) |
| 代码简化/清理 | `simplify-code` — 3 路并行 |
| 开发浏览器扩展 | `browser-extension-dev` — 纯 JS 模块化 + cat 构建 + Shadow DOM |

## 研究

| 场景 | 用 |
|------|-----|
| 搜论文 | `arxiv` — 全文检索, Semantic Scholar 引用 |
| 监控 RSS | `blogwatcher` |
| 知识库 | `llm-wiki` (Karpathy) |
| 预测市场 | `polymarket` |

## DevOps & 运维

| 场景 | 用 |
|------|-----|
| 备份 Hermes | `hermes-backup` — robocopy 增量 |
| 监控用量 | `hermes-monitoring` |
| 技能管理 | `external-skill-sources` / `external-skill-sync` |

## 生产力工具

| 场景 | 用 |
|------|-----|
| 幻灯片 | `powerpoint` — 创建/编辑 .pptx |
| PDF 编辑/OCR | `nano-pdf` / `ocr-and-documents` |
| 概念图/架构图 | `excalidraw` (手绘风) / `architecture-diagram` (暗色 SVG) |
| 信息图 | `baoyu-infographic` — 21×21 布局+风格 |
| 网页设计原型 | `sketch` (快速多方案) / `claude-design` (完整页面) |
| 邮件 | `himalaya` |
| Notion | `notion` |
| Google Workspace | `google-workspace` |

## 常见误用纠正

1. **"先写全部测试再写全部代码"** — 这是水平切片，tdd 明确禁止。正确做法：一个测试→一个实现→重复。
2. **"bug 来了直接看代码猜原因"** — diagnosing-bugs 第一阶段是建反馈循环，不是看代码。
3. **"prototype 留着以后用"** — prototype 是一次性的，答完问题就删。
4. **"grill 的时候一次问多个问题"** — grilling 要求一次只问一个，等答案。

## 描述的核心哲学概念

- **深模块（Deep Module）**：小接口 + 大实现。删除测试：删了它复杂性是集中还是扩散？
- **接缝（Seam）**：可以改行为而不改代码的地方。一个适配器 = 假设的接缝，两个 = 真实的接缝。
- **Tracer Bullet**：纵向切穿所有层（schema→API→UI→test），每片独立可交付。
- **Smart Zone**：~120K token 内模型推理仍然清晰。超出就 handoff。
- **反馈循环**：debug 的核心不是猜测，是能自动判断 bug 在/不在的命令行。

## 参考文件

- `references/skills-ecosystem-comparison.md` — 三种 skill 范式对比（自建/mattpocock/awesome-skills），含深度评价和互补关系
- `references/plugins-directory-pattern.md` — 插件目录架构模式，类型优先、工作型、按需扩展的设计决策
