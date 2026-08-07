---
name: publish-to-feishu
description: >
  将 Knowledge Base 中的笔记发布为飞书文档（Doc）。用 lark-cli docs +create 创建文档，
  自动回填文档链接到 frontmatter。Trigger: 发布到飞书/推送到飞书/发布到飞书文档/push to feishu.
---

# 发布笔记到飞书文档

将 Obsidian vault 中的 Markdown 笔记创建为飞书文档。

## 流程

1. 读取指定笔记（确认 frontmatter 有 `feishu: true`）
2. 去掉 YAML frontmatter，保留正文
3. 正文写入临时文件 `./_feishu_push.md`（lark-cli `@file` 只接受相对路径）
4. 执行：`lark-cli docs +create --doc-format markdown --content @_feishu_push.md --parent-position <位置> --as user`
5. 从返回 JSON 提取文档链接
6. 写回笔记 frontmatter：`feishu_doc_url: <url>`
7. git commit + push
8. 清理临时文件

## lark-cli 关键参数

```
lark-cli docs +create \
  --doc-format markdown \
  --content @_feishu_push.md \
  --parent-position my_library \
  --as user
```

- `--doc-format markdown`：直接传 Markdown，无需转 XML
- `@_feishu_push.md`：文件传参，绕开 shell 转义问题
- `--parent-position`：默认 `my_library`（我的空间），也可用 `feishu_parent` frontmatter 覆盖
- `--as user`：以用户身份创建（有 `docx:document:create` 权限）

## Markdown 转义规则

- 一级标题 `# xxx` = 文档标题（只能有一个）
- 正文从 `## ` 开始
- Windows 路径中的 `\` 需转义为 `\\`
- `[[wikilink]]` 改为纯文本 `笔记名`

## 输出

发布成功后输出：
```
✅ 已发布到飞书文档
📄 标题
🔗 https://xxx.feishu.cn/docx/xxxxx
```

## Pitfalls

- `@file` 只接受当前工作目录下的相对路径，不能用绝对路径
- 笔记开头只能有一个 `# 标题`（文档标题），正文标题从 `##` 开始
- `--as bot` 没有文档创建权限，必须用 `--as user`
- 发布后记得更新 frontmatter `feishu_doc_url`，避免重复发布
