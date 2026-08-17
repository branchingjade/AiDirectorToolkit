# 哈利豪森研习轮记录（视效/实体特效轴第一轮）

## 任务
Ray Harryhausen（定格动画特效宗师，1920–2013）制作大师卡片。产出：`_work/v2-大师卡-20260809/哈利豪森/哈利豪森_制作大师卡片.md`（27.5KB，八段式；本轮同轴后续：Dykstra/Muren/Letteri/斯坦·温斯顿）。

## 来源 URL 清单（10 存档，全部直连 curl 可抓）
1. **Guardian 讣告 2013-05-07**：`https://www.theguardian.com/film/2013/may/07/ray-harryhausen-dies`（注意 URL 带 `-dies` 后缀；先猜 `/ray-harryhausen` 返回 404——Guardian 讣告 URL 无固定模式，先 web_search 拿准确 URL 再抓）
2. **1984 年本人讲座原文（一手）**：`https://networkninenews.com/2017/05/05/dynamation-from-a-lecture-by-ray-harryhausen-in-1984/`（116KB 直连可抓；Network Nine News 是英国影视工艺讲座/访谈存档站，同站还有 Neville Smallwood 1948 化妆讲座、Wendy Laybourn 特效文——**视效/实体特效轴的一手讲座金矿**）
3. **自传摘录（一手）**：`https://www.theguardian.com/books/2003/dec/20/featuresreviews.guardianreview16`（《Ray Harryhausen: An Animated Life》Aurum Press 摘录，文末版权行"© Ray Harryhausen and Tony Dalton 2003"；骷髅战全部硬数据在此）
4. **Observer 2019-07-21**：`https://www.theguardian.com/film/2019/jul/21/harryhausen-animation-cinema-hollywood-film-mythology-adventure-models`（John Walsh 基金会受托人访谈；Lucas 名言第二版措辞）
5. 英文维基主条目：`en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&rvslots=main&redirects=1&titles=Ray%20Harryhausen`（action=raw 在 redirect 条目给 32B，API 才是正路）
6-9. 影片专条（同 API 法）：Jason and the Argonauts (1963 film) / The 7th Voyage of Sinbad / One Million Years B.C. / Clash of the Titans (1981 film)
10. 中文维基「雷·哈利豪森」（API 自动跟随重定向；influenced 名单=影响谱系中文佐证）

## 已验证引语锚（40 条全命中）
[一手·讲座 S2] "we build small models and shrink the actors down to size in order to have control"；"thirteen frames per nine-hour day"；"choreographed like a ballet and broken down into numbers"；"Dynamation is a term which was coined by producer Charles Schneer"；"miniature rear projection instead of travelling mattes"；"yellow backing travelling matte process"；"the darkest day I can remember"；"I always prefer to animate models of animals"；"a talented crab… a baboon who can play chess"；"at the whim and mercy of a lizard"；"spoils the illusion"
[一手·自传 S3] "three men fighting seven skeletons"；"five appendages to move in each separate frame"；"at least 35 animation movements"；"less than one second of screen time"；"a record four and a half months"；"deliberately stiff and mechanical movement"（Talos 材质僵硬论）；"the only way to kill off something that was already dead"；"rotting corpses, but we thought this would give the film a certificate"；"model of Talos is approximately 12in high"；"I shot a frame and gouged out a little of the clay"；"Colossus in reverse"
[讣告转引 S1] "stunned and haunted. They looked absolutely lifelike"；"heartsick over some of my pictures"；"It would be Medusa. But don't tell the others."；"devised a dynamic split-screen technique"；"did not have any character and that he should study anatomy"
[维基 Legacy 段 S5] Lucas "Without Ray Harryhausen, there would likely have been no Star Wars"（家族声明）；Gilliam "Only with his digits"；Cameron "standing on the shoulders of a giant"；Edgar Wright "the man who made me believe in monsters"；Peter Lord "a one-man industry and a one-man genre"

## 视效/实体特效轴来源地图（本轮验证）
- **维基主条目 "Death and legacy" 段=逝者引语聚合金矿**：家族声明+同行悼词+媒体评价集中于此段且逐条带 refs——Lucas/Gilliam/Cameron/Wright 五条引语一次 grep 全取到；去世人物先读此段，再按 refs 决定补抓
- **逝世时家族声明（family statement）名言经媒体转引措辞不一**：Lucas 两版（ComingSoon 版 "Without Ray…no Star Wars" vs Guardian 2019 版 "no Star Wars without Ray…"），卡片两版并记、标"转引"而非一手
- **Guardian books 栏目自传摘录**：`guardian.com/books/<日期>/…` 常刊载影人自传节选（一手），文末版权行给出版本/年份（发现自传年份双口径 2003 vs 2004 即靠此）；维基条目 refs 段会引用这类链接——从维基 refs 挖
- **颁奖礼致辞经转引**：1992 Gordon E. Sawyer 奖 Hanks 致辞"greatest film ever made"经 NYT 讣告/维基影片条目转引——NYT 反爬时走维基转引链
- **实体特效"翻车案例"=方法论证据**：泡沫塑料石头浮水事故（连夜换实心石膏）、石膏骷髅扔海一次成——自传里找事故段落，比工艺描述更有卡片价值
- **模型动画的量化数据是一手讲座/自传的招牌**：13 帧/9 小时日、每帧 35 动作、4.5 个月——特效轴卡片的"硬数据锚"

## 诚实声明要点（本轮）
- 未逐帧看片；1984 讲座为第三方存档转载（无官方原件核对）；Lucas 名言经转引两版措辞并记；骷髅战时长双口径（本人 "four and a half months" vs 维基脚注 "well over three months"）；自传年份双口径（2003 版权行 vs Guardian 讣告 2004）
- 未取到：NYT 讣告原文（403）、Saturday Evening Post 2020（Cloudflare 挑战页）、BFI Mighty Ray Harryhausen（JS 渲染仅 232B，名单经维基转引）、The Beast from 20,000 Fathoms 维基条目（多次 429，以 Guardian 讣告内容覆盖）

## 本轮新陷阱
- **维基斜体标记 `''` 打断子串匹配**：原文 `no ''Star Wars''` 不含连续子串 "no Star Wars"——wikitext 特有的陷阱（区别于 markdown 强调符）；归一化时对维基语料先 `re.sub(r"''", "", txt)` 再匹配
- **维基 API 429 在 6s 间隔仍触发**：本轮 6s 批量 3/8 失败；处理=间隔 12s+ 重试或直接重跑同一脚本（SKIP-if-exists 逻辑天然=断点续抓，一次工具调用可重跑多轮）
- **Guardian URL 猜测易 404**：讣告/纪念文 URL 带随机后缀（-dies 等），先 web_search 拿准确 URL，避免 404 存档占位（SKIP 逻辑会把 404 页当成功存档，重抓前须先删旧文件）
