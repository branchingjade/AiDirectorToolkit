---
name: external-skill-sync
description: "Install and sync skills from external GitHub repos into Hermes. Covers tap setup, bulk install via direct copy (CLI timeout workaround), and cron-based auto-update."
version: 1.3.0
author: agent
platforms: [windows, linux, macos]
tags: [skills, tap, github, sync, cron, feishu]
---

# External Skill Sync

Manage skills from third-party GitHub repos (e.g. mattpocock/skills). Covers adding the repo as a tap, installing all skills at once, and keeping them updated via cron.

## Trigger

Use when the user wants to install skills from a GitHub repo, or set up auto-sync for external skill repos.

## Adding a tap

```bash
hermes skills tap add https://github.com/<owner>/<repo>
```

Verify: `hermes skills tap list`

## Bulk install — direct copy method

When `hermes skills install <URL>` times out or hits GitHub rate limits, bypass it by cloning the repo and copying skill directories directly:

```bash
# 1. Clone
git clone --depth 1 https://github.com/<owner>/<repo>.git /tmp/<repo>

# 2. Copy each category (skip deprecated)
for cat in engineering productivity misc in-progress personal; do
    cp -r "/tmp/<repo>/skills/$cat" "$HOME/AppData/Local/hermes/skills/mattpocock-$cat"
done
```

On Windows: `$HOME/AppData/Local/hermes/skills/`. On Linux/macOS: `~/.hermes/skills/`.

Each skill is a directory with a `SKILL.md` file. Hermes auto-discovers them. No restart needed — use `/reload-skills` in-session.

### Flat 格式仓库（`skills/<name>/SKILL.md`，无分类层）

```bash
git clone --depth 1 https://github.com/<owner>/<repo>.git /tmp/<repo>
DST="$HOME/AppData/Local/hermes/skills"
# 每个技能目录整体复制，加 `skills-` 前缀区分来源
for d in /tmp/<repo>/skills/*/; do
    name="$(basename "$d")"
    cp -r "$d" "$DST/skills-$name"
done
```

验证：`hermes skills list | grep <name>`（注意用**注册名**而非目录名，见 Pitfalls 的 frontmatter 怪癖）。

## Auto-sync via cron

Create a sync script (`~/.hermes/scripts/sync-<repo>-skills.sh`):

```bash
#!/bin/bash
set -e
REPO_URL="https://github.com/<owner>/<repo>.git"
CLONE_DIR="/tmp/<repo>-update"
SKILLS_DST="$HOME/AppData/Local/hermes/skills"

rm -rf "$CLONE_DIR"
git clone --depth 1 "$REPO_URL" "$CLONE_DIR" 2>/dev/null

for cat in engineering productivity misc in-progress personal; do
    src="$CLONE_DIR/skills/$cat"
    dst="$SKILLS_DST/<prefix>-$cat"
    if [ -d "$src" ]; then
        rm -rf "$dst"
        cp -r "$src" "$dst"
        echo "Synced <prefix>-$cat: $(find "$dst" -name SKILL.md | wc -l) skills"
    fi
done

rm -rf "$CLONE_DIR"
echo "Sync complete."
```

Then create a cron job with `no_agent=true` + `script=<path>`:

```bash
hermes cron create "0 9 * * *" --name "Sync <repo> skills" --script scripts/sync-<repo>-skills.sh --no-agent
```

To also deliver to Feishu: use `cronjob(action='update', deliver='origin,feishu', job_id='...')`. Bare `feishu` routes to home channel (set via `/sethome`).

## Python sync script (cron-ready)

**统一同步脚本** `scripts/sync-external-skills.py`：

- **自动发现源**：从 `hermes skills tap list` + `~/.hermes/hermes_skill_sources.yaml` 自动获取所有外部技能仓库
- **格式自检测**：clone 后自动判断 nested / flat / zip / single 四种格式
- **JSON 输出**：结构化输出给 LLM 做智能判断

```bash
python3 ~/AppData/Local/hermes/scripts/sync-external-skills.py
```

输出 JSON 结构：
```json
{
  "status": "ok",
  "stats": {"ok": 2, "clone_fail": 0, "total_skills": 44, "changed": 1},
  "sources": [
    {"source": "...", "prefix": "mattpocock", "format": "nested", "results": [...]},
    ...
  ]
}
```

**添加新源**：`hermes skills tap add <url>` 或在 `hermes_skill_sources.yaml` 加一条。脚本自动感知，零代码改动。

**手动源配置**（`~/.hermes/hermes_skill_sources.yaml`）：
```yaml
sources:
  - repo_url: https://github.com/owner/repo.git
    prefix: my-prefix    # 可选，默认用 owner 名
    categories:           # 可选，限制只同步特定分类
      - engineering
```

## 同步覆盖范围

**`hermes_skill_sources.yaml` + `hermes skills tap list` 自动发现的源都会被同步。** 当前活跃源：

| 仓库 | 格式 | 同步状态 | 说明 |
|------|------|---------|------|
| mattpocock/skills | nested（`skills/<category>/SKILL.md`） | ✅ 已实现 | 5个分类目录，`rmtree → copytree` 整目录替换 |
| branchingjade/AI-Skills | flat（`妖玉影视/` 子目录下各有 `SKILL.md`） | ⚠️ 需配 `skills_subpath` | 根目录 `README.md` 会误导 `detect_format` 判为 single；需在 yaml 中设 `skills_subpath: "妖玉影视"` 走 flat 格式。技能本地在 `skills/妖玉影视/` |
| MiniMax-AI/skills | flat（`skills/<name>/SKILL.md`，17 个平铺技能） | ❌ 已卸载（2026-08） | 用户评估后认为"没有用武之地"，本会话卸载：删 17 个 `skills-<name>/` 目录 + `hermes skills tap remove`。**卸载后必须同时移 tap**，否则每日 cron 会自动装回来 |

**不会被覆盖的：**
- `devops/`、`hermes-browser-cdp/` 等非 `mattpocock-*` 前缀的本地技能
- 用户手动创建或用 `skill_manage` 维护的技能
- `hermes skills install` 从 hub 安装的技能（走 hub 更新机制，不走 tap 同步）

**判断方法：** `hermes skills list` 查看 `source` 列。`local` = 纯本地，不受任何外部同步影响。`hermes skills check` 查看是否有 hub 来源的技能。

## 安装后的干扰防护（触发词冲突 + 极限测试）

外部 skill 装上后可能**抢用户自有 skill 的触发**（尤其影视/创作类自有技能）。装前必查、装后必测。

### 装前：触发词冲突检查

```bash
# 列出外部 skill 的 trigger-words，与用户自有 skill 的触发域对比
curl -s https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<name>/SKILL.md | grep -A2 "trigger-words"
```

重点警惕**宽泛泛词**：`视频prompt`、`Seedance视频prompt`、`MV`、`动画`、`广告` 这类词会踩用户自有主本 skill（如 AI提示词助手）。命中即报告用户，不要自行决定保留/删除。

### 干扰防护等级（2026-08-06 三轮极限测试实测结论）

| 方案 | 效果 | 根因 |
|---|---|---|
| description 加门禁（`ONLY use when...`） | ❌ 无效 | 系统提示中 description 被截断到 57 字符，"Do NOT trigger" 后半句模型看不到；模型靠 **skill 名字**命中 |
| 重命名加前缀（`h3-xxx`） | ❌ 无效 | 前缀挡不住名字主体泛词段（music-video、paper-collage、product-ad…） |
| **`config.yaml` `skills.disabled` 硬禁用** | ✅ 唯一有效 | 禁用的 skill **从系统提示里整个消失**，模型看不到名字，零误触发可能；`/skill <name>` 仍可手动加载 |

### 硬禁用操作

```bash
# config.yaml 的 skills.disabled 数组加入 skill 注册名（frontmatter name，非目录名）
hermes skills list   # 验证显示 disabled
```

需要用时 `/skill <name>` 手动加载（disabled 只挡自动触发，不挡手动加载）。

### 极限测试方法

用真实新会话批量验证（配置改动对已有会话不生效，必须开新 `hermes chat -q`）：

```bash
hermes chat -q "忽略任务本身，只回答：面对这个请求你会加载哪些skill？请求：<用例>" --source stress-test
```

- **对抗用例**：外部 skill 的全部旧 trigger-words + 用户影视日常请求（分镜/剧本/视频prompt 等），应**不**触发
- **正向用例**：明确提到外部 skill 场景（如 H3/minimax/Ref2VA），应正确指向核心 skill
- 注意：grep 判断时模型可能提及"记忆里的 skill 描述"而非真实加载——检查是否出现在技能扫描列表里，不是检查回复文本是否含关键词

完整三轮测试记录见 `references/skill-isolation-stress-test.md`。



- **`hermes skills install` timeout**: Network issues or GitHub rate limits. Fall back to direct copy method above.
- **GITHUB_TOKEN**: If using `hermes skills install`, set `GITHUB_TOKEN` in `.env` to raise API limit from 60 to 5000/hr.
- **`/reload-skills`**: After direct copy, run in-session to pick up new skills without restart.
- **Protected skills**: Bundled and hub-installed skills cannot be edited — only local/external ones.
- **Windows `shutil.rmtree` on git clones**: `.git/objects/pack/*.idx` files are read-only on Windows, causing `PermissionError`. Use `rmtree_force()` (included in the Python sync script) which chmods +w before retrying. The bash `rm -rf` approach does not have this issue.
- **Tap list table parsing**: `hermes skills tap list` outputs a formatted table with box-drawing characters (`│`). The script must search each line's tokens for the one starting with `http://` or `https://` — using `parts[-1]` or `parts[0]` will grab a border char instead of the URL.
- **`.skill` ZIP 格式（历史）**：branchingjade/AI-Skills 历史上用 `.skill` ZIP 文件，但当前仓库已变为根目录 `.md` 文件的 single 格式。如果未来恢复为 ZIP，需在 `detect_format()` 中添加 ZIP 检测。详见 `references/ai-skills-sync.md`。
- **Windows Python 路径解析**：`python3 "$HOME/AppData/..."` 在 git-bash/MSYS 下会将 `$HOME` 解析为 `/c/Users/...`，再被 Windows Python 转成 `C:\c\Users\...` 导致文件找不到。必须先 `cd` 到脚本目录再执行：`cd "$HOME/AppData/Local/hermes/scripts" && python sync-external-skills.py`。
- **single 格式的 `clone_dir.name` 后缀 bug**：`clone()` 创建的临时目录名为 `{name}-sync`（如 `AI-Skills-sync`），`sync_repo` 将其传给 `sync_flat([clone_dir.name], clone_dir, prefix)`，但 `sync_flat` 会拼接 `src_base / clone_dir.name` 即 `clone_dir / "AI-Skills-sync"`，此路径不存在，导致 `total_skills=0, results=[]`。根因：`clone_dir.name` 含 `-sync` 后缀与 `sync_flat` 的目录匹配逻辑不兼容。临时绕过：在 yaml 中设 `skills_subpath` 指向实际技能目录。
- **`stats.changed` 语义**：脚本的 `changed` 字段记录的是 `results` 数组长度（即被处理的分类目录数），不是实际新增/变更的技能数。LLM 消费者不应直接把它当"变更数"使用。判断是否真有变更需对比 `git diff` 或目录时间戳。
- **prefix 漂移导致目录重复（2026-08 实测）**：tap 源的 `dst_prefix` 从 URL 最后一段推断——`mattpocock/skills` 和 `MiniMax-AI/skills` 都会得到 `skills`，导致不同源写同一批 `skills-<cat>` 目录互相覆盖；且配置变更后旧前缀目录（如曾用 prefix=mattpocock 生成的 `mattpocock-engineering` 等）不会被清理，与新 `skills-engineering` 并存，同一套技能被 Hermes 注册两次。修复：在 `hermes_skill_sources.yaml` 为每个源显式配置 `prefix`（如 `prefix: mattpocock`），不再依赖 URL 推断；同步后检查并清理旧前缀残留目录（确认无本地自定义修改再删）。
- **清理旧前缀残留目录的完整流程（2026-08-06 实战）**：先 `hermes skills tap list` + `cat hermes_skill_sources.yaml` 确认当前前缀；再 `git clone --depth 1` 上游仓库对比各分类目录，确认哪套是最新（用目录 mtime 判断，如 `skills-*` 08-06 同步 vs `mattpocock-*` 07-23 旧快照）；抽查 `diff` 确认旧版差异只是上游版本演进、无本地 sed patch；确认 cron「外部技能同步」调用的是 sync-external-skills.py（写 `skills-*`）而非旧脚本后，才 `rm -rf` 旧前缀目录。**白名单**：`mattpocock-skills-navigator` 不在上游仓库 `skills/` 下（独立技能，frontmatter category=mattpocock-engineering），清理时保留；删除前先 `tar -czf` 到 `$HOME/AppData/Local/Temp/` 兜底。删完 `hermes skills list` 验证同名技能只出现一次（长名会截断显示如 `git-guardrails-clau…`，用前缀 grep）。旧脚本 `sync-mattpocock-skills.sh`（写 `mattpocock-*` 目录）虽无 cron 引用，属死代码，可提示用户删除。
- **AI-Skills 仓库格式变更（2025-08）**：仓库根目录现在有 `README.md`，`detect_format` 会优先匹配到 single 格式（根目录 `.md` 文件），但实际技能在 `妖玉影视/` 子目录下（三目录各有 `SKILL.md`）。正确配置：在 `hermes_skill_sources.yaml` 中设 `skills_subpath: "妖玉影视"` 让脚本走 flat 格式检测。当前临时状态：技能已在 `skills/妖玉影视/` 下（之前同步留存），不受本次同步影响。
- **注册名≠目录名（frontmatter name 怪癖）**：Hermes 按 SKILL.md frontmatter 的 `name` 字段注册技能，不是目录名。实测 MiniMax 的 `skills-minimax-multimodal-toolkit/` 目录注册名为 `mmx-cli`（仓库自带 frontmatter name 是 mmx-cli）。同步后验证必须用 `hermes skills list` 按实际注册名 grep，不能假设目录名=技能名；漏检时先查 SKILL.md 头部 frontmatter，不要误报"同步失败"。另外 `hermes skills list` 显示会截断长名（如 `minimax-music-playl…`），grep 全名可能匹配不到，用前缀即可。
- **MSYS `/tmp` 路径与 git 不一致（Windows）**：`git clone` 到 `/tmp/<repo>` 在 git-bash 下会报 `already exists and is not an empty directory`——因为 MSYS 的 `/tmp` 和 Windows 原生 git 解析的路径不同，先 `rm -rf /tmp/xxx` 也删不掉（rm 走 MSYS 路径，git 走 Windows 路径）。绕过：clone 到工作区子目录（如 `./tmp-h3`）而不是 `/tmp/`，或用 `$HOME/AppData/Local/Temp/` 显式路径。
- **`rm -rf` 报 `Device or resource busy`**：shell 当前 cwd 还在目标目录内时无法删除。先 `cd` 出目录再删（`cd "$HOME" && rm -rf ...`）。
- **Hub 生态 skill 评估（装前必看）**：MiniMax 官方 skill 是 MiniMax Hub 生态专属——SKILL.md 的 `allowed-tools` 全是 `hub_*` 工具（`hub_generate_image/video/audio` 等），Hermes 没有这些工具，**装了实际触发会卡住**。这类 skill 的价值是参考性的（提示词结构/分镜工作流可借鉴），装前明确告知用户"装了但触发会缺工具"，让用户决定是否值得。判断方法：`curl SKILL.md | grep allowed-tools`。例外：明确声明跨模型兜底的 skill（如 MiniMax-H3 的 3d-animation-short-generator 写"H3 默认，Seedance 2.0 兜底"）其工作流可通用。
