# Hermes 完整技能生态

> 本文件由 2026-06-25 会话编译，供 `mattpocock-skills-navigator` 引用。

## 影视/AI 创作相关（与用户主领域直接相关）

| 技能 | 类别 | 用途 | 何时用 |
|------|------|------|--------|
| `comfyui` | creative | SD/Flux/Wan 图像视频生成，Comfy Cloud 或本地 | 生图、视频生成、ControlNet |
| `touchdesigner-mcp` | creative | MCP 直接控制 TouchDesigner，36 个工具 | 实时视觉、音频反应、GLSL |
| `manim-video` | creative | 3Blue1Brown 风格数学/算法动画 | 教育视频、概念可视化 |
| `songwriting-and-ai-music` | creative | Suno AI 音乐生成，歌词+结构+提示词工程 | AI 音乐、配乐 |
| `heartmula` | media | 开源本地音乐生成（Suno 替代） | 离线音乐生成 |
| `humanizer` | creative | 29 种 AI 写作模式检测+重写 | 去 AI 味文章 |
| `ascii-video` | creative | 视频转 ASCII 艺术 | 风格化视觉输出 |
| `p5js` | creative | 创意编程/生成艺术 | 交互式视觉原型 |
| `sketch` | creative | 快速 HTML 多方案 UI 对比 | UI 原型 |
| `claude-design` | creative | 完整 HTML 页面设计 | Landing page/演示 |

## 自动化编程代理

| 技能 | 用途 | 模式 |
|------|------|------|
| `claude-code` | Claude Code CLI — print 模式一行任务，tmux 交互式 | 委托编程 |
| `codex` | OpenAI Codex CLI | 委托编程 |
| `opencode` | OpenCode CLI | PR 审查 |

## Matt Pocock 工程方法论（完整 30 技能，5 类）

### 工程主线 (15)
| 技能 | 阶段 | 核心思想 |
|------|------|----------|
| `ask-matt` | 🧭 路由器 | 根据情境推荐技能 |
| `setup-matt-pocock-skills` | ⚙️ 初始化 | issue tracker + labels + domain docs |
| `grill-with-docs` | 💬 需求 | 追问+写 CONTEXT.md + ADR |
| `grill-me` | 💬 需求（无代码库） | 追问，无状态 |
| `domain-modeling` | 📖 建模 | 术语表、ADR、消除模糊 |
| `codebase-design` | 🧱 架构词汇 | 深模块/接口/接缝 |
| `to-prd` | 📝 文档 | 对话→PRD |
| `to-issues` | 🔢 拆分 | tracer bullet 纵向切片 |
| `implement` | 🔨 执行 | 按 issue 实现，用 TDD |
| `tdd` | 🟢🔴 测试 | 纵向切片 RED-GREEN-REFACTOR |
| `triage` | 🏷️ 分诊 | Issue 状态机 |
| `diagnosing-bugs` | 🐛 调试 | 6 阶段，反馈循环优先 |
| `improve-codebase-architecture` | 🏗️ 优化 | 扫描→HTML→深度化 |
| `prototype` | 🧪 原型 | 一次性代码，答完即删 |
| `review` | ✅ 审查 | Standards + Spec 双轴并行 |
| `resolving-merge-conflicts` | 🔀 合并 | 理解双方意图→解决 |

### 实验性 (4)
`decision-mapping` — 决策地图 | `writing-beats` — beat 写作 | `writing-fragments` — 碎片挖掘 | `writing-shape` — 素材塑形

### 生产力 (5)
`grilling` — 追问引擎 | `handoff` — 跨 session | `teach` — 教学引擎 | `writing-great-skills` — Skill 方法论 | `grill-me` — 快速追问

### 杂项 (4)
`git-guardrails-claude-code` | `migrate-to-shoehorn` | `scaffold-exercises` | `setup-pre-commit`

### 个人 (2)
`edit-article` | `obsidian-vault`

## 软件工程

| 技能 | 用途 |
|------|------|
| `plan` | 实现计划，写到 `.hermes/plans/` |
| `spike` | 快速验证可行性，一次性 |
| `systematic-debugging` | 4 阶段系统化调试 |
| `test-driven-development` | 标准 TDD |
| `simplify-code` | 3 路并行代码清理 |
| `requesting-code-review` | 预提交审查 |

## DevOps/运维

| 技能 | 用途 |
|------|------|
| `hermes-backup` | robocopy 增量备份到坚果云 |
| `hermes-monitoring` | token 用量监控 |
| `external-skill-sources` | 外部 GitHub skill 源管理 |
| `external-skill-sync` | 外部 skill 同步 |

## 研究

| 技能 | 用途 |
|------|------|
| `arxiv` | arXiv + Semantic Scholar 论文检索 |
| `blogwatcher` | RSS 监控 |
| `llm-wiki` | Karpathy LLM 知识库 |
| `polymarket` | 预测市场查询 |

## 效率工具

| 技能 | 用途 |
|------|------|
| `powerpoint` | 创建/编辑 .pptx |
| `nano-pdf` | PDF 编辑 |
| `ocr-and-documents` | PDF/扫描 OCR |
| `excalidraw` | 手绘风图表 |
| `architecture-diagram` | 暗色 SVG 架构图 |
| `baoyu-infographic` | 信息图 |
| `notion` | Notion API |
| `google-workspace` | Gmail/Calendar/Drive |
| `himalaya` | 终端邮件 |
| `obsidian` | Obsidian 笔记 |

## 触发词速查

| 用户说 | → 加载 |
|--------|--------|
| "追问"/"grill"/"打磨想法" | `grilling` |
| "写计划"/"先规划" | `plan` |
| "快速验证"/"试一下能不能" | `spike` |
| "修 bug"/"查原因" | `systematic-debugging` 或 `diagnosing-bugs` |
| "备份" | `hermes-backup` |
| "生成图片"/"AI 绘图" | `comfyui` |
| "AI 音乐"/"写歌" | `songwriting-and-ai-music` |
| "做动画"/"3B1B 风格" | `manim-video` |
| "去 AI 味"/"人味化" | `humanizer` |
| "搜论文" | `arxiv` |
| "代码审查" | `review` |
| "拆分任务" | `to-issues` |
