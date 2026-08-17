# OpenCode Go 订阅服务档案

来源：opencode.ai 官方文档 + 本机 Hermes 源码 + 2026-08-11 实测。

## 是什么

- OpenCode（opencode.ai）官方的低成本开源编程模型订阅服务
- 定价：首月 $5，之后 $10/月；一个 workspace 限一人订阅
- key 获取：https://opencode.ai/auth 登录 → 订阅 → 复制 API key
- 与 OpenCode CLI 的关系：Go 是 provider，不依赖 CLI 也能用；Hermes 原生支持

## Hermes 接入要点

- provider id：`opencode-go`
- 环境变量：`OPENCODE_GO_API_KEY`（key）、`OPENCODE_GO_BASE_URL`（覆盖项，**一般不要设**）
- 内置默认 base_url：`https://opencode.ai/zen/go/v1`（源码 hermes_cli/auth.py ProviderConfig 定义）
- 模型名不带 provider 前缀：`glm-5.2`、`deepseek-v4-flash`（Hermes 侧写 `opencode-go/glm-5.2`）

## 混合 API 面（源码注释确认）

- GLM / Kimi：OpenAI 兼容 chat completions 下 /v1
- MiniMax / Qwen 3.7：Anthropic Messages 下 /v1/messages
- Hermes 按模型自动选 api_mode；手动 curl 验证用 OpenAI 格式即可

## 模型清单（2026-08-11 GET /models 实测，25 个）

| 类别 | 模型 |
|---|---|
| 强推理 | glm-5.2 / glm-5.1 / glm-5、qwen3.8-max / qwen3.7-max / qwen3.7-plus / qwen3.6-plus / qwen3.5-plus、grok-4.5、gpt-5.6-luna、kimi-k3 |
| 均衡 | deepseek-v4-pro、kimi-k2.7-code / kimi-k2.6 / kimi-k2.5、minimax-m3 / m2.7 / m2.5 |
| 轻量快 | deepseek-v4-flash、mimo-v2.5-pro / mimo-v2.5 / mimo-v2-pro / mimo-v2-omni、hy3 / hy3-preview |

## 实测数据（2026-08-11）

- `deepseek-v4-flash`：HTTP 200，首 token ~9.5s，max_tokens 20 正常返回
- `glm-5.2`：30s 超时（推理模型首 token 慢，非故障）——验证链路别用它当探针
- 误配案例：`.env` 曾设 `OPENCODE_GO_BASE_URL=https://api.anthropic.com/v1` → 403（key 完好，是端点错）；改回默认后 200

## 用户现状（2026-08-11）

- 已订阅，key 有效（67 字符 sk-PrA… 前缀），base_url 已修正，.env 备份 `.env.bak-opencode-go`
- 接入方式待用户拍板：主模型切换 / fallback 兜底 / 会话内 /model 按需切换
