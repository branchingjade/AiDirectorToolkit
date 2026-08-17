# 阿方索·卡隆导演轮来源地图（2026-08-09，v2 导演研习轮 14 人并行批）

> 导演卡片+手法体系深化双文档轮。12 存档 10 编号（S1-S10），53 条引文校验 52 直中+1 假 MISS（数字千分位逗号）。产出写入 `_work/v2-导演研习-20260809/阿方索·卡隆/`（导演轮产出在工作区而非 film-suite-research，与单批轮一致）。
> 本次是**拉美导演通道轮**：没有 Criterion essay（Netflix/华纳版权）、没有 SoC 专条、没有中文影评投入——靠"颁奖季访谈 + 英中维"完成取证，证明**欧美主流导演在无 Criterion/无中文渠道时，颁奖季媒体长文就是第一手通道**。

## 存档对照（pages/，12 个）

| 存档 | 来源 | 关键内容 |
|---|---|---|
| cuaron_wiki_raw.txt (41KB) | enwiki 主条目 | **Style and themes 段=均镜量化金矿**（处女作 ~6s→Y tu mamá también 19.6s→Children of Men 16s vs 好莱坞 2s；"unconventionally lengthy shots"）；2010-present 段=Roma 立项/Liboria Rodríguez 保姆原型/奥斯卡 3 项 |
| cuaron_roma_wiki_raw.txt (47KB) | enwiki Roma 条目 | Production 段："I wanted to do a modern film that looks into the past"；**彩色实拍后期转黑白**；shot in sequence；实景拍摄（棚拍对新人演员难）；"semi-autobiographical take on Cuarón's upbringing" |
| cuaron_gravity_wiki_raw.txt (113KB) | enwiki Gravity 条目 | Filming 段：**156 镜均镜 45 秒**、LED 灯箱（Bullock 每天 10 小时）、汽车机器人、"there is no sound in space"、Time 2013 最佳发明、测试观众要怪物被拒；Cinematography 段：**13 分钟开场一镜 + invisible cuts 缝合**、光随威胁由亮转暗 |
| cuaron_com_wiki_raw.txt (96KB) | enwiki Children of Men 条目 | **三个连续长镜实测 3m19s/4m7s/6m18s**；车戏 6 段/4 地/1 周/5 无缝数字转场；Doggicam rig（Gary Thieltges）；长镜实验史（Great Expectations→Y tu mamá también→Azkaban）；Stevens "two of the most virtuoso single-shot chase sequences" |
| cuaron_zhwiki_raw.txt (10KB) | zhwiki 艾方索·柯朗主条目 | "自传式西班牙语黑白电影《羅馬》"；拉丁美洲首位奥斯卡最佳导演；身兼导演/编剧/制片/剪辑/摄影 |
| cuaron_roma_zhwiki_raw.txt (10KB) | zhwiki 羅馬条目 | 剧情摘要全文（海滩救子/死婴/新年大火+摇篮曲/屋顶晾衣）；"改编自他的童年经历"；预算 1500 万美元 |
| cuaron_gravity_zhwiki_raw.txt (35KB) | zhwiki 地心引力条目 | **4096 颗 LED 灯泡巨型灯箱**（电脑同步灯光/镜头/吊架）；"这样的镜头首先代表的是安全感，如婴儿在母体的安全感" |
| cuaron_variety_clean.txt (17.7KB) | **Variety 2018-10-23 封面长文**《Alfonso Cuarón Digs Deep Into His Childhood for 'Roma'》 | 一手金矿：博尔赫斯裂纹记忆隐喻原话；三要素（以 Libo 为中心/自己记忆/黑白）；阶级愧疚原话（"white, middle-class, Mexican kid living in this bubble"）；Libo 原型细节（Mixtec/9 个月入家/Oaxaca）；Lubezki 缺席自任摄影；不给剧本按序拍；110 天；场景重建（滑动墙+可拆屋顶） |
| cuaron_yahoo.txt (6.2KB) | **IndieWire 2018-12 经 Yahoo 转载**《'Roma': Childhood Memories Flowed Like Water…》 | 4 分钟擦地开场长镜定全片节奏（"that flow started to dictate the other stuff"）；**"Memory is the implied narrator"**；单镜分娩一次过（"they got it in one take"）；怀孕戏 60 条/4 小时 master；"I would not cut, I just let it roll"；4 小时粗剪→135 分钟；Pepe=导演 alter-ego；水=记忆闭环 |
| cuaron_redbull_clean.txt (13.9KB) | **Red Bulletin 2018-12 访谈**（redbull.com 品牌杂志） | 90% 场景来自记忆（转述）；"faithful and pure to the idea of re-creating memories"；巴赫旋律取景轶事；记忆迷宫三年（"opening doors from the memory labyrinth"）；"curiosity for the unknown"；"It wasn't until Y Tu Mamá También that technique ceased to matter"；El Halconazo 12 年计划；Canoa "obliquely, indirectly" |

（cuaron_variety.txt 592KB 原始 HTML 保留备查；cuaron_redbull.txt 为 jina markdown 原始版。）

## 新通道（本轮实测）

1. **Variety 封面长文 = 颁奖季导演访谈金矿**：好莱坞导演轮第一顺位（Variety 颁奖季 cover story 常为数千字一手访谈）。**正文提取配方**：`<article>` 容器正则只拿到 1008 字符（首段）、`<p>` 正则 0 字符、JSON-LD `articleBody` **被截断**（350 字符带 "[…]"）——三法全败后，用正文独特短语（"painstaking emotion"）在 raw HTML 里 `find` 定位（位置 393326），从该处切 ~40KB、剥 script/style/标签、按行长过滤（>100 字符）即得 17736 字符完整正文。**通用化：新闻站 HTML 正文提取失败时，用文中独特短语定位正文起点再剥标签**。
2. **Yahoo entertainment 转载 = IndieWire 内容镜像通道**：IndieWire 文章常被 `yahoo.com/entertainment/` 转载（标题相同），r.jina.ai 直抓 Yahoo 版成功——IndieWire 原文被 CF 挡时的第一镜像。
3. **Red Bulletin（redbull.com/theredbulletin）= 品牌杂志导演访谈通道**：品牌杂志（Red Bull/红牛）颁奖季做深度导演访谈，jina 可抓全文无壳。

## 新坑（登记 pitfalls-log ㊿-卡隆轮）

- **数字千分位逗号假 MISS**："4096" vs 存档 "4,096"（zhwiki LED 灯箱）——norm 不归一数字逗号时断匹配，53 条校验唯一 MISS 即此；数字类测试短语先核对存档是否带千分位逗号（㉟ 全角标点家族的数字形态）。
- **JSON-LD articleBody 截断不可当全文**（Variety 实测 350 字符 "[…]"）——JSON-LD 只给首段+摘要，全文必须从页面 HTML 提取（见上配方）。
- **英维条目 Production 空父段**：Gravity 的 `==Production==` 是空壳，内容全在 `===Filming===`/`===Cinematography===` 子段——按 `==Production==` 正则提取得空串；先 `re.findall(r'==+[^=]+?==+')` 看结构再选段（脚本第 1 步就该做）。
- **jina 429 重试模式**：`{"code":429,"name":"RateLimitTriggeredError","retryAfter":2}`——sleep 3 秒原 URL 重试即成功（13967 字节全文），不要换通道；同批多 URL 连续 jina 抓取时中间插 sleep。
- **主条目 Style and themes 段 = 均镜量化金矿**（grep 目标）：英维导演主条目自身就有 Style and themes 段（无独立 "Cinematic style of" 专条时）——均镜秒数/风格概述/主题段常整段在此（诺兰轮专条之外的第二形态）。

## 内容层双口径

- **地心引力开场长镜**：英维 "uninterrupted 13-minute opening scene" vs 通行宣传"17 分钟"——17 分钟未直接取证到权威原文（web_search 英文查询被垃圾污染），正文采用英维 13 分钟口径并写入诚实声明。
- **罗马记忆浓度**：Red Bull 转述"90 percent of the scenes came from his memory"（非导演逐字）vs Variety 三要素原话——转述与逐字分开标。

## 未取证（写入诚实声明）

Criterion essay（Netflix/华纳版权）、Ebert 影评（反爬未投入）、"Cinematic style of Alfonso Cuarón" 专条（404 不存在）、罗马均镜秒数量化（只有单镜数据：4 分钟开场/单镜分娩）、中文影评人长评（预算未投入）。

## 自查修正记录（写作纪律再证）

定稿前自查发现 3 处凭印象表述，均按存档原文改写：①"柯达/Arri 大画幅黑白"→Variety 原文 "the pristine imagery of large-format black-and-white digital photography"（机型未取证）；②画面锚点"屋顶晾衣天空横过飞机"→删除飞机（中维剧情只有"拿着衣服爬到屋顶去洗"）；③深化表"门廊"→"车库"（中维剧情有据）。与 ⑩/㊲ 同族：**成片画面细节（名场面构图）最容易凭印象写，逐条对照存档原文**。
