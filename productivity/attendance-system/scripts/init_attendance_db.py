#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_attendance_db.py —— 考勤数据库初始化脚本

用法：
  1. 编辑下方 MEMBERS 列表填入实际人员
  2. 编辑 WORK_HOURS 设置工作时间
  3. 运行：python init_attendance_db.py

表结构：
  - members: 人员主表
  - daily_status: 单日状态（手动标记）
  - leave_records: 请假记录（多日一条）
  - monthly_reports: 月度报表归档
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("C:/Users/HMSJ/AppData/Local/hermes/cron/attendance.db")

# ===== 在此编辑：在职人员清单 =====
MEMBERS = [
    # ("open_id", "姓名", "状态"),
    # 示例：
    # ("ou_xxxxxxxxxxxx", "张三", "在职"),
]

WORK_HOURS = {
    "morning_start": "09:00",
    "morning_end": "12:00",
    "afternoon_start": "14:00",
    "afternoon_end": "19:00",
}


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # 表结构（4 张表）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS members (
        open_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT DEFAULT '在职',
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        open_id TEXT NOT NULL,
        work_date TEXT NOT NULL,
        status TEXT NOT NULL,
        note TEXT,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(open_id, work_date)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leave_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        open_id TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        leave_type TEXT NOT NULL,
        reason TEXT,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS monthly_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year_month TEXT NOT NULL,
        generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        delivered_at TEXT,
        delivered_to TEXT,
        report_content TEXT,
        UNIQUE(year_month)
    )""")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_status_date ON daily_status(work_date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_leave_records_dates ON leave_records(start_date, end_date)")

    # 种子数据
    for open_id, name, status in MEMBERS:
        cur.execute(
            "INSERT OR IGNORE INTO members (open_id, name, status) VALUES (?, ?, ?)",
            (open_id, name, status)
        )

    con.commit()

    # 验证
    cur.execute("SELECT COUNT(*) FROM members")
    n = cur.fetchone()[0]
    print(f"✅ 考勤数据库初始化完成: {DB_PATH}")
    print(f"   人员数: {n}")
    print(f"   工作时间: 上午 {WORK_HOURS['morning_start']}-{WORK_HOURS['morning_end']}, "
          f"下午 {WORK_HOURS['afternoon_start']}-{WORK_HOURS['afternoon_end']}")

    con.close()


if __name__ == "__main__":
    init_db()