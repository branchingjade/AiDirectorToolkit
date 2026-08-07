# 卓别林深化轮 2026-08 来源地图（手法体系深化·无主卡片变体）

产出：《卓别林_手法体系深化.md》（技法卡片源稿/，46KB）；校验脚本 `_verify_chaplin_deep.py`（100 引文 0 MISS）。

## 轮次定性

- **无主卡片变体第七例**（李安/昆汀/宫崎骏/陈凯歌/谢晋同型）：卓别林无《导演美学卡片》主卡片 → 自建 [S1]-[S11]（编号=存档文件名前缀），并行轮存档用 [卡X] 前缀。
- **零存量开局 + 并行轮中途落盘复用**：开局 `ls pages/ | grep chaplin` 为空；抓取中途中出现并行城市之光轮 15 档存档（chaplin_citylights_*：Criterion essay/Ebert/百度百科/中维/豆瓣长评 10 篇）→ 立即复用为 [卡X] 证据（Criterion Giddins essay 直接成为悲悯线主证据），不重复抓。⚠️ 深化轮开局 grep 空 ≠ 全程无存量，可能是并行轮尚未开始抓——中途与定稿前各重扫一次。
- **任务指定转引资产处置**：①《城市之光_技法卡片》定稿前落盘 → 按 ㊴ 三阶段补 [卡城市之光卡片] 转引链（正文注脚+附录登记+诚实声明升级），校验目标改为卡片本体（㊿③）；②《摩登时代_技法卡片》《喜剧题材密码.md》不存在 → find 确认后诚实声明，证据以英维条目+豆瓣长评直接取证。

## 存档编号表（pages/）

| # | 文件 | 内容 |
|---|---|---|
| S1 | chaplin_main_wiki.txt | 英维主条目：Method 段（Karno 悲悯打闹起源/Stan Laurel 引文/53 takes）、Style and themes 段（"lifting his hat to the tree"/"serious demeanour"/1925 dignity 原话/tragedy-ridicule Rquote/社会评论演变链/哑剧大师 Rquote）、Modern Times 节（satire on industrial life/15 年政治化）、Great Dictator 节（Hitler must be laughed at/五分钟演讲）、Legacy（Sight & Sound 排名） |
| S2 | chaplin_kid_wiki.txt | 弃婴剧情/孤儿纸条/Vance「perfect blend of comedy and drama」/芝加哥媒体悲喜双拳评语（**It's right glove...** 转录错字按 [原文如此] 直录） |
| S3 | chaplin_citylights_wiki.txt | give the talkies three years/结尾先构思/everything I do is a dance/38.8:1 拍摄比/Agee 评语/配乐首创 |
| S4 | chaplin_moderntimes_wiki.txt | 甘地对话/1934 talkie 尝试后放弃/18fps silent speed/gibberish 歌/Vance valedictory/first overtly political-themed film/戈培尔禁映 |
| S5 | chaplin_dictator_wiki.txt | he's the madman I'm the comic/As Hitler I could harangue...silent/Vance「most self-consciously political work and the cinema's first important satire」/Insdorf 双角反转/Schatz/Shindler/Telotte 三连 |
| S6 | chaplin_zhwiki_main.txt | 基石「粗暴、粗俗而残忍」/艾萨奈温和浪漫化/《银行》首次悲剧结局/流浪汉服装反差自传引文 |
| S7 | chaplin_ebert_citylights.txt | 五元素总括/dig at dialogue/「Speech was not how the Tramp really expressed himself」/Keaton 对比/1972 威尼斯 |
| S8 | chaplin_ebert_moderntimes.txt | **「The voices in the movie are channeled through other media」=声音媒介化核心证据**/电视+唱片/唯一同步声=唱歌侍者 |
| S9 | chaplin_ebert_dictator.txt | first talking picture/comedy followed by an editorial/He never played a little man with a mustache again/150 万自有资金 |
| S10 | chaplin_wikiquote_raw.txt | Life is a tragedy in close-up, comedy in long-shot（卫报讣告）/clown far higher plane than politician/大独裁者演讲节选/Disney 米老鼠 |
| S11 | chaplin_quoteinvestigator_comedy.txt | **QI 考证「Comedy Is a Serious Thing」=Garrick 1834/Colman 1775，非卓别林原话** |

[卡X]：卡城市之光Criterion（Giddins essay 全文）/卡城市之光百科（342 遍镜头 0.95% 采用率）/卡城市之光中维/卡城市之光Ebert（与 S7 同文冗余）/卡豆瓣·Delorme（《电影手册》585 期《惯性之力》机翻，节拍器喜剧）/卡豆瓣·3381502（906 有用雕像讽刺）/卡豆瓣·8684540（结尾触觉）/卡豆瓣·7543948（小人物悲悯）/卡城市之光卡片（定稿前落盘的技法卡片，三层凝视）。

## 三新坑（2026-08 卓别林轮）

1. **预设名言归属证伪→Quote Investigator 通道**：任务预设「喜剧是严肃的事情」全部存档 0 命中。DDG 直连空壳 → 经 r.jina.ai 代理 DDG 搜 `Chaplin "comedy is a serious"` 命中 quoteinvestigator.com/2020/05/17/comedy-serious/ 专文（2020-05-17），全文确认源头=David Garrick（1834 Campbell 传记转述「but comedy is a serious thing, so don't try it yet」）+ George Colman（1775「to write a Comedy is a serious matter」），**与卓别林无关**。处置：等价一手引文替代（tragedy stimulates ridicule [S1] + "Life is a tragedy when seen in close-up, but a comedy in long-shot" [S10]），诚实声明注明 QI 边界（未覆盖卓别林口头表述可能）。QI 站专事名人名言溯源，含 "Dying is easy; comedy is hard" 等同类考证——导演名言归属存疑时的第一通道。
2. **Ebert slug 按重映年份命名**：`great-movie-modern-times-1936` 404，正确 slug=`modern-times-1972`（Ebert 评 1972 芝加哥重映）。发现路径=Ebert《City Lights》Great Movies 影评正文内链（reviews/modern-times-1972）。Ebert slug 404 排查顺序：同作者其他影评正文内链 → 重映年变体 → CDX/wayback。
3. **校验脚本实现级**：① load_archives 只 glob .txt 漏掉全部豆瓣长评 .json（中文引文集体假 MISS）→ 并列加载 .json（json.load 取 content 字段、剥标签、html.unescape）；② norm 须剥 ASCII 直引号 `"` 与单方括号 `[` `]`（Ebert "talkie"、维基编者 [his]/[walking] 补全）；③ 测试短语切词吞字（「此前的角色常被批评为」vs 存档「此前在基石影业时期，他的角色常被批评为」）。

## 预设验证记录

- 双线（小人物悲悯 寻子→城市之光→摩登时代 / 体制批判 摩登时代→大独裁者）全部取证成立，交点=摩登时代（既是 valedictory for the Tramp 又是 first overtly political-themed film）。
- 片序与真实年份一致（1921→1931→1936→1940），无需重排。
- 「喜剧是严肃的事情」证伪（见新坑 1）。

## 校验迭代记录

99→100 条：修文档 2 处真错（Keystone 批评英维真实措辞 "mean, crude, and brutish" 替代凭记忆的 "rough, coarse and brutal"；Modern Times 引文补 (1936)）+ 修脚本 3 处（.json 加载/norm 剥 ASCII 引号与方括号/切词短语）→ 100/100 0 MISS。S# 双向对账零孤儿零越界；[卡X] 孤儿（同文冗余/未入正文）以「⚠️ 未入正文」标注闭环。
