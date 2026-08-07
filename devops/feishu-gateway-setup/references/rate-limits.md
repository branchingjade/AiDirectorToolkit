# Feishu API Rate Limits (频控策略)

Last verified: 2026-06-29. Source: https://open.feishu.cn/document/server-docs/api-call-guide/rate-limit

## Custom Bot Limits

自定义机器人（即 Hermes Gateway 使用的类型）：

| 维度 | 限制 |
|------|------|
| QPS | **5 次/秒** |
| QPM | **100 次/分钟** |

两个上限任意一个触发都会返回 HTTP 429（部分旧版 API 返回 HTTP 400 + error code 99991400）。响应头包含：
- `x-ogw-ratelimit-limit`: 窗口期上限（秒）
- `x-ogw-ratelimit-reset`: 恢复周期（秒），应等待此秒数后重试

## Key Constraints

- **消息/群组 API 不支持提频** — 无法申请提高
- 建议避开整点/半点发送（如 10:00、17:30），否则可能触发系统级 11232 限流
- 频控是 **每应用、每租户** 粒度

## Standard API Rate Limit Tiers

自建应用根据企业套餐等级有不同限制。以下是所有标准等级（商店应用另有规则）：

| 等级 | 描述 | 限制 |
|------|------|------|
| 1 | 10次/分 | 10次/分 |
| 2 | 20次/分 | 20次/分 |
| 3 | 100次/分 | 100次/分 |
| 4 | 1000次/分 & 50次/秒 | 1000次/分 & 50次/秒 |
| 5 | 1次/秒 | 1次/秒 |
| 6 | 5次/秒 | 5次/秒 |
| 7 | 10次/秒 | 10次/秒 |
| 8 | 20次/秒 | 20次/秒 |
| 9 | 50次/秒 | 50次/秒 |
| 10 | 50次/秒（商业版100次/秒） | 50-100次/秒 |
| 11 | 100次/秒 | 100次/秒 |
| 21 | 3次/秒 | 3次/秒 |

## Handling Rate Limits

1. 收到 HTTP 429 → 读取 `x-ogw-ratelimit-reset` 响应头
2. 等待指定秒数
3. 重试请求
4. 若再次失败，继续退避直到成功

Hermes Gateway 的 feishu adapter 内部已实现自动重试，通常无需手动处理。
