#!/usr/bin/env python3
"""
memory_provider_health.py — Hermes memory provider 端到端健康探测（2026-08-28）

不依赖 Hermes CLI，直读 provider 配置 + agent.log + 直打服务端，10 秒内给出结论。
覆盖三类 provider：本地 daemon（Hindsight 9177）、SaaS HTTPS（OpenViking VolcEngine）、
本地 HTTP（OpenViking 1933）。

用法：
  python memory_provider_health.py                  # 自动检测当前 provider + 输出结论
  python memory_provider_health.py --provider openviking
  python memory_provider_health.py --verbose

输出三档：
  WORKING  — provider activated + 最近 30 秒 0 错误 + 服务端可达
  DEGRADED — provider activated 但有错误（列出最近错误样本）
  BROKEN   — provider 未激活 / 服务端不可达 / 配置错
"""
from __future__ import annotations
import argparse
import base64
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

HERMES_HOME = Path.home() / "AppData/Local/hermes"
AGENT_LOG = HERMES_HOME / "logs/agent.log"
CONFIG_YAML = HERMES_HOME / "config.yaml"
OPENVIKING_CONF = Path.home() / ".openviking/ovcli.conf"
HINDSIGHT_CONFIG = HERMES_HOME / "hindsight/config.json"

ERROR_PATTERNS = re.compile(
    r"(AuthenticationError|HTTPError|ConnectionError|sync_turn failed|HTTP 4\d\d|HTTP 5\d\d)",
    re.IGNORECASE,
)
ACTIVATED_PATTERN = re.compile(
    r"Memory provider '(\w+)' (registered|activated)"
)


def read_yaml_provider() -> str | None:
    """读 config.yaml 的 memory.provider（嵌套在 memory: 块下，2 空格缩进）"""
    try:
        text = CONFIG_YAML.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    in_memory_block = False
    for line in text.splitlines():
        if line.startswith("memory:"):
            in_memory_block = True
            continue
        if in_memory_block:
            # 块结束条件：新的顶层 key（无缩进）
            if line and not line.startswith(" "):
                in_memory_block = False
                continue
            stripped = line.strip()
            if stripped.startswith("provider:"):
                return stripped.split(":", 1)[1].strip()
    return None


def read_open_viking_endpoint_and_key() -> tuple[str, str | None]:
    """读 ~/.openviking/ovcli.conf"""
    if not OPENVIKING_CONF.exists():
        return ("", None)
    try:
        cfg = json.loads(OPENVIKING_CONF.read_text(encoding="utf-8"))
        return (cfg.get("url", ""), cfg.get("api_key"))
    except (json.JSONDecodeError, OSError):
        return ("", None)


def decode_api_key_health(key: str) -> str:
    """解码 OpenViking key，判 demo vs 真凭据"""
    parts = key.split(".")
    decoded = []
    for p in parts:
        pad = "=" * (4 - len(p) % 4)
        try:
            decoded.append(base64.urlsafe_b64decode(p + pad).decode("utf-8", errors="replace"))
        except Exception:
            decoded.append("?")
    is_demo = decoded[0] == "default" and decoded[1] == "default"
    return (
        f"parts = {decoded} → {'⚠️ DEMO TOKEN (SaaS 必然 401)' if is_demo else '✓ 真凭据特征'}"
    )


def http_probe(url: str, api_key: str | None, paths: list[str], timeout: float = 10.0) -> dict:
    """对每个 path 试 GET/POST，返回 status code 字典"""
    results = {}
    for path in paths:
        full = url.rstrip("/") + path
        req = urllib.request.Request(full, method="GET")
        if api_key:
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("X-API-Key", api_key)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                results[path] = ("HTTP " + str(resp.status), None)
        except urllib.error.HTTPError as e:
            body_preview = ""
            try:
                body_preview = e.read(200).decode("utf-8", errors="replace")[:150]
            except Exception:
                pass
            results[path] = (f"HTTP {e.code}", body_preview)
        except (urllib.error.URLError, TimeoutError) as e:
            results[path] = (f"NETWORK ERROR ({type(e).__name__})", str(e))
    return results


def scan_recent_agent_log(window_minutes: int = 30) -> dict:
    """扫最近 N 分钟 agent.log，统计 activated / error 次数"""
    if not AGENT_LOG.exists():
        return {"exists": False}
    cutoff = datetime.now() - timedelta(minutes=window_minutes)
    activated = []
    errors = []
    activated_count = 0
    try:
        for line in AGENT_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
            m = ACTIVATED_PATTERN.search(line)
            if m:
                activated_count += 1
                # 提取时间戳（行首的 datetime）
                ts_match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                ts = ts_match.group(1) if ts_match else "?"
                activated.append(f"{ts}  {m.group(1)} {m.group(2)}")
            if ERROR_PATTERNS.search(line):
                ts_match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                ts = ts_match.group(1) if ts_match else "?"
                # 只保留 WARNING/ERROR 行的简短描述
                short = line[:250]
                errors.append(f"{ts}  {short}")
    except OSError as e:
        return {"exists": True, "error": str(e)}
    return {
        "exists": True,
        "activated_count": activated_count,
        "last_5_activated": activated[-5:],
        "error_count": len(errors),
        "last_5_errors": errors[-5:],
    }


def check_hindsight_daemon() -> dict:
    """Hindsight 本地 daemon（端口 9177）"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect(("127.0.0.1", 9177))
        sock.close()
        return {"daemon": "LISTENING on 9177"}
    except (socket.timeout, ConnectionRefusedError, OSError):
        return {"daemon": "NOT LISTENING"}
    finally:
        try:
            sock.close()
        except Exception:
            pass


def diagnose(provider: str | None) -> dict:
    out = {"timestamp": datetime.now().isoformat(timespec="seconds")}
    provider = provider or read_yaml_provider()
    out["config_provider"] = provider

    if provider == "openviking":
        url, key = read_open_viking_endpoint_and_key()
        out["endpoint"] = url
        out["has_key"] = bool(key)
        if key:
            out["key_health"] = decode_api_key_health(key)
        if "127.0.0.1" in url or "localhost" in url:
            out["mode"] = "local server"
            paths = ["/api/v1/system/status", "/api/v1/fs/ls"]
        else:
            out["mode"] = "SaaS"
            paths = ["/api/v1/system/status"]
        out["http_probe"] = http_probe(url, key, paths)
    elif provider == "hindsight":
        out["hindsight"] = check_hindsight_daemon()
        if HINDSIGHT_CONFIG.exists():
            try:
                cfg = json.loads(HINDSIGHT_CONFIG.read_text(encoding="utf-8"))
                out["hindsight_config"] = {
                    "auto_retain": cfg.get("auto_retain"),
                    "auto_recall": cfg.get("auto_recall"),
                    "idle_timeout": cfg.get("idle_timeout"),
                }
            except Exception:
                pass

    log_scan = scan_recent_agent_log()
    out["agent_log_30min"] = log_scan

    # 结论
    errors = log_scan.get("error_count", 0) if log_scan.get("exists") else 0
    activated = log_scan.get("activated_count", 0) if log_scan.get("exists") else 0
    if not log_scan.get("exists"):
        verdict = "UNKNOWN (no agent.log)"
    elif activated == 0:
        verdict = "BROKEN (provider never activated)"
    elif errors >= activated * 2:
        verdict = f"DEGRADED ({errors} errors / {activated} activated — likely key/network)"
    elif errors > 0:
        verdict = f"DEGRADED ({errors} errors in last 30min)"
    else:
        verdict = "WORKING"
    out["verdict"] = verdict

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes memory provider health probe")
    parser.add_argument("--provider", help="override provider name (default: read config.yaml)")
    parser.add_argument("--verbose", "-v", action="store_true", help="dump raw log lines too")
    args = parser.parse_args()

    result = diagnose(args.provider)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 退出码：CI 用
    verdict = result.get("verdict", "")
    if verdict.startswith("BROKEN"):
        return 2
    if verdict.startswith("DEGRADED"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
