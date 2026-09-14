#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
attendance_cli.py —— 考勤系统命令行工具（模板版）

复制此文件到 C:/Users/HMSJ/Documents/Hermes/scripts/attendance_cli.py 后使用。

子命令：
  add_leave     录入请假
  add_status    录入单日状态
  list_leave    列出请假
  delete_leave  删除请假
  list_members  列出全员
  gen_report    生成月度报表（不发飞书）
"""
import sqlite3
import argparse
import sys
from pathlib import Path

DB_PATH = Path("C:/Users/HMSJ/AppData/Local/hermes/cron/attendance.db")

VALID_LEAVE_TYPES = {"事假", "病假", "年假", "调休", "婚假", "产假", "其他"}
VALID_STATUS = {"在岗", "迟到", "早退", "请假", "缺勤", "休息"}


def get_member_by_name(name):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT open_id, name FROM members WHERE name=? OR open_id=?", (name, name))
    row = cur.fetchone()
    con.close()
    return row


def add_leave(args):
    member = get_member_by_name(args.name)
    if not member:
        print(f"❌ 找不到成员: {args.name}")
        sys.exit(1)
    open_id, name = member
    end_date = args.end_date or args.date

    if args.type not in VALID_LEAVE_TYPES:
        print(f"❌ 请假类型无效，应为: {', '.join(VALID_LEAVE_TYPES)}")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO leave_records (open_id, start_date, end_date, leave_type, reason) VALUES (?, ?, ?, ?, ?)",
        (open_id, args.date, end_date, args.type, args.reason or "")
    )
    con.commit()
    leave_id = cur.lastrowid
    con.close()

    if args.date == end_date:
        print(f"✅ 已记录: {name} {args.date} {args.type} ({args.reason or '无原因'})")
    else:
        print(f"✅ 已记录: {name} {args.date} ~ {end_date} {args.type} ({args.reason or '无原因'})")
    print(f"   leave_id = {leave_id}")


def add_status(args):
    member = get_member_by_name(args.name)
    if not member:
        print(f"❌ 找不到成员: {args.name}")
        sys.exit(1)
    open_id, name = member

    if args.status not in VALID_STATUS:
        print(f"❌ 状态无效，应为: {', '.join(VALID_STATUS)}")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO daily_status (open_id, work_date, status, note) VALUES (?, ?, ?, ?)",
        (open_id, args.date, args.status, args.note or "")
    )
    con.commit()
    con.close()
    print(f"✅ 已记录: {name} {args.date} {args.status} ({args.note or '无备注'})")


def list_leave(args):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    if args.month:
        cur.execute("""
            SELECT lr.id, m.name, lr.start_date, lr.end_date, lr.leave_type, lr.reason
            FROM leave_records lr JOIN members m ON m.open_id = lr.open_id
            WHERE substr(lr.start_date, 1, 7) <= ? AND substr(lr.end_date, 1, 7) >= ?
            ORDER BY lr.start_date, m.name
        """, (args.month, args.month))
    else:
        cur.execute("""
            SELECT lr.id, m.name, lr.start_date, lr.end_date, lr.leave_type, lr.reason
            FROM leave_records lr JOIN members m ON m.open_id = lr.open_id
            ORDER BY lr.start_date DESC, m.name
        """)
    rows = cur.fetchall()
    con.close()

    if not rows:
        print(f"📭 {args.month or '全部'} 无请假记录")
        return
    print(f"📋 请假记录 ({args.month or '全部'}):")
    print(f"{'ID':>4}  {'姓名':<8}  {'开始':<10}  {'结束':<10}  {'类型':<6}  {'原因':<20}")
    for r in rows:
        print(f"{r[0]:>4}  {r[1]:<8}  {r[2]:<10}  {r[3]:<10}  {r[4]:<6}  {r[5][:20]:<20}")


def delete_leave(args):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM leave_records WHERE id=?", (args.id,))
    n = cur.rowcount
    con.commit()
    con.close()
    if n:
        print(f"✅ 已删除 leave_id={args.id}")
    else:
        print(f"⚠️ 未找到 leave_id={args.id}")


def list_members(args):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT name, open_id, status FROM members ORDER BY name")
    rows = cur.fetchall()
    con.close()
    print(f"👥 在职名单 ({len(rows)} 人):")
    for r in rows:
        print(f"   - {r[0]:<6}  {r[1][:24]}...  {r[2]}")


def gen_report(args):
    import calendar
    from datetime import datetime, date
    year, month = map(int, args.month.split("-"))
    _, last_day = calendar.monthrange(year, month)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT open_id, name FROM members ORDER BY name")
    members = cur.fetchall()
    cur.execute("""
        SELECT m.name, lr.start_date, lr.end_date, lr.leave_type, lr.reason
        FROM leave_records lr JOIN members m ON m.open_id = lr.open_id
        WHERE substr(lr.start_date, 1, 7) <= ? AND substr(lr.end_date, 1, 7) >= ?
        ORDER BY lr.start_date, m.name
    """, (args.month, args.month))
    leaves = cur.fetchall()
    con.close()

    lines = [f"# {args.month} 考勤报表", ""]
    lines.append(f"工作时间: 上午 09:00 – 12:00 · 下午 14:00 – 19:00")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("\n---\n## 在岗人员\n")
    lines.append("| 姓名 | open_id |")
    lines.append("|---|---|")
    for open_id, name in members:
        lines.append(f"| {name} | {open_id[:20]}... |")

    lines.append("\n## 请假记录\n")
    if not leaves:
        lines.append("（当月无请假记录）\n")
    else:
        lines.append("| 姓名 | 开始 | 结束 | 类型 | 原因 |")
        lines.append("|---|---|---|---|---|")
        for name, sd, ed, lt, rs in leaves:
            lines.append(f"| {name} | {sd} | {ed} | {lt} | {rs} |")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="考勤系统 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add_leave")
    p.add_argument("--name", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--end-date")
    p.add_argument("--type", required=True)
    p.add_argument("--reason")
    p.set_defaults(func=add_leave)

    p = sub.add_parser("add_status")
    p.add_argument("--name", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--note")
    p.set_defaults(func=add_status)

    p = sub.add_parser("list_leave")
    p.add_argument("--month")
    p.set_defaults(func=list_leave)

    p = sub.add_parser("delete_leave")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=delete_leave)

    p = sub.add_parser("list_members")
    p.set_defaults(func=list_members)

    p = sub.add_parser("gen_report")
    p.add_argument("--month", required=True)
    p.set_defaults(func=gen_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()