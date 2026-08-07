# 模型兜底链（fallback_providers）诊断 — 配置/传递/触发三层核查

2026-08-07 实测：用户问「飞书渠道也要引入兜底模型」，排查结论是飞书与桌面在 fallback 上完全平级（无需渠道级配置），「没见切换」≠「没兜底」。

## 架构事实（源码核实）

1. **兜底链是根级全局配置**：config.yaml 根级 `fallback_providers`（列表）或旧式 `fallback_model`（单 dict），由 `hermes_cli/fallback_config.py::get_fallback_chain()` 合并解析（两条 key 都读，fallback_providers 优先，去重）。
2. **全渠道统一传递，与渠道 model 覆盖无关**：gateway 创建 agent 时对**所有**渠道（含飞书）统一传 `fallback_model=self._runner._refresh_fallback_model()`（gateway/run.py:4826，`_refresh_fallback_model` 定义于 run.py:8415）——`platforms.feishu.model/provider` 渠道覆盖只改主模型，不 bypass 兜底链。**飞书不需要渠道级 fallback 配置**。
3. **重试先于兜底**：`agent.api_max_retries`（默认 3）先重试，重试耗尽才走 `try_activate_fallback`（agent/chat_completion_helpers.py:1730）。限流/计费/连接失败/认证失败四类（FailoverReason）都触发兜底，但偶发连接错误通常被重试救回，根本到不了切换。
4. **`fallback_active: false` 是正常态**：state.db sessions 表 `model_config.gateway_runtime.fallback_active` 为 false 只说明主模型最近没失败到需要切换——不是没装兜底链。别当「没兜底」的证据。

## 验证配方（按序，每步有独立结论）

```bash
# 1. 配置层：解析实际生效的链（条目缺 model 会被静默过滤！）
cd ~/AppData/Local/hermes/hermes-agent && ./venv/Scripts/python.exe -c "
import json, yaml
from hermes_cli.fallback_config import get_fallback_chain
cfg = yaml.safe_load(open(r'C:/Users/HMSJ/AppData/Local/hermes/config.yaml', encoding='utf-8'))
print(json.dumps(get_fallback_chain(cfg), ensure_ascii=False, indent=1))
"

# 2. 可用层：兜底目标 client 能否真正构建（base_url + key 是否就位）
./venv/Scripts/python.exe -c "
import os; os.environ.setdefault('HERMES_HOME', r'C:/Users/HMSJ/AppData/Local/hermes')
from agent.auxiliary_client import resolve_provider_client
client, fm = resolve_provider_client(provider='xiaomi', model='mimo-v2.5-pro', raw_codex=True)
print('client:', bool(client), '| base_url:', str(client.base_url)[:60] if client else None, '| model:', fm)
"

# 3. 运行时层：主模型失败时是「重试救回」还是「真切换」
grep -i "Retrying API call\|switching to fallback\|trying fallback" ~/AppData/Local/hermes/logs/errors.log ~/AppData/Local/hermes/logs/agent.log | tail

# 4. 会话记录层：查 fallback_active 状态
#    state.db sessions 表 → model_config 列 → gateway_runtime.fallback_active
#    （false=正常没触发，非缺失）
```

## 关键坑

- **链条目缺 model 字段 = 静默失效**：`_iter_fallback_entries`（fallback_config.py:43）要求 provider 和 model 都非空，缺 model 的条目直接跳过。`- provider: deepseek` 没 model 就白配。
- **同 provider 同模型条目被跳过**：`try_activate_fallback` 用 `agent.backend_identity.should_skip_candidate` 判重，与当前失败后端相同的条目跳过（防循环）——主模型是 deepseek-v4-flash 时，链里再写 deepseek/deepseek-v4-flash 等于不存在。
- **真兜底 = 异 provider 条目**：链里 deepseek→deepseek 在 DeepSeek 整体宕机时同样失败，只有 xiaomi 等异 provider 条目才是真兜底。本机链：xiaomi/mimo-v2.5-pro → xiaomi/mimo-v2.5 → deepseek/deepseek-v4-flash（被跳过）→ deepseek/deepseek-v4-pro。
- **`resolve_entry_api_key` 返回 None 是正常的**：fallback 条目没配 `key_env`/`api_key` 时返回 None，让 `resolve_provider_client` 走 provider 标准凭据解析（XIAOMI_API_KEY / XIAOMI_BASE_URL 环境变量）。不要据此判「没配 key」。
- **`resolve_provider_client` 返回 (client, final_model) 不是 (client, base_url)**：第二个返回值是模型名不是 URL，打印时别误读成 base_url 错误（实测踩过：把 final_model 当成 base_url 怀疑 xiaomi 路由坏了）。
- **xiaomi 作为 LLM provider 走 generic API-key 分支**：`hermes_cli/providers.py:184` HermesOverlay(transport="openai_chat", base_url_env_var="XIAOMI_BASE_URL")。.env 中 XIAOMI_API_KEY + XIAOMI_BASE_URL 就位即可，实测 client 构建成功（https://api.xiaomimimo.com/v1/）。
- **渠道级 model/provider 覆盖（platforms.feishu.model）不影响兜底链**：fallback 链独立传入，与 turn_route 的 model 解析无关（`_resolve_turn_agent_config` run.py:7101）。

## 排查报告话术

给用户的结论先分层：配置层（链在不在）→ 传递层（渠道有没有拿到）→ 触发层（失败有没有到切换）。「没见切换」≠「没兜底」，先说明重试救回机制，再问用户具体观察到的场景（报错时间点/是否手动测试过），有实据再回溯日志。可用 clarify 问用户是哪种场景（确认即可/独立兜底/换主模型/实际没兜底需排查）。
