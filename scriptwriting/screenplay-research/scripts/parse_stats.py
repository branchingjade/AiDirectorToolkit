"""剧本格式启发式统计器：场景标题 / 角色提示 / 对白 / 动作 词数与行数。

用法: python parse_stats.py file1.txt [file2.txt ...]
输出: 词数、标题数、提示数、对白%/动作%、平均行词数（含折行）。
口径: 启发式状态机，百分比仅作横向比较；统计前自动归一化 CRLF 与 formfeed。
"""
import re
import sys


def parse(path):
    raw = open(path, encoding="utf-8", errors="ignore").read()
    raw = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    lines = raw.split("\n")
    state = "action"  # action | cue | dialogue | paren
    stats = {
        "headings": 0, "cues": 0, "action_words": 0, "dialogue_words": 0,
        "action_lines": 0, "dialogue_lines": 0, "total_words": 0,
    }
    cue_re = re.compile(r"^\s*([A-Z][A-Z0-9 &'.\-]{1,28})\s*$")
    for l in lines:
        s = l.strip()
        if not s:
            continue
        w = len(s.split())
        stats["total_words"] += w
        # 场景标题：行首 INT/EXT 系列，或"编号+字母后缀 + INT/EXT"（肖申克/寄生虫编号制；
        # 字母后缀 17A/45A 为拍摄稿插入场，2026-08-05 实测《房间》严格版漏数 32%）
        if re.match(r"^\s*\d{1,3}[A-Z]?\s+(INT|EXT|INT/EXT|I/E)[\.\s]", l) or re.match(r"^\s*(INT|EXT|EST|I/E)\.", l):
            state = "action"
            stats["headings"] += 1
            continue
        m = cue_re.match(l)
        if m and len(m.group(1).split()) <= 4 and state != "dialogue":
            # 排除大写动作片段（'AN OLD PHOTO.' 以句点/冒号结尾）
            if not m.group(1).endswith(".") and not s.endswith(":"):
                state = "cue"
                stats["cues"] += 1
                continue
        if state == "cue" or state == "paren":
            state = "paren" if s.startswith("(") else "dialogue"
            stats["dialogue_words"] += w
            stats["dialogue_lines"] += 1
            continue
        if state == "dialogue" and not cue_re.match(l):
            stats["dialogue_words"] += w
            stats["dialogue_lines"] += 1
            continue
        state = "action"
        stats["action_words"] += w
        stats["action_lines"] += 1
    return stats


if __name__ == "__main__":
    for path in sys.argv[1:]:
        st = parse(path)
        tw = st["total_words"] or 1
        print(f"{path}:")
        print(f"  words={tw} headings={st['headings']} cues={st['cues']}")
        print(f"  dialogue={st['dialogue_words']} ({100*st['dialogue_words']//tw}%)  action={st['action_words']} ({100*st['action_words']//tw}%)")
        print(f"  action: {st['action_lines']} lines, avg {st['action_words']/max(1,st['action_lines']):.1f} w/line;  dialogue: {st['dialogue_lines']} lines, avg {st['dialogue_words']/max(1,st['dialogue_lines']):.1f} w/line")
        print()
