---
name: hermes-dsh-skill-sync
description: DSH 与 Hermes 技能库约定——2026-08-19 晚起 DSH 直连 Hermes 正本：~/.dsh/skills 是 junction → %LOCALAPPDATA%\hermes\skills，不存实体副本、无需手动同步，Hermes 侧改技能即热生效。当需要新建 skill、决定 skill 放哪、排查 skill 不同步时使用。
whenToUse: 新建或维护 skill 时必读；两侧技能库出现不一致、不知道新 skill 该写到哪里时使用。
version: 3.0.0
author: 妖玉
license: MIT
metadata:
  hermes:
    tags: [DSH, Hermes, 技能库, junction, 直连]
    related_skills: [hermes-workspace-conventions]
---

# DSH × Hermes 技能库约定（2026-08-19 晚直连版）

## 机制（v3：junction 直连，单实体）

- **唯一正本**：`C:\Users\HMSJ\AppData\Local\hermes\skills`（Hermes 官方 skill 库，git 正本 → AiDirectorToolkit）。
- **DSH 直连**：`C:\Users\HMSJ\.dsh\skills` 是 **junction** → Hermes 正本（2026-08-19 晚用户拍板「DSH 不存副本，是直连 Hermes 技能库才对」，从 v2 实体副本改回）。**单实体、零同步**——Hermes 侧改技能 DSH 即热生效。
- 热生效原理：DSH skill-filesystem `watchFollowSymlinks` 默认 true（chokidar 跟随 junction），Hermes 侧增/改/删 skill 自动触发 DSH 技能刷新，**无需手动 robocopy、无需重启 DSH**。
- junction 暴露的运行时目录（`.git`/`.hub`/`.curator_backups`/`.archive`）无直接 `SKILL.md`，`discoverRoot` 扫描时静默跳过——**不会误载入归档技能**（已读源码验证 `packages/skill/skill-filesystem/src/index.ts`）。
- DSH 通过 `customSkillDirs` 读取**分类子目录**（devops、scriptwriting、妖玉影视、film-production、post-production、lark 等），使二级 skill 可发现（路径经 junction 透传）。**⚠️ 生效点分层（2026-08-19 修复）**：web-app bundle 将 host 层 skill-filesystem 设为 `disabled: true`（presets own local discovery）——机器级 `~/.dsh/cordis.patch.yml` 的 customSkillDirs 挂在 host 行上 **对 web profile 不生效**（分类二级技能缺失的根因，8-19 验收只看文件系统透传漏检）。真正生效点 = **creator preset 层**（`~/.dsh/.agent-presets/creator/agent.cordis.yml` 的 skill-filesystem customSkillDirs，与 cordis.patch.yml 清单一致，两处需同步维护）。headless profile 无 agent-presets 插件、host 层未被禁用，走机器级 patch 即可。
- DSH 默认 preset = `creator`（cordis 副本 + 上述二级目录），新会话生效。preset 文件用 `compositionStamp`（mtime）检测变化——**改 preset 后新会话自动重载，无需重启 DSH**。
- 技能格式两侧一致（`SKILL.md` + YAML frontmatter，必需 `name`/`description`），无需转换。

## 写 skill 约定

1. **只写 Hermes 正本**（唯一写入点）：一级 skill 写到 `<技能库>\<name>\SKILL.md`；分类 skill 写到 `<技能库>\<category>\<name>\SKILL.md`（如 `devops\hermes-dsh-fusion`）。写完 DSH 自动可见，**不要**再往 `~/.dsh/skills` 写。
2. 命名：**必须 kebab-case（`^[a-z0-9]+(?:-[a-z0-9]+)*$`）**——这是 DSH 侧 `isSkillName` 的**硬校验**，中文/大写/下划线名会被 DSH **静默忽略**（不报错，只在日志 warn，技能直接不可见）。
3. 写完 skill 后，**git commit + push 到 AiDirectorToolkit 正本**（Git 归位铁律：只 commit 不 push 不算归档完成）。

## 中文名技能教训（2026-08-19 拉齐实测）

- 现象：妖玉影视 8 个技能 + 前端设计知识库共 **9 个中文 frontmatter name 技能在 DSH 完全不可见**（运行时 243 个技能里一个都没有），Hermes 侧正常。
- 根因：`packages/skill/skill/src/index.ts` 的 `SKILL_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/`，skill-filesystem 对 invalid name 仅 warn + 静默跳过。
- 修复：9 个技能改名（2026-08-19 已提交）：AI电影编剧→`ai-movie-screenwriter`、AI电影导演→`ai-movie-director`、AI短剧编剧助手→`ai-short-drama-writer`、AI短剧导演助手→`ai-short-drama-director`、AI提示词助手→`ai-prompt-assistant`、妖玉影视知识库→`yaoyu-film-knowledge-base`、剧本库维护→`screenplay-library-maintenance`、电影大师研习→`film-master-study`、前端设计知识库→`frontend-design-knowledge-base`。
- **新建 skill 铁律：frontmatter `name` 一律英文 kebab-case；中文名只放进 `description`/正文标题**。

## 维护注意

- Hermes 的 `sync-external-skills.py` 会**整目录替换**同步分类（如 mattpocock 系）——手写 skill 放一级位置或非同步分类，别放进会被覆盖的目录。
- `skills.disabled` 名单（Hermes config.yaml）只在 Hermes 侧生效，不影响 DSH 加载。
- 删除 skill：只删 Hermes 正本（junction 透传，DSH 侧自动消失），无需再删副本。
- v2 遗留：实体副本备份 `~/.dsh/skills-entity-bak`（2026-08-19 切换时保留，验证稳定后删除）。**不要**把它当 DSH 技能库用。**（已删 2026-08-19 夜，junction 稳定验证通过）**

## 验收

- Hermes 侧：Hermes 能加载该 skill。
- DSH 侧：`Test-Path ~\.dsh\skills\<name>\SKILL.md` 存在（经 junction 透传，非实体文件）。
- 直连性：`(Get-Item ~\.dsh\skills).LinkType` 为 `Junction`、Target 指向 `%LOCALAPPDATA%\hermes\skills`。
- 一致性：DSH 侧 `Get-ChildItem ~\.dsh\skills -Recurse -Filter SKILL.md` 计数 = Hermes 正本计数（含 `.archive`，junction 下不排除；当前 307）。差异排查看 Hermes 正本，不用看 DSH 副本。
