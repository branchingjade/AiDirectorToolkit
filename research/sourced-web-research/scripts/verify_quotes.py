# -*- coding: utf-8 -*-
"""研习报告/技法卡片 引文全量校验（通用版，2026-08-09 逍遥骑士轮实测 0 FAIL）

用法：复制到工作区（或就地改配置），把交付文档的英文/日文引文逐条对回 pages/ 存档源文件。
校验 = 归一化后引文是归一化后源文件的子串。输出 TOTAL/PASS/FAIL/SHORT 统计与 FAIL 明细。

配置四件套：
  BASE        工作区绝对路径（Windows 用 C:/ 正斜杠盘符形式，MSYS /c/ 路径会被原生 Python 吞掉）
  DELIVERABLES 交付文档名列表（自动提取其中的英文引文）
  SRC_MAP     {来源编号: 存档文件路径}
  MANUAL      手工条目 [(S#, 引文)]：跨行/拆分/短引句（<12 字符）逐条补录

归一化管线（踩坑全集）：
  去软连字符 \\u00ad（jina/维基文本常见）→ em/en dash 归一 → 弯引号转直 →
  去 markdown 强调符 _ *（jina 提取的 Criterion 文本带 _Easy Rider_ 斜体）→
  引号字符全部移除（引文用 ' 源用 " 也能匹配；两端一致即可）→ NFKC → 去全部空白 → 小写
"""
import re, unicodedata

BASE = r"C:/path/to/workdir"          # ← 改成你的工作区
DELIVERABLES = ["报告.md", "技法卡片.md"]  # ← 改成你的交付文档
SRC_MAP = {
    "S1": f"{BASE}/pages/format-wp.txt",
    "S2": f"{BASE}/pages/format-criterion.txt",
}
MANUAL = []   # [(sid, quote), ...]

def norm(s):
    s = s.replace("\u00ad", "")                                  # 软连字符
    s = s.replace("\u2014", "-").replace("\u2013", "-")          # em/en dash
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2026", "...")                               # 省略号
    s = s.replace("_", "").replace("*", "")                      # markdown 强调符
    s = s.replace("'", "").replace('"', "")                      # 引号字符全移除
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", "", s)
    return s.lower()

def is_ascii_dominant(s):
    return sum(1 for c in s if ord(c) < 128) / max(len(s), 1) > 0.8

def extract_quotes(path):
    """自动提取：块引用（含 "..." 取引号片段，否则按句拆分）+ 行内 "..." 片段。
    只处理带 [S#] 标签的行；ASCII 占比 <0.8 的行跳过（中文说明行误报防护）。"""
    out = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            m = re.search(r"\[(S\d)\]", ln)
            if not m:
                continue
            sid = m.group(1)
            if ln.strip().startswith(">"):
                body = ln.strip().lstrip(">").strip()
                eng = re.findall(r'"[^"]*"', body)
                if not eng:
                    eng = re.split(r"(?<=[.!?])\s+", body)  # 多句块引用按句拆
                for e in eng:
                    if re.search(r"[a-zA-Z]{3,}", e) and is_ascii_dominant(e):
                        out.append((sid, e.strip('"')))
            for e in re.findall(r'"([^"]*[a-zA-Z]{3,}[^"]*)"', ln):
                if re.search(r"[a-zA-Z]{3,}", e) and sid in ln:
                    out.append((sid, e))
    return out

def main():
    sources = {}
    for k, p in SRC_MAP.items():
        with open(p, encoding="utf-8", errors="replace") as f:
            sources[k] = norm(f.read())

    results = []
    for sid, q in MANUAL:
        nq = norm(q)
        st = "SHORT" if len(nq) < 12 else ("PASS" if nq in sources.get(sid, "") else "FAIL")
        results.append((sid, q, st))

    for fname in DELIVERABLES:
        for sid, q in extract_quotes(f"{BASE}/{fname}"):
            nq = norm(q)
            if len(nq) < 12:
                results.append((sid, q, "SHORT"))
                continue
            # 先对行内标注的来源；多来源行（[S4][S5]）片段可能属另一来源 → 全部源兜底
            if nq in sources.get(sid, ""):
                results.append((sid, q, "PASS"))
            elif any(nq in t for t in sources.values()):
                results.append((sid, q, "PASS"))
            else:
                results.append((sid, q, "FAIL"))

    fails = [r for r in results if r[2] == "FAIL"]
    shorts = [r for r in results if r[2] == "SHORT"]
    print(f"TOTAL={len(results)} PASS={len(results)-len(fails)-len(shorts)} FAIL={len(fails)} SHORT={len(shorts)}")
    for sid, q, st in fails:
        print(f"[FAIL {sid}] {q[:110]}")
    for sid, q, st in shorts:
        print(f"[SHORT {sid}] {q[:80]}")
    print("VERIFY_DONE")

if __name__ == "__main__":
    main()
