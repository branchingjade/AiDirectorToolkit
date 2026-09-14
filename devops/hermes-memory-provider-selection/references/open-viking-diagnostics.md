# OpenViking 诊断手册（双模式 + "activated ≠ working" 铁律）

> 写于 2026-08-28，端到端实测闭合。覆盖 OpenViking 作为 Hermes memory provider 时的全部真实诊断路径与常见陷阱。

## 1. 双模式架构速查

OpenViking provider 在 `hermes-agent/plugins/memory/openviking/__init__.py` 里同时支持两种部署模式——切换只改 endpoint 一行：

| 模式 | endpoint 形态 | 鉴权 | MCP `viking_*` 工具 | 适用 |
|---|---|---|---|---|
| **本地 server** | `http://127.0.0.1:1933`（默认） | 通常无 key（trusted mode 走 `X-OpenViking-Account`/`X-OpenViking-User` 头） | ✅ 工作 | 自部署 / 内网 / Docker |
| **SaaS（VolcEngine Cloud）** | `https://api.vikingdb.cn-beijing.volces.com/openviking` | `Authorization: Bearer <api_key>` + `X-API-Key: <api_key>` | ✗ 必然 not connected | 官方云服务 |

**关键事实**：`viking_*` MCP 工具（viking_browse / viking_search / viking_read 等）走的是**本地 server 的 viking:// 文件系统接口**（HTTP 8090/1933 端口），跟 SaaS provider 是**两套完全独立的代码路径**。

→ 用户配 SaaS 时调用 `viking_*` 工具必然报 "OpenViking server not connected"——**这是预期行为，不是 provider 故障**。不要因为看到 `viking_*` 报错就以为记忆坏了，要看 agent.log 里 provider 真实调用的请求日志。

## 2. "activated ≠ working" 铁律（最常见误判）

agent.log 里看到这一行 ≠ 记忆在跑：

```
INFO run_agent: Memory provider 'openviking' activated
```

`activated` 只代表：provider 构造完成 → 注册 6 个 tool → 当前 agent 接入了 provider 接口。**实际每个 recall/retain 请求是否 200，还得看紧跟的日志**。

### 判定三步（10 秒出结论）

```bash
# 第 1 步：定位最后 activated 时间
grep "Memory provider" ~/AppData/Local/hermes/logs/agent.log | tail -3
# 例：2026-08-28 11:54:09 activated

# 第 2 步：紧跟 30 秒内是否错误爆发
grep -E "(AuthenticationError|HTTPError|HTTP 4|HTTP 5|ConnectionError|sync_turn failed)" \
     ~/AppData/Local/hermes/logs/agent.log | tail -20

# 第 3 步：直打服务端确认
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer <api_key>" \
  -H "X-API-Key: <api_key>" \
  https://api.vikingdb.cn-beijing.volces.com/openviking/api/v1/system/status
# 200 → 服务+key 都通
# 401 → key 错 / 过期 / 是 demo token
# 404 → 端点路径不对（不是 /v1/ 是 /api/v1/）
# 000 / timeout → 网络/服务挂
```

### 实战样本：SaaS + 失效 key 的完整 agent.log 形态（2026-08-28 真实截取）

```
11:10:13 WARNING plugins.memory.openviking: Service at https://api.vikingdb.../openviking responded with AuthenticationError: The API key in the request is missing or invalid. Request ID: 02178788661626700000000000000000000ffff0a00e854861859. OpenViking memory is temporarily unavailable; Hermes will retry on a later access (after cooldown) or when the config changes.
11:14:45 INFO agent.memory_manager: Memory provider 'openviking' registered (6 tools)
11:14:45 INFO run_agent: Memory provider 'openviking' activated
11:14:45 WARNING plugins.memory.openviking: Service ... AuthenticationError ...
11:14:46 WARNING [cron_1b140a071247_...] plugins.memory.openviking: Service ... AuthenticationError ...
11:16:04 WARNING plugins.memory.openviking: Service ... AuthenticationError ...
...（每 30-90 秒一次 WARNING）
11:30:08 INFO agent.memory_manager: Memory provider 'openviking' registered (6 tools)
11:30:09 INFO run_agent: Memory provider 'openviking' activated
11:30:09 WARNING plugins.memory.openviking: Service ... AuthenticationError ...
```

**模式**：每个 `activated` 后面立即跟一条同错 WARNING，然后 cooldown 重试。**整段时间 recall/retain 100% 失败，但 agent 表面看起来"激活了"**——这就是典型的假活状态，记忆实际没工作。

## 3. OpenViking 真实端点路径（不要猜）

OpenViking SaaS 真实路径前缀是 **`/api/v1/`**，不是 `/v1/`。完整路径列表（从 `plugins/memory/openviking/__init__.py` 的 `_client.post/get` 调用直接抓出）：

```
POST   /api/v1/search/search      # deep search
POST   /api/v1/search/find        # fast search
GET    /api/v1/fs/ls              # viking:// 列表
POST   /api/v1/fs/tree            # viking:// 递归
GET    /api/v1/fs/stat            # viking:// stat
GET    /api/v1/content/read       # 读资源内容
GET    /api/v1/content/abstract   # 摘要
GET    /api/v1/content/overview   # 概览
POST   /api/v1/content/write      # 写资源
POST   /api/v1/sessions           # 创建会话
GET    /api/v1/sessions/{sid}
POST   /api/v1/sessions/{sid}/messages
POST   /api/v1/sessions/{sid}/messages/batch
POST   /api/v1/sessions/{sid}/commit
POST   /api/v1/resources/temp_upload
GET    /api/v1/system/status      # 健康检查（最常用探测点）
GET    /api/v1/admin/accounts
```

### 学习真实路径的最快姿势

```bash
grep -nE '"/api/v1/' \
  ~/AppData/Local/hermes/hermes-agent/plugins/memory/openviking/__init__.py
# ↑ 源码里调用什么，server 端就有什么——比查任何文档都快
```

### 鉴权头（provider 真实发的，源码 line 305-319）

```python
h = {"Content-Type": "application/json"}
if self._agent:
    h["X-OpenViking-Actor-Peer"] = self._agent
if include_tenant:
    if self._account: h["X-OpenViking-Account"] = self._account
    if self._user:    h["X-OpenViking-User"]    = self._user
if self._api_key:
    h["X-API-Key"] = self._api_key
    h["Authorization"] = "Bearer " + self._api_key
return h
```

**有 api_key 时不传 account/user**（trusted-mode retry 才补）。SaaS 必须带 `X-API-Key` + `Authorization: Bearer`。

## 4. API key 健康度快速判定

ovcli.conf 里 api_key 是 `<tenant>.<user>.<token>` 三段格式（base64url 编码），base64 解码可读：

```python
import base64
key = open("~/.openviking/ovcli.conf").read().split('"api_key": "')[1].split('"')[0]
parts = key.split(".")
for i, p in enumerate(parts):
    pad = "=" * (4 - len(p) % 4)
    print(f"part[{i}] = {base64.urlsafe_b64decode(p + pad)}")
```

**判定规则**：
- `default.default.<hex>` → demo token，SaaS 必然 401
- `<真租户>.<真用户>.<hex>` → 真凭据，可能 work

真凭据获取路径（2026-08-28 已查实）：
1. 火山引擎控制台 https://console.volcengine.com/vikingdb/openviking/region:openviking+cn-beijing
2. 创建 API key（不是 access key，OpenViking 有自己的 key 类型）
3. CLI 写入：`printf '%s' "$OV_KEY" | ov config add ov-service --api-key-stdin --activate`
4. **不要走交互式向导** `ov config add ov-service` —— 实测卡在 "Does this server require authentication? [Y/n]" 180 秒超时

## 5. PowerShell HTTP 探测脚本模板（带 BOM 写盘）

直接发请求验证 SaaS 端点（不经过 Hermes provider），用 `.ps1` 文件 + PowerShell 5.1：

```powershell
# probe_open_viking.ps1 —— UTF-8 with BOM（无 BOM 中文/特殊字符按 GBK 解析报错）
$url = "https://api.vikingdb.cn-beijing.volces.com/openviking"
$apiKey = "<your_key>"

function Send-Post {
    param([string]$Path, [string]$Json)
    $full = $url + $Path
    Write-Host ">>> POST $full"
    try {
        $req = [System.Net.HttpWebRequest]::Create($full)
        $req.Method = "POST"
        $req.ContentType = "application/json"
        $req.Headers.Add("Authorization", "Bearer $apiKey")
        $req.Headers.Add("X-API-Key", $apiKey)
        $req.Timeout = 15000
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Json)
        $req.ContentLength = $bytes.Length
        # .NET Framework 5.x 上 HttpWebRequest.Body 是只读，必须 GetRequestStream
        $stream = $req.GetRequestStream()
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Close()
        $resp = $req.GetResponse()
        $rd = New-Object System.IO.StreamReader($resp.GetResponseStream())
        Write-Host "Body: $($rd.ReadToEnd())"
        $rd.Close(); $resp.Close()
    } catch {
        if ($_.Exception.Response) {
            Write-Host "Status: $($_.Exception.Response.StatusCode)"
            try {
                $rd = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                Write-Host "Body: $($rd.ReadToEnd())"
                $rd.Close()
            } catch {}
        } else { Write-Host "Error: $($_.Exception.Message)" }
    }
}

Send-Post "/api/v1/system/status"   ""
Send-Post "/api/v1/search/find"     '{"query":"test","limit":3}'
```

### 关键陷阱（已踩过）

- **必须 UTF-8 with BOM**：PowerShell 5.1 对无 BOM .ps1 按系统 ANSI（中文系统=GBK）解析 → 中文/em-dash 字节错位 → 假语法错且报错行号漂移。**落盘后补 BOM**：
  ```python
  p = r'C:\path\to\probe.ps1'
  data = open(p, 'rb').read()
  if not data.startswith(b'\xef\xbb\xbf'):
      open(p, 'wb').write(b'\xef\xbb\xbf' + data)
  ```
- **`.ps1` 里的 `Write-Host "..."` 中引号必须用双引号**（PowerShell 字符串），单引号转义规则不同
- **`HttpWebRequest.Body` 是只读属性**（.NET Framework 5.x）——直接 `$req.Body = $bytes` 报 "The property 'Body' cannot be found on this object"。**正确姿势**：`$req.GetRequestStream().Write($bytes, 0, $bytes.Length)`

### 探测端点的鉴权差异（2026-08-28 实测）

不是所有端点都强制鉴权，`/api/v1/system/status` 是公开的：

| 端点 | demo token 是否能访问 |
|---|---|
| `GET /api/v1/system/status` | ✅ 200（不鉴权，可作"服务在不在"探测） |
| `GET /api/v1/admin/accounts` | ❌ 401 |
| `POST /api/v1/search/find` | ❌ 401 |
| `POST /api/v1/fs/ls` | ❌ 401 |

**判定服务存活 vs key 有效**：先打 `/api/v1/system/status`（200 = 服务活），再打 `/api/v1/admin/accounts`（200 = key 真；401 = key 错）。两步组合区分"服务挂"和"key 错"——单凭 401 永远无法分辨。

## 6. 决策表：发现假活之后

| 现状 | 建议 |
|---|---|
| 配置 SaaS + demo token | 拿真 key + 走 `ov config add ov-service --api-key-stdin --activate` |
| 配置 SaaS + 真 key 但仍 401 | 检查 key 区域（cn-beijing）vs 端点 URL 区域是否一致；key 是不是 OpenViking 服务而非通用 access key |
| 想用本地 server 但没装 | `pip install openviking` 起 server（默认 1933），改 endpoint 为 `http://127.0.0.1:1933` |
| 误以为 SaaS 通了 + 实际 recall 全 401 | 立即换 key / 改 endpoint；**今天产生的会话事实不会自动进库**，需要重新 retain 关键事实 |
| 切回 Hindsight 本地嵌入 | 走 `hindsight-memory-ops` skill 末尾的恢复流程（改 watchdog + 启计划任务 + 改 config.json） |

## 7. 已知假活期间会发生什么

| 组件 | 假活期行为 |
|---|---|
| `agent.log` | activated 每 30-90 秒一次，紧跟 WARNING |
| 桌面 / 飞书 agent | "激活" 但**没有真实记忆注入**——所有 recall 返回 401 后降级为空 |
| MEMORY.md / USER.md | ✅ 独立工作，不受 provider 影响（铁律） |
| Hindsight（如果还在用） | 走自家 daemon（9177），跟 OpenViking 无关 |
| cron 任务 | 仍然触发，但每条 cron 都会触发一次 401 WARNING |
| 网关资源 | 每次 401 都是一次 HTTPS 往返（200-500ms）+ log WARNING，**长期累积可观**——这就是当时停 Hindsight 的部分理由（冗余写浪费 token） |

**关键提醒**：诊断前不要盲切 provider。先按本手册 3 步走完，确认"是真不通 + 真 key 错"再动配置。

## 8. `hermes mcp test <name>` 假阳性陷阱（2026-08-28 实测）

`hermes mcp test ov-mcp-server` 显示 `✓ Connected (1187ms)` + `Tools discovered: 10` **不等于 MCP 真的跑通了**。实测拆解：

| 测试输出 | 实际做了什么 | 没做什么 |
|---|---|---|
| `✓ Connected` | HTTP TCP 探活（preflight_content_type） | **没发 initialize 请求** |
| `Tools discovered: 10` | 读 `cache/mcp_schema_cache.json` 缓存的工具列表 | **没真发 tools/list 请求** |

**判定方法**：跑完 `hermes mcp test` 后，立即用 mcp SDK 客户端打一次真 initialize：

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    ep = "https://api.vikingdb.cn-beijing.volces.com/openviking/mcp"
    key = "<base64_token>"
    async with streamablehttp_client(url=ep, headers={"Authorization": f"Bearer {key}"}, timeout=10) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()  # 真鉴权在这里
            tools = await session.list_tools()  # 真的 list_tools
            print(f"OK: {len(tools.tools)} tools")

asyncio.run(main())
```

→ 401 = 鉴权失败（即使 `hermes mcp test` 显示 ✓）。

### Token 失效时间窗诊断法

看 `cache/mcp_schema_cache.json` 的 mtime：

```python
import os, time, datetime
sp = r"C:/Users/HMSJ/AppData/Local/hermes/cache/mcp_schema_cache.json"
mtime = os.path.getmtime(sp)
ago_hours = (time.time() - mtime) / 3600
print(f"cache mtime: {datetime.datetime.utcfromtimestamp(mtime)}")
print(f"age: {ago_hours:.1f} hours ago")
# 关键: 如果 cache mtime 比当前时间早但 token 仍被 MCP server 接受 → token 未 rotate
#       如果 cache 存在但 initialize 当前 401 → token 已 rotate（最常见 1-24h 失效）
```

**实战信号**（2026-08-28）：cache mtime 1.1 小时前（03:45），4 种鉴权 header 组合当前（04:48）全部 401 → **token 在 1 小时内被火山引擎 rotate/过期**。

### 真正的工具调用验证

`hermes mcp test` 只验证连通性。**唯一可信的"工具可用"验证**：

```python
# initialize → list_tools → call_tool 任意一个工具 → 拿到 result
r = await session.call_tool("search", {"query": "test", "limit": 3}, read_timeout_seconds=30)
# 拿到 content 列表 + text → 才是真的通了
```

## 9. OpenViking MCP 工具集 vs 内置 Provider 工具集（2026-08-28 实测对照）

同一个 OpenViking 能力,通过不同接入方式暴露的工具**不一样**:

| 接入方式 | 暴露工具 | 工具数 |
|---|---|---|
| **内置 provider**（`config.yaml memory.provider: openviking`） | `viking_search`, `viking_read`, `viking_browse`, `viking_remember`, `viking_forget`, `viking_add_resource` | 6 |
| **MCP server**（`mcp_servers.ov-mcp-server`） | `search`, `find`, `read`, `list`, `glob`, `grep`, `remember`, `forget`, `add_resource`, `health` | 10 |

**关键差异**：
- MCP 独有：`glob`（文件名匹配）、`grep`（内容 grep）、`health`（健康检查）、`find`（快速无 session 检索）
- 内置独有：无
- 名称不同但能力对应：`viking_search ↔ search`、`viking_read ↔ read`、`viking_browse ↔ list`、`viking_remember ↔ remember`、`viking_forget ↔ forget`、`viking_add_resource ↔ add_resource`

**用户决策路径**：如果想要 agent **自动**每会话 retain 关键事实 + 跨会话 recall → 用内置 provider（`memory.provider: openviking`）。如果只想在需要时 **手动查**（agent 主动调 search/read）→ MCP server 就够了，且鉴权走 token bearer 不走火山 IAM 签名。

**实测推荐**：如果只为"用 OpenViking 存/查资料"，**MCP 通道门槛更低**（base64 token 就够，不用配火山 IAM AK/SK）。内置 provider 需要火山 IAM 双段签名（AccessKey + SecretKey），云服务 SaaS 模式当前 REST API 鉴权与 MCP 鉴权方式不通用。

## 10. grep 显示截断 ≠ 文件被截断（2026-08-28 误判教训）

排查 token 长度时：

```bash
grep -B 1 -A 6 "ov-mcp-server" /c/Users/HMSJ/AppData/Local/hermes/config.yaml
# 输出: Authorization: Bearer ZGVmYX...I2NA   ← grep 自己截断显示
```

→ 看起来像 token 被 mask 截断。**但实际文件 token 完整**。验证：

```python
import re
with open(r"C:/.../config.yaml", 'rb') as f:
    raw = f.read()
m = re.search(rb'Bearer\s+(\S+)', raw)
if m:
    print(f"token len: {len(m.group(1))}")  # 真实长度
    print(f"token: {m.group(1)!r}")  # 完整 token
```

`token len: 109`（完整 base64 三段）≠ grep 显示的 `...` 截断版本。

**教训**：用 grep 看 token 显示截断时（默认 terminal 宽度限制），不要立刻判定"token 被截断了"——用 Python 读 raw bytes 才是真实状态。Hermes 输出流对 `sk-` 前缀的 mask 也只在 stdout 触发，不改原文件。
