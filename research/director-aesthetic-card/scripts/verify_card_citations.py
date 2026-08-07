#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导演美学卡片定稿校验脚本（director-aesthetic-card 技能配套）。

用法:
  python verify_card_citations.py <卡片.md> <pages目录> <存档前缀> [短语文件]

校验 1（编号一致性）: 正文 [S#] 引用 ↔ 文末「取证来源清单」表（^| S\d+ 行）对账，
  正文引用但清单缺失 = 错引/漏登，必须修。
校验 2（引文短语）: 短语文件每行一个短语（# 开头为注释），对 pages 目录下 <前缀>*
  全部 .txt/.json 存档做归一化（空白/弯引号/大小写）后的子串检索，输出 OK/MISS。

引文必须从存档逐字复制。MISS 时按顺序排查（都是实测假 MISS 源）:
  ① 测试短语是引文的译文 → 改校验英文/原文短语
  ② 转录帖错别字/繁体是否按原文保留（如"纲丝"、"雪地裡"）→ 卡片应保留原文拼写
  ③ 多字/少字/换序（对照存档原文）
  ④ 引号/繁简未归一（脚本已处理弯引号、空白，并整体剥离引号字符——'X' vs "X"
     形态不一必须整体剥离而非只转换，否则假 MISS；双侧一致剥离后子串匹配仍成立）
  ⑤ 引文出自另一个存档文件（换文件再查）
  ⑥ 引文包在 {{quote box|quote=...}}/{{blockquote|...}} 模板内，通用剥壳会整段删掉
     → 对含模板的英维 raw 建议做双语料校验：每档存档 norm 两版（剥模板版 + 只剥
     标签/链接/压空白不删模板版），任一命中即通过（昆汀轮 88 引文 0 MISS 配方，
     详见 references/tarantino-evolution-research-2026-08.md）
  ⑦ {{lang|de|Wehrmacht}} 类语言模板吞词 → 先做内容保留
     re.sub(r'\{\{lang\|[^{}|]*\|([^{}]*)\}\}', r'\1', s) 再剥壳
  ⑧ while '[[' in s: re.sub(...) 遇模板剥壳残留的残缺 [[ 死循环超时 → 先
     new = re.sub(...); if new == s: break 再赋值
  ⑨ 自己节引从省略号处起头时借用了原文相邻词（「a 'Quarter Pounder'」实为
     「a [[McDonald's]] '[[Quarter Pounder]]'」节引，冠词 a 属 McDonald's）→
     修正引文措辞而非放宽校验；中文文档英文引文包在「」里，短语提取正则用
     「([^」]+)」+ [A-Za-z]{3} 过滤（英文引号正则提取会 total 0）

退出码: 0=全部通过; 1=存在 MISS 或编号缺失; 2=参数错误。
"""
import re, sys, glob, json, os


def norm(s: str) -> str:
    s = re.sub(r'\s+', ' ', s).lower()
    s = (s.replace('\u2018', "'").replace('\u2019', "'")
         .replace('\u201c', '"').replace('\u201d', '"'))
    # 整体剥离引号字符：'X' 与 "X" 形态不一时只转换仍假 MISS（昆汀轮实测）
    return s.replace("'", '').replace('"', '')


def check_numbers(text: str) -> bool:
    body = text.split('## 附录')[0]
    cited = set(int(x) for x in re.findall(r'\[S(\d+)\]', body))
    table = set(int(x) for x in re.findall(r'^\| S(\d+) ', text, re.M))
    print('正文引用编号:', sorted(cited))
    print('清单编号:', sorted(table))
    print('正文引用但清单缺失:', sorted(cited - table) or '无')
    print('清单有但正文未引(备用可留):', sorted(table - cited))
    ok = not (cited - table)
    if not ok:
        print('!! 正文引用了清单里不存在的编号，先补登记再定稿')
    return ok


def check_phrases(pages_dir: str, prefix: str, phrases_file: str) -> bool:
    corpus = {}
    for f in glob.glob(os.path.join(pages_dir, prefix + '*')):
        if not f.endswith(('.txt', '.json')):
            continue
        try:
            raw = open(f, encoding='utf-8', errors='ignore').read()
            if f.endswith('.json'):
                try:
                    raw = ' '.join(str(x) for x in json.loads(raw).values())
                except Exception:
                    pass
            corpus[f] = norm(raw)
        except Exception:
            pass
    miss = []
    for line in open(phrases_file, encoding='utf-8'):
        p = line.strip()
        if not p or p.startswith('#'):
            continue
        np = norm(p)
        hits = [f for f, c in corpus.items() if np in c]
        if hits:
            print("OK  [%s]  %s" % (', '.join(os.path.basename(h) for h in hits[:3]), p))
        else:
            miss.append(p)
    print("\n=== MISS (%d) ===" % len(miss))
    for p in miss:
        print("MISS:", p)
    return not miss


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    card, pages_dir, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
    phrases_file = sys.argv[4] if len(sys.argv) > 4 else None
    text = open(card, encoding='utf-8').read()
    ok = check_numbers(text)
    if phrases_file:
        ok = check_phrases(pages_dir, prefix, phrases_file) and ok
    print('\n校验结论:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
