#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书孤儿消息检测 — 抓最近 N 分钟内 lark API 看到的入站消息 vs gateway.log
"Inbound ... message received" 记录，发现孤儿（API 有、log 没有 Inbound）即告警。

场景：bot 收到 raw WebSocket 事件后被 silent drop（mention-only wake / dedup /
_admit 拒绝）——用户消息存在但 bot 不回。

用法：
  python3 'C:/Users/HMSJ/AppData/Local/hermes/scripts/feishu-orphan-messages.py' \\
      --window-minutes 5 --chats oc_b7396f845a84a3aebdb1bf38c872e37a,oc_f7b91a21f9a134dec23959b9af54e6bb

输出：exit code
  0 = 无孤儿
  1 = 有 warn（孤儿消息）
stdout：JSON {window_minutes, api_messages, inbound_messages, orphans:[...]}
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

HERMES_HOME = Path(r"C:/Users/HMSJ/AppData/Local/hermes")
LARK_RUNJS = r"C:\Users\HMSJ\AppData\Local\hermes\node\node_modules\@larksuite\cli\scripts\run.js"
LARK_NODE = r"C:\Users\HMSJ\AppData\Local\hermes\node\node.exe"
GATEWAY_LOG = HERMES_HOME / "logs" / "gateway.log"

# 默认监控的飞书 chat_id（天有答辫群 + 徐学环 DM）
DEFAULT_CHATS = [
    "oc_b7396f845a84a3aebdb1bf38c872e37a",  # 天有答辫群
    "oc_f7b91a21f9a134dec23959b9af54e6bb",  # 徐学环 DM
]

INBOUND_RE = re.compile(
    r"\[Feishu\] Inbound (?:dm|group) message received: id=(om_[0-9a-z]+)"
)


def run_lark(chat_id: str, since: datetime) -> dict:
    """拉最近 N 分钟该 chat 的所有入站消息（bot 身份）"""
    cmd = [
        LARK_NODE, LARK_RUNJS, "im", "+chat-messages-list",
        "--chat-id", chat_id, "--as", "bot",
        "--order", "desc", "--page-limit", "30",
    ]
    try:
        out = subprocess.check_output(cmd, text=True, timeout=30, stderr=subprocess.DEVNULL)
    except Exception as e:
        return {"error": f"lark-cli failed: {e}"}
    idx = out.find("{")
    if idx < 0:
        return {"error": f"lark-cli returned no JSON: {out[:200]}"}
    try:
        return json.loads(out[idx:])
    except Exception as e:
        return {"error": f"json decode failed: {e}: {out[idx():idx+200]}"}


def collect_api_message_ids(data: dict, since: datetime) -> list[dict]:
    """从 lark 返回 data 中提取窗口内 user 消息（过滤 bot/app 自身 + 已删除 + command 类型）。"""
    items = data.get("data", {}).get("messages") or data.get("messages") or []
    matched = []
    for m in items:
        ct_str = m.get("create_time", "")
        try:
            # "2026-08-27 09:12" → 解析为本地时间
            ct = datetime.strptime(ct_str, "%Y-%m-%d %H:%M")
        except Exception:
            continue
        if ct < since:
            continue
        sender = m.get("sender", {})
        if sender.get("sender_type") != "user":
            continue  # 跳过 bot 自己发的
        if m.get("deleted"):
            continue
        # command 类型（/new /status /kanban 等）bot 已走 inbound 拒了，不是孤儿
        if m.get("msg_type") == "text":
            content = m.get("content", "") or ""
            try:
                parsed = json.loads(content)
                text = parsed.get("text", "") if isinstance(parsed, dict) else ""
            except Exception:
                text = content
            if text.strip().startswith("/"):
                continue
        matched.append({
            "message_id": m.get("message_id", ""),
            "create_time": ct_str,
            "sender": sender.get("name") or sender.get("id", "?"),
            "msg_type": m.get("msg_type", "?"),
            "content_preview": (m.get("content", "") or "")[:80],
        })
    return matched


def collect_inbound_ids(since: datetime) -> set[str]:
    """从 gateway.log 中提取窗口内所有 Inbound 消息的 message_id"""
    ids = set()
    if not GATEWAY_LOG.exists():
        return ids
    # 简单扫描：grep 不带时间过滤先拿 id，再按时间过滤
    # 因日志大，限定窗口
    cutoff_line = since.strftime("%Y-%m-%d %H:%M")
    keep = False
    try:
        with GATEWAY_LOG.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # 提取行首时间戳
                ts_m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2})", line)
                if ts_m:
                    ts_str = ts_m.group(1)
                    keep = ts_str >= cutoff_line
                if not keep:
                    continue
                for m in INBOUND_RE.finditer(line):
                    ids.add(m.group(1))
    except Exception as e:
        print(json.dumps({"error": f"log read failed: {e}"}))
    return ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-minutes", type=int, default=5)
    ap.add_argument("--chats", default=",".join(DEFAULT_CHATS))
    args = ap.parse_args()

    since = datetime.now() - timedelta(minutes=args.window_minutes)
    chats = [c.strip() for c in args.chats.split(",") if c.strip()]

    api_messages: list[dict] = []
    errors: list[str] = []
    for chat_id in chats:
        data = run_lark(chat_id, since)
        if "error" in data:
            errors.append(f"{chat_id}: {data['error']}")
            continue
        api_messages.extend(collect_api_message_ids(data, since))

    inbound_ids = collect_inbound_ids(since)

    # 孤儿 = API 看到但 log 没 Inbound
    orphans = [m for m in api_messages if m["message_id"] not in inbound_ids]

    result = {
        "window_minutes": args.window_minutes,
        "since": since.strftime("%Y-%m-%d %H:%M"),
        "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chats_monitored": len(chats),
        "api_messages_seen": len(api_messages),
        "inbound_logged": len(inbound_ids),
        "orphans": orphans,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if orphans else 0


if __name__ == "__main__":
    sys.exit(main())