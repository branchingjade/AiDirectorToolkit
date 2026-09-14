#!/usr/bin/env python3
"""Migration Value Check — 边际价值评估脚本

在启动记忆批量迁移前，跑这个脚本判定「源数据再灌=边际价值低」还是「值得灌」。

用法：
  python scripts/migration_value_check.py
  python scripts/migration_value_check.py --queries "query1" "query2" ...

输出：
  - 目标 provider 现状量化（已有 L0/L1 数量）
  - 5 个采样 query 的 find() 召回 score + 内容摘要
  - 平均 score + 决策（STOP / PROCEED）

判定标准（2026-08-28 实测）：
  - 平均 score ≥ 50% + 内容带决策摘要/路径标注 → STOP（源数据再灌=边际价值低）
  - 平均 score < 30% 或内容是源数据原文 → PROCEED（进 Phase 3 灌入流程）

依赖：调用方需先加载 ov-mcp-server 工具（find/list）。
"""
import argparse
import json
import statistics
import sys
from typing import List, Dict


DEFAULT_QUERIES = [
    # 覆盖五大维度：核心项目 / 主题 / 角色 / 工具 / 决策
    "<项目名> 主线 一句话故事",
    "<主题> 核心招式 创作密码",
    "<角色名> 设定 关系",
    "<工具名> 配置 端口 协议",
    "用户决策 偏好 拍板",
]

STOP_THRESHOLD = 50.0  # ≥50% 平均 score + 内容是 LLM 精炼版 → STOP
PROCEED_THRESHOLD = 30.0  # <30% → PROCEED


def call_ov_find(query: str, limit: int = 5) -> List[Dict]:
    """调用 OpenViking find() MCP 工具（本机/云服务两套）"""
    try:
        # 尝试 MCP 工具（本机 server 模式）
        from mcp__ov_mcp_server__find import find
        result = find(query=query, limit=limit)
        return result.get("results", [])
    except ImportError:
        pass
    try:
        # SaaS 模式（HTTP REST）
        import os, requests
        ep = os.environ.get("OPENVIKING_ENDPOINT", "")
        if not ep:
            print("❌ OPENVIKING_ENDPOINT 未配置", file=sys.stderr)
            return []
        resp = requests.post(
            f"{ep}/api/v1/search/find",
            json={"query": query, "limit": limit},
            headers={
                "Authorization": f"Bearer {os.environ.get('OPENVIKING_TOKEN', '')}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as e:
        print(f"❌ find() 失败：{e}", file=sys.stderr)
        return []


def parse_score(result: Dict) -> float:
    """从 find() 输出提取 score（不同格式归一化到 0-100）"""
    # 兼容两种格式：MCP 工具输出 [memory 61%]，HTTP 输出 {"score": 0.61}
    if "score" in result:
        s = result["score"]
        return s * 100 if s <= 1.0 else s
    # MCP 文本格式：[memory 61%] xxx
    text = result.get("text", "") or str(result.get("content", ""))
    import re
    m = re.search(r"\[(?:memory|resource)\s+(\d+)%\]", text)
    if m:
        return float(m.group(1))
    return 0.0


def is_refined_content(result: Dict) -> bool:
    """判定内容是否为 LLM 精炼版（带摘要+路径）"""
    text = result.get("text", "") or str(result.get("content", ""))
    # 精炼版特征：含 "# Summary" 标题 + 文件路径标注
    has_summary = "Summary" in text or "总结" in text
    has_path = "viking://" in text or ".md" in text
    return has_summary and has_path


def main():
    ap = argparse.ArgumentParser(description="边际价值评估")
    ap.add_argument("--queries", nargs="*", help="自定义 5 个 query")
    ap.add_argument("--threshold-stop", type=float, default=STOP_THRESHOLD)
    ap.add_argument("--threshold-proceed", type=float, default=PROCEED_THRESHOLD)
    args = ap.parse_args()

    queries = args.queries if args.queries else DEFAULT_QUERIES
    print(f"📊 边际价值评估：{len(queries)} 个 query\n")

    scores = []
    refined_count = 0

    for i, q in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] find('{q}')")
        results = call_ov_find(q, limit=5)
        if not results:
            print("  ❌ 无召回")
            scores.append(0)
            continue

        # 取最高分那条作为代表
        top = max(results, key=lambda r: parse_score(r))
        s = parse_score(top)
        refined = is_refined_content(top)
        scores.append(s)
        if refined:
            refined_count += 1

        preview = (top.get("text", "") or str(top.get("content", "")))[:100].replace("\n", " ")
        print(f"  score={s:.0f}% refined={refined} | {preview}...")

    avg = statistics.mean(scores) if scores else 0
    print(f"\n=== 评估结果 ===")
    print(f"  平均 score: {avg:.1f}%")
    print(f"  精炼版占比: {refined_count}/{len(queries)} ({refined_count/len(queries)*100:.0f}%)")

    # 决策
    if avg >= args.threshold_stop and refined_count >= len(queries) // 2:
        print(f"\n🛑 STOP — 目标 provider 已有 LLM 精炼版（score ≥ {args.threshold_stop}% + 精炼版过半）")
        print(f"   源数据再灌 = 边际价值低，会触发 503 + extraction 队列压力 + 召回噪音")
        sys.exit(0)
    elif avg < args.threshold_proceed:
        print(f"\n✅ PROCEED — 目标 provider recall 不及格（score < {args.threshold_proceed}%）")
        print(f"   进 Phase 3 灌入流程：按主题分桶 + 20 条/批 + 间隔 30s")
        sys.exit(1)
    else:
        print(f"\n⚠️  GRAY ZONE — score {avg:.1f}% 介于阈值之间")
        print(f"   决策权交给用户：是 STOP（保守）还是 PROCEED（补齐知识盲区）")
        sys.exit(2)


if __name__ == "__main__":
    main()