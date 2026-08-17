# Sonnenfeld 研习轮记录（2026-08-09B 轮）· 调色师 Stefan Sonnenfeld

取证式人物卡片（制作大师卡片）完整实战记录。产出物：`_work/制作大师研习-20260809B/Sonnenfeld/Sonnenfeld_制作大师卡片.md` + `pages/` 18 份存档。

## 本类任务可用 URL 模板（验证过可抓）
- 维基主条目：`https://r.jina.ai/https://en.wikipedia.org/wiki/<Person>`（人名条目 200KB+，filmography 表在文件后部，用 grep 行号定位）
- IMDb fullcredits：`https://r.jina.ai/https://www.imdb.com/title/<ttid>/fullcredits`（角色行格式：姓名行 + 角色行相邻，用 `grep -B2 -A2 <姓名>` 确认角色）
- 公司官网 artist bio / news 页：`https://r.jina.ai/https://www.company3.com/artists/<slug>/`（cookie 条款占前半，正文从 `# <标题>` 行开始）
- YouTube 视频页：`https://r.jina.ai/https://www.youtube.com/watch?v=<id>`（description 段常内嵌长引语，`grep -n "## Description"` 后取上下文）
- LBBOnline 访谈全文：`https://r.jina.ai/https://lbbonline.com/news/5-minutes-with-<slug>`

## IMDb 署名查证案例（核心教训）
- 简报称 Sonnenfeld 调色《银翼杀手2049》（tt1856101）→ fullcredits 查证：`supervising digital colorist: Mitch Paulson`、`digital intermediate producer (EFilm): Robert E. Phillips`、`colorist: dailies: Matt Wallach`，**全文无 Sonnenfeld / Company 3** → 卡片按查证结果写，加查证框 + 诚实声明条目。
- 正向验证：TFA（tt2488496）→ `digital intermediate executive producer: Company 3 / senior colorist` = Stefan Sonnenfeld ✓。
- 维基交叉验证：BR2049 维基全文无调色师署名（无信息≠无人做）；TFA 维基无 Company 3 信息 → 一律以 IMDb 为准。

## 已验证引语（存于 pages/ 对应文件，可直接引用）
- LBB 2025 全文（lbbonline_5min.txt）："heightened version of reality"；"spend five hours meticulously analysing the colour of a can"；DI 革命："People like Tony would fight the studios to say, 'No, I'm not working at this traditional place. I want to work with this dude'"；"separation anxiety"；"What's perfect? Red, green, blue…"；AI："AI doesn't replace the high-end creativity in anything"。
- Dolby Creator Talks 200 期（dolby_creator_talks_youtube.txt 简介）：Michael Mann "talk through emotions…I'm sort of interpreting that, in a color way" 长引语。
- Company 3《神奇女侠》纪实（company3_wonder_woman.txt）："talking about the color over a year ago"；"great contrast and skin tones"；"all in the service of what she envisioned"。
- 官网传记（company3_artist_bio.txt）："first colorist inducted into the Academy of Motion Picture Arts and Sciences (AMPAS)"。
- 论坛转述（lowepost_hullfish_quotes.txt，二手）："keeps it simple and has great taste"；"you can't steal my taste" 轶事（无一手出处，须标注）。

## 关键事实（写卡片时用的骨架）
- Company 3：1997 年 Santa Monica 创立（Sonnenfeld+Mike Pethel+Noel Castley-Wright，4MC 旗下）→ 2000 Liberty Media → 2010 Deluxe → 2020 Framestore/FC3。
- HPA 奖：《300》2007 最佳故事片调色；Pepsi "Pass" 2009 商业；《爱丽丝梦游仙境》2010 最佳 DI。
- 代表作品谱系：Pirates of the Caribbean (2003 起)、Transformers 系列、300、Watchmen、Wonder Woman、TFA/TROS、Top Gun: Maverick、The White Lotus、Michael (2026)。

## 遇到的坑（本类任务通用）
- 弯引号使 grep 整句假失败 → 用不含引号片段或 `.` 通配符（如 "It.s my third movie"）。
- Wookieepedia/Fandom 页经 r.jina.ai 只回导航，正文不渲染 → 标「未取到正文」。
- Art of the Grade 播客站域名已停用（artofthegrade.com / theartofthegrade.com）→ 标「未取到」。
- company3.com/about/ 会被重定向到无关影片页 → 抓前先看 URL slug 是否精确。
- 任务简报的影片归属可能错（BR2049 案例）→ 署名查证步骤不可省。
