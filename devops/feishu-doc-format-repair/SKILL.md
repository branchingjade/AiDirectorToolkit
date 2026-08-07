---
name: feishu-doc-format-repair
description: 修复飞书文档段落格式，内容零改动。触发词：修复段落格式、统一格式。
---

# 飞书文档批量格式修复

## 适用场景

用户要求"修复/统一飞书文档的段落格式"、"内容一定不要改"时。典型：从其他工具导入的文档（短剧剧本、小说、会议纪要）格式混乱——同一类内容（集数标题、案件标题、场次标题、人物行）混用了标题块 / 加粗段落 / 普通段落+空格伪居中等多种格式，甚至正文被误标成标题。

## 核心原则

1. **只改格式，内容零改动**——用纯文本逐字符对比验证（见工作流第5步）
2. **同类内容统一为同一种格式**——先盘点现状，再定统一目标（如：案件=h2居中、集数=h3居中、场次=加粗段落、人物行=加粗段落）
3. **局部编辑优先**：用 `block_replace` 逐个改，**绝不用 `overwrite` 全文重写**（会丢图片/评论/嵌入资源）

## 工作流

### 1. 拉取全文并存档基线

```bash
lark-cli docs +fetch --doc "<URL>" --detail with-ids --format json > baseline.json
```

**基线必须保存**——第5步的内容零改动验证要用它对比。注意：同一文档多次 fetch 时 block ID 会变（block_replace 后旧 ID 失效），所以基线 = 最早那份原始 XML。

### 2. 生成修复清单（Python 解析 XML）

- 用正则枚举每种内容的**全部格式变体**（见陷阱2），输出 `(block_id, old_preview, new_xml)` 清单
- 同 block_id 去重（后者覆盖前者）
- 清单存 JSON，供执行和复核

### 3. 执行（bash 循环，Windows 必读）

Windows 下 Python subprocess 可能找不到 lark-cli（PATH/包装脚本解析问题，报 WinError 2）——**改用 bash 脚本循环执行**：

```bash
DOC="<URL>"
out=$(LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1 \
  lark-cli docs +update --doc "$DOC" --command block_replace \
  --block-id "$ID" --content '<新内容>' --format json 2>&1)
```

成功判定：`ok==true` 且 `data.document.result != "failed"`。每个操作之间 sleep 0.3 防限流。

### 4. 重新 fetch + 健壮验证

重新 `docs +fetch --detail with-ids`，用**嵌套安全正则**扫描（见 scripts/verify_format.py），不能靠肉眼。

### 5. 内容零改动验证

- 修复前 XML 基线 vs 修复后 XML：剥离所有标签 + 空白后逐字符对比，必须完全一致
- **不要用 markdown 导出做对比基准**——ol/li 列表序号在 markdown 渲染成"1."、在 XML 纯文本里不存在，会产生大量假差异（本会话曾因此误报 263 处差异，换 XML 基准后 0 差异）

## 关键陷阱

1. **block_replace 后旧 block ID 失效**（见 lark-doc skill 的 Block ID 生命周期）——批量操作清单必须基于**最新一次** fetch 生成；每轮执行后重新 fetch 再生成下一轮。同一 block 只能 replace 一次；重复 replace 同一 ID 报 `degrade_code=1011 no document changes`（不是失败，是内容已一致）。

2. **格式变体防不胜防**：同一类内容（如"第X集"）至少见过 5 种变体：①普通段+前导空格伪居中 ②`<b>空格</b>+文本` ③整段 `<b>` 包裹 ④已是 h2/h3/h4 但层级错 ⑤ol/li 列表。枚举正则必须全部覆盖，否则漏网——生成清单后打印"非集数标题的修复"和覆盖范围（如 1-50 集是否齐全）复核。

3. **验证正则必须嵌套安全**：`<h4>[^<]*</h4>` 匹配不到 `<h4><b>人物</b>：xxx</h4>`（内容含嵌套标签）→ 漏检、误报"全绿"。必须用 `<h[1-4][^>]*>(.*?)</h[1-4]>` + re.S 再剥离内层标签取文本。**首轮自检曾因这个坑误报全绿，用户要求复查后才发现 2 处残留**（h2 场次标题、h4 人物行各 1）。

4. **"人物：xxx"行**：全篇标准是 `<p><b>人物：xxx</b></p>` 整行加粗；误标为 `<h4><b>人物</b>：xxx</h4>` 的变体要归并成标准格式。

5. **伪居中空格**：`<p>  第2集</p>` 这类前导空格是伪居中——标题块删空格改用 `align="center"` 属性，正文段直接删前导空格。

6. **纯空格空段** `<p>      </p>` 是格式垃圾，清空为 `<p></p>`（不算动内容）。

7. **结构完整性自检**：修复后检查标题层级计数（h2=案件数、h3=集数且序号连续 1-N、h4=0）、剧情锚点文本顺序、文档首尾完整。

## 参考

- lark-doc skill：`docs +fetch` / `+update` 语法、Block ID 生命周期、str_replace 行内匹配限制
- scripts/verify_format.py：嵌套安全的格式验证脚本
