#!/usr/bin/env python3
"""研习文档引文校验脚本（0 MISS 门禁）——batch-film-research-ingestion 配套。

用法:
    python verify_quotes.py <草稿.md> [<草稿2.md> ...] [--pages DIR]

行为:
  1. 从草稿提取引文: 英文双引号 "..." (>=25 字符, 跳过 URL/代码), 中文「」 (>=15 字符)
  2. 对 pages/ 目录全部存档(*.txt/*.md) 做规范化匹配(压空白/小写/去弯引号/去撇号)
  3. 英文用 4 词滑动窗口、中文用 12 字符滑动窗口匹配——
     容忍 wiki 标记 [[链接]]、斜体 ''..''、&nbsp; 实体打断短语（假 MISS 高频源）
  4. 自动跳过 "AI 提示词示例" 段落（创作建议, 非引文）
  5. 输出每条引文的命中文件 + PASS/MISS 汇总

MISS 分类先行（不要见 MISS 就改稿）:
  - 译文: 中文「」译文不在存档是正常的, 核对对应英文原文已 PASS 即可
  - AI 提示词示例: 创作建议, 非引文, 不修
  - 维基标记假 MISS: 换更短的 3-4 词短语复核
  - 真错: 才修改草稿（如引文与原档措辞不符、简繁混用）

蓝丝绒轮实测: 95 条短语抽查 17 MISS 全为 wiki 标记假 MISS;
全量提取 78 条、51 个疑似 MISS 分类后仅 3 个真错。
"""
import re
import os
import sys
import glob


def norm(s: str) -> str:
    """压空白/小写/去弯引号与撇号——匹配对引号样式不敏感。"""
    return re.sub(r"[\s\u201c\u201d\"']+", " ", s).strip().lower()


def load_corpus(pages_dir: str) -> dict:
    corpus = {}
    for f in glob.glob(os.path.join(pages_dir, "*.txt")) + \
             glob.glob(os.path.join(pages_dir, "*.md")):
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                corpus[os.path.basename(f)] = re.sub(r"\s+", " ", fh.read()).lower()
        except Exception as e:  # noqa: BLE001
            print("skip", f, e)
    return corpus


def find_in_corpus(phrase: str, corpus: dict):
    p = norm(phrase)
    return [f for f, t in corpus.items() if p in t]


def check_en(quote: str, corpus: dict):
    words = quote.split()
    if len(words) < 4:
        return find_in_corpus(quote, corpus)
    for i in range(len(words) - 3):
        hits = find_in_corpus(" ".join(words[i:i + 4]), corpus)
        if hits:
            return hits
    return []


def check_zh(quote: str, corpus: dict):
    if len(quote) < 8:
        return find_in_corpus(quote, corpus)
    for i in range(len(quote) - 8):
        hits = find_in_corpus(quote[i:i + 12], corpus)
        if hits:
            return hits
    return []


def main() -> int:
    args = sys.argv[1:]
    if "--pages" in args:
        i = args.index("--pages")
        pages_dir = args[i + 1]
        del args[i:i + 2]
    else:
        pages_dir = os.path.join(os.getcwd(), "pages")
    drafts = [a for a in args if a.endswith((".md", ".txt"))]
    if not drafts:
        print(__doc__)
        return 2
    if not os.path.isdir(pages_dir):
        print(f"pages 目录不存在: {pages_dir}")
        return 2

    corpus = load_corpus(pages_dir)
    print(f"语料存档: {len(corpus)} 个")

    fails, total = [], 0
    for draft in drafts:
        with open(draft, encoding="utf-8") as f:
            text = f.read()
        # 去掉 AI 提示词示例段（创作建议非引文）
        text_clean = re.sub(r"AI 提示词示例[：:][^。]*。\"", "", text)
        quotes = []
        for m in re.finditer(r'"([^"]{25,})"', text_clean):
            q = m.group(1).strip()
            if re.search(r"[a-z]{3,}\.\w{2,}|^https?://", q):
                continue
            han = len(re.findall(r"[\u4e00-\u9fff]", q))
            if han > len(q) * 0.3:  # 纯中文译文跳过（译文不在存档属正常）
                continue
            quotes.append(("EN", q))
        for m in re.finditer(r"「([^」]{15,})」", text):
            q = m.group(1).strip()
            if re.search(r"[\u4e00-\u9fff]", q):
                quotes.append(("ZH", q))

        for lang, q in quotes:
            total += 1
            hits = check_en(q, corpus) if lang == "EN" else check_zh(q, corpus)
            if hits:
                print("PASS", os.path.basename(draft)[:10], lang, "->", hits[0][:28], "|", q[:60])
            else:
                fails.append((draft, lang, q))
                print("MISS", os.path.basename(draft)[:10], lang, "|", q[:80])

    print(f"\n引文总数: {total}  MISS: {len(fails)}")
    for draft, lang, q in fails:
        print("  MISS:", lang, q[:120], f"({draft})")
    print("提示: MISS 先分类(译文/AI示例/维基标记假MISS)再决定是否改稿——分类方法见脚本 docstring。")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
