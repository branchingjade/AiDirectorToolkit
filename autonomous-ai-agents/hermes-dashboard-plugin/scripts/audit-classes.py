#!/usr/bin/env python3
"""Hermes dashboard 插件 Tailwind 类审计（2026-08-10 本机实战沉淀）。

背景：web_dist 编译产物只含 web 源码用过的类——插件 JS 的 className 只要
web/src 没用过就没编译，UI 不报错但布局静默全乱（w-52 渲染成 2091px 实例）。
本脚本提取插件 JSX/JS 里全部 className，对照 web_dist CSS 查缺失。

用法：
    python audit-classes.py <插件JS或JSX路径> [web_dist_assets_dir] [插件style.css]

- web_dist_assets_dir 默认 C:\\Users\\HMSJ\\AppData\\Local\\hermes\\hermes-agent\\hermes_cli\\web_dist\\assets
- 传插件 dist/style.css 时，已在该 CSS 中定义的类不算缺失（CSS 选择器的 \\ 转义会自动处理）
缺失类处理：加进插件 dist/style.css（manifest 需 "css": "dist/style.css"）或改内联 style。
"""
import re
import sys
from pathlib import Path

DEFAULT_CSS_DIR = Path(
    r"C:\Users\HMSJ\AppData\Local\hermes\hermes-agent\hermes_cli\web_dist\assets"
)


def extract_classes(src: str) -> set:
    """提取 className=\"...\" 与 cn(\"...\", ...) 里的全部类名。"""
    classes: set = set()
    for m in re.findall(r'className:\s*"([^"]+)"', src):
        classes.update(m.split())
    for m in re.findall(r'cn\(\s*"([^"]+)"', src):
        classes.update(m.split())
    for m in re.findall(r'className:\s*cn\(([^)]*)\)', src):
        for lit in re.findall(r'"([^"]+)"', m):
            classes.update(lit.split())
    return classes


def escape_css_selector(cls: str) -> str:
    """Tailwind 类名转 CSS 选择器（转义 [ ] . / :；变体前缀如 hover: 只查主体）。"""
    body = cls.split(":")[-1]
    return (
        body.replace("[", r"\[")
        .replace("]", r"\]")
        .replace(".", r"\.")
        .replace("/", r"\/")
    )


def audit(js_path: str, css_dir: Path = DEFAULT_CSS_DIR, patch_css: str | None = None) -> list:
    src = Path(js_path).read_text(encoding="utf-8")
    classes = extract_classes(src)
    css_text = ""
    for f in css_dir.glob("*.css"):
        css_text += f.read_text(encoding="utf-8", errors="replace")

    # 插件自带 style.css 已补的类不算缺失（CSS 选择器里的 \ 转义要去掉再匹配；
    # 注意用完整类名 c 而非 escape_css_selector(c)——后者剥变体前缀，xl:grid-cols-3
    # 会错剥成 grid-cols-3 导致 style.css 的 .xl\:grid-cols-3 匹配不上）
    patch_covered: set = set()
    if patch_css:
        pc = Path(patch_css)
        if pc.exists():
            ptext = pc.read_text(encoding="utf-8").replace("\\", "")
            for c in classes:
                full_esc = (
                    c.replace("[", r"\[")
                    .replace("]", r"\]")
                    .replace(".", r"\.")
                    .replace("/", r"\/")
                    .replace(":", r"\:")
                )
                if re.search(r"\.%s(?![a-zA-Z0-9_-])" % full_esc, ptext):
                    patch_covered.add(c)

    missing = []
    for c in sorted(classes):
        esc = escape_css_selector(c)
        if c in patch_covered:
            continue
        if not re.search(r"\.%s(?![a-zA-Z0-9_-])" % esc, css_text):
            missing.append(c)

    covered = f", style.css 已补 {len(patch_covered)}" if patch_css else ""
    print(f"=== {Path(js_path).name}: 共 {len(classes)} 类, 缺失 {len(missing)}{covered} ===")
    for m in missing:
        print("  MISSING:", m)
    return missing


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    css_dir = Path(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else DEFAULT_CSS_DIR
    patch_css = sys.argv[3] if len(sys.argv) > 3 else None
    missing = audit(sys.argv[1], css_dir, patch_css)
    sys.exit(1 if missing else 0)
