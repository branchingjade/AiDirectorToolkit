# WebBridge 抓中文站要点（2026-08 实测）

情境：用 Kimi WebBridge（localhost:10086）在用户真实浏览器里抓百度百科 / 豆瓣 / 知乎 / 百度搜索等需登录态或反爬强的中文站，产出带来源 URL 的中文调研笔记。

## 铁律（多任务并行时尤甚）

1. **session 名必须唯一**（如 `research-<random-hex>`），一任务一个、全程不变。共享 session（如 `yanben`）会被并发任务劫持，出现串页：新开的 A 页 tab 里加载出 B 页、甚至无关的搜索页。发现 tab 内容对不上就换唯一 session 重开。
2. **navigate 后必须核对**：evaluate 返回 `location.href` + `document.title`，与预期不符（静默跳转 / 陈旧 tab 状态）→ 用 `newTab:true` 重开再试。静默跳转会产生"看似合理的错误内容"（如豆瓣跳到别的电影、百科跳到 404 错误页）。
3. **慢页重试**：evaluate 抛 `TypeError: Cannot read properties of null` = 页面未加载完。重试 3–5 次、间隔 ~2.5s，guard `document.readyState`，选择器回退 `document.body`。
4. **中文 URL 百分号编码**；Windows 上请求体走唯一命名 temp 文件（`curl.exe --data-binary @file`），中文不能内联。

## 站点配方

- **百度百科**：item ID 不能凭记忆猜（错 → 404 错误页）。先 navigate `/search?word=<编码>`，evaluate 收集 `/item/` 链接再进词条页。正文选择器 `.main-content`。词条信息密度高：剧情简介 / 角色介绍 / 幕后制作（造型、置景）/ 影片评价均有可直接引用的原文。
- **豆瓣**：subject ID 猜错**不会 404，而是静默跳到别的电影**（实测 1307394 是《千年女优》）。必须 `search.douban.com/movie/subject_search?search_text=<编码>` 定位。正文在 `#content`。影评 `/review/<id>/` 单页可 evaluate 全文；长影评常含逐字台词转录，是验证台词/细节的富矿。
- **知乎**：未登录时搜索页返回"未搜索到相关内容"空结果，别纠缠。验证台词/事实改用百度搜索。
- **百度搜索**：WebBridge navigate `baidu.com/s?wd=<编码>` 免 cookie 可用；结果摘要直接可引用；`link?url=` 重定向链接 navigate 后可解析到原文（百家号 / 豆瓣等）。

## 验证台词的方法

精确引语 → 百度搜索 → 摘要里出现多个来源的台词变体（如《青蛇》"放弃一千年道行"实际台词为"姐姐，你千年修行，为了一个许仙，值不值得？"等多个变体）→ 交叉确认多来源一致后再写进笔记；引语标注来源 URL（搜索页 URL 也可作来源）。
