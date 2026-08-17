# 北野武轮（2026-08-08）取证地图

布局研习轮子代理产出：《北野武_导演美学卡片.md》+《北野武_手法体系深化.md》（`_work/布局研习-20260808/北野武/`）。工作目录 pages/ 18 个存档。

## 来源编号表（S1–S9）

| 编号 | 存档文件 | 来源 | 关键内容 |
|---|---|---|---|
| S1 | kitano_wiki_en.wikitext | 英文维基·Takeshi Kitano 主条目 | 风格段（deadpan/near-stasis/长镜/省略剪辑）、作品表、金狮奖、AV Club/Electric Sheep 转引 |
| S2 | kitano_wiki_zh.wikitext | 中文维基·北野武主条目 | 「作品特色」三段（快速暴力画面/海边镜头/停止式镜头）、中文片名对照 |
| S3 | kitano_wiki_hanabi.wikitext | 英文维基·Hana-bi 词条 | 结尾风筝+画外枪声、堀部点彩画=北野武自绘、Ebert 评语、预算 230 万美元 |
| S4 | kitano_soc_greatdirectors.txt | SoC Great Directors 专条（**作者 Bob Davis**，Issue 27, 2003） | 否定式风格；ASL 13.5/14.5/12s；音乐 cue 数据；Violence by contrast；省略剪辑；尾巴镜头；回避正反打；Film Comment/Rayns/Dafoe 转引；"I am the Master!" |
| S5 | kitano_soc_hanabi.txt | SoC·Edwards《Never Yielding Entirely Into Art》(Issue 10, 2000) | "explosive calm"、碎片化叙事、身体在场/右脸麻痹、车祸日期 1994-08-02 |
| S6 | kitano_soc_sonatine.txt | SoC·Dan Harper《Kitano Takeshi's Sonatine》(Issue 10, 2000) | "closed space"引题、沙滩游戏、games rehearsed the outcome、"granitic" |
| S7 | kitano_soc_scene.txt | SoC·Andrew Saunders《A Scene at the Sea: Reflections》 | 去冲突化叙事、安静空间、聋哑主角 |
| S8 | kitano_midnighteye_2003.txt | Midnight Eye·Tom Mes 访谈（2003-11-05，巴黎群访）——**本轮唯一一手** | 暴力观（When I show it, it hurts）、剑vs枪、CGI 缓冲、artisan 论、女性角色论、踢踏舞/kabuki、黑泽明 winks |
| S9 | kitano_douban_hanabi_1069269_browser.txt | 豆瓣长评 1069269（2006，经浏览器抓取） | 中文影迷视角：结构晦涩、画作、孤独主题 |

## 本轮新通道/新坑（已入 SKILL.md / web-fetch-fallbacks）

1. **r.jina.ai 全域名 403**（连 example.com 测试也 403）→ 判为 jina 侧限流，切浏览器通道。→ 已入 web-fetch-fallbacks §2b。
2. **豆瓣长评浏览器直抓**：`browser_navigate movie.douban.com/review/<id>/` + `browser_console` 提取 `#link-report` innerText，免登录取全文（正文不在 snapshot 里，必须 console 取）。→ 已入 web-fetch-fallbacks §2b。
3. **Wayback availability API 空快照**：豆瓣/卫报 4 个 URL 全 `"archived_snapshots": {}`；卫报 curl 403 无快照 → 如实标「未取证到」。→ 已入 web-fetch-fallbacks §2b。
4. **SoC 专条作者 byline 丢失**：txt 无署名，`grep -oE 'author/[a-z-]+/'` HTML 命中 `author/bob-davis/`。→ 已入 SKILL.md 步骤 2。
5. **引文归属错挂实例**：'unconscious suicide attempt' 被引 S3 MISS、S1/S5 HIT——修正来源标注后引文保留（expect_keys 实战）。→ 已入 SKILL.md 校验纪律。
6. **vs 表格单元格取证**：黑泽明侧三格无硬数据，补「⚠️ 对照性概述，本轮未直接取证」标注。→ 已入 SKILL.md 深化变体纪律。
7. **web_extract 后端为 search-only（ddgs）不可用** → 全程 python urllib 批量下载 + HTML→txt 正则清洗 + grep 验证（63 条引文，4 处初始 MISS 全为格式/归属问题，修正后 0 MISS）。

## 未取证到（写入卡片 §8）

- Criterion essay（Criterion Collection 未发行北野武作品，Reddit r/criterion 侧证）
- Guardian 2010 Steve Rose 访谈（403 + 无 wayback 快照）
- 豆瓣其余长评、中文一手访谈
- SoC 2000 Kitano 专题《菊次郎的夏天》两篇（Gardner/Saunders）
- 《极恶非道》三部曲逐片风格分析（仅访谈转引+维基概述）；《首》(2023) 深度影评

## 本导演取证要点备忘（供后续轮复用）

- **一手通道**：Midnight Eye（Tom Mes 日本电影站）= 日本导演一手访谈首选站（今敏轮同结论），curl 带 UA 直抓可取全文；北野武 2003 Zatoichi 时期访谈含暴力观原话。
- **量化数据**：ASL（Boiling Point 13.5s / A Scene at the Sea 14.5s / Sonatine 12s）与音乐 cue 数据（Violent Cop 3 cues×12 次）出自 SoC 专条脚注（引 Barry Salt/Bordwell），非官方——引用已标。
- **风格演变链**：暴力省略→突爆→画外化（Hana-bi 结尾）→CGI 缓冲（Zatoichi）→冷血群像（Outrage）；摄影机钉死→解锁（Kids Return）→z 轴（Hana-bi）→过度运动（Dolls，双口径）→节奏化（Zatoichi）。
