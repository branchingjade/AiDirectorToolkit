# MemOS（NAS）迁移 / 共存参考（2026-08-24 实测）

> 与 Hindsight 本地嵌入共存的 NAS 记忆后端。Hermes 框架 retain 主路径**实际已写到 NAS MemOS**（不是 Hindsight 真相库）——本文件记真实端点形态、当前数据状态、迁移工作流。

## 与 Hindsight 的关系（核心事实，2026-08-24 实测）

- Hermes `config.yaml` 写 `memory.provider: memos` + `memory.providers.memos: {}`（**配置空**）
- 实际行为：框架 retain 主路径走 **memos provider 写 NAS**（已通，已有 12,214 条文本记忆）
- **Hindsight 本地嵌入（`mode: local_embedded`）还在独立写 `memories/MEMORY.md`**——与 memos 路径并行，**不冲突但双写冗余**
- 结论：**不是"memOS 没接通"，是 Hindsight 没停**——两者并存，memos 主路径已通

## ⚠️ 排查陷阱（2026-08-24 用户纠正的关键教训）

**"我用 search 搜不到 → 断言后端是空的"是错的**。本次踩坑全流程：

1. 我用 `cube_id: 'hermes-memory'` + `query: 'DSH 升级'` 调 `/product/search` → 返回 `total_nodes: 0`
2. 用 `cube_id: 'hermes-memory'` + `memory_type: 'text_mem'` 调 `/product/get_all` → 返回只有空 cube `hermes`，0 nodes
3. → 断言"NAS 是空的，没接通"
4. **用户截图前端 memos-console-web 显示 12,218 条记忆**——我被打脸
5. 重新查实际端点（前端用的是 `mem_cube_id` + `/product/get_memory_dashboard`）→ **拿到 12,214 条**

**铁律（写进 skill，跨会话生效）**：

- ❌ **不要凭单次 API 查询返回空就下"后端空/未接通"的结论**
- ✅ **从用户截图 / 实际工作端点（前端/CLI/SDK）反推真实字段名和端点**，再查
- ✅ **多端点交叉验证**：search / get_all / get_memory_dashboard / get_memory 三种不同接口各试一遍
- ✅ **字段名差异是高频坑**：`cube_id` vs `mem_cube_id` vs `cube_name`——同一后端不同端点不同字段，**看实际接口调用代码（前端源码/SDK）再传参**

## MemOS API 真实形态（Krolik Extended v2.0.3，NAS @ 192.168.1.2:8001）

### 端点（从前端 `memos-console-web` 源码实测）

| 端点 | 方法 | 用途 | 关键字段 |
|---|---|---|---|
| `/product/search` | POST | 语义搜索 | `query`, `mem_cube_id`, `user_id`, `top_k` |
| `/product/get_memory_dashboard` | POST | 统计概览 | `mem_cube_id`, `page`, `page_size` |
| `/product/get_memory` | POST | 列记忆 | `mem_cube_id`, `page`, `page_size` |
| `/product/get_memory/{id}` | GET | 单条详情 | URL param |
| `/product/add` | POST | 写入（async 默认） | `user_id`, `messages`, `mem_cube_id`, `custom_tags`, `info` |
| `/product/get_all` | POST | 全量（**要求 `memory_type`**） | `user_id`, `cube_id`, **`memory_type`** |
| `/product/exist_mem_cube_id` | POST | cube 存在性 | `user_id`, `mem_cube_id` |
| `/product/scheduler/allstatus` | GET | 任务队列状态 | — |
| `/openapi.json` | GET | 完整 API 文档 | — |

### 字段名差异（关键！）

| 我以为的 | 实际用的 | 端点 |
|---|---|---|
| `cube_id` | **`mem_cube_id`** | search / get_memory_dashboard / get_memory |
| `cube_id` | `cube_id` | get_all / exist_mem_cube_id（混用） |
| `search_query` | **`query`** | search |
| — | `user_id` | 全端点 |
| — | `memory_type` | get_all（必填：`text_mem`/`act_mem`/`para_mem`/`pref_mem`/`tool_mem`/`skill_mem`） |
| — | `custom_tags` | add（搜索过滤） |
| — | `info` | add（metadata 任意 KV，可作 filter） |

### auth

- Bearer token：`Authorization: Bearer <MEMOS_API_KEY>`
- 本机 `krlk_2809...` key 已配（`C:/Users/HMSJ/AppData/Local/hermes/.env` 的 `MEMOS_API_KEY`）
- key 不通过控制台（前端 cookie 登录 = `memos-console-web` 代理层独立鉴权，与 API key 无关）

### 当前数据状态（2026-08-24 实测）

| memory_type | 节点数 | 来源 |
|---|---|---|
| `text_mem` | **12,214** | DSH damage-pulse cron + 今日对话 retain + 历史积累 |
| `tool_mem` | 1 | — |
| `pref_mem` | 0 | — |
| `skill_mem` | 0 | — |
| `act_mem` | cube 不存在 | — |
| `para_mem` | cube 不存在 | — |

**cube `hermes-memory` 已存在且有数据**（`.env` 的 `MEMOS_CUBE_ID=hermes-memory` 已生效）。**MEMORY.md 的 69 条本地铁律没在 NAS 搜到**——是 Hindsight 本地嵌入独写的内容。

## 迁移工作流（Hindsight 本地 → MemOS NAS）

### 流程（1 条 → 一条 text_mem）

```python
import json, urllib.request

api_key = 'krlk_2809ffc7d34aa1156e68babd87aa264d903fb167b2e3c5b3daebe441cd5a84ca'
hdr = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}

# 每条本地铁律 → 一条 user message
entry = "DSH 升级流程铁律（2026-08-24 rc.8→rc.2）..."
payload = {
    'user_id': 'hermes',
    'mem_cube_id': 'hermes-memory',
    'messages': [{'role': 'user', 'content': entry}],
    'custom_tags': ['hermes-bootstrap', 'memories-archive-2026-08-24'],
    'info': {'source': 'local-memories-md', 'migrated_at': '2026-08-24'},
    'async_mode': 'async',  # 默认异步，不阻塞
}
req = urllib.request.Request('http://192.168.1.2:8001/product/add',
    data=json.dumps(payload).encode(), method='POST', headers=hdr)
with urllib.request.urlopen(req, timeout=20) as r:
    print(r.read().decode()[:300])
```

### 验证召回（必做，2026-08-24 用户纠正的核心）

```python
# 1. 试 search 召回——5 个不同关键词
for kw in ['DSH 升级', 'Eagle', '妖玉影视', '创作类 skill 强制门禁', 'GEM']:
    payload = {
        'query': kw,
        'mem_cube_id': 'hermes-memory',
        'user_id': 'hermes',
        'top_k': 3,
    }
    req = urllib.request.Request('http://192.168.1.2:8001/product/search',
        data=json.dumps(payload).encode(), method='POST', headers=hdr)
    with urllib.request.urlopen(req, timeout=15) as r:
        body = json.loads(r.read())
    d = body.get('data', {})
    text_mems = d.get('text_mem', [])
    n = sum(it.get('total_nodes', 0) or 0 for it in text_mems)
    print(f'  "{kw}" → 命中 {n}')

# 2. 端点总览核验
payload = {'mem_cube_id': 'hermes-memory', 'page': 1, 'page_size': 1}
req = urllib.request.Request('http://192.168.1.2:8001/product/get_memory_dashboard',
    data=json.dumps(payload).encode(), method='POST', headers=hdr)
with urllib.request.urlopen(req, timeout=15) as r:
    d = json.loads(r.read())['data']
print(f"text_mem nodes: {d.get('statistics',{}).get('total_text_nodes')}")
```

### 灌数据后停 Hindsight（顺序）

1. **写脚本**：循环 69 条 `add_memory`（带重试 3 次 + 失败日志到 `migration-failures.json`）
2. **抽样验证**：灌完 5 条先 search 召回 + dashboard 计数 → 通过再全量
3. **全量灌**：异步写入（`async_mode: 'async'`），不阻塞
4. **dashboard 计数对比**：灌前 ~12214 → 灌后 ~12283（+69 文本）
5. **改 `hindsight/config.json`**：`auto_retain: false`、`auto_recall: false`（**保留配置不删**，仅停行为）
6. **备份本地**：`memories/MEMORY.md` → `memories/.archive/2026-08-24-pre-memos/MEMORY.md`（时间戳存档）
7. **本地软化**：`memories/MEMORY.md` 改名为 `.archive/MEMORY.md.archive`，留空文件 `MEMORY.md` 指向 archive（防框架找不到崩溃）
8. **改 `config.yaml`** 补 `providers.memos` 配置（当前 `{}` 空，未来切回纯 memos 时需要）
9. **改 `.env`**：`MEMOS_API_URL=http://hmsj.local:8001` → `http://192.168.1.2:8001`（IP 直连，避开 mDNS）
10. **重启 gateway**（杀 `gateway run` PID → Start-ScheduledTask Hermes_Gateway）
11. **端到端验证**：新会话写一条 → search 能查到

### 失败兜底

- 单条 `add` 失败重试 3 次（指数退避）→ 第 3 次仍败则跳过 + 记录 uuid 失败的条目到 `migration-failures.json`
- 全量失败回滚：Hindsight 不动、config 不改，本地 `MEMORY.md` 仍在
- dashboard 计数对比兜底（灌前/灌后差值 ≠ 灌入条数 → 有丢失，重灌失败条）

## 排障入口速查（不要再走弯路）

| 现象 | 实际原因 | 正确做法 |
|---|---|---|
| `search` 返回空 | 字段名错（`cube_id` 应是 `mem_cube_id`）| 查前端源码 / openapi.json |
| `get_all` 返回只有空 cube `hermes` | 字段名错 + 漏必填 `memory_type` | 换 `get_memory_dashboard` |
| `get_memory_dashboard` 422 | 漏 `mem_cube_id` 或 `page` | openapi.json 看必填 |
| 422 `Parameter validation error on ...` | 必填字段缺失 | 调 openapi.json 看 schema |
| scheduler 全 0 | 没有积压任务（正常） | 不必查 |
| `add` 异步任务丢 | scheduler 失败但入口未报 | 查 `scheduler/allstatus` + 失败条记 |
| cube `hermes` 空但 `hermes-memory` 有 | 默认 cube 名字差异 | 用 `.env` 的 `MEMOS_CUBE_ID` 实际值 |

## 前端真源（`memos-console-web`）

| 项 | 值 |
|---|---|
| 端口 | **8090**（本机 dev server）|
| 进程 | `memos-console-web/server/src/index.ts`（tsx watch，PID 55328/59908） |
| 真实后端 | 转发到 `MEMOS_BASE=http://hmsj.local:8001` |
| 鉴权 | `ACCESS_PASSWORD` 环境变量 → cookie 签名（HS256）|
| 端点白名单 | `isAllowedEndpoint()`（在 `dsh-memos-console/src/memos.ts`）|
| 数据流向 | 浏览器 → 8090 鉴权 → 注入 `mem_cube_id` + `user_id` 默认值 → 8001 |

**关键：memos-console-web 的 `dsh-memos-console/src/memos.ts` 是缺失文件**（import 路径存在但 fs 上没有），但 tsx watch 模式下 server 仍能跑——意味着代理功能可能 fallback 到默认行为或部分端点失效。**登 8090 看是数据真源最直接方式**。

## 写进本 skill 的核心教训

1. **API 字段名要看实际调用代码，不要猜**（`cube_id` vs `mem_cube_id` 是教训典型）
2. **多端点交叉验证**：dashboard / search / get_memory / get_all 各端点的字段组合不同，**任一返回空都先换端点再下结论**
3. **用户截图 = 真源**：当用户给截图证明数据存在时，**别用自己的单次失败查询反证用户错**——错的几乎总是自己
4. **Hindsight 与 memos 可共存**：停 Hindsight 不是因为 memos 失败，而是因为冗余写浪费 token；保留 Hindsight 配置以便回退