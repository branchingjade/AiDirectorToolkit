"""剧本文本完整性校验器：公共剧本 PDF 文本层常因字库解码丢失内容，统计前必跑。

用法: python verify_screenplay.py file1.txt [file2.txt ...]
输出: 词数、非空行数、formfeed 页数、结尾标记位置、场景标题数、末尾几行。
判读:
  - 'THE END'/'FADE OUT' 位置应 >90%；出现在 <10% 处多半是正文普通句子
  - formfeed 页数 ≈ PDF 页数（pdftotext 转换前先核对）
  - 场景标题数为 0 或异常低（如教父 13 处）→ 文本层有损，标题统计不可靠，如实标注
"""
import re
import sys


def verify(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    txt = txt.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    lines = [l for l in txt.split("\n") if l.strip()]
    words = len(re.findall(r"\S+", txt))
    print(f"=== {path}")
    print(f"  words={words}  nonempty_lines={len(lines)}  formfeed_pages={txt.count(chr(12))}")
    for marker in ["FADE OUT", "THE END", "FADE TO BLACK"]:
        idx = txt.rfind(marker)
        if idx >= 0 and len(txt):
            print(f"  last '{marker}' at {100*idx//len(txt)}% of file")
    heads = [l for l in lines if re.match(r"^(INT|EXT|EST|I/E)\.", l) or re.match(r"^\d{1,3}\s+(INT|EXT)", l)]
    print(f"  INT/EXT headings: {len(heads)}")
    if heads:
        for h in heads[:3]:
            print("    ", h[:70])
    print("  tail:")
    for l in lines[-3:]:
        print("    ", l[:80])


if __name__ == "__main__":
    for p in sys.argv[1:]:
        verify(p)
