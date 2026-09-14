# Krolik v2 端点详细映射

> 容器内权威来源：`/opt/tdai-gateway/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/v2-router.ts` 第 219-235 行 `routeTable`
> 容器内命令复现：
> ```bash
> docker exec tencentdb-gateway sh -c \
>   "sed -n '219,235p' /opt/tdai-gateway/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/v2-router.ts"
> ```

## 1. 完整 v2 路由表（容器内取证）

```ts
const routeTable: Record<string, RouteHandler> = {
  [`${V2_PREFIX}/conversation/add`]:    handleConversationAdd,
  [`${V2_PREFIX}/conversation/query`]:  handleConversationQuery,
  [`${V2_PREFIX}/conversation/search`]: handleConversationSearch,
  [`${V2_PREFIX}/conversation/delete`]: handleConversationDelete,
  [`${V2_PREFIX}/atomic/update`]:       handleAtomicUpdate,
  [`${V2_PREFIX}/atomic/query`]:        handleAtomicQuery,
  [`${V2_PREFIX}/atomic/search`]:       handleAtomicSearch,
  [`${V2_PREFIX}/atomic/delete`]:       handleAtomicDelete,
  [`${V2_PREFIX}/scenario/ls`]:         handleScenarioLs,
  [`${V2_PREFIX}/scenario/read`]:       handleScenarioRead,
  [`${V2_PREFIX}/scenario/write`]:      handleScenarioWrite,
  [`${V2_PREFIX}/scenario/rm`]:         handleScenarioRm,
  [`${V2_PREFIX}/core/read`]:           handleCoreRead,
  [`${V2_PREFIX}/core/write`]:          handleCoreWrite,
  [`${V2_PREFIX}/pipeline/status`]:     handlePipelineStatus,
};
```

其中 `V2_PREFIX = "/v2"`（在同文件上面定义）。所有路由均为 `POST`，除 `/v2/pipeline/status` 走 GET（独立在 server.ts 第 1064 行）。

## 2. 旧 MemOS `/product/<endpoint>` → Krolik v2 适配建议

旧 MemOS 客户端（memos-console-web 的 memos.ts）用 `callMemos` 拼 `${base}/product/${endpoint}`。要适配 TDB，需要：

| 旧 MemOS endpoint（语义）| TDB 真实路径 |
|---|---|
| `search` | `/v2/conversation/search` 或 `/v2/atomic/search`（按类型）|
| `get_memory_dashboard` | 聚合 `/v2/core/read` + `/v2/scenario/ls` + 计数 |
| `add_memory` | `/v2/conversation/add` 或 `/v2/atomic/update` |
| `delete_memory` | `/v2/conversation/delete` 或 `/v2/atomic/delete` |
| `delete_memory_by_record_id` | `/v2/atomic/delete`（payload 字段需重映射）|
| `get_all` | `/v2/scenario/ls` |

**不要**简单做字符串前缀替换——endpoint 语义组群不同，需要按白名单逐一映射。

## 3. 鉴权细节

- `Authorization: Bearer <TDAI_GATEWAY_API_KEY>` 必需
- key 来源：容器启动时从 `MODEL_API_KEY` 环境变量透传
- 与 LLM 端点共用同一密钥（设计如此）
- 401 = key 不对；403 = key 对但权限不足（v1 风格某些 admin 路由）

## 4. 调试时容器内无 curl

容器内 `docker exec tencentdb-gateway sh -c 'curl ...'` 会报 `sh: curl: not found`。替代方案：

```bash
# 用 node 内置 fetch
docker exec tencentdb-gateway sh -c \
  'node -e "fetch(\"http://host.docker.internal:8420/health\").then(r=>r.text()).then(t=>console.log(t))"'

# 或 wget（如果有）
docker exec tencentdb-gateway sh -c 'wget -qO- http://host.docker.internal:8420/health'
```

宿主侧直接用 curl，路径用真实路由 `/v2/...` 而不是 `/product/...`。

## 5. 实测样本（2026-08-26 NAS 现状）

```
# 健康
$ curl http://127.0.0.1:8420/health
{"status":"ok","version":"0.1.0","uptime":6014,
 "stores":{"vectorStore":true,"embeddingService":false},
 "services":{"timerScanner":{...},"pipelineWorker":{...}},
 "stateBackend":"connected"}

# /v2/conversation/search（容器内 fetch）
$ docker exec tencentdb-gateway sh -c \
    'node -e "fetch(\"http://host.docker.internal:8420/v2/conversation/search\",{method:\"POST\",headers:{Authorization:\"Bearer xxx\",\"Content-Type\":\"application/json\"},body:\"{}\"}).then(r=>r.text()).then(console.log)"'
（具体响应取决于 mem_cube 数据）

# 旧协议 404（验证不兼容）
$ curl -X POST http://127.0.0.1:8420/product/get_memory_dashboard -d '{}'
{"error":"Not found: POST /product/get_memory_dashboard"}
```