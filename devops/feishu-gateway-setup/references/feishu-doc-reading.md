# 飞书文档读取/导出

当需要查看飞书文档内容时（如用户提到"看我的飞书文档"），用 `lark-cli drive` 命令读取，
**不要**试图用浏览器打开（需要登录且 CDP 环境无法完成认证）。

## 步骤 1 — 检查文档信息

```bash
lark-cli drive +inspect --url "https://my.feishu.cn/docx/DOC_TOKEN"
```

返回文档类型、标题、token：
```json
{
  "ok": true,
  "data": {
    "title": "AI创作笔记",
    "token": "HerSdSRijoa49nxhVefcSBMHnWe",
    "type": "docx"
  }
}
```

## 步骤 2 — 导出为 Markdown

```bash
lark-cli drive +export \
  --token DOC_TOKEN \
  --doc-type docx \
  --file-extension markdown \
  --output-dir . \
  --overwrite
```

### 关键限制

- `--output-dir` **必须是相对路径**（`lark-cli` 安全检查禁止绝对路径）
- 先 `cd` 到目标目录，再用 `.` 作为相对路径
- 文件自动命名为 `<文档标题>.md`

### 支持的导出格式

| `--doc-type` | `--file-extension` |
|---|---|
| docx | markdown, docx, pdf |
| sheet | xlsx, csv |
| bitable | csv, base |
| slides | pptx |

## 完整示例

```bash
# 1. 获取文档信息
lark-cli drive +inspect --url "https://my.feishu.cn/docx/HerSdSRijoa49nxhVefcSBMHnWe"

# 2. 导出到临时目录
mkdir -p /tmp/feishu-export
cd /tmp/feishu-export
lark-cli drive +export \
  --token HerSdSRijoa49nxhVefcSBMHnWe \
  --doc-type docx \
  --file-extension markdown \
  --output-dir . \
  --overwrite

# 3. 用 read_file 读取本地 .md 文件
```

## 注意事项

- 使用 `--as user`（用户身份）导出个人文档，bot 身份可能无权限
- 导出的 Markdown 中，飞书特有元素（如 bookmark、折叠块）会丢失或退化为纯文本
- 文档中的图片会保留为飞书内链 URL，不会下载到本地
