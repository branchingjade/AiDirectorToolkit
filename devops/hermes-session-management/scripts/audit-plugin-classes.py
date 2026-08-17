#!/usr/bin/env python3
"""Hermes 桌面插件 className 审计：核对插件用的 Tailwind 类是否存在于 app 编译 CSS。

背景：Hermes 桌面 app 的 CSS 是构建时从自己的源码编译的（Tailwind v4），插件文件在构建图
之外——插件里写到的 className 若 app 源码没用过，编译产物里就没有对应 CSS，UI 会静默破损
（透明背景/字号失效），且 selfcheck 与 node --check 都查不出。

用法：
    python audit-plugin-classes.py <plugin.js> [<dist-css-glob>]

默认 dist glob: %LOCALAPPDATA%/hermes/hermes-agent/apps/desktop/dist/assets/*.css
退出码：0 = 全部类存在；1 = 有缺失（stdout 列出缺失类）。
"""
import glob
import os
import re
import sys


def escape_css_class(body: str) -> str:
    """Tailwind 编译产物的类名转义：'[', ']', '(', ')', '/', '.', ':' 前加反斜杠。"""
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


def collect_classes(source: str) -> set:
    classes = set()
    for m in re.finditer(r"className:\s*'([^']+)'", source):
        for part in m.group(1).split():
            if part and not part.startswith("'"):
                classes.add(part)
    return classes


def load_css(glob_pattern: str) -> str:
    files = sorted(glob.glob(glob_pattern))
    if not files:
        print(f"⚠️ 未找到编译 CSS: {glob_pattern}", file=sys.stderr)
        return ""
    chunks = []
    for f in files:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                chunks.append(fh.read())
        except OSError as exc:
            print(f"⚠️ 读取失败 {f}: {exc}", file=sys.stderr)
    return "\n".join(chunks)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    plugin_path = sys.argv[1]
    css_glob = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "hermes", "hermes-agent", "apps", "desktop", "dist", "assets", "*.css",
    )
    try:
        with open(plugin_path, encoding="utf-8") as fh:
            source = fh.read()
    except OSError as exc:
        print(f"❌ 读取插件失败: {exc}", file=sys.stderr)
        return 2

    css = load_css(css_glob)
    classes = collect_classes(source)
    if not css:
        # 拿不到 CSS 时没法审计——不当作通过，也不当作失败，给提示
        print(f"共 {len(classes)} 个类；⚠️ 编译 CSS 为空，跳过存在性核对")
        return 0

    missing = []
    for c in sorted(classes):
        body = c.split(":")[-1]  # hover:bg-x → bg-x；group-hover:x → x
        if ("." + escape_css_class(body)) not in css:
            missing.append(c)

    print(f"共 {len(classes)} 个类片段，缺失 {len(missing)} 个")
    for c in missing:
        print(f"  MISSING: {c}")
    if missing:
        print("提示：替换为编译产物中存在的等价类（见 references/plugin-frontend-pitfalls.md）")
        return 1
    print("✅ 全部类均存在于 Hermes 编译 CSS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
