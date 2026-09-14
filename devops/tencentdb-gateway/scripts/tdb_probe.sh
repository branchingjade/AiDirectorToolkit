#!/usr/bin/env bash
# tdb_probe.sh — TDB (TencentDB Agent Memory) 端到端探活
# 用法：bash tdb_probe.sh [NAS_HOST]  默认 hmsj.local
#
# 返回：
#   0 = 全通
#   1 = 容器 / 端口不通
#   2 = 鉴权失败
#   3 = /v2 协议不识别（说明客户端还在用旧 /product/ 协议）
#
# 设计：5 步逐层定位，每步独立返回码，便于在 cron / 监控脚本里精细报警。

set -u

HOST="${1:-hmsj.local}"
PORT="${TDB_PORT:-8420}"
KEY="${TDAI_GATEWAY_API_KEY:-${MODEL_API_KEY:-}}"
KEY_FROM="${KEY:+env}"

if [ -z "$KEY" ]; then
  echo "[1/5] ⚠️  未提供 TDAI_GATEWAY_API_KEY / MODEL_API_KEY；尝试从 NAS .env 读取..."
  KEY="$(ssh HMSJadmin@"$HOST" "cat /opt/data/.env 2>/dev/null | grep OPENAI_API_KEY= | cut -d= -f2" 2>/dev/null)"
  KEY_FROM="${KEY:+ssh-remote}"
fi

echo "[1/5] 健康检查 http://$HOST:$PORT/health"
HEALTH="$(curl -s --max-time 5 "http://$HOST:$PORT/health")"
if [ -z "$HEALTH" ] || ! echo "$HEALTH" | grep -q '"status":"ok"'; then
  echo "  ✗ 失败：服务不在 / 端口错"
  echo "  原始响应：${HEALTH:-<empty>}"
  exit 1
fi
echo "  ✓ $(echo "$HEALTH" | python3 -c "import sys,json;d=json.load(sys.stdin);print(f\"uptime={d.get('uptime')}s embedding={d.get('stores',{}).get('embeddingService')}\")" 2>/dev/null || echo ok)"

echo "[2/5] 鉴权探测 /v2/scenario/ls"
if [ -z "$KEY" ]; then
  echo "  ⚠️  跳过：未取到 key"
else
  RESP="$(curl -s --max-time 8 -X POST "http://$HOST:$PORT/v2/scenario/ls" \
    -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d '{}')"
  CODE="$(echo "$RESP" | head -c 80)"
  if echo "$RESP" | grep -qi "unauthorized\|invalid.*token"; then
    echo "  ✗ 鉴权失败"
    echo "  响应：$CODE"
    exit 2
  fi
  if echo "$RESP" | grep -q "Not found"; then
    echo "  ✗ /v2 协议不识别——客户端可能还在用旧 /product/ 路径"
    exit 3
  fi
  echo "  ✓ /v2 协议识别 OK（响应前 80 字符：$CODE）"
fi

echo "[3/5] 旧协议 404 校验（确认旧 MemOS /product 不兼容）"
OLD="$(curl -s --max-time 5 -X POST "http://$HOST:$PORT/product/get_memory_dashboard" \
  -H "Content-Type: application/json" -d '{}')"
echo "$OLD" | grep -q "Not found" && echo "  ✓ /product/ 已确认不兼容（旧客户端需迁移）" || echo "  ⚠️  /product/ 居然返回了——协议可能变更，需查 server.ts 路由表"

echo "[4/5] Docker 容器状态（仅 NAS 本机执行时）"
if [ "$HOST" = "hmsj.local" ] || [ "$HOST" = "localhost" ]; then
  docker ps --filter 'name=tencentdb-gateway' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>&1 | tail -3
else
  echo "  跳过（远端）"
fi

echo "[5/5] 一键结论"
cat <<EOF
  - 服务端点：POST http://$HOST:$PORT/v2/<group>/<action>
  - 鉴权：Bearer <TDAI_GATEWAY_API_KEY>（key 来源：${KEY_FROM:-missing}）
  - 旧 MemOS /product/* 已不兼容，迁移见 tencentdb-gateway skill §6
EOF
exit 0