---
name: deepseek-harness
description: Use when 让 DeepSeek Harness (DSH) 执行编码任务或评估 Hermes↔DSH 联动。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [dsh, deepseek-harness, multi-agent, delegation, cordis]
    related_skills: [opencode, claude-code, codex, codebase-inspection]
---

# DeepSeek Harness (DSH) 集成

DSH = DeepSeek Harness（官方 `deepseek-ai/deepseek-harness`，13.2万★，定位 "Everything is a Plugin"）。Cordis 应用，自带 agent 运行时（tools/llm/agents/sessions/presets）+ 插件生态（dsh-plugin 标签、插件市场 dsh-market）。可作 Hermes 的外部执行臂：Hermes 当大脑（上下文/记忆/验收），DSH 当胳膊（flash 档实际干活）。

## 何时用

- 大重构/长提炼（如读几十份文档）会撑爆 Hermes 上下文 → 甩给 DSH headless 干
- 多个互不相干任务并行执行
- 用户提到 DSH/DeepSeek Harness 集成、插件、生态时

## 联动方式（从轻到重）

1. **CLI 直驱（零安装）**：`cd <项目根> && dsh --profile headless "任务"`。
   - **写回靠启动目录**：workspace-write 沙箱写白名单 = 启动 cwd + 平台临时根。不在项目根启动 → 产物落在 /tmp 写不回。
   - 最轻、最快验证链路的方式；配合 skill 包纪律用（见 3）。
2. **MCP 桥**（`chushixixin/dsh-harness-mcp-server`）：在 DSH 内部起 MCP server（StreamableHTTP，默认 127.0.0.1:8090），Hermes 侧 `hermes mcp add harness_plugin --url http://127.0.0.1:8090/mcp` 后即可 `agent_run`/`task_inbox` 直接驱动。
   - 优点：会话按 cwd 复用（省 15-20 倍上下文加载）、三级续接（池→live→持久化 resume）、结构化结果（changes/verification/leftovers）可写回 Hermes 记忆。
   - 代价：安装重（要进 DSH 的 pnpm workspace 构建或 npm 装）；bash 沙箱依赖 bubblewrap（Linux）；异步队列在进程内存、重启即丢。
3. **Skill 包**（`Cavan-Ou/hermes-dsh-collab`）：纯提示词协作规范（spec 三铁律/模型分层/质量门/git 唯一写者），复制进 `$DSH_HOME/skills/` 即装（skill-filesystem 扫 `<skills root>/<name>/SKILL.md`，热加载）。

## 协作纪律（Hermes 主控 / DSH 执行者）

- **git 唯一写者 = Hermes**：派单任务书必须显式写「不 commit」——历史观测：不写时 DSH 会自己 commit。
- **spec 三铁律缺一不派单**：Plan 先行（先出改动清单）· 测试先行（TDD 红→绿，没先红过的绿不可信）· 范围声明（只准改列出的文件，禁止清单同等重要）。
- **质量门归主控，不信自报**：四步独立验证——测试全绿 → build → `git diff` 对照范围声明 → 浏览器走查。dsh 的「全绿」只当线索。
- **模型分层路由**（按阶段复杂度不按心情）：Flash-max 常规（默认）/ Pro 复杂（多文件重构/长提炼/跨层调试）/ qwen 视觉（看设计稿截图）。拿不准先 Flash 试跑，**返工才升级**（不是失败才升级）。
- **回炉 = 新任务书重派**：headless 无 resume（每次调用随机 session UUID），失败原因写进新任务书。

## 已知踩坑（速览；详情与来源见 references/dsh-pitfalls.md）

- `--patch` 是**整段替换非深合并**——providers 必须写完整定义，只写局部字段报 `Provider is not configured`
- qwen3.7-plus 不支持 `reasoning: max`；vision patch 不改主模型，只声明 `input: [text, image]` 让 read_image 自动路由
- 旧后端进程残留 → 「测试全绿」验到旧代码（主控用 terminal(background=true) 管进程，不用 nohup）
- bash 沙箱要 bubblewrap（Linux 工具），Windows 上要么 WSL 要么绕沙箱
- DSH 插件安装：`dsh plugin --profile X add <pkg>` 走 pnpm 转发（pnpm 要在 PATH）；纯提示词 skill 用目录复制，别走 bundle

## 生态索引

Hermes↔DSH 桥接项目清单与深读评估结论见 `references/hermes-dsh-ecosystem.md`（dsh-chat-import / dsh-claude-move / dsh-tool-search 等 6 个 + 生态索引仓库）。评估新项目时按 codebase-inspection 的「深读评估流程」走。

## 注意事项

- 上表的踩坑提炼自 hermes-dsh-collab 作者的实测管线（style-museum，14 天 30 commits）与项目文档，**非本机实测**——本机使用前先跑小任务验证。
- 两个 5★ 小项目社区验证少、DSH 内部 API 耦合紧（已见 rc.6 workaround），升级 DSH 有 breaking 风险。
