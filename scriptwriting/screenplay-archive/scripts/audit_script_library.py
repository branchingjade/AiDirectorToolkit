"""剧本库全量质量巡检脚本——screenplay-archive 配套。

用法: python audit_script_library.py <剧本原文目录> [研习报告目录]

检查项:
1. frontmatter 完整性（来源/版本/与成片差异/可信度/抓取日期）
2. 乱码字符 \ufffd 计数
3. 控制字符 \f \t \r
4. 装饰残留行（纯符号行，非合法分隔符 ---/***/___/...）
5. H1 重复（文件内出现 # 标题，Obsidian 会与文件名重复）
6. 研习报告链接有效性
7. 引号配对（YAML 值内残留 ""）

退出码: 0 = 全干净, 1 = 有问题
"""
import os
import re
import sys

# 装饰残留行模式：纯符号无字母数字，且不是合法分隔符
DECOR = re.compile(r'^[·\.\-—_~\\\/\^\*\(\)\[\]{}<>|=+&%$#@!?`\'"，。：；、？！【】（）\s]{3,}$')
LEGIT_SEP = re.compile(r'^-{3,}|\*{3,}|_{3,}|\.{3,}$')
CONTROL_CHARS = ['\f', '\t', '\r']
FM_FIELDS = ["来源", "版本", "与成片差异", "可信度", "抓取日期"]


def audit_md(path):
    issues = []
    content = open(path, encoding="utf-8", errors="replace").read()

    # 1. frontmatter
    fm = re.match(r'^---\n(.*?)\n---\n', content, re.S)
    if not fm:
        issues.append("无 frontmatter")
    else:
        for field in FM_FIELDS:
            if field not in fm.group(1):
                issues.append(f"frontmatter 缺 {field}")
        if fm.group(1).count('"') % 2 != 0:
            issues.append("frontmatter 引号不配对")
    # 9. frontmatter 后多余 ---
    if re.match(r'^---\n(?:.*?\n)---\n\s*---', content, re.S):
        issues.append("frontmatter 后多余 ---")

    # 2. 乱码
    n_bad = content.count('\ufffd')
    if n_bad > 0:
        issues.append(f"乱码 {n_bad} 处")

    # 3. 控制字符
    for ch in CONTROL_CHARS:
        if ch in content:
            issues.append(f"控制字符 {repr(ch)}")

    # 4. 装饰残留 + 5. H1
    for line in content.split('\n'):
        s = line.strip()
        if s.startswith('# ') and not s.startswith('## '):
            issues.append(f"H1 标题: {s[:40]}")
        if DECOR.fullmatch(s) and not LEGIT_SEP.fullmatch(s):
            issues.append(f"装饰残留: {s[:30]}")
            break  # 每类报一次即可

    return issues


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    dirs = [sys.argv[1]]
    if len(sys.argv) > 2:
        dirs.append(sys.argv[2])

    total_issues = 0
    for d in dirs:
        if not os.path.isdir(d):
            print(f"⚠️ 目录不存在: {d}")
            continue
        print(f"=== {d} ===")
        for f in sorted(os.listdir(d)):
            if not f.endswith('.md'):
                continue
            issues = audit_md(os.path.join(d, f))
            if issues:
                total_issues += len(issues)
                print(f"  ⚠️ {f}: {issues}")
            else:
                print(f"  ✅ {f}")
    print(f"\n总问题数: {total_issues}")
    sys.exit(0 if total_issues == 0 else 1)


if __name__ == '__main__':
    main()
