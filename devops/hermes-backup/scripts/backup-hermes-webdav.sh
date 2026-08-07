#!/bin/bash
# Hermes WebDAV 备份 — 直传坚果云
# 用法: bash backup-hermes-webdav.sh
# 凭据: ~/.hermes/.webdav-cred (chmod 600)

set -uo pipefail

TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
LOG_FILE="$HOME/Documents/Hermes/scripts/backup-hermes-webdav.log"
CRED_FILE="$HOME/.hermes/.webdav-cred"
BASE_URL="https://dav.jianguoyun.com/dav/hermes-backup"

echo "===== Hermes WebDAV 备份 $TIMESTAMP =====" | tee -a "$LOG_FILE"

source "$CRED_FILE"
CREDS="$WEBDAV_USER:$WEBDAV_PASS"

# 打包
ARCHIVE="$HOME/Documents/Hermes/backups/hermes-$TIMESTAMP.tar.gz"
mkdir -p "$(dirname "$ARCHIVE")"

echo "[1/3] 打包 ..." | tee -a "$LOG_FILE"
tar -czf "$ARCHIVE" \
  -C "$HOME" \
  --exclude='.hermes/logs' \
  --exclude='.hermes/cache' \
  --exclude='*.log' \
  --exclude='*.tmp' \
  --exclude='.hermes/.webdav-cred' \
  --exclude='.obsidian' \
  .hermes \
  AppData/Local/hermes/state.db \
  "Documents/Obsidian Vault" \
  2>/dev/null

echo "  $(ls -lh "$ARCHIVE" | awk '{print $5}')" | tee -a "$LOG_FILE"

# 创建远程目录 (已存在则忽略 405)
echo "[2/3] 创建远程目录 ..." | tee -a "$LOG_FILE"
curl -s -u "$CREDS" -X MKCOL "$BASE_URL/" -w "  HTTP %{http_code}\n" | tee -a "$LOG_FILE"

# 上传
REMOTE_FILE="hermes-$TIMESTAMP.tar.gz"
echo "[3/3] 上传 $REMOTE_FILE ..." | tee -a "$LOG_FILE"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -u "$CREDS" -T "$ARCHIVE" \
  "$BASE_URL/$REMOTE_FILE")

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "204" ]; then
  echo "  成功" | tee -a "$LOG_FILE"
else
  echo "  失败 (HTTP $HTTP_CODE)" | tee -a "$LOG_FILE"
fi

# 清理本地旧备份（保留最近7个）
ls -t "$HOME/Documents/Hermes/backups"/hermes-*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true

echo "" | tee -a "$LOG_FILE"
