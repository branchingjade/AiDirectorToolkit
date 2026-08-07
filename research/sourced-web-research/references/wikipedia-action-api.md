# 维基百科批量抓取：MediaWiki action API（2026-08-05 实测）

## 结论
- REST plaintext 端点 `https://en.wikipedia.org/api/rest_v1/page/plaintext/<Title>` 对全部测试标题返回 404（body `{"httpCode":404,...}`）——不要用。
- 可靠端点：`https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&explaintext=1&redirects=1&titles=<Title>`

## 可用脚本模式（python 标准库，无依赖）

```python
import json, time, urllib.parse, urllib.request

def fetch_plaintext(title, retries=5):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "extracts",
                                "explaintext": "1", "redirects": "1", "titles": title})
    url = "https://en.wikipedia.org/w/api.php?" + q
    hdr = {"User-Agent": "ResearchAgent/1.0 (research task)"}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=hdr)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            txt = ""
            for pid, p in data.get("query", {}).get("pages", {}).items():
                if "extract" in p:
                    txt = p["extract"]
            return txt  # 可能为空串：missing / 消歧义 / 重定向链断
        except Exception as e:  # 以 HTTP 429 Too Many Requests 为主
            time.sleep(5 * (attempt + 1))
    return None
```

- 请求间必须 sleep ~2s；实测第 13 个左右请求开始 429，退避 5/10/15s 后可恢复。
- 一次性抓 25+ 词条：统一用退避循环即可（实测 26 词条一轮跑完，中途 429 自动恢复）。

## 响应判读
- `"missing": ""` → 词条不存在。实例：`Shot list` 在英文维基不存在（镜头清单内容在 `Storyboard` 词条）。
- 正文开头 "X may refer to:" → 消歧义页。实例：`Cutaway (film)` → 正条 `Cutaway (filmmaking)`。
- `redirects=1` 自动跟随：`Sound_bridge` → `Split edit` 正文（L cut / J cut 内容），笔记中标注实际落点。
- 词条存在但 extract 为 0 字符 → 重定向链断或特殊页，换标题。

## 引用纪律
- 存档 `pages/pro-<关键词>.txt`，一份词条一个文件（纯文本，grep/read 友好）。
- 最终笔记的英文原文摘录必须从存档 grep 逐字复制，不凭记忆改写。
- 笔记中来源 URL 用规范词条 URL `https://en.wikipedia.org/wiki/<Title>`；重定向/替代条目标注实际落点。
