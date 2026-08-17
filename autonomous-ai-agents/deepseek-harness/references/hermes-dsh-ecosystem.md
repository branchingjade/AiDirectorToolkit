# Hermes ↔ DSH 生态调研（2026-08-17 实证）

> 调研方法：`gh search repos` / GitHub API readme 端点 + 深读两个核心项目全部源码（见 codebase-inspection「深读评估流程」）。star 与更新日期为调研当日数据，使用前可再核对。

## 生态索引（找 DSH 项目先查这几个）

- `0xsline/awesome-deepseek-harness`（606★）— DSH 生态精选清单，含官方插件 hub（dsh-external）条目
- `awesome-dsh-plugin/awesome-dsh-plugin`（5227★）— DSH 插件精选列表
- `bruc3van/awesome-dsh-plugin`（178★）— 脚本每天自动抓取全部 dsh-plugin 标签仓库 + 人工核实
- `dsh-market/dsh-market`（577★）— DSH 可视化插件市场
- `deepseek-ai/deepseek-harness`（13.2万★）— 官方本体（README 里的 `.agents/skills` 是官方 skill 写法范本）

## Hermes↔DSH 直接联动（3 个）

### 1. Cavan-Ou/hermes-dsh-collab（5★，v0.3.0，2026-08-16 活跃）— 流程规范层
- **本质：纯提示词 skill 包，零功能代码**（553 行仓库 ≈ 500 行 markdown + 23 行 index.mjs 注册 skill provider）
- 内容：Hermes 主控/DSH 执行者的协作规范——spec 三铁律、模型分层路由（Flash/Pro/qwen）、质量门「不信自报」、git 唯一写者、写回靠启动目录；10 条踩坑全带「症状→根因→对策」
- 来源：style-museum 管线 14 天 30 commits 实战提炼（REPORT.md 有完整决策记录 + 三项加载自测）
- **硬伤**：①真源路径是作者 WSL 绝对路径（`/mnt/d/...`），换机器必改；②README 推荐 bundle 安装但 SKILL.md 明确「不要 bundle 装纯提示词 skill」——文档自相矛盾；③skills/ 与 .agents/skills/ 双副本漂移风险
- 安装：`cp -r skills/hermes-dsh-collab $DSH_HOME/skills/`

### 2. chushixixin/dsh-harness-mcp-server（5★，npm `@chushixixin/dsh-harness-mcp-server`，2026-08-15）— 技术桥接层
- **本质：DSH 内部起 MCP server（StreamableHTTP :8090），Hermes 经 MCP 直接驱动 DSH agent**（brain=Hermes, arms=Harness）
- 774 行 TS：echo / harness_list_tools / agent_run（同步）/ task_inbox+task_result（异步队列）/ attach_session / rename_session
- 设计亮点：会话按 cwd 复用（LRU 8，省 15-20 倍上下文）、三级续接（进程池→live→持久化 resume）、realpath 规范化 cwd、同 cwd 串行锁、结构化结果解析（从后往前找 JSON summary，中英文键都认）、Bearer token + workspaceRoots 白名单、对 dsh rc.6 unscoped-context bug 检测降级、12 项 smoke test
- **硬伤**：安装重（进 pnpm workspace 构建或 npm）；bash 沙箱要 bubblewrap（Linux）；任务队列在进程内存重启即丢；无 CI/无社区验证；依赖 DSH 内部 API 有 breaking 风险
- Hermes 侧配置：`printf 'n\nY\n' | hermes mcp add harness_plugin --url http://127.0.0.1:8090/mcp`

### 3. Nwflower/dsh-chat-import（47★，最热，2026-08-16 活跃）— 数据迁移层
- 14+ agent 会话历史导入 DSH 续聊（Claude Code/Codex/ChatGPT/Gemini/opencode/**Hermes**/Kimi 等），全保真、可逆导出/同步、bundle 备份

## 迁移/移植类（类似方向）

- `PerryLink/dsh-claude-move`（6★）— 四源迁移向导：把 Claude Code/Codex/OpenCode/**Hermes** 的会话+记忆+skills+指令迁入 DSH（/move，可断点续传、幂等）
- `Letter2025/dsh-tool-search`（4★）— 把 Hermes 的渐进式工具披露（tool_search/describe）移植到 DSH（topic 标 hermes）

## 风格对标类

- `youngiry/dsh-discord-gateway`（0★）— "Hermes-grade" DSH Discord 网关（对标 Hermes 渠道网关）
- `crafter-station/petdex`（3855★）— 宠物画廊，Hermes + DSH 双平台（Hermes 侧已有 petdex skill）

## 评估结论（2026-08-17 交付用户）

- 两个核心项目**互补不互斥**：mcp-server 解决「怎么接线」（程序级），collab 解决「怎么派活验收」（流程级）；真用 DSH 当执行手两者一起上
- 均 5★ 小项目，胜在实战提炼与设计质量，输在社区验证少；不建议直接上生产管线，先跑一轮小任务验证链路
- collab 的「记忆回路」设计（Hermes 记忆→context→任务→changes/verification 回写）与用户记忆架构思路吻合
