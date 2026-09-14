# curl `-F` multipart 在 MSYS bash 下的 HTTP_CODE=000 陷阱

## 现象（2026-08-31 实测）

任何 `curl -F "file=@/tmp/xxx"` 在 MSYS bash 下都会 **HTTP_CODE=000**（连接挂起/无响应），即使端点不存在、即使鉴权正确：

```bash
curl -s -o /tmp/r.json -w "HTTP=%{http_code}\n" \
  -X POST "https://api.xxx/api/v1/temp_upload" \
  -H "Authorization: Bearer xxx" \
  -F "file=@/tmp/test.md" \
  --max-time 30
# → HTTP=000
```

即使是同一个端点的 GET 测试（`HTTP 200`）也能正常返回——**问题只在 multipart + MSYS /tmp 路径组合**。

## 根因

MSYS 把 `@/tmp/...` 翻译成本地 Windows 路径时，如果本地没该文件（MSYS `/tmp` 与 Windows `$TEMP` 不同），curl 会**发空 multipart** 或**连接挂起**——服务端拿不到正常请求就拒绝响应或挂死。

## 三种修复

### 1. Python `requests`（最稳，已验证）

```python
import os, requests
TEST = os.environ["TEMP"] + "\\test.md"  # 用 Windows temp 路径
with open(TEST, "w", encoding="utf-8") as f: f.write("hello")
with open(TEST, "rb") as f:
    files = {"file": ("test.md", f, "text/markdown")}
    r = requests.post(url, headers={"Authorization":"Bearer "+key},
                      files=files, timeout=60)
# → HTTP 200
```

### 2. curl + Windows 绝对路径

```bash
curl -F "file=@C:/Users/HMSJ/AppData/Local/Temp/test.md" ...
```

### 3. curl + `--form-string`（仅文本）

不适合二进制。

## 经验

- **curl `-F` 在 MSYS 下不可靠**，复杂 multipart 一律走 Python `requests`
- 写测试文件用 `os.environ["TEMP"]`（Windows），不要用 `/tmp`（MSYS 翻译）
- 这是 **shell 路径翻译问题**，不是协议问题——别误判为「服务端不鉴权」「端点不存在」