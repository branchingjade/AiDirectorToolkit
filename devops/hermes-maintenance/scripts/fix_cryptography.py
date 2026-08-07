#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_cryptography.py - 修复 hermes venv 中损坏的 cryptography 安装

背景：hermes update 中断导致 cryptography dist-info 缺失 RECORD/METADATA，
      pip 无法卸载/重装（WinError 5 文件被占用 / invalid metadata 跳过）。
用法：关闭所有 Hermes 窗口（桌面 app + gateway）后，在终端运行：
      cd /d C:/Users/HMSJ/AppData/Local/hermes/hermes-agent
      venv\\Scripts\\python.exe ..\\scripts\\fix_cryptography.py
说明：脚本会 1)备份 2)清损坏 dist-info 3)重装 cryptography 4)验证 import。
"""

import os
import shutil
import subprocess
import sys
import time

HOME = os.environ.get("HERMES_HOME", "C:/Users/HMSJ/AppData/Local/hermes")
VENV = os.path.join(HOME, "hermes-agent", "venv")
SP = os.path.join(VENV, "Lib", "site-packages")
PY = os.path.join(VENV, "Scripts", "python.exe")
VERSION = "48.0.1"  # 与 update 目标一致；如官方已升级可改


def step(msg):
    print("\n=== " + msg + " ===")


def main():
    step("0. 前置检查：确认没有 Hermes 进程占用")
    out = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
         "Where-Object { $_.CommandLine -match 'hermes' } | "
         "Select-Object -ExpandProperty ProcessId"],
        capture_output=True, text=True, timeout=30,
    )
    pids = [l.strip() for l in out.stdout.splitlines() if l.strip().isdigit()]
    if pids:
        print("WARNING: 仍有 Hermes 进程在跑 (PID %s)，请先关闭所有 Hermes 窗口再运行。" % pids)
        sys.exit(1)
    print("OK: 无 Hermes 进程，可以安全修复")

    step("1. 备份现有 cryptography 目录")
    bak = os.path.join(SP, "cryptography.bak-" + str(int(time.time())))
    src = os.path.join(SP, "cryptography")
    if os.path.isdir(src):
        shutil.copytree(src, bak)
        print("OK: 已备份到 " + bak)
    else:
        print("INFO: 无现有目录，跳过备份")

    step("2. 清理损坏的 dist-info")
    removed = 0
    for name in os.listdir(SP):
        if name.startswith("cryptography-") and name.endswith(".dist-info"):
            shutil.rmtree(os.path.join(SP, name), ignore_errors=True)
            print("DEL: " + name)
            removed += 1
    if removed == 0:
        print("INFO: 无 dist-info 需清理")

    step("3. 重装 cryptography==%s" % VERSION)
    r = subprocess.run(
        [PY, "-m", "pip", "install", "--force-reinstall", "--no-deps",
         "cryptography==" + VERSION],
        capture_output=True, text=True, timeout=600,
    )
    print((r.stdout or "")[-1500:])
    if r.returncode != 0:
        print("FAIL: 安装失败:\n" + (r.stderr or "")[-800:])
        sys.exit(2)
    print("OK: 安装完成")

    step("4. 验证 import + 版本")
    r = subprocess.run(
        [PY, "-c", "import cryptography; print('version:', cryptography.__version__)"],
        capture_output=True, text=True, timeout=60,
    )
    print((r.stdout or r.stderr).strip())
    if VERSION not in r.stdout:
        print("FAIL: 版本验证失败")
        sys.exit(3)
    print("OK: 修复完成")

    step("5. 后续：重启 Hermes 桌面 app + gateway")
    print("  1) 打开 Hermes 桌面 app")
    print("  2) 启动 gateway（桌面 app 或 hermes gateway start）")
    print("  3) 恢复 watchdog 计划任务（Enable-ScheduledTask -TaskName Hermes_Gateway_Watchdog）")


if __name__ == "__main__":
    main()
