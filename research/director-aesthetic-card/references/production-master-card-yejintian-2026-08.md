# 制作大师卡片 · 叶锦添轮（2026-08-09 实测，美术指导/服装设计大师）

产出：《叶锦添_制作大师卡片.md》→ `_work/制作大师研习-20260809/叶锦添/`，11 个编号来源 S1–S11，卡片 26.5KB。
对象特征：**华语美术/服装大师**（区别于声音/配乐轮）——《卧虎藏龙》奥斯卡最佳艺术指导+BAFTA 最佳服装设计、新东方主义美学体系、横跨电影/歌剧/芭蕾/装置。轮次任务是「制作大师研习-20260809」批派（同批还有张叔平、和田惠美）。

## 证据通道（美术/服装大师轮实测）

| 渠道 | 抓取结果 | 关键内容 |
|---|---|---|
| **WestEast Magazine**（westeastmag.wordpress.com）2009 一手访谈 | r.jina.ai 被 Cloudflare「Just a moment...」挑战页拦截（5.9KB 壳）；**直接 curl 原站成功** 25KB | 25 岁欧洲放逐/1993 转向舞台/"empty container"空容器论/"can't stand a stable world"/奥斯卡改变人生 |
| **NewsChina Magazine**（newschinamag.com）2024 一手访谈 | curl 直抓成功 22.9KB | "服装即叙事者"引语/李慕白"主角的消失"设计法/新东方主义定义权引语（reclaim the narrative definition）/Met《罗恩格林》300 套戏服/《诱僧》Klimt 金 |
| **新京报**（m.bjnews.com.cn）2025 深度专访 | 直抓成功 15.9KB | 虚无=无限空间/精神DNA 水杯论/封神朝歌超现实/去焦点性 |
| **新京报转载《叶锦添的创意美学》卧虎藏龙专章** | 直抓成功 13.4KB | **大师自己写的书章节经媒体转载 = 美术大师一手金矿**：五色场域（京灰/疆红/皖木原色/竹绿/窑黑）、玉娇龙六阶段造型、李慕白四套同剪裁大袍——整章细节级自述 |
| **每日经济新闻**（m.nbd.com.cn）2026-03 + **凤凰** h5.ifeng.com 长篇 | 直抓成功（7.1KB/17.4KB） | 笼罩感论/大明宫词"发型无一真实但氛围对"/物质只是精神的显影/夜宴婉后红青女白主题色 |
| **Guardian 2016** ng-interactive 图片专稿 | 文字极少但标题+lede 引语可抓 | "I change my style all the time"/新东方主义=向国际观众传达 |
| **SCMP 2024**（芭蕾《梁祝》） | 仅开头 ~2KB，正文 paywall 截断 | 如实声明截断，只用开头事实 |
| **artsmia.org**（明尼阿波利斯美术馆专稿） | Vercel 429，重试仍 429 | 诚实声明未取到 |
| **英文维基 Timmy Yip + 中文维基 葉錦添** | 双条直抓成功 | 奖项/生平/跨媒介清单；中文条目 URL 必须 quote 编码（久石让轮坑复用） |

## 新坑（写卡时踩到）

1. **任务预设奖项口径错误 → 以维基为准修正**：任务说「奥斯卡最佳艺术指导+服装设计」，实际是 **奥斯卡最佳艺术指导 + BAFTA 最佳服装设计**（enwiki 明确区分 "won an Academy Award for Best Art Direction. Yip also won a BAFTA award for the film's costume design"；2001 奥斯卡服装设计奖属《角斗士》Janty Yates）。媒体稿（NewsChina 引语）也有混称——**奖项类事实以维基/官方库为准，媒体引语混称在诚实声明里说明**。
2. **出生年份三口径并列**：维基 1967-12-22 / WestEast 2009 记 1965 / Asprey 展览稿记 b. 1961——沿用「数据双口径并列不强行统一」纪律，标题取维基口径、其余列诚实声明。
3. **r.jina.ai 也会被 Cloudflare 拦**（westeastmag 返回 challenge 壳）——**WordPress/博客类站先直接 curl 原站**，jina 是兜底不是第一顺位；判别：`<title>Just a moment...` 签名（与 Criterion 壳签名相同）。
4. **模板路径坑**：任务给的模板路径 `_knowledge/...` 实际目录是 `_知识库/...`（read_file 找不到）——用 terminal `find` 定位（search_files 对中文路径 IO error，已有坑记录再次印证）。
5. **引语验证的弯引号坑复用**："can't stand a stable world" 在存档里是 `can’t`（弯引号），grep "can't" 0 命中——验证短语按存档原字形写（`grep "stable world"` 命中）。

## 验证

20+ 条关键引语 grep 全部命中（含 五色场域/笼罩感/无我/去焦点/后现代卷轴画/主角的消失/past tense to the present tense 等中英引语）。卡片附录来源表 11 行，失败存档（artsmia 429 页、mtime 38 字节壳、asvoof 无文字页）如实登记。

## 对后续轮的可复用面

- 美术/服装大师轮渠道优先级：**大师自述书稿转载（媒体连载书章节）> 一手访谈（WestEast/NewsChina/新京报/每经）> 维基 > 展览稿**——华语美术大师的书稿（《叶锦添的创意美学》类）是整章级细节金矿，比碎片访谈强一个量级（同 Burtt 轮「书全文 > 二手转引」纪律）。
- 同批张叔平/和田惠美轮可复用：新京报/每经/凤凰的专访通道、奖项口径核对纪律、出生年份多口径处理。
