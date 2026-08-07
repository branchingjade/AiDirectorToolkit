# lark-cli 文档编辑陷阱（2026-08-06 实测）

## 核心陷阱：str_replace 跨 block 静默失败

**现象**：`docs +update --command str_replace --pattern X --content Y` 返回 `"ok": true`，但 fetch 后内容**根本没变**——不报错、不提示，静默失败。

**根因**：XML 模式下 `--pattern` **只支持行内匹配，不能跨 block**。当目标文本横跨多个 block（如 `<h2>` 标题 + 段落内容、表格单元格 + 表外文本）时，pattern 匹配不到，但 CLI 不报错。

**判定方法**：str_replace 后必须 `docs +fetch` 验证，不能信任返回的 `"ok": true`。

**正确姿势（block 级操作）**：
```bash
# 1. 拿到目标 block ID（keyword scope + with-ids）
lark-cli docs +fetch --doc <token> --scope keyword --keyword "关键词" --detail with-ids --format json
#    → 输出含 <h2 id="doxcnXXXX"> 这样的 block ID

# 2. 用 block_replace 替换该 block
lark-cli docs +update --doc <token> --command block_replace --block-id doxcnXXXX --content @new.xml

# 3. 用 block_insert_after 在指定 block 后插入新内容（需要新 block ID，重新 fetch）
lark-cli docs +update --doc <token> --command block_insert_after --block-id doxcnXXXX --content @para.xml
```

**注意**：`block_replace`/`block_delete` 后旧 ID 失效，继续 block 操作前必须重新 fetch。

## 其他陷阱

1. **`--content ""` 删除 = 删全部匹配，不是第一个**（2026-08-06 实测翻车）：`str_replace --content ""` 会把 `--pattern` 在文中出现的**所有**位置都删掉。镜妖"她的苦"条目在文档里重复出现 2 次（之前 str_replace 拼接导致），想删重复处时 `--content ""` 把两处全删，内容一度丢光。**删除前先 `docs +fetch --scope keyword --keyword <片段>` 数出现次数**；出现 >1 次时用 `block_delete --block-id` 精确定位，不要用 str_replace 空 content 删
2. **str_replace 用在表格单元格里**：往 `<td>` 单元格插入长段落会破坏表格结构——单元格内容应保持短句，长内容用 block_insert_after 插到表格外
3. **不要用 `<h2>` 包裹正文内容**：主题落点等内容塞进 h2 会让整个段落变成标题（"信息差设计"标题被吃掉）。h2 只放标题，正文用 `<p>`
4. **跨 block 的修复序列**（本会话踩坑实例）：h2 内容混入正文后，正确修复 = ① block_replace 把 h2 恢复纯标题 → ② 重新 fetch 拿新 ID → ③ block_insert_after 插入正文段落 → ④ markdown 格式 fetch 验证渲染（`--doc-format markdown` 比 XML 直观）
5. **fetch 的 keyword scope** 是独立 flag 不是 `--params`：`--scope keyword --keyword "词"`（不是 `--params '{"keyword":...}'`，后者 KeyError）
6. **完整参数参考**：`lark-cli skills read lark-doc references/lark-doc-update.md`（CLI 内置版本匹配的文档，比外部 skill 副本可靠）
7. **block 内容丢失后的恢复**：万一内容被误删（如 `--content ""` 全删），用 `docs +fetch --scope keyword --keyword <残存片段> --detail with-ids` 拿幸存 block ID → `block_replace --block-id` 恢复完整内容。恢复后 fetch 验证各关键词出现次数=1
