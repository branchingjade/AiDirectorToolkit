# 武指轴第一轮 · 程小东（Ching Siu-tung）研习记录 2026-08

制作大师卡轮武指轴首张卡（《程小东_制作大师卡片.md》，产出于 `_work\v2-大师卡-20260809\程小东\`）。本文件=URL 清单/勘误案例/已验证引语锚/通道实测/双口径/未取到清单，供后续武指人物（董玮、元奎、刘家良、洪金宝等）复用。

## 关键勘误（简报 vs 查证）
- 简报：「程小东=卧虎藏龙武指（竹林/屋顶追逐）」→ 查证：卧虎藏龙 Best Action Choreography = **Yuen Wo-ping**（cthd_en_wiki.txt 奖项行 L461/L583）。程小东未参与该片武指。
- 替代事实（写进卡片）：程小东的竹林战在《十面埋伏》（数十人凌空滑翔投竹矛 vs 地面战斗，china.org.cn 影评原文），威亚写意巅峰在《倩女幽魂》《东方不败》《英雄》。
- 验证路径：**单片维基 awards/infobox 的 Best Action Choreography 行 = 武指署名最可靠快速通道**，比 IMDb fullcredits 快。
- 交叉印证：同库《袁和平_导演美学卡片》已写卧虎藏龙竹林=袁和平执行——既有卡片与简报冲突时以查证为准。

## URL 清单（17 存档，pages/ 目录）
| 文件 | 来源 | 通道 |
|---|---|---|
| ching_en_wiki.txt | 英文维基主条目 | action=raw（9KB，含奖项表/外部链接线索） |
| ching_zh_wiki.txt | 中文维基程小東 | API（**简体条目**——风格评价段是简体字，繁简双试时简体过繁体 MISS 属正常） |
| toutiao_interview.txt | 场库/V电影 2014 专访（一手·白筱娴整理） | 直连/jina 403 → 浏览器 console innerText 全文 |
| kungfucinema_interview.txt | Kung Fu Cinema 2004《Hero》武指访谈（一手·经翻译） | Wayback **20040624id_**（原站已死；2007 capture 只剩 frameset 壳 1-3.5KB） |
| thr_dialogue2008.txt | Hollywood Reporter 2008 Dialogue（一手·Maggie Lee） | 直连 OK（jina 403） |
| scmp_choreographers.txt | SCMP 2021 Richard James Havis 深度文 | 直连部分正文（4 分钟阅读版）；jina 403 |
| sina_bio2008.txt | 新浪娱乐 2008 资料页 | 直连，gb18030 解码（首抓 utf-8 误解码出锟斤拷→重抓原始字节） |
| sina_ghoststory30.txt | 澎湃 2017《倩女幽魂》30 年（新浪转载） | 直连；含波德威尔 170 镜头量化 |
| ghoststory/swordsman2/hero/daggers/cthd/dragoninn _en_wiki.txt | 单片维基 | API（含 redirects=1；action=raw 对歧义标题 404） |
| daggers_chinaorg.txt / daggers_fareast.txt | 十面埋伏英文影评 | 直连 |
| asianwiki_ching.txt | AsianWiki 作品年表 | 直连（辅助） |
| zi_compare.txt | zi.media 对比文 | 反爬残页，不构成证据 |

## 已验证引语锚（写入卡片前全部 grep 通过）
- 一手（toutiao）："诗意的、比较飘逸的" / "我不会让拳拳到肉" / "动作戏只是绿叶" / "特技只是辅助不能替代" / "武术的根在这里" / "先有剧本之后，再有动作这是必须的" / 武指三层定义 / 薪酬 8 万 vs 2 万 / 《白蛇传说》剧本自评 / 风格品牌论
- 一手（KFC，英文翻译版）："As action director, I do my own editing" / "I have always held the camera myself" / "It mostly really is the actors doing it themselves"（英雄威亚演员亲自上阵）/ "Action with comedy is the most difficult" / "not fighting hard style with hard style"（少林足球太极）
- 一手（THR）："pioneering a new style of wuxia ... fast-paced yet ethereal"（记者评处女作）/ 特效不依赖论 / **"Many moviegoers have become sick of high-wire stunts where the actors fly around like in 'Hero'"**（2008 写意威亚自我修正）
- 二手锚：中维"飘逸、潇洒……凌空蹈虚"；新浪"北派大开大合的磅礴气势"；SCMP"looks more 1993 than 1983"（生死决超前时代）+ "reportedly chose Ching to direct"（徐克选人转述）；波德威尔"170个镜头，每个镜头平均不到两秒"；Far East"unlike Crouching Tiger ... owes more to traditional choreography than ballet"（程/袁对照）；china.org.cn"gliding above the bamboo forest" + "Mei hitting the drums with her long sleeves"

## 通道实测（本轮新增）
- **toutiao 文章 403**：browser_navigate 文章 URL 后 browser_console `document.body.innerText` 一次拿全文（快照可能显示别的 tab/跳转页——innerText 才是含文章 tab 的真实内容，照存）。
- **Wayback 已死站 frameset 壳**：返回「Kung Fu Cinema » Home」导航壳（<6KB）≠ 没存档；迭代时间戳，**最早 capture 常含全文**（20040624id_ 取回 28KB）。
- **新浪 GBK**：utf-8 replace 落盘后出现锟斤拷——重抓原始字节 gb18030 解码，损坏文件不可二次解码挽救。
- **英文维基歧义标题**：ghoststory action=raw 404 → API 多标题一次试（A_Chinese_Ghost_Story / (film) / (1987)）自动跟重定向。

## 双口径清单
- 出生年：1952-10-30（中文维基，引裁判文书网）vs 1953-10-31（英文维基/THR/新浪）
- 武指作品数："more than 60 films"（THR）vs 程小东自述约 100 部+1500 部电视（toutiao/KFC）
- 金马 2001 最佳动作设计获奖作品：《我的野蛮同学》（中维/新浪）vs《少林足球》（英维主条目/THR）——中文源为主口径
- 首导《生死决》：自述 1981 左右拍摄 / 英维 1982 / 上映 1983（中维/新浪/金像奖第 3 届）

## 未取到
- 今日头条原链接直连 403（浏览器提取解决，非未取到）；BAFTA 2018 大师课新闻 403；SCMP 后半（订阅墙）；张艺谋谈程小东书法武打原话（"书法入武"仅以《英雄》剧情设定+影评支撑）；《东方不败》绣花针等成片细节的一手/评论原文（仅署名与地位事实）。
