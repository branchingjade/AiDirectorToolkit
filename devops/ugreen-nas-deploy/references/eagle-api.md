# Eagle 4.0 本地 API 对接笔记（2026-08-13 实测）

Eagle 素材库（本机 `localhost:41595`）HTTP API 对接要点。来源：doubao-tts-server 素材面板「→ Eagle」功能实战 + curl 端点探测。

## 基线事实

- **`Access-Control-Allow-Origin: *`**——浏览器跨域 GET 直连可行（无需代理/bridge）
- 版本信息 + **apiToken**：`GET /api/application/info` → `data.preferences.developer.apiToken`（Eagle 4.0 build 20260401）
- 无鉴权也可用（本机 API 默认开放）

## ⚠️ 三大坑（全部 2026-08-13 实测）

1. **`createFromURL` 已废弃（4.0 返回 404 "method not allowed"）**——正确端点是 **`POST /api/item/addFromURL`**：
   ```bash
   curl -X POST http://localhost:41595/api/item/addFromURL \
     -H "Content-Type: application/json" \
     -d '{"url":"http://192.168.1.2:8000/audio/115?download=1","name":"素材名","tags":["豆包TTS","音色"],"website":"http://来源"}'
   # → {"status":"success"}（Eagle 自己下载 URL，服务器端可直接用 application/json）
   ```
2. **Eagle 不响应 CORS preflight（OPTIONS 返回 404）**——浏览器 `fetch` POST + `Content-Type: application/json` 必被拦（`Failed to fetch`）。**解法：`Content-Type: text/plain` + JSON body**（简单请求不触发 preflight，Eagle 服务端 json 解析不依赖 content-type，实测 success）：
   ```js
   await fetch('http://localhost:41595/api/item/addFromURL', {
     method:'POST', headers:{'Content-Type':'text/plain'},
     body: JSON.stringify({url, name, website, tags})
   });
   ```
3. **端点在 4.0 大改**——探测结果（POST 空 body 测存在性）：`createFromURL/createFromPath/createFromUrls/create` 全 404；`addFromURL` 400（存在，参数校验）；`addFromPath` 500（存在）；`item/list`、`folder/list` 只支持 GET（405）。

## 可用端点速查（GET 只读类）

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/application/info` | GET | 版本/偏好/apiToken |
| `/api/item/list?limit=N&orderBy=CREATEDATE&order=DESC` | GET | 素材列表（`data` 是**数组**不是 {items}） |
| `/api/folder/list` | GET | 文件夹列表 |
| `/api/item/addFromURL` | POST | **4.0 入库正解**（text/plain 绕 preflight） |
| `/api/item/addFromPath` | POST | 本地路径入库 |

## 验证入库结果

```bash
curl -s "http://localhost:41595/api/item/list?limit=3&orderBy=CREATEDATE&order=DESC" | \
  python3 -c "import json,sys; [print(' -', it.get('name'), '| tags:', it.get('tags')) for it in json.load(sys.stdin)['data'][:3]]"
```

## 前端集成模式（素材管理面板）

- `checkEagle()`：`fetch(/api/application/info, {signal:AbortSignal.timeout(2500)})` 探测在线 → 徽章「● Eagle 已连接」/「○ Eagle 未启动」
- `sendToEagle(id)`：先探测 → 用 `location.origin` 拼素材 URL（Eagle 本机能访问 NAS/源站即可）→ text/plain POST addFromURL → toast 反馈
- 标签建议：`['来源产品', 音色/角色, 日期]` 过滤空值

## 相关

- 用 Python urllib 调 Eagle API 需 `ProxyHandler({})` 绕代理（本机直连）
- 完整对接上下文（素材语义化命名/批量导出）见 doubao-tts-case.md v5.0 段
