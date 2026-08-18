#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""知识库使用率统计 — 从 state.db 统计 skill_view 实际加载了哪些知识库文件。

数据源：messages 表 tool 角色消息，skill_view 结果 JSON：
  - 主本：  {"success": true, "name": "妖玉影视知识库", "content": "..."}
  - 文件：  {"success": true, "name": "妖玉影视知识库", "file": "references/xxx.md", ...}

用法：
  python3 scripts/knowledge-usage.py [days]   # 默认 7 天
输出：知识库文件加载次数 + 0 次加载的潜在僵尸资产清单

背景（2026-08-08 全链路审视）：用画像成熟度五标准（NN/g《Personas Are Living
Documents》）审视各数据链路时，发现创作知识库是最像"画像改造前"的链路——建了
不知道用没用。本脚本补上反馈闭环：被反复加载的=土壤养分（该继续深化）；0 次
加载的=潜在荒地（该回测/该宣传/该考虑是否冗余）。挂接在知识库每日巡检 cron
（22:00）步骤6。
"""
import sqlite3
import datetime
import json
import os
import sys

HERMES_HOME = os.path.expandvars(r"C:/Users/HMSJ/AppData/Local/hermes")
DB_PATH = os.path.join(HERMES_HOME, "state.db")
KB_SKILLS = ("妖玉影视知识库",)
# 知识库文件根目录（references/ 下所有 .md 即知识库资产）
KB_ROOT = os.path.join(HERMES_HOME, "skills", "妖玉影视", "_知识库", "references")

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 7


def main():
    since = datetime.datetime.now() - datetime.timedelta(days=DAYS)
    since_ts = since.timestamp()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # ⚠️ 坑：过滤条件用知识库名（结果 JSON 含 name），不是 'skill_view'（结果里没有该字样）
    cur.execute(
        "SELECT content FROM messages WHERE role='tool' AND content (content LIKE '%妖玉影视知识库%' OR content LIKE '%yaoyu-film-knowledge-base%') AND timestamp > ?",
        (since_ts,),
    )
    rows = cur.fetchall()
    conn.close()

    skill_counts = {}   # skill_name -> n（主本加载）
    file_counts = {}    # file -> n（references 文件加载）
    for (content,) in rows:
        content = content or ""
        try:
            d = json.loads(content)
        except (ValueError, TypeError):
            continue
        if not isinstance(d, dict) or not d.get("success"):
            continue
        name = d.get("name", "")
        if name in KB_SKILLS:
            if "file" in d:
                fp = d.get("file", "")
                # 归一化：去掉 references/ 前缀，统一用 目录/文件.md 相对路径
                norm = fp.split("references/", 1)[1] if "references/" in fp else fp
                file_counts[norm] = file_counts.get(norm, 0) + 1
            elif "content" in d:
                skill_counts[name] = skill_counts.get(name, 0) + 1

    print(f"== 知识库使用率（近 {DAYS} 天）==\n")

    # 1. 主本加载
    print("【1】知识库主本加载次数")
    if skill_counts:
        for name, n in sorted(skill_counts.items(), key=lambda x: -x[1]):
            print(f"  {name:<20} {n} 次")
    else:
        print("  （近 {} 天无主本加载）".format(DAYS))
    print()

    # 2. references 文件加载（按目录归类）
    print("【2】references 文件加载次数")
    if file_counts:
        cats = {}
        for fp, n in file_counts.items():
            cat = fp.split("/")[0] if "/" in fp else "(根)"
            cats.setdefault(cat, []).append((fp, n))
        for cat in sorted(cats):
            print(f"  [{cat}]")
            for fp, n in sorted(cats[cat], key=lambda x: -x[1]):
                fname = fp.split("/")[-1]
                print(f"    {n:>3} 次  {fname}")
    else:
        print("  （近 {} 天无 references 文件加载）".format(DAYS))
    print()

    # 3. 潜在僵尸资产（state.db 现存记录中从未被 skill_view 加载过）
    print("【3】潜在僵尸资产（state.db 记录中从未被 skill_view 加载过）")
    print("  ⚠️ 注：state.db 可能已清理早期会话，'从未加载'指现存记录范围")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT content FROM messages WHERE role='tool' AND (content LIKE '%妖玉影视知识库%' OR content LIKE '%yaoyu-film-knowledge-base%')"
    )
    all_rows = cur.fetchall()
    conn.close()
    ever_loaded = set()
    for (content,) in all_rows:
        content = content or ""
        try:
            d = json.loads(content)
        except (ValueError, TypeError):
            continue
        if isinstance(d, dict) and d.get("success") and d.get("name") in KB_SKILLS:
            if "file" in d:
                fp = d.get("file", "")
                norm = fp.split("references/", 1)[1] if "references/" in fp else fp
                ever_loaded.add(norm)

    if os.path.isdir(KB_ROOT):
        zombies = []
        total = 0
        for root, dirs, files in os.walk(KB_ROOT):
            for f in files:
                if not f.endswith(".md"):
                    continue
                total += 1
                full = os.path.join(root, f).replace("\\", "/")
                marker = "references/"
                rel = full.split(marker, 1)[1] if marker in full else full
                if rel not in ever_loaded and f not in ever_loaded:
                    zombies.append(rel)
        if zombies:
            for z in sorted(zombies):
                print(f"  🧟 {z}")
            print(f"  （共 {total} 个资产，{len(zombies)} 个从未加载 = {len(zombies)*100//total}%）")
        else:
            print(f"  ✓ 全部 {total} 个资产均被加载过")
    else:
        print(f"  （知识库目录不存在: {KB_ROOT}）")


if __name__ == "__main__":
    main()
