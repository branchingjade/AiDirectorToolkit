# DSH web /api 网关外部调用协议

> 来源：DSH 读源码勘察（2026-08-17 实测验证通过）。服务端契约在 `packages/host/apiproxy/`，客户端参考 `packages/client/connection/`。

## 核心事实

- 协议是「仿 JSON-RPC 的自定义 RPC」：`POST /api/<method>` + `client-request` 信封 + 直接业务 payload
- **不是 Typert Remote 协议**（那个 payload 要包 `{args:...}`，别混用）
- web UI 和外部客户端走同一套协议

## 信封格式

请求：
```json
{ "type": "client-request", "rpcId": "<唯一字符串>", "method": "<method>", "payload": { "直接业务字段" } }
```

响应：
```json
{ "type": "server-response", "rpcId": "<回显>",
  "result": { "ok": true, "value": {...} } | { "ok": false, "error": { "code": "...", "message": "..." } } }
```

⚠️ 业务错误一律 **HTTP 200 + result.ok=false**；HTTP 状态只表达载体层（403=围栏/404=路径/415=content-type/400=body 非 JSON）。

## 方法表（RpcMethodMap 键）

- **session**：`session.list` / `session.search` / `session.create` / `session.history` / `session.models` / `session.selectModel` / `session.rename` / `session.fork` / `session.prompt` / `session.attachment` / `session.updateQueue` / `session.cancel`
- **subagent**：`subagent.list` / `subagent.history` / `subagent.prompt` / `subagent.interrupt`
- **host**：`host.describe` / `host.pickDirectory` / `host.listDirectory` / `host.createDirectory` / `host.openPath`
- **workspace**：`workspace.list|create|rename|delete|insertBefore|insertSessionBefore|archiveSession`
- **skills**：`skill.list`；**agentPreset**：`list|select|read|copy|openDocument|remove`
- **goals**：`goal.create|edit|pause|resume|complete|clear`
- **其他**：`settings.*`、`credentials.*`、`llm.providers|models|discoverModels`
- 特殊：`POST /api/respond`（回答 approval/question 帧）；`GET /api/session.export?sessionId=...`（下载日志）

## 信任围栏（loopback 直接放行）

- Host 必须解析为 loopback（127.0.0.1/localhost/::1）或在 trustedHosts 声明，否则 403
- `sec-fetch-site: cross-site` 拒绝；带 Origin 必须同源；**不带 Origin 没问题**
- 特权方法（`settings.*`/`credentials.*`/`agentPreset.read/copy/openDocument/remove`/`host.pickDirectory`/`host.openPath`/`llm.discoverModels`）强制 loopback-only
- `session.*` / `host.describe` / `goal.*` 不在特权列表——Hermes 直接用

## 调用序列（已验证全通）

```
1. host.describe  {} → {version, cwd, provider, model, attachedSessions}
2. session.create {workspaceId?|cwd?, sessionId?, agentPreset?}
   → {sessionId}；固定 sessionId+cwd 幂等（cwd 变了报 session-conflict）= 断点续跑机制
3. session.prompt {sessionId, mode:"queue", content:[{type:"text",text:"..."}]}
   → {accepted:true}，只是入队；mode:"steer" 是改向不是发消息
4. session.history {sessionId, beforeSeq?, maxMessages?}
   → {events:[{event:{type,seq,time,data}, view?}], hasMore, projections?}
```

## 轨迹事件类型（思考链路）

`turn/start → step/start → user/message → assistant/chunk → assistant/message → tool/call → tool/result → step/end → turn/end`

- `tool/call` data 带 `{name, arguments|input}`；`tool/result` data 带原始载荷
- `view` 是 UI 渲染意图（可选），读原始数据用 `event.data` 即可
- 内部事件（request/header、request/context、todo/write）也会透传——按 event.type 白名单过滤

## WebSocket /api/events.mux（实时轨迹）

- WebSocket 升级（fetch 拿 426）；**downlink only**（往 socket 发消息 → close 1008）
- 每帧一条 `{type:"server-request", rpcId, method, payload}`，payload.type 为 `session/event` 时含 `{sessionId, event, view?}`
- 打开时重放 attached session 的 `session/subscribed` 控制帧（lastSeq 可作断点基线）
- **断点续读 v1 未实现**（since 被忽略）：重连 = 重开流 + `session.history` 从 lastSeq 补漏（两者数据结构同构）
- 推荐 WebSocket 而非 SSE 轮询（轨迹是高频长连接事件订阅）

## 坑清单

1. payload **不要包 `{args:...}`**（那是 Typert Remote 的协议）
2. WS 只读（1008 downlink only），上行只能 HTTP POST
3. 业务失败是 200+ok=false，别只看 HTTP 状态
4. `session.prompt` 返回只表示入队；`mode:'steer'` 不是发消息；首字符 `/` 当 slash 命令
5. `blank:true` 空会话在 UI 隐藏/复用——投一条消息才可见
6. rpcId 必须唯一且服务端回显校验
7. 会话可见性：session.create 落盘即发布 host/session-added，web UI 会话列表几乎即刻可见
8. 最大请求体默认 160 MiB（含 base64 图片）

## 最小调用示例（Python 零依赖，已验证跑通）

```python
import json, time, uuid, urllib.request

BASE = "http://127.0.0.1:8080"

def rpc(method, payload, timeout=120):
    body = json.dumps({
        "type": "client-request",
        "rpcId": f"h-{method}-{uuid.uuid4().hex[:8]}",
        "method": method, "payload": payload,
    }).encode()
    req = urllib.request.Request(f"{BASE}/api/{method}", data=body,
        headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        env = json.loads(resp.read())
    if not env["result"]["ok"]:
        raise RuntimeError(f"{method}: {env['result']['error']}")
    return env["result"]["value"]

desc = rpc("host.describe", {})                       # 握手
sid = rpc("session.create", {"cwd": r"C:\path\to\workspace"})["sessionId"]
rpc("session.prompt", {"sessionId": sid, "mode": "queue",
                       "content": [{"type": "text", "text": "任务"}]})
for _ in range(180):                                   # 轮询至 turn/end
    evs = rpc("session.history", {"sessionId": sid, "maxMessages": 50})["events"]
    types = [e["event"]["type"] for e in evs]
    if "turn/end" in types:
        break
    time.sleep(1)
```

> ⚠️ Windows 下 python 不认 MSYS 路径（`/c/Users/...`），脚本路径要用 `C:\Users\...` 原生格式。
