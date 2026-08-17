# Hermes↔DSH 联动项目清单与评估结论（2026-08-17 深读评估）

DSH = DeepSeek Harness（官方 `deepseek-ai/deepseek-harness`，13.2万 star，"Everything is a Plugin"）。
用户本机 DSH 已装并跑 web UI :8080，具备全部实测条件。

## 直接联动（Hermes 管线里跑 DSH）

| 项目 | Star/活跃 | 做什么 | 评估结论 |
|---|---|---|---|
| Cavan-Ou/hermes-dsh-collab | 5★ / 活跃 | 把 DSH 挂进 Hermes 多 agent 管线：模型分层路由、spec 三铁律、质量门、git 唯一写者，打包成 SKILL.md | **纯提示词 skill 包**（553 行，唯一代码是 23 行 index.mjs 注册 provider）。内容质量高（14 天真实管线 30 commits 提炼，踩坑全实证：patch 整段替换语义/qwen 不支持 reasoning:max/vision patch 不改主模型/旧进程假绿/headless 无 resume）。硬伤：真源路径是作者 WSL 绝对路径（/mnt/d/... 需改）；README 与 SKILL.md 对 bundle 安装自相矛盾；两份副本漂移风险 |
| chushixixin/dsh-harness-mcp-server | 5★ / 活跃 | DSH 内部起 MCP server（StreamableHTTP :8090），Hermes 通过 MCP 驱动 DSH（brain=Hermes, arms=Harness） | **真程序级桥**，774 行 TS 质量扎实：会话按 cwd 复用（LRU 8，省 15-20 倍上下文）、三级续接（进程池→live→持久化 resume）、realpath 规范化 cwd、同 cwd 串行锁、结构化结果解析（中英文键）、Bearer token + workspaceRoots 白名单。硬伤：安装链路重（需进 DSH pnpm workspace 构建）；bash 沙箱依赖 bubblewrap（Linux，Windows 受限）；任务队列在进程内存（重启即丢）；仅 dev smoke test 无 CI/release |
| Nwflower/dsh-chat-import | 47★（最热） | 14+ agent 会话历史导入 DSH 续聊（Hermes 是来源之一），全保真可逆 | 数据层联动，最成熟 |

## 迁移/移植类

- PerryLink/dsh-claude-move（6★）—— Hermes 会话/记忆/skills/指令整体迁入 DSH 的向导
- Letter2025/dsh-tool-search（4★）—— 把 Hermes 渐进式工具披露移植到 DSH（topic 标 hermes）

## 风格对标类

- youngiry/dsh-discord-gateway —— "Hermes-grade" DSH Discord 网关
- crafter-station/petdex（3855★）—— 宠物画廊，Hermes+DSH 双平台

## 参考索引

- 0xsline/awesome-deepseek-harness（606★）—— DSH 生态精选清单（Hermes 相关条目即上文所列）
- dsh-external/* —— 官方插件 hub 组织

## 用户场景建议（已给出）

- 两者互补：mcp-server 解决「Hermes 通过 MCP 驱动 DSH agent、结果结构化回传」，collab 解决「任务怎么写、怎么验收」——一起上才是完整方案
- 都是 5★ 小项目，社区验证少；先跑一轮小任务验证链路再上生产管线
- 写 DSH 任务书注意：DSH 的 shell 是 pwsh 不是 bash（与 Hermes git-bash 终端不同）
