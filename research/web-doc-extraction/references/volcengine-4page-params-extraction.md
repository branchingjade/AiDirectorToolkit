# Volcengine Speech API 4-Page Parameter Extraction Example

## Source URLs
1. 播客API-websocket-v3协议: https://docs.volcengine.com/docs/6561/1668014?lang=zh
2. 同声传译2.0: https://docs.volcengine.com/docs/6561/1756902?lang=zh
3. 机器翻译大模型: https://docs.volcengine.com/docs/6561/2306735?lang=zh
4. 豆包语音妙记: https://docs.volcengine.com/docs/6561/1798094?lang=zh

## Extraction Pattern Used
- `browser_navigate(url)` → `browser_snapshot(full=true)` → `read_file(snapshot_path)` per page
- Each page had ~1500-3400 lines of accessibility tree
- Extracted: endpoints, auth headers, request params, response fields, event definitions, error codes

## Output File Format (written to `verify_c.txt`)
```
=== 模块名称 ===
【源StaticText】页面标题
【端点】端点URL (含HTTP method或WSS)

【请求头参数表】
| Key | 说明 | 是否必须 | Value示例 |

【请求体/请求字段参数表】
| 字段 | 说明 | 是否必须 | 类型 | 默认值 |

【事件定义】(WebSocket only)
| Event code | 含义 | 类型 |

【响应字段】
| 字段 | 类型 | 说明 |

【错误码】
| 错误码 | 含义 | 说明 |
```

## Key Differences per Protocol Type

| Aspect | HTTP (机器翻译、妙记) | WebSocket (播客、同传) |
|--------|---------------------|----------------------|
| Endpoint format | `POST <url>` | `wss://...` |
| Auth | Headers only | Headers on connect + binary frame header |
| Parameter transport | JSON request body | Binary frame + Protobuf/JSON payload |
| Statefulness | Stateless (request→response) | Session-based (StartSession→events→FinishSession) |
| Response streaming | No | Yes (event codes for start/data/end) |
| Extra extraction needed | — | Event code table + binary frame structure |

## Common Pitfalls on Volcengine Docs
- SPA renders content dynamically — always use browser (never requests.get)
- Large snapshot files (>100K chars) need `read_file` with offset/limit
- Pages mix multiple parameter tables (headers, payload, response, events) — extract each separately
- Auth varies: newer docs use `X-Api-Key`; older docs use `X-Api-App-Id` + `X-Api-Access-Key`
- WebSocket binary protocol: 4-byte header (version/type/serialization/compression) + payload
