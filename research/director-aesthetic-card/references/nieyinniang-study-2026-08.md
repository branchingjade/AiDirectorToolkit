# 聂隐娘（刺客聂隐娘）轮来源地图 2026-08

侯孝贤《刺客聂隐娘》(The Assassin, 2015) 单片研习轮。产出：研习报告/刺客聂隐娘_研习报告.md + 技法卡片源稿/刺客聂隐娘_技法卡片.md（6 张），校验脚本 scripts/verify_nieyinniang.py（129 条引文 0 MISS）。

## S# 来源编号对照（与产出文件共用）

| # | 存档（pages/） | 来源 | 关键内容 |
|---|---|---|---|
| S1 | hou_nieyinniang_wiki_raw.txt / _clean.txt | 英文维基 | 制作/评价/奖项/预算/拍摄地（Hubei/Inner Mongolia/东北） |
| S2 | hou_nieyinniang_zhwiki_raw.txt | 中文维基（全繁 API） | 剧情/角色表/风格段《印刻》访谈/取景地详单/青鸾自述/片名事件 |
| S3 | hou_taipingguangji_194.txt | 太平广记卷194《聂隐娘》（出《傳奇》） | 唐传奇原文全文（羊角匕首/磨镜少年/精精儿/空空儿） |
| S4 | hou_yiyuan_juan3.txt | 《异苑》卷三「鸞鳴」 | 青鸾舞镜典源原文（注意原文作"鸞"非"青鸞"） |
| S5 | hou_filmcomment_interview.txt | Film Comment 2015 侯孝贤访谈 | 武=cut&stop/青鸾自述/无排练/晨3000暮500鼓/35mm机内调色 |
| S6 | hou_soc_interview.txt | Senses of Cinema 2015 戛纳圆桌访谈 | 黑泽明参照/不开飞天/黑白开场=过去时/长镜论/海上花30镜/舒淇恐高 |
| S7 | hou_soc_cteq.txt | Senses of Cinema CTEQ 影评 | 幕帘窥视构图/黑白-彩色二元/台词转引 |
| S8 | hou_criterion_3754.txt | Criterion 侯孝贤访谈 | "bringing realism to the genre…creating limits is quite freeing" |
| S9 | hou_criterion_becoming.txt | Criterion Becoming Hou Hsiao-hsien | 沈从文影响/keep a distance and be cooler |
| S10 | hou_baike.txt | 百度百科（DDG 定位 id 16846105） | 原声带表（推广曲《一个人没有同类》龚琳娜） |
| S11-S20 | hou_nieyinniang_review_*.txt | 豆瓣长评 10 篇 | 7904 有用《几条线索》（田元氏暗线/凝视/唐诗风格）、隐娘的能量（一息之间）、腾讯专稿（改编分析/朱天文语）、时间线整理、光如一片水、青鸾对镜等 |
| S21 | hou_culturedarm.txt | culturedarm.com | 打斗 "relatively sparse"（定性） |
| S22 | hou_zhihu_q.txt | 知乎 30557033 | 讨论 |
| S23/S24 | hou_nieyinniang_reviews_list.json / hou_douban_suggest.json | 豆瓣 rexxar | 长评列表 total 2580；subject id 2303845 |

## 渠道实测（本轮新增/确认）

- **中文维基全繁原则**：action=raw 对"刺客聂隐娘"（全简）与"刺客聶隐娘"（聶繁+隐简混用）均报 Wikimedia Error；API `action=query&prop=revisions&rvprop=content&rvslots=main&format=json&formatversion=2` 对全繁"刺客聶隱娘"成功（24KB）——**繁简混用 = 假 404，必须逐字全繁**，且 raw 挂时 API 直取。
- **维基文库 API = 唐传奇/志怪典源通道**（国风志怪轮必用）：`zh.wikisource.org/w/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&format=json&formatversion=2&titles=<全繁标题>`。标题要先用 `action=query&list=search&srsearch=<词>` 拿真实标题——太平广记卷194 真实标题是"太平廣記/卷第194"（有"第"字，猜"卷194"会 MISSING）；《异苑》卷三"異苑/卷03"直接命中。青鸾舞镜典源《異苑·鸞鳴》原文由此一次拿到（比对用：片中台词是电影改编，典源原文作"鸞"、无"青"）。
- **Film Comment 直抓**：DDG html 经 r.jina.ai 搜 site 关键词 → uddg 解出 URL → r.jina.ai 直抓全文（22KB），无 Cloudflare 拦。侯孝贤武侠观一手金矿（"The _wu_ in _wuxia_ means both 'to cut' and 'to stop.'"）。
- **Senses of Cinema 站内搜索**：`sensesofcinema.com/?s=<片名+导演>` 一次命中 CTEQ 影评 + 2015 访谈（17KB 一手），比 DDG 稳。
- **Criterion posts/3754、8407 经 r.jina.ai 直抓成功**（live 可抓，无需 wayback）。
- **预设"打不起来"句未取证到**：多轮搜索无果 → 用一手等价原话替代（cut&stop / not in my blood / 硬造還不如不造），诚实声明逐条对照——预设只是线索，取证才是答案的又一实例。
- **打斗总时长分钟数未取证到**：DDG 英/中多轮无果 → 定性描述（S21 "relatively sparse" + S16 "一息之间"），正文明标"具体分钟数未取证到"。

## 并行轮共享 pages/ 坑（本轮实测）

任务断言"侯孝贤零存量"，开局 `ls pages | grep -iE 'hou|...'` 也确实为空；但抓取中途 pages/ 出现 30+ 个 `hou_beiqing_*`（悲情城市并行轮的侯孝贤存档：SoC 导演专条、Criterion essay、13 篇豆瓣长评）。**并行研习轮共享 pages/，中途会新增存档**——抓新前与写卡片前各重扫一次导演级前缀（`ls pages | grep <导演前缀>` 用导演名而非片名），发现的跨片导演存量可中途复用（本轮复用 Criterion 8407 Becoming Hou 作风格背景）。

## 校验

scripts/verify_nieyinniang.py：129 条引文 0 MISS。归一含：弯引号统一、全空白剥离、`[[X|Y]]`→Y 维基内链剥离（zhwiki raw 必做，本轮 3 条假 MISS 由此归零）。引文归属错挂 3 处（青鸾台词错挂 S20 实为 S12/S13、浴缸回忆错挂 S12 实为 S11）——**同主题多篇长评时，每条引文先 `grep -l` 定位真实文件再定 S#，别按标题关键词猜**。
