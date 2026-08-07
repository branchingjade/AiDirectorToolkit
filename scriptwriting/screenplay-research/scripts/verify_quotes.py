#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用摘录校验器：md 笔记里所有英文引号 span 对剧本原文做归一化 in 校验。

用法: python verify_quotes.py <source.txt> <note1.md> [note2.md ...]

四种通过路径（任一命中即过）:
  A. 原文归一化（去标点+小写+压缩空白）子串匹配
  B. 剥舞台指示变体: 源稿先去掉 (He sighs) 类圆括号内容再归一化
  C. 去空格变体: 解决连字符折行（源稿 health\\n-food vs 引号 health-food）
  D. 省略号分段: 引号内 "..." 拆段逐片段校验（省略的是真实对白时整串必不连续）

内置过滤（缺一即误报）:
  - 角色名前缀剥除 (ALVY:/ACTOR:/JEFF:...)
  - CJK 过滤: 中英混排行抓出的伪 span 直接跳过
  - 缩写残片过滤: 单引号正则抓到的 're both crazy!' / 's right!' 等残片
  - 过短 span (归一化后 < 18 字符) 不判

退出码: 0=全过, 1=有 FAIL, 2=参数错误。
自检纪律: 0 FAIL 结果必须先用"故意改写一句台词"的坏例反向验证校验器本身没 bug。
"""
import re
import sys

CJK = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")
CONTR = re.compile(r"^([mst]|re|ll|ve|d) ")
MINLEN = 18
FRAGMIN = 12


def norm(q):
    q = re.sub(r"[^A-Za-z0-9\s]", "", q).lower()
    return re.sub(r"\s+", " ", q).strip()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    nsA = norm(src)                              # 原文归一化
    nsB = norm(re.sub(r"\([^()]*\)", " ", src))  # 剥舞台指示变体
    nsC = re.sub(r"\s+", "", nsA)                # 去空格变体
    nsD = re.sub(r"\s+", "", nsB)

    def check(sp):
        sp = re.sub(r"^\s*([A-Z][A-Z\s\.\'\-]{1,20}):\s*", "", sp)
        if CJK.search(sp):
            return None
        n = norm(sp)
        if len(n) < MINLEN:
            return None
        nn = re.sub(r"\s+", "", n)
        if n in nsA or n in nsB or nn in nsC or nn in nsD:
            return True
        frags = re.split(r"\.\.\.", sp)
        if len(frags) > 1:
            for fr in frags:
                nf = norm(fr)
                if len(nf) >= FRAGMIN:
                    nfn = re.sub(r"\s+", "", nf)
                    if not (nf in nsA or nf in nsB or nfn in nsC or nfn in nsD):
                        return False
            return True
        return False

    results = []
    for f in sys.argv[2:]:
        for i, ln in enumerate(open(f, encoding="utf-8"), 1):
            if len(ln) < 20:
                continue
            spans = [m.group(1) for m in re.finditer(r'["“]([^"”]{15,})["”]', ln)]
            for m in re.finditer(r"'([^']{20,})'", ln):
                s = m.group(1)
                if not CONTR.match(s) and not CJK.search(s):
                    spans.append(s)
            for sp in spans:
                r = check(sp)
                if r is not None:
                    results.append((f, i, r, sp))

    fails = [r for r in results if not r[2]]
    print(f"TOTAL checked spans: {len(results)} | PASS: {len(results) - len(fails)} | FAIL: {len(fails)}")
    for f, i, _ok, sp in fails:
        print(f"FAIL {f}:{i}\n  {sp[:160]}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
