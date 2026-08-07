#!/usr/bin/env python3
"""
Hermes Agent 版本监控 — 分级过滤 + 中文简报。
用于 cron no_agent=True 模式：有新版本时 stdout → 推送，无新版本静默退出。

部署：cp 到 ~/.hermes/scripts/，创建 cron job 引用文件名即可。
"""

import json, re, os, sys
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

REPO = "NousResearch/hermes-agent"
API_BASE = f"https://api.github.com/repos/{REPO}"
STATE_FILE = os.path.expanduser("~/.hermes/last_hermes_release.txt")

# ── 用户关注的分类 ──────────────────────────────────────────
CATEGORY_PRIORITY = {
    "BREAKING":    {"emoji": "🚨", "label": "破坏性变更"},
    "SECURITY":    {"emoji": "🔒", "label": "安全"},
    "HIGHLIGHTS":  {"emoji": "✨", "label": "亮点"},
    "WINDOWS":     {"emoji": "🪟", "label": "Windows"},
    "DESKTOP":     {"emoji": "🖥️", "label": "桌面端"},
    "DASHBOARD":   {"emoji": "📊", "label": "Dashboard"},
    "CLI_TUI":     {"emoji": "⌨️", "label": "CLI/TUI"},
    "TOOLS_MCP":   {"emoji": "🔧", "label": "工具/MCP"},
    "CORE":        {"emoji": "🏗️", "label": "核心架构"},
    "FEISHU":      {"emoji": "📱", "label": "飞书"},
    "OTHER":       {"emoji": "📌", "label": "其他"},
}

SECTION_RULES = [
    (["breaking", "⚠️", "deprecated", "removed"], "BREAKING"),
    (["security", "安全", "vulnerability", "cve"], "SECURITY"),
    (["highlight"], "HIGHLIGHTS"),
    (["window"], "WINDOWS"),
    (["desktop"], "DESKTOP"),
    (["dashboard"], "DASHBOARD"),
    (["cli", "tui", "setup"], "CLI_TUI"),
    (["tool", "skill", "mcp"], "TOOLS_MCP"),
    (["core", "agent", "architecture"], "CORE"),
    (["feishu", "lark", "飞书"], "FEISHU"),
]

RELEVANT_KEYWORDS = [
    "windows", "win32", "desktop", "dashboard", "cli", "tui",
    "terminal", "tool", "skill", "mcp", "memory", "browser",
    "feishu", "lark", "飞书", "gateway", "deepseek", "mimo",
    "cron", "checkpoint", "config", "profile",
]

SKIP_KEYWORDS = [
    "discord", "slack", "telegram", "whatsapp", "signal",
    "matrix", "imessage", "photon", "bluebubbles",
    "docker", "nix", "linux-only", "macos-only", "darwin",
]


def get_releases(count=5):
    url = f"{API_BASE}/releases?per_page={count}"
    req = Request(url, headers={"User-Agent": "Hermes-Release-Monitor/1.0", "Accept": "application/vnd.github+json"})
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except URLError as e:
        print(f"GitHub API 错误: {e}", file=sys.stderr)
        return []


def get_last_seen():
    try:
        with open(STATE_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def set_last_seen(tag):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        f.write(tag)


def extract_timeline(body):
    m = re.search(r'> \*\*(.+?)\*\*', body)
    if m:
        return m.group(1)
    m = re.search(r'\*\*(.+?)\*\*', body)
    return m.group(1) if m else ""


def extract_breaking(body):
    """只抓明确标记 BREAKING 或 ⚠️ 的列表项。"""
    items = []
    for line in body.split("\n"):
        stripped = line.strip()
        if not re.search(r'(BREAKING|⚠️)', stripped, re.IGNORECASE):
            continue
        if not (stripped.startswith("- ") or stripped.startswith("* ")):
            continue
        cleaned = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped[2:])
        cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
        cleaned = cleaned.strip()
        if len(cleaned) < 15:
            continue
        if re.search(r'(optimization|only|default)', cleaned, re.IGNORECASE) and not re.search(r'removed|no longer|must|break', cleaned, re.IGNORECASE):
            continue
        items.append(cleaned[:130])
    return items[:3]


def is_relevant_to_user(line):
    lower = line.lower()
    for kw in SKIP_KEYWORDS:
        if kw in lower:
            return False
    for kw in RELEVANT_KEYWORDS:
        if kw in lower:
            return True
    if re.search(r'(highlight|breaking|security|⚠️)', lower):
        return True
    return True


def extract_section_items(body, heading_pattern, max_items=2):
    pattern = re.compile(rf'^{heading_pattern}$', re.MULTILINE)
    m = pattern.search(body)
    if not m:
        return []
    start = m.end()
    next_section = re.search(r'^## ', body[start:], re.MULTILINE)
    end = start + next_section.start() if next_section else len(body)
    section_body = body[start:end]
    items = []
    for line in section_body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            cleaned = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped[2:])
            cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
            cleaned = cleaned.strip()
            if re.search(r'extracted|reorganized|moved to|split into|rename|refactor', cleaned, re.IGNORECASE):
                continue
            if len(cleaned) < 8:
                continue
            if is_relevant_to_user(cleaned):
                items.append(cleaned[:120])
    return items[:max_items]


def format_release(r):
    tag = r["tag_name"]
    name = r["name"]
    body = r.get("body", "")
    published = r["published_at"][:10]
    prerelease = r.get("prerelease", False)
    draft = r.get("draft", False)
    tagline = extract_timeline(body)
    lines = []
    prerelease_tag = " [预发布]" if prerelease else ""
    draft_tag = " [草稿]" if draft else ""
    if tagline:
        lines.append(f"📦 {name}{prerelease_tag}{draft_tag} — {tagline}")
    else:
        lines.append(f"📦 {name}{prerelease_tag}{draft_tag}")
    lines.append(f"   日期: {published}  |  tag: {tag}")
    breaking = extract_breaking(body)
    if breaking:
        lines.append(f"  🚨 破坏性变更:")
        for b in breaking:
            lines.append(f"     • {b}")
    sec_items = extract_section_items(body, r"## 🔒 Secur.+", max_items=2)
    if sec_items:
        lines.append(f"  🔒 安全修复:")
        for s in sec_items:
            lines.append(f"     • {s}")
    win_items = extract_section_items(body, r"## 🪟 Windows", max_items=2)
    if win_items:
        lines.append(f"  🪟 Windows:")
        for w in win_items:
            lines.append(f"     • {w}")
    section_map = {
        "🖥️ Hermes Desktop": ("DESKTOP", "桌面端"),
        "📊 Web Dashboard": ("DASHBOARD", "Dashboard"),
        "🖥️ CLI.*TUI": ("CLI_TUI", "CLI/TUI"),
        "🔧 Tool.*Skill.*MCP": ("TOOLS_MCP", "工具/MCP"),
        "🏗️ Core Agent": ("CORE", "核心"),
        "📱 Messaging": ("FEISHU", "消息平台"),
    }
    for pattern, (cat_key, cat_label) in section_map.items():
        items = extract_section_items(body, rf"## {pattern}.+", max_items=2)
        if cat_key == "FEISHU":
            items = [i for i in items if any(kw in i.lower() for kw in ["feishu", "lark", "飞书", "gateway"])]
        if items:
            info = CATEGORY_PRIORITY.get(cat_key, CATEGORY_PRIORITY["OTHER"])
            lines.append(f"  {info['emoji']} {cat_label}:")
            for item in items:
                lines.append(f"     • {item}")
    return "\n".join(lines)


def main():
    releases = get_releases(5)
    if not releases:
        return
    last_tag = get_last_seen()
    releases.sort(key=lambda r: r["published_at"])
    new_releases = []
    found_last = (last_tag is None)
    for r in releases:
        if not found_last:
            if r["tag_name"] == last_tag:
                found_last = True
            continue
        new_releases.append(r)
    if not new_releases:
        return
    print("─" * 50)
    print("  Hermes Agent 版本更新简报")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("─" * 50)
    print()
    for r in new_releases:
        if r.get("draft"):
            continue
        print(format_release(r))
        print()
    latest_tag = releases[-1]["tag_name"]
    set_last_seen(latest_tag)
    total = len(new_releases)
    breaking_count = sum(1 for r in new_releases if extract_breaking(r.get("body", "")))
    print(f"📋 本次共 {total} 个新版本")
    if breaking_count:
        print(f"🚨 其中 {breaking_count} 个版本含破坏性变更，请及时关注")


if __name__ == "__main__":
    main()
