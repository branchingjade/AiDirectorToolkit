# 豆瓣电影数据抓取：rexxar 移动 API 配方（2026-08-07 重庆森林实战）

网页端双路线（curl JS 壳 / 浏览器 sec.douban.com 验证页）都挂时，**rexxar 移动 API 是免登录的第三通道**——纯 curl 即可拿到影评列表 + 长评全文。本次实测：`movie.douban.com/subject/1291999/`（重庆森林）4 篇长评全文直接到手，含 3000+ 有用数的拉片分析。

## 三步配方

### 1. 拿精确 subject id（勿凭记忆猜）

```bash
curl -s -m 30 -A "$UA" "https://movie.douban.com/j/subject_suggest?q=<URL编码片名>"
# 返回 JSON 数组：[{"title":"重庆森林","url":"https://movie.douban.com/subject/1291999/...","type":"movie","year":"1994","id":"1291999"}]
```

- 纯 curl 可用（无需 cookie、无需 WebBridge fetch，2026-08-07 实测）
- 同名词条多时按 title/year 挑选

### 2. 热门长评列表

```bash
UA_mobile="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
curl -s -m 40 -A "$UA_mobile" -H "Referer: https://m.douban.com/movie/subject/{id}/" \
  "https://m.douban.com/rexxar/api/v2/movie/{id}/reviews?start=0&count=8&sortby=hot"
```

- 返回 `{"start":0,"count":8,"total":3082,"reviews":[...]}`——**total 给全站影评总数**（可用性信号）
- 每条 review 含：id / title / useful_count（有用数，挑高赞用）/ rating.value / url（如 `movie.douban.com/review/5670197/`）
- ⚠️ 列表里 `content` 字段为空——**全文必须逐篇走第 3 步**
- 按有用数挑选目标长评：`useful_count` 上万的是热门；拉片/结构分析类长评标题常带「拉片」「结构」「两段」等词

### 3. 逐篇长评全文

```bash
curl -s -m 40 -A "$UA_mobile" -H "Referer: https://m.douban.com/movie/subject/{id}/" \
  "https://m.douban.com/rexxar/api/v2/review/{review_id}"
```

- 返回 JSON，`content` 字段即全文，**含 HTML 标签**（`<div id='content'>`、`<br>`）——提取时用 `re.sub(r'<[^>]+>',' ',c)` + `html.unescape()` 剥离
- `title` 字段=长评标题；`author.name` 可能为 null（不影响引用，引用时用标题+URL 即可）
- 有赞数/评分信息（rating.value）

## 陷阱与纪律

- **引用 URL 用网页版**（`https://movie.douban.com/review/{id}/`），不是 m.douban.com API 地址——读者可点开
- 影评是**个人观点**：解读类结论（如"林青霞不是杀手"）引用时标注「影评人观点，非官方说法」；影评里转述的台词可能与原声有出入，重要台词交叉核验 Wikiquote/维基
- 影评转述的第三方评价（如昆汀语录）属二手转述，标注「转引自豆瓣影评，未核验原始访谈」
- 存档：列表存 `chungking_rexxar.json`，逐篇存 `chungking_review_{id}.json`，剥 HTML 后合并存 `chungking_reviews_all.txt` 供 grep
- 若 rexxar 也返回空/验证页（环境变化），回退 zh.wikipedia 同名词条（评价段信息密度高）并如实标注

## 本技能其他文件的关联修正提示

- `references/china-sites-webbridge.md` 里的「豆瓣 subject_suggest 需 WebBridge」已被本次纯 curl 实测取代（2026-08-07）
- `references/director-aesthetics-card.md` 的「豆瓣检索三形态失败（SPA/搜索页/API 均需登录）」结论过时——那是网页 API 形态；**rexxar 移动端点免登录**。下次编辑该文件时请同步修正
