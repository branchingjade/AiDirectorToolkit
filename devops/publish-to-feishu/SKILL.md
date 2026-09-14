---
name: publish-to-feishu
description: >
  将工作区的 Markdown 内容发布为飞书云文档（Doc）。覆盖三类场景：①Obsidian vault 笔记发布
  （带 frontmatter 回写）；②工作区任意 md 文档发布到指定飞书目录（如项目美术考据目录）；
  ③长文档骨架+分段 append 建后校对完整工作流。用 lark-cli docs +create/+update，
  默认 user 名义（项目目录需 --parent-token）。Trigger: 发布到飞书/推送到飞书/发布到飞书
  文档/push to feishu/把这份内容发到飞书/整理好放飞书.
---
# 发布内容到飞书云文档

将工作区里的 Markdown 文档创建为飞书云文档（Docx）。覆盖三类场景：①Obsidian 笔记发
布（带 frontmatter 回写）；②工作区任意 md 发到指定飞书目录（项目美术考据/知识库参考
库等）；③长文档骨架+分段 append 建后校对完整工作流。

## 场景路由

| 场景 | 触发词 | 关键差异 |
|---|---|---|
| **A. Obsidian 笔记发布** | "把这个笔记发到飞书" | 读笔记 → 删 frontmatter → 发到我的空间 → 写回 frontmatter → git commit |
| **B. 工作区文档发到指定目录** | "把这份造型参考发到美术考据目录" | 保留 frontmatter（如有）→ 用 `--parent-token` 指定项目目录 → 不写 frontmatter |
| **C. 长文档骨架+分段 append** | "整理一份文档发我" | 一次 create 写骨架（标题+说明）→ 多次 append 分段 → fetch + grep 校验 → str_replace 修错字 |

> **C 是 A/B 的超集**——任何超过 ~15KB 的内容都走 C。一次 overwrite 写 30KB+ 内容
> 触发飞书服务端 timeout/截断风险（实测 32KB 可行但不稳定）；骨架+append 分摊风险，
> 每段 5-10KB 是安全窗口。

## 流程（A：Obsidian 笔记）

1. 读取指定笔记（确认 frontmatter 有 `feishu: true`）
2. 去掉 YAML frontmatter，保留正文
3. 正文写入临时文件 `./_feishu_push.md`（lark-cli `@file` 只接受相对路径）
4. 执行：`lark-cli docs +create --doc-format markdown --content @_feishu_push.md --parent-position <位置> --as user`
5. 从返回 JSON 提取文档链接
6. 写回笔记 frontmatter：`feishu_doc_url: <url>`
7. git commit + push
8. 清理临时文件

## 流程（B：工作区文档→指定目录）

1. 读源文件（不删 frontmatter，但清理 YAML 标记若会污染抬头——见「md 清洗」节）
2. 决定目标目录：项目美术考据目录等**已知父目录**走 `--parent-token <folder_token>`，
   个人/未知目录走 `--parent-position my_library`
3. 直接 `lark-cli docs +create --doc-format markdown --content @<file.md> --parent-token <folder_token> --as user`
4. 拿回 doc_token + url

> 父目录 token 从 OV 记忆/项目文档登记/已建文档所在目录里取——别问用户"放在哪个目录"，按
> 已有约定拍板（如伏妖记美术考据目录 = `LPqefEZoHlbICEdkDd9cUGjFnCd`）。

## 流程（C：长文档骨架+分段 append）

适用：内容超过 15KB / 多章节 / 含表格+代码块混排。

1. **骨架先写**：标题+文档性质说明+章节目录提示，写入临时 `_push_skeleton.xml`
2. **首次 create**：`lark-cli docs +create --parent-token <folder_token> --content @_push_skeleton.xml --as user`
   - 拿回 doc_token 与 revision_id（此时 revision=3，骨架已被计入）
3. **分段 append**：把每章（5-10KB）写入独立 XML 文件，按顺序逐次
   `lark-cli docs +update --doc <token> --command append --content @<part_n>.xml --as user`
   - 每段 revision 自增；append 是 block 级追加，不会冲掉前文
   - **不要用 overwrite 第二次**——会把已 append 的图/已 write 的块冲掉（详见
     feishu-doc-maintenance 5·七 坑 4）
4. **建后校验（关键）**：
   - `lark-cli docs +fetch --doc <token> --scope full --doc-format xml` 拉回全文
   - `grep -c "关键词"` 核对易错字 / 朝代名 / 数据点
   - 发现错字用 `str_replace` 修（XML 模式下 `--pattern` 行内匹配，不是 `--old-string`；
     `--content` 不是 `--new-text`——见 feishu-doc-maintenance 5·六）

## lark-cli 关键参数

### create 子命令（场景 A/B/C 通用）

```
lark-cli docs +create \
  --content @<file> \
  --parent-token <folder_token> \
  --as user
```

- `--content @file`：**必须相对 cwd 的相对路径**，绝对路径报 `unsafe file path`
- `--parent-token <token>`：发到指定飞书文件夹（**项目目录用这个**）
- `--parent-position my_library`：发到我的空间（**未指定目录时默认**）
- `--doc-format xml`（默认）/ `markdown`：长文档含表格/代码块混排用 XML；纯散文用 markdown
- `--as user`：以用户身份创建（有 `docx:document:create` 权限）

### update --command append（场景 C 用）

```
lark-cli docs +update --doc <token> --command append --content @<part.xml> --as user
```

- append 在文档末尾追加新 block，不影响已有内容
- 多次 append 顺序即文档最终章节顺序
- append 后 revision 自增；不要根据 revision 推断内容顺序

### update --command str_replace（建后校对用）

```
lark-cli docs +update --doc <token> --command str_replace \
  --pattern "<原文锚点>" --content "<新文>" --as user
```

- **参数陷阱**：是 `--pattern`（不是 `--old-string`/`--old-text`）+ `--content`（不是
  `--new-text`）——这两个名字写错会报 unknown flag
- 替换后必须 fetch 验证（str_replace 可能静默成功但 pattern 没匹配到）
- XML 模式下 str_replace 只支持行内匹配，不能跨 block；整段替换用 `block_replace`
- 全文 grep 双校验：旧文本 0 命中 + 新文本 1 命中 = 改成功

## Markdown 转义规则

- 一级标题 `# xxx` = 文档标题（只能有一个）
- 正文从 `## ` 开始
- Windows 路径中的 `\` 需转义为 `\\`
- `[[wikilink]]` 改为纯文本 `笔记名`

## md 导入 docx 前的清洗（防抬头脏）

**Obsidian/markdown 文件直接 `drive +import --type docx` 或 `docs +create --doc-format markdown`
时，YAML frontmatter（`tags/date/updated/related`）会被当成正文显示在文档抬头**——
用户会指出"抬头有不需要的东西"。导入前必须两步清洗：

```python
import re
content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.S)  # ① 删 YAML frontmatter
content = content.replace('\r\n', '\n')                          # ② CRLF → LF
```

**XML 模式不受影响**——XML 写不进 `<title>` 之外的元数据。但 `docs +create --doc-format
markdown` 模式下要清洗。

## 输出

发布成功后输出：
```
✅ 已发布到飞书文档
📄 标题
🔗 https://xxx.feishu.cn/docx/xxxxx
```

## Pitfalls

- `@file` 只接受当前工作目录下的相对路径，不能用绝对路径（绝对路径报
  `unsafe file path: --file must be a relative path within the current directory`）
- 笔记开头只能有一个 `# 标题`（文档标题），正文标题从 `##` 开始
- `--as bot` 没有文档创建权限，必须用 `--as user`（2026-09-03 伏妖记美术考据实战
  走 user 名义落档，与本 skill 口径一致）
- 发布后记得更新 frontmatter `feishu_doc_url`（场景 A），避免重复发布
- **长文档不要一次 overwrite**：超过 15KB 触发 timeout 风险，走场景 C 骨架+分段 append
- **str_replace 改后必须 fetch 验证**：本会话实战发现 `眉眼`→`状元` 错字录入，靠
  fetch + grep `眉眼=0 / 状元=1` 双校验才暴露+修复
- **str_replace 参数名陷阱**：`--pattern` 不是 `--old-string`，`--content` 不是
  `--new-text`——首次踩坑重试一次的成本 = 一次失败的 lark-cli 调用
- **`--content @file` 的 file 不能跨目录**：必须在 cwd 下；写文件时先确认 cwd（通常是
  `Documents/Hermes/`），必要时 `cd` 后再调
- **与 feishu-doc-maintenance 的边界**：
  - 本 skill 管"创建+写入"（create/append/overwrite）
  - feishu-doc-maintenance 管"已有文档的修改"（str_replace/block_replace/media-insert/
    权限/格式修复/异步删除移动）
  - 实战工作流经常组合：先 publish-to-feishu（场景 C 骨架+append），再 feishu-doc-maintenance
    （str_replace 修错字 + media-insert 嵌图）

## 相关

- [lark-doc](lark-doc/SKILL.md) — 文档读写命令语法（含 XML/Markdown 标签规则）
- [lark-drive](lark-drive/SKILL.md) — 云空间移动/删除/权限
- [lark-shared](lark-shared/SKILL.md) — 认证与 bot 权限处理
- [feishu-doc-maintenance](../feishu-doc-maintenance/SKILL.md) — 已有文档的格式修复/
  str_replace/media-insert/权限诊断/异步操作容错