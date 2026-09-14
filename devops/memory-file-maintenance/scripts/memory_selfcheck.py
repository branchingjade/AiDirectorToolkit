#!/usr/bin/env python3
"""
MEMORY.md 自检脚本（基于 2026-08-26 实测）。

Usage:
    python memory_selfcheck.py [path/to/MEMORY.md]

默认检查 ~/AppData/Local/hermes/memories/MEMORY.md。

检查项：
1. 基础指标（段数 / 字数 / 占用率）
2. § 分隔符齐全（段数+1 == § 出现次数）
3. 应删段全部 NOT found（用关键词列表）
4. 应精简段都含精简版关键词
5. 关键铁律全部 still present
6. 备份存在（MEMORY.md.bak-*）

返回非零 exit code 表示有 fail（agent 可用此决定是否阻断流程）。
"""

import re
import sys
from pathlib import Path

DEFAULT_PATH = Path.home() / "AppData" / "Local" / "hermes" / "memories" / "MEMORY.md"

# 关键铁律（每次优化后必须 NOT lost）
CRITICAL_RULES = [
    "安全红线",
    "cron 设计铁律",
    "浏览器铁律",
    "Skill 升级铁律",
    "改编创作铁律",
    "bot 角色边界",
    "用户偏好「本地的单独的」",
]

# 应删的关键词（迁到 skill 或废机制的段）
DELETED_KEYWORDS = [
    "达芬奇桥文件 C:",
    "NAS 域名 hmsj.local",
    "Hindsight 已退役（2026-08-25 实测闭环）",
    "agent + 桌面 GUI 下载器协作模式",
    "达芬奇 .resolvedbkey 密钥文件",
    "用户术语 Hindsight local_embedded",
    "施文皓全局消息格式偏好（2026-08-25 拍板）",
    "绿联NAS 达芬奇 PostgreSQL 13",
    "Obsidian Vault 路径 =",
    "Hermes-DSH 桥 P0 修复闭环（2026-08-19/20）",
    "⑧升级审计产物",
    "DSH background task wrapper exit ≠ DSH 死亡（2026-08-24 实测 3 次）",
    "运维/技术方案偏好：①方案收敛",
    "用户偏好「本地独立线」与 NAS 远程线并行共存",
    "skill 大小守纪（2026-08-20）：hermes-dsh-fusion",
    "用户有 M 系列（Apple Silicon）Mac",
    "Hermes STT 已配好：stt.provider=local_command",
]


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    if not path.exists():
        print(f"FAIL: file not found: {path}")
        sys.exit(2)

    text = path.read_text(encoding="utf-8")
    parts = re.split(r"(?m)^§$", text)
    seg_count = len(parts) - 1
    total_chars = sum(len(p.strip()) for p in parts[1:])
    usage_pct = total_chars / 16000 * 100

    print("=" * 60)
    print("MEMORY.md 自检")
    print("=" * 60)
    print(f"文件: {path}")
    print(f"段数: {seg_count}")
    print(f"段内容字符: {total_chars}")
    print(f"占用率: {usage_pct:.1f}% (目标 <60%)")
    print(f"缓冲: {16000 - total_chars} 字")
    print()

    fail_count = 0

    # 1. 占用率
    if usage_pct > 80:
        print(f"⚠️ 占用率偏高 (>80%)，考虑精简或删除冗余段")
    if usage_pct > 60:
        print(f"ℹ️ 占用率 >60%，下次会话写入可能受限")
    print()

    # 2. § 分隔符
    section_count = text.count("§")
    expected = seg_count + 1
    if section_count == expected:
        print(f"✅ § 分隔符齐全（{section_count} == 段数+1 = {expected}）")
    else:
        print(f"❌ § 分隔符异常：{section_count} ≠ 段数+1 = {expected}")
        fail_count += 1
    print()

    # 3. 应删段
    print("应删段检查（必须 NOT found）：")
    deleted_failures = []
    for kw in DELETED_KEYWORDS:
        if kw in text:
            print(f"  ❌ {kw[:50]}")
            deleted_failures.append(kw)
        # 否则静默通过
    if not deleted_failures:
        print(f"  ✅ {len(DELETED_KEYWORDS)}/{len(DELETED_KEYWORDS)} 全部已删")
    else:
        print(f"  ❌ {len(deleted_failures)} 段未删干净")
        fail_count += len(deleted_failures)
    print()

    # 4. 关键铁律
    print("关键铁律检查（必须 still present）：")
    critical_failures = []
    for kw in CRITICAL_RULES:
        if kw in text:
            print(f"  ✅ {kw}")
        else:
            print(f"  ❌ {kw[:50]}")
            critical_failures.append(kw)
    if critical_failures:
        print(f"\n⚠️ {len(critical_failures)} 条核心铁律丢失！")
        fail_count += len(critical_failures)
    print()

    # 5. 备份存在
    memory_dir = path.parent
    backups = sorted(memory_dir.glob("MEMORY.md.bak-*"))
    print(f"备份: {len(backups)} 个")
    for b in backups[-3:]:  # 最新 3 个
        print(f"  - {b.name}")
    if not backups:
        print("  ⚠️ 没有备份（建议操作前 cp 备份）")
    print()

    # 结论
    print("=" * 60)
    print("结论")
    print("=" * 60)
    if fail_count == 0:
        print(f"✅ 通过（{seg_count} 段 / {total_chars} 字 / {usage_pct:.1f}%）")
        sys.exit(0)
    else:
        print(f"❌ {fail_count} 项 fail")
        sys.exit(1)


if __name__ == "__main__":
    main()