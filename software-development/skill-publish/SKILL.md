---
name: skill-publish
description: "Use when 升级或发布 Hermes skill 到 GitHub 正本，含打 Release。"
version: 1.0.0
author: 妖玉
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [skills, publish, release, github]
    related_skills: [hermes-skill-management, hermes-agent-skill-authoring]
---

# Skill 发布（GitHub 正本 + Release）

当本地 skill 有版本升级时，发布到 GitHub 正本是流程的一部分——**不是可选项**。版本号变了，就要打 release。

## 触发条件（满足任一即执行）

1. 本地 skill 的 `version:` 字段升级（v2.2.0 → v2.3.0 等）
2. 用户要求"同步到 GitHub"、"打 release"、"发布版本"
3. 修改了有 GitHub 正本的 skill（如妖玉影视三件套 → branchingjade/AiDirectorToolkit）

## 发布流程（三步，缺一不可）

### 1. 同步正本

```bash
# 妖玉影视三件套正本仓库 = Hermes 主工作区 skills 目录（2026-08-17 起，ClaudeCode 副本已删除）
cd /c/Users/HMSJ/AppData/Local/hermes/skills
# 本地 skill 目录 → 同目录提交（skill 就在正本仓库内，直接 git add）
git add "妖玉影视/<SKILL名>/" && git commit -m "feat(<名>): vX.Y.Z <改动摘要>"
```

**注意**：
- 仓库结构是 `妖玉影视/<skill名>/`，不是根目录——先 `find . -name "SKILL.md"` 确认
- 远程可能有结构重构（如"归入妖玉影视分类目录"），pull 前先看远程结构，push 被拒先 `git pull --rebase`
- **历史教训（2026-08-17）**：曾存在 `Documents/ClaudeCode/AiDirectorToolkit` 副本（AI-Skills 身份）与主工作区双写同一 GitHub 远程，导致两线分叉 60+ 提交。副本已删，**一律以主工作区 skills 目录为唯一正本**，不要再建第二个仓库副本
- 中文路径用 `/bin/cp` 或 python，别用 `cp`（MSYS `cp -i` 别名静默失败）

### 2. 打 tag

tag 命名惯例（按 skill 类型）：

| Skill | tag 前缀 |
|-------|---------|
| AI短剧编剧助手 | `ai-screenwriter-assistant-vX.Y.Z` |
| AI短剧导演助手 | `ai-director-assistant-vX.Y.Z` |
| AI提示词助手 | `ai-prompt-assistant-vX.Y.Z` |

```bash
git tag "ai-screenwriter-assistant-v2.3.0"
git push origin "ai-screenwriter-assistant-v2.3.0"
```

### 3. 打 Release

```bash
gh release create "<tag>" --title "<中文标题>" --notes-file <notes文件>
```

- **标题**：中文，如 "AI短剧编剧助手 v2.3.0 — 新增改编专项"
- **notes 文件**：用 `write_file` 写 Windows 路径（`gh` 是 Windows 程序，读不到 MSYS `/tmp`），用后删除
- **多件同时升级**：合发"三件套" release（参考 `gh release view v2.0.0` 的格式：按 skill 分节）

### Release note 格式（参考 v2.0.0）

```markdown
## AI短剧编剧助手 v2.3.0 — 新增改编专项

### <改动分类>

1. <条目> — 说明
2. <条目> — 说明

### 来源

<这次改动的实战来源>
```

## 验证清单

- [ ] 本地 skill 与仓库 SKILL.md 完全一致（`diff` 确认）
- [ ] tag 已推送（`git ls-remote --tags origin | grep <tag>`）
- [ ] release 已创建（`gh release view <tag>` 确认 title/draft=false）
- [ ] 版本号在 SKILL.md 和 CHANGELOG 中一致
- [ ] CHANGELOG（versions/ 或 references/）有对应版本条目

## 常见坑

1. **push 被拒**：远程有重构（如目录归入妖玉影视/）——先 `git pull --rebase`，冲突时以远程结构为准，`git rm` 旧路径
2. **gh 读不到 /tmp**：MSYS 的 /tmp 对 Windows 程序不可见，notes 文件写到仓库目录下 Windows 路径
3. **只 push 不打 release**：版本升级必须三步全走（同步→tag→release），推完代码就收工 = 发布未完成
4. **中文路径 cp 失败**：MSYS `cp -i` 别名静默跳过，用 `/bin/cp`
