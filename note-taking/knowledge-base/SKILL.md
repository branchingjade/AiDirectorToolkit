---
name: knowledge-base
description: 知识库完整维护系统——目录架构、笔记创建、frontmatter规范、MOC同步、Git版本控制、持续维护触发规则。
platforms: [linux, macos, windows]
version: 3.1.1
---

# 知识库维护

> 触发词：知识库、KnowledgeBase、vault、笔记、MOC、知识管理、Obsidian

不只是文件读写——这是知识库的完整维护系统。涵盖架构设计、笔记生命周期（创建→链接→提交）、MOC 索引维护、两级巡检，以及持续更新的触发规则。

## 目录架构

```
~/Documents/KnowledgeBase/              ← Git 仓库 (branchingjade/knowledge-base)
├── .git/
├── .gitignore
├── README.md
├── CHANGELOG.md
└── Obsidian Vault/                     ← Obsidian 唯一仓库 = GitHub 主内容
    ├── .obsidian/                      ← Obsidian 配置
    ├── MOC.md                          ← 总索引（唯一入口）
    ├── 知识库维护指南.md                ← 维护规范
    ├── 踩坑记录.md                      ← 跨项目通用踩坑，长期维护
    ├── Hermes运维/                     ← 🛠 Hermes 配置、策略、复盘
    │   ├── 备份迁移.md
    │   ├── 浏览器双轨策略.md
    │   ├── 飞书推送.md
    │   ├── Memory与Skill划分原则.md
    │   ├── Memory清理复盘-2026-07-22.md
    │   └── Memory优化踩坑记录-2026-07-22.md
    ├── _hermes/                        ← 🤖 Hermes 协作数据层（2026-08-07 起）
    │   ├── memory/                     ← 记忆快照（cron 自动同步，真源 ~/AppData/Local/hermes/memories/）
    │   │   ├── MEMORY.md
    │   │   └── USER.md
    │   ├── 记忆MOC.md                  ← 记忆总 MOC（#记忆 成支）
    │   ├── 飞书协作记忆MOC.md          ← 飞书协作记忆枢纽（#飞书协作）
    │   ├── 会话路由.json
    │   ├── 成员名单.json
    │   └── 评论会话/                   ← 评论会话记忆（git 归档）
    ├── 工具与集成/                     ← 🔧 工具、MCP、工作流
    │   ├── 工具索引.md                  ← 全部工具（自建/外部、来源、用处）
    │   ├── Eagle/                       ← Eagle 工具本体
    │   │   ├── Eagle MCP 集成.md
    │   │   └── Eagle 复盘.md
    │   ├── Eagle曲多多元数据提取/        ← quduoduo→Eagle
    │   │   ├── 元数据提取.md
    │   │   └── 提取复盘.md
    │   ├── Blender MCP/
    │   │   ├── Blender MCP 集成.md
    │   │   └── Blender MCP 复盘.md
    │   ├── Resolve MCP/
    │   │   ├── Resolve MCP 集成.md
    │   │   └── Resolve MCP 复盘.md
    │   ├── Kimi WebBridge/
    │   │   ├── Kimi WebBridge 集成.md
    │   │   └── Kimi WebBridge 复盘.md
    │   ├── 黑盒语音/
    │   │   ├── 黑盒语音 Bot 集成.md
    │   │   └── 黑盒语音复盘.md
    │   ├── 备份迁移/
    │   │   └── 备份迁移复盘.md
    │   └── 知识库/
    │       ├── knowledge-base-skill.md
    │       └── 知识库建设复盘.md
    ├── 犬子无双/                       ← 🎬 影视项目（直接置于 vault 根）
    │   ├── 人名条设计.md
    │   ├── 第一场调色分析.md
    │   ├── 犬子无双复盘.md
    │   ├── references/
    │   │   ├── 人名条设计参考.md        ← 图文参考文档（含截图）
    │   │   └── assets/
    │   │       ├── 钢的琴_片头字幕.jpg
    │   │       ├── 工厂标语_实拍.jpg
    │   │       ├── 白日焰火_字幕.jpg
    │   │       ├── 铁西区_纪实.jpg
    │   │       ├── 贾樟柯_字幕风格.jpg
    │   │       └── 沈念安_人名条参考.png
    │   └── assets/
    ├── 技术/                           ← 🔬 技术参考（基础知识库）
    │   ├── 知识库架构.md
    │   └── 超分/
    │       ├── 图像超分指南.md
    │       ├── 视频超分工具对比.md
    │       └── SeedVR2 fp8伪影排查.md
    └── 日志/                           ← 📋 会话记录（年月周结构）
```

## 日志架构

```
日志/
└── YYYY-MM/                    ← 按月分目录
    ├── YYYY-MM-月报.md          ← 月报=索引入口（一文件双职）
    ├── YYYY-MM-W{N}-周报.md     ← 周报（W号按月重置）
    ├── W1/  YYYY-MM-DD.md       ← 日报（全日期命名）
    ├── W2/
    └── ...
```

- 月报 = 月度索引 + 月度总结（主题/跨日关联/关键决策/产出/教训）
- 空周不建目录，有内容的周才建
- 日报↔周报↔月报 全链路 related 字段交叉引用

### 图谱颜色分组

Obsidian 图谱配置 6 个颜色组（`graph.json` 中 `colorGroups` 字段）：

| 颜色 | 搜索条件 | 覆盖领域 |
|------|---------|---------|
| 🟢 | `tag:#犬子无双` | 犬子无双项目 |
| 🔵 | `tag:#Hermes运维` | Hermes运维 |
| 🟡 | `tag:#工具` | 工具与集成 |
| 🟣 | `tag:#日志` | 日志 |
| 🔴 | `tag:#复盘` | 复盘/教训 |
| 🟠 | `tag:#规范` | 规范/维护 |

每个笔记必须至少包含一个颜色标签。标签用纯文本格式，不在 tags 中使用 `[[wikilink]]`。

- **KnowledgeBase 根目录** = Git 仓库
- **Obsidian Vault 子目录** = Obsidian 打开的唯一仓库 = GitHub 主内容
- 仓库根只保留 `README.md`、`CHANGELOG.md` 和 `.gitignore`，不放笔记
- GitHub clone 下来 = Obsidian 打开的内容，完全一致

### 复盘规则

每个工具/项目目录下必须有 `xxx复盘.md`：
- 通用坑写入 `踩坑记录.md`
- 项目复盘 → [[踩坑记录]] 双向 [[wikilink]]，叙事式交叉引用
- 复盘内容：做了什么、核心经验、教训

### 工具文档模板

新增工具时，在 `工具与集成/<工具名>/` 下创建两个文件：

**`xxx 集成.md`**：
```yaml
---
tags: [工具, <关键词>, MCP/integration]
date: YYYY-MM-DD
related:
  - "[[工具索引]]"
  - "[[xxx 复盘]]"
---
# xxx 集成
> 🏗️ 自建 | 状态：<已配置/开发中>
## 架构 / 配置 / 核心能力 / 已知陷阱
> 详见 [[xxx 复盘]] · [[踩坑记录]]
```

**`xxx 复盘.md`**：
```yaml
---
tags: [工具, <关键词>, 复盘]
date: YYYY-MM-DD
related:
  - "[[xxx 集成]]"
  - "[[踩坑记录]]"
---
# xxx 复盘
> 关联：[[xxx 集成]] · [[踩坑记录]]
## 做了什么
## 核心经验
### 1. ...
## 教训
> 详见 [[踩坑记录#具体章节]]
```

**经验段落写作标准**：每条经验必须有决策逻辑——不只是"做了什么"，要写出**为什么这样做、替代方案是什么、代价是什么**。参考 `Eagle 复盘#核心经验`、`Blender MCP 复盘#核心经验` 的叙事深度。

**待补充占位**：工具刚创建时经验和教训可能空白，用 `⚠️ 待补充：<引导性问题>` 格式标记，方便后续查找和填补。搜索 vault 中 `⚠️ 待补充` 即可找到所有空缺。

## 笔记创建规范

### Frontmatter 模板

每篇笔记必须包含以下 frontmatter：

```yaml
---
tags:
  - 分类标签1
  - 分类标签2
date: YYYY-MM-DD
related:
  - "[[关联笔记1]]"
  - "[[关联笔记2]]"
  - "[[踩坑记录]]"
---
```

- `tags`：至少 2 个标签，首标签为父目录/主题
- `date`：创建日期
- `related`：YAML 列表格式，用 `[[wikilink]]` 链接关联笔记。必须用列表格式（避免 Obsidian 属性类型推断不一致导致"无效属性"）

### 命名规范

| 类型 | 格式 | 示例 | 说明 |
|------|------|------|------|
| 日报 | `YYYY-MM-DD.md` | `2026-07-21.md` | 全日期，搜索自描述 |
| 周报 | `YYYY-MM-W{N}-周报.md` | `2026-07-W2-周报.md` | W号按月重置 |
| 月报 | `YYYY-MM-月报.md` | `2026-07-月报.md` | 月报=索引，一文件双职 |
| 普通笔记 | `中文名.md` | `网页抓取任务复盘.md` | 不含 `:` `\|` `/` |
| 参考文档 | `中文名.md` | `人名条设计参考.md` | 放 `references/` 下 |

- 统一用 `-` 分隔（不用 `_` `~` 混搭）
- 路径已含信息不在文件名中重复
- 日报/周报/月报全日期命名 → 离开目录仍可识别

### 创建流程

1. 判断归属目录（按权重）
2. `write_file` 创建笔记，含完整 frontmatter + 内容
3. 检查 MOC.md 是否需要新增链接
4. `git add -A && git commit -m "..." && git push`

### MOC 维护

- 新增笔记后，检查 MOC.md 对应分类下是否有该笔记的链接
- 如无，在 MOC.md 对应小节追加 `- [[新笔记名]] — 一句话描述`
- 删除笔记时同步移除 MOC 链接
- MOC.md 自身保持精简，不重复笔记内容

### 交叉引用深度标准

**禁止标签式链接**（`详见 [[xxx]]`）。每条交叉引用必须是叙事段落，包含三要素：

1. **场景**：在什么任务/阶段踩的或发现的
2. **因果**：为什么会在这里发生、导致了什么
3. **教训**：从中学到什么

**双向性**：A 链到 B 的同时，B 也必须链回 A。踩坑记录 → 项目笔记 → 踩坑记录，形成闭环。

**精确性**：用 `[[笔记名#章节锚点|显示文本]]` 链到具体位置，不是笼统链整篇。

**独立可读**：不跳转也能理解上下文。读者只看当前笔记就能通顺读完，需要深入时再点链接。

### 踩坑记录规范

每条坑必须含 `> 发生在 [[项目笔记]]` 叙事段——不可只有 wikilink，要附一段上下文：什么项目、当时在做什么、为什么会踩。坑与坑之间有关联时（如"同一晚连踩两坑"），明确写出姊妹坑链接。

## 笔记写入时机

**阶段性完成后写，不即时写。** 一项任务/功能/排查做完了、验证过了、结论清晰了，再落笔记。半成品不写。

## 维护分级

### 每日小维护

| 检查项 | 操作 |
|--------|------|
| Hermes 记忆同步 | `/bin/cp` 同步 MEMORY.md + USER.md 到 `_hermes/memory/`（Windows MSYS 必须用 `/bin/cp` 绕过 `cp -i` 别名；旧位置 `Hermes运维/memory/` 已于 2026-08-07 废弃删除） |
| 未提交 git 变更 | `git status --short`，有则 commit + push |
| 悬空 `[[wikilinks]]` | 遍历 frontmatter `related`，确认目标文件存在 |
| 新增文件归位 | 有 `.md` 不在正确目录 → 移动 |

> Cron 自动化执行细节见 `references/cron-daily-maintenance.md`
> Shell 命令速查（execute_code 不可用时，如 cron jobs）见 `references/weekly-maintenance-shell-commands.md`

### 每周大维护（附加每日项）

| 检查项 | 操作 |
|--------|------|
| 过时内容 | 比对当前配置/版本，标记或更新 |
| MOC 完整性 | 遍历所有笔记，确认 MOC.md 有对应链接 |
| 目录健康 | 检查是否有空目录、命名不一致、根目录进入笔记 |
| 图谱孤岛 | 无 `[[wikilinks]]` 入/出的笔记，补链或归档 |
| 颜色标签 | 确认所有笔记含至少一个颜色组标签（犬子无双/Hermes运维/工具/日志/复盘/规范） |

> 自动化检测脚本：`scripts/weekly-check.py` — 覆盖悬空链接、孤岛分析、MOC 覆盖。用法 `python3 scripts/weekly-check.py [--vault /path]`。

## 持续维护触发

以下场景在**阶段完成后**触发写笔记：

| 触发场景 | 归属目录 | 示例 |
|---------|---------|------|
| 技术决策/方案选型 | `技术/` | 工具对比、架构选型 |
| 排查/故障分析 | `技术/` | fp8 伪影、性能瓶颈 |
| 配置变更/迁移 | `Hermes运维/` | 备份切换、网关迁移 |
| 方法论/工作流 | `Hermes运维/` | Memory/Skill 划分 |
| 工具/MCP 集成 | `工具与集成/` | Eagle MCP、Blender MCP、Resolve MCP |
| 踩坑/教训 | `踩坑记录.md`（通用）或项目复盘 | MSYS路径、编码、API边界 |

**禁止**：A. 过程半成品写笔记 B. 做完不留笔记。

### Push 规则

KnowledgeBase 内任何文件变动后：先 `git status --short` 展示变更清单 → 再 `git add -A && git commit -m "..." && git push`。少量单文件提交不需询问，批量或多文件时用 `clarify` 确认。

## Skill 自维护

本 skill 是知识库规范的**唯一权威源**。以下场景必须同步更新本 skill + GitHub 副本：

| 场景 | 更新内容 |
|------|---------|
| 笔记规范变更 | frontmatter 模板、命名规则、交叉引用标准 |
| 目录架构调整 | 架构图、权重说明 |
| 维护流程变化 | 每日/每周巡检项、触发表 |
| 新增笔记类型 | 触发表追加行 |

**GitHub 副本同步**：skill 源文件（`SKILL.md`）和 vault 副本（`knowledge-base-skill.md`）使用不同的 frontmatter——源文件用 `name:`/`version:` 等 skill 元数据，vault 副本用 `tags:`/`date:`/`related:` 等 Obsidian 属性。同步时先复制内容再手动调整 frontmatter：

```bash
# 1. 复制正文（跳过 frontmatter）到 vault 副本
sed -n '/^---$/,/^---$/!p' ~/AppData/Local/hermes/skills/note-taking/knowledge-base/SKILL.md \
  > ~/Documents/KnowledgeBase/Obsidian\ Vault/工具与集成/知识库/knowledge-base-skill.md.tmp

# 2. 用 write_file 重写 vault 副本（保留 Obsidian frontmatter + 新正文）
```

默认路径：`~/Documents/KnowledgeBase/Obsidian Vault`。可用 `OBSIDIAN_VAULT_PATH` 环境变量覆盖。路径含空格，优先用 `read_file`/`write_file`/`search_files` 等文件工具而非 shell 命令。

## 常见坑

### `python3` 在 MSYS 下调用 Windows Python 时 MSYS 路径被双重转换

**现象**：`python3 "/c/Users/.../weekly-check.py"` 报 `can't open file 'C:\\c\\Users\\...'`，MSYS 路径 `/c/...` 被 Python 的 Windows 运行时错误转换为 `C:\c\...`。

**根因**：MSYS bash 传递 `/c/...` 路径给 Windows 原生 Python 时，Python 的路径解析层将 `/c` 当作相对路径并拼接当前驱动器号，产生 `C:\c\...` 这种不存在的路径。

**解决**：对所有需要传给 `python3`（Windows 原生 Python）的路径，使用 Windows 正斜杠格式：

```bash
# ❌ MSYS 路径 → Python 3.12 报错
python3 "/c/Users/HMSJ/AppData/.../weekly-check.py"

# ✅ Windows 正斜杠格式
python3 "C:/Users/HMSJ/AppData/.../weekly-check.py"
```

涉及场景：运行 `scripts/weekly-check.py`、任何传给 Windows Python 的脚本路径。

### `search_files` 在含空格的 vault 路径下可能返回 0 结果

**现象**：`search_files(path="~/Documents/KnowledgeBase/Obsidian Vault", pattern="*.md", target="files")` 返回 0 结果，但 `find` 同一路径正常列出 39 个 .md 文件。

**根因**：疑似 Hermes 文件搜索工具对含空格路径的内部解析问题（"Obsidian Vault" 中间有空格）。

**解决**：在 vault 路径含空格时，用 terminal `find` 代替 `search_files` 做文件列表：

```bash
cd "/c/Users/HMSJ/Documents/KnowledgeBase/Obsidian Vault" && find . -name '*.md' -not -path './.obsidian/*' | sort
```

`read_file` 和 `write_file` 不受影响——仅 `search_files` 有此问题。

### `weekly-check.py` 的 wikilink 正则误抓代码片段

**现象**：`weekly-check.py` 报告 `[[{"tag": "md", "text": content}]]` 为 TRUE DANGLING。

**根因**：wikilink 提取正则 `\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]` 无法区分真实 wikilink 和代码片段（如 Python f-string / dict 中的 `[[...]]` 结构）。TEMPLATE_LINKS 白名单只覆盖已知模板占位符，不覆盖任意代码。

**影响**：仅影响 `飞书Markdown渲染修复.md` 等含 `[[...]]` 代码片段的笔记，误报数量极少（当前仅 1 条）。

**缓解**：无需修复——人工确认后忽略即可。若误报增多，可在 TEMPLATE_LINKS 中添加具体片段或增加代码块过滤逻辑。

### write_file 创建的 frontmatter 导致 Obsidian "无效属性"

**现象**：`write_file` 创建的新文件在 Obsidian 中显示"无效属性"红色警告，但通过 `git mv + patch` 编辑的旧文件无此问题。

**根因**：Obsidian Properties 对 `related: [[A]] · [[B]]` 内联字符串格式的类型推断不稳定——`write_file` 生成的全新文件被 Obsidian 当作新属性类型解析，可能与已有文件的类型缓存冲突。

**解决**：`related` 字段必须用 YAML 列表格式：

```yaml
# ❌ 内联格式（新文件可能触发"无效属性"）
related: [[笔记A]] · [[笔记B]]

# ✅ YAML 列表格式（稳定兼容）
related:
  - "[[笔记A]]"
  - "[[笔记B]]"
```

此规则已同步到 frontmatter 模板和全部 vault 笔记。批量修复脚本：`scripts/fix-frontmatter.py [vault_path]`。

**批量修复经验**（2026-07-16）：vault 中 32 个文件的 `tags:` 和 `related:` 字段使用了内联列表格式（`tags: [a, b]`），导致 Obsidian 全部标红。用 Python 正则批量替换为 YAML 列表格式。修复后 git commit + push 即可。

### Agent 忘记主动触发维护（最常见）

写完笔记、git push 不是终点。以下场景 agent 必须**主动检查并执行**，不等用户问：

| 检查项 | 操作 |
|--------|------|
| 有新笔记/MOC 变更 | `git add -A && git commit && git push` |
| 有悬空 wikilink | 遍历 related 确认目标文件存在 |
| 阶段成果完成 | 主动问"要写 Obsidian 笔记吗？"而不是沉默跳过 |

反面案例：处理了 20 首 Eagle 音乐、更新了 skill、加了 memory 铁律——全程没提 Obsidian，用户问「维护了吗」才发现遗漏。

### `git -C` 在 Windows MSYS 下失败

**现象**：`git -C ~/Documents/KnowledgeBase status --short` 报 `fatal: cannot change to '...': No such file or directory`，但 `ls` 同一路径正常。

**根因**：`git -C` 在 MSYS/git-bash 下对含 tilde 展开的路径解析不稳定。

**解决**：先 `cd` 到仓库目录再执行 git 命令：

```bash
# ❌ 失败
git -C ~/Documents/KnowledgeBase status --short

# ✅ 可靠
cd ~/Documents/KnowledgeBase && git status --short
```

涉及场景：所有 KnowledgeBase 仓库的 git 操作。

### MSYS `cp -i` 别名导致静默失败

Windows git-bash/MSYS 环境下 `cp` 默认 alias 为 `cp -i`（交互式确认）。在 cron 或非 TTY 模式下，`cp -i` 因无法读取用户输入而**静默跳过覆盖**（不报错、不写入、exit code 0）。

**修复**：使用 `/bin/cp` 绕过别名，或用 `\cp`：

```bash
# ❌ 静默失败
cp source target

# ✅ 强制覆盖
/bin/cp source target
```

涉及场景：记忆同步（`cp ~/AppData/Local/hermes/memories/*.md` → vault）、GitHub 副本同步。

### 悬空 Wikilink 检测误报

自动化检测 `[[wikilink]]` 时常见误报来源：

1. **语法示例文本**：笔记正文中的 `[[...]]` 是展示 wikilink 语法，不是真实链接
2. **空 wikilink**：`[[]]` 残留或 grep 提取 artifact
3. **路径分隔符**：`[[子目录/笔记名]]` 提取出的 link 名含 `/`，对比 `.md` 文件名时需取最后一段（`${link##*/}`）或直接用文件路径匹配

**标准工具**：`scripts/weekly-check.py` — 已内置上述误报过滤 + Obsidian 风格的裸文件名解析（`name_to_path` 索引），直接运行即可。

**Shell 备选**：`comm -23 <(grep -roh '\\[\\[[^]]*\\]\\]' ... | sed ... | sort -u) <(find ... -name '*.md' | sed ... | sort -u)`，然后人工排查 `...` 和空行等误报。

### Wikilink 解析必须按裸文件名匹配

**陷阱**：编写 wikilink 解析器时**不能只做路径精确匹配**。Obsidian 的 `[[Eagle 复盘]]` 会匹配 vault 中任意位置的 `Eagle 复盘.md`（如 `工具与集成/Eagle/Eagle 复盘.md`），不要求调用方给出完整路径。

**根因**：只检查 `link in paths` 或 `link + '.md' in paths` 会把所有裸文件名链接误判为悬空。本 session 第一版脚本因此产生 47 条假阳性（包括 `[[Blender MCP 集成]]`、`[[Resolve MCP 集成]]` 等实存链接）。

**解决**：构建 `name_to_path: dict[str, set[str]]` 索引（`{bare_filename: {rel_path, ...}}`），解析时提取 `link.split('/')[-1]` 做后备匹配。`scripts/weekly-check.py` 已实现此逻辑。

### `write_file` 到 `/tmp/...` 在 Windows MSYS 下路径错位

**现象**：`write_file(path="/tmp/kb-check.py")` 写入成功，但 `python3 /tmp/kb-check.py` 报 `No such file or directory`，`python3 C:/tmp/kb-check.py` 同样失败。`ls /tmp/kb-check.py` 在 MSYS 终端中却能看到文件。

**根因**：`write_file` 将 `/tmp/...` 解析为 Windows 原生路径 `\tmp\...`（即 `C:\tmp\...`），而 MSYS 的 `/tmp` 映射到完全不同的位置（如 `C:\msys64\tmp`）。两个 `/tmp` 不是同一个目录。

**解决**：临时脚本写入用户目录下的确定性路径（如 `C:\Users\HMSJ\Documents\...` 或 vault 根目录），确保 Windows Python 和 MSYS 都能访问同一文件：

```bash
# ❌ write_file 到 /tmp → 实际写入 C:\tmp\，MSYS 的 /tmp 看不到
write_file(path="/tmp/kb-check.py", ...)
python3 "/tmp/kb-check.py"  # 失败

# ✅ 写入 Windows 绝对路径
write_file(path="C:/Users/HMSJ/Documents/KnowledgeBase/kb-check.py", ...)
python3 "C:/Users/HMSJ/Documents/KnowledgeBase/kb-check.py"  # 成功
```

涉及场景：cron 日检中需要写临时 Python 脚本替代 `execute_code` 时。

### Shell `basename` 处理中文文件名含空格时截断

**现象**：shell 循环中 `basename "$f" .md` 对含空格的中文文件名（如 `Blender MCP 集成.md`）输出被截断为 `MCP`、`集成.md` 等碎片。

**根因**：shell `for f in $(find ...)` 默认按空格/换行分词，中文文件名含空格时被拆成多个 token。`basename` 只处理了截断后的片段。

**解决**：涉及中文文件名的批量处理一律用 Python（`python3 -c`），不要用 shell `for` 循环 + `basename`。孤岛检测、MOC 完整性等需要 bare name 提取的场景，Python 的 `os.walk` + `f[:-3]` 远比 shell 可靠。

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

### Wikilinks 交叉引用

- `[[笔记名]]` — 基础链接
- `[[笔记名#章节标题|显示文本]]` — 精确锚点，直指目标章节
- 踩坑记录用 `> 发生在 [[项目笔记]]：具体场景描述` 格式做反向叙事链接

**深度标准**：交叉引用必须含上下文叙事，两份文档各读各的通顺，交叉时能顺藤摸瓜。

| ❌ 标签式 | ✅ 叙事式 |
|----------|---------|
| `详见 [[踩坑记录]]` | 讲清楚**怎么踩的、为什么这里会踩、教训是什么** → `详见 [[踩坑记录#具体章节]]` |

## Git integration

When the vault lives inside a Git repo (e.g. as a subdirectory like `repo/Obsidian Vault/`), `.gitignore` must handle `.obsidian/` directories correctly.

### .gitignore pattern for nested vaults

```
# Track core config, ignore everything else
**/.obsidian/*
!**/.obsidian/app.json
!**/.obsidian/appearance.json
!**/.obsidian/core-plugins.json
!**/.obsidian/community-plugins.json
**/.obsidian/workspace*
```

**Why `**/` prefix is required:** `.obsidian/*` (without `**/`) only matches `.obsidian/` at the repo root — it will NOT match `Subfolder/.obsidian/`. The `**/` glob matches at any depth, so `**/.obsidian/*` correctly ignores `.obsidian/` directories anywhere in the repo tree.

**Why `/*` not `/`:** `.obsidian/` (trailing slash, directory-only match) prevents re-inclusion of files inside it — Git refuses to un-ignore files whose parent directory is excluded. Use `.obsidian/*` (match all contents) so that negation patterns (`!**/.obsidian/app.json`) can re-include specific files.

Verify with `git check-ignore`:
- Core config (app.json, etc.) should NOT be ignored → tracked
- workspace.json and everything else inside `.obsidian/` should be ignored
