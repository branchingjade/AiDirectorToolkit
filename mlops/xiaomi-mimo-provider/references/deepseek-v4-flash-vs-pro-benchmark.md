# DeepSeek v4-flash vs v4-pro Benchmark (2026-07-17)

## Test Setup

- **Task**: Chinese prompt optimization (~80 chars input, Seedance 2.0 format)
- **Input**: "优化这段提示词：中景跟拍，王秀娟转身扯了下王建国，手持特写从手部摇到两人中间，眼神示意陈建国说话。陈建国犹豫，鼓了鼓嘴说不出口，王秀娟面色一冷眼睛一瞪。"
- **Provider**: DeepSeek API (`https://api.deepseek.com/v1`)
- **Config**: `max_tokens=500`, `stream=false`

## Results

| Metric | v4-flash | v4-pro |
|--------|:--------:|:------:|
| TTFB | **1.5s** | 7.0s |
| Output length | 78 chars | 430 chars |
| Total tokens | 121 | 764 |
| Reasoning tokens | 0 | 408 |
| Price (input/output) | ¥1/¥2 per MTok | ¥3/¥6 per MTok |

## Output Comparison

### v4-flash (1.5s)
> 中景跟拍，王秀娟转身扯了下王建国。手持特写从两人手部摇至面部之间，王秀娟以眼神示意陈建国开口。陈建国犹豫片刻，鼓了鼓嘴却说不出口。王秀娟面色一沉，双目一瞪。

### v4-pro (7.0s)
Gave three optimization versions plus analysis, totaling 430 chars. Actively caught the name inconsistency (王建国/陈建国). More thorough but 5x slower and 6x more tokens.

## Conclusion

- **v4-flash**: Best for chat/Feishu interactions — fast, concise, cheap
- **v4-pro**: Best for deep analysis requiring multi-version output — delegate as sub-agent
- For prompt optimization in chat workflows, v4-flash is the clear winner due to speed and cost

## Comparison with MiMo v2.5

| Same task | MiMo v2.5 | DeepSeek v4-flash |
|-----------|:---------:|:-----------------:|
| Response | **60s+ timeout** | **1.5s** |
| Conclusion | ❌ Not suitable for Chinese prompt optimization | ✅ Primary recommendation |
