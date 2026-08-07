# 豆瓣长评全文/影评列表 rexxar API 通道（实测 2026-08-07 ·《空山灵雨》研习）

纯 curl 免浏览器，比 jina reader 更稳（结构化 JSON、无限流）。r.jina.ai 对部分豆瓣影评返回 403 时优先换此通道。

## 两个等价变体（都实测 200，按需选用）

| 变体 | URL | 差异 |
|---|---|---|
| A（空山灵雨轮） | `https://m.douban.com/rexxar/api/v2/review/<review_id>?api_version=2`，Referer `https://m.douban.com/movie/review/<review_id>/` | `author.name` **常为空** |
| B（龙门客栈轮） | `https://m.douban.com/rexxar/api/v2/review/<id>?ck=&for_mobile=1`，Referer `https://m.douban.com/movie/subject/<id>/` | `author.name`/`title`/`rating` 同包返回 |

两者 `content` 都是 HTML 全文。要署名引用影评 → 变体 B 或 interests 端点。

## 影评列表（拿 review ID + 热度 + 摘要）

```
GET https://m.douban.com/rexxar/api/v2/movie/<subject_id>/reviews?start=0&count=20&order_by=hot
Headers: User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1
         Referer: https://m.douban.com/movie/subject/<subject_id>/
```

→ JSON `reviews[].id / title / rating / abstract / useful_count`。先抓列表按热度排序再挑高价值影评逐篇抓全文——比「先搜影评标题再猜 review ID」可靠。

## 正文剥 HTML

```python
import re, html as h
text = re.sub(r"</p>", "\n\n", d["content"])   # 先段落换行，否则全文挤成一行
text = re.sub(r"<br\s*/?>", "\n", text)
text = re.sub(r"<[^>]+>", "", text)
text = h.unescape(text)
```

## 优先级与失败处理

1. **rexxar > jina**（结构化、无限流）；jina 作兜底
2. 账号注销/被删影评两通道都 403（实测 review/2613023）→ 换别的影评或标「未取证到」，不要反复重试
3. 批量抓取：execute_code 里循环 curl（`subprocess.run` 或 urllib），每篇 sleep ~1s，输出落盘 `pages/kongshan_review_<id>.json`，循环只 print 状态行
4. rexxar 搜索 API 需登录（`/rexxar/api/v2/search` 回 `need_login`）；找 subject ID 走 `m.douban.com/search?query=` 或 jina 读桌面搜索页

## 实测档案（2026-08-07 空山灵雨，subject 1301136）

- reviews 列表 19 条（含 209/111/76/60/55 有用等）
- 变体 A 全部 200：review/14512621（胡金铨访谈，7378 字）、4805579（朱熠《高处不胜寒》）、2598697（八卦数则）、7649240（丛二）、13603517（《关于〈空山灵雨〉中的几处疑思》）
- 2613023（《不立文字，直指人心》，账号已注销）→ 403
- 存档：film-suite-research/pages/kongshan_review_*.json
