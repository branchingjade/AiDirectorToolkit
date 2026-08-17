# DSH 会话日志提取（zstd jsonl）

headless 调用产生的会话**不进 web UI 会话列表**，但完整过程落盘在磁盘——用户想看「DSH 的思考链路/会话过程」时用这个方法提取。

## 位置

```
~/.dsh/sessions/<project-key>/<session-id>/session.jsonl.zstd
```

- `<project-key>` = 会话 cwd 的路径转换：`C:\Users\HMSJ\Documents\Hermes\Projects\deepseek-harness` → `--C-Users-HMSJ-Documents-Hermes-Projects-deepseek-harness--`
- 多个会话按目录时间排序，最新的在最上（`ls -lt`）
- 会话是 zstd 压缩的 jsonl（DSH 自己的 `SESSION_FORMAT_VERSION`，无跨版本兼容承诺——尽力解析 + 失败回退）

## zstd 解压（关键坑）

**不能用 `dctx.decompress(f.read())`**——会报 `could not determine content size in frame header`。必须流式解压：

```python
import zstandard
dctx = zstandard.ZstdDecompressor()
with open(path, "rb") as f:
    data = dctx.stream_reader(f).read()
lines = [json.loads(l) for l in data.decode("utf-8", errors="replace").splitlines() if l.strip()]
```

## 事件结构要点

- 每条是 `{type, timestamp, data, ...}`；`timestamp` 是 epoch **毫秒** int（>1e12 时 `/1000` 再转 datetime）
- `tool/call`：data 里有 `{name, arguments|input}`——arguments 可能是 JSON 字符串，要二次 parse
- `tool/result`：data 里是原始载荷（可能嵌套 message.content[].tool-result）
- `assistant/message`：data.message.content[].text 是推理全文
- `user/message`：注入的任务/上下文

## 统计 + 导出

- 事件类型计数：`collections.Counter(ev.get("type") for ev in lines)`——快速判断会话规模（tool/call 次数=读了多少次文件）
- 导出可读 markdown：按时间线输出 user/message、assistant/message（截断 4000 字符）、tool/call（工具名+参数 800 字符）、tool/result（截断 1500）——这个导出文件可直接 MEDIA: 交付给用户看完整会话过程

## 用户看到的「会话」

- headless 会话不进 web UI（web 界面只显示 web profile 会话）——用户说看不到时要解释这一点
- 用 `/api` 网关创建的任务会话（走 web 同款会话体系）会出现在 web UI 列表——这是「后台可见」的正解
