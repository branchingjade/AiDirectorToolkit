# OpenViking MCP 真链路验证 + 工具 schema (2026-08-28)

## MCP 通道是云服务 OpenViking 的实际可行路径

**结论先放**：用户「用 OpenViking」类需求在云服务 (Volcengine) 模式下，**不要碰内置 `memory.provider`**，直接走 MCP server `ov-mcp-server`（HTTP transport 接 `https://api.vikingdb.cn-beijing.volces.com/openviking/mcp`，Bearer 用 base64 `account.user.credential`）。

**为什么**：内置 provider 走 `/api/v1/*` REST，要火山 IAM 签名（AK + SK 双段），user-management 那串鉴权凭证不是这个。MCP `/mcp` 端点走的是 MCP 协议，鉴权直接接受 base64 token（控制台 user-management 那串）。

**判断当前接法**：
```bash
grep -B 1 -A 6 "ov-mcp-server" ~/AppData/Local/hermes/config.yaml
# 看到 enabled: true → 已经走 MCP，不用动
# 没有该段 → 没接入，按需选择内置 vs MCP
```

## 真实可用工具集（10 个）

`ov-mcp-server` 当前 schema 暴露：

| MCP 工具名 | 功能 | 类比内置 `viking_*` |
|---|---|---|
| `search` | 深度语义检索（含意图分析） | `viking_search` |
| `find` | 快速语义检索，无 session | `viking_search`（fast） |
| `read` | 读 `viking://` URI（L0/L1/L2） | `viking_read` |
| `list` | 列目录 | `viking_browse` |
| `glob` | 按文件名 glob 匹配（`*.md`、`**/*.py`） | — |
| `grep` | 内容 grep 搜索 | — |
| `remember` | 写记忆到 OpenViking | `viking_remember` |
| `forget` | 删记忆 | `viking_forget` |
| `add_resource` | 灌资源（URL/本地文件） | `viking_add_resource` |
| `health` | 健康检查 | — |

## 工具 schema 真实参数（容易踩坑）

`remember` 用 `messages` 数组（不是单 `content`）：
```json
{
  "messages": [{"role": "user", "content": "..."}],
  "target_uri": "viking://user/default/memories/foo.md"
}
```

`read` 用 `uris` 数组（不是单 `uri`）：
```json
{"uris": ["viking://user/default/memories/identity.md"], "level": "overview"}
# level 可选: overview / full
```

`list` 用 `uri`（单数）：
```json
{"uri": "viking://user/default/memories/", "recursive": true}
```

`find` 用 `query` + 可选 `target_uri` + `limit`：
```json
{"query": "影视从业者", "target_uri": null, "limit": 5, "min_score": 0.35}
```

## `remember` 后的 memory extraction 行为

OpenViking 后台会自动**按主题拆分**记忆——你写 1 条 facts，自动分类成多个独立文件：

```
写 1 条: "命名不用简写；偏好简洁回复；执行/干/拍板 = chain 不中断"
自动拆分为:
  viking://user/default/memories/preferences/user/命名习惯.md
  viking://user/default/memories/preferences/user/回复风格.md
  viking://user/default/memories/preferences/user/工作操作规范.md
```

**核心优势**：你给 facts，OpenViking 自动归类成 `preferences/<theme>.md`，不需要手工维护 MEMORY.md 主题分类。

**`identity.md` 和 `soul.md` 是默认模板**——不会被 `remember` 覆盖（除非显式 target_uri 指向它们）。

### `remember` 写入路径 = 服务端语义自动归类（2026-08-28 实测发现）

服务端按**内容性质**自动决定写到哪个命名空间，不是无脑建文件：

| 内容性质 | 归类去向 | 路径形态 | 典型场景 |
|---|---|---|---|
| **新模式 / 通用规则 / 抽象规律** | `patterns/` | `peers/<agent>/memories/patterns/mem_<hash>.md` | "OV provider 不依赖 MCP 通道"、"鉴权 header 不是 Bearer" |
| **补充性事实 / 实体属性更新** | `entities/<topic>/` | `user/default/memories/entities/<分类>/<topic>.md` | 给 openviking.md 加一段新发现、双通道稳定性对比 |
| **时间线事件 / 单次会话事实** | `events/` | `user/default/memories/events/YYYY/MM/DD/<topic>.md` | "Hermes 排查验证7条铁律确立"、"诊断铁律确立" |

**核心规则**：

- **同主题的补充信息会被合并到现有实体页**——不是无脑建新文件
- 写一条 "MCP通道 vs 内置 provider 通道 鉴权差异" → 自动合并到 `entities/技术项目/openviking.md`（不生成新 patterns 条目）
- 写一条新发现的**抽象模式**（"activated ≠ working"） → 新建 `patterns/mem_<hash>.md`
- 写一条**带日期的具体事件** → 新建 `events/<日期>/<topic>.md`

**索引延迟**：~90 秒（写完到 find 能召回之间的窗口期）。**不要立即 find 验证**——给它 ~90s；否则召回不到会被误判为"写失败"。正确验证节奏：

1. `remember` 返回 success（Stored N message(s)）→ 写入已提交
2. 等 90s
3. `find` 用**事实里具体字串**（不是抽象概念）召回——语义索引未建时关键词召回率极低

**实战反模式**（2026-08-28 踩坑）：

- ❌ remember 后立即 find → 召回空 → 误以为"写挂"
- ❌ 用抽象词（如"通道对比"）find → 召回率低 → 误以为"没写进去"
- ✅ 等 90s 后用具体字串（如"encrypted write lock error"）find → 召回命中

**验证写入是否真成功的更可靠方式**：用 `list` 看对应命名空间是否新增/更新了文件：

```python
list(uri="viking://user/default/peers/hermes/memories/patterns/")
# 看到新增 mem_<hash>.md = 写入了新模式
list(uri="viking://user/default/memories/entities/技术项目/")
# 看到 openviking.md mtime 更新 + 内容包含新事实 = 写入了实体补充
list(uri="viking://user/default/memories/events/2026/08/28/")
# 看到新增 topic 文件 = 写入了时间线事件
```

## 真测试流程（必须做，不要只看 schema 缓存）

**反面教材**：本次会话我看完 schema cache 里 10 个工具名，告诉用户「无感、工具齐全」——错。直到用户问「测试过了吗」才真测。

**真测试脚本**（用 mcp SDK 1.29.1）：
```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    ep = "https://api.vikingdb.cn-beijing.volces.com/openviking/mcp"
    key = "<base64.account.user.credential>"
    h = {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json, text/event-stream",
        "mcp-protocol-version": "2025-11-25",
    }
    async with streamablehttp_client(url=ep, headers=h, timeout=15) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()  # 握手
            tools = await session.list_tools()  # 拿工具列表
            # 真实调用 (不要传 read_timeout_seconds, mcp 1.29.1 有 int.total_seconds bug)
            r = await session.call_tool("list", {"uri": "viking://user/default/"})
            print(r.content[0].text)
asyncio.run(main())
```

## 踩坑记录（2026-08-28）

1. **mcp SDK 1.29.1 bug**：`read_timeout_seconds=30`（int）会触发 `AttributeError: 'int' object has no attribute 'total_seconds'`，**不传这个参数**让 SDK 用默认 float 即可。
2. **streamable 返回值版本差异**：mcp 1.x 返回 3-tuple `(read, write, get_session_id)`；2.x 返回 2-tuple。Hermes 当前 venv 是 1.29.1，用 3-tuple 解构。
3. **`/health` 端点独立鉴权**：MCP `/mcp` 通了不代表 `/health` 通（可能走另一层火山网关）。
4. **`grep` 显示 `...` 不代表文件被改**：grep 截断输出 ≠ mask 反向污染文件。用 `re.search(rb'Bearer\s+(\S+)', raw_bytes)` 验证实际字节。