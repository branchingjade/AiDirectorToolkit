# 周检 Shell 命令速查

> 用于 `execute_code` 不可用的场景（如 cron jobs、受限环境）。直接用 terminal 命令完成每周大维护。

## 1. Git 状态

```bash
cd ~/Documents/KnowledgeBase && git status --short
```

## 2. 记忆同步

```bash
# ⚠️ 镜像位置 = _hermes/memory/（2026-08-07 起；旧位置 Hermes运维/memory/ 已废弃，勿回写——曾致旧目录复活被误提交，2026-08-16 修复）
/bin/cp ~/AppData/Local/hermes/memories/MEMORY.md ~/Documents/KnowledgeBase/"Obsidian Vault"/_hermes/memory/MEMORY.md
/bin/cp ~/AppData/Local/hermes/memories/USER.md ~/Documents/KnowledgeBase/"Obsidian Vault"/_hermes/memory/USER.md
```

## 3. 列出所有笔记

```bash
cd ~/Documents/KnowledgeBase && find "Obsidian Vault" -name '*.md' -not -path '*/.obsidian/*' | sort
```

## 4. 悬空链接检测

分两步：先提取所有 wikilink 目标和所有笔记名，再求差集。

```bash
cd "/c/Users/HMSJ/Documents/KnowledgeBase/Obsidian Vault"

# 提取所有 wikilink 目标（bare name）
find . -name '*.md' -not -path './.obsidian/*' -exec grep -oh '\[\[[^]|#]*' {} \; \
  | sed 's/\[\[//' | sort -u > /tmp/all_links.txt

# 提取所有笔记 bare name
find . -name '*.md' -not -path './.obsidian/*' -exec basename {} .md \; | sort -u > /tmp/all_notes.txt

# 差集 = 可能的悬空链接
comm -23 /tmp/all_links.txt /tmp/all_notes.txt
```

**过滤误报**：差集结果需人工过滤以下类别：
- 模板占位符：`xxx`、`笔记A`、`关联A`、`新笔记名` 等
- 代码片段：`{"tag": ...}` 等被误抓的 `[[...]]`
- 路径式链接：含 `/` 的链接（如 `犬子无双/第一场调色分析`）在 Obsidian 中作为路径后缀解析，需单独验证文件是否存在

## 5. 路径式链接验证

对差集中含 `/` 的链接，逐个检查文件是否存在：

```bash
cd "/c/Users/HMSJ/Documents/KnowledgeBase/Obsidian Vault"
for f in "路径/文件名.md" ...; do
  if [ -f "$f" ]; then echo "OK: $f"; else echo "MISSING: $f"; fi
done
```

## 6. MOC 完整性

用 Python 单行脚本（`python3 -c`）对比所有笔记 bare name 与 MOC 中的链接：

```bash
cd "/c/Users/HMSJ/Documents/KnowledgeBase/Obsidian Vault" && python3 -c "
import os, re
vault = '.'
all_notes = set()
for root, dirs, files in os.walk(vault):
    if '.obsidian' in root: continue
    for f in files:
        if f.endswith('.md'):
            all_notes.add(f[:-3])
with open('MOC.md', encoding='utf-8') as f:
    moc = f.read()
moc_bare = set()
for l in re.findall(r'\[\[([^\]|#]+?)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]', moc):
    moc_bare.add(l.split('/')[-1])
skip = {'MOC','README','CHANGELOG','MEMORY','USER','knowledge-base-skill'}
for n in sorted(all_notes - skip):
    if n not in moc_bare:
        print(n)
"
```

## 7. 孤岛检测

检查无入/出 wikilink 的笔记：

```bash
cd "/c/Users/HMSJ/Documents/KnowledgeBase/Obsidian Vault" && python3 -c "
import os, re
vault = '.'
notes = {}
for root, dirs, files in os.walk(vault):
    if '.obsidian' in root: continue
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path, encoding='utf-8') as fh:
                content = fh.read()
            notes[f[:-3]] = {'path': path, 'links': set(re.findall(r'\[\[([^\]|#]+?)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]', content))}
all_targets = set()
for d in notes.values():
    for l in d['links']:
        all_targets.add(l.split('/')[-1])
skip = {'MOC','README','CHANGELOG','知识库维护指南','MEMORY','USER'}
for bare, d in sorted(notes.items()):
    if bare in skip: continue
    if not d['links'] and bare not in all_targets:
        print(f'ORPHAN: {bare} ({d[\"path\"]})')
"
```

## 8. 待补充占位扫描

```bash
grep -rn "⚠️ 待补充" "/c/Users/HMSJ/Documents/KnowledgeBase/Obsidian Vault" --include='*.md'
```

## 9. 提交推送

```bash
cd ~/Documents/KnowledgeBase && git add -A && git commit -m "周检: ..." && git push
```

## 坑

- `search_files` 在含空格路径下返回 0 结果 → 用 `find` 代替（已知坑）
- `python3` 在 MSYS 下路径被双重转换 → 用 Windows 正斜杠格式 `C:/Users/...`
- `cp` 在 MSYS 下默认 `cp -i` → 用 `/bin/cp`
- `basename` 处理含空格中文文件名会截断 → 用 Python 代替 shell 循环
