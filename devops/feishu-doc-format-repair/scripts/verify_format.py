# -*- coding: utf-8 -*-
"""飞书文档格式修复后的健壮验证脚本（嵌套标签安全）

用法：
    python verify_format.py <fetch_json> [baseline_json]

- fetch_json: lark-cli docs +fetch --detail with-ids 输出的 JSON 文件
- baseline_json: 修复前拉取的基线 JSON（可选，提供则做内容零改动对比）

检查项：
    1. 标题层级统计（h1-h4）
    2. 嵌套安全扫描所有标题块（不会因 <b> 等嵌套标签漏检）
    3. 场次标题是否残留为标题块（应为加粗段落）
    4. 前导空格 / 纯空格空段
    5. 内容零改动（与基线纯文本逐字符对比）
"""
import json
import re
import sys


def load_content(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d["data"]["document"]["content"]


def pure_text(xml: str) -> str:
    """剥离所有标签和空白，用于内容对比。"""
    return re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", xml))


def scan_titles(xml: str):
    """嵌套安全扫描所有标题块。返回 [(level, text), ...]"""
    titles = []
    for m in re.finditer(r"<(h[1-4])([^>]*)>(.*?)</\1>", xml, re.S):
        text = re.sub(r"<[^>]+>", "", m.group(3)).strip()
        titles.append((m.group(1), text))
    return titles


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    xml = load_content(sys.argv[1])

    print("=== 1. 标题层级统计 ===")
    titles = scan_titles(xml)
    from collections import Counter
    hc = Counter(h for h, _ in titles)
    print(f"h1={hc.get('h1', 0)} h2={hc.get('h2', 0)} h3={hc.get('h3', 0)} h4={hc.get('h4', 0)}")

    print("\n=== 2. 全部标题块（嵌套安全） ===")
    for h, t in titles:
        print(f"  <{h}> {t[:50]}")

    print("\n=== 3. 场次标题残留检查（应无标题化场次） ===")
    bad = [(h, t) for h, t in titles if re.search(r"\d+-\d+", t)]
    print("  残留:", bad if bad else "无 ✓")

    print("\n=== 4. 空格垃圾 ===")
    lead = len(re.findall(r'<p[^>]*id="[^"]+"[^>]*>\s{2,}\S', xml))
    blank = len(re.findall(r"<p[^>]*>\s{4,}</p>", xml))
    print(f"  前导空格段落: {lead}  纯空格空段: {blank}")

    if len(sys.argv) > 2:
        print("\n=== 5. 内容零改动对比 ===")
        base = pure_text(load_content(sys.argv[2]))
        cur = pure_text(xml)
        if base == cur:
            print(f"  ✓ 完全一致（{len(cur)} 字符）")
        else:
            for i, (a, b) in enumerate(zip(base, cur)):
                if a != b:
                    print(f"  ✗ 首个差异 @{i}: 新={cur[max(0,i-15):i+15]!r} 旧={base[max(0,i-15):i+15]!r}")
                    break


if __name__ == "__main__":
    main()
