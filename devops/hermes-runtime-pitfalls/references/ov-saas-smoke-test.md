# OpenViking SaaS 端到端冒烟测试（2026-09-01 实测通过）

适用：`api.vikingdb.cn-beijing.volces.com/openviking`，v0.4.14.5，写盘场景。

## 必填环境变量（从 `~/AppData/Local/hermes/.env` 读）

```bash
OPENVIKING_ENDPOINT  # https://api.vikingdb.cn-beijing.volces.com/openviking
OPENVIKING_API_KEY   # JWT 格式 base64.base64.signature
OPENVIKING_ACCOUNT   # default
OPENVIKING_USER      # default
OPENVIKING_AGENT     # hermes（仅作 peer ID，写盘不需要）
```

## 步骤 1：加载环境

```bash
export $(grep -v '^#' ~/AppData/Local/hermes/.env | xargs)
echo "endpoint=$OPENVIKING_ENDPOINT"
echo "key_len=${#OPENVIKING_API_KEY}"   # 应 ≥ 50
```

## 步骤 2：健康探测（不鉴权）

```bash
curl -sS --max-time 5 "$OPENVIKING_ENDPOINT/health" | python3 -m json.tool
# 期望：{"status":"ok","healthy":true,"version":"v0.4.14.5","auth_mode":"api_key","account_id":"default","user_id":"default","role":"admin"}
```

## 步骤 3：鉴权探活（带 header）

```bash
curl -sS --max-time 5 \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: $OPENVIKING_USER" \
  -w '\nHTTP %{http_code}\n' \
  "$OPENVIKING_ENDPOINT/api/v1/fs/ls?uri=viking://resources/" | head -c 500
# 期望：HTTP 200 + 资源目录列表
```

## 步骤 4：temp_upload（multipart，必走 Windows 路径）

```bash
TMPFILE=$(mktemp --suffix=.md)
cat > "$TMPFILE" << 'EOF'
# OV 冒烟测试
本文件用于验证 OpenViking SaaS 端到端写盘链路。如果能在 search 中召回本条内容，说明全链路打通。
EOF
TMPFILE_WIN=$(cygpath -w "$TMPFILE")

UPLOAD_RESP=$(curl -sS --max-time 10 -X POST \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: $OPENVIKING_USER" \
  -F "file=@$TMPFILE_WIN" \
  "$OPENVIKING_ENDPOINT/api/v1/resources/temp_upload")

echo "$UPLOAD_RESP" | python3 -m json.tool
TEMP_ID=$(echo "$UPLOAD_RESP" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["temp_file_id"])')
echo "TEMP_ID=$TEMP_ID"
```

## 步骤 5：resources POST 触发 ingest

```bash
STAMP=$(date +%Y-%m-%d-%H%M%S)
curl -sS --max-time 15 -X POST \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: $OPENVIKING_USER" \
  -H "Content-Type: application/json" \
  -d "{\"temp_file_id\":\"$TEMP_ID\",\"to\":\"viking://resources/_test/${STAMP}-ov-smoke.md\"}" \
  "$OPENVIKING_ENDPOINT/api/v1/resources" | python3 -m json.tool
# 期望：{"status":"ok","result":{"status":"success","root_uri":"viking://resources/_test/...","meta":{"file_id":"tos-..."}}}
```

## 步骤 6：search 召回验证（等 3-5 秒索引）

```bash
sleep 5
curl -sS --max-time 10 -X POST \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: $OPENVIKING_USER" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"OV 冒烟测试\",\"target_uri\":\"viking://resources/_test\",\"limit\":3}" \
  "$OPENVIKING_ENDPOINT/api/v1/search/search" \
  -o /tmp/ov_smoke_resp.json

python3 << 'PY'
import json
data = json.load(open('/tmp/ov_smoke_resp.json'))
print('memories:', len(data['result'].get('memories', [])))
print('resources:')
for r in data['result'].get('resources', [])[:3]:
    print(f"  score={r['score']:.3f}  uri=.../{r['uri'].split('/')[-1]}")
PY
# 期望：score ≥ 0.5 命中刚写入的文件
```

## 判定矩阵

| 步骤 | 期望 | 失败时排查 |
|---|---|---|
| 1. health | HTTP 200, role=admin | endpoint URL 错；服务下线 |
| 2. fs/ls | HTTP 200 | API key 错（401）→ 看 .env 长度；account/user 错（403） |
| 3. temp_upload | HTTP 200 + temp_file_id | multipart 路径用 MSYS 格式（改 cygpath -w）；file 字段缺失 |
| 4. resources POST | HTTP 200 + file_id | `to` 指向目录（改具体 .md 文件 URI）；指向 viking://user/（改 viking://resources/） |
| 5. search | score ≥ 0.5 命中 | 等更久（30s）；检查 query 关键词与内容相关 |

## 一键全跑脚本（直接复用）

```bash
#!/usr/bin/env bash
set -e
export $(grep -v '^#' ~/AppData/Local/hermes/.env | xargs)

TMPFILE=$(mktemp --suffix=.md)
cat > "$TMPFILE" << 'EOF'
# OV 冒烟测试（自动）
$(date) — 端到端验证。如果你能召回本条，说明写盘链路打通。
EOF
TMPFILE_WIN=$(cygpath -w "$TMPFILE")
STAMP=$(date +%Y-%m-%d-%H%M%S)

TEMP_ID=$(curl -sS -X POST \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: $OPENVIKING_USER" \
  -F "file=@$TMPFILE_WIN" \
  "$OPENVIKING_ENDPOINT/api/v1/resources/temp_upload" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["temp_file_id"])')

curl -sS -X POST \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: $OPENVIKING_USER" \
  -H "Content-Type: application/json" \
  -d "{\"temp_file_id\":\"$TEMP_ID\",\"to\":\"viking://resources/_test/${STAMP}-ov-smoke.md\"}" \
  "$OPENVIKING_ENDPOINT/api/v1/resources" >/dev/null

sleep 5
curl -sS -X POST \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: $OPENVIKING_USER" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"OV 冒烟测试\",\"target_uri\":\"viking://resources/_test\",\"limit\":1}" \
  "$OPENVIKING_ENDPOINT/api/v1/search/search" \
  | python3 -c '
import json, sys
d = json.load(sys.stdin)
hits = d["result"].get("resources", [])
if hits and hits[0]["score"] >= 0.5:
    print(f"✅ PASS  score={hits[0][\"score\"]:.3f}")
    sys.exit(0)
else:
    print(f"❌ FAIL  no hits (got {len(hits)})")
    sys.exit(1)
'
```
