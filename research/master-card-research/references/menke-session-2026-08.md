# Sally Menke 研习轮记录（2026-08，剪辑轴第一轮）

任务：产出《莎莉·门克_制作大师卡片.md》（昆汀御用剪辑，低俗小说/杀死比尔/落水狗/无耻混蛋）。工作目录 `_work/制作大师研习-20260809E/莎莉·门克/`，pages/ 存档 11 个（8 有效 + 3 失败记录）。

## 来源 URL 清单（全部经 r.jina.ai 抓取成功，除标注外）

| 存档 | URL | 类型 |
|---|---|---|
| menke_guardian2009.txt | theguardian.com/film/2009/dec/06/sally-menke-quentin-tarantino-editing | 一手·本人 Guardian 自述 |
| menke_editorsguild.txt | orangecow.org/articles/sallymenke.html | 一手·Editors Guild Magazine 访谈（Garrett Gilchrist 采，2009-07-13） |
| tarantino_charlierose1994.txt | screenwritingfromiowa.wordpress.com/2019/08/05/... | 一手转录·1994 昆汀×Charlie Rose |
| menke_wiki_en.txt | en.wikipedia.org/wiki/Sally_Menke | 二手·维基主条目 |
| reservoir_dogs_wiki.txt | en.wikipedia.org/wiki/Reservoir_Dogs | 二手·片条目 |
| menke_nyt_obit.txt | archive.nytimes.com/artsbeat.blogs.nytimes.com/2010/09/28/... | 二手·讣告（含 Bender 原话） |
| menke_slashfilm.txt | slashfilm.com/1487314/sally-menke-quentin-tarantino-secret-weapon/ | 二手·特稿（大量转引原话） |
| screenrant_pulp_chrono.txt | screenrant.com/pulp-fiction-movie-story-chronological-order/ | 二手·结构事实 |

未取到：Videomaker（403 Forbidden，重试仍 403）、eNotes Dargis 评论（CAPTCHA）、Art of the Cut（栏目 2015 年后创办，门克 2010 年去世，无访谈）。

## 已验证引语锚（grep 通过，卡片直接引用）

- 共写论（昆汀）："when it comes to the editing I write with Sally... I don't remember what her idea was, what was my idea" [SlashFilm/NYT 转引 Death Proof DVD 访谈]
- 素材自由（门克）："he gives me the dailies and I put 'em together and there's little interference" [Guardian]
- 风格论："Our style is to mimic, not homage, but it's all about recontextualising the film language to make it fresh within the new genre" [Guardian/Editors Guild 双源]
- 音乐机制："I don't cut to music. I just make the scene work emotionally and dramatically, and then Quentin will come in and lay the track over it" [Guardian]；"I don't cut with his music before he comes in" [Editors Guild]
- 师承："I learned how to collapse time in action but still push characters through a scene"；"It's the illusion that time is ticking away. It's all about tension" [Guardian]
- 非线性（昆汀 1994）："My storyline [for Pulp Fiction] jumps all over the place, back and forward"；"75% of the stories... But there is the 25%... Both Reservoir Dogs and Pulp Fiction gain a lot more resonance being told in this wild way"；小说家自由论 [Charlie Rose 转录]
- Kill Bill："The idea was there early on, to divide it"；"The fighting we didn't speed up"；"the blink was a decision on our part"；"The swordfights feel real" [Editors Guild]
- 剪辑观："I don't do match cuts really... the audience is really willing to accept a lot of discontinuity"；"A cut is a cut no matter what... It still was frame perfect"；"I realized every single edit is important"（perfunctory 教训）；"what their body is saying"；"a painting looks like its painter" [Editors Guild]
- 合作强度（Bender）："I'm not going to shoot the movie until she's available"；"Hi, Sally" 传统 [NYT]

## 陷阱案例：WordPress raw-HTML 实体

screenwritingfromiowa 页 r.jina.ai 回原始 HTML（103KB），验证 "constantly unfolds" 假失败——存档里是 `constantly&nbsp;unfolds`；NYT 讣告 "she's available" 假失败——弯引号 `she’s`。对策：验证串拆短（"shoot the movie until"）、python html.unescape 后验证、假失败先打上下文确认实体/引号形态再判。WordPress 正文提取：正则 `<p>(.*?)</p>` 或定位 "by <作者>" 起点后剥标签+解实体。

## 双侧取证规则（剪辑轴特有，写入卡片诚实声明第 6 条）

昆汀-门克组合中：非线性/跳过关键事件/分段等**结构构思**证据全在昆汀访谈（Charlie Rose 1994、落水狗维基引昆汀语）；门克访谈的自我定位是执行+共写（节奏、情绪、帧精确）。卡片按两侧分别取证、分别标注 [S 编号]，并在诚实声明明示"避免把导演的构思冒认为剪辑师独有"。量化口径：奥斯卡 2 提名/BAFTA 3 提名/"25 提名 12 获奖"/75 佳剪辑榜第 18 均出自维基（S1）。

## 可复用 URL 模板（剪辑/声音/调色师轮）

- 本人 Guardian 自述：`theguardian.com/film/<年>/<月>/<日>/<人名>-<导演名>-editing`（门克 2009 即此格式）
- Editors Guild 镜像：`orangecow.org/articles/<人名>.html`（Garrett Gilchrist 采编，含 Kill Bill/Inglourious Basterds 等具体影片剪辑决策）
- 老访谈转录：`site:wordpress.com "<人名>" interview transcript`（Charlie Rose 类 90 年代访谈转录常在个人博客）
- 结构事实：`site:screenrant.com "<片名>" chronological order`（非线性片的时间线梳理）
