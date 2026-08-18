---
name: hermes-dsh-skill-sync
description: DSH 与 Hermes 技能库共享约定——两侧共用 %LOCALAPPDATA%\hermes\skills 一套技能库；新增/维护 skill 时按此约定落位，保证两边一致。当需要新建 skill、决定 skill 放哪、排查 skill 不同步时使用。
whenToUse: 新建或维护 skill 时必读；两侧技能库出现不一致、不知道新 skill 该写到哪里时使用。
version: 1.0.0
author: 妖玉
license: MIT
metadata:
  hermes:
    tags: [DSH, Hermes, 技能库, 共享, 同步]
    related_skills: [hermes-dsh-fusion, hermes-workspace-conventions]
---

# DSH × Hermes 技能库共享约定（2026-08-18 起生效）

## 机制

- **一套技能库**：`C:\Users\HMSJ\AppData\Local\hermes\skills`（Hermes 官方 skill 库，同步脚本的 DST 也在这里）。
- **DSH 侧接入**：
  - `~/.dsh/skills` 是指向技能库的 **junction**（读 + 写都落在 Hermes 库）——DSH 的一级 skill 直接就是 Hermes 的。
  - DSH 通过 `customSkillDirs` 额外读取技能库下的**分类子目录**（devops、scriptwriting、妖玉影视、film-production、post-production、lark 等），使二级 skill 同样可发现。
  - DSH 默认 preset = `hermes-cordis`（cordis 副本 + 上述二级目录），新会话生效。
- **技能格式**：两侧一致（`SKILL.md` + YAML frontmatter，必需 `name`/`description`），无需转换。

## 写 skill 约定

1. **一级 skill**（独立能力）：写到技能库根的一级位置：`<技能库>\<name>\SKILL.md`。
2. **分类 skill**（归属明确）：写到对应分类子目录：`<技能库>\<category>\<name>\SKILL.md`（如 `devops\hermes-dsh-fusion`）。
3. 命名：**必须 kebab-case（`^[a-z0-9]+(?:-[a-z0-9]+)*$`）**——这是 DSH 侧 `isSkillName` 的**硬校验**，中文/大写/下划线名会被 DSH **静默忽略**（不报错，只在日志 warn，技能直接不可见）。Hermes 侧不校验、DSH 侧校验，所以两侧共享时以 DSH 规则为准；避免与 `lark-*`、`mattpocock-*` 等既有前缀冲突。
4. 新建后两侧**自动可见**（junction + watcher 实时），无需手动同步。

## 中文名技能教训（2026-08-19 拉齐实测）

- 现象：妖玉影视 8 个技能 + 前端设计知识库共 **9 个中文 frontmatter name 技能在 DSH 完全不可见**（运行时 243 个技能里一个都没有），Hermes 侧正常。
- 根因：`packages/skill/skill/src/index.ts` 的 `SKILL_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/`，skill-filesystem 对 invalid name 仅 warn + 静默跳过。
- 修复：9 个技能改名（2026-08-19 已提交）：AI电影编剧→`ai-movie-screenwriter`、AI电影导演→`ai-movie-director`、AI短剧编剧助手→`ai-short-drama-writer`、AI短剧导演助手→`ai-short-drama-director`、AI提示词助手→`ai-prompt-assistant`、妖玉影视知识库→`yaoyu-film-knowledge-base`、剧本库维护→`screenplay-library-maintenance`、电影大师研习→`film-master-study`、前端设计知识库→`frontend-design-knowledge-base`。
- **新建 skill 铁律：frontmatter `name` 一律英文 kebab-case；中文名只放进 `description`/正文标题**。

## 维护注意

- Hermes 的 `sync-external-skills.py` 会**整目录替换**同步分类（如 mattpocock 系）——手写 skill 放一级位置或非同步分类，别放进会被覆盖的目录。
- `skills.disabled` 名单（Hermes config.yaml）只在 Hermes 侧生效，不影响 DSH 加载。
- 删除 skill：删文件即可，两侧同时消失；`.git` 历史保留。
- DSH 侧新增的一级 skill 会出现在 Hermes 侧（若 Hermes 未禁用）——命名冲突时优先保留手写版。

## 验收

- 任意一侧（DSH/Hermes）能加载该 skill 即通过。
- 一致性核对：`Test-Path ~\.dsh\skills\<name>\SKILL.md` 与 Hermes 库同名文件为同一路径（junction）。
