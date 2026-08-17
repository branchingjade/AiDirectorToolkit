#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""归档一致性自动检查 — 覆盖四条链路的系统性校验（2026-08-08 全链路审视落地）。

检查项：
1. MEMORY/USER 镜像 vs 真源 diff（_hermes/memory/ vs ~/AppData/Local/hermes/memories/）
2. 剧本库 MOC 计数 vs 磁盘实际（华语/海外 × 剧本原文/研习报告）
3. 看板日报新鲜度（协作/任务看板日报.md 是否过期）
4. 成员名单上游校验（名单 open_id vs 画像文件 vs 路由）

用法：
  python3 scripts/archive-consistency.py
输出：每项 ✓ / ⚠️ + 摘要行（供 cron 投递）
"""
import datetime
import os
import re

VAULT = r"C:/Users/HMSJ/Documents/KnowledgeBase/Obsidian Vault"
HERMES_HOME = os.path.expandvars(r"C:/Users/HMSJ/AppData/Local/hermes")


def check_mirror():
    """1. MEMORY/USER 镜像 vs 真源"""
    print("【1】MEMORY/USER 镜像一致性")
    issues = []
    for name in ("MEMORY.md", "USER.md"):
        mirror = os.path.join(VAULT, "_hermes", "memory", name)
        source = os.path.join(HERMES_HOME, "memories", name)
        if not os.path.exists(mirror) or not os.path.exists(source):
            issues.append(f"{name}: 文件缺失（镜像 {os.path.exists(mirror)} / 真源 {os.path.exists(source)}）")
            continue
        m_content = open(mirror, encoding="utf-8").read()
        s_content = open(source, encoding="utf-8").read()
        if m_content == s_content:
            print(f"  ✓ {name} 一致")
        else:
            print(f"  ⚠️ {name} 有差异（镜像 {len(m_content)} 字符 vs 真源 {len(s_content)} 字符，差 {abs(len(m_content)-len(s_content))} 字符）")
            issues.append(f"{name} 镜像滞后")
    if not issues:
        print("  ✓ 全部一致")
    print()
    return issues


def check_script_moc():
    """2. 剧本库 MOC 计数 vs 磁盘实际"""
    print("【2】剧本库 MOC vs 磁盘")
    issues = []
    moc_path = os.path.join(VAULT, "剧本库", "剧本库MOC.md")
    moc = open(moc_path, encoding="utf-8").read()
    # 从 MOC 提取声明数（"中文剧本 10 份 + 华语片研习报告 52 份"）
    m = re.search(r"华语剧本/.*?（中文剧本 (\d+) 份 \+ 华语片研习报告 (\d+) 份）", moc)
    m2 = re.search(r"海外剧本/.*?（英文剧本 (\d+) 份 \+ 海外片研习报告 (\d+) 份）", moc)
    declared = {}
    if m:
        declared["华语原文"] = int(m.group(1))
        declared["华语报告"] = int(m.group(2))
    if m2:
        declared["海外原文"] = int(m2.group(1))
        declared["海外报告"] = int(m2.group(2))
    if not declared:
        print("  ⚠️ MOC 声明数解析失败（格式变化？）")
        issues.append("MOC 声明数解析失败")
        print()
        return issues
    actual = {
        "华语原文": len([f for f in os.listdir(os.path.join(VAULT, "剧本库", "华语剧本", "剧本原文")) if f.endswith(".md")]) if os.path.isdir(os.path.join(VAULT, "剧本库", "华语剧本", "剧本原文")) else 0,
        "华语报告": len([f for f in os.listdir(os.path.join(VAULT, "剧本库", "华语剧本", "研习报告")) if f.endswith(".md")]) if os.path.isdir(os.path.join(VAULT, "剧本库", "华语剧本", "研习报告")) else 0,
        "海外原文": len([f for f in os.listdir(os.path.join(VAULT, "剧本库", "海外剧本", "剧本原文")) if f.endswith(".md")]) if os.path.isdir(os.path.join(VAULT, "剧本库", "海外剧本", "剧本原文")) else 0,
        "海外报告": len([f for f in os.listdir(os.path.join(VAULT, "剧本库", "海外剧本", "研习报告")) if f.endswith(".md")]) if os.path.isdir(os.path.join(VAULT, "剧本库", "海外剧本", "研习报告")) else 0,
    }
    for key in declared:
        d, a = declared[key], actual.get(key, 0)
        mark = "✓" if d == a else "⚠️"
        print(f"  {mark} {key}: MOC {d} vs 磁盘 {a}")
        if d != a:
            issues.append(f"{key} MOC({d})≠磁盘({a})")
    print()
    return issues


def check_kanban_report():
    """3. 看板日报新鲜度"""
    print("【3】看板日报新鲜度")
    issues = []
    path = os.path.join(VAULT, "协作", "任务看板日报.md")
    if not os.path.exists(path):
        print("  ⚠️ 任务看板日报.md 不存在")
        issues.append("看板日报缺失")
    else:
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        days = (datetime.datetime.now() - mtime).days
        if days > 3:
            print(f"  ⚠️ 看板日报 {days} 天未更新（最后 {mtime.strftime('%m-%d %H:%M')}）")
            issues.append(f"看板日报 {days} 天未更新")
        else:
            print(f"  ✓ 看板日报 {days} 天前更新（{mtime.strftime('%m-%d %H:%M')}）")
    print()
    return issues


def check_member_upstream():
    """4. 成员名单 vs 画像 vs 路由"""
    print("【4】成员名单上游校验")
    issues = []
    try:
        import json
        members = json.load(open(os.path.join(VAULT, "_hermes", "成员名单.json"), encoding="utf-8")).get("成员", {})
        profiles = {}
        for f in os.listdir(os.path.join(VAULT, "成员画像")):
            if f.endswith(".md") and f not in ("_模板.md", "成员画像.md", "历史协作者观察.md"):
                name = f[:-3]
                content = open(os.path.join(VAULT, "成员画像", f), encoding="utf-8").read()
                m = re.search(r"open_id: (\S+)", content)
                if m:
                    profiles[m.group(1)] = name
        no_profile = [info.get("name", oid) for oid, info in members.items() if oid not in profiles]
        print(f"  名单 {len(members)} 人，画像 {len(profiles)} 份")
        if no_profile:
            print(f"  ⚠️ 名单有但画像缺失/无 open_id: {', '.join(no_profile)}")
            issues.append(f"画像缺失: {len(no_profile)} 人")
        else:
            print("  ✓ 名单↔画像 open_id 全部对应")
        route = json.load(open(os.path.join(VAULT, "_hermes", "会话路由.json"), encoding="utf-8"))
        dic = route.get("项目词典", [])
        print(f"  路由词典 {len(dic)} 项")
    except Exception as e:
        print(f"  ⚠️ 检查失败: {e}")
        issues.append("成员名单校验异常")
    print()
    return issues


def main():
    print(f"== 归档一致性检查（{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}）==\n")
    all_issues = []
    all_issues += check_mirror()
    all_issues += check_script_moc()
    all_issues += check_kanban_report()
    all_issues += check_member_upstream()
    print("== 汇总 ==")
    if all_issues:
        print("  ⚠️ " + "；".join(all_issues))
    else:
        print("  ✓ 归档一致性全部通过")


if __name__ == "__main__":
    main()
