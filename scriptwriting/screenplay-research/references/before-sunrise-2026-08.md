# 《爱在黎明破晓前》Before Sunrise (1995) — 抓取与研习记录（2026-08-07）

## 抓取记录

| 渠道 | 结果 |
|---|---|
| Script Slug PDF 直链 `https://assets.scriptslug.com/live/pdf/scripts/before-sunrise-1995.pdf` | ✅ 200，168KB；pdftotext -layout → 73 页 / 121K 字符；slug 可猜（`before-sunrise-1995`） |
| IMSDb `imsdb.com/scripts/Before-Sunrise.html` | ❌ 7,785 字节空壳（scrtext 仅 559 字符），软 404 未采用——"判据永远是 grep scrtext 长度，不是 HTTP 状态"再验证 |
| thescriptsavant `Before_Sunrise.pdf` | ❌ 404 |
| Criterion Dennis Lim 论文（《The Before Trilogy: Time Regained》） | ❌ 403（Cloudflare）；换维基三部曲条目 Production/Authorship 节补制作资料 |

## 版本

流传稿：稿头仅 "BEFORE SUNRISE by Richard Linklater Kim Krizan"，无日期卡/版权页/修订色标，无法确定稿次。IMSDb 条目是空壳、无第二来源交叉，版本指纹检测（成片名句 grep）无参照系——如实标注"流传稿"即可。

## 稿本 vs 成片差异（已核实）

1. **假打电话戏位置**：稿本第 32 场 `INT. CAFÉ - NIGHT`；维基剧情段证实成片同在咖啡馆（"In a Viennese café, Jesse and Céline stage fake phone conversations"）。**教训：稿本/成片位置争议用维基剧情段仲裁，别凭观影记忆**——本会话曾误记成唱片店，被维基纠正（成片唱片店第 13 场只有听歌间对望，"Come Here" 歌词全文入稿）。
2. **看手相者**：稿本为卖花婆婆（ROSE PEDDLER），台词 "He is learning." / "You are stardust"；成片版台词未抓逐字稿，报告不引用成片版。

## 结构骨架（42 场，场标题时间词表 = 一夜倒计时引擎）

AFTERNOON(1-3 火车相遇) → LATE AFTERNOON(4-8 车站/下车决定) → DAY(9-13 桥/博物馆/电车/唱片店) → DUSK(16 无名者墓地) → SUNSET/NIGHT(17-38 摩天轮初吻第 17 场≈40%/夜游主体) → EARLY MORNING(39-40 大键琴手/Albertina 露台) → DAWN(41 车站誓约) → MORNING MONTAGE(42 空镜回访)。"12 小时时间约束"替代反派 = 纯对白爱情片的结构引擎（维基主题段）。

## 即兴共创（话痨片创作思路，报告须双述署名争议）

- 林克莱特+克里赞仅讨论大纲，11 天写完初稿（维基 Production 节）
- 德尔皮 2016 自述（Creative Screenwriting，经维基 Authorship 节转引）："Ethan and I basically re-wrote all of it. There was an original screenplay, but it wasn't very romantic, believe it or not. It was just a lot of talking, rather than romance. Richard hired us because he knew we were writing and he wanted us to bring that romance to the film."
- 克里赞 2019 否认"完全重写"——署名争议是这类工作法的代价
- 续集《爱在日落黄昏时》《爱在午夜降临前》霍克/德尔皮获编剧署名（克里赞得 story credit）

## 话痨爱情片研习要点（本片独有，可复用）

1. **假打电话转述告白**（第 32 场）："I like to feel his eyes on me when I look away"——当面转述=双方都可撤回的安全告白
2. **时间旅行包装请求**（第 17 场）："How come every time you want me to do something, you start talking about time travel?"——理论语言提身体请求，对象拆穿即笑点
3. **反高潮收尾**（第 41-42 场）：不交换联系方式只立誓约（December sixteenth, six o'clock in the evening, track eleven / 不写信不打电话）+ 晨间空镜回访（"the transformation has begun"）
4. **身体三级跳**："对话停、动作起"（偷看→初吻→草地亲热），动作指示每处只有一两行

## 关键场景行号图（sunrise_slug_raw.txt，pdftotext 提取）

| 场景 | 行号 |
|---|---|
| 唱片店听歌间（第13场） | L1351-1412 |
| 摩天轮+时间旅行（第17场） | L1490-1552 |
| 看手相（卖花婆婆） | L1745-1829 |
| 街头诗人《Delusion Angel》（第23场） | L2277-2334 |
| 假打电话（第32场） | L2876-2988 |
| 草地亲热+黎明（第38-39场） | L3610-3693 |
| 车站誓约（第41场） | L3806-3951 |
| 晨间蒙太奇（第42场） | L3954-3970 |

## 摘录复核

v6 严格校验器 36/36 直过 + 自检 3/3（坏例 FAIL / 正例命中 / 跨页 CONT'D 句命中）。本轮新增清洗规则（详见 SKILL.md 陷阱「摘录复核 v6」条）：块引用行拆分、CJK+箭头区过滤、URL/路径段过滤、只剥双引号不剥撇号、`\(MORE\)` 裸正则（`\b` 版静默失效）、翻页残留页号剥离（`\s+\d{1,3}\.\s+`）。
