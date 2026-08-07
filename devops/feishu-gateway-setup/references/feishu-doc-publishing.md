# 飞书文档（Doc）发布

从 Obsidian/本地 Markdown 直接创建飞书文档。

## 前提

- `lark-cli` 已安装并登录（`lark-cli auth status` 确认 `docx:document:create` 权限）
- 以用户身份操作（`--as user`），bot 没有文档创建权限

## 基本命令

```bash
lark-cli docs +create \
  --doc-format markdown \
  --content @_push.md \
  --parent-token <folder_token> \
  --as user
```

- `--doc-format markdown`：直接传 Markdown，无需转 XML
- `@_push.md`：文件传参（**必须用相对路径**，`@file` 不接受绝对路径）
- `--parent-token`：目标文件夹 token（飞书文件夹 URL 中提取）
- `--as user`：用户身份，需 `docx:document:create` scope

## 文档标题规则

- 笔记第一个 `# 标题` = 飞书文档标题
- 正文从 `## ` 开始
- 只能有一个一级标题，否则标题可能被识别为 `Untitled`

## 返回

```json
{
  "document": {
    "document_id": "Q8i7djCP0ovIygxVy8zcsWmRnDh",
    "url": "https://my.feishu.cn/docx/Q8i7djCP0ovIygxVy8zcsWmRnDh"
  }
}
```

## Markdown 转义

| 字符 | 转义 |
|------|------|
| `\` | `\\` |
| `#` 行首 | `\#` |
| `*` `_` `[` `]` `` ` `` `$` `~` `<` | 前加 `\` |
| 代码块内 | 无需转义 |
| `[[wikilink]]` | 改为纯文本 |

## 修改现有文档（Docx API 局限）

**⚠️ `my.feishu.cn` 文档的 docx API 写端点（PATCH/DELETE/POST blocks）返回 404。** 只有 GET（读取 blocks）可用。这是平台限制，非 lark-cli 版本问题。

### 可用操作

- `GET /open-apis/docx/v1/documents/{id}/blocks` — 读取文档结构 ✅
- `lark-cli drive +export` — 导出为 markdown ✅
- `lark-cli drive +import --type docx` — 新建文档 ✅
- `lark-cli drive +inspect --url` — 查看文档元信息 ✅

### 不可用操作

- `PATCH /.../blocks/{block_id}` — 更新块内容 ❌ (404)
- `DELETE /.../blocks/{block_id}` — 删除块 ❌ (404)
- `POST /.../blocks/{parent_id}/children` — 创建子块 ❌ (404)

### 修改文档的 Workaround

导出 → 修改 markdown → 导入为新文档：

```bash
# 1. 导出原文档为 markdown
lark-cli drive +export --token <doc_token> --doc-type docx --file-extension markdown

# 2. 用脚本/Python 修改 markdown 内容

# 3. 导入为新文档
lark-cli drive +import --file <modified.md> --type docx
```

新文档有不同 URL，需手动替换原链接。

## lark-cli 常见坑

- **`--data` 只接受内联 JSON 字符串**，不支持 `@file` 语法
- **路径限制**：`--output-dir`/`--file` 只能使用当前目录下的相对路径
- **Windows Python subprocess**：`lark-cli` 不在 PATH 中，需用完整路径 `C:\Users\<user>\AppData\Roaming\npm\lark-cli.cmd`
- **`lark-cli schema` 不支持 `docx` 服务**（只支持 drive/im/calendar 等）
- **`lark-cli api` raw API 调用**：GET 可读 docx blocks，但写操作全部返回 404

## 与 Gateway 的区别

| | Gateway (IM) | lark-cli docs |
|------|------|------|
| 产出 | 群聊消息 | 飞书文档 |
| 格式 | post (Markdown 子集) | 完整 Docx |
| 身份 | bot | user |
| 场景 | 即时回复 | 知识发布 |
