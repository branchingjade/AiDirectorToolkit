# 《喋血双雄》(The Killer, 1989) 单片研习轮来源地图（第十七轮 2026-08）

产出：`研习报告/喋血双雄_研习报告.md` + `技法卡片源稿/喋血双雄_技法卡片.md`（吴宇森补代表作研习：双雄情义/暴力美学定型作）。
编号体系：单片研习独立 [研S1]-[研S15] + 「对应主卡」列映射导演卡片存档 [卡A]-[卡I]（沿用三峡好人轮先例；吴宇森主卡片无 S#，映射列登记存档文件名）。

## 存量盘点结果

- 吴宇森导演轮存量 `woo_*` 齐全：英维《喋血双雄》词条（woo_wiki_The_Killer_(1989_film).txt，59KB raw 已含 Plot/Themes/Production/Music/Reception/Legacy 全段）+ Salon/Guardian/BFI/Vulture/NYT/ScreenAnarchy 访谈存档——**本轮主力证据 60% 来自存量复用，仅补抓 4 类新源**。
- `woo_criterion_killer.txt` 是 "Shop All Films" 壳页（猜错 film ID 的失败留档，与技能已知坑一致）——真实 essay URL 在英维 External links 段（见下）。

## 新抓存档对照（研S#）

| 编号 | 存档 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | woo_criterion_1062_killer_jina.txt | Criterion essay by David Chute（CF 壳→r.jina.ai 兜底） | "Chinese blood operas/arias" 暴力=咏叹调论、"The only person who really knows me turns out to be a cop!"、"assassin or best friend"、双雄关系定调 |
| 研S2 | woo_zhwiki_diexue.txt | 中维 raw（**真实条目名=简体「喋血双雄 (1989年电影)」**） | 剧情/演员表（含粤语配音列）/制作（28天赤柱+36天教堂+口琴结局）/创作源流（独行杀手/雙雄喋血記/地老天荒不了情）/歌曲/奖项/影响 |
| 研S3 | woo_baike_diexue_dvd.txt | 百度百科「喋血双雄（DVD 简装版）」变体词条 | "教堂=杀手殿堂与杀戮战场"、白鸽/圣母像/烛光、"一部哲学式的电影，表达了我心中的正义" 导演自述转引 |
| 研S4 | woo_diexue_reviews.json | 豆瓣 reviews 列表（subject 1296519） | 20 条热门长评标题/有用数 |
| 研S5-14 | woo_diexue_review_*.txt | 豆瓣长评 10 篇全文 | 1099434（447 有用台词金矿：念旧句/朋友句/四哥承诺句/曾爷台词/希腊悲剧论）、3242483（85 有用四哥临终对白全段）、7547913（24 有用逐场拉片：开场教堂/夜总会双枪/龙舟狙击/半山腰对白/口琴结局）、14252513（39 有用 111min vs 124min 版本考据）等 |
| 研S15 | woo_diexue_comments.json | 豆瓣短评（**API 404 traversal_error，失败留档**） | comments 端点对 subject 1296519 不可用——短评未取到，不硬凑 |

## 本轮新坑实例（已回写 SKILL.md）

1. **中维条目名可能是简体**（与"必须全繁"规则相反）：港片《喋血双雄》真实条目「喋血双雄 (1989年电影)」简体；猜繁体「喋血雙雄」连环 Wikimedia Error。解法：`action=query&titles=<候选>&redirects=1&format=json` 探测真实标题；URL 编码用 `urllib.parse.quote` 别手写 %XX（喋=U+56D4，两次错打成 喷/喔）。
2. **{{douban}} 模板只有 title 没 id**：raw 里 `{{douban|title=喋血双雄}}` 无数字 → 抓中维渲染页 HTML grep `douban\.com/subject/[0-9]+` 一步拿 id（1296519）。
3. **百度百科电影主词条整体 404**：`item/喋血双雄`、`/1541`、`/61733` 全挂 → DDG site: 搜出变体词条「DVD 简装版」/15179296，仍含剧情摘要+导演自述转引，可用但标注权威性低于电影词条。
4. **Criterion essay URL = 英维 External links 段直接列出**：`grep -o 'criterion.com/current/posts/[0-9]*-[a-z0-9-]*'` 英维 raw 一次命中 posts/1062-the-killer（附作者名 David Chute）——零成本第一顺位，优先于 films/<id> 页与 DDG site:。
5. **繁简映射表缺字 → 校验短语直接改用存档原文繁体**：str.maketrans 表漏 槍/雙/導演/屆 等字致 7 条假 MISS；中维 raw 存档本身是繁体，短语侧保留原文（「因為見到阿莊…」）逐字直比比无限补表更快。

## 定稿校验记录

- 103 条引文（研习报告+技法卡片正文）0 MISS 定稿；脚本 `pages/_verify_diexue.py`（v3：递归剥嵌套 [[A|B]] 链接 + 繁体短语直比 + 全角括号归一 + 大小写兜底）。
- 中文台词双稿并存处并录标注（「念旧」句两版、「朋友」句两版），未强行统一。
- 预设验证：「暴力芭蕾」英文侧铁证=RT consensus "balletic violence" + Chute "blood ballets/Chinese blood operas"；「白鸽首用」双源（英维+Salon 原话）；「吴宇森自称最完美」仅豆瓣标题转述→传闻级处理。

## 未取证清单

- 剧本原文（无公开剧本）；百度百科电影主词条（404）；豆瓣短评（API 404）；「吴宇森自称最完美」导演原话（仅影评标题转述）。
