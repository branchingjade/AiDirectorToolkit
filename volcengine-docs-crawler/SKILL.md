---
name: volcengine-docs-crawler
description: 批量抓取火山引擎（豆包语音）API文档页面。触发词：豆包语音API、volcengine docs、火山引擎API参考。
category: devops
---

# 火山引擎文档批量抓取

## 铁律

1. **只用三步法：`browser_navigate → browser_snapshot(full=true) → read_file`**。禁止 CORS fetch / Python requests / browser_console 批量 fetch。
2. **每个页面默认显示"产品动态"，API 内容在子导航下** — 用 snapshot 里的 StaticText 提取，不要点导航。
3. **一页一页串行**，单页 30 秒，不贪多。
4. **并行用 `delegate_task`** — 每个子 agent 独立浏览器实例。

## 标准流程

```
browser_navigate(url)
browser_snapshot(full=true)
read_file(返回的snapshot路径)
```

## snapshot 解析规则

- 参数行：`- StaticText "参数名 类型 说明"`
- 表头行：`- columnheader "字段"` / `- columnheader "类型"`
- 端点行：包含 `POST https://openspeech.bytedance.com` 或 `wss://openspeech.bytedance.com`
- 错误码：8 位数字如 `20000000`

## 已踩坑

- 火山引擎文档是 SPA，`requests.get()` 只能拿到空壳
- HTTP 请求走 `openspeech.bytedance.com`，控制台接口走 `open.volcengineapi.com`
- 鉴权不统一：新版 `X-Api-Key` / 旧版 `X-Api-App-Id + X-Api-Access-Key` / AKSK
- 异步接口统一 submit + query 模式
- WebSocket 接口用 4 字节二进制 Header + Payload
