# 中国内容站 WebBridge 浏览器路线（2026-08-05 实测）

场景：百度百科/豆瓣/知乎需要**全文正文**时，curl 路线（403/壳/登录墙）拿不到 → 用 Kimi WebBridge（用户真实浏览器，localhost:10086），以下为三个高频站的具体姿势。均实测于《倩女幽魂》1987 调研。

## 百度百科

- **坑**：裸词条 URL `/item/<词条名>`（不带 id）可能落到**错误义项**——`/item/倩女幽魂` 实测跳转到 2011 翻拍版（叶伟信），而不是 1987 版。直接引用前必须核对演职员/剧情。
- **找精确词条**：导航 `https://baike.baidu.com/search/none?word=<URL编码>`，evaluate 收集结果页链接：
  ```js
  [...document.querySelectorAll('a')].map(a=>({t:a.innerText.trim(),h:a.href}))
    .filter(x=>x.h && x.h.includes('/item/'))
  ```
  标题自带括号消歧义（如 `倩女幽魂(1987年程小东执导的奇幻电影)`，id 10118475）。
- **取正文**：`document.querySelector('.J-lemma-content')` 兜底 `.lemma-main`，再 `.innerText`（长文先 slice 分段）。角色介绍/幕后制作/影片评价等子节都在同一容器里。

## 豆瓣电影

- **坑**：subject id 不能凭记忆猜——1297438 实测是《佩姬苏要出嫁》。
- **拿精确 id**：在豆瓣页面上下文直接 fetch（同源，免登录）：
  ```js
  fetch('https://movie.douban.com/j/subject_suggest?q='+encodeURIComponent('片名'))
    .then(r=>r.json()).then(d=>JSON.stringify(d.map(x=>({t:x.title,y:x.year,id:x.id}))))
  ```
- **读正文**：`https://movie.douban.com/subject/<id>/` 剧情简介/演职员/短评/影评**无需登录**即可读（WebBridge navigate + evaluate innerText）。

## 知乎

- **坑**：搜索页 `zhihu.com/search` 不渲染结果；`/api/v4/search_v3` 返回 `{"error":{"code":101,"message":"ZERR_NOT_LOGIN"}}`——未登录时搜索不可用。
- **绕过（免登录读回答）**：Bing 搜问题直链：
  1. 导航 `https://www.bing.com/search?q=site%3Azhihu.com%2Fquestion+<关键词>`
  2. evaluate 取 `[...document.querySelectorAll('#b_results h2 a')].map(a=>({t:a.innerText,h:a.href}))`
  3. 挑问题页 href（`zhihu.com/question/<id>`）直接导航——**问题页顶部回答免登录可渲染**（含长答全文）。
- **导航超时是常态**：知乎页常报 `navigate: page load timeout (30s)`，但 tab 实际已存活——忽略报错，`time.sleep(4-8)` 后 evaluate 即可。
- **长回答分段读**：`(() => { const t = document.body.innerText; return t.slice(起, 止); })()` 多段取，避免一次传输截断。
- 知乎搜索 API 仍有登录态时（用户在浏览器已登录）可直接 `fetch('/api/v4/search_v3?t=general&q=...&correction=1&offset=0&limit=8', {credentials:'include'})`。
- Jina Reader（r.jina.ai）仍是无浏览器时的兜底。

## 通用注意

- 每次 navigate/evaluate 请求体含中文时必须走**临时文件体**（Windows 下内联中文会变 `?`），见 kimi-webbridge 技能。
- 先导航拿 URL 再 evaluate 正文，抓回后核对页面标题/演职员，避免静默跳转到无关词条/翻拍版。
