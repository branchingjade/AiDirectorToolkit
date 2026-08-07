---
name: feishu-doc-batch-format
version: 1.0.0
description: "飞书文档批量格式修复，只改格式不改内容。触发词：修复段落格式、格式统一、只改格式不改内容。"
---

# 飞书文档批量格式修复

用户要求"修复段落格式 / 统一格式 / 只改格式一定不改内容"时使用。命令语法看 lark-doc 技能（本技能只讲批量流程与内容保护）。

## 核心原则

1. **内容零改动是硬指标**：做完必须用纯文本对比验证，不能只靠肉眼检查。
2. **格式归一化目标**：同一内容类型（案件标题/集数标题/场次标题/人物行）必须用同一种标签与层级，全篇一致。以文档中**已占多数的格式**为准，把少数派改过去。
3. 层级惯例：章节标题 `h2` 居中 → 集数标题 `h3` 居中 → 场次/人物行 加粗段落 `<p><b>`。误标成标题的正文行（`<h4>▲...`、`<h4>人物：...</h4>`）恢复为段落。

## 工作流

### 1. 拉取全文 XML（带 block ID）

```bash
lark-cli docs +fetch --doc "<URL>" --detail with-ids --format json > doc_before.json
```

`with-ids` 必须，后续 block_replace 需要 block_id。

### 2. 诊断格式不一致

用 Python 正则扫描 XML，列出同一内容类型的所有现状：
- 标题：哪些在 `<h2>/<h3>/<h4>`，哪些是普通 `<p>` 加前导空格伪居中
- 场次标题（`X-X 日/夜/昏 内/外 ...`）：加粗段落 vs h4 vs h2 混用
- 正文行被误标成标题（`<h4>▲...` 动作行、`<h4>人物：...</h4>`）
- 集数标题的特殊变体：`<p><b>空格</b>第X集</p>`、`<p><b>第X集</b></p>` 都要单独写正则
- 前导空格、纯空格空段 `<p>   </p>`

### 3. 生成修复清单（block_id → 新 XML）

写 Python 脚本，用正则从 XML 提取目标块文本，**只剥离空白、不改任何文字**，重建为统一标签。输出 JSON 清单 `[{block_id, old, new}]`。**同一 block 只能 block_replace 一次 → 按 block_id 去重**。

### 4. 批量执行：生成 bash 循环脚本

**Windows 上 lark-cli 在 Python subprocess 里会报 WinError 2**（它是 shell 命令/alias，Python 找不到）——生成 `.sh` 用 bash 执行，逐条调用并解析 JSON 判断成功：

```bash
out=$(LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1 \
  lark-cli docs +update --doc "$DOC" --command block_replace \
  --block-id "$BID" --content '<新XML>' --format json 2>&1)
echo "$out" | python -c "import json,sys; d=json.load(sys.stdin); ok=d.get('ok') and d.get('data',{}).get('document',{}).get('result')!='failed'; print('OK' if ok else 'FAIL')"
```

**成功判定**：只看 `ok:true` 不够——必须同时检查 `data.document.result != "failed"`。重复替换已改过的块会返回 `ok:true` 但 `result:"failed"`（warning: no document changes）。

### 5. 迭代：重新 fetch → 重新生成清单

`block_replace` 后**被替换块的旧 ID 失效**（skill 文档明示）。所以：
1. 执行完一轮 → 重新 `+fetch --detail with-ids`
2. 用最新 XML 重新跑诊断脚本 → 已完成的块不再匹配、自动跳过，得到"剩余清单"
3. 循环执行直到剩余清单为空

### 6. 验证内容零改动（必须）

对比**最初 fetch 的 XML 纯文本** vs **最终 fetch 的 XML 纯文本**：

```python
def pure(x):
    x = re.sub(r'<[^>]+>', '', x)
    return re.sub(r'\s+', '', x)
assert pure(before) == pure(after)
```

用本技能自带 `scripts/verify_content_unchanged.py`。

**⚠️ 禁止用 markdown 导出做对比基准**：markdown 会把 ol 列表序号（`1.` `2.`）渲染进文本，XML 纯文本里没有，导致成百上千个假差异（实测 263 个）。markdown 的 `\~` 转义也会造成假差异。

## 陷阱清单

| 陷阱 | 正确做法 |
|---|---|
| 用 markdown 导出当内容对比基准 | 用修复前后 `with-ids` XML 的纯文本对比 |
| 只看 `ok:true` 判断写入成功 | 同时检查 `data.document.result != "failed"` |
| Python subprocess 调 lark-cli | 生成 bash `.sh` 脚本循环执行 |
| 不重新 fetch 就复用旧 block_id | 每轮后重新 fetch，重新生成清单 |
| 把纯空格空段 `<p>   </p>` 当内容删掉 | 清空为 `<p></p>`（保留块，只去空格） |
| 顺手修错别字/标点/空格 | "不改内容"= 文字一个字符都不能动，只动标签与空白 |
| 验证正则用 `[^<]` 匹配标题内容 | 嵌套标签标题（`<h4><b>人物</b>：XXX</h4>`、`<h2><b>11-3 …</b></h2>`）匹配不到 → "0 残留"误报。必须用 `<(h[1-4])([^>]*)>(.*?)</\1>` + `re.S`，去标签后比对文本（实测第一轮验证"全绿"实有 2 处嵌套残留） |

## 验证清单

- [ ] 各层级标题数量与预期一致（如 5 个案件 h2 + 50 个集数 h3）
- [ ] **嵌套正则扫描标题块**：`<(h[1-4])([^>]*)>(.*?)</\1>` + `re.S`，去标签后核对——h2 全是章节标题、h3 全是集数、无残留 h4 场次/人物行
- [ ] 场次标题全部为加粗段落，无残留 `<h4>`/`<h2>` 场次
- [ ] "人物"行全部为加粗段落，无标题化残留
- [ ] 前导空格段落、纯空格空段为 0
- [ ] 纯文本完全一致（`scripts/verify_content_unchanged.py` 通过）
