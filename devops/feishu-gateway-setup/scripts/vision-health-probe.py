"""Vision model health probe for Hermes auxiliary.vision.

Verifies the configured auxiliary vision backend can build a client AND
actually perform an image inference (1x1 PNG data URL → expect "红色").

Usage:
    python scripts/vision-health-probe.py

Optional env overrides:
    VISION_PROBE_PROVIDER (default: xiaomi)
    VISION_PROBE_MODEL    (default: mimo-v2.5)

Known pitfall (2026-08-07 实测): reasoning models (mimo-v2.5) return EMPTY
content with max_tokens=20 — the reasoning tokens eat the whole budget
(observed 34 reasoning tokens / 20 budget). Always use max_tokens>=200.
"""
import base64
import os
import sys
import time

os.environ.setdefault("HERMES_HOME", os.path.expanduser(r"~\AppData\Local\hermes"))
sys.path.insert(0, os.path.join(os.environ["HERMES_HOME"], "hermes-agent"))

from agent.auxiliary_client import resolve_provider_client  # noqa: E402

PROVIDER = os.environ.get("VISION_PROBE_PROVIDER", "xiaomi")
MODEL = os.environ.get("VISION_PROBE_MODEL", "mimo-v2.5")

# 1x1 red pixel PNG
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def main() -> int:
    client, resolved_model = resolve_provider_client(
        provider=PROVIDER, model=MODEL, is_vision=True
    )
    if not client:
        print(f"ERR: client build failed for {PROVIDER}/{MODEL}")
        return 1
    print(f"OK client: {resolved_model} @ {client.base_url}")

    data_url = "data:image/png;base64," + base64.b64encode(PNG).decode()
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=resolved_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "这张图片是什么颜色？只答颜色名。"},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            max_tokens=200,
            timeout=90,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERR inference: {type(exc).__name__}: {exc}")
        return 1

    content = (resp.choices[0].message.content or "").strip()
    print(
        f"OK inference {time.time() - t0:.1f}s "
        f"finish={resp.choices[0].finish_reason} content={content[:60]!r}"
    )
    if not content:
        print("WARN: empty content — max_tokens too small for reasoning model")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
