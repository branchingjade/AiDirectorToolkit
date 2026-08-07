# juben.pro 名作库：登录态分页全文抓取配方（2026-08-06 实测）

## 背景

juben.pro（华语剧本网）《剧本名作》栏目的剧本正文是**登录态 + 分页**的。实测《小偷家族》（2018，是枝裕和，中文整理稿）：WebBridge 继承登录态可读**全 8 页**正文（约 23368 字符 / 79 场），页面标注字数 20086。

## 关键事实

- 作品页 URL：`https://www.juben.pro/writing/{作品id}.html`（例：`8-17440.html`）
- 正文在「作品正文」tab 容器 `#tab1_div_1`（直接读 innerText 即可）
- 需先点「阅读剧本正文」（`.btn-readBodyContent`）展开正文
- **分页 URL 模式**：`https://www.juben.pro/writing/{作品id}-{页码N}-ccontent-hpdefault.html`，N = 2..末页；第 1 页 = 无页码 URL；页数/末页链接在 `.text-page-list`（href 可提取，如 `8-17440-8-ccontent-hpdefault.html`）
- **无登录 cookie 的 curl 直抓只返回前 ~4 场**（试读截断）。判断法：抓到的场景号停在 4 以内即被截断——必须 WebBridge 继承登录态
- 站内搜索：POST `/search/`（字段 `SearchKeywords` + `__RequestVerificationToken` 防伪 token），curl GET 不可用；WebBridge fill+click 最省事，搜索命中后作品链接在结果页 `<a>` 的 href 里

## 抓全循环（WebBridge，Python 脚本化）

```python
import json, time, urllib.request
BASE = "http://127.0.0.1:10086/command"
SESS = "kazoku-xxxx"   # 任务唯一 session 名

def wb(payload):
    req = urllib.request.Request(BASE, data=json.dumps(payload).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode('utf-8'))

def read_body():  # evaluate 字段名是 code（不是 expression）
    d = wb({"action":"evaluate",
            "args":{"code":"(() => { const el = document.getElementById('tab1_div_1'); return el ? el.innerText : ''; })()"},
            "session":SESS})
    return d.get('data',{}).get('value','')

def goto(url):
    wb({"action":"navigate","args":{"url":url},"session":SESS})
    time.sleep(2.5)

pages = {}
pages[1] = read_body()
for n in range(2, 9):                      # 末页数从 .text-page-list 链接拿
    goto(f"https://www.juben.pro/writing/8-17440-{n}-ccontent-hpdefault.html")
    pages[n] = read_body()
# 落盘 + 后续处理：每页头部重复「本剧本由…根据影片整理」声明，分析前正则去重
```

- WebBridge /command 细节：evaluate 字段名 `code`；中文参数（搜索词等）一律 write_file 写临时 JSON 文件体再 `curl --data-binary @file` 发送（Windows shell 内联中文会坏）
- 分页导航复用同一 session 的同一 tab 即可，无需新开

## 实测案例

| 作品 | 作品id | 登录态可读范围 | 备注 |
|---|---|---|---|
| 《小偷家族》(2018) | 8-17440 | 全 8 页（79 场） | 整理稿【剧本君的电影世界】根据影片整理；人名/地名本土化（"淞沪弹珠机房"、"柴田"氏），**非是枝裕和原剧本直译**，引用需诚实标注；IMSDb/Script Slug 无此片英文版 |
| 《小山回家》(1995) | 7-60644 | 全文 4 页免费 | 约 10643 字（此前会话记录） |
| 《你好，李焕英》 | — | 试读 9 场截断 | 页面标注全文 31990 字（此前会话记录） |

→ **试读深度因作品而异**：登录后可读深度不统一（有的全文、有的前 N 场），逐部实测，别一刀切。

## 陷阱

- 页面标注字数 ≠ 实测正文字数（标注 20086 vs 实测 23368，因整理稿含空白与重复头）
- 每页正文头部重复「本剧本由…根据影片整理」声明，统计前正则去重
- 场号重复/缺号是整理稿常见录入瑕疵（《小偷家族》53 号重复两次），统计时宽容处理并在报告中标注，不当异常
- 分析前保存原始全文存档（如 `_tmp/kazoku_full.txt`），报告引用它保证可复查
