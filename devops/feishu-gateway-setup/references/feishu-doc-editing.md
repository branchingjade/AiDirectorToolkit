# 飞书文档编辑（Block 级别 API）

当需要**修改**飞书文档内容（而非仅读取/导出），使用 `lark-cli api` 直接调 Block API。

## docs +update 命令层（比裸 API 更省事，但有静默陷阱）

`lark-cli docs +update` 是高级命令封装（str_replace / block_replace / block_insert_after / block_delete），**推荐优先用这个**——不用手写 JSON。但有一个必须知道的陷阱：

### 🔴 str_replace 跨 block 静默失败（2026-08-06 实测）

**现象**：`docs +update --command str_replace --pattern X --content Y` 返回 `"ok": true`，但 fetch 后内容**根本没变**——不报错、不提示。

**根因**：XML 模式下 `--pattern` **只支持行内匹配，不能跨 block**。目标文本横跨多个 block（如 `<h2>` 标题+正文、表格单元格+表外文本）时匹配不到，CLI 静默返回 ok。

**铁律**：str_replace 后必须 `docs +fetch` 验证，不能信任返回的 `"ok": true`。

**正确姿势（block 级操作）**：
```bash
# 1. 拿目标 block ID（keyword scope + with-ids；注意 keyword 是独立 flag 不是 --params）
lark-cli docs +fetch --doc <token> --scope keyword --keyword "关键词" --detail with-ids --format json
#    → 输出含 <h2 id="doxcnXXXX"> 等 block ID

# 2. block_replace 替换整个 block
lark-cli docs +update --doc <token> --command block_replace --block-id doxcnXXXX --content @new.xml

# 3. block_insert_after 在指定 block 后插入（插入后重新 fetch 拿新 ID 才能再操作新块）
lark-cli docs +update --doc <token> --command block_insert_after --block-id doxcnXXXX --content @para.xml
```

**block ID 生命周期**：`block_replace`/`block_delete` 后旧 ID 失效，继续 block 操作前必须重新 fetch；`block_insert_after` 后新内容是新 ID。

### 其他陷阱

1. **str_replace 用于表格单元格**：往 `<td>` 插长段落会破坏表格结构——单元格内容保持短句，长内容用 `block_insert_after` 插到表格外
2. **别用 `<h2>` 包裹正文**：主题落点等内容塞进 h2 会让整段变成标题（原标题被"吃掉"）。h2 只放标题，正文用 `<p>`
3. **跨 block 修复序列**（实测）：h2 混入正文后 → ① block_replace 把 h2 恢复纯标题 → ② 重新 fetch 拿新 ID → ③ block_insert_after 插正文 → ④ `--doc-format markdown` fetch 验证渲染（比 XML 直观）
4. **完整参数参考**：`lark-cli skills read lark-doc references/lark-doc-update.md`（CLI 内置版本匹配文档，比外部 skill 副本可靠）

## 🔴 关键前置条件：document_revision_id

**所有写操作（PATCH/POST/DELETE）必须带 `?document_revision_id=-1` 参数，否则返回 HTTP 404。**

```bash
# ✅ 正确
lark-cli api PATCH "/open-apis/docx/v1/documents/{token}/blocks/{block_id}?document_revision_id=-1" --data '{...}'

# ❌ 错误（404）
lark-cli api PATCH "/open-apis/docx/v1/documents/{token}/blocks/{block_id}" --data '{...}'
```

GET 读操作不需要此参数。

## 核心概念

飞书文档内部是 block 树：根 block（`document_id`）→ children（按顺序排列的 block）→ 递归嵌套。

### Block 类型

| block_type | 含义 | 内容字段 |
|---|---|---|
| 1 | 页面（根） | `children` 数组 |
| 2 | 文本段落 | `text.elements[].text_run.content` |
| 3 | 一级标题 | `heading1.elements[].text_run.content` |
| 4 | 二级标题 | `heading2.elements[].text_run.content` |
| 12 | 无序列表项 | `bullet.elements[].text_run.content` |

### 链接

链接在 `text_element_style.link.url` 中，**URL 编码**（`https://` → `https%3A%2F%2F`）。创建块时传入原始 URL 即可（API 自动编码）。

## 获取文档结构

```bash
lark-cli api GET "/open-apis/docx/v1/documents/{token}/blocks?page_size=500"
```

解析流程：
1. 找到根 block（`block_type=1`）的 `children` 数组 → 获得子块 ID 及顺序
2. 遍历 items 查找目标块 → 根据 `block_type` 确定内容字段
3. 提取文本时需切换 key：`heading1`/`heading2`/`bullet`/`text`

## 更新块内容（推荐：原地修改文本）

```bash
lark-cli api PATCH "/open-apis/docx/v1/documents/{token}/blocks/{block_id}?document_revision_id=-1" \
  --data '{"update_text_elements":{"elements":[{"text_run":{"content":"新内容"}}]}}'
```

- 只改变文本，不改变 block 类型
- 可同时更新多个 `text_run` 元素（如链接 + 描述文字）
- 如果原块有链接，需在 `text_element_style.link.url` 中重新指定（否则链接丢失）

### 更新带链接的列表项

```json
{
  "update_text_elements": {
    "elements": [
      {"text_run": {"content": "名称", "text_element_style": {"link": {"url": "https://..."}}}},
      {"text_run": {"content": "  — 描述"}}
    ]
  }
}
```

## 删除块

```bash
lark-cli api DELETE "/open-apis/docx/v1/documents/{token}/blocks/{block_id}?document_revision_id=-1"
```

⚠️ **个人文档（my.feishu.cn）可能不支持 DELETE**。如遇 404 即使用 `document_revision_id=-1`，改用 PATCH 清空块内容 + 创建新块替代。

## 创建块

```bash
lark-cli api POST "/open-apis/docx/v1/documents/{token}/blocks/{parent_id}/children?document_revision_id=-1" \
  --data '{"children": [{...}], "index": 7}'
```

- `index`：0-based 插入位置，相对于 parent 的 children 数组
- 每次插入后后续块的索引自动 +1

### 创建二级标题

```json
{
  "block_type": 4,
  "heading2": {
    "elements": [{"text_run": {"content": "🎬 导演创作"}}],
    "style": {}
  }
}
```

### 创建带链接的列表项

```json
{
  "block_type": 12,
  "bullet": {
    "elements": [
      {"text_run": {
        "content": "UP名称",
        "text_element_style": {"link": {"url": "https://space.bilibili.com/xxx"}}
      }},
      {"text_run": {"content": "  — 描述文字"}}
    ],
    "style": {}
  }
}
```

## 批量插入策略

向一个段落后插入多个块时，索引会不断变化。安全策略：

1. **插入单一块**：指定目标 index
2. **从下往上插入多个块**：用 `reversed()` 顺序，始终 insert at 同一个 index（后续块自然下移）
3. **大规模替换**：优先 PATCH 现有块（不改变结构），仅对新类别标题用 POST 创建

示例：在 index=7 处插入 6 个标题（从下往上）

```python
for title in reversed(headings):
    lark("POST", f"/docx/v1/documents/{doc}/blocks/{doc}/children",
         {"children": [heading_block], "index": 7})
# 结果：6 个标题依次排在 index 7-12
```

## Python 调用 lark-cli（稳定模式）

**用 subprocess list 传参**（不用 `shell=True` + `shlex.quote`，避免 JSON 转义问题）：

```python
import subprocess, json

LARK = r"C:\Users\HMSJ\AppData\Roaming\npm\lark-cli.cmd"

def lark(method, path, body=None):
    """path 需包含 ?document_revision_id=-1"""
    args = [LARK, "api", method, path]
    if body:
        args.extend(["--data", json.dumps(body, ensure_ascii=False)])
    r = subprocess.run(args, capture_output=True, text=True, timeout=20)

    # lark-cli 成功时输出到 stdout，失败时输出到 stderr
    out = r.stdout.strip()
    err = r.stderr.strip()
    if not out and err:
        try: return json.loads(err)
        except: pass
    if not out:
        return {"ok": True}  # DELETE 返回空体
    try: return json.loads(out)
    except: return {"ok": False, "error": f"parse: {out[:100]}"}
```

- **Windows 陷阱**：`subprocess.run(["lark-cli", ...])` 找不到文件 → 必须用绝对路径 + `.cmd` 扩展名
- **错误输出到 stderr**：lark-cli 的 `ok: false` 响应输出到 stderr 而非 stdout
- **`--as user`**：API 调用自动使用 `lark-cli config bind` 绑定的身份；如未指定则默认 user

## 典型工作流：批量替换文档段落

1. `GET /blocks?...` → 获取全文档结构
2. 定位目标段落：找到根 block children 中对应 index 范围
3. **PATCH 现有块**（改文本，不变结构）：适合内容替换
4. **POST 新块**（创建标题/分隔）：适合插入新结构
5. **DELETE 旧块**（如有需要）：个人文档可能不支持，用 PATCH 清空替代

## 限制

- 单次 API 调用只能操作一个 block（无批量操作）
- 个人文档（my.feishu.cn）DELETE 可能返回 404
- 不能通过 PATCH 改变 block_type（无法把 bullet 变成 heading）
- 写操作频率限制：单篇文档每秒 3 次并发编辑
