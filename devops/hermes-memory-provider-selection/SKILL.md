---
name: hermes-memory-provider-selection
description: 评估/对比/切换 Hermes 记忆提供方（memory provider）时用——以及处理 NAS 自部署 MemOS（Krolik 分支等）行为偏差时也用。触发词：记忆方案对比、换记忆、memory provider、MemOS、NAS MemOS、Krolik、custom_tags 失效、info 散到 metadata、Krolik 模块合入历史、MemOS 4 个行为坑溯源。
version: 1.5.0
author: curator
license: MIT
metadata:
  hermes:
    tags: [devops, hermes, memory, provider-selection, memos]
    related_skills: [hindsight-memory-ops, hermes-provider-integration]
    changelog:
          - 1.6.0 (2026-09-03): OV 单租户现实与「成员自己的目录」映射（admin 可访问 user/ 所有子目录，二分法落地：成员私有 → viking://user/default/memories/，项目公共 → viking://resources/）
          - 1.5.0 (2026-08-28): 新增「边际价值评估」3.1 节（迁移前 5 步 30 秒判定流程 + 用户原话「垃圾记忆不需要」+ 验收脚本 scripts/migration_value_check.py）
          - 1.4.0 (2026-08-28): OpenViking 双模式架构 + hermes mcp test 假阳性陷阱 + token 失效时间窗诊断法
---

# Hermes 记忆提供方选型与迁移评估

## When to Use

评估"要不要换掉现在的记忆方案"这一类任务的标准流程。触发词：记忆方案对比、换记忆、memory provider、OpenViking、TencentDB、TDB、商用范围。用户问某记忆系统/上下文数据库怎么样、商用范围、值不值得换时用。

## 一、先看官方内置，避免重复评估

Hermes memory provider 插件机制（2026-08 查证，`agent/memory_provider.py` + `plugins/memory/__init__.py`）：
- **内置（bundled）**：`<hermes-agent>/plugins/memory/<name>/`，当前含 hindsight、openviking(v2.0.0)、mem0、honcho、byterover、holographic、retaindb、supermemory
- **用户安装**：`$HERMES_HOME/plugins/<name>/`，同名冲突时内置优先
- 同一时间**只有一个 provider 激活**，由 `memory.provider` 配置决定——切换=改一行配置，内置 provider 零安装成本
- 评估任何第三方 provider 前先 `ls plugins/memory/` 确认官方是否已内置（2026-08 就发现 openviking 早已内置，差点白评估）

## 二、决策框架：什么时候才值得换

三个触发信号，没触发就不换（用户偏好最小必要实现，多一个 sidecar 进程/密钥配置本身就是反对理由）：
1. 现有 provider 出现**实际 recall 质量问题**（搜不到该记的东西）且无法调优
2. 要把记忆能力做成**对外商业产品**（许可证差异才真正重要）
3. 长任务 **token 成本**成为真实账单压力（订阅制计费场景此条自动失效）

换的方案必须包含：现有记忆 bank 数据**不自动迁移**（断档成本）、新 provider 的运维负担（额外进程/依赖）、与用户已有工作流（如 Obsidian 画像体系）是否重复。

### 三点一、迁移前必做：「边际价值评估」再决定迁不迁（2026-08-28 实测）

**反模式**：看到「未迁移 N,xxx 条源数据」就启动批量灌入脚本。**问题**：目标 provider 往往已有 LLM 精炼版（4,180 LLM 摘要 + 384 个 yaoyu-knowledge-base/*.md），再灌 = 触发 503 限流 + extraction 队列压力 + 召回噪音。**用户原话**：「垃圾记忆不需要」。

**正确流程**（5 步 30 秒判定）：
```
1. ls 目标 provider 现状：list(uri, recursive=True) 量化已有 L0/L1 数量
2. 5 个采样 query find()（覆盖核心项目 / 主题 / 角色 / 工具 / 决策）
3. 计算平均 score：
   - ≥ 50% + 内容是 LLM 精炼版（带决策摘要 + 路径标注）→ 停止，源数据再灌边际价值低
   - < 30% 或内容是源数据原文 → 才进入 Phase 3 灌入流程
4. 评估指标不是「文件数」，是「find() 召回命中率 + 召回内容是否直接可用」
5. 「直接可用」定义 = LLM 摘要 + 决策原文 + 路径标注，agent 不必再读源文件就能用
```

**验收脚本**：见 `scripts/migration_value_check.py`（基于 find() 5-query 平均 score + 精炼版占比，判定 STOP / PROCEED / GRAY ZONE）

## 三、兼容性验证流程（只查不改）

评估第三方 provider 本机可装性，用户同意后才做，全程不改配置：
1. 读 `config.yaml` 的 `memory.provider`（当前值）
2. `ls <hermes-agent>/plugins/memory/` 看官方已内置哪些
3. 抓安装脚本，**核对它假设的 HERMES_HOME/插件目标路径 vs 实际路径**——本机 HERMES_HOME=`C:\Users\HMSJ\AppData\Local\hermes`，不是 `~/.hermes`（`~/.hermes` 是空壳，只有 `custom_providers: []`）；多数第三方脚本默认 `%USERPROFILE%\.hermes`，直接跑会装错目录 Hermes 根本扫不到
4. `netstat -ano | grep :<端口>` 查 sidecar 端口占用
5. `node --version` / `npm --version` 对照要求
6. 输出=环境门槛表 + 决策建议，不改任何配置

验证 Hermes 实际 home 目录：`python -c "import sys; sys.path.insert(0,'<hermes-agent路径>'); from hermes_constants import get_hermes_home; print(get_hermes_home())"`

## 三点五、Provider "activated" ≠ "working" — 必须区分的诊断铁律（2026-08-28 实测）

**最常见的认知陷阱**：看到 agent.log 里 `Memory provider 'openviking' activated` 就以为记忆在跑。**不是**——`activated` 只代表 provider 构造完成、6 个 tool 注册成功。**真正的 recall/retain 是否通，必须看激活后紧跟的请求是不是 200**。

### 诊断三步（10 秒内出结论）

```bash
# 1. 抓最新一组 activated + 后续 30 秒的日志
grep "Memory provider" ~/AppData/Local/hermes/logs/agent.log | tail -3
# ↑ 拿到最后 activated 时间戳（如 11:54:09）

# 2. 紧跟 activated 之后看是否有错误爆发
grep -E "(AuthenticationError|HTTPError|HTTP 4|HTTP 5|ConnectionError|timeout|sync_turn failed)" \
     ~/AppData/Local/hermes/logs/agent.log | tail -20
# ↑ 401/403/500/死锁 任何一个连续出现 → key 失效 / 服务挂 / 端口死

# 3. 验证服务端真的活着
curl -s -o /dev/null -w "%{http_code}\n" <provider endpoint>
# 200/401/403 → 服务在响应（401 多半是 key 错）
# 000 / timeout → 服务挂或网络不通
```

### 关键反模式

- **别只 grep `activated`** ——provider 每次新 agent 都会打印一次，看着像"通了"实际背后可能 100% 在重试 401
- **别信 `hermes memory status` 显示 `available`** ——这只代表 import 没崩，不代表端到端能 recall
- **别把 `viking_*` MCP 工具的 "OpenViking server not connected" 当成 provider 故障** ——`viking_*` 工具是给**本地 OpenViking server**（HTTP 8090/1933，viking:// 文件系统接口）用的，跟 SaaS provider 是两套代码路径。本机配 SaaS 端点时 `viking_*` 必然报 not connected，这是预期不是 bug

### `hermes mcp test` 的"✓ Connected + Tools discovered"是乐观假象（2026-08-28 实测踩坑）

**现象**：配置好 MCP server 后跑 `hermes mcp test <name>`，终端打 `✓ Connected (1187ms) ✓ Tools discovered: 10`，你以为通了。**实际**：这只是 preflight HTTP 探活 + 读 `cache/mcp_schema_cache.json` 里旧 schema，**不发真鉴权请求**。

**为什么这样设计**（看 `hermes_cli/mcp_config.py:_probe_single_server` + `tools/mcp_tool.py:_preflight_content_type`）：

1. `_preflight_content_type` 先做一次 HEAD/GET 探活 → TCP 通就判 Connected
2. `tools` 列表从 `mcp_schema_cache.json` 直接读指纹（`fingerprint`）合并，不发 `initialize/list_tools`
3. 所以 schema 可能来自一小时前/一天前的成功握手，**server 早已 401 但 fingerprint 还在缓存**

**判定"真连通"的正确做法**（不能信 mcp test）：

```python
# 用 mcp SDK 真发 initialize + 一次 tool call（一次工具调用 = 端到端通了）
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    ep = "<server url>"
    h = {"Authorization": f"Bearer <key>", "Accept": "application/json, text/event-stream"}
    async with streamablehttp_client(url=ep, headers=h, timeout=15) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()                # 鉴权真正校验
            tools = await session.list_tools()        # 拿真 schema
            r = await session.call_tool("xxx", {...}) # 真调一次工具
            print(r.content[0].text[:300])

asyncio.run(main())
# 只要全程没 raise = 真通
```

**陷阱**：`mcp` SDK 1.29.1 有个 bug，`call_tool(name, args, read_timeout_seconds=30)` 会抛 `AttributeError: 'int' object has no attribute 'total_seconds'`（不传 `read_timeout_seconds` 就正常）。这是 SDK bug 不是鉴权问题。

**何时重跑 schema cache**：任何 MCP server 配置变更（URL/key/headers），必须先 `rm ~/.cache/mcp_schema_cache.json` 再用，否则新 schema 永远不写、cache 里的旧 fingerprint 让你误以为测试通过。

**判断 token 是否真失效**：`cache/mcp_schema_cache.json` 的 mtime = 上次真握手时间。如果现在 `mcp test` 通过但上次成功是 1 小时前 → 大概率 token 已 rotate/过期；不要相信 test 的"✓"。

### OpenViking viking:// 命名空间设计（2026-08-28 实测）— 别再问"公开库怎么做"

`viking://` 是统一文件系统协议，根下两个一级目录**性质完全不一样**：

| 命名空间 | 范围 | 谁能看到 | 用途 |
|---|---|---|---|
| `viking://user/<account>/` | 私有（per-account） | 只有当前账户的 agents | 长期记忆（memories / preferences / sessions / skills） |
| `viking://resources/` | 公开（账户级共享） | 同账户下所有 agents | 团队/项目共享知识、官方文档、add_resource 灌入的资源 |

**用户的"公有库怎么做"问题答案**：`viking://resources/` 就是答案。不要再去搭新的"公开库"。

**几个真实坑**：

1. `add_resource(url, to=...)` 是**异步处理**——加进去后立即 `find()` 大概率抓不到（LLM 后台消化需要 30s~几分钟）。等一会儿再查。
2. `find(query, target_uri='viking://resources/')` 限定范围；不传 = 全局搜（user + resources 混）。
3. `read(uri, level='abstract'|'overview'|'full')` 三层加载。L0 ~100 token 摘要适合注入 prompt；L1 overview 概要；L2 full 慎用（大文件）。
4. `add_resource` 自动按主题拆分（README → 3 个子文档）。这是核心优势，但**不要把所有东西都灌进去**——token 账单 + 后台处理吃不消，757 md 全灌必爆。
5. **AGPL-3.0 商用雷区**：用云服务没问题（你付钱给火山），但**不能拿 OpenViking 服务做商业产品二次包装对外销售**——会触发 AGPL 传染条款（改后对外网络服务须整体开源回吐）。

#### 单租户现实与「成员自己的目录」映射（2026-09-03 实战确立）

**反模式**：以为 `viking://user/<成员名>/` 能给每位成员开独立 namespace → 在飞书多用户场景"按成员分别落"。**错**——admin token 看到的 `viking://user/` 下只有 `default/` 单租户实例；`default` **就是**当前账号的个人 namespace。

**「成员自己的目录」的正确语义**：

| 你想表达的 | OV 里对应路径 |
|---|---|
| 某位飞书成员（陈星艳/全志越...）的画像 / 偏好 / 历史交互 | `viking://user/default/memories/entities/人物/<姓名>.md` |
| 当前你（hermes/施文皓）的偏好 / 配置 / 踩坑 | `viking://user/default/memories/preferences/...` |
| 当前你的事件流 / 调试日志 | `viking://user/default/memories/events/<YYYY>/<MM>/<DD>/<event>.md` |
| 跨成员共享的项目资产（伏妖记剧本 / 犬子无双分镜） | `viking://resources/projects/<项目名>/...` |
| 团队公开手册 / 公约（团队记忆手册等） | `viking://resources/_team-handbook/...` |
| **飞书侧成员共享的协作数据**（成员名单 / 路由表 / 评论线程归档） | 按"私有"还是"团队"二选一，**不等于** obsidian `_hermes/` 一锅端保留 |

**决策二分（2026-09-03 用户拍板）**：
- **成员私有 / 私人偏好 / 个人事件记忆** → `viking://user/default/memories/...` （admin 可访问所有 user/ 子目录，团队协作不需要复写到 resources）
- **项目共享资产 / 真正需要公开广播的手册** → `viking://resources/<dir>/...`

> 迁移时不要按"成员"维度去拆 namespace——OV 是单租户 admin 视角，把所有 user/ 内容当成"admin 能看到的协作池"看待即可。判断标准回归到"是不是项目/公共都需要看"，不是"是不是发给谁的"。

**反模式**（之前踩过）："我觉得飞书侧要走公共空间 viking://resources/，因为是协作"——其实只要 owner=admin 凭据，所有 user/ 私有都能在 admin 视角下协作访问。**走公共空间的前提是「需要非 admin 账号也读到」，不是「需要多人看到」**。这两个条件容易混。

**写入 schema 注意**（`remember`/`read` 命名怪点）：
- `remember(messages=[{"role":"user","content":"..."}], target_uri="viking://...")` — 数组结构，不是单 content
- `read(uris=["viking://..."])` — 数组，单数 uri 报 "InvalidArgument: uris must not be empty"
- `list(uri="...")` — 单数
- `find(query=..., target_uri=..., limit=...)` — query 必填，target_uri 可选

**OpenViking Service 云服务的鉴权双轨**（必须区分）：
- `/mcp` 端点（MCP 协议）→ 用 base64 token `account.user.credential`（user-management 里的鉴权凭证列）
- `/api/v1/*`（REST）→ **不接受同一 token**，需要火山引擎 IAM AK/SK 双段签名
- 所以内置 provider（走 REST）**用不了 user-management 的 token**，必须用 MCP（走 /mcp）

### OpenViking 双模式架构（2026-08-28 实测端到端闭合）

OpenViking provider **同时支持两种部署**，配置一行切换：

| 模式 | endpoint | 端点前缀 | MCP `viking_*` 工具 | 典型场景 |
|---|---|---|---|---|
| **本地 server** | `http://127.0.0.1:1933` | `/api/v1/` | ✅ 工作（HTTP 直连） | 自部署/内网/Docker |
| **SaaS（VolcEngine Cloud）** | `https://api.vikingdb.cn-beijing.volces.com/openviking` | `/api/v1/` | ✗ 必然 not connected | 官方云服务 |

**判断当前模式**：读 `~/.openviking/ovcli.conf`（CLI 默认配置）or 看 `OPENVIKING_ENDPOINT` 环境变量 —— URL 含 `127.0.0.1` = 本地，含 `volces.com` = SaaS。

**真实端点路径前缀是 `/api/v1/`**（不是 `/v1/`），不要凭 SDK 约定猜路径。**最快的学习办法**：在 `plugins/memory/openviking/__init__.py` 里 grep `self._client.get/post.*"/api/v1/`，源码暴露什么路径服务端就有什么路径——比查文档快。

### API key 健康度快速判定

```python
import base64
key = "ZGVmYXVsdA.ZZGVmYXVsdA.MzM2..."  # ovcli.conf 的 api_key
parts = key.split(".")
for i, p in enumerate(parts):
    decoded = base64.urlsafe_b64decode(p + "=" * (4 - len(p) % 4)).decode("utf-8", errors="replace")
    print(f"part[{i}] = {decoded!r}")
# part[0/1] = 'default' / part[2] = '<hex>'  ← demo token 特征
# 真凭据 part[0] 是真实租户 ID，不是 "default"
```

`default.default.<hex>` 形态 = demo/test token，火山引擎 SaaS 必然 401。要拿真凭据：火山引擎控制台 → VikingDB → OpenViking 服务 → 创建 API key（不是 access key）。CLI 写法：`printf '%s' "$OV_KEY" | ov config add ov-service --api-key-stdin --activate`（不要走交互式向导，180 秒卡在 "Does this server require authentication?" 已实测）。

完整诊断脚本 + agent.log 错误样本见 `references/open-viking-diagnostics.md`。

## 四、已评估 provider 速查（2026-08-14 本机实测）

| 项目 | OpenViking（字节） | TencentDB Agent Memory（腾讯） | Hindsight（现用） |
|---|---|---|---|
| 许可证 | AGPL-3.0（改后对外网络服务须整体开源回吐） | MIT（随便商用，保留版权声明即可） | Hermes 内置 |
| 部署 | 本地 | 本地 SQLite+sqlite-vec，不强制上腾讯云 | 本地+外部服务 |
| Hermes 集成 | **官方内置 provider v2.0.0**，改 `memory.provider` 即切 | 第三方插件 `memory_tencentdb`，Node sidecar gateway :8420 | 官方内置，已全面启用 |
| 安装门槛 | 零 | Node≥22.16 + npm + `TDAI_LLM_*` 环境变量 + bat 脚本（HERMES_HOME 要手动指路） | — |
| 卖点 | 上下文文件系统 viking://，L0/L1/L2 分层 | L0→L3 语义金字塔含用户画像层，长任务 token -61%（厂商自报） | 已稳定运行 |

详细对比与来源见 `references/provider-comparison.md`。 Krolik 实测踩坑（2026-08-26 NAS 192.168.1.2:8001 端到端验证，client `scripts/memos_client.py` + 物证 `分析/MemOS端到端验证-2026-08-26.md`）：
- **Krolik 不是"私有 fork"——是 MemTensor 官方 `docker/Dockerfile.krolik` 模板 + 二次分发者维护的 overlay**。MemTensor 公开版本是 `MemOS 2.0 Stardust`，Krolik 不在公开 README 中（README_ZH.md 全文 0 次出现 Krolik）。`docker/Dockerfile.krolik` 是 MemTensor 在自己 docker 目录里提供的另一 build target，标语 *"MemOS with Krolik Security Extensions"*——它从 base 镜像装完基础依赖后 `COPY overlays/krolik/ ./src/memos/` 加一层 overlay。**关键**：`overlays/krolik/` 目录不在公开仓里，是某二次分发者 build 时加进去的（NAS 镜像源 / 内部 PaaS / 团队封装都可能是）。所以 `2.0.3-krolik` = `MemTensor Dockerfile.krolik 模板` + `二次分发者的内部 overlay`。判断"是不是 bug"用这条：upstream main 有 `exclude_fields` 过滤，Krolik overlay 没移植，所以行为有差；不是 MemTensor 自己的 bug，是 fork 扩展的差异。
- **Krolik 不是私有 fork,不是某个二次分发者维护的 overlay**——是 MemTensor 公开仓里某个开发者(2026-02-06,GitHub 用户 `Hustzdy`, PR #1040, commit `c2bc36b15f`)合入的**实验性扩展模块**,官方文档明示:"某位开发者扩展后的 API 及部署配置,**仅供参考**。这些内容**尚未与云服务集成**,**仍处于测试阶段**"(`docs/cn/open_source/modules/api_deployment.md` L11)。
- **Krolik 只加 4 件事**(看 `src/memos/api/server_api_ext.py` 自己的 docstring):API Key 鉴权、Redis 限流、Admin 路由(`/admin/*`)、安全响应头。**业务行为一个没动**——add/search/feedback/delete 全是 MemTensor 上游 main 自己的实现。
- **MemTensor 没发布官方 docker 镜像**——12 个 workflow 0 处 `docker push` / `ghcr.io` / `docker/build-push-action`。`docker/Dockerfile.krolik` 是**给自部署者本地 build 用的模板**,`overlays/krolik/` 是**空目录**,Krolik 全部代码(`server_api_ext.py` / `admin_router.py` / `middleware/auth.py` / `middleware/rate_limit.py`)**都在 base 仓里**。
- **CORS 配置里的 `krolik.hully.one` 域名 + commit author 邮箱 `syzsunshine219@gmail.com`**——是 Hustzdy / 该团队运营面(不是你的部署,也不是你之前 mvs-doubao-2 项目的产出)。
- **"4 个坑"的真实溯源(全部 MemTensor 上游 main,不是 Krolik 引入)**:
  - `custom_tags` 字段被接受 + 覆写为 `["mode:fast"]` → MemTensor 上游 `add_handler.py`
  - `info` 散到 metadata 顶层 → MemTensor 上游(2026-02-06 之后 `c2bc36b15f` commit 加了 `exclude_fields` 过滤,你 NAS 镜像 build 时选了**比 c2bc36b15f 更早**的 main commit,所以才有这个 bug——不是 Krolik 没移植,是你镜像的 base 老)
  - `feedback` 必填 `history` → MemTensor 上游 schema 漏标必填
  - `delete_memory` 互斥但 silent failure → MemTensor 上游
- **怎么确证"4 个坑来自哪一版 main"**(比 docker inspect 更直接):
  ```bash
  # 1. 看 Krolik 第一次合入的 commit,确定基线
  curl -s https://api.github.com/repos/MemTensor/MemOS/commits?path=src/memos/api/server_api_ext.py | jq -r '.[].commit.committer.date'
  # ↑ 2026-02-06, c2bc36b15f

  # 2. 拉那个 commit 当时的 add_handler.py,看有没有 exclude_fields
  curl -s https://raw.githubusercontent.com/MemTensor/MemOS/c2bc36b15f/src/memos/api/handlers/add_handler.py | grep exclude_fields
  # ↑ 已有 → 你 NAS 镜像 base 比这更老

  # 3. SSH 进 NAS 看实际 base 是哪个 commit
  ssh HMSJ@192.168.1.2 "docker exec memos-server git -C /app log --oneline -1 2>/dev/null || echo NO_GIT"
  ```
  注意:**`overlays/krolik/` 是空目录**这个事就足以证伪"overlay 改了 add 行为"——一个空目录 COPY 不会覆盖任何东西。
- **NAS 部署版(Krolik)≠ Cloud 版本**——OpenAPI 一致但行为有偏差,根因不是 fork drift,是 base main commit 不同。
- `custom_tags` **被系统覆写为 `["mode:fast"]`**——你传的 list 全丢。需求强分类时**改写进 messages 文本**(`[伏妖记][山神设定] 三件套...`),不要指望 `tags`/`info` 当分类用。
- `info` 字段**散到 metadata 顶层**(不是 metadata.info),传 `info={"topic":"y","agent":"z"}` 后看到的是 `metadata.topic` / `metadata.agent` 单独出现在 metadata 上。`source`/`info`/`tags` 是 MemTensor/MemOS 字段名占位,**不要**用这名字当自定义 key,用 `topic`/`agent`/`proj`/`ts`。
- `feedback` 必传 `history=[]`(OpenAPI 未标必填)。`sync=True` 卡 30+s 默认走 `sync=False`(async 队列 ~10s 返回)。
- `delete_memory` 同时传 `memory_ids` + `user_id` 是 **silent failure**:返回 200 但 `data.status=failure` 什么都不删。要求"恰好一种删除模式"(`memory_ids`/`session_id`/`file_ids`/`filter` 四选一)。要按用户清空不要传 `memory_ids`。
- sync 写入卡 30~40s(实测超 12s 必超时)。**默认 async**(~5s 可被 search 召回)。`sync` 仅在必须"写完立刻读"时用。
- 召回字段是 `id` 不是 `memory_id`(OpenAPI 提及但表现不稳)。Client 封装兼容。
- `/product/get_all` 名字误导——它实际是分页全量拉,不是 dashboard。**真要看分布用 `/product/get_memory_dashboard`**(重计算,控超时 8s 以上)。
- NAS version `2.0.3-krolik`。`auth_enabled=true` + `master_key_configured=true`,但 `/product/*` 似乎未强制头校验(实测无 token 也能 200,返回空 cube)。**生产写入仍推带 master key**,拿法见 `scripts/memos_client.py` docstring。

- **TencentDB Agent Memory `/capture` 端点只收 `string` 字段**(2026-08-26 实测源码 `src/gateway/types.ts`):`user_content`/`assistant_content`/`messages[]` 全部 string,无 `image_url`/`file_id`/`base64`/multipart 任何多模态字段。**bot 想"记住图"必须 bot→OCR adapter→转文字→再 capture**,图片本体不进 hub。Obsidian vault 里 41 个 PDF 同样不能直接进 hub——走 LLM-Wiki 资产 + 文件路径索引(不要想着将 PDF 灌进 fact layer)。这是选型时容易忽视的"功能盲点",写技术评估时必须实测 `CaptureRequest` schema 不能只看 OpenAPI 描述。

  **OCR 替代方案验证可用**(2026-08-26): MiMo-v2.5 **有 vision**(`mimo-v2.5` 模型支持 OpenAI `image_url` 标准格式)。bot 收到飞书群图 → lark-cli 下载 → MiMo vision 描述 → 文字 capture 到 TDB。完整流程见 `references/tencentdb-gateway-deploy.md` 末尾"MiMo-v2.5 真实能力"节 + `scripts/ocr_adapter.py` + `scripts/feishu_image_ocr.py` 端到端集成版。

## 五、坑(2026-08-14 + 2026-08-26 实测)

- 第三方 Hermes 集成脚本(TDB 的 `setup-hermes-memory-tencentdb.bat`)默认 `HERMES_HOME=%USERPROFILE%\.hermes`——本机必须 `$env:HERMES_HOME="C:\Users\HMSJ\AppData\Local\hermes"` 后再跑
- 厂商基准数据(token 节省/通过率提升)是自报,且场景多为编程长任务(SWE-bench/WideSearch),与创作/运维场景相关度有限;订阅制计费下省 token 不省钱
- 评估结论要诚实区分"环境门槛过了"和"值得换"——两者独立
- **NAS MemOS 实例行为 ≠ Cloud API 文档**:Cloud 上能用 `info` 过滤、`custom_tags` 强分类的隐性预期,Krolik 上做不到。**不要拿云 API 预期下沉到 NAS 自部署版**,必须本机实测后总结(上表为已实证)。端到端验证脚本 `Temp/memos_e2e_*/smoke*.py` 可重跑评估 Krolik 现状。
- `memos_client.py` 作为 NAS MemOS 的客户端封装,**评估其他 NAS 部署场景时复用**(同步改 `BASE` + `KEY`)。
- **"是 bug 还是 fork"这类溯源问题不要凭文档一句话下结论**(2026-08-26 实测踩过 3 次):先后被"私有 fork"→"fork 扩展"→"实验性模块"骗了两次,正确路径是先 `git log --follow` 找首次合入 commit,再 `curl raw.githubusercontent.com` 拉那个 commit 的源码看是不是上游行为。**没有源码证据不下"是 fork 改的"这种结论**。
- **OpenAPI 文档 ≠ 服务实际行为**——尤其私有 fork / 实验性扩展场景。**当前 NAS MemOS 上 4 个坑(custom_tags 覆写 / info 散顶层 / feedback 必填 history / delete 互斥静默)全在 client `scripts/memos_client.py` 兜底**,新坑按相同模式加进去就行。

## 六、参考文献

- `references/provider-comparison.md` — OpenViking / TencentDB / Hindsight 三方对比
- `references/krolik-sourcing.md` — Krolik 溯源 / 4 个坑的真实出处 / 客户端兜底位置 / 跨实例迁移注意(本次新增,2026-08-26)
- `references/open-viking-diagnostics.md` — OpenViking 双模式诊断 + "activated ≠ working" 判定铁律 + agent.log 401 实战样本（2026-08-28 新增）。新增第 8-10 节：`hermes mcp test` 假阳性陷阱、token 失效时间窗诊断法、MCP vs 内置 provider 工具集对照、grep 显示截断 vs 真实文件状态（2026-08-28 晚）
- `references/openviking-mcp-real-test-20260828.md` — MCP 真实可用工具集 + `remember` 后**服务端语义自动归类（patterns/entities/events 三路径）+ ~90s 索引延迟 + 验证写入的 list 姿势**（2026-08-28 晚补）
- 端到端物证:`分析/MemOS端到端验证-2026-08-26.md`(7/7 OK + 4 个坑现场复现)
- 客户端:`scripts/memos_client.py`(265 行,标准库 only)

## 七、团队公用资源灌入实战（`viking://resources/...` 写入路径，2026-08-28 晚端到端验证）

> **场景**：团队助手需要把手册/文档/公约写到团队公共空间，让所有成员助手都能 find 召回。
> **坑集中在工具边界**：MCP 通道和内置 HTTP API 字段不一致，必须按服务端契约走，否则写到 user/ 私有空间。

### 7.1 MCP `add_resource` 工具 vs 内置 HTTP API 行为差异

| 维度 | MCP `mcp__ov_mcp_server__add_resource` | 内置 HTTP API `POST /api/v1/resources` |
|---|---|---|
| 接 `to` 字段？ | **❌**（参数 schema 校验失败 `unexpected additional properties 'to'`） | ✅（必须用 `to`，**不是** `path`） |
| 接 `uri` 字段？ | ❌ | ❌ |
| 接 `path` 字段？ | ❌ | ⚠️ 接受但**silently 忽略**——结果写到 `viking://user/default/resources/<basename>` |
| 默认写入位置 | `viking://user/default/resources/<basename>` | 同上（无 to 时） |
| 返回警告 | "Use --to <path> to specify exact target" | 同上 |

**实测 5 个候选字段名**（`to` / `target_uri` / `uri` / `dest` / `destination`）：只有 `to` 被服务端接受，其余全部 `INVALID_ARGUMENT: Extra inputs are not permitted`。

### 7.2 团队公共空间灌入的正确流程（4 步）

```bash
# Step 1: multipart 上传到 temp 池（拿到 temp_file_id）
POST {endpoint}/api/v1/resources/temp_upload
  Headers: X-API-Key + X-OpenViking-Account + X-OpenViking-User（**不是** Bearer）
  Body: multipart/form-data, field="file"
  → 返回: {"temp_file_id": "upload_xxx.md"}

# Step 2: 把 temp 资源落到目标 URI（关键：用 'to' 不是 'path'）
POST {endpoint}/api/v1/resources
  Headers: X-API-Key + X-OpenViking-Account + X-OpenViking-User
  Body: {"temp_file_id": "upload_xxx.md", "to": "viking://resources/_team-handbook/foo.md"}
  → 返回: {"root_uri": "viking://resources/_team-handbook/foo.md"}

# Step 3: 验证（等 ~90s 后台语义索引完成）
POST {endpoint}/api/v1/search/search
  Body: {"query": "<关键词>", "target_uri": "viking://resources/", "limit": 5}
  → 应看到新写入条目 + 服务端自动生成的 .abstract.md + .overview.md

# Step 4: 检查 overview 更新
GET /v1/v1/content/read
  Body: {"uri": "viking://resources/.overview.md"}
  → 索引应自动包含新子目录
```

**完整 Python 实现**（无硬编码，凭据走 .env）：见 `scripts/ov_public_resource_publish.py`。
**端到端 transcript**（草稿生成 → 5 次字段探测 → 成功 → find 验证 → user/ 残留处理）：见 `references/ov-public-resource-publish-20260828.md`。

### 7.3 ⚠️ MCP `forget` 强制 unreachable 陷阱（2026-08-28 晚首次撞出）

**症状**：连续 3 次调 `mcp__ov_mcp_server__forget` 失败（如 `FAILED_PRECONDITION: Cannot remove directory without --recursive`），第四次再调就被告知：

```
MCP server 'ov-mcp-server' is unreachable after 3 consecutive failures.
Auto-retry available in ~47s. Do NOT retry this tool yet — use alternative approaches or ask the user to check the MCP server.
```

**根因**：`tools/mcp_tool.py` 的"park"机制——3 次失败触发 parked 状态，**5 分钟内**（`_PARKED_RETRY_INTERVAL=300`）所有 MCP 工具调用直接被客户端 reject，即使服务端已恢复。

**坑点**：

1. **验证操作会消耗重试预算**——想"试一下能否清掉残留" → 连续 3 次失败 → 后续 MCP 通道全部不可用 47 秒
2. **`forget` 不支持 `--recursive` 参数**（MCP 工具封装层缺），但删除嵌套目录必须 `--recursive`` → MCP 通道**根本删不了目录资源**
3. **HTTP API 删除端点不存在**（实测 `/api/v1/resources/delete` / `/api/v1/resources/manage` / `/api/v1/admin/resources/delete` 全 404）——admin endpoint 才有但本机无权限

**处理策略**：
- **写入前先想清楚路径**——错了就留 `user/default/resources/<basename>_N` 残留（MCP 删除受限）
- **不要为了清理残留连续调 `forget`**——直接放空，等下次 sync 覆盖或联系火山引擎 admin 端
- **真要清理 → 走 `hermes` 内置 provider 通道的 delete 端点**（如果有 admin 权限）

### 7.4 MCP `add_resource` 写错位置怎么办

**症状**：用 MCP `add_resource` 没指定 URI，自动落到 `viking://user/default/resources/`，累积 N 个 `<basename>`、`<basename>_1`、`<basename>_2`、`<basename>_3` 残留。

**判定**：污染度评估——这些是**空目录容器**（只占 metadata slot，不影响 find 召回），除非磁盘/账户配额紧张，**接受为已知遗留**比死磕清理更划算。

**清理路径**（按优先级）：

| 路径 | 可行？ |
|---|---|
| `mcp__ov_mcp_server__forget` 多次调用 | ❌ 受 MCP park 限制 + 工具不支持 `--recursive` |
| HTTP API `/api/v1/resources/delete` | ❌ 404 不存在 |
| HTTP API `/api/v1/admin/resources/delete` | ❌ 404 不存在 |
| 联系火山引擎 admin 端 | ✅ 唯一靠谱路径，**标记为运维待办** |

### 7.5 团队公用决策模式（用户偏好信号，2026-08-28 晚确立）

当任务涉及"团队/公用/共享"语义：

1. **目标位置必须是 `viking://resources/<dir>/`，不是 user/ 私有空间**——区分命名空间是第一步
2. **目录命名用下划线前缀**（如 `_team-handbook/`）——和内置排除目录 `.archive/` `.hub/` 同语义（系统资源 vs 用户资源），区别于 skill 的 `viking://resources/skills/`（不带下划线）
3. **形态优先单文件**——单文件 find 召回无需指定 target_uri，跨场景通用；多文件要分层 target_uri 易漏
4. **写入由管理员拍板**——read-only on team 治理，避免漂移
5. **起草流程**：起草者出 v0 → 拍板者 review → 定稿（不在 v0 阶段就纠结细节）
6. **通知机制先不做**——除非明确要，否则"通知"是后续可选项，避免第一版就背上通知运维负担
