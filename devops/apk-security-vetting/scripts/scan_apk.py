#!/usr/bin/env python3
"""APK 静态安全扫描：权限 / 统计SDK(带上下文) / 网络端点(按域名归并)。
用法: python scan_apk.py <apk1> [apk2 ...]
注: AXML 与 dex 字符串池为 UTF-16, 先去掉 \\x00 再匹配。
关键词命中需人工看上下文定性, 误报对照见 SKILL.md §四。
"""
import re
import sys
import zipfile
from collections import Counter

TRACKING_PATTERNS = [
    b'firebase', b'analytics', b'umeng', b'appcenter', b'mixpanel',
    b'talkingdata', b'flurry', b'getui', b'jpush', b'crashreport',
    b'adjust', b'bugly', b'mta', b'tencent',
]

SENSITIVE_PERMS = [
    'READ_CONTACTS', 'READ_SMS', 'RECORD_AUDIO', 'ACCESS_FINE_LOCATION',
    'ACCESS_COARSE_LOCATION', 'READ_PHONE_STATE', 'CAMERA', 'READ_CALL_LOG',
]


def scan(apk_path):
    print('#' * 30, apk_path)
    with zipfile.ZipFile(apk_path) as z:
        # 1. 权限 (AXML UTF-16 去零)
        mani = z.read('AndroidManifest.xml').replace(b'\x00', b'')
        perms = sorted(set(re.findall(rb'android\.permission\.[A-Z_]+', mani)))
        print('--- 权限 ---')
        for p in perms:
            mark = '  <-- 敏感!' if any(s in p.decode() for s in SENSITIVE_PERMS) else ''
            print('  ', p.decode(), mark)
        if not perms:
            print('  (未提取到, AXML 可能非 UTF-16)')

        # 2. dex SDK 关键词扫描 (带上下文)
        dexes = [n for n in z.namelist() if n.startswith('classes') and n.endswith('.dex')]
        hits = {}
        for d in dexes:
            data = z.read(d)
            clean = data.replace(b'\x00', b'')
            for pat in TRACKING_PATTERNS:
                for m in re.finditer(re.escape(pat), clean, re.I):
                    ctx = ''.join(chr(c) if 32 <= c < 127 else '.' for c in
                                  clean[max(0, m.start() - 60):m.start() + 90])
                    hits.setdefault(pat.decode(), []).append((d, ctx))
        print('--- 关键词命中 (对照 SKILL.md 误报表人工定性) ---')
        if not hits:
            print('  (零命中 = 干净)')
        for k, v in hits.items():
            print(f'  {k}: {len(v)} 处')
            for d, ctx in v[:4]:
                print(f'    [{d}] ...{ctx}...')

        # 3. 网络端点 (按域名归并)
        urls = Counter()
        for d in dexes:
            clean = z.read(d).replace(b'\x00', b'')
            for m in re.finditer(rb'https?://[a-zA-Z0-9._~:/?#\[\]@!$&\'()*+,;=%-]{5,120}', clean):
                dm = re.match(rb'https?://([^/]+)', m.group())
                if dm:
                    urls[dm.group(1).decode(errors='replace')] += 1
        print('--- 网络端点(按域名) ---')
        for dom, c in urls.most_common(40):
            print(f'  {c:4d}  {dom}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for a in sys.argv[1:]:
        scan(a)
