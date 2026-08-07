# 《巴里·林登》(Barry Lyndon, 1975) 单片研习轮来源地图（第二十三轮）

库布里克补代表作，创作极=**古典油画美学 / 自然光长镜**。16 存档 [研S1-16]（新抓 13 + 存量复用 3：kubrick_barry_wiki.txt plaintext、kubrick_ebert_barry.txt、kubrick_wiki.txt 经导演卡片转引链 [卡K·W-K]）。产出：《巴里·林登_研习报告.md》《巴里·林登_技法卡片.md》（6 卡）。校验：105 引文 + 16 数字 0 MISS（脚本 verify_barry_lyndon.py 在 film-suite-research/ 根目录）。

## 存档↔来源对照

| 存档 | 来源 | 关键内容 |
|---|---|---|
| kubrick_barry_wiki_raw.txt | 英维 raw（**Barry Lyndon (film) 是 95 字节 `#REDIRECT [[Barry Lyndon]]`，真实标题不带年份消歧**） | Cinematography/Principal photography/Thematic analysis/Reception 全段 + 46 refs（TelegraphReview=Tim Robey、DiGiulio AC、Lightman ASC、Ciment 访谈） |
| kubrick_barry_wiki.txt | 英维 plaintext（存量） | 无 refs，正文同构；Principal photography 段含 Troubles 拍摄史 |
| kubrick_ebert_barry.txt | Ebert Great Movies 2009 wayback（存量） | 一手影评全文 + Ciment 访谈转述（"novel had too much incident"） |
| kubrick_barry_zhwiki_raw.txt | 中维 亂世兒女 (1975年電影)（redirects=1 探测：乱世儿女/巴里·林登 都重定向到全繁条目） | 剧情全本/特点段（NASA 镜头/烛光/油画）/评价段（Kael 批评、斯科塞斯、斯皮尔伯格）/四项奥斯卡/结尾语中译 |
| kubrick_barry_baike_jina.txt | 百度百科裸词条 r.jina.ai | 基本信息：1975-12-18 英国上映、184 分钟、萨克雷 1844《巴里·林登的回忆》 |
| kubrick_barry_digiulio_jina.txt | **DiGiulio《Two Special Lenses for "Barry Lyndon"》AC 原文（visual-memory.co.uk 经 r.jina.ai）** | 改造者一手：纯烛光目标句/4mm 后组/两圈调焦/36.5mm Kollmorgen 适配器/24mm 弃用/整片推冲一档/安全联锁 |
| kubrick_barry_lightman_asc.txt | **Lightman《Photographing Stanley Kubrick's Barry Lyndon》ASC 1976-03 原刊（2018 重刊，wayback 20210916153823）** | Alcott 访谈一手：3 英尺烛光/70 烛吊灯/金属反射板顶光/burnt-out 脸部高光/Mini-Brutes 窗打法/零搭景/CCTV 对焦/Technicolor 取景器 |
| kubrick_barry_robey_telegraph.txt | Tim Robey《Kubrick by candlelight》Telegraph 2016-07-27（wayback 20190826130615） | **"actors ... under instruction to move as slowly as possible, to avoid underexposure"**/gilded-cage/绘画谱系/dutiful admiration but not love |
| kubrick_barry_bradshaw_guardian.txt | Bradshaw Guardian 2016-07-28（wayback 20181210064726） | 5/5：催眠慢板/喜剧到悲剧转换/Hordern 旁白"缺席的父亲"/书挡决斗/结尾字幕 exquisitely judged |
| kubrick_barry_review_14111718.txt | 豆瓣长评（269 有用，译自 Neil Oseman） | **摄影技术专文中译通道**：维米尔影响/43mm 景深计算（2.5m 外 f/0.7 全开）/720° 调焦环/柯达 5254 推冲 EI 200/NASA 批产 10 支 |
| kubrick_barry_review_2925794.txt | 豆瓣长评《不要低估了库布里克》（411 有用） | 旁白英文原文四段（七年战争/初战/父亲/片尾字幕）/纸衣服省钱细节/儿子葬礼观感 |
| kubrick_barry_review_8042359.txt | 豆瓣长评=**肖模译剧本全本**（1147 行，31 有用） | "解说"78 次/上集下集结构/结束语 L1145/译者的话点名"解说词及其用法的特色" |
| kubrick_barry_review_12250972.txt | 豆瓣长评《油画感。》（68 有用） | 影迷油画要素分析（自称"并不专业"），仅辅助证据 |
| kubrick_barry_review_1221557.txt | 豆瓣长评（103 有用，297 字符短稿） | 真实服装细节，未展开引用 |
| kubrick_barry_rexxar_list.json | rexxar reviews 列表（subject 1292472，total 234） | 选稿：f/0.7 摄影幕后（14111718）与剧本转载（8042359）都在热门 20 条内 |
| kubrick_barry_douban_suggest.json | suggest 裸片名"巴里·林登" | subject id 1292472（一次命中） |

## 本轮实测新通道 / 配方

1. **The Kubrick Site（visual-memory.co.uk）= 库布里克一手技术文献站**：DiGiulio AC 原文 + Ciment「Three Interviews with Stanley Kubrick」全文都在这站。wayback 快照是 JS 壳（2627 字节 "Your browser doesn't seem to support Javascript!"）→ **r.jina.ai 直抓 14KB 全文一次到手**。发现路径：英维 raw 的 ref 域名 grep。
2. **ascmag.com wayback**：ASC 1976 原刊重刊（Lightman 文=Alcott 访谈）86KB 直抓，含技术史硬数据（胶片型号/测光表型号/烛台支数）。
3. **豆瓣长评=英文摄影技术文中译通道**：标题"摄影幕后/谈谈 f/0.7"类长评是技术细节中译金矿（269 有用）。
4. **英维 (film) 后缀重定向**：`Barry_Lyndon_(film)` → 95 字节 `#REDIRECT [[Barry Lyndon]]`——先 curl 看返回体，是 #REDIRECT 就按目标标题重抓（与 2026 前"X (film) 可能重定向"的旧坑同型，本例给了具体判据：95 字节 = 纯重定向）。

## 关键引文位置（供复用）

- 结束语 L1145（剧本 8042359）；片尾字幕英文（2925794）；"It is well to dream of glorious war in a snug armchair at home"（2925794）
- DiGiulio 纯烛光目标句/推冲一档句（digiulio 文件前 5.5K 内）
- Alcott 3 英尺烛光/burnt-out/零搭景句（lightman 文件 ~26.8K-31K 区间）
- Robey 慢移动句（robey 正文第一屏）；gilded-cage 句同段
- 英维 Cinematography 段引文大量出自 TelegraphReview（Tim Robey）——"gilded-cage aesthetic"、"lowest f-stop in film history"、"recreating the huddle and glow of a pre-electrical age" 都归他，不是英维编者原创

## 校验新坑实例（㊽-㊿）

- ㊽ 校验脚本超长短语反向分支（>120 字符引文全误报）+ 短语侧未 lower（"born in Ireland" 大写 I）
- ㊾ Ebert 1975 vs 2009 两句措辞不同（forces vs asks / remain detached about vs only observers of），按版本归属
- ㊿ Champlin "coffee table books" 实为管道链接 `[[coffee table book|books...]]` 剥壳后文本；ASC 转录错字 "what is “sees,”" 按 [原文如此] 直录

## 双口径并记实例

- f/0.7 后组镜片距胶片平面：DiGiulio（改造者）4mm vs 英维 2.5mm——正文以一手为准并两源并记
- 片长 184 分钟（Ebert）vs 185 分钟（中维）并存

## 未取证清单

- Criterion essay、Ciment 访谈原文（仅经 Ebert/英维转引）、"每幕一幅画"逐镜对照文献、剧本原刊期号（世界电影哪期未取证到）
