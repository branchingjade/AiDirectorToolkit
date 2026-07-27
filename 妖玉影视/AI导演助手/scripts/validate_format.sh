#!/bin/bash
# v12.0.0 分镜格式校验脚本
# 用法: bash validate_format.sh <分镜产出目录>
# 输出: 逐文件检查结果，有违规则报错
# 检查项: Seedance约束 + 段级资产锁 + 描述行规范

DIR="${1:-.}"
FAIL=0
FILES=$(ls "$DIR"/EP*.md 2>/dev/null | sort)

if [ -z "$FILES" ]; then
  echo "错误: $DIR 中未找到EP*.md文件"
  exit 1
fi

echo "=== v12.0.0 格式校验 ==="
echo "目录: $DIR"
echo "文件数: $(echo "$FILES" | wc -l)"
echo ""

for f in $FILES; do
  name=$(basename "$f")
  issues=""

  # 1. 精确秒数（如 3s 0.8s 4.0s）— Seedance约束
  seconds=$(grep -nP '(?<![~>])\b[0-9]+\.[0-9]+s\b' "$f")
  if [ -n "$seconds" ]; then
    issues="$issues\n  [1] 精确秒数残留"
  fi

  # 2. 表格分镜（| 镜号 | 开头）— Seedance约束
  tables=$(grep -nP '^\| 镜号' "$f")
  if [ -n "$tables" ]; then
    issues="$issues\n  [2] 表格分镜"
  fi

  # 3. 段级资产锁（整体风格：）
  asset_lock=$(grep -c '整体风格：' "$f")
  if [ "$asset_lock" -eq 0 ]; then
    issues="$issues\n  [3] 缺少段级资产锁(整体风格)"
  fi

  # 4. 描述行中的@Tag（@中文名）
  at_in_desc=$(grep -nP '(?<!：)(?<!：\S)@[一-龥]+' "$f" | grep -v '整体风格：\|人物：\|场景：\|道具：\|音色：\|配音：\|角色：\|画幅：')
  if [ -n "$at_in_desc" ]; then
    issues="$issues\n  [4] 描述行含@Tag"
  fi

  # 5. 描述行中的资产代码（大写字母+连字符+数字，如 CQ-01）
  code_in_desc=$(grep -nP '\b[A-Z]{2,4}-[0-9]+\b' "$f" | grep -v '整体风格：\|人物：\|场景：\|道具：\|音色：\|配音：\|角色：\|画幅：')
  if [ -n "$code_in_desc" ]; then
    issues="$issues\n  [5] 描述行含资产代码"
  fi

  # 6. 独立焦点转移行（旧格式）
  focus_line=$(grep -nP '^焦点转移：' "$f")
  if [ -n "$focus_line" ]; then
    issues="$issues\n  [6] 独立焦点转移行(应融入描述行)"
  fi

  # 7. [音效: xxx]标签（旧格式）
  sfx_tag=$(grep -nP '\[音效[:：]' "$f")
  if [ -n "$sfx_tag" ]; then
    issues="$issues\n  [7] [音效:]标签(应自然融入)"
  fi

  # 8. 独立配置行（旧格式: 景别 | 运镜 | 日夜）
  config_line=$(grep -nP '^[^\s]+\s\|\s[^\s]+\s\|\s[^\s]+$' "$f" | grep -v '画幅：\|整体风格：\|人物：\|场景：\|道具：\|音色：\|配音：\|角色：')
  if [ -n "$config_line" ]; then
    issues="$issues\n  [8] 独立配置行(应融入描述行)"
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
