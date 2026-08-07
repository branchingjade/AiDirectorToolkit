#!/usr/bin/env python3
"""alist WebDAV 一键自检脚本。

检查链路：登录 → 存储列表 → WebDAV PROPFIND（根 + 挂载路径）→ 全局设置。

用法：
    python3 webdav-check.py [--host localhost] [--port 5244] [--user admin] [--password ...]

修改密码/修复 db 后跑一次，验证全链路是否恢复。
"""

import argparse
import base64
import json
import re
import urllib.parse
import urllib.request


def api(base, path, method="GET", body=None, token=None):
    url = f"{base}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if token:
        req.add_header("Authorization", token)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", default=5244, type=int)
    ap.add_argument("--user", default="admin")
    ap.add_argument("--password", required=True)
    args = ap.parse_args()

    base = f"http://{args.host}:{args.port}"

    # 1. 登录
    resp = api(base, "/api/auth/login", method="POST",
               body={"username": args.user, "password": args.password})
    if resp.get("code") != 200:
        print(f"✗ 登录失败: {resp.get('message')}")
        print("  排查：用户名是否权威（跑 alist admin 确认）？密码是否被清空（读 SQLite pw_len）？")
        return 1
    token = resp["data"]["token"]
    print(f"✓ 登录成功 ({args.user})")

    # 2. 存储列表
    resp = api(base, "/api/admin/storage/list", token=token)
    total = resp["data"]["total"]
    print(f"✓ 存储数量: {total}")
    for s in resp["data"]["content"]:
        try:
            add = json.loads(s.get("addition", "{}"))
        except json.JSONDecodeError:
            add = {}
        print(f"  ├─ ID={s['id']} {s['mount_path']} ({s['driver']}) 状态={s['status']}")
        print(f"  │  WebDAV策略={s.get('webdav_policy')}")
        print(f"  │  root_folder={add.get('root_folder_path')}")
        rt = add.get("refresh_token", "")
        print(f"  └─ refresh_token={rt[:20] + '...' if rt else '空！'}")

    if total == 0:
        print("✗ 存储为空——可能 server 读错了数据库（db_file 路径问题）")
        return 1

    # 3. WebDAV PROPFIND
    auth = base64.b64encode(f"{args.user}:{args.password}".encode()).decode()
    print()
    for path, label in [("/dav", "根"), ("/dav/" + urllib.parse.quote("百度网盘"), "百度网盘")]:
        req = urllib.request.Request(f"{base}{path}", method="PROPFIND")
        req.add_header("Authorization", f"Basic {auth}")
        req.add_header("Depth", "1")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                n = body.count("<D:response>")
                print(f"✓ PROPFIND {label} -> HTTP {resp.status}, {n} 项")
                errs = re.findall(r"<D:responsedescription>(.*?)</D:responsedescription>", body)
                for e in errs:
                    print(f"  ⚠️ {e}")
        except urllib.error.HTTPError as e:
            print(f"✗ PROPFIND {label} -> HTTP {e.code}")
            body = e.read().decode("utf-8", errors="replace")
            if "D:error" in body:
                errs = re.findall(r"<D:responsedescription>(.*?)</D:responsedescription>", body)
                print(f"  错误: {errs}")
        except Exception as e:
            print(f"✗ PROPFIND {label} -> {e}")

    # 4. 全局设置
    print()
    resp = api(base, "/api/admin/setting/list", token=token)
    settings = {s["key"]: s["value"] for s in resp.get("data", [])}
    for k in ("sign_all", "allow_indexed", "allow_mounted", "version"):
        print(f"✓ {k}={settings.get(k)}")

    print()
    print("✅ 自检完成" if total > 0 else "❌ 自检发现问题")
    return 0 if total > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
