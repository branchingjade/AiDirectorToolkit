#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
docx → markdown 转换器，用于把 docx 内容倒入飞书文档。

核心要点：python-docx 的 `d.paragraphs` 不包含表格（表格在 `d.tables`），
但飞书文档渲染需要段落和表格交错——必须按 `body.iterchildren()` 顺序遍历。

用法：
    python docx_to_feishu_markdown.py --input <docx> --output <md>
    python docx_to_feishu_markdown.py --input <docx> --output <md> --title "自定义标题"
"""

import argparse
import sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="docx → markdown (保表格顺序)")
    p.add_argument("--input", required=True, help="输入 docx 路径")
    p.add_argument("--output", required=True, help="输出 markdown 路径")
    p.add_argument("--title", default=None, help="可选：自定义一级标题（默认用首个 H1 段落）")
    return p.parse_args()


def docx_to_markdown(docx_path: str, custom_title: str = None) -> str:
    from docx import Document

    d = Document(docx_path)
    body = d.element.body

    # 索引映射
    para_map = {id(p._element): p for p in d.paragraphs}
    table_map = {id(t._element): t for t in d.tables}

    lines = []

    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]

        if tag == "p":
            p = para_map.get(id(child))
            if p is None:
                continue
            text = p.text
            if not text.strip():
                continue
            sz = None
            bold = False
            for run in p.runs:
                if run.font.size:
                    sz = run.font.size.pt
                if run.font.bold:
                    bold = True
            if sz is None:
                sz = 10.5

            # 标题判级（按字号 + 加粗）
            if bold and sz >= 20:
                lines.append(f"# {text}")
            elif bold and sz >= 15:
                lines.append(f"## {text}")
            elif bold and sz >= 12:
                lines.append(f"### {text}")
            # Seedance 提示词代码块（等宽字体小块）启发式
            elif sz <= 10 and ("竖构图" in text or "剑身斜入" in text or "剑身居中" in text):
                lines.append("```")
                lines.append(text)
                lines.append("```")
            else:
                lines.append(text)

        elif tag == "tbl":
            t = table_map.get(id(child))
            if t is None:
                continue
            rows_data = []
            for row in t.rows:
                cells = [cell.text.replace("\n", " ").replace("|", "\\|") for cell in row.cells]
                rows_data.append(cells)
            if not rows_data:
                continue
            header = rows_data[0]
            lines.append("")
            lines.append("| " + " | ".join(header) + " |")
            lines.append("| " + " | ".join(["---"] * len(header)) + " |")
            for r in rows_data[1:]:
                lines.append("| " + " | ".join(r) + " |")
            lines.append("")

    md = "\n".join(lines)

    if custom_title:
        # 把第一个 H1 换成自定义
        if md.startswith("# "):
            md = f"# {custom_title}\n" + md.split("\n", 1)[1]

    return md


def main():
    args = parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        print(f"❌ 输入文件不存在: {in_path}", file=sys.stderr)
        sys.exit(1)

    md = docx_to_markdown(str(in_path), custom_title=args.title)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")

    table_count = md.count("| ---")
    char_count = len(md)
    print(f"✅ 已生成: {out_path}")
    print(f"   字符数: {char_count}, 表格数: {table_count}")


if __name__ == "__main__":
    main()