#!/usr/bin/env python3
"""OpenViking 团队公共空间盘点脚本（v1.0，2026-08-28 实测落地）

功能：列出 `viking://resources/` 下所有 URI，按一级目录统计，
     检查命名规范违规，输出 inventory 报告。

用法：
    python ov_public_inventory.py [--target-uri viking://resources/] [--limit 500] [--output inventory.md]

为什么这个脚本独立于 `ov_public_resource_publish.py`：
- 那是**写**资源（up 流量）
- 这是**盘点**资源（read 流量），on-demand / 季度跑

已知陷阱：
1. **盘点端点用 `/api/v1/search/search`** + `target_uri=viking://resources/` + 大 limit（500+），
   不是 `/api/v1/fs/ls`（该端点对部分 user 不开放或返回空）
2. **`.abstract.md` / `.overview.md` 是服务端自动生成的 LLM 摘要**，
   正常盘点时算"已索引"标志，不要当成污染内容
3. **顶层目录命名规范**（2026-08-28 团队规则）：
   - 下划线前缀 = 团队公共资源（`_team-handbook/` / `_test/` / `_archive/`）
   - kebab-case = 业务资源（`skills/` / `openviking-docs/` / `yaoyu-knowledge-base/`）
   - 全大写 / 含空格 / 中文标点 = 违规
4. **返回的 unique URI 数 vs parent dir 文件数**应接近 1:1（差异大 = 同步未清）
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict, Counter
from pathlib import Path

ENV_PATH = Path(os.environ.get("HERMES_HOME", str(Path.home() / "AppData/Local/hermes"))) / ".env"


def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("OPENVIKING_") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v
    return env


def list_resources(endpoint, env, target_uri, limit):
    """POST /api/v1/search/search 列目标 URI 下所有资源"""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": env["OPENVIKING_API_KEY"],
        "X-OpenViking-Account": env["OPENVIKING_ACCOUNT"],
        "X-OpenViking-User": env["OPENVIKING_USER"],
    }
    body = json.dumps({"query": "目录", "limit": limit, "target_uri": target_uri}).encode()
    req = urllib.request.Request(f"{endpoint}/api/v1/search/search", data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        r = json.loads(resp.read().decode())
        return sorted(set(x.get("uri", "") for x in r.get("result", {}).get("resources", [])))


def check_naming(uri):
    """返回 (is_violation, reason)"""
    name = uri.split("/")[-1]
    # 全大写（README / LICENSE / SOP 例外）
    if name.isupper() and name not in ("README", "LICENSE", "SOP"):
        return True, "全大写"
    # 含空格
    if " " in name:
        return True, "含空格"
    # 中文标点
    if re.search(r"[，。！？、；：]", name):
        return True, "中文标点"
    # 顶层目录命名
    top_match = re.match(r"viking://resources/([^/]+)/", uri)
    if top_match:
        top = top_match.group(1)
        # 业务资源（不是团队公共前缀）应该是 kebab-case
        if not top.startswith("_") and "_" in top:
            return True, f"业务目录 `{top}/` 含下划线（应用 kebab-case）"
        # 团队公共资源应该是下划线前缀
        if top.startswith("_") and not re.match(r"^_[a-z0-9-]+$", top):
            return True, f"团队公共目录 `{top}/` 命名违规"
    return False, ""


def main():
    parser = argparse.ArgumentParser(description="盘点 OpenViking 团队公共空间")
    parser.add_argument("--target-uri", default="viking://resources/", help="盘点根 URI")
    parser.add_argument("--limit", type=int, default=500, help="最大拉取数")
    parser.add_argument("--output", help="输出文件路径（可选）")
    args = parser.parse_args()

    env = load_env(ENV_PATH)
    if not env.get("OPENVIKING_API_KEY"):
        print("错误：~/.hermes/.env 缺 OPENVIKING_API_KEY", file=sys.stderr)
        sys.exit(1)

    print(f"盘点 {args.target_uri} (limit={args.limit})...")
    uris = list_resources(env["OPENVIKING_ENDPOINT"], env, args.target_uri, args.limit)
    print(f"共 {len(uris)} 个 unique URI")

    # 统计
    top_dirs = Counter()
    abstract_count = sum(1 for u in uris if ".abstract.md" in u)
    overview_count = sum(1 for u in uris if ".overview.md" in u)
    for uri in uris:
        m = re.match(r"viking://resources/([^/]+)/", uri)
        if m:
            top_dirs[m.group(1)] += 1

    # 命名规范违规检查
    violations = []
    for uri in uris:
        is_viol, reason = check_naming(uri)
        if is_viol:
            violations.append((uri, reason))

    # 报告
    report = f"""# OV 公共空间盘点报告 ({time.strftime("%Y-%m-%d")})

> **盘点目标**：`{args.target_uri}`
> **总条目**：{len(uris)} unique URIs

## 一级目录统计

| 目录 | 条目数 |
|---|---|
"""
    for d, c in top_dirs.most_common():
        report += f"| `{d}/` | {c} |
"

    report += f"""
**派生**：`.abstract.md`={abstract_count} / `.overview.md`={overview_count}

## 命名规范违规（{len(violations)} 条）

"""
    if violations:
        for uri, reason in violations[:20]:
            report += f"- ❌ `{uri}` — {reason}
"
        if len(violations) > 20:
            report += f"- ... 还有 {len(violations) - 20} 条
"
    else:
        report += "- ✅ 无违规
"

    print(report)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"已写入 {args.output}")


import time  # noqa: E402

if __name__ == "__main__":
    main()
