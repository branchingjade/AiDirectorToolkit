# 《出租车司机》单片轮来源地图（2026-08，斯科塞斯补代表作）

创作极：都市孤独 / 暴力觉醒 / 精神病患视角。导演本体待补、零存量全新建档。
产出：`研习报告/出租车司机_研习报告.md` + `技法卡片源稿/出租车司机_技法卡片.md`（7 卡片），独立 [研S#] 编号。

## 存档对照（30 档，[研S1-研S23] + 留档）

| 编号 | 文件（pages/） | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | scorsese_taxi_enwiki_raw.txt | 英维 Taxi Driver raw 94.5KB | Plot/Production/Music/Themes/Legacy/"You talkin' to me?" 专节；施拉德 Reddit 循环论、父亲形象、莫霍克、Chemtone |
| 研S2 | scorsese_taxi_zhwiki_raw.txt | 中维「的士司機 (1976年電影)」raw 11.2KB | 風格與影響（第一人称叙述/唯一非POV戏/跳接/地下室手记）、影片结尾、人物分析 |
| 研S3 | scorsese_taxi_zhwiki_disambig.txt | 中维消歧义页 | 标题探测留档：消歧义页→真实条目名 |
| 研S4 | scorsese_taxi_ebert_greatmovie.txt | Ebert Great Movies（wayback 20130414194024） | "the only one here" 尾句解读、结局 "plays like music" |
| 研S5 | scorsese_taxi_ebert_1976.txt | Ebert 1976 原评（wayback 20130603064546） | "weathers of a man's soul"、camera looks straight down；schema 4.0/4.0 |
| 研S6 | scorsese_taxi_criterion_818.txt/.html | Criterion posts/818，Frank Rich 1990（live 直抓） | "Psycho 换主角视点"开场、scum off the streets、孤独者画像 |
| 研S7 | scorsese_taxi_script_douban.txt | 豆瓣 6282644 施拉德剧本中译全本（224 有用） | 沃尔夫题词/开场日记/四乘客/对镜练枪（无台词）/血拚/指枪/剪报/匹茨堡信 |
| 研S8 | scorsese_taxi_review_12112161_kael.json | 凯尔《纽约客》影评中译（35 有用，《虹膜》首发） | 霓虹灯的红光/特拉维斯对阵纽约/暴力=唯一性高潮/赫曼配乐批评 |
| 研S9 | scorsese_taxi_review_1378730_乘客.json | 《四个乘客》（2082 有用） | 6月8日两分法、愤怒积累"古井填满"、伪君子动机 |
| 研S10-21 | scorsese_taxi_review_*.json ×12 | 豆瓣长评（1527010/5320796/12984218/1579748/1046362/5388229/12074845/1010583/1405860/1007307/1117497/1061926） | 见报告附录；12984218=施拉德评论音轨笔记 14 条（本轮最大一手金矿） |
| 研S22 | scorsese_taxi_baike_clean.txt | 百度百科 6787835（DDG site: 定位） | 次要来源 |
| 研S23 | scorsese_enwiki_raw.txt | 英维 Martin Scorsese 主条目 226KB | 查普曼高反差强色、金发女主白衣慢镜谱系、movie brats |

## 预设纠正与关键取证

1. **Criterion essay 作者预设证伪**：任务预设「Colin MacCabe essay」→ 实为 **Frank Rich**（posts/818，1990-09-24）。双通道取证：渲染文本 byline「By Frank Rich」+ HTML `data-article-metadata` JSON `"author":"Frank Rich"`。清洗正文按 "View Comments" 截尾会丢掉其后的作者简介；HTML byline 是 `By <a>作者</a>` 标签分隔，"By Frank Rich" 连续子串需先剥标签。
2. **Ebert 星级预设纠正**：任务预设「五星」→ Ebert 四星制，wayback HTML `<span itemprop="reviewRating"><meta content="4.0" itemprop="ratingValue"><meta content="4.0" itemprop="bestRating">` = 4.0/4.0 满星。1976 原评与 Great Movies 均 4/4。
3. **"You talkin' to me?" 剧本无此句**：剧本只写「他站在镜子前」「自说自话地表演着使用武器的高尚技巧」——德尼罗即兴（施拉德证实，灵感=地下纽约喜剧演员）；斯科塞斯画面灵感=《金眼神》白兰度对镜。AFI 百大台词第 10。
4. **中维条目名=「的士司機 (1976年電影)」**（港译）；「計程車司機 (電影)」重定向到消歧义页；消歧义页 raw 直接列出电影条目链接。
5. **剧本=俄译转译本**：注1「转译自俄罗斯《电影剧本》杂志1993年第3、4期」（王燎/潘桂珍译）；注3 血拚超现实论=译者解读金矿。
6. **循环结局三源**：Chemtone 首尾同工艺（施拉德音轨）+ Reddit「could be spliced to the first frame」+ 成片后视镜躁动（英维 Plot）。
7. **暴力觉醒三段式细化**：暗杀政客（未遂）→血洗妓院→指枪自我献祭；施拉德 father figure 论证明三段同源；指枪=失败标志、「想死」是剧本自带动机。
8. **色彩系统**：剧本「黄、红、绿色的灯光反射」+ 凯尔「霓虹灯的红光」+ 丹·佩里 slit-scan 片头（lurid colors/glowing neon/deep black levels）+ 影迷「三件外套=交通灯」拉片（红西装约会/绿大衣行刺/黄夹克日常）。

## 校验记录

- 手写清单 ~110 条目（短语逐字复制+期望存档关键词）双侧归一 grep，**0 真 MISS**。
- 自动提取陷阱：从交付文档自动提取「」引号短语 → 174 条中 105 条假 MISS（自己行文的强调性引号/标题被误当引文）。**自动提取只认带 [S#] 标注行的引号块，或回到手写清单法**。
- 引文措辞修正 5 例：马格尼特≠马格努姆（**同译本内音译三形态并存**：马格尼特/马格努姆/玛克努姆）；「举起血淋淋的左手」缺「举起」；「呈现的下坠感同时将背景画面也渐渐压暗」断句；「is not cured by the movie's end」引文外代词 he 去掉；「By Frank Rich」需剥 HTML 标签（criterion 文件非纯文本）。
- [研S#] 一致性：正文使用 ⊆ {1..23}，无越界。

## 并行轮互引

- pages/ 中途（18:02）出现并行子代理存档：scorsese_review_*.txt（同批豆瓣长评纯文本版，含 6282644/12984218 同文）、scorsese_casino/goodfellas/irishman/meanst/raging/departed 影片条目——不属本轮编号。
- `技法卡片源稿/斯科塞斯_手法体系深化.md`（18:09 落盘）自建 [S1-S40]，其 S3/S19/S21/S22 与我方同源存档（共享 pages/ 文件）；其诚实声明第 9 条「未见单片轮产物落盘」已由本报告闭环。互引以存档文件名为准。

## 渠道备忘

- 豆瓣 rexxar 不带 Referer → `{"msg": "invalid_request_1284", "code": 1287}`（详见 douban-rexxar-api.md 补丁）。
- 英维 enwiki API 限流（"You are making too many requests"）→ 放缓到 4s/请求或用 raw 端点。
- zhwiki 电影条目标题探测：裸名/「(電影)」后缀/「(1976年電影)」后缀/台港译名/消歧义页 raw 五形态。
- Ebert CDX：`rogerebert.com/reviews/great-movie-taxi-driver-1976*` 与 `reviews/taxi-driver-1976*` 均有快照；h1+角色名定位法（Travis|Scorsese|De Niro|taxi 起点标记）两快照均适用；两快照均无 meta description。
