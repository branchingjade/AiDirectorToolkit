#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TDB L1 pipeline 端到端诊断脚本

诊断 TDB memory-core 容器 L1 pipeline 配置：
1. 容器 env vars（TDAI_LLM_*）
2. yaml llm 配置（baseUrl vs base_url）
3. NAS 防火墙是否拦截该端点
4. L1 抽取结果（extracted > 0?）

用法：
  python tdb_l1_diag.py                       # 默认 192.168.1.2:8420
  python tdb_l1_diag.py --nas hmsj.local       # 自定义 NAS
  python tdb_l1_diag.py --key sk-mimo-key      # 提供 mimo key 测连通
"""
from __future__ import annotations
import argparse
import shlex
import subprocess
import sys
import urllib.request
import urllib.error
import json

NAS_DEFAULT = "192.168.1.2"
TDB_PORT = 8420


def run_ssh(cmd: str, nas: str) -> str:
    """SSH 到 NAS 执行命令，返回 stdout（用 list 形式避免 shell 注入）"""
    ssh_cmd = ["ssh", f"HMSJadmin@{nas}", f"export PATH=/overlay/upper/usr/bin:/usr/bin:/bin && {cmd}"]
    try:
        r = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception as e:
        return f"[ERR] {e}"


def section(title: str):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nas", default=NAS_DEFAULT)
    ap.add_argument("--key", default="", help="mimo API key（可选）")
    args = ap.parse_args()
    nas = args.nas

    section("1. TDB /health 端到端")
    try:
        req = urllib.request.urlopen(f"http://{nas}:{TDB_PORT}/health", timeout=5)
        d = json.loads(req.read())
        print(f"  OK status={d.get('status')}, vectorStore={d.get('stores',{}).get('vectorStore')}")
    except Exception as e:
        print(f"  ERR {e}")
        return

    section("2. memory-core 容器 env vars (TDAI_LLM_*)")
    # 简单 grep，不用嵌套引号
    out = run_ssh('docker inspect tdb-core --format "{{range .Config.Env}}{{println .}}{{end}}" | grep -E "LLM|MODEL"', nas)
    print(out if out else "  WARN 无 TDAI_LLM_* env vars（默认走 yaml）")

    section("3. yaml llm 配置（注意 base_url vs baseUrl）")
    out = run_ssh('docker exec tdb-core sh -c "cat /data/config/tdai-gateway.yaml"', nas)
    print(out)
    if "base_url:" in out and "baseUrl:" not in out:
        print("  WARN yaml 用下划线 base_url，代码读驼峰 baseUrl → 字段名错配！")

    section("4. NAS 防火墙验证（端点是否可达）")
    for endpoint in ["https://api.openai.com/v1", "https://api.xiaomimimo.com/v1"]:
        out = run_ssh(f'curl -s -m 5 -X POST {endpoint}/chat/completions -H \'Authorization: Bearer test\' -d \'{{}}\' 2>&1 | head -1', nas)
        if "timed out" in out.lower() or "could not resolve" in out.lower():
            print(f"  BLOCKED {endpoint}: {out[:60]}")
        else:
            print(f"  REACHABLE {endpoint}: {out[:60]}")

    section("5. 容器内直连测试（如果提供了 --key）")
    if args.key:
        # 用 here-doc 风格避免引号嵌套
        js_code = (
            'fetch("https://api.xiaomimimo.com/v1/chat/completions",{'
            'method:"POST",'
            'headers:{"Content-Type":"application/json","Authorization":"Bearer ' + args.key + '"},'
            'body:JSON.stringify({model:"mimo-v2.5",messages:[{role:"user",content:"hi"}],max_tokens:20})'
            '}).then(r=>r.text()).then(t=>console.log(t.substring(0,200)))'
        )
        out = run_ssh(f"docker exec tdb-core node -e '{js_code}'", nas)
        print(out)
    else:
        print("  SKIP no --key")

    section("6. L1 pipeline 抽取结果（最近 5 条 L1 complete）")
    out = run_ssh('docker logs tdb-core --tail 200 2>&1 | grep -E "L1 complete" | tail -5', nas)
    print(out if out else "  WARN 暂无 L1 complete 日志")

    section("7. 诊断结论")
    l1_out = run_ssh('docker logs tdb-core --tail 100 2>&1 | grep -E "openai.com|Invalid API"', nas)
    if "openai.com" in l1_out:
        print("  FAIL L1 pipeline 仍走 openai.com — env var 配置未生效或被覆盖")
    elif "Invalid API Key" in l1_out:
        print("  WARN L1 端点已切换到 mimo，但 API key 无效")
        print("       -> 用户需手动更新 docker-compose.yml 里的 TDAI_LLM_API_KEY 为真实值")
    elif "extracted=" in l1_out:
        # 检查 extracted>0
        last = l1_out.split("extracted=")[-1].split(",")[0]
        if last.strip() != "0":
            print(f"  OK L1 pipeline 工作正常（extracted={last}）")
        else:
            print("  WARN L1 仍在 extracted=0")
    else:
        print("  UNKNOWN 状态未知，请检查 docker logs tdb-core --tail 200")


if __name__ == "__main__":
    main()