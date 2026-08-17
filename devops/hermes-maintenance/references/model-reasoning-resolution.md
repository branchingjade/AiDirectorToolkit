# Hermes 模型/思考强度解析链（查「XX端现在用什么模型、thinking 多高」）

用户问「飞书端/评论 agent/某渠道现在用什么模型、思考强度多少」时的标准解答链（2026-08-17 实测整理）。

## 核心事实

1. **思考强度只有一个统一解析口**：`hermes_constants.py::resolve_reasoning_config(cfg, model)`（源码 docstring 明列 shared by every surface：CLI startup / messaging gateway / Desktop/TUI / cron / fallback 激活）。优先级：
   - ① per-model 覆盖：`agent.reasoning_overrides`（按模型名查，spelling-tolerant，见 `resolve_per_model_reasoning_effort`）
   - ② 全局 `agent.reasoning_effort`——**保留原始值**：YAML `False`/`off`/`no` = thinking 禁用，代码不用 `or ""` 强转（否则静默重开 thinking）
   - 会话级 `/reasoning --session` 覆盖由 gateway 调用方**先于**本函数解析，永远最高优先级

2. **AIAgent 构造器不收 reasoning_effort 参数**——内部从 config.yaml 解析。因此任何临时 AIAgent（飞书评论 agent、/compress 等）只要构造时没显式传 reasoning 相关参数，**思考强度 = 全局 `agent.reasoning_effort`**。查某个 agent 的思考强度：先 grep 它的 `AIAgent(` 调用有没有显式传参，没有就是全局值，别去猜平台级覆盖。

3. **模型解析有两条路，容易混**：
   - gateway 消息会话：`platforms.<平台>.model` / `.provider` 平台级覆盖 → 否则 `model.default`
   - 飞书评论 agent（`plugins/platforms/feishu/feishu_comment.py::_resolve_model_and_runtime`）→ `_resolve_gateway_model(user_config)`（`gateway/run.py:3358`）**只读 model 段的 default/model 键——不吃 platforms.feishu.model 覆盖**。所以评论 agent 模型与飞书消息端模型可能不同（本机恰好都是 deepseek-v4-flash 是巧合不是机制）。`_resolve_runtime_agent_kwargs`（run.py:2596）只返回凭据（api_key/base_url/provider/api_mode/max_tokens），**不含 reasoning 字段**。

4. **`delegation.reasoning_effort` 只管 delegate_task 子代理**。渠道 channel_prompt 里写了 delegate_task 委托时，被委托子代理的思考强度 = delegation.reasoning_effort，不是渠道那套——回复前想清楚用户问的是「主会话」还是「子代理」。

## 排查顺序（30 秒出结论）

```bash
# 1. reasoning_effort 出现在哪几段（agent 全局 / delegation / auxiliary 分任务）
grep -n -i "reasoning_effort\|reasoning_overrides" "$LOCALAPPDATA/hermes/config.yaml"
# 2. 平台段有无 model/其他覆盖
grep -n -A8 "^  feishu:" "$LOCALAPPDATA/hermes/config.yaml"
# 3. 会话级覆盖（/reasoning --session 持久化痕迹）
grep -o -i "reasoning[^\"]*" "$LOCALAPPDATA/hermes/gateway_state.json"   # 空=无会话覆盖
# 4. 目标 agent 构造代码是否显式传参
grep -n "AIAgent("  "$LOCALAPPDATA/hermes/hermes-agent"/plugins/platforms/feishu/feishu_comment.py
```

结论 = `agent.reasoning_effort`（无 per-model 覆盖、无平台级覆盖、无会话级覆盖时）。

## 本机实况（2026-08-17 查证）

- `agent.reasoning_effort: medium`（config.yaml:75）；无 `agent.reasoning_overrides`
- `platforms.feishu.model: deepseek-v4-flash`（provider deepseek），平台段无 reasoning 键
- `gateway_state.json` 无会话级 reasoning 覆盖
- 飞书消息端 = deepseek-v4-flash / medium；评论 agent = deepseek-v4-flash（model.default 解析）/ medium（AIAgent 未传参回落全局）
- `delegation.reasoning_effort: xhigh` → 飞书 channel_prompt 委托的子代理是 xhigh，比主会话高

## 工具坑（本次踩到，复用）

- `search_files` 传 Windows 反斜杠绝对路径间歇 IO error（rg 无法访问路径）→ 改用 `terminal` cd 到目录 + grep
- grep+sed 嵌套巨型单行（`sed -n "$(grep -n ... | cut ...),+40p"`）被命令护栏按 oversized 拦截 → 先 `grep -n` 拿行号，再 read_file 分段读