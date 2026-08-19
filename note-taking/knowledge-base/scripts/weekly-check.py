#!/usr/bin/env python3
"""Obsidian vault weekly health check — dangling wikilinks, orphans, MOC coverage.

Usage:
    python3 scripts/weekly-check.py [--vault /path/to/vault]

Default vault: ~/Documents/KnowledgeBase/Obsidian Vault
Override with OBSIDIAN_VAULT_PATH env var or --vault flag.

Output:
    1. Dangling wikilinks (w/ classification: TEMPLATE/EXAMPLE vs TRUE DANGLING)
    2. Orphan analysis (0-in-0-out, no-inbound, no-outbound)
    3. MOC coverage — files NOT linked from MOC.md
    4. MOC dangling — MOC links that don't resolve
"""

import re
import os
import sys
import argparse


def collect_md_files(vault: str) -> tuple[set[str], dict[str, set[str]]]:
    """Return (all_md, name_to_path) — relative paths + bare-filename index."""
    all_md = set()
    name_to_path: dict[str, set[str]] = {}
    for root, dirs, files in os.walk(vault):
        if '.obsidian' in root:
            continue
        for f in files:
            if not f.endswith('.md'):
                continue
            rel = os.path.relpath(os.path.join(root, f), vault).replace('\\', '/')
            all_md.add(rel)
            bare = f[:-3]
            name_to_path.setdefault(bare, set()).add(rel)
    return all_md, name_to_path


def extract_wikilinks(vault: str, all_md: set[str]) -> dict[str, set[str]]:
    """Return {relative_path: set_of_wikilink_targets}."""
    wikilink_re = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]')
    file_links: dict[str, set[str]] = {}
    for root, dirs, files in os.walk(vault):
        if '.obsidian' in root:
            continue
        for f in files:
            if not f.endswith('.md'):
                continue
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, vault).replace('\\', '/')
            with open(fpath, 'r', encoding='utf-8') as fh:
                content = fh.read()
            links = set(wikilink_re.findall(content))
            links = {l.strip() for l in links if l.strip()}
            file_links[rel] = links
    return file_links


def resolve(link: str, all_md: set[str], name_to_path: dict[str, set[str]]) -> set[str]:
    """Resolve a wikilink target to matching .md files (Obsidian-style resolution).

    Handles both bare filenames ([[Eagle 复盘]]) and relative paths ([[工具与集成/Eagle/Eagle 复盘]]).
    """
    results: set[str] = set()
    # Exact path or path+.md
    if link in all_md:
        results.add(link)
    if link + '.md' in all_md:
        results.add(link + '.md')
    # Bare filename match (Obsidian-style: [[Eagle 复盘]] -> any Eagle 复盘.md in vault)
    bare = link.split('/')[-1]
    if bare in name_to_path:
        results.update(name_to_path[bare])
    return results


# Known template/example wikilinks that exist as syntax demonstrations, not real links
TEMPLATE_LINKS = frozenset({
    'A', 'B', '^', 'xxx', 'xxx 复盘', 'xxx 集成',
    '关联A', '关联B', '子目录/笔记名', '新笔记名',
    '笔记A', '笔记B', '笔记名', '项目笔记',
    'wikilink', 'wikilinks',
})


def check_dangling(
    file_links: dict[str, set[str]],
    all_md: set[str],
    name_to_path: dict[str, set[str]],
) -> tuple[list, list]:
    """Return (template_dangling, true_dangling) — each a list of (link, sources)."""
    all_links = set()
    for links in file_links.values():
        all_links.update(links)

    template, true = [], []
    for link in sorted(all_links):
        if not link or link == '...':
            continue
        if resolve(link, all_md, name_to_path):
            continue
        sources = [f for f, ls in file_links.items() if link in ls]
        if link in TEMPLATE_LINKS:
            template.append((link, sources))
        else:
            true.append((link, sources))
    return template, true


def check_orphans(
    file_links: dict[str, set[str]],
    all_md: set[str],
    name_to_path: dict[str, set[str]],
) -> dict:
    """Return orphan classification dict."""
    indegree = {f: 0 for f in all_md}
    outdegree = {f: 0 for f in all_md}
    for f, links in file_links.items():
        resolved_count = 0
        for l in links:
            targets = resolve(l, all_md, name_to_path)
            resolved_count += len(targets)
            for t in targets:
                indegree[t] += 1
        outdegree[f] = resolved_count

    orphans = [f for f in sorted(all_md) if indegree[f] == 0 and outdegree[f] == 0]
    no_in = [(f, outdegree[f]) for f in sorted(all_md) if indegree[f] == 0 and outdegree[f] > 0]
    no_out = [(f, indegree[f]) for f in sorted(all_md) if outdegree[f] == 0 and indegree[f] > 0]
    return {'orphans': orphans, 'no_inbound': no_in, 'no_outbound': no_out}


EXCLUDE_FROM_MOC = frozenset({
    'Hermes运维/memory/', 'MOC.md', '知识库维护指南.md', '踩坑记录.md',
})


def check_moc(
    vault: str,
    all_md: set[str],
    name_to_path: dict[str, set[str]],
) -> tuple[list, list]:
    """Return (missing_from_moc, moc_dangling)."""
    wikilink_re = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]')
    moc_path = os.path.join(vault, 'MOC.md')
    if not os.path.exists(moc_path):
        return [], []
    with open(moc_path, 'r', encoding='utf-8') as f:
        moc_content = f.read()
    moc_links = set(wikilink_re.findall(moc_content))
    moc_links = {l.strip() for l in moc_links if l.strip()}

    missing = []
    for f in sorted(all_md):
        skip = any(f.startswith(pat) or f == pat for pat in EXCLUDE_FROM_MOC)
        if skip:
            continue
        found = any(f in resolve(ml, all_md, name_to_path) for ml in moc_links)
        if not found:
            missing.append(f)

    moc_dangling = [ml for ml in sorted(moc_links) if not resolve(ml, all_md, name_to_path)]
    return missing, moc_dangling


def main():
    parser = argparse.ArgumentParser(description='Obsidian vault weekly health check')
    parser.add_argument('--vault', default=os.environ.get(
        'OBSIDIAN_VAULT_PATH',
        os.path.expanduser('~/Documents/KnowledgeBase/Obsidian Vault'),
    ))
    args = parser.parse_args()
    vault = args.vault
    if not os.path.isdir(vault):
        print(f'ERROR: vault not found at {vault}')
        sys.exit(1)

    all_md, name_to_path = collect_md_files(vault)
    file_links = extract_wikilinks(vault, all_md)

    # 1. Dangling
    template, true = check_dangling(file_links, all_md, name_to_path)
    print('=== DANGLING WIKILINKS ===')
    for link, sources in template:
        print(f'  [[{link}]] [TEMPLATE/EXAMPLE]')
        for s in sources:
            print(f'    from: {s}')
    for link, sources in true:
        print(f'  [[{link}]] [TRUE DANGLING]')
        for s in sources:
            print(f'    from: {s}')
    print(f'True dangling: {len(true)}  |  Template examples: {len(template)}')

    # 2. Orphans
    print()
    print('=== ORPHAN ANALYSIS ===')
    orch = check_orphans(file_links, all_md, name_to_path)
    for f in orch['orphans']:
        print(f'  ORPHAN (0 in + 0 out): {f}')
    for f, deg in orch['no_inbound']:
        print(f'  NO_INBOUND (out: {deg}): {f}')
    for f, deg in orch['no_outbound']:
        print(f'  NO_OUTBOUND (in: {deg}): {f}')
    print(f'True orphans: {len(orch["orphans"])}')

    # 3. MOC
    print()
    print('=== MOC COVERAGE ===')
    missing, moc_dangling = check_moc(vault, all_md, name_to_path)
    for f in missing:
        print(f'  MISSING from MOC: {f}')
    print(f'Missing count: {len(missing)}')
    if moc_dangling:
        print()
        print('=== MOC DANGLING ===')
        for ml in moc_dangling:
            print(f'  [[{ml}]] does not resolve')


if __name__ == '__main__':
    main()
