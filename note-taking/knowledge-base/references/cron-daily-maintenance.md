# 知识库每日维护 Cron 脚本

> 2026-07-01 验证通过。在 Hermes cron 环境下执行，无用户交互。

## 前置条件

- `~/Documents/KnowledgeBase` 已 clone 且 git remote 配置正确
- `~/AppData/Local/hermes/memories/MEMORY.md` 和 `USER.md` 存在
- Shell 为 git-bash/MSYS（Windows 环境）

## 执行步骤

### 1. 同步 Hermes 记忆到 Vault

```bash
# ⚠️ 必须用 /bin/cp 绕过 MSYS cp -i 别名
# ⚠️ 镜像位置 = _hermes/memory/（2026-08-07 起，旧位置 Hermes运维/memory/ 已废弃——references 曾残留旧路径导致周检 cron 复活旧目录，2026-08-16 修复）
mkdir -p "$HOME/Documents/KnowledgeBase/Obsidian Vault/_hermes/memory"
/bin/cp "$HOME/AppData/Local/hermes/memories/MEMORY.md" \
        "$HOME/Documents/KnowledgeBase/Obsidian Vault/_hermes/memory/MEMORY.md"
/bin/cp "$HOME/AppData/Local/hermes/memories/USER.md" \
        "$HOME/Documents/KnowledgeBase/Obsidian Vault/_hermes/memory/USER.md"
```

### 2. Git 提交

```bash
cd "$HOME/Documents/KnowledgeBase"
git status --short
# 有变更则：
git add -A && git commit -m "chore: 每日自动提交 — 同步 Hermes 记忆/画像" && git push
```

### 3. 悬空 Wikilink 检测

```bash
cd "$HOME/Documents/KnowledgeBase/Obsidian Vault"

# 提取所有 wikilink 目标名（去锚点、去别名）
grep -roh '\\[\\[[^]]*\\]\\]' --include='*.md' --exclude-dir='.obsidian' . | \\
  sed 's/\\[\\[//;s/\\]\\]//;s/#.*//;s/|.*//' | sort -u > /tmp/wikilinks.txt

# 构建两级索引：全路径 + 裸文件名
find . -name '*.md' -not -path './.obsidian/*' | sed 's|^\\./||;s|\\.md$||' | sort -u > /tmp/all_filepaths.txt
find . -name '*.md' -not -path './.obsidian/*' -exec basename {} .md \\; | sort -u > /tmp/all_basenames.txt

# 两级匹配：先精确路径，再裸文件名后备
while IFS= read -r link; do
  [ -z "$link" ] && continue
  linkpath="${link}.md"
  basename="${link##*/}"
  # 阶段1：精确路径
  grep -qxF "$linkpath" /tmp/all_filepaths.txt 2>/dev/null && continue
  # 阶段2：裸文件名后备（Obsidian 风格）
  grep -qxF "$basename" /tmp/all_basenames.txt 2>/dev/null && continue
  echo "DANGLING: [[$link]]"
done < /tmp/wikilinks.txt
```

> `grep -qxF` 比每链接一次 `find` 快一个数量级——预建索引后全量匹配只需 O(n)。

### 4. Vault 根目录检查

```bash
cd "$HOME/Documents/KnowledgeBase/Obsidian Vault"
# MOC.md 在根目录是正常的，其他 .md 需要归位
ls *.md 2>/dev/null
```

## 已知误报

| 模式 | 来源 | 处理 |
|------|------|------|
| `...` | 笔记中展示 wikilink 语法的示例 `[[...]]` | 忽略 |
| 空行 | grep 提取 artifact | 忽略 |
| 含 `/` 的 wikilink | `[[子目录/笔记名]]` — 实际指向子目录中的文件 | 用 `${link##*/}` 取文件名后匹配 |
