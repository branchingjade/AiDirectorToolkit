#!/usr/bin/env python
"""Hindsight 本地嵌入式记忆 provider 端到端验证脚本。

用途：安装/升级 hindsight-all 后，验证 retain → consolidation → recall 闭环可用。
比手敲 python -c 稳：自动加载 .env、initialize()（配置加载在此方法，直接 new 实例读不到 config）、
处理异步时序（retain 后必须等 consolidation 完成才能 recall 命中）。

用法（务必用 Hermes venv python，勿用系统 python——PYTHONPATH 污染见 hermes-workspace-conventions）：
    cd ~/AppData/Local/hermes/hermes-agent
    venv/Scripts/python.exe <本脚本路径>

预期输出：
    mode: local_embedded | model: deepseek-v4-flash
    retain: {"result": "Memory stored successfully."}
    recall: {"result": "1. ..."}          ← 命中即闭环可用
    E2E PASS

坑（2026-08-07 实测）：
- provider 方法名不是 retain()/recall()，是 handle_tool_call('hindsight_retain'/'hindsight_recall')
- retain 是异步的（retain_async=true）：存完立即 recall 返回 "No relevant memories found"，
  需等 daemon 侧 consolidation（LLM 提取 ~8-10s）完成再查
- daemon 子进程 stderr 有非 UTF-8 字节 → UnicodeDecodeError 噪音，不影响功能
- daemon 日志：~/.hermes/logs/hindsight-embed.log（启动）；~/.hindsight/profiles/hermes.log（consolidation）
- 首次启动 daemon 要下载 embedding 模型，可能很慢；daemon 空闲 5 分钟自动停（idle_timeout=300）
"""
import os
import sys
import time
from pathlib import Path


def main() -> int:
    # 1. 加载真实 .env（HERMES_HOME = LOCALAPPDATA/hermes，不是 ~/.hermes）
    hermes_home = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes"
    env_path = hermes_home / ".env"
    if not env_path.exists():
        print(f"FAIL: 找不到 {env_path}")
        return 1
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k, v)

    sys.path.insert(0, str(hermes_home / "hermes-agent"))
    from plugins.memory.hindsight import HindsightMemoryProvider

    # 2. 实例化 + initialize（配置在 initialize 里才加载）
    p = HindsightMemoryProvider()
    p.initialize("e2e-verify-" + str(int(time.time())))
    print(f"mode: {p._mode} | model: {p._config.get('llm_model')}")
    if p._mode != "local_embedded":
        print(f"FAIL: mode={p._mode}，期望 local_embedded。检查 config.json / .env 三件套。")
        return 1

    # 3. retain
    r = p.handle_tool_call(
        "hindsight_retain",
        {
            "content": f"E2E 验证记忆：Hindsight 插件在 {time.strftime('%Y-%m-%d %H:%M:%S')} 跑通",
            "context": "e2e verification",
        },
    )
    print("retain:", str(r)[:200])
    if "stored successfully" not in str(r):
        print("FAIL: retain 未成功")
        return 1

    # 4. 等 consolidation（异步 LLM 提取），再 recall
    print("等待 consolidation（~12s）...")
    time.sleep(12)
    q = p.handle_tool_call("hindsight_recall", {"query": "E2E 验证记忆 Hindsight"})
    print("recall:", str(q)[:400])
    if "No relevant" in str(q):
        print("WARN: recall 未命中——可能 consolidation 未完成或 embedding 模型首次下载慢，重跑一次。")
        return 2

    print("E2E PASS: retain→consolidation→recall 闭环可用")
    return 0


if __name__ == "__main__":
    sys.exit(main())
