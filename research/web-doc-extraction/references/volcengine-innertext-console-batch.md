# 火山引擎文档 Console 批量提取示例

**方法：** Method B（console 内文提取）
**页数：** 4
**产出：** `hermes-output/pages_c.txt`（72,669 字节，1,621 行）

## 提取步骤

```
for each URL:
  browser_navigate(url)
  sleep 3                          # 通过 terminal 等待 SPA 渲染
  browser_console(clear=true, expression="document.body.innerText")
  write_file(append, content)      # 写入 pages_c.txt，含 ===PAGE(N): URL=== 分隔
```

## 抓取页面

1. **产品动态** — `https://docs.volcengine.com/docs/6561/1630433?lang=zh`
   - 产品更新日志：语音同传大模型、语音播客大模型、端到端实时语音大模型、语音合成大模型、声音复刻、语音识别大模型
   - 大量音色表（TTS 1.0/2.0，按语种/类别/名称/Speaker 列）
2. **错误码查询** — `https://docs.volcengine.com/docs/6561/2534853?lang=zh`
   - 音频生成/单向流式/声音复刻 HTTP 接口错误码 + 解决方案
3. **流式语音识别WebSocket** — `https://docs.volcengine.com/docs/6561/1354869?lang=zh`
   - WebSocket ASR 协议：鉴权、二进制 Header、参数表、响应结构、错误码
4. **录音文件识别标准版HTTP** — `https://docs.volcengine.com/docs/6561/1354868?lang=zh`
   - HTTP ASR 接口：提交任务/查询结果双阶段、参数表、响应格式、错误码

## 输出格式

```
===PAGE(1): https://docs.volcengine.com/docs/6561/1630433?lang=zh===
[完整 innerText]

===PAGE(2): https://docs.volcengine.com/docs/6561/2534853?lang=zh===
[完整 innerText]
...
```

## 注意事项

- 火山引擎文档是 SPA，`requests.get()` 拿不到内容，必须用浏览器
- 3s 等待足够渲染；如果网络慢可以加到 5s
- console 提取的内容比 snapshot 更完整（snapshot 长页面会截断）
- 每页 head/footer 导航内容被包含在内 — 如需纯文档内容可后续清洗
