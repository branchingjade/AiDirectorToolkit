#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书剧本文档拉取→落盘→分页阅读 一步到位。

用法:
  python fetch_feishu_script.py <doc_url> [workdir]

将 lark-cli docs +fetch 的输出落盘为 <workdir>/script.md，
并打印总字符数。后续用分页参数继续读同一文件:
  python -c "t=open('<workdir>/script.md',encoding='utf-8').read(); print(t[起点:终点])"
"""
import json
import os
import subprocess
import sys

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    doc_url = sys.argv[1]
    workdir = sys.argv[2] if len(sys.argv) > 2 else "_work"
    os.makedirs(workdir, exist_ok=True)

    cmd = [
        "lark-cli", "docs", "+fetch",
        "--doc", doc_url,
        "--doc-format", "markdown",
        "--format", "json",
    ]
    env = dict(os.environ)
    env["LARKSUITE_CLI_NO_UPDATE_NOTIFIER"] = "1"
    env["LARKSUITE_CLI_NO_SKILLS_NOTIFIER"] = "1"
    raw = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
    if raw.returncode != 0:
        print("lark-cli 失败(exit=%s): %s" % (raw.returncode, raw.stderr[:2000]))
        sys.exit(raw.returncode or 1)

    data = json.loads(raw.stdout)
    content = data["data"]["document"]["content"]
    out_path = os.path.join(workdir, "script.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("字符数:", len(content))
    print("已保存:", os.path.abspath(out_path))

if __name__ == "__main__":
    main()
