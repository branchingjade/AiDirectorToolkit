#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hindsight recall 验证脚本 — 验证外部记忆能否召回指定内容（如飞书协作内容）。

前置条件：
1. hindsight-api 已在 9177 端口运行且连对数据库（见 SKILL.md「手动启动 API」，
   必须 source hermes.env + export HINDSIGHT_API_DATABASE_URL 指向 5433）
2. 用法：python recall_check.py

核心思路：对每个查询跑 recall（observation 与全类型各一次），标记每条结果为
飞书内容或桌面内容，判断召回是否打通。修改 QUERIES 列表适配新验证场景。
"""
import json
import urllib.request

BASE = "http://127.0.0.1:9177/v1/default/banks/hermes/memories/recall"

# 每项: (名称, 查询词, [飞书关键词列表]) — 飞书关键词用于标记结果归属
QUERIES = [
    ("飞书-魔王项目", "魔王 收购谈判 圣晶石 金玄 白泽 八千万债务",
     ["魔王", "收购", "八千万", "圣晶", "金玄", "白泽", "萧烬", "神域",
      "谈判", "工友鼓掌", "阿蜥", "林虽然", "施文皓", "陈星艳", "苑津铭", "全志越"]),
    ("飞书-工友鼓掌/神域", "工友鼓掌 神域 披风 阿蜥 萧烬",
     ["魔王", "神域", "金玄", "白泽", "萧烬", "阿蜥", "工友鼓掌", "林虽然"]),
]

TYPES_VARIANTS = [
    ("observation-only", ["observation"]),
    ("all-types", ["world", "experience", "observation"]),
]


def recall(query, types=None, budget="high", max_tokens=8192):
    body = {"query": query, "budget": budget, "max_tokens": max_tokens}
    if types is not None:
        body["types"] = types
    req = urllib.request.Request(
        BASE,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return None, {"error": str(e)}


def is_feishu(text, feishu_kws):
    return any(k in text for k in feishu_kws)


def main():
    for name, query, feishu_kws in QUERIES:
        for tname, types in TYPES_VARIANTS:
            status, d = recall(query, types)
            print("=" * 70)
            print(f"[{name} / {tname}] query={query} status={status}")
            if status != 200:
                print("  ERROR:", json.dumps(d, ensure_ascii=False)[:300])
                continue
            results = d.get("results", [])
            feishu_hits = [r for r in results if is_feishu(r.get("text", ""), feishu_kws)]
            print(f"  results={len(results)} feishu_hits={len(feishu_hits)}")
            for i, r in enumerate(results):
                t = r.get("text", "").replace("\n", " ").strip()
                tag = "[飞书]" if is_feishu(t, feishu_kws) else "[桌面]"
                print(f"  {tag} [{i}] {t[:150]}")
            if len(feishu_hits) == 0:
                print("  ⚠️ 无飞书命中：先查 stats.total_nodes 确认连对库，再查 consolidation 积压")


if __name__ == "__main__":
    main()
