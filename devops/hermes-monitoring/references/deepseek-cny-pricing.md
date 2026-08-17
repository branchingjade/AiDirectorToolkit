# DeepSeek API 人民币定价与费用核算

官方定价页：https://api-docs.deepseek.com/zh-cn/quick_start/pricing （2026-08-06 快照）

## 价格表（元 / 百万 tokens）

| 模型 | 输入·缓存命中 | 输入·未命中 | 输出 |
|------|------|------|------|
| deepseek-v4-flash | 0.02 | 1 | 2 |
| deepseek-v4-pro | 0.025 | 3 | 6 |

## 费用公式

```
费用(元) = cache_read_tokens/1e6 × 命中价 + input_tokens/1e6 × 未命中价 + output_tokens/1e6 × 输出价
```

```python
def cny_cost(model, input_tokens, output_tokens, cache_read_tokens):
    P = {
        'deepseek-v4-flash': (0.02, 1.0, 2.0),
        'deepseek-v4-pro':   (0.025, 3.0, 6.0),
    }
    hit, miss, out = P[model]
    return (cache_read_tokens or 0)/1e6*hit + (input_tokens or 0)/1e6*miss + (output_tokens or 0)/1e6*out
```

注意：`reasoning_tokens` 已含在 output 内，不单独计费（DeepSeek 思考模式不另收费）。

## 实测要点（2026-08-08，8 月全月核算）

- 缓存命中占输入量 95%+（长会话反复读同一上下文：系统提示+知识库+历史），命中价是未命中价的 1/50，是成本主降点。
- state.db 的 `estimated_cost_usd` 是美元估算，DeepSeek 原生人民币计费——向用户报费用一律用人民币重算，不报美元。
- 8 月全月 423 会话、74.4M 非缓存 tokens，费用约 155.9 元（输入未命中 ~56 元 + 输出 ~37 元 + 缓存命中 ~61 元）。
- ⚠️ 官方页面 2026-08 提示「计划近期整体上调定价，预计涨幅较大」——价格以官方页面为准，用前先查。
