"""Hermes 插件 Tailwind 类存在性审计。

用途：Hermes 桌面 app 用 Tailwind v4 编译期扫描自己的源码生成 CSS，插件在
构建图之外——插件 JS 里的 className 若 app 源码没用过就没有对应 CSS，UI
静默破损（无报错）。写/改 Hermes 桌面插件后跑本脚本，缺失=0 才安全。

用法：
    python audit_classes.py <plugin.js路径> [<distCSS路径或目录>]
    不传 dist 时自动探测 LOCALAPPDATA\\hermes\\hermes-agent\\apps\\desktop\\dist\\assets

输出：缺失类列表；无输出行=全部存在。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def find_dist_css() -> list[str]:
    candidates = [
        Path(r"%LOCALAPPDATA%" % {"LOCALAPPDATA": ""}).parent,  # 占位，实际用下方探测
    ]
    del candidates
    # 优先环境变量，其次常见安装路径
    import os

    paths = []
    la = os.environ.get("LOCALAPPDATA", "")
    if la:
        paths.append(Path(la) / "hermes" / "hermes-agent" / "apps" / "desktop" / "dist" / "assets")
    home = Path.home()
    paths.append(home / ".hermes" / "hermes-agent" / "apps" / "desktop" / "dist" / "assets")
    for p in paths:
        if p.is_dir():
            return sorted(str(f) for f in p.glob("index-*.css"))
    return []


def tailwind_escape(body: str) -> str:
    """类主体 → CSS 选择器转义形式（Tailwind 产物：. 转 \. 等）。"""
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


def audit(plugin_js: str, css_texts: list[str]) -> list[str]:
    css = "\n".join(css_texts)
    src = Path(plugin_js).read_text(encoding="utf-8")
    classes: set[str] = set()
    for m in re.finditer(r"className:\s*'([^']+)'", src):
        for part in m.group(1).split():
            if not part.startswith("'"):
                classes.add(part)
    missing = []
    for c in sorted(classes):
        body = c.split(":")[-1]  # hover:bg-x → bg-x；group-hover:x → x
        if ("." + tailwind_escape(body)) not in css:
            missing.append(c)
    return missing


def main() -> int:
    args = sys.argv[1:]
    plugin = args[0] if args else r"~\AppData\Local\hermes\desktop-plugins\channel-sessions\plugin.js"
    plugin = str(Path(plugin).expanduser())
    css_files: list[str] = []
    if len(args) > 1:
        p = Path(args[1])
        css_files = [str(p)] if p.is_file() else sorted(str(f) for f in p.glob("index-*.css"))
    else:
        css_files = find_dist_css()
    if not css_files:
        print("⚠️ 未找到编译 CSS（dist），跳过审计。指定路径：python audit_classes.py plugin.js /path/to/dist")
        return 0
    css_texts = [Path(f).read_text(encoding="utf-8", errors="replace") for f in css_files]
    missing = audit(plugin, css_texts)
    if missing:
        print(f"❌ 缺失 CSS 类（{len(missing)}）:")
        for c in missing:
            print(f"   {c}")
        return 1
    print("✅ 全部类存在于编译 CSS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
