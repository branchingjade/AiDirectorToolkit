# -*- coding: utf-8 -*-
"""严格摘录复核器 v6（2026-08-07《爱在黎明破晓前》实测 36/36 直过 + 自检 3/3）。

用法：改下方 SOURCES（抓取存档 txt 列表）与 FILES（待复核 md 列表）后运行。
规则要点（详见 SKILL.md 陷阱「摘录复核 v6」条）：
1. 提取三源：反引号块 / 行级 > 引文 / 全角引号跨度（["“]([^"”]{15,})["”]）
2. 原始跨度先按块引用行 (?m)^\s*>\s* 拆分（跨度会吞进多个 > 行）
3. 剥中文括注（含（L#）行号）→ 找首个 ASCII 字母截断中文前缀 → 剥 markdown 杂符 → 剥角色名前缀（含 (CONT'D) 变体）→ 按 / 与 ... 拆段 → 段尾标点修剪
4. 含 CJK（含箭头区 \u2190-\u21ff）或 URL/路径形态的段 SKIP（伪引文，不算 FAIL）
5. 源文本归一化顺序：\r\n|\r|\f→空格 → 翻页残留页号剥离 \s+\d{1,3}\.\s+ → 剥 (MORE)（裸正则，\b 版静默失效）→ 剥 NAME (CONT'D)
6. 只剥双引号类 [“”"]，绝不剥撇号 '（You'll/I'd 缩写）
7. 自检三断言缺一不可：坏例 FAIL / 正例命中 / 跨页 (CONT'D) 打断句命中
"""
import re

def norm(s):
    s = re.sub(r'\r\n|\r|\f', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def strip_artifacts(s):
    s = re.sub(r'\s+\d{1,3}\.\s+', ' ', s)   # 翻页残留页号（如 " 67. "）
    s = re.sub(r'\(MORE\)', ' ', s)          # 裸正则！\b\(MORE\) 因空格与 ( 之间无词边界而静默失效
    s = re.sub(r'\b[A-Z][A-Za-z\'\- ]{0,25}\(CONT\'D\)', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s

# ===== 每片修改：源文本（抓取存档 txt）与待复核 md =====
SOURCES = [
    ('script', r'C:/Users/HMSJ/Documents/Hermes/film-suite-research/pages/sunrise_slug_raw.txt', True),   # (tag, path, 需剥伪影)
    ('wiki_sunrise', r'C:/Users/HMSJ/Documents/Hermes/film-suite-research/pages/wiki_before_sunrise.txt', False),
    ('wiki_trilogy', r'C:/Users/HMSJ/Documents/Hermes/film-suite-research/pages/wiki_before_trilogy.txt', False),
    ('ebert', r'C:/Users/HMSJ/Documents/Hermes/film-suite-research/pages/ebert_before_sunrise.txt', False),
]
FILES = [
    r'C:/Users/HMSJ/Documents/Hermes/film-suite-research/研习报告/爱在黎明破晓前_研习报告.md',
    r'C:/Users/HMSJ/Documents/Hermes/film-suite-research/技法卡片源稿/爱在黎明破晓前_技法卡片.md',
]

sources = {}
for tag, path, strip in SOURCES:
    t = norm(open(path, encoding='utf-8', errors='replace').read())
    sources[tag] = strip_artifacts(t) if strip else t

CJK = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u2190-\u21ff]')
URLPATH = re.compile(r'://|\.(txt|pdf|html|md)\b|scriptslug\.com|wikipedia\.org|rogerebert\.com|imsdb\.com')

def segments_of(q):
    out = []
    for chunk in re.split(r'(?m)^\s*>\s*', q):          # 先按块引用行拆（跨度会吞进多个 > 行）
        chunk = re.sub(r'（[^）]*）', ' ', chunk)          # 中文括注（含（L#）行号）
        chunk = re.sub(r'[“”"]', ' ', chunk)              # 只剥双引号类，不剥撇号（You'll/I'd）
        m = re.search(r'[A-Za-z]', chunk)
        if not m:
            continue
        chunk = chunk[m.start():]
        chunk = re.sub(r'^[\s>|*#\-_`]+', '', chunk)      # markdown 杂符
        for part in re.split(r'\s*/\s*|\.{3,}', chunk):   # / 段拼接 + 省略号分段
            p = re.sub(r'^(?:[A-Z][A-Za-z\'\- ]{0,30}|SONG):\s*', '', part.strip())
            p = re.sub(r'^[A-Z][A-Za-z\'\- ]{0,30}:\s*', '', p)
            p = re.sub(r'[.,!?;:–—-]+$', '', p.strip()).strip()
            if len(re.findall(r'[A-Za-z]', p)) >= 12 and not CJK.search(p) and not URLPATH.search(p):
                out.append(p)
    return out

def check_seg(seg):
    seg_n = re.sub(r'\s+', ' ', seg).strip()
    for tag, src in sources.items():
        if seg_n in src:
            return tag
        f = lambda s: re.sub(r'[^A-Za-z0-9]', '', s).lower()
        if f(seg_n) and f(seg_n) in f(src):
            return tag + '(fuzzy)'
    return None

def extract(path):
    t = open(path, encoding='utf-8').read()
    qs = []
    for m in re.findall(r'`([^`]{8,})`', t):
        qs.append(m)
    for m in re.findall(r'(?m)^\s*>\s*(.+)$', t):
        qs.append(m.strip())
    for m in re.findall(r'["“]([^"”]{15,})["”]', t):
        qs.append(m)
    return qs

results = []
seen = set()
for f in FILES:
    for q in extract(f):
        for s in segments_of(q):
            key = s[:40]
            if key in seen:
                continue
            seen.add(key)
            results.append((s, check_seg(s)))

fails = [(s, t) for s, t in results if t is None]
print('segments checked:', len(results), '| PASS:', len(results) - len(fails), '| FAIL:', len(fails))
for s, t in fails:
    print('FAIL:', s[:120])

# 自检三断言（缺一即校验器自身 bug）
assert check_seg('HORSE MILKSHAKE BANANA PANCAKE') is None, 'negative self-check broken'
assert check_seg("I like to feel his eyes on me when I look away") == 'script', 'positive self-check broken'
assert check_seg("No. You'll drive me crazy. You don't speak French. I'd have to completely take care of you. It would be a big mistake") == 'script', 'CONT_D positive broken'
print('self-check ok (3/3)')
