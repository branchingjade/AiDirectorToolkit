# 从本地 Markdown 创建结构化飞书文档（大纲/剧本/方案）

> 适用：用户已有本地 .md（Obsidian 笔记、大纲、剧本），要转成结构化飞书文档并做富功能优化。
> 前置：读 `lark-doc-md.md` / `lark-doc-xml.md` 语法基础；权限问题走 `lark-shared`。

## 流程

### 1. 转换：md → XML

```bash
python3 scripts/md2xml.py input.md -o output.xml
```

支持：标题 h1-h6、表格（含表头）、列表、引用块、代码块、加粗、行内代码。frontmatter 自动跳过。

### 2. 创建

```bash
lark-cli --as bot docs +create --content @output.xml --format json
```

- `--as user` 创建的文档归属用户；`--as bot` 归属应用（需要完整权限链，见 lark-shared）
- **坑：`<title>` 标签不生效**——XML 里的 `<title>` 不会被识别为文档标题，创建后文档显示 "Untitled"。必须补一步改名：

```bash
lark-cli drive files patch --params '{"file_token":"<DOC_TOKEN>","type":"docx"}' --data '{"new_title":"正式标题"}'
```

### 3. 富功能优化（大纲/剧本类文档推荐套路）

创建后按内容类型加分：

| 内容 | 推荐功能 | 说明 |
|------|---------|------|
| 一句话故事/核心冲突 | `<callout emoji="🎬">` 高亮块 | 插在核心设定标题后，打开文档第一眼看到全片的魂 |
| 时间线/节奏 | `<whiteboard type="mermaid">` 时间轴 | 三幕结构、逐段节点、关键台词挂轴上 |
| 分集/分场 | 表格 | 已有表格转换后直接可用 |

**Mermaid 时间轴示例**（timeline 语法）：

```xml
<whiteboard type="mermaid">
timeline
    title 75分钟 · 三幕时间轴
    section 第一幕 0-15min
        0-8min : 开场打戏
               : 角色引入
    section 第二幕 15-55min
        15-22min : 主线推进
</whiteboard>
```

插入位置：`docs +update --command block_insert_after --block-id <目标标题block> --content @timeline.xml`
（block id 从 `docs +fetch --detail with-ids` 获取）

**验证渲染**：`lark-cli whiteboard +export --whiteboard-token <board_token> --output-type preview --output preview.jpg`（注意返回的扩展名可能是 .jpg，输出路径要匹配）

### 4. 自检清单

创建/更新后验证：

- [ ] `docs +fetch` 拉全文，确认标题层级（h1/h2/h3 数量）、表格数、关键内容锚点
- [ ] **block 级写操作（block_replace/insert）后必须 fetch 验证实际内容**——返回 `result: failed` 不代表没生效（旧 block ID 失效会误报），看 fetch 结果
- [ ] callout/whiteboard 是否在位（fetch 里搜 `<callout`/`<whiteboard`）
- [ ] 自检正则用 `<(h[1-4])[^>]*>(.*?)</\1>` + re.S 容错嵌套标签，禁止 `[^<]`（嵌套 `<b>` 会漏检）

## 踩过的坑

1. **`<title>` 标签不生效** → 创建后 `drive files patch` 改名（见上）
2. **block_replace 返回 failed 但已生效** → 判断成功必须 fetch 验证，重复修改先重新 fetch 拿新 block ID
3. **bot 创建需完整权限**（`docx:document` + `docs:permission.member:create` + drive 系列）→ 见 `lark-shared`
4. **read_file 对中文 UTF-8 文件误判二进制** → 用 python 读，或 terminal cat
