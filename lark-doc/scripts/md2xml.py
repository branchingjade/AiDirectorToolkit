#!/usr/bin/env python3
"""Markdown → 飞书文档 XML 转换器。

把本地 Markdown 文件（Obsidian 笔记、大纲、剧本等）转成 lark-cli docs +create 可用的
XML 内容。支持：标题层级(h1-h6)、表格、无序/有序列表、引用块、代码块、加粗、行内代码。

用法:
    python3 md2xml.py input.md                 # 输出 XML 到 stdout
    python3 md2xml.py input.md -o output.xml   # 写入文件

转换后创建文档:
    lark-cli --as bot docs +create --content @output.xml

注意:
- frontmatter（--- 之间的 YAML）自动跳过
- 表格必须带表头行（| 分隔），转换后为 table>thead+tbody
- 列表项每个转成独立 <ul><li>（lark-cli 会合并连续列表）
- 有序列表用 <ol><li seq="auto"> 自动编号
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def inline(s: str) -> str:
    """行内样式：**bold** -> <b>，`code` -> <code>"""
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def md2xml(md: str) -> str:
    # 去掉 YAML frontmatter
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    in_table = False

    while i < len(lines):
        line = lines[i]

        # 表格行
        if line.strip().startswith("|"):
            if re.match(r"^\|[\s:\-|]+\|$", line):  # 表头分隔行
                i += 1
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                out.append(
                    "<table><thead><tr>"
                    + "".join(f"<th>{inline(c)}</th>" for c in cells)
                    + "</tr></thead><tbody>"
                )
                in_table = True
            else:
                out.append(
                    "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>"
                )
            i += 1
            if i < len(lines) and not lines[i].strip().startswith("|"):
                out.append("</tbody></table>")
                in_table = False
            continue
        if in_table:
            out.append("</tbody></table>")
            in_table = False

        s = line.strip()
        if not s:
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)", s)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        # 无序列表
        if re.match(r"^[-*]\s+", s):
            item = re.sub(r"^[-*]\s+", "", s)
            out.append(f"<ul><li>{inline(item)}</li></ul>")
            i += 1
            continue

        # 有序列表
        if re.match(r"^\d+\.\s+", s):
            item = re.sub(r"^\d+\.\s+", "", s)
            out.append(f'<ol><li seq="auto">{inline(item)}</li></ol>')
            i += 1
            continue

        # 引用块
        if s.startswith(">"):
            out.append(f"<blockquote>{inline(s.lstrip('> '))}</blockquote>")
            i += 1
            continue

        # 代码块围栏
        if s.startswith("```"):
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            code_text = "\n".join(code)
            out.append(f'<pre lang="text"><code>{code_text}</code></pre>')
            continue

        # 普通段落
        out.append(f"<p>{inline(s)}</p>")
        i += 1

    return "".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Markdown → 飞书 XML")
    parser.add_argument("input", help="输入 .md 文件路径")
    parser.add_argument("-o", "--output", help="输出 XML 文件路径（默认 stdout）")
    args = parser.parse_args()

    md = Path(args.input).read_text(encoding="utf-8")
    xml = md2xml(md)
    if args.output:
        Path(args.output).write_text(xml, encoding="utf-8")
        print(f"已写入 {args.output}，XML 长度: {len(xml)}")
    else:
        print(xml)


if __name__ == "__main__":
    main()
