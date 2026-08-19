#!/usr/bin/env python
"""验证生成的剧本 docx 文件结构是否正确。
用法: python verify.py 魔王-第38场.docx [expected_line_count]
退出码 0 = 通过, 1 = 失败。
"""
import sys, re, zipfile, subprocess, os

if len(sys.argv) < 2:
    print(__doc__); sys.exit(1)
DOCX = sys.argv[1]
EXPECTED = int(sys.argv[2]) if len(sys.argv) > 2 else None
VALIDATOR = os.path.expandvars(r'%LOCALAPPDATA%\hermes\skills\productivity\docx\scripts\office\validate.py')

# 1) schema 验证
try:
    out = subprocess.run([sys.executable, VALIDATOR, DOCX], capture_output=True, text=True, timeout=30)
    schema_ok = 'PASSED' in (out.stdout + out.stderr)
    print('[schema]', 'PASS' if schema_ok else 'FAIL', '—', (out.stdout + out.stderr).strip().splitlines()[-1] if out.stdout or out.stderr else '')
except Exception as e:
    schema_ok = False
    print('[schema] FAIL —', e)

# 2) 段落统计
z = zipfile.ZipFile(DOCX)
xml = z.read('word/document.xml').decode('utf-8')
paragraphs = re.findall(r'<w:p[ >].*?</w:p>', xml, re.S)
n = len(paragraphs)
print(f'[paragraphs] {n}')

# 3) 类型分布
counts = {'num':0, 'sceneHead':0, 'note':0, 'dialog':0, 'action':0}
for p in paragraphs:
    t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))
    if re.match(r'^\d+(-\d+)?$', t.strip()): counts['num']+=1
    elif t.startswith('场'): counts['sceneHead']+=1
    elif t.startswith('△'): counts['note']+=1
    elif re.match(r'^[^：:]+[：:]', t): counts['dialog']+=1
    else: counts['action']+=1
print(f'[types] {counts}')

# 4) 段落数对得上输入?
ok_n = EXPECTED is None or abs(n - EXPECTED) <= 2
print('[count]', 'PASS' if ok_n else 'WARN', f'(预期 ~{EXPECTED})' if EXPECTED else '')

sys.exit(0 if schema_ok and ok_n else 1)