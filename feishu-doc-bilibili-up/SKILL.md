---
name: feishu-doc-bilibili-up
description: "飞书文档中维护B站UP主推荐列表——拉取数据、内容分析、分类整理、写回飞书文档的完整工作流。"
version: 1.1.0
tags: [feishu, bilibili, docx, up主, 分类]
---

# 飞书文档 B站UP推荐 维护

## 触发条件
- 用户在飞书文档中维护 B站 UP 主推荐列表
- 需要批量拉取 UP 信息、分析内容、归类整理并写回文档

## 核心工作流

### Phase 1: 拉取 UP 数据

**用户信息**（card API，Googlebot UA 可直通）：
```
GET https://api.bilibili.com/x/web-interface/card?mid=<mid>
UA: Mozilla/5.0 (compatible; Googlebot/2.1)
```
返回：昵称、头像、签名、粉丝数、视频数、等级、认证信息。

**视频列表**（移动端 UA，无需 WBI 签名）：
```
GET https://api.bilibili.com/x/space/arc/search?mid=<mid>&ps=8&pn=1&order=click
UA: BiliApp/1.0 Android
```
返回：视频标题、播放量、弹幕数、时长、简介。

⚠️ 不要尝试 WBI 签名——风控极严（-352/-403），移动端 UA 是最稳定方案。卡住就换 UA。

### Phase 2: 内容分析

**不要望文生义**。必须基于实际视频标题和签名做用户画像：

1. 看视频标题关键词：拉片/教程/vlog/评测/创作/导演/摄影/调色/剪辑
2. 看签名定位：教学/从业者/爱好者/学术
3. 看粉丝量级和播放量级：判断影响力
4. 综合归类：导演创作 / 电影分析 / 剪辑实战 / 摄影摄像 / 调色 / 综合

### Phase 3: 本地出 MD（先确认）

⚠️ **铁律：先写本地 MD，展示确认后再动飞书。**

1. 基于 Phase 2 的分析结果，在本地生成结构化的 markdown 文件
2. 展示给用户确认分类、内容、格式
3. 用户确认后，进入 Phase 4

### Phase 4: 写回飞书文档（获批后）

**前提**：飞书 docx API 所有写操作（PATCH/POST）必须带 `?document_revision_id=-1`。

**lark-cli 调用规范**（避免 shell 转义问题）：
```python
subprocess.run([LARK_CLI, "api", method, f"{path}?document_revision_id=-1", "--data", json_str], ...)
```
- 用 list 传参，不用 shell=True
- stderr 也要检查（lark-cli 错误输出到 stderr）

**文档编辑步骤**：

> 完整 API 端点参考：`references/api-endpoints.md`

1. `GET /open-apis/docx/v1/documents/{token}/blocks` — 获取 block 结构
2. `PATCH .../blocks/{block_id}` — 更新 block 文本内容
   ```json
   {"update_text_elements":{"elements":[
     {"text_run":{"content":"文本","text_element_style":{"link":{"url":"https://..."}}}},
     {"text_run":{"content":"  — 描述"}}
   ]}}
   ```
3. `POST .../blocks/{parent_id}/children` — 创建新 block
   ```json
   {"children":[{"block_type":4,"heading2":{"elements":[...],"style":{}}}],"index":N}
   ```
   - block_type: 4=H2, 12=bullet
   - 从底部向上插入保持 index 稳定

4. 创建后必须重新 GET blocks 刷新 block ID 列表（index 会变化）

### Phase 5: 验证

发布后重新 GET blocks 检查结构，确认分类标题和内容正确。

## 已知限制

- **DELETE 不支持**：docx API 的 DELETE 端点始终返回 404，只能更新不能删除
- **PATCH 只能改文本**：不能改 block 类型，要新类型只能 POST 创建
- **并发限制**：单文档每秒 3 次编辑，加 sleep(0.3) 保安全
- **B站 API 不稳定**：Googlebot/移动端 UA 可能随时被 B 站封，遇到风控换 UA 重试

## 相关记忆

- Memory: B站API反爬 — 移动端UA绕过WBI
- Memory: 飞书docx写操作需要document_revision_id=-1
