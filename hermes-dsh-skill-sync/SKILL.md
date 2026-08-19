---
name: hermes-dsh-skill-sync
description: DSH 与 Hermes 技能库同步约定——2026-08-19 起两侧已解耦：Hermes 正本在 %LOCALAPPDATA%\hermes\skills，DSH 是 ~/.dsh/skills 实体副本（不再是 junction）。Hermes 改技能后需手动同步到 DSH 副本。当需要新建 skill、决定 skill 放哪、排查 skill 不同步时使用。
whenToUse: 新建或维护 skill 时必读；两侧技能库出现不一致、不知道新 skill 该写到哪里时使用。
version: 2.0.0
author: 妖玉
license: MIT
metadata:
  hermes:
    tags: [DSH, Hermes, 技能库, 同步, 解耦]
    related_skills: [hermes-workspace-conventions]
---

# DSH × Hermes 技能库同步约定（2026-08-19 解耦版）

## 机制（v2：两侧独立实体）

- **Hermes 正本**：`C:\Users\HMSJ\AppData\Local\hermes\skills`（Hermes 官方 skill 库，同步脚本的 DST 也在这里，git 正本 → AiDirectorToolkit）。
- **DSH 实体副本**：`C:\Users\HMSJ\.dsh\skills` —— 2026-08-19 起从 junction 换成 **robocopy 实体拷贝**（排除 `.git`/`.hub`/`.curator_backups`/`.archive`）。**两侧不再自动同步**。
- DSH 通过 `customSkillDirs`（hermes-cordis preset）读取副本下的**分类子目录**（devops、scriptwriting、妖玉影视、film-production、post-production、lark 等），使二级 skill 可发现。
- DSH 默认 preset = `hermes-cordis`（cordis 副本 + 上述二级目录），新会话生效。
- 技能格式两侧一致（`SKILL.md` + YAML frontmatter，必需 `name`/`description`），无需转换。

## 写 skill 约定

1. **写 Hermes 正本**（唯一写入点）：一级 skill 写到 `<技能库>\<name>\SKILL.md`；分类 skill 写到 `<技能库>\<category>\<name>\SKILL.md`（如 `devops\hermes-dsh-fusion`）。
2. 命名：**必须 kebab-case（`^[a-z0-9]+(?:-[a-z0-9]+)*$`）**——这是 DSH 侧 `isSkillName` 的**硬校验**，中文/大写/下划线名会被 DSH **静默忽略**（不报错，只在日志 warn，技能直接不可见）。
3. **写完同步到 DSH 副本**（手动，单向 Hermes→DSH）：
   ```
   robocopy "C:\Users\HMSJ\AppData\Local\hermes\skills" "C:\Users\HMSJ\.dsh\skills" /E /XD .git .hub .curator_backups .archive /NFL /NDL /NP /R:2 /W:3
   ```
   ⚠️ 排除项必须与建副本时一致；`.git` 绝不能拷（双副本指向同一远程会分叉）。

## 中文名技能教训（2026-08-19 拉齐实测）

- 现象：妖玉影视 8 个技能 + 前端设计知识库共 **9 个中文 frontmatter name 技能在 DSH 完全不可见**（运行时 243 个技能里一个都没有），Hermes 侧正常。
- 根因：`packages/skill/skill/src/index.ts` 的 `SKILL_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/`，skill-filesystem 对 invalid name 仅 warn + 静默跳过。
- 修复：9 个技能改名（2026-08-19 已提交）：AI电影编剧→`ai-movie-screenwriter`、AI电影导演→`ai-movie-director`、AI短剧编剧助手→`ai-short-drama-writer`、AI短剧导演助手→`ai-short-drama-director`、AI提示词助手→`ai-prompt-assistant`、妖玉影视知识库→`yaoyu-film-knowledge-base`、剧本库维护→`screenplay-library-maintenance`、电影大师研习→`film-master-study`、前端设计知识库→`frontend-design-knowledge-base`。
- **新建 skill 铁律：frontmatter `name` 一律英文 kebab-case；中文名只放进 `description`/正文标题**。

## 维护注意

- Hermes 的 `sync-external-skills.py` 会**整目录替换**同步分类（如 mattpocock 系）——手写 skill 放一级位置或非同步分类，别放进会被覆盖的目录。
- `skills.disabled` 名单（Hermes config.yaml）只在 Hermes 侧生效，不影响 DSH 加载。
- 删除 skill：删 Hermes 正本 + 同步删除 DSH 副本（或重跑 robocopy 用 /MIR 镜像——⚠️ /MIR 会删掉 DSH 侧独有文件，慎用；默认用 /E 增量追加）。
- DSH 侧不再自动出现 Hermes 新增的一级 skill——**必须手动 robocopy 同步**。

## 验收

- Hermes 侧：Hermes 能加载该 skill。
- DSH 侧：`Test-Path ~\.dsh\skills\<name>\SKILL.md` 存在（实体文件，非 junction）。
- 一致性：`(Get-ChildItem "C:\Users\HMSJ\AppData\Local\hermes\skills" -Recurse -Filter SKILL.md | Measure-Object).Count` 与 DSH 副本计数差 = 排除项数量（当前 306 vs 295，差 11 = `.archive`）。
