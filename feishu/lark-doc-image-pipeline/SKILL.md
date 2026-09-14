---
name: lark-doc-image-pipeline
description: "飞书 doc 批量配图。Use when 给飞书 doc 表格或条目批量加参考图。"
version: 1.0.0
tags: [feishu, lark, docx, image, pipeline, batch, 配图]
license: MIT
---

# 飞书 Doc 批量配图工作流

> **来源**：2026-09-03 中国古剑器物档案配图实战（5/6 张图，1 章节完成）。
> **场景**：飞书云文档里有大量表格条目需要给每条配参考图（博物馆藏品 / 维基百科 / 百度百科 / 影视资料站）。

## 硬限制（必读）

**`lark-cli docs +media-insert` 不能把图插入到 table cell 内**——CLI 文档原文：
> "Media is inserted at the top-level ancestor of the matched block — i.e., when the selection is inside a callout, **table cell**, or nested list, **media lands outside that container, not inside it**."

**唯一可行的配图方案**：在表格 block **之后**（外层）追加图片 block，配 caption 标器物本名 + 出处。原表格不动，图片作为独立段落紧跟表格。

## 完整工具链（按调用顺序）

### 步骤 1: 抓图（外部工具，不在 lark-cli 范围）

**优先级**：
1. **博物馆官网直链**（最稳）：故宫 DPM（`https://img.dpm.org.cn/Uploads/Picture/dc/<id>[1024].jpg`）、国博 chnmuseum（`https://www.chnmuseum.cn/zp/zpml/<cat>/<YYYY>/P<id>.jpg`）。盲扫 ID 不连续，命中率约 30%。
2. **维基百科中文版**：commons.wikimedia.org 搜 "Sword of Goujian" 等具体器物
3. **百度百科**：词条里有文物图，但反爬严，curl 直连常返空
4. **DDG web_search 兜底**：ddgs 包要装，没装用浏览器走 SPA

**curl 坑**：故宫 DPM URL 含 `[1024]`，curl 必须 `-g` 关 globbing，否则 `bad range in URL`。

**下载到本地**（必须相对路径后续用）：`_sword_imgs/<章节>/<器物本名>.jpg`，单张 ≤ 500KB，长边 ≥ 800px。

**vision_analyze 鉴定每张图**（必做）：盲抓可能抓到不相关图（人头/合影/活动现场）。判断标准 = 图里能看清目标器物，背景/材质/年代给出。

### 步骤 2: 上传到飞书 doc（lark-cli）

**关键铁律 5 条**：

```bash
# 铁律 1: --file 必须相对路径，绝对路径报 "unsafe file path"
# ❌ --file "C:/Users/.../img.jpg" → 报 unsafe
# ✅ 先 cd 到目录用 ./filename

# 铁律 2: --media-insert 默认插到文档末尾（index 87），不在表格后
# 必须配合 step 3 的 block_move_after 才能移到正确位置

# 铁律 3: --update block_replace 创建新 block 不改原 block id
# 每次 replace 生成新 ID，原 block_id 引用全部失效
# 想改 caption → 重新 +media-insert + block_delete 旧图

# 铁律 4: --update block_move_after 支持批量 src-block-ids（逗号分隔）
# 一次性移动多张图到同一锚点

# 铁律 5: caption 用 XML 格式 <img caption="..." height=... src=<file_token> width=.../>
# file_token 来自 +media-insert 返回值
```

**完整流程**：

```bash
cd /c/Users/<user>/Documents/<project>/_sword_imgs/<chapter>

# 1. 上传 1 张图到文档末尾（拿 file_token + block_id）
lark-cli docs +media-insert \
  --doc "<doc URL>" \
  --file "./<器物本名>.jpg" \
  --caption "剑·<样式>（<朝代/出土>）— <博物馆>" 2>&1 | head -20
# 返回: {"block_id": "doxcn...", "file_token": "<token>", "type": "image"}

# 2. 批量移图：把多张图从末尾移到目标表格 block 后
lark-cli docs +update \
  --doc "<doc URL>" \
  --command block_move_after \
  --block-id "<目标表格 block_id>" \
  --src-block-ids "block_id_1,block_id_2,block_id_3,..."

# 3. 在表格上方加注释段（可选）
lark-cli docs +update \
  --doc "<doc URL>" \
  --command block_insert_after \
  --block-id "<目标表格 block_id>" \
  --content '<p><em>↓ 本章参考图见下方（<5 个器物名>；<1 个器物>暂缺）</em></p>'
```

### 步骤 3: 验证

```bash
# fetch 表格附近 range 看图实际渲染顺序
lark-cli docs +fetch --doc "<URL>" \
  --scope range \
  --start-block-id "<目标表格 block_id>" \
  --end-block-id "<下一节 h3 block_id>" \
  --detail with-ids
# 期望输出：<table>...</table><img>图1</img><img>图2</img>...<h3>下一节</h3>
```

## 子代理派发红线

**单子代理抓图任务并发 >5 张必超时**（DDG/百度百科反爬 + 国博 SPA 渲染 + 多次 vision_analyze 调用，单子代理 30 分钟内挂掉）。

**批量配图任务的正确拆分**：

| 规模 | 拆法 |
|------|------|
| < 30 张图，< 3 章节 | 主代理自己跑 |
| 30-60 张图 | 每章节 1 个子代理（≤10 张），N 子代理串行 |
| > 60 张图 | 同上 + 跨会话分批跑（每会话 ≤ 2 章节） |

**禁止**"一波派 11 个并行子代理做 11 个章节"——子代理各自跑抓图+vision_analyze+写图的总开销超 5 分钟必超时。

## 文档末尾加汇报段（bot 跨线程上下文丢失的兜底）

**场景**：bot 在评论链路看不到原始消息（已知工具限制）→ 评论无法 reply → 在文档正文末尾加 v1.x 汇报段，让用户打开文档就能看到进度。

```bash
lark-cli docs +update --doc "<URL>" \
  --command append \
  --content '<h2>v1.1 配图进度（YYYY-MM-DD 更新）</h2><p>用户：X 章节已补 N 张参考图：...。暂缺：...。</p><p>剩余工作量：...。</p>'
```

## 完整实战案例

**中国古剑器物档案 v1.0**（2026-09-03）：B 轴 11 章节中第 1 章节「剑首」6 条器物，配 5 张图（镂空球首缺开放版权图），单章节 30 分钟（子代理超时被砍后主代理接管）。

| 步骤 | 耗时 | 备注 |
|------|------|------|
| 子代理抓图 | 超时被砍（30 分钟） | DDG/百度百科反爬 + 国博 SPA |
| 主代理接管 + 4 张抓图（故宫 DPM + 国博） | 10 分钟 | curl `-g` 关 globbing 关键 |
| vision 鉴定 8 张图 | 3 分钟 | 排除人头合影活动现场等无效图 |
| 5 张图上传 + 排序 + caption | 8 分钟 | block_move_after 批量 + block_replace 改 caption |
| 表格上方注释段 + 文档末尾汇报段 | 5 分钟 | bot 跨线程回不去评论，文档内补汇报 |

**输出验证**（fetch 实测）：
- 表格顺序保留：6 行（圆首/菱首/兽首/盘首/圆箍首/镂空球首）
- 表格后 5 张图按表格顺序排列
- 注释段：「↓ 本章「剑首」参考图见下方（5 张已名；镂空球首暂缺）」
- 文档末尾 v1.1 配图进度段
- 文档版本：revision 4 → 24（+20 次写操作）

## 常见错误

| 症状 | 原因 | 修法 |
|------|------|------|
| `unsafe file path: --file must be a relative path` | 用绝对路径 | `cd` 到目录用 `./filename` |
| `invalid token` (跨 block 匹配) | `--selection-with-ellipsis` 跨多 block | 用 `start...end` 加唯一标识或放弃，走 block_id |
| 图插在文档末尾（index 87）不在表格后 | `+media-insert` 默认行为 | 配合 `block_move_after` 移到目标 |
| caption 改不成功 | `block_replace` 创建新 block 不改原 ID | 用 `+media-insert` 重新插入带正确 caption，`block_delete` 删旧 |
| 子代理 30 分钟挂掉无返回 | 单子代理并发 >5 张图 | 拆单章节单子代理或主代理自己跑 |

## 适用范围

- ✅ 飞书 doc 表格批量配图（博物馆藏品 / 百科条目 / 菜单 / 文物档案）
- ✅ 飞书 doc 段落式条目批量配图（如 D 轴五流派首图）
- ⚠️ cell 内插图：做不到（lark-cli 硬限制）
- ❌ 飞书 sheet/slide：本 skill 不覆盖

## 相关 Skill

- `lark-doc`：lark-cli 操作通用 skill（fetch/update/+media-insert 等基础用法）
- `cn-content-site-extraction`：百度百科/豆瓣/知乎抓取专项
- `web-content-extractor`：通用网页内容批量提取
- `spa-content-extractor`：SPA 文档站提取