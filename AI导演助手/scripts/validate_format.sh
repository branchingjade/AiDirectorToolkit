#!/bin/bash
# v9.0.0 分镜格式校验脚本
# 用法: bash validate_format.sh <分镜产出目录>
# 输出: 逐文件8项检查结果，有违规则报错

DIR="${1:-.}"
FAIL=0
FILES=$(ls "$DIR"/EP*.md 2>/dev/null | sort)

if [ -z "$FILES" ]; then
  echo "错误: $DIR 中未找到EP*.md文件"
  exit 1
fi

echo "=== v9.0.0 格式校验 ==="
echo "目录: $DIR"
echo "文件数: $(echo "$FILES" | wc -l)"
echo ""

for f in $FILES; do
  name=$(basename "$f")
  issues=""

  # 1. 配置行仅3字段（景别 | 运镜 | 日夜），无秒数/场景/资产
  # 匹配不规范配置行：含4个或更多 | 分隔符，或含秒数
  bad_config=$(grep -nP '^\S+ \| \S+ \| \S+ \| \S+' "$f" | grep -v '^\s*[0-9]*:\s*画幅：')
  if [ -n "$bad_config" ]; then
    issues="$issues\n  [1] 配置行>3字段"
  fi

  # 2. 精确秒数（如 3s 0.8s 4.0s）
  seconds=$(grep -nP '(?<![~>])\b[0-9]+\.[0-9]+s\b' "$f")
  if [ -n "$seconds" ]; then
    issues="$issues\n  [2] 精确秒数残留"
  fi

  # 3. 表格分镜（| 镜号 | 开头）
  tables=$(grep -nP '^\| 镜号' "$f")
  if [ -n "$tables" ]; then
    issues="$issues\n  [3] 表格分镜"
  fi

  # 4. 描述/配置前缀（旧格式）
  old_prefix=$(grep -nP '^配置：|^描述：' "$f")
  if [ -n "$old_prefix" ]; then
    issues="$issues\n  [4] 配置/描述前缀"
  fi

  # 5. 镜分标题（### 镜X）
  sub_headers=$(grep -nP '^### 镜\d' "$f")
  if [ -n "$sub_headers" ]; then
    issues="$issues\n  [5] ### 镜分标题"
  fi

  # 6. 段级资产锁（整体风格：）
  asset_lock=$(grep -c '整体风格：' "$f")
  if [ "$asset_lock" -eq 0 ]; then
    issues="$issues\n  [6] 缺少段级资产锁(整体风格)"
  fi

  # 7. 描述行中的@Tag（通用匹配：6空格缩进后的行中含 @中文名）
  at_in_desc=$(grep -nP '^\s{6}.*@[一-龥]+' "$f")
  if [ -n "$at_in_desc" ]; then
    issues="$issues\n  [7] 描述行含@Tag"
  fi
  # 8. 描述行中的资产代码（通用匹配：大写字母+连字符+数字，如 CQ-01）
  code_in_desc=$(grep -nP '^\s{6}.*\b[A-Z]{2,4}-[0-9]+\b' "$f")
  if [ -n "$code_in_desc" ]; then
    issues="$issues\n  [8] 描述行含资产代码"
  fi

  if [ -z "$issues" ]; then
    echo "✅ $name"
  else
    echo "❌ $name$issues"
    FAIL=$((FAIL + 1))
  fi
done

echo ""
echo "=== 结果: $FAIL/$(echo "$FILES" | wc -l | tr -d ' ') 文件违规 ==="
exit $FAIL
