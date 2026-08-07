#!/usr/bin/env python3
"""Chromium 扩展清单审计（Edge/Chrome）—— i18n 名解析 + 启用状态 + 拦截权限。

为什么需要它：2026-08 实测，grep manifest.json 的 "name" 字段会把 i18n 化的
扩展显示成 __MSG_name__ 占位符（Adblock Plus 就是这样被漏掉的），导致"扩展层
已排除"的错误结论。本脚本以磁盘扩展目录为准 + 解析 _locales 真实名 + 读
Secure Preferences 的 disable_reasons 判断启用状态 + 标记有网络拦截权限的扩展。

用法：
  python chromium-extensions.py edge
  python chromium-extensions.py chrome
  python chromium-extensions.py all

输出列：启用状态 | 名称（★广告拦截器）| 拦截权限 | 版本
"""
import json
import os
import sys

BROWSERS = {
    "edge": r"C:\Users\HMSJ\AppData\Local\Microsoft\Edge\User Data",
    "chrome": r"C:\Users\HMSJ\AppData\Local\Google\Chrome\User Data",
}

# 知名广告拦截器（按扩展 ID 判定最权威，名称可能被 i18n 遮蔽）
ADBLOCK_IDS = {
    "cfhdojbkjhnklbpkdaibdccddilifddb": "Adblock Plus",
    "gighmpiobklfepjocnamgkkbiglidom": "AdBlock",
    "cjpalhdlnbpafiamejdnhcphjbkeiagm": "uBlock Origin",
    "bgnkhhnnamicmpejdlnlpkijmimjjhig": "AdGuard",
    "odkdlljoangmamjilkbbgcgbaohjfdlk": "AdGuard VPN",
}

# 有拦截/改写网络请求能力的权限 → 能静默掐断 OAuth 跳转链
INTERCEPT_PERMS = (
    "webRequest", "webRequestBlocking", "declarativeNetRequest",
    "declarativeNetRequestWithHostAccess", "proxy", "browsingData",
)


def resolve_i18n_name(ext_dir, raw_name):
    """__MSG_xxx__ → _locales/<locale>/messages.json 里的 message 值"""
    if not raw_name or not raw_name.startswith("__MSG_") or not raw_name.endswith("__"):
        return raw_name
    key = raw_name[6:-2]
    for locale in ("zh_CN", "zh", "en_US", "en"):
        msg_path = os.path.join(ext_dir, "_locales", locale, "messages.json")
        if os.path.exists(msg_path):
            try:
                msgs = json.load(open(msg_path, encoding="utf-8"))
                if key in msgs:
                    return msgs[key].get("message", raw_name)
            except Exception:
                pass
    return raw_name + " (i18n未解析)"


def audit(browser):
    base = BROWSERS[browser]
    if not os.path.isdir(base):
        print(f"[{browser}] User Data 目录不存在: {base}")
        return
    ext_root = os.path.join(base, "Default", "Extensions")
    sec = {}
    sec_path = os.path.join(base, "Default", "Secure Preferences")
    if os.path.exists(sec_path):
        try:
            sec = json.load(open(sec_path, encoding="utf-8")).get("extensions", {}).get("settings", {})
        except Exception as e:
            print(f"[{browser}] Secure Preferences 解析失败: {e}")

    print(f"\n===== {browser} 已安装扩展（磁盘目录为准）=====")
    if not os.path.isdir(ext_root):
        print("  无扩展目录")
        return
    for eid in sorted(os.listdir(ext_root)):
        edir = os.path.join(ext_root, eid)
        if not os.path.isdir(edir):
            continue
        versions = [d for d in os.listdir(edir) if os.path.isdir(os.path.join(edir, d))]
        ver = versions[-1] if versions else "?"
        mf_path = os.path.join(edir, ver, "manifest.json")
        if not os.path.exists(mf_path):
            continue
        try:
            mf = json.load(open(mf_path, encoding="utf-8"))
        except Exception:
            continue
        name = resolve_i18n_name(os.path.join(edir, ver), mf.get("name", "?"))
        perms = set(mf.get("permissions", []))
        host_perms = mf.get("host_permissions", [])
        intercept = [p for p in perms if p in INTERCEPT_PERMS]
        if "<all_urls>" in host_perms:
            intercept.append("<all_urls>")
        # 启用状态：disable_reasons 空列表=启用；非空=禁用；缺失=状态未知
        meta = sec.get(eid, {})
        dr = meta.get("disable_reasons")
        if dr == []:
            state = "启用"
        elif isinstance(dr, list) and dr:
            state = "禁用"
        else:
            state = "状态未知"
        flags = []
        if eid in ADBLOCK_IDS:
            flags.append(f"★{ADBLOCK_IDS[eid]}")
        if intercept:
            flags.append("拦截权限:" + ",".join(intercept))
        tail = " | " + " | ".join(flags) if flags else ""
        print(f"  {state:6s} | {name}{tail} | {ver}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = list(BROWSERS) if target == "all" else [target]
    for b in targets:
        if b in BROWSERS:
            audit(b)
        else:
            print(f"未知浏览器: {b}（可选: edge / chrome / all）")
