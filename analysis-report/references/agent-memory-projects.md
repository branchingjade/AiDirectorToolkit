# Agent 记忆项目横向对比（2026-08-11 案例存档）

用户 @url 扔来 TencentCloud/TencentDB-Agent-Memory 说「对比下个项目」，纠正为「对比同类项目」。本文件是该案例的数据与结论存档，也是「GitHub 同类对标」的产出模板示例。

## 元数据（GitHub API 实时抓取，2026-08-11）

| 项目 | ⭐ | 语言 | 创建 | 活跃 | 许可 |
|---|---|---|---|---|---|
| mem0ai/mem0 | 62,961 | Python | 2023-06 | 2026-08 | Apache-2.0 |
| letta-ai/letta (原 MemGPT) | 24,180 | Python | 2023-10 | 2026-08 | Apache-2.0 |
| vectorize-io/hindsight | 19,501 | Python | 2025-10 | 2026-08 | MIT |
| TencentCloud/TencentDB-Agent-Memory | 19,449 | TypeScript | 2026-04 | 2026-08 | MIT |
| getzep/zep | 4,823 | Python | 2023-04 | 2026-08 | Apache-2.0 |

## 定位一句话

- **TencentDB-Agent-Memory**：团队级记忆中心（Memory Hub）——对话/文档/代码转成四类记忆资产（Chat Memory / Skill / Wiki / CodeGraph），团队共享 + ACL + 按 Agent 装备。三服务一键部署（memory-core + hub + proxy），面板 :8125
- **Hindsight**（用户正在用，Hermes memory.provider=hindsight）：Agent 记忆自动 retain/recall，语义检索 + 实体图谱，L0→L3 分层蒸馏。单人单 bank，无用户隔离
- **Mem0**：通用记忆层（Universal memory layer），提取-检索范式，事实存向量库，最流行的单 Agent 长期记忆
- **Letta**：有状态 Agent 平台，记忆 = Agent 自身状态，可自编辑、自我改进
- **Zep**：时序知识图谱（temporal knowledge graph），图 + 时间双维

## 关键洞察

- TencentDB 差异化在「协作层」（团队共享/ACL/按角色装配/资产生命周期），不在「存储层」（也是 BM25+向量+RRF 成熟组合）——存储层 Mem0/Letta/Zep/Hindsight 各有所长
- 它原生支持 Hermes（README 徽章列了 Hermes Gateway），Skill 管理部分直接引用了 Hermes Agent 代码（README Acknowledgements 区）
- 检索设计：L2/L3 快速引导 + L1/L0 精确回退（BM25+向量+RRF），按需调用工具不整段注入；基准 PersonaMem 48%→76% (+59%)

## 对用户（Hermes 用户）的参考价值

| 用户现状 | TencentDB 对应物 | 可借鉴度 |
|---|---|---|
| Hermes MEMORY.md + USER.md | Chat Memory L0-L3 分层蒸馏 | 思路可借鉴 |
| Hindsight 记忆插件 | 同为 Agent 记忆，多了团队/权限层 | 互补 |
| 妖玉影视知识库（skills/_知识库 references/） | Wiki + Skill 资产（链接图/版本/装备） | 形态相似，缺版本/权限管理 |
| 飞书多用户协作（画像/路由/评论会话） | Team Memory Hub（建队/ACL/按角色分配） | 最相关借鉴点 |
| 代码影响面分析 | CodeGraph（符号/调用关系/影响路径） | 新概念可研究 |

## 技术坑记录

- **默认分支 ≠ main**：TencentDB-Agent-Memory 默认分支 `feat/server_team`，raw.githubusercontent main 抓 404。必须先查 API 的 `default_branch` 字段
- **`/tmp` 在 MSYS 下不可写**：curl -o /tmp/xxx.md 报 No such file，要写工作目录（如 Documents/Hermes/）
- **GitHub API readme 端点 + Accept raw header 失败**（返回空），改用 raw.githubusercontent.com + 正确分支直接抓
- **web_extract 不可用于 GitHub 页面**：ddgs 后端只支持搜索，extract 报错「search-only backend」——GitHub 内容一律走 raw.githubusercontent + API
- **open_preview 是 deferred tool**：需 tool_search → tool_describe → tool_call 三步加载；接受本地 HTML 文件路径，在右侧预览窗渲染
