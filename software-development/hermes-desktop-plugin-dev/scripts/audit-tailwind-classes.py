#!/usr/bin/env python3
"""审计 Hermes 桌面插件 className 是否存在于编译 CSS 产物。

背景：Hermes 桌面 app 的 CSS 是 Tailwind v4 从 app 自身源码编译的，插件目录在
构建图之外——插件 JS 里写的 className，只要 app 源码没用过就没有对应 CSS，
UI 静默破损（透明背景/字号失效/布局坏），不报任何错。2026-08-09 channel-sessions
v1.4.2 根因级教训：--ui-fill-* 变量不存在、text-[10.5px]/[12.5px]/[13px]、
w-[380px]、max-w-24、space-y-3.5、bg-x/50 /60 变体全部缺失。

用法：
    python audit-tailwind-classes.py <plugin.js> [<dist-css-dir>]

    <plugin.js>    插件前端文件（必填）
    <dist-css-dir> Hermes dist assets 目录（可选，默认
                   %LOCALAPPDATA%\\hermes\\hermes-agent\\apps\\desktop\\dist\\assets）
                   目录里匹配 index-*.css 的全部文件都会纳入。

退出码 0 = 全部类存在；1 = 有缺失（打印缺失列表）。
也可直接 import 本文件调用 audit(plugin_path, css_dir) -> (total, missing)。

转义规则（Tailwind 产物形式）：[ → \[ , ] → \] , ( → \( , ) → \)
/ → \/ , . → \. , : → \: ，变体前缀（hover:bg-x）只取冒号后主体。
"""
import re
import sys
from pathlib import Path

DEFAULT_CSS_DIR = (
    Path(__import__("os").environ.get("LOCALAPPDATA", ""))
    / "hermes" / "hermes-agent" / "apps" / "desktop" / "dist" / "assets"
)


def _escaped(body: str) -> str:
    return (
        body.replace("\\", "\\\\")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("/", "\\/")
        .replace(".", "\\.")
        .replace(":", "\\:")
    )


def audit(plugin_path: str | Path, css_dir: str | Path | None = None) -> tuple[int, list[str]]:
    css_dir = Path(css_dir or DEFAULT_CSS_DIR)
    src = Path(plugin_path).read_text(encoding="utf-8")
    css = "".join(
        f.read_text(encoding="utf-8", errors="replace")
        for f in sorted(css_dir.glob("index-*.css"))
    )

    classes: set[str] = set()
    for m in re.finditer(r"className:\s*'([^']+)'", src):
        for part in m.group(1).split():
            if not part.startswith("'"):
                classes.add(part)

    missing: list[str] = []
    for c in sorted(classes):
        body = c.split(":")[-1]  # hover:bg-x → bg-x；group-hover:x → x
        if ("." + _escaped(body)) not in css:
            missing.append(c)
    return len(classes), missing


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    plugin = sys.argv[1]
    css_dir = sys.argv[2] if len(sys.argv) > 2 else None
    total, missing = audit(plugin, css_dir)
    print(f"总类片段: {total}, 缺失: {len(missing)}")
    for c in missing:
        print("  MISSING:", c)
    if missing:
        # 常见修复映射
        print("\n常见缺失类 → 替换（编译产物验证过存在）：")
        print("  --ui-fill-*        → --ui-bg-*（app 只有 --ui-bg 系列）")
        print("  text-[10.5px]      → text-[10px] 或 text-[11px]")
        print("  text-[12.5px]      → text-xs (12px)")
        print("  text-[13px]        → text-sm (14px)")
        print("  w-[380px]          → w-80 (320px)")
        print("  max-w-24           → max-w-60")
        print("  min-h-[30px]       → min-h-7")
        print("  space-y-3.5        → space-y-3")
        print("  bg-x/50, bg-x/60   → /40（app 只编译过 /40）")
        sys.exit(1)
    sys.exit(0)
