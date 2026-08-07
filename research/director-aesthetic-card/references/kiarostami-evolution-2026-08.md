# 阿巴斯深化轮来源地图（2026-08）

手法体系深化·童年乡野/存在追问双线跨作品矩阵。零存量全新建档 19 档 [S1-S19]（自建编号，无主卡片第五种变体）。产出：`技法卡片源稿/阿巴斯_手法体系深化.md`（44KB，257 行）。88 引文 0 MISS。并行轮地图：`references/kiaro-cherry-study-2026-08.md`（樱桃单片轮）。

## 存档清单（pages/）

| 编号 | 文件名 | 来源 | 关键内容 |
|---|---|---|---|
| S1 | kiaro_abbas_enwiki_raw.txt | 英维导演条目 | 寇科三部曲/地震 40,000/四十天单镜头/Ten 车载/Akrami 观众参与论/"instinctual thirst for survival"对照句/树之喻 |
| S2 | kiaro_style_enwiki_raw.txt | 英维风格专条 | 提问者原话转述（"raises questions, rather than answers them"）/远景距离论/声画辩证/Close-Up"evidence" |
| S3 | kiaro_where_enwiki_raw.txt | 英维《何处是我朋友的家》 | 还作业本剧情/塞佩里诗题/Rosenbaum 三片总括（"raise more questions than they answer"） |
| S4 | kiaro_life,_enwiki_raw.txt | 英维《生生长流》 | 地震寻人/结尾大坡+字幕滚动/30,000 口径（三口径并记：40,000/50,000/30,000+） |
| S5 | kiaro_through_enwiki_raw.txt | 英维《橄榄树下的情人》 | 片中之片/"The audience is left to wonder" |
| S6 | kiaro_taste_enwiki_raw.txt | 英维《樱桃的滋味》（并行轮存档复用） | Ebert 1 星原文/Rosenbaum "Fill in the Blanks"/Marsh Slant 结尾论/烂番茄共识 |
| S7 | kiaro_certified_enwiki_raw.txt | 英维《合法副本》 | 原品/复制论题/Denby "double fiction"/"simplest film" 导演原话 |
| S8 | kiaro_close-up_enwiki_raw.txt | 英维《特写》 | 真人重演审判/身份主题 |
| S9 | kiaro_the_enwiki_raw.txt | 英维《风带着我来》 | 等待结构（"the event they are waiting for... does not occur"） |
| S10 | kiaro_ten_enwiki_raw.txt | 英维《十》 | 十段车内对话/车载结构 |
| S11 | kiaro_koker_enwiki_raw.txt | 英维《Koker trilogy》 | 三部曲定义/导演拒绝命名/50,000 口径/Martin "diagrammatical" |
| S12 | kiaro_zh_main_raw.txt | 中维导演条目 | 寇科三部曲中文表述/导演自认三部曲/译名 noteTA |
| S13 | kiaro_wikiquote_raw.txt | 英维 Wikiquote | 树之喻/极简主义原话/Close-Up 自述（每条带来源 URL） |
| S14 | kiaro_guardian2005_live.txt | Guardian 海伊节访谈 live 全文 | 极简主义原话（"progressing towards a certain kind of minimalism... Bresson's method of creation through omission"）/地震后三天/儿童方法论/《十》离轨自述 |
| S15 | kiaro_pbs2009.txt | PBS Frontline 2009 | "show, don't narrate"原话/未完成的故事原话/拒绝展示一切/trees and roads 摄影母题 |
| S16 | kiaro_crit_posts_7026.txt | Criterion Hamrah《Stay Near the Tree》 | 结尾 video 逐段描述/Ershadi 路边拦车/导演坐路虎应答演员/"meant to conceal, even to frustrate" |
| S17 | kiaro_crit_posts_55.txt | Criterion Cheshire 旧 essay（1999） | "no films, only relations between films"/寇科三部曲+导演自认三部曲（preciousness of life）/Badii 三段谈话 |
| S18 | kiaro_crit_posts_6565.txt | Criterion《Behind the Wheel》 | 三部曲总括（neorealist-like odyssey→sliding fact/fiction→behind the scenes） |
| S19 | kiaro_crit_posts_6516.txt | Criterion《Three Weeks》回顾展 | Godard 语/纪录-虚构边界总括 |

本地转引：[卡费穆]费穆_手法体系深化.md（空气论 S7/散点透视 S12）、[卡贾]贾樟柯_手法体系深化.md（旁观者 S11/站台量化 S22/声音作曲 S26-27）、[卡樱桃]樱桃的滋味_技法卡片.md（研S12=彭明辉文转引 Sterritt《Film Comment》2000 访谈中文译文，引文[1]-[17]）。

## 新通道（本轮实测）

1. **Wikiquote=导演名言索引**：en.wikiquote.org/wiki/<导演名> raw（API 同维基）每条名言自带来源 URL → 回源一手访谈。阿巴斯轮靠它一次定位 Guardian 2005 海伊节访谈 + PBS Frontline 2009 访谈两个原文通道。Wikiquote 只作索引不作引文源。
2. **Guardian 旧访谈 live 经 r.jina.ai 直抓**：wayback 经 jina 只回 521 字节存根，live URL 一次抓回 26KB 全文（2005-04-28 hayfilmfestival2005）。回退序：live 先行。
3. **Criterion posts/55 作者验归属**：jina markdown 丢 byline，作者 Godfrey Cheshire 经并行轮 wayback HTML 版（kiaro_taste_criterion.txt "by Godfrey Cheshire"）确认——jina 丢署名时查 wayback HTML 版本。

## 新坑/配方（校验 norm 层，代码已验证）

1. **Wikipedia API 429 限流**：`for attempt in range(4): try: ... except: sleep(3*(attempt+1))` + 条间 sleep(2)；10 条 9 成 1 重试即过。
2. **`<ref>` 未闭合吞正文（㊶ 代码化）**：`re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)` 在 enwiki raw 存在无配对 `</ref>` 的 `<ref name=...>`（cite 模板未闭合）时会吃到远处闭合标签、删掉大段正文→批量假 MISS。修复：
   `re.sub(r"<ref[^>]*/>"," ",s)` → `re.sub(r"<ref[^>]*>(?:(?!<ref).)*?</ref>"," ",s,flags=re.S)`（负向前瞻防跨 ref）→ `re.sub(r"<ref[^>]*>"," ",s)` 清残留开标签。
3. **{{Blockquote}} 模板吞引文（㉛ 代码化）**：enwiki 影评引文常整体包在 `{{Blockquote|text="..."}}` 内，通用 `{{}}` 剥壳连引文一起删。先提取保内文再剥其余模板：
   `re.sub(r"\{\{(?:[Bb]lockquote|[Qq]uote|[Cc]quote)\|(.*?)\}\}", lambda m: m.group(1), s, flags=re.S)`。
4. **jina markdown 下划线斜体**：Criterion 经 r.jina.ai 的文本用 `_斜体_`（下划线）非 `*`——norm 需同时剥 `_`（kiaro_crit_posts_6565 "the neorealist-like odyssey of _Where Is the Friend's House?_" 即此因）。
5. **&nbsp; 实体**：`html.unescape` 必须在 norm 第一步（"40,000&nbsp;people died" 断匹配）。

## 预设处置记录

- **「电影一半是观众完成的」**：英文全量检索（Guardian/PBS/Criterion×2/英维×2/Wikiquote）"half"+"audience" 零逐字命中。经并行樱桃卡片 [卡樱桃·研S12]（彭明辉文转引 Sterritt《Film Comment》2000 访谈中文译文）定位两句最接近出处：引文8「我在电影中留下空格，不是等待观众去填写我想要的答案，而是期待他们照自己的思考去填入自己所想要的。」+ 引文9「我看电影时常常只看到一半就离开……我宁可用我自己的方式去结束一部电影。」——推测中文圈通行表述系两句浓缩转述。**通用教训：导演名言通行转述若英文无逐字源，先查 Film Comment 系访谈中文转引（豆瓣长评通道），再标注「浓缩转述，非逐字」**。
- **寇科三部曲称谓**：通行归类（critics dubbed / 被電影評論家稱為），导演拒绝（"accident of place"），自认三部曲=后两部+樱桃（preciousness of life）——按通行归类分级表述，未升格。
- 地震死亡数三口径并记（40,000 [S1]/50,000 [S11][S14]/30,000+ [S4]）。

## 未取证清单

- 各片均镜时长/镜头总数量化数据（无影迷逐帧统计存档）。
- 《何处》结尾花朵镜头、《生生长流》双筒望远镜搬家具夫妇、《橄榄树》结尾白色身影——均只到剧情摘要级证据。
- 《剧情作者电影密码.md》任务指定转引资产 find 全盘不存在（回测报告/ 亦无），诚实声明处理。
- 「寇科三部曲=后两部+樱桃」表述仅见 Criterion essay 转述与维基转引，导演直接访谈原话未单独取证。
