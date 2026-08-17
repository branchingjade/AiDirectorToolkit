# 杜可风（Christopher Doyle）研习轮记录 · 2026-08-09

摄影指导（DP）轴大师卡片扩展轮。产出：`_work/制作大师研习-20260809C/杜可风/杜可风_制作大师卡片.md` + pages/ 存档。

## 来源 URL 清单（全部直连 curl 成功，r.jina.ai 当时整体失效）

| 编号 | URL | 用途 |
|---|---|---|
| S1 | https://en.wikipedia.org/wiki/Christopher_Doyle | 英文维基主条目（建议 action=raw 拿 wikitext） |
| S2 | https://zh.wikipedia.org/w/index.php?title=杜可風&action=raw | 中文维基（简体条目是 43B #REDIRECT，须跟繁体） |
| S3 | https://www.theskinny.co.uk/film/interviews/reflections-in-a-golden-eye-an-interview-with-christopher-doyle | 一手访谈 2012：舞蹈论/坛城论/雕塑论 |
| S4 | https://thefilmstage.com/christopher-doyle-on-moving-on-from-wong-kar-wai-constant-reinvention-and-the-strange-journey-of-life/ | 一手访谈 2019 Camerimage（Cloudflare 站点但直连可抓） |
| S5 | https://www.tatlerasia.com/lifestyle/arts/cinematographer-christopher-doyle-interview | 2021 长篇：王家卫 2008 MoMI 转述火场逸事 |
| S6 | https://stillslab.com/news/christopher-doyle-how-wong-kar-wai-s-dp-made-longing-look-like-that | 抽帧/超广角/带源色技术解码 |
| S7 | https://colorculture.org/cinematography-analysis-of-in-the-mood-for-love/ | 《花样年华》构图/色彩/布光分析 |
| S8 | https://deepfilmanalysis.com/chungking-express-1994-deep-film-analysis/ | 《重庆森林》分段摄影归属（关键勘误源） |
| S9 | https://www.cinematography.net/edited-pages/StepPrinting-ExamplesInformation.htm | CML 邮件组：抽帧技术定义 + 快门效果组合 |
| S10 | https://sightlines.media/sightline/the-camera-that-feels | 评论：摄影机=情绪器官 |
| S11 | https://en.wikipedia.org/w/index.php?title=Ashes_of_Time&action=raw | 东邪西毒条目（含 NYT 影评引用） |
| S12 | https://russilvong.com/ashes.html | 东邪西毒影评（stop-motion 打斗） |
| S13 | https://h5.ifeng.com/c/vivoArticle/v002u4sePpLmAcE6amvh9mXczClx9LNx1rPACg7tNfNOPkc__?isNews=1&showComments=0 | 澎湃 2024：35kg 摄影机/婚姻吐槽（二手转述） |
| S14 | https://content.mtime.com/article/229265271 | Mtime 2024：重庆森林 30 年（手持/杜可风的家） |
| S15 | https://ent.sina.com.cn/2003-11-04/0216226614.html | 新浪 2003：**GBK 编码**，gb18030 解码；杜可风中文一手引语 |
| S16 | https://en.wikipedia.org/w/index.php?title=In_the_Mood_for_Love&action=raw | 花样年华条目：双摄影/超期退出/技术大奖 |
| S17 | https://bfidatadigipres.github.io/world+of+wong+kar+wai/2021/07/10/ashes-of-time/ | 404 未取到（BFI 节目笔记） |

## 两处署名勘误（简报 vs 查证）

1. **《花样年华》**：简报称杜可风主创（手持/慢门）。查证 [S16]：Doyle + Mark Lee Ping-bin 双署名，杜可风超期退出，维基原文 "Both DPs are credited equally for the final film, though Doyle's more typically kinetic style is never on view, and the film is shaped by more subtle, longer shots typically associated with Lee." 成片主调归李屏宾；杜可风可验证贡献=前期颜色体系（[S15]「《2046》延续了《花样年华》的颜色系统」）。《花样年华》的「慢门拖影」仅雨中对峙大全景一处有 CML 例证 [S9]。
2. **《重庆森林》**：第一段（金城武/林青霞）抽帧为 Andrew Lau 所拍（6fps+每帧印 4 次）[S8]；杜可风第二段「漂过空间」、选择性抽帧。CML [S9] 将整片示例署 Doyle（"shot by Chris Doyle"）+ 注明是抽帧与快门效果组合。两种口径并存，卡片按更细的分段分析写。

## 验证过的一手引语（grep 行号见卡片附录）

- "There's only three people in cinema...our job as cinematographers is to be that bridge, that conduit." [S3]
- "Dance is the most important thing. The dance between the camera and the actors." [S3]
- "We're a lot like a mandala...You're looking to complete the cycle." [S3]
- "It's like a sculptor taking a block of stone and ending with Giacometti...That was the sculpture hidden in the stone." [S3]
- "The most important thing Wong Kar-wai said to me was, 'Is that all you can do, Chris?'" [S5]；中文版「你就只能拍成这样子吗？……他是我合作导演中最厉害的」[S15]
- "The script is a blueprint, but the film is a process." / "We make the film we can. They buy the film they think they want." [S4]
- "It's only a film. But it's your life. It's only a film, but it has to be yours." [S4]
- "The light bouncing off that guy's head is much more interesting than a reference to a film noir from the forties." [S3]
- 王家卫转述火场逸事：Doyle "stripped naked, covered himself in water, grabbed the camera, ran onto the fiery set, and got the shot in one take" [S5]

## 抓取要点备忘

- r.jina.ai 四连全返回 Cloudflare "Just a moment..." 挑战页 → 直连 curl 全部成功（含 Cloudflare 保护的 filmstage）。
- html2text 未装，bs4 可用；Chinese 站点（sina）GBK 编码须 `raw.decode('gb18030')`。
- 维基 action=raw wikitext 比 HTML 转换干净，直接 grep。
