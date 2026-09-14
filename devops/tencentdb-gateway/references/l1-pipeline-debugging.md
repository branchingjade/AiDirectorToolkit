# TDB L1 Pipeline Deep-Dive (2026-08-27 实战)

> SKILL.md §13/§14 写了"端点 + 灌入"修复。本文件记录**第二个根因层**——端点修对后仍然 PARSE_FAIL 的真相。

## 真相：agentmemory/memory-core 是完全开源的

**不要被"商业版三件套"叙述误导**。Docker Hub 上 `agentmemory/memory-core:latest` 容器内**全部源码在** `/app/src/`：

| 路径 | 作用 |
|------|------|
| `/app/src/core/record/l1-extractor.ts` | L1 主流程：解析 LLM 返回 → 写 L1 atomic |
| `/app/src/core/prompts/l1-extraction.ts` | LLM prompt 模板（system 期望 schema = `[{"scene_name", "message_ids", "memories": [...]}]`）|
| `/app/src/core/record/l1-writer.ts` | L1 atomic 写入 SQLite + vectors.db |
| `/app/src/utils/sanitize.ts` | JSON sanitize（`sanitizeJsonForParse`）|
| `/app/src/utils/clean-context-runner.ts` | LLM runner（fallback 路径）|
| `/app/src/adapters/standalone/llm-runner.ts` | Standalone LLM 调用（实际被 l1-extractor 用）|
| `/app/src/gateway/config.ts` | 配置解析（line 451 = LLM baseUrl 优先级）|
| `/app/node_modules/ai/dist/index.js` | **AI SDK 6.0.266**（关键 bug 出处）|

任何"找不到字段"、"schema 不匹配"、"返回 null"的问题——**直接 cat 文件**，不要查文档。

## L1 PARSE_FAIL 根因（端点修复后仍 0 抽取）

**症状**（修完 §13 openai.com → mimo 后）：
```
INFO  [l1-extractor] run() completed: 65473ms, steps=1, output=181 chars
WARN  [l1-extractor] PARSE_FAIL rawLen=181, rawFull="[\n  {\n    \"scene_name\": \"...
LLM detected 0 scene(s)
Total extracted memories: 0 across 0 scene(s)
```

**关键证据**：rawLen=181，**但 `l1_extraction_output_tokens=4096`**（mimo 实际输出 4096 tokens ≈ 18000+ 字符）—— 数字矛盾说明 raw 被中间层截断。

**根因（三层）**：

### 第 1 层：AI SDK `safeParseJSON` → `fixJson` 截断

`/app/node_modules/ai/dist/index.js` 的 `parsePartialJson(jsonText)`：

```js
async function parsePartialJson(jsonText) {
  let result = await safeParseJSON({ text: jsonText });
  if (result.success) return { value: result.value, state: "successful-parse" };
  result = await safeParseJSON({ text: fixJson(jsonText) });  // ← 问题在这
  if (result.success) return { value: result.value, state: "repaired-parse" };
  return { value: undefined, state: "failed-parse" };
}
```

`fixJson(input)` 是给**流式 JSON** 用的——它按字符遍历，匹配到 invalid 字符就**截断到 `lastValidIndex`**。当 LLM 返回的完整 JSON 在某个位置被它误判为"无效"（例如中文标点、全角字符、双引号转义），raw 就会被截到 181 字符。

**这是 AI SDK 6.0.266 的已知行为**——用流式解析逻辑处理非流式完整 JSON，导致正常返回被截断。

### 第 2 层：l1-extractor 默认依赖 AI SDK 的 text 字段

`/app/src/core/record/l1-extractor.ts` line 487：

```ts
result = await llmRunner.run({
  prompt: userPrompt,
  systemPrompt,
  taskId: "l1-extraction",
  timeoutMs: 180_000,
  ...traceParams,
});
// 接着 parseExtractionResult(result, logger)  ← 拿到的是已截断的 raw
```

**`llmRunner.run()` 返回的是 `generateText()` 的 `.text` 字段**——已被 AI SDK 的 fixJson 处理过，原始 mimo 响应丢失。

**没有方法绕过 AI SDK**——除非重写 runner 调用层，直接调 mimo HTTP API。

### 第 3 层：raw 截断 ≠ token 计数丢失

metric 上报 `l1_extraction_output_tokens=4096`（从 `usage.outputTokens` 拿）——但传给 l1-extractor 的 `raw` 已经被截断。**两个值来自不同路径**：

- `usage` = AI SDK 直接拿 mimo 响应里的 usage 字段（准确）
- `text` = AI SDK 经过 fixJson 处理后的输出（被截断）

**这解释了为什么 log 显示 "output=181 chars" 但 metrics 显示 4096 tokens**——同一调用，不同处理路径。

## 验证步骤（按顺序）

```bash
# 1. 确认 mimo 本身能返回完整 JSON（绕过 AI SDK）
#    在容器内 / 本机 curl：
curl -s -X POST https://api.xiaomimimo.com/v1/chat/completions \
  -H "Authorization: Bearer <real_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mimo-v2.5",
    "messages": [
      {"role": "system", "content": "你是专业的\"情境切分与记忆提取专家\"。返回且仅返回一个合法的 JSON 数组：[{\"scene_name\": \"...\", \"message_ids\": [...], \"memories\": []}]"},
      {"role": "user", "content": "用户：今天确认了 TDB L1 pipeline 端点修复。\n助手：L1 pipeline 修通。"}
    ],
    "max_tokens": 8000,
    "temperature": 0.3
  }'
# 期望：content 字段返回完整 JSON 数组（~400 字符），finish_reason=stop
# 实测：✅ mimo 工作完全正常

# 2. 观察容器内 l1-extractor 收到的 raw
ssh HMSJadmin@hmsj.local "docker logs tdb-core --tail 200 | grep 'PARSE_FAIL'"
# rawFull 字段被截到 ~181 字符，但 output_tokens metric 是 4096

# 3. 直接 cat 容器内的 l1-extractor 源码确认解析逻辑
ssh HMSJadmin@hmsj.local "docker exec tdb-core sh -c 'sed -n \"485,520p\" /app/src/core/record/l1-extractor.ts'"
# 看到 llmRunner.run() → parseExtractionResult(result, logger)
```

## 解决方案（按工作量从小到大）

### 方案 1：接受现状（0 工作量）
- L0 conversation 持续写入（每天几千行 jsonl）
- 跨桶 recall 用 L0 已能工作（score 0.93-0.97）
- **代价**：L1 atomic 三 type 永远是 0，recall 时无法按 episodic/persona/instruction 精准过滤

### 方案 2：升级 ai 包到能正确处理完整 JSON 的版本
- `/app/node_modules/ai/package.json` 当前 6.0.266
- 需要找能区分 partial JSON 和 complete JSON 的版本（也许 6.x 后续版本修了）
- **风险**：npm install 在 NAS docker.io 不通时拉不到
- **回滚**：必须 `docker cp + docker restart`（不能 docker compose build）

### 方案 3：在容器内 patch AI SDK（治标）
- 找到 `parsePartialJson` 函数（`/app/node_modules/ai/dist/index.js` line ~3750）
- 改成：如果 `JSON.parse(jsonText)` 直接成功，就**不走 `fixJson` 分支**
- 这就是"绕过 fixJson 截断"的最小改动
- 实施：在容器内 `sed -i 's/.../.../'` 或写入修复文件 + `docker cp`
- ⚠ **patch 会被 npm install 覆盖**——必须 docker commit 固化（坑 8）

### 方案 4：重写 l1-extractor 直接调 mimo HTTP API（治本但工作量大）
- 跳过 AI SDK 完全
- 在 `/app/src/core/record/l1-extractor.ts` 添加 `directMimoCall()` 函数
- 修改 LLMRunner 调用处用 direct path
- 然后 `docker cp + restart + docker commit`

## mimo 返回 JSON 完整 schema 验证

mimo `mimo-v2.5` 在收到 L1 prompt 时**返回完整合法 JSON**——这是经过本机 curl 验证的（mimo API 直接调用，无需 AI SDK）：

```json
[
  {
    "scene_name": "TDB L1 pipeline 端点修复确认",
    "message_ids": [1, 2],
    "memories": [
      {
        "content": "确认 TDB L1 pipeline 端点修复：从 openai.com 改回 xiaomimimo.com；L1 pipeline 修通，mimo 调用成功，运行时间 32267ms。",
        "type": "episodic",
        "priority": 80,
        "source_message_ids": [1, 2],
        "metadata": {}
      }
    ]
  }
]
```

**schema 字段完全对齐**（`scene_name` / `message_ids` / `memories[].content/type/priority/source_message_ids/metadata`）。

`l1-extractor` 的 `parseExtractionResult()` 也是按这个 schema 解析的（line 565+）。

## 决策矩阵

| 场景 | 方案 |
|------|------|
| 用户能接受"L0 跨桶 recall 工作即可" | 方案 1 |
| 需要 L1 atomic 结构化数据 + NAS 有 docker.io 临时通道 | 方案 2 |
| 需要快速修复 + 可承受 commit 工作量 | 方案 3 |
| 长期方案（NAS 不通 docker.io） | 方案 4 |

## 关联引用

- SKILL.md §13：L1 pipeline openai.com → mimo 端点修复（前置步骤）
- SKILL.md §6 坑 8：Docker.io 不通时的修补兜底（方案 3/4 落地姿势）
- SKILL.md §6 坑 7：Docker compose env 必须 down + up（方案 2/3 后重启姿势）