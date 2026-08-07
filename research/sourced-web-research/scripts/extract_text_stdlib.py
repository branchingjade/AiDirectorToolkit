#!/usr/bin/env python3
"""Extract readable text from raw HTML files using stdlib only (no bs4).

Usage: python extract_text_stdlib.py <input.html> <output.txt>

Skips script/style/nav/noscript/svg/iframe/form content, treats block-level
tags as line breaks, collapses blank lines. Verified 2026-08 on Final Draft,
Writers Store, StudioBinder, Wikipedia, John August pages.
"""
import html.parser
import re
import sys


class TextExtractor(html.parser.HTMLParser):
    BLOCK_TAGS = {'p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                  'tr', 'section', 'article', 'blockquote', 'ul', 'ol',
                  'table', 'figcaption', 'header', 'footer'}
    SKIP_TAGS = {'script', 'style', 'noscript', 'svg', 'canvas', 'iframe',
                 'nav', 'form'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        elif tag in self.BLOCK_TAGS and self.skip_depth == 0:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
        elif tag in self.BLOCK_TAGS and self.skip_depth == 0:
            self.parts.append('\n')

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.parts.append(data)


def extract(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        src = f.read()
    p = TextExtractor()
    p.feed(src)
    lines = [re.sub(r'[ \t]+', ' ', ln).strip() for ln in ''.join(p.parts).split('\n')]
    out = []
    blank = 0
    for ln in lines:
        if not ln:
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        out.append(ln)
    return '\n'.join(out)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('usage: python extract_text_stdlib.py <input.html> <output.txt>')
    txt = extract(sys.argv[1])
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write(txt)
    print(f'{sys.argv[1]} -> {sys.argv[2]}: {len(txt)} chars')
