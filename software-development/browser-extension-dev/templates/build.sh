#!/bin/bash
# 浏览器扩展构建脚本模板
# 将 src/ 下的模块按依赖顺序拼接为 dist/content.js

set -e
SRC="src" && DIST="dist"

echo "==> 构建 content.js..."
cat "$SRC/modules/config.js" \
    "$SRC/modules/algorithm.js" \
    "$SRC/modules/feature-a.js" \
    "$SRC/modules/feature-b.js" \
    "$SRC/modules/main.js" \
    > "$DIST/content.js"
echo "   content.js ($(wc -c < "$DIST/content.js") bytes)"

echo "==> 复制静态文件..."
cp "$SRC/bridge.js"          "$DIST/"
cp "$SRC/manifest.json"      "$DIST/"
cp "$SRC/popup.html"         "$DIST/"
cp "$SRC/popup.css"          "$DIST/"
cp "$SRC/popup.js"           "$DIST/"
cp "$SRC/content-styles.css" "$DIST/"
mkdir -p "$DIST/icons" && cp "$SRC/icons"/* "$DIST/icons/" 2>/dev/null || true

echo ""
echo "✅ 构建完成 — 加载 dist/ 到 Chrome 即可"
