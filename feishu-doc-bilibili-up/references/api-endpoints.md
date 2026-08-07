# Feishu Docx API 端点参考

## 读取 blocks

```bash
GET /open-apis/docx/v1/documents/{document_id}/blocks?page_size=500
```

返回 `data.items[]`，每个 item 含 `block_id`、`block_type`、文本内容和 `parent_id`。根 block 的 `children[]` 列出子 block 的 `block_id` 顺序。

**block_type 映射**：
| type | 含义 | 文本所在 key |
|------|------|-------------|
| 2 | 正文 | `text` |
| 3 | H1 | `heading1` |
| 4 | H2 | `heading2` |
| 12 | 无序列表 | `bullet` |

**文本元素结构示例**：
```json
{
  "block_id": "Skwudp5Pvo0K73x9QvZcogTonRN",
  "block_type": 12,
  "bullet": {
    "elements": [{
      "text_run": {
        "content": "电影细胞",
        "text_element_style": {
          "link": {"url": "https://space.bilibili.com/431169809"}
        }
      }
    }],
    "style": {}
  },
  "parent_id": "HerSdSRijoa49nxhVefcSBMHnWe"
}
```

## 更新 block 文本（PATCH）

```bash
PATCH /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}?document_revision_id=-1
```

Body：
```json
{
  "update_text_elements": {
    "elements": [
      {
        "text_run": {
          "content": "显示文本",
          "text_element_style": {
            "link": {"url": "https://example.com"}
          }
        }
      },
      {
        "text_run": {
          "content": "  — 描述文本"
        }
      }
    ]
  }
}
```

- 多个 `text_run` 会在同一行拼接
- 第一个元素设 `link` 做超链接
- 不能改 block_type——要换类型只能 POST 新建

## 创建子 block（POST）

```bash
POST /open-apis/docx/v1/documents/{document_id}/blocks/{parent_id}/children?document_revision_id=-1
```

Body（创建 H2）：
```json
{
  "children": [{
    "block_type": 4,
    "heading2": {
      "elements": [{"text_run": {"content": "分类标题"}}],
      "style": {}
    }
  }],
  "index": 7
}
```

Body（创建 bullet）：
```json
{
  "children": [{
    "block_type": 12,
    "bullet": {
      "elements": [
        {"text_run": {
          "content": "UP名",
          "text_element_style": {"link": {"url": "https://..."}}
        }},
        {"text_run": {"content": "  — 描述"}}
      ],
      "style": {}
    }
  }],
  "index": 8
}
```

- `index`：插入位置（0-based），创建后原 index 的 block 后移
- 多次插入同一 index 时，从底部向上（先插最后的），保持 index 稳定
- 创建后必须重新 GET blocks 刷新 block_id 列表

## 注意事项

- **所有写操作 URL 必须带 `?document_revision_id=-1`**，否则 404
- 单文档每秒 3 次编辑，建议 `sleep(0.3)` 保安全
- lark-cli 错误输出到 stderr，不要只看 stdout
- DELETE block 不支持（始终 404）
- PATCH 只能改文本，不能改 block type
