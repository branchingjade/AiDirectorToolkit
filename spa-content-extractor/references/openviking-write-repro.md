# OpenViking 写盘复现与根因诊断（2026-08-31）

## 来源

官方文档：https://docs.volcengine.com/docs/84313/2371368?lang=zh#sdk-接入与-api-接入如何选择
（"Agent 接入 -- 向量数据库 VikingDB -- 火山引擎"，最新更新 2026.08.03 16:15:05）

`web_extract` 对此页返 `no content extracted`（SPA bug）。用浏览器 `innerText` dump 拿到。

## 文档复现法（"读官方文档 → 原样走一遍 API → 拿到的错误响应就是根因"）

任何"客户端/服务端分不清"的诊断，按这五步走：

1. **读官方文档**：用 browser + `document.body.innerText` 拿全页面（不是 snapshot）
3. **按文档示例原样调用**：用 Python `requests` 库（不是 curl `-F`，MSYS 会把 multipart 路径翻译错）
4. **服务端的 4xx/5xx 错误响应本身就是契约**——400 响应里的 `validation_errors` 直接告诉你"哪个字段错、需要什么"。比读文档更直接。
5. **跨路径/跨参数对照测试**：同一 payload 改 `to` 字段看错误是否一致——一致就是底层问题，不一致才是路径问题。

## OpenViking 写盘完整链路（文档第 4 步 + 第 2 步）

```
# Step 1: temp_upload（multipart, 返 temp_file_id）
POST https://api.vikingdb.cn-beijing.volces.com/openviking/api/v1/resources/temp_upload
Headers: Authorization: Bearer <api_key>
         X-OpenViking-Agent: <agent_id>   # 可选，不传默认 default
Body: multipart/form-data, field "file" = <本地文件>
→ 200 OK: {"temp_file_id": "upload_xxxxx.md"}

# Step 2: 提交写入（文档第 4 步）
POST https://api.vikingdb.cn-beijing.volces.com/openviking/api/v1/resources
Headers: Authorization: Bearer <api_key>
         X-OpenViking-Agent: <agent_id>
         Content-Type: application/json
Body: {
  "temp_file_id": "upload_xxxxx.md",
  "source_name": "filename.md",
  "to": "viking://resources/<path>/<filename>.md",
  "reason": "human-readable reason"
}
```

## 关键约束（文档 + 实测）

- **资源路径必须以 `viking://resources/...` 开头**（`viking://user/...` 和 `viking://agent/...` 也可，managed 子树 skills/peers/privacy/sessions 只读）
- **API 直接传本地文件路径不接受**：必须先 `temp_upload` 拿 `temp_file_id`，再调主接口
- **错误响应契约**（直接来自服务端 400）：
  ```
  "Invalid request parameters: body: Value error, 
   Either 'path' or 'temp_file_id' must be provided"
  ```
  → 主接口接受 `path`（远端 URL）或 `temp_file_id`（已上传）二选一
- **`X-OpenViking-Agent` 可选**：不传默认 `default`（Hermes 当前用的就是 default）

## 2026-08-31 实测根因

按文档流程原样调用，第二步恒定返回 500：

```
HTTP 500
{"status":"error","error":{"code":"PROCESSING_ERROR",
 "message":"Parse error: internal error: encrypted write lock error: 
  lock I/O error: failed to create lock token at 
  /local/_system/temp/.encrypt_stage/.exact.ovlock.<hash>.encrypt.<hash>"
}}
```

**根因**：服务端在 `/local/_system/temp/.encrypt_stage/` 创建加密锁文件 I/O 失败——**容器/mount/磁盘/权限层**，不是 API 契约问题。

**跨路径一致**（同时测了 3 个不同 `to`）→ 排除是路径问题。

**结论**：客户端完全按文档来；服务端 encrypt_stage 容器基础设施侧问题，只能等火山引擎修。**用户原话"OV 云服务正常"是对的**——鉴权、read、find、tree 全 OK，写盘卡在加密暂存目录。

## MCP 层入口（同一链路的不同包装）

MCP `ov-mcp-server` 暴露的 `add_resource` 工具签名（`tool_describe` 拿到）：

```python
add_resource(
    path: str = None,              # 远端 URL / git URL / 本地路径（本地路径返上传指令）
    temp_file_id: str = None,      # 已上传的文件 id（与 path 二选一）
    description: str = None,       # forward as reason
    to: str = None,                # viking://resources/...
)
```

MCP `write` 工具（直接文本写入，比 add_resource 更轻量）：
```python
write(
    content: str,
    uri: str,                      # viking://resources/<path>/<file>.md
    mode: str = "replace",         # replace | append | create
    wait: bool = False
)
```
约束：URI 必须以 `.md/.txt/.json/.yaml/.yml/.toml/.py/.js/.ts` 结尾；managed 子树只读。

实测 `write` 工具返 `INTERNAL: Internal server error`（与 HTTP API 同源——都崩在 encrypt_stage 锁）。

## "完全接管 skill/记忆"的边界

- ✅ MCP **读侧**全可用：`health / list / read / find / search / tree / glob / grep`
- ❌ MCP **写侧**：所有写盘路径都崩在 encrypt_stage 锁
- ❌ HTTP API **写盘第二步**：同样崩在 encrypt_stage 锁
- ⏸️ cron `ebd87ff73725`（OV 团队 skill 同步）必须暂停，否则持续污染 AddResource 队列
- ✅ **用户原话"OV 云服务正常"一直是对的**——不要把责任推给服务端业务层；正确说法是"服务端基础设施（encrypt_stage 锁）问题"

## 复现脚本（粘贴可跑）

```python
import os, re, requests
cfg = open(os.environ["LOCALAPPDATA"] + "\\hermes\\config.yaml", "r", encoding="utf-8").read()
m = re.search(r'Authorization: Bearer (\S+)', cfg)
api_key = m.group(1).strip().strip('"')
base = "https://api.vikingdb.cn-beijing.volces.com/openviking"

TEST = os.environ["TEMP"] + "\\ov_test.md"
with open(TEST, "w", encoding="utf-8") as f: f.write("# test\n")

# Step 1
with open(TEST, "rb") as f:
    r = requests.post(base + "/api/v1/resources/temp_upload",
                      headers={"Authorization":"Bearer "+api_key,
                               "X-OpenViking-Agent":"hermes-test"},
                      files={"file": ("ov_test.md", f, "text/markdown")}, timeout=60)
temp_id = r.json()["result"]["temp_file_id"]

# Step 2（这一步会 500 if 服务端基础设施问题）
r2 = requests.post(base + "/api/v1/resources",
                   headers={"Authorization":"Bearer "+api_key,
                            "X-OpenViking-Agent":"hermes-test",
                            "Content-Type":"application/json"},
                   json={"temp_file_id": temp_id, "source_name":"ov_test.md",
                         "to": "viking://resources/_diag/test.md",
                         "reason": "diag"}, timeout=60)
print(r2.status_code, r2.text[:500])
```