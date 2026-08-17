# 日文歌词站抓取配方（2026-08 实测有效）

适用：抓取日本动漫/流行歌曲日文歌词原文。web_extract 不可用时用 urllib/requests 直抓（带浏览器 UA）。

## 首选站 1：UtaTen（utaten.com）

**搜索（真实可用）**：
```
GET https://utaten.com/lyric/search?title=<歌名>&artist_name=<歌手>&sort=score
```
注意：`/search?q=` 端点会忽略 q 参数（永远返回最新歌单），是死路。

**URL 发现捷径**：
- web_search `site:utaten.com <歌手>` 或 `site:utaten.com <专辑名>` → 专辑页 `https://utaten.com/album/index/<id>`（如红莲华专辑 id=5019、いきものがかり精选 id=50369）
- 专辑页 HTML 里全部歌曲链接为 `/lyric/<id>/` 模式，正则 `href="(/lyric/[a-z0-9]+/)"` 直接提取
- 歌词页：`https://utaten.com/lyric/<id>/`
- **搜索端点直抓（2026-08-14 实测有效）**：web_search 超时/无结果时，直接用 urllib 抓 `https://utaten.com/lyric/search?title=<URL编码歌名>&artist_name=<URL编码歌手>&sort=score`，用同一正则 `href="(/lyric/[a-z0-9]+/)"` 提取歌词页链接。实测：残酷な天使のテーゼ+高橋洋子 → ja00003143；crossing field+LiSA → jb51210097（日文原版）、yc15030207（English ver.）。**同曲多版本并存**（original ver./movie ver./English ver.），抓取后核对页面 `<title>` 确认版本并标注。

**歌词提取**（带 ruby 注音，必须按序处理）：
```
<div class="lyricBody"> → <div class="hiragana"> 内：
<span class="ruby"><span class="rb">漢字</span><span class="rt">よみ</span></span>
```
处理步骤：
1. 取 `<div class="hiragana"[^>]*>(.*?)</div>\s*</div>`（re.S）
2. 删 `<span class="rt">.*?</span>`（注音，否则污染原文）
3. `<br>` → `\n`；删剩余标签；html.unescape；折叠空格/空行

## 首选站 2：j-lyric.net

**歌词页**：`https://j-lyric.net/artist/<artistid>/l<songid>.html`
- 歌词容器是 `<p id="Lyric">`（不是 div！），`<br>` 分行，UTF-8
- URL 发现：web_search `site:j-lyric.net <曲名> <歌手>`（实测有效，残酷天使/STYX HELIX/君知物语均一次命中）
- 站内搜索 search.php（ex=on&ct=2&ca=2&cl=2&ops=1&key=…）GET/POST 均返回空——不要依赖

## 通用编码回退链

```
for enc in ("utf-8", "shift_jis", "euc-jp", "big5"):
    try: return raw.decode(enc)
```
UA 头必须带：`Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36`

## 备选站实测（2026-08，失败记录，别浪费时间）

- uta-net.com 搜索路径 404
- genius.com API 403（反爬）
- mojim.com SSL handshake 超时
- lyrsense.com 猜测路径 404
- html.duckduckgo.com 搜索返回空
- r.jina.ai 无 key 403

策略：首选站失败 → 换 web_search 找 UtaTen/j-lyric 页面 → 仍无则标注「未验证」，不编造。

## 其他经验

- 歌名先验证存在性（web_search 多引擎），查无此歌就替换同类经典并说明
- 抓到原文立即存 `lyrics_raw/<歌名>.txt` 备份，研习卡中标注来源 URL + 抓取日期
- utaten 收录同一首歌多个版本（movie ver. / original ver.），抓取时注意标注版本
