# -*- coding: utf-8 -*-
"""Extract zhidao.baidu.com question pages to readable text.

Usage: python extract_zhidao.py pages/raw_zhidao_<id>.html [more.html...]
Output: <input base> replaced raw_zhidao_ -> cn-format-zhidao-, .html -> .txt

Pitfalls handled:
- zhidao HTML contains \x00 bytes inside UTF-8 text; must strip or read_file
  flags the output as binary.
- Nav/sidebar blocks repeat; dedupe consecutive identical lines.
"""
import re, html, sys


def extract(fn):
    t = open(fn, encoding='utf-8', errors='ignore').read()
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    m = re.search(r'<title>(.*?)</title>', t, flags=re.S)
    title = html.unescape(m.group(1)).strip() if m else ''
    body = re.sub(r'<[^>]+>', '\n', t)
    body = html.unescape(body)
    body = body.replace('\x00', '')
    lines = []
    for l in body.split('\n'):
        l = l.strip()
        if not l:
            continue
        if lines and lines[-1] == l:
            continue
        lines.append(l)
    return 'TITLE: ' + title + '\n\n' + '\n'.join(lines)


if __name__ == '__main__':
    for fn in sys.argv[1:]:
        out = fn.replace('raw_zhidao_', 'cn-format-zhidao-').replace('.html', '.txt')
        with open(out, 'w', encoding='utf-8') as f:
            f.write(extract(fn))
        print(out, len(open(out, encoding='utf-8').read()))
