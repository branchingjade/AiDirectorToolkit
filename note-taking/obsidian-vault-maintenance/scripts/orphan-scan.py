"""Obsidian vault 孤岛扫描——找出出链/入链为 0 的 md 文件。

用法: python scripts/orphan-scan.py <vault根目录>
例:   python scripts/orphan-scan.py "C:/Users/HMSJ/Documents/KnowledgeBase/Obsidian Vault"

规则（Obsidian 风格裸名匹配）:
- 链接目标取 split('/')[-1]，若带 .md 后缀先剥掉——否则 MOC/索引里的
  [[华语剧本/剧本原文/xxx.md]] 全部匹配失败，产生整库误报（实测一次 97 个假孤岛）
- 出链 = 文件内 [[wikilink]] 数；入链 = 其他文件链接到它的次数
- 孤岛 = 出链 0 且 入链 0
- 排除 .obsidian 内部文件

预期内孤岛（不算问题）:
- AGENTS.md 等根目录 agent 指令文件（不参与图谱）
- 系统/模板文件
"""
import os, re, sys, glob

root = sys.argv[1] if len(sys.argv) > 1 else "."
files = [f.replace("\\", "/") for f in glob.glob(os.path.join(root, "**/*.md"), recursive=True)]
files = [f for f in files if "/.obsidian/" not in f]
files.sort()

outlink = {}
inlink = {f: 0 for f in files}
for f in files:
    try:
        text = open(f, encoding="utf-8").read()
    except Exception as e:
        print(f"[跳过无法读取] {f}: {e}")
        continue
    links = set(re.findall(r"\[\[([^\]|#]+)", text))
    outlink[f] = len(links)
    for l in links:
        t = l.strip().split("/")[-1]
        if t.endswith(".md"):
            t = t[:-3]  # 关键：剥 .md 后缀
        for g in files:
            if os.path.basename(g)[:-3] == t:
                inlink[g] += 1

orphans = [f for f in files if outlink.get(f, 0) == 0 and inlink.get(f, 0) == 0]
print(f"总文件 {len(files)}，孤岛 {len(orphans)} 个:")
for o in orphans:
    print(" ", o)
