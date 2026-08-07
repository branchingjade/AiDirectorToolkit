# Sample Output: Volcano Engine API Documentation Extraction

This file shows the output format from a 5-page batch extraction of Volcano Engine (豆包语音) API documentation. Use as a reference for the `web-doc-extraction` skill.

**Source URLs (5 pages):**
- Page 1: 替换词 API v1.1 (Correct Table API)
- Page 2: 术语词 (Translation terminology)
- Page 3: API Key使用 (Key management)
- Page 4: QPS/并发查询接口 (QuotaMonitoring)
- Page 5: 调用量查询接口 (UsageMonitoring)

**Output structure per page:**
- `## [N] Page Title` with `### URL:`
- `### 基本信息` — endpoint host, method, auth, service/region constants
- `### API列表` or per-API sections with request/response parameter tables
- `### ResourceID 附录` — reference tables when present
- Separated by `---`

**Example section (page 4):**

```
## [4] QPS/并发查询接口 (QuotaMonitoring)
### URL: https://docs.volcengine.com/docs/6561/1476626?lang=zh

### 基本信息
- 接口地址: open.volcengineapi.com
- 请求方式: GET
- Action: QuotaMonitoring
- Version: 2021-08-30
- Service: speech_saas_prod
- Region: cn-north-1

### 请求参数 (Query)
| 参数 | 类型 | 必选 | 说明 | 示例 |
|------|------|------|------|------|
| AppID | string | 是 | 应用ID | 10000000 |
| ResourceID | string | 是 | 资源ID(详见附录) | volc.service_type.10029 |
| Start | date | 是 | 查询起始时间 yyyy-MM-dd | 2024-08-15 |
| End | date | 是 | 查询结束时间 yyyy-MM-dd | 2024-08-15 |
| Mode | string | 否 | daily/hourly/minutely/5 minutely | hourly |

### 响应参数
| 参数 | 类型 | 说明 |
| status | string | 响应状态 success/fail |
| data.quota_monitoring[].day | string | 查询日期维度指标 |
| data.quota_monitoring[].value | int | 指标用量(qps/并发) |
| data.quota_monitoring[].limit | int | quota最大值 |

### 响应示例
{
    "status": "success",
    "data": {
        "quota_monitoring": [
            {"day": "2024-08-14 00:00:00", "value": 2, "limit": 2}
        ]
    }
}
```

**Key technique — sub-page drill-down:**
Some documentation pages are *index* pages that list links to sub-pages (e.g., "API Key使用" shows links to "ListAPIKeys", "CreateAPIKey", "DeleteAPIKey", "UpdateAPIKey"). Click through to each sub-page to capture the actual API spec — the menu stays open across clicks.

**Rapid navigation pattern:**
- After writing extracted data for page N, navigate to page N+1 in the same response turn (parallel write + navigate)
- browser_snapshot(full=true) saves the full page to a cache file; read_file reads from that cache path
