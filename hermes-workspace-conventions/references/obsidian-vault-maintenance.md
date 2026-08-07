# Obsidian Vault 维护约定

> 知识库路径：`C:\Users\HMSJ\Documents\KnowledgeBase\Obsidian Vault\`
> Git 仓库：`branchingjade/knowledge-base`（私有）
> 版本：master 唯一主分支

## 架构

```
Obsidian Vault/
├── MOC.md                       # 总索引，所有笔记入口
├── 知识库维护指南.md              # 维护规范
├── 踩坑记录.md                   # 跨项目通用踩坑，长期维护
├── Hermes运维/                  # Hermes 配置、策略、记忆镜像
│   └── memory/                  # 记忆快照（cron 自动同步）
├── 工具与集成/                   # 工具、MCP、工作流（子项目独立目录+自带复盘）
│   ├── 工具索引.md               # 全部工具（自建/外部、来源、用处）
│   ├── Eagle/ · Eagle曲多多元数据提取/
│   ├── Blender MCP/ · Resolve MCP/
│   └── 知识库/
├── 影视/                        # 影视项目
├── 技术/                        # 技术参考（基础知识库）
└── 日志/                        # 按日期归档的会话总结
```

## 笔记规范

### Frontmatter（每篇必加）

```yaml
---
tags:
  - tag1
  - tag2
date: YYYY-MM-DD
related:
  - "[[笔记A]]"
  - "[[笔记B]]"
---
```

- `related` 必须用 YAML 列表格式，禁止内联格式（`related: [[A]] · [[B]]`）——Obsidian 会报「无效属性」
- 禁止使用非标准属性（`name:`、`platforms:`、`version:`）——这些是 skill 元数据

### [[wikilinks]]

- 目录内互链：`[[笔记名]]`
- 跨目录：`[[子目录/笔记名]]`
- MOC 必须链接所有活跃笔记
- 交叉引用必须是叙事段落（场景+因果+教训），禁止标签式 `详见 [[xxx]]`

### 文件命名

- 中文优先，描述性强
- 目录名：`Hermes运维/`、`工具与集成/`
- 文件名不含 `:` `|` `/`

## 复盘规则

每个工具/项目目录下必须有 `xxx复盘.md`：
- 通用坑写入 `踩坑记录.md`
- 项目复盘 → [[踩坑记录]] 双向 [[wikilink]]

## 维护节奏

- 每次阶段完成后 → 写笔记、git push、MOC 补链
- 每日 cron：记忆同步至 `Hermes运维/memory/`、git 提交、悬空链接检查
- 每周 cron：过时内容、MOC 完整性、图谱孤岛

## 图谱健康

- 所有笔记（系统文件除外）必须有入链和出链
- 子域入口由 MOC.md 承担，不重复建空壳 landing page
- 高内容文件可加导航块（`> 📁 项目导航：[[link1]] · [[link2]]`）作为项目内入口
- 颜色分组通过标签前缀实现（犬子无双/Hermes运维/工具/日志/复盘/规范）

## 目录规则

| 目录 | 放什么 | 不放什么 |
|------|--------|---------|
| `Hermes运维/` | 备份、策略、飞书推送、Memory/Skill 原则 | 项目产出 |
| `工具与集成/` | 工具/MCP 集成文档、工作流、复盘 | Hermes 运维 |
| `影视/` | 影视项目产出（调色分析、剧本等） | 跨项目通用 |
| `技术/` | 通用技术研究、工具对比、基础知识库 | Hermes 专属 |
| `日志/` | 按日期归档的会话总结 | 技术笔记 |

## Git 工作流

```bash
cd ~/Documents/KnowledgeBase
git add -A
git commit -m "<type>: <描述>"
git push
```

- type：`docs`（新笔记）、`refactor`（重组架构）、`fix`（更正过时内容）
- 单分支 `master`
