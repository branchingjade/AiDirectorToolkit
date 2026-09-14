#!/usr/bin/env python3
"""OpenViking 团队公共资源灌入脚本（v1.0，2026-08-28 实测落地）

功能：把本地 Markdown / 任意文件灌入 OpenViking 团队公共空间 `viking://resources/<dir>/`，
让团队助手能 find 召回。**绕过 MCP `add_resource` 工具强写 user/ 私有空间的限制**。

用法：
    python ov_public_resource_publish.py <local_file> <target_uri> [--verify]

示例：
    python ov_public_resource_publish.py \
        ./handbook.md \
        "viking://resources/_team-handbook/handbook.md" \
        --verify

凭据：~/.hermes/.env 里的 OPENVIKING_ENDPOINT / OPENVIKING_API_KEY / OPENVIKING_ACCOUNT / OPENVIKING_USER
（**不是** Bearer，是 X-API-Key 三件套；参见 hermes-memory-provider-selection skill §三.五）

依赖：Python 3.10+ 标准库（urllib，无 requests / httpx 依赖）

已知陷阱（写在这里避免重踩）：
1. **POST /api/v1/resources body 用 `to` 字段，不要用 `path`**——`path` 被 silently 忽略，写到 `user/default/resources/` 私有空间
2. **multipart upload 端点 `/api/v1/resources/temp_upload`** 返回 `temp_file_id`，再用此 id 调 add_resource
3. **服务端 ~90s 后台语义索引**——灌完立即 find 大概率抓不到，等一会儿再 verify
4. **删除受 MCP park 限制**——写错位置留 `user/default/resources/<basename>_N` 残留，先评估污染度再决定是否死磕清理
"""
import argparse
import json
import mimetypes
import os
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path

ENV_PATH = Path(os.environ.get("HERMES_HOME", str(Path.home() / "AppData/Local/hermes"))) / ".env"


def load_env(path: Path) -> dict:
    """读 OPENVIKING_* 4 行；找不到则抛错（不要默认 demo key 静默写入）"""
    env = {}
    if not path.exists():
        sys.exit(f"[ERROR] .env 不存在：{path}（参考 hermes-memory-provider-selection skill §三.五获取凭据）")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("OPENVIKING_") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v
    required = ("OPENVIKING_ENDPOINT", "OPENVIKING_API_KEY", "OPENVIKING_ACCOUNT", "OPENVIKING_USER")
    missing = [k for k in required if k not in env]
    if missing:
        sys.exit(f"[ERROR] .env 缺少 {missing}（参考 skill §三.五）")
    # demo token 警告
    demo_decode = "ZGVmYXVsdA"
    if demo_decode in env["OPENVIKING_API_KEY"]:
        print(f"[WARN] API key 含 'default.default' 形态，是 demo token，SaaS 必然 401", file=sys.stderr)
    return env


def multipart_upload(env: dict, local_path: Path) -> str:
    """Step 1: 上传文件到 temp 池，返回 temp_file_id"""
    boundary = "----formboundary-public-publish"
    mime, _ = mimetypes.guess_type(str(local_path))
    mime = mime or "application/octet-stream"
    file_bytes = local_path.read_bytes()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{local_path.name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        f"{env['OPENVIKING_ENDPOINT']}/api/v1/resources/temp_upload",
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-API-Key": env["OPENVIKING_API_KEY"],
            "X-OpenViking-Account": env["OPENVIKING_ACCOUNT"],
            "X-OpenViking-User": env["OPENVIKING_USER"],
        },
        method="POST",
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        result = json.loads(resp.read().decode())
    if result.get("status") != "ok":
        sys.exit(f"[ERROR] multipart 上传失败：{result}")
    return result["result"]["temp_file_id"]


def add_resource(env: dict, temp_file_id: str, target_uri: str) -> dict:
    """Step 2: 把 temp 资源落到目标 URI（关键：用 'to' 不是 'path'）"""
    body = json.dumps({"temp_file_id": temp_file_id, "to": target_uri}).encode()
    req = urllib.request.Request(
        f"{env['OPENVIKING_ENDPOINT']}/api/v1/resources",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": env["OPENVIKING_API_KEY"],
            "X-OpenViking-Account": env["OPENVIKING_ACCOUNT"],
            "X-OpenViking-User": env["OPENVIKING_USER"],
        },
        method="POST",
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        result = json.loads(resp.read().decode())
    return result


def find(env: dict, query: str, target_uri: str = "viking://resources/", limit: int = 3) -> dict:
    """Step 3: verify find 召回"""
    body = json.dumps({"query": query, "target_uri": target_uri, "limit": limit}).encode()
    req = urllib.request.Request(
        f"{env['OPENVIKING_ENDPOINT']}/api/v1/search/search",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": env["OPENVIKING_API_KEY"],
            "X-OpenViking-Account": env["OPENVIKING_ACCOUNT"],
            "X-OpenViking-User": env["OPENVIKING_USER"],
        },
        method="POST",
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        return json.loads(resp.read().decode())


def main():
    parser = argparse.ArgumentParser(description="灌入 OpenViking 团队公共资源")
    parser.add_argument("local_file", type=Path, help="本地文件路径（Markdown / 任意）")
    parser.add_argument("target_uri", help="目标 viking:// URI，如 viking://resources/_team-handbook/foo.md")
    parser.add_argument("--verify", action="store_true", help="灌入后跑一轮 verify find（要等 ~90s 后台索引）")
    parser.add_argument("--verify-query", default=None, help="verify find 的关键词（默认用文件名 basename）")
    args = parser.parse_args()

    if not args.local_file.exists():
        sys.exit(f"[ERROR] 本地文件不存在：{args.local_file}")

    print(f"[INFO] 加载凭据 from {ENV_PATH}")
    env = load_env(ENV_PATH)
    print(f"[INFO] endpoint={env['OPENVIKING_ENDPOINT']}")
    print(f"[INFO] target={args.target_uri}")

    # Step 1
    print(f"[STEP 1] multipart upload...")
    temp_id = multipart_upload(env, args.local_file)
    print(f"[STEP 1] temp_file_id={temp_id}")

    # Step 2
    print(f"[STEP 2] add_resource to {args.target_uri}...")
    result = add_resource(env, temp_id, args.target_uri)
    root_uri = result.get("result", {}).get("root_uri", "N/A")
    warnings = result.get("result", {}).get("warnings", [])
    print(f"[STEP 2] root_uri={root_uri}")
    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")

    # 检查是否真写到目标位置
    if root_uri != args.target_uri:
        print(f"[ERROR] root_uri ({root_uri}) ≠ target ({args.target_uri})，可能写错位置！")
        sys.exit(1)

    # Step 3 (optional)
    if args.verify:
        query = args.verify_query or args.local_file.stem
        print(f"[STEP 3] verify find (query={query!r})...")
        print(f"[INFO] 后台 ~90s 索引——灌完立即 find 可能抓不到，等一会儿再 verify")
        result = find(env, query)
        memories = result.get("result", {}).get("memories", [])
        resources = result.get("result", {}).get("resources", [])
        print(f"[STEP 3] 召回 memories={len(memories)}, resources={len(resources)}")
        for r in resources[:3]:
            print(f"  - {r.get('uri')} (score={r.get('score', 'N/A'):.2f})" if isinstance(r.get('score'), float) else f"  - {r.get('uri')}")

    print(f"[DONE] 团队公共资源已灌入：{root_uri}")


if __name__ == "__main__":
    main()
