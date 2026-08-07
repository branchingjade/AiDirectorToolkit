---
name: fix-model-pricing
description: "修正 Hermes 硬编码的模型定价，与官方文档同步。覆盖 DeepSeek / MiMo / Kimi。"
version: 2.0.0
---

# 修正模型定价

Hermes 在 `agent/usage_pricing.py` 的 `_OFFICIAL_DOCS_PRICING` 字典中硬编码了各模型价格。中国厂商（DeepSeek、MiMo、Kimi）定价变动频繁，需定期对照官方文档修正。**不需要修改 `resolve_billing_route`**——默认路由会透传 provider name 给定价查找。

## 触发条件

- `/usage` 显示成本为 `n/a`（说明模型不在定价表里）
- 预估成本明显偏高或偏低
- 厂商发布新模型或调整价格

## 通用步骤

### 1. 查 Hermes 当前定价

```bash
grep -B1 -A8 '"<provider>"' ~/.hermes/hermes-agent/agent/usage_pricing.py
```

### 2. 查官方最新价格

根据 provider 打开对应官方页面，获取人民币价格（元/百万 tokens）。

### 3. 换算为 USD（汇率按当前）

### 4. 更新 `_OFFICIAL_DOCS_PRICING`

编辑 `~/.hermes/hermes-agent/agent/usage_pricing.py`，新增或更新条目。

**注意：中国厂商定价模型是「缓存命中/未命中」，不是 Anthropic 的 input+cache_read+cache_write。映射关系：**
- `input_cost_per_million` ← 缓存未命中价格（USD）
- `cache_read_cost_per_million` ← 缓存命中价格（USD）
- `output_cost_per_million` ← 输出价格（USD）
- 没有 cache_write 价格（不填）

### 5. 重启生效

`/reset` 或新会话。

---

## DeepSeek

**官方页：** https://api-docs.deepseek.com/zh-cn/quick_start/pricing/

| 模型 | 缓存未命中 | 缓存命中 | 输出 |
|------|----------|---------|------|
| deepseek-v4-flash | ¥1 | ¥0.02 | ¥2 |
| deepseek-v4-pro | ¥3 | ¥0.025 | ¥6 |

Hermes 条目 key：`("deepseek", "deepseek-v4-pro")` / `("deepseek", "deepseek-v4-flash")`。`deepseek-chat`（V3）和 `deepseek-reasoner`（R1）将于北京时间 2026/07/24 23:59 弃用。过渡期内仍可用，之后分别对应 `deepseek-v4-flash` 的非思考与思考模式。

注意：Hermes 的模型选择器（`hermes model`）目前只列出 deepseek-v4-pro，未列出 v4-flash。直接用 `hermes config set model.default deepseek-v4-flash` 或 `hermes chat -m deepseek-v4-flash` 即可使用，无需等官方适配。

## MiMo (Xiaomi)

**官方页：** https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go （海外 USD 定价直接列在页面上，无需换算）

| 模型 | 缓存未命中 | 缓存命中 | 输出 |
|------|----------|---------|------|
| mimo-v2.5 | $0.14 | $0.0028 | $0.28 |
| mimo-v2.5-pro | $0.435 | $0.0036 | $0.87 |

Hermes 条目 key：`("xiaomi", "mimo-v2.5")` / `("xiaomi", "mimo-v2.5-pro")`。

## Kimi (Moonshot)

**官方页：** https://platform.kimi.com/docs/pricing （RMB，需换算 USD）

| 模型 | 缓存未命中 | 缓存命中 | 输出 |
|------|----------|---------|------|
| kimi-k2.7-code | ¥6.50 | ¥1.30 | ¥27.00 |
| kimi-k2.6 | ¥6.50 | ¥1.10 | ¥27.00 |
| kimi-k2.5 | ¥4.00 | ¥0.70 | ¥21.00 |

Hermes 条目 key：`("moonshot", "kimi-k2.5")` 等。

---

## Pitfalls

- Hermes 更新（`hermes update`）会覆盖此文件，需重新打补丁
- `pricing_version` 日期格式：`<provider>-pricing-YYYY-MM-DD`
- 中国厂商定价页面可能根据登录地区显示不同价格
- **MiMo 官方页直接提供海外 USD 定价，优先使用，避免汇率换算误差**
- Kimi/Moonshot 官方页仅提供 RMB 定价，需自行换算（汇率约 7.2）
- 别动 `resolve_billing_route`——不需要，默认路由已透传 provider
- Kimi provider key 用 `"moonshot"`，不是 `"kimi"`
