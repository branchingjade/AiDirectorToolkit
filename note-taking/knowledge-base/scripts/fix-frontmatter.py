#!/usr/bin/env python3
"""Fix inline YAML lists in Obsidian frontmatter.

Obsidian properties require YAML multi-line format:
  tags:           →   tags:
    - a                 - a
    - b                 - b

Inline format `tags: [a, b]` triggers 'invalid property' warning.
This script scans all .md files and converts inline lists.

Usage: python3 fix-frontmatter.py [vault_path]
Default vault: ~/Documents/KnowledgeBase/Obsidian Vault
"""
import os, re, sys

vault = sys.argv[1] if len(sys.argv) > 1 else os.path.expandvars(
    r"%USERPROFILE%\Documents\KnowledgeBase\Obsidian Vault")

fixed = 0
for root, dirs, files in os.walk(vault):
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        with open(path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        orig = content
        content = re.sub(r'^tags:\s*\[(.+?)\]', lambda m: 'tags:\n' + '\n'.join(
            f'  - {t.strip()}' for t in m.group(1).split(',')),
            content, flags=re.MULTILINE)
        content = re.sub(r'^related:\s*\[(.+?)\]', lambda m: 'related:\n' + '\n'.join(
            f'  - {t.strip()}' for t in m.group(1).split(',')),
            content, flags=re.MULTILINE)
        if content != orig:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(content)
            print(f'Fixed: {os.path.relpath(path, vault)}')
            fixed += 1

print(f'\nTotal: {fixed} files fixed')
