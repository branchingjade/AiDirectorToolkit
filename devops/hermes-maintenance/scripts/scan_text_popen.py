#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描 hermes-agent 源码里 text=True 但缺 errors= 的 subprocess 调用点。

用途：排查 Windows zh-CN 下 subprocess 编码错配（子进程输出 GBK 被 UTF-8 读，
reader 线程抛 UnicodeDecodeError —— 参见 hermes-maintenance skill
「Diagnostic: tui_gateway_crash.log 被编码噪音刷屏」章节）。

text=True / universal_newlines=True 的 Popen/run 若没有 errors= 参数，
子进程输出非 UTF-8 时 stdout reader 线程会抛异常（丢输出 / 污染 crash log）。
errors="replace" 语义无损（UTF-8 输出不受影响），漏网点应统一补上。

用法：
    python scan_text_popen.py                 # 默认扫 hermes-agent 源码
    python scan_text_popen.py --root <路径>   # 扫指定目录
    python scan_text_popen.py --quiet         # 只输出漏网点清单

2026-08-08 实测：hermes-agent 全库 28 处漏网（tui_gateway/ 下已全部安全——
server.py:377、host_supervisor.py:326、tools/environments/local.py:1532
都带 errors="replace"，是 2026-08-07 上游 #52649 修复）。
"""
import argparse
import os
import re
import sys

DEFAULT_ROOT = r"C:\Users\HMSJ\AppData\Local\hermes\hermes-agent"
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".hermes-runtime",
    "dist", "build", "release", "venv", ".venv", "tests", "test",
}


def scan(root: str) -> list[tuple[str, int, str]]:
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                with open(fp, encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
            except Exception:
                continue
            for i, ln in enumerate(lines):
                m = re.search(r"(?:subprocess\.(?:Popen|run|check_output|call)|(?:^|\s)Popen)\(", ln)
                if not m:
                    continue
                # 收集调用块（简单括号配对，字符串内括号的极端情况不影响本扫描目的）
                depth = 0
                block = ""
                j = i
                while j < len(lines) and j - i <= 25:
                    block += lines[j]
                    depth += lines[j].count("(") - lines[j].count(")")
                    j += 1
                    if depth <= 0 and j > i:
                        break
                if "text=True" not in block and "universal_newlines=True" not in block:
                    continue
                if re.search(r"errors\s*=", block):
                    continue
                rel = os.path.relpath(fp, root).replace("\\", "/")
                results.append((rel, i + 1, ln.strip()[:70]))
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=DEFAULT_ROOT, help="扫描根目录（默认 hermes-agent 源码）")
    ap.add_argument("--quiet", action="store_true", help="只输出漏网点清单")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"✗ 目录不存在: {args.root}")
        return 1

    results = scan(args.root)
    if not args.quiet:
        print(f"扫描目录: {args.root}")
        print(f"text 模式但缺 errors= 的调用点: {len(results)} 处\n")
    for rel, lineno, snippet in results:
        print(f"{rel}:{lineno}: {snippet}")
    if not args.quiet and results:
        print("\n修法：每个调用点补 errors=\"replace\"（语义无损，UTF-8 输出不受影响）。")
        print("注意：已带 errors= 的调用点不会出现在此清单——出现在清单里才需要修。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
