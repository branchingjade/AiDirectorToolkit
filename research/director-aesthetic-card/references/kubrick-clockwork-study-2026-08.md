# 发条橙（A Clockwork Orange, 1971）单片研习轮来源地图（第二十轮）

产出：
- `研习报告/发条橙_研习报告.md`（27.8KB，9 节：档案/创作脉络/主题取证/视听技法/表演/改编删节/争议批评/来源清单/诚实声明）
- `技法卡片源稿/发条橙_技法卡片.md`（16.6KB，6 张：奶吧对称开场/雨中曲强奸戏/贝九三次易主/神父选择宣言/Ludovico 治疗/结尾 I was cured）
- 编号：独立 [研S1-研S19] + 映射主卡 [W-CO]/[W-K]（主卡片 [W-X] 字母代号体系沿用，不另起炉灶）

## 存档对照（pages/kubrick_co_* + 存量）

| 编号 | 存档 | 来源 | 要点 |
|---|---|---|---|
| 研S1 | kubrick_clockwork_wiki.txt | enwiki 片条目（存量复用，35.8KB 完整） | 主题/删节/Production（广角、坠机、角膜伤）/Music（罗西尼>贝多芬）/Reception/撤片 |
| 研S2 | kubrick_wiki.txt | enwiki 导演条目（存量复用） | Baxter 1.66:1「rigorously symmetrical framing」引文 L80、McDowell 排练引文 L163 |
| 研S3 | kubrick_co_zhwiki_raw.txt | 中维「發條橘子 (電影)」API revisions（新抓） | 档案/剧情（「我已經痊癒了。」）/奖项/136 分钟 |
| 研S4 | kubrick_co_zhwiki_novel.txt | 中维「發條橘子」（小说条目，新抓） | 「刪減片段」段（21 章删节史）/小说原型（伯吉斯妻子遭轮奸） |
| 研S5 | kubrick_co_script_springfield.txt | springfield 对白转录稿 59KB（新抓） | 开场独白/雨中曲两处/神父善与选择/演示会 Choice 质问/Ludovico 场景/结尾 L2412 |
| 研S6 | kubrick_co_baike_body.txt | 百度百科「发条橙」经 jina（新抓） | 实为小说词条（三部分×七章/第 21 章成长结局） |
| 研S7-S16 | kubrick_co_review_*.txt | 豆瓣长评 10 篇 rexxar（新抓） | 1098754(6852 有用)/3423525(3837)/1159982(495)/13908755 厌女(705)/3114745 福柯(432)/4971351 后现代(125, 对称构图证据)/7943435 音乐声画(73, 贝九六次)等 |
| 研S17 | kubrick_co_review_10428064.txt | 凯尔批判译文（新抓） | 仅译者按，正文以图片发布→正文未取证 |
| 研S18 | kubrick_co_imsdb.html / kubrick_co_slug.html | IMSDb / Script Slug（新抓） | 均无剧本正文（坑见下） |
| 研S19 | kubrick_co_suggest.json / kubrick_co_reviews.json | 豆瓣 suggest+reviews（新抓） | subject id=1292233、total 1350 |

## 本轮新坑/配方

1. **IMSDb 条目页≠剧本**：`imsdb.com/scripts/Clockwork-Orange,-A.html` 回 ~8KB 条目页（有片名/编剧行）但无 `<td class="scrtext">`——先 grep 'scrtext' 确认正文再提取，标题页不算剧本。
2. **Script Slug 空壳**：`scriptslug.com/script/clockwork-orange-1971` 回 130KB 页（JS pre-fetch 配置+导航，`<title>` 空、无 script 容器 div）——页面体积≠内容证据。
3. **springfield slug 探测**：`movie_script.php?movie=clockwork-orange` 与 `clockwork-orange-1971` 都回通用壳页（title="Movie Scripts | SS"），正确 slug 是 **`a-clockwork-orange`（带冠词 a-）**；以 `<title>` 含片名验证 slug，转录稿正文在最后一个 `scrolling-script-container` div（沿用卢布廖夫轮配方）。
4. **中维裸片名重定向实体坑**：「发条橙」→「發條橘子」=**小说条目**（Infobox Book），电影条目在「發條橘子 (電影)」（Infobox Film）；改编片先探测重定向目标再查 (電影) 后缀。
5. **百度百科同名词条=小说词条**：`item/发条橙` 正文按小说写（内容简介/艺术特色/第 21 章结局），作小说层证据用、不作电影条目。
6. **转录稿=行号级证据兜底成功案例**：59KB 全对白（含 Singin' in the Rain 整段歌词、神父 "Goodness is chosen" 题眼台词），标「转录稿非剧本」用；结尾 I was cured 三源互证（转录稿 L2412/英维剧情段/中维「我已經痊癒了」）。

## 预设验证

- 古典乐错位 ✓（enwiki Music 段：罗西尼>贝多芬；贝九六次影迷统计 7943435「影迷统计非官方」标注）
- 对称构图 ✓（Baxter「rigorously symmetrical framing」[研S2] + 豆瓣 4971351 奶吧/部长演示会逐镜证据）
- 「暴力芭蕾」术语未取证 ✗ → 成片词汇 ultra-violence + 影迷用语「暴力美学」替代，写入诚实声明
- 「小说最后一章删节」✓ 三源互证（研S1 Comparison/Novelist's response + 研S4 刪減片段 + 研S9 再吮发条橙）

## 校验

90 条引文 0 MISS（脚本 `pages/verify_co_quotes.py`）。测试短语修正 3 处：遠→远（测试短语混排繁简，存档全简）、矫正是→矫正（笔误）、137→136（测试错值）；norm 管道加了迭代维基链接剥壳 `while "[[" in s: re.sub(r"\[\[([^\[\]]*)\]\]", lambda m: m.group(1).split("|")[-1], s)`（与校验坑 ⑦/㊱ 同族，本轮中文维基 raw 的 `[[安東尼·伯吉斯]]` 内链即由此修复）。
