#!/bin/bash
# Hermes 备份脚本 — 增量同步到坚果云
# 用法: bash backup-hermes.sh
# robocopy 返回码 <=7 均为成功

set -uo pipefail
export MSYS_NO_PATHCONV=1

TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
LOG_FILE="$HOME/Documents/Hermes/scripts/backup-hermes.log"
CLOUD="$HOME/Nutstore/1/我的坚果云/Hermes备份"

echo "===== Hermes 备份 $TIMESTAMP =====" | tee -a "$LOG_FILE"

SRC_HERMES=$(cygpath -w "$HOME/.hermes")
DST_HERMES=$(cygpath -w "$CLOUD/.hermes")

echo "[1/2] 同步 ~/.hermes/ ..." | tee -a "$LOG_FILE"
robocopy "$SRC_HERMES" "$DST_HERMES" \
  /MIR /NP /NDL /NFL /R:2 /W:3 \
  /XD logs cache __pycache__ .git \
  /XF "*.log" "*.tmp" "*.lock" > /dev/null
RC=$?
if [ $RC -le 7 ]; then
  echo "  完成 (rc=$RC)" | tee -a "$LOG_FILE"
else
  echo "  失败 (rc=$RC)" | tee -a "$LOG_FILE"
fi

echo "[2/2] 同步 state.db ..." | tee -a "$LOG_FILE"
mkdir -p "$CLOUD/AppData"
cp "$HOME/AppData/Local/hermes/state.db" "$CLOUD/AppData/state.db" 2>/dev/null || true
echo "  完成" | tee -a "$LOG_FILE"

FILES=$(find "$CLOUD/.hermes" -type f 2>/dev/null | wc -l)
echo "  ${FILES} 个文件 → $CLOUD" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
