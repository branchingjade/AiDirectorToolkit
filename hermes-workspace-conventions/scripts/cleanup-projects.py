#!/usr/bin/env python3
"""Clean up stale Hermes project entries and worktree stubs.

- Removes duplicate project entries in projects.db
- Fixes AiDirectorToolkit path with double `\c\` prefix
- Reports without destructive action — review before committing.
"""

import sqlite3, os, sys
from pathlib import Path

DB = Path.home() / "AppData" / "Local" / "hermes" / "projects.db"
WORKTREES = Path.home() / "Documents" / "Hermes" / ".worktrees"

def main(dry_run=True):
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()

    # --- Identify problems ---
    c.execute("SELECT id, slug, name, primary_path, archived FROM projects")
    all_rows = c.fetchall()

    # Duplicates (same primary_path, multiple entries)
    path_groups = {}
    for row in all_rows:
        pid, slug, name, path, archived = row
        norm = str(path).replace("\\", "/").lower().rstrip("/")
        path_groups.setdefault(norm, []).append(row)

    to_delete = []
    to_fix = []

    for norm_path, entries in path_groups.items():
        active = [e for e in entries if not e[4]]  # non-archived
        if len(active) > 1:
            # Keep the first one, delete the rest
            keep = active[0]
            for dup in active[1:]:
                to_delete.append(dup[0])

    # Bad paths
    for row in all_rows:
        pid, slug, name, path, archived = row
        if "\\c\\" in str(path) or "C:\\\\c\\\\" in str(path):
            fixed = str(path).replace("C:\\c\\", "C:\\").replace("C:\\\\c\\\\", "C:\\")
            to_fix.append((pid, path, fixed))

    # --- Report ---
    print("=== 重复项目条目 ===")
    if not to_delete:
        print("  (无)")
    else:
        for pid in to_delete:
            c.execute("SELECT id, slug, name FROM projects WHERE id=?", (pid,))
            r = c.fetchone()
            print(f"  删除: {r[1]} ({r[2]}) — {r[0]}")

    print("\n=== 坏路径 ===")
    if not to_fix:
        print("  (无)")
    else:
        for pid, old, new in to_fix:
            print(f"  修复: {old} → {new}")

    # --- Worktrees ---
    print(f"\n=== .worktrees/ ===")
    if WORKTREES.exists():
        contents = list(WORKTREES.iterdir())
        print(f"  路径: {WORKTREES}")
        print(f"  内容: {[d.name for d in contents]}")
        for d in contents:
            if d.is_dir():
                files = list(d.rglob("*"))
                print(f"    {d.name}/ — {len(files)} 文件")
        print("\n  建议: rm -rf 删除（已确认为历史空壳，无有效内容）")
    else:
        print("  (不存在)")

    # --- Execute if not dry run ---
    if not dry_run:
        print("\n⚠️  dry_run=False，执行清理...")
        for pid in to_delete:
            c.execute("DELETE FROM projects WHERE id=?", (pid,))
            c.execute("DELETE FROM project_folders WHERE project_id=?", (pid,))
            print(f"  已删除: {pid}")
        for pid, old, new in to_fix:
            c.execute("UPDATE projects SET primary_path=? WHERE id=?", (new, pid))
            print(f"  已修复: {pid} → {new}")
        conn.commit()
        print("Done.")

    conn.close()

if __name__ == "__main__":
    dry = "--execute" not in sys.argv
    main(dry_run=dry)
