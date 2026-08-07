---
name: lark-doc-batch-format
version: 1.0.0
description: "修复飞书文档段落/标题格式，内容零改动。触发词：修复格式、格式统一、排版。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 飞书文档批量格式修复（内容零改动）

## 适用场景

用户给出飞书文档并要求「修复段落格式 / 统一格式 / 整理排版」，且强调**不要修改内容**。典型：剧本、长文档中同一类型内容（章节标题、集数标题、场次标题、人物行）格式五花八门——有的是标题层级、有的是普通段落+空格伪居中、有的是 ol 列表，甚至正文被误标成标题。

## 铁律

1. **内容零改动**：所有操作只换标签/属性，文字一字不动。交付前必须做纯文本对比验证（见第5步与 scripts）。
2. **不用 `overwrite`**：批量格式修复走 `block_replace` 逐块替换，绝不整篇覆盖（会丢图片、画板、评论等资源块）。
3. **批处理后必须重新 fetch**：`block_replace` 会让被改块的旧 ID 失效（生成新 ID）。继续 block 级操作前重新 fetch 拿最新 ID；每批跑完基于最新 XML 重新生成剩余 ops。

## 工作流

### 第1步：拉取 XML 存档（修复前基线）

```bash
lark-cli docs +fetch --doc "<URL>" --detail with-ids --format json > before.json
```

把 `data.document.content` 存为 `before.xml`——这是后面内容对比的**唯一正确基准**（不是 markdown 导出）。

### 第2步：盘点格式问题，生成 ops 清单

- 用正则扫描 XML，分类统计：标题块（h1-h4）、加粗段落、带前导空格段落、纯空格空段、ol/li 列表。
- 输出 ops JSON：`[{block_id, old, new_xml}]`。**每个 block 只操作一次**（同一 block 只能 replace 一次）。

### 第3步：批处理执行（Windows 用 bash 脚本）

- **坑（Windows）**：Python `subprocess.run(["lark-cli", ...])` 报 `[WinError 2]`——lark-cli 是 .cmd shim，Python 找不到。**正确姿势：生成 bash 脚本**逐条执行，每条用 python 解析 JSON 判断 `ok==true` 且 `result!='failed'`。
- 单条命令：

```bash
LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1 \
  lark-cli docs +update --doc "$DOC" --command block_replace \
  --block-id "<block_id>" --content '<h3 align="center">第2集</h3>' --format json
```

### 第4步：迭代收敛

- 每批跑完后**重新 fetch**，基于最新 XML 重新生成剩余 ops（已改完的块正则不再命中，自动跳过）。
- **`degrade_code=1011 "Instruction produced no document changes"` 不是错误**——是重复执行了已完成的 op（block 内容已等于目标内容），说明该块已改好，跳过即可，不要当作失败重试死磕。

### 第5步：验证（健壮正则 + 纯文本对比）

- **标题扫描必须处理嵌套标签**：先 `re.sub(r'<[^>]+>','',inner)` 再匹配文本。**不要用 `[^<]` 字符类匹配标题内容**——`<h2><b>11-3 夜内 …</b></h2>`、`<h4><b>人物</b>：…</h4>` 这类内嵌 `<b>` 的块会被 `[^<]` 漏检，导致「0 残留」假阳性、漏掉真问题。
- **验证必须用更严格的正则交叉检查，不能用生成清单时的同一套正则**：用有缺陷的正则生成清单 → 同一套正则验证 → 会自我确认假阳性（实测：第一轮验证报「全绿」，换健壮正则 `<(h[1-4])[^>]*>(.*?)</\1>` + re.S + 剥标签后才发现 2 处漏网）。生成正则求「能命中目标」，验证正则求「一个都不漏」——两者标准不同，必须分开写。
- **内容对比基准必须用修复前 XML**（`before.xml`），不是 markdown 导出——markdown 会渲染 ol 列表序号（如「1. 昏外 乡间小路」的「1.」），XML 纯文本里没有，逐字符对比会出现几百个假差异。
- 对比方法：两侧 XML 都 strip 掉所有标签 + 所有空白后逐字符比较，完全一致 = 内容零改动。
- 验证脚本：`scripts/verify_content_same.py before.xml after.xml`（最终裁决）。

## 常见格式问题清单（本类任务高发项）

| 问题 | 修复 |
|---|---|
| 集数/章节标题：普通段落+一堆空格伪居中（`<p>    第2集</p>`） | 删空格，改 `<h3 align="center">` |
| 同类标题层级混用（同是「第X集」，h2/h3/h4/段落都有） | 统一为同一层级（集数 h3、案件 h2 之类，按文档语义定） |
| 案件/大章节标题：缩进加粗段、伪居中段、h4 混用 | 统一 h2 居中 |
| 场次标题：少数被误标成 h2/h4/ol 列表，其余是加粗段落 | 以多数格式为准，统一为加粗段落 |
| 正文被误标成标题（`▲…` 动作行、`人物：…` 行变成 h4） | 降回普通段落 / 加粗人物行 |
| 正文段落前导空格、纯空格空段 `<p>     </p>` | 删除空格 / 清空为 `<p></p>` |

## 内容一致性补充检查

- 关键锚点序列：抽出全文纯文本，按顺序查找开头标题、各章节名、结尾标志（如「【第一季完】」）、关键伏笔台词——顺序正确且都在 = 内容未乱序未丢失。
- 结构完整性抽查：每章应有场次+人物+台词骨架；个别章缺某类行时先核对原文（可能是原文就没有，不是修复引入）。

## 参考

- 基础命令（`docs +fetch` / `+update` / block ID 生命周期）见 `lark-doc` skill。
- 本 skill 的 `scripts/verify_content_same.py` 是内容零改动的最终裁决。
