# OpenViking 公有库 `viking://resources/` 工作流 (2026-08-28 实测)

## 命名空间区分

OpenViking 用 `viking://` URI 协议管理三块内容, **scope 不同鉴权不共享**:

| 命名空间 | 范围 | 典型用途 |
|---|---|---|
| `viking://user/<account>/` | **私有**(绑定账户) | 长期记忆 / preferences / identity.md / soul.md |
| `viking://user/<account>/peers/` | 私有 + 跨 agent | peer-scoped 记忆 (peer_id 隔离) |
| `viking://resources/` | **公开/账户级共享** | 团队/项目共享知识库(同账户所有 agent 共享, **非真公网公开**) |
| `viking://skills/` | 系统/用户 skills | agent 调用的能力 |

## `viking://resources/` 公开库实际工作流

**用户语义**: 「OpenViking 怎么用做公用库」= 在 `viking://resources/` 范围维护共享知识库, 其他 user 的 agent 通过 find/query 共享访问(同账户内)。

### 1. 灌资源 (异步)

```python
await call_tool("add_resource", {
    "path": "https://github.com/<owner>/<repo>/blob/<branch>/README.md",  # 远程 URL
    # 或本地路径: "/Users/me/notes.md"
    "to": "viking://resources/<topic>/",  # 落到哪个公开子目录
})
# 返回: "Resource added: viking://resources/<topic>"
# 异步: 后台 LLM 拆分 + 摘要, 30-60s 完成, 立即 find 抓不到
```

**OpenViking 后台 LLM 自动拆分**: 1 个长 README 会被拆成 N 个 markdown 子文件 + 每个 `.abstract.md` + 每个 `.overview.md`。例如 1 个官方 introduction 文档拆出:
- `Introduction/Introduction_introduction/Core_Features_core-features.md`
- `Introduction/Introduction_introduction/Introduction_intr_2more_<hash>.md`
- 多个 `.abstract.md` (中文摘要, ~100 token)

### 2. 检索资源库

```python
# 限定 resources 范围 (不掺 user 私有记忆)
r = await call_tool("find", {
    "query": "OpenViking API key 配置",
    "target_uri": "viking://resources/",  # 关键: 限定 scope
    "limit": 5,
    "min_score": 0.35,  # 默认太严, 中文 query 经常 No match, 降到 0.2 试试
})

# 不传 target_uri = 全局搜 (user + resources + skills 全部)
r = await call_tool("find", {"query": "OpenViking", "limit": 5})
```

### 3. 分层读取 (L0/L1/L2)

```python
# L0 abstract: ~100 token, 适合注入 prompt
r = await call_tool("read", {
    "uris": ["viking://resources/<topic>/<file>.md"],
    "level": "abstract"  # 默认
})

# L1 overview: ~2k token, 拿概要
r = await call_tool("read", {
    "uris": ["viking://resources/<topic>/<file>.md"],
    "level": "overview"
})

# L2 full: 全文, token 大慎用
r = await call_tool("read", {
    "uris": ["viking://resources/<topic>/<file>.md"],
    "level": "full"
})
```

## 跟私有库的差异

| 维度 | `viking://user/default/` 私有 | `viking://resources/` 公开 |
|---|---|---|
| 谁能读 | 仅此账户 | 同账户内所有 agent / user |
| 谁能写 | 此账户 | 此账户 |
| find 默认包含 | ✓ | ✓ |
| 跨账户 | ✗ | ✗ (账户级共享, 非真公网) |
| 真公网公开 | — | ✗ (需要走 OpenViking Studio 或自部署) |

## 公开库 ≠ 真公网 — 跨账户限制

**踩坑警告**: `viking://resources/` 是 **账户级共享**, 不是真公网公开。其他 OpenViking 账户的用户看不到你的 resources。要做真公网公开, 你需要:

1. **自部署 OpenViking server** + 配置 dev/auth_mode + 暴露公网 — 但 AGPL-3.0 商用雷区 (改后对外网络服务须整体开源回吐)
2. **OpenViking Studio** (官方 playground) — 适合 demo / 分享特定资源
3. **导出静态文档** (HTML/PDF) 放到公网 — 失去 L0/L1 检索能力

## 实测: `viking://resources/openviking-docs/` 当前内容

2026-08-28 实测灌的官方文档, OpenViking LLM 自动拆分成:
- `openviking-docs/introduction/Introduction/Introduction_introduction/` — Core_Features + Introduction_intr_2more
- `openviking-docs/api-reference/API_Overview/API_Endpoints/` — Administration/Privacy + Lifecycle
- `openviking-docs/api-reference/API_Overview/Connection_Modes/Client-Server_Mode/` — SDK/CLI 示例
- `openviking-docs/auth/Authentication/Authentication_authentication/` — 8 个独立子文档:
  - Quick_Start_API_Key_Mode (推荐)
  - Dev_Mode, LDAP_Authentication, OIDC_Authentication
  - Trusted_Mode, Custom_Authentication_Plugins, CLI_LDAP_Configuration

## 跟 MEMORY.md 工作流对比 (决策点)

| 场景 | 用 MEMORY.md (本地) | 用 `viking://resources/` 公开库 |
|---|---|---|
| 单 agent 私有长期记忆 | ✓ (本地, 立即生效) | ✗ (私有用 `viking://user/`) |
| 跨 agent 共享 (同账户) | ✗ | ✓ |
| 团队/项目知识库 | ✗ | ✓ (account 级共享) |
| 真公网公开 | 静态发布 | ✗ (需自部署, AGPL 风险) |
| L0/L1/L2 自动分层 | ✗ (手写) | ✓ (后台 LLM 自动) |
| 主题自动拆分 | ✗ (手维护) | ✓ (memory extraction) |

**结论**: 用 `viking://resources/` 当**账户内团队共享知识库**是 OpenViking 的真正卖点。私有记忆 (`viking://user/`) 跟 MEMORY.md 重复, 看场景选一个; 真公网公开需要自部署或静态导出。