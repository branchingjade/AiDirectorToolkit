# 费穆《狼山喋血记》单片研习轮来源地图（2026-08）

费穆导演本体零存量首轮（无《费穆_导演美学卡片》），产出《狼山喋血记_研习报告》+《狼山喋血记_技法卡片》。新抓 20 档 + 存量复用 4 档 = 研S1-S24，186 引文 0 MISS。

## 存档对照（pages/）

| 编号 | 存档 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | feimu_wolf_enwiki_raw.txt | enwiki Blood on Wolf Mountain | 寓言定位（九一八以来中日冲突）、Time 1977 ref、片长 70min、1936-11 |
| 研S2 | feimu_enwiki_raw.txt | enwiki Fei Mu | 「often seen as an allegory on the war with Japan」、王家卫「only film poet」、小城之春 HKFCS 第一 |
| 研S3 | feimu_zhwiki_raw.txt | zhwiki 费穆(导演) | 「被认为是国防电影的代表作」、「开启了中国诗化电影的先河」 |
| 研S4 | feimu_wolf_zhwiki_raw.txt | zhwiki 狼山喋血记 | 存根 |
| 研S5 | feimu_wolf_baike_jina.txt | 百度百科（带 lemma ID 的 URL） | 沈浮/费穆编剧、内容提要全本、32 位影评人联名推荐「在中国电影史上开始了一个新的纪元」、别名冷月狼烟录、片长 69min |
| 研S6-13 | feimu_wolf_review_*.txt | 豆瓣长评 8 篇（8593204/12586615/13912455/13972427/17726331/5459940/14113731/2884410） | 蓝苹磕牙+逼加戏、警官学校拒借狼犬→动物园、取景以远/情节以淡/构图以简/动作以虚、蒙太奇三段分析、寓言两解、狼狗扮狼 |
| 研S14 | feimu_wolf_interests.json | 豆瓣短评（478 条中前 30） | 黑狗成/火娃剪影镜头/Jasmine_长乐小城之春奠基/友荣文革批判/介意反绥靖 |
| 研S15 | feimu_wolf_sohu_jina.txt | 搜狐号《电影北上》之八（鲍盛华报告文学节选） | 沈浮「你脑子快」邀稿、冷月狼烟录→狼山喋血记、1936-11-20 卡尔登+新光大戏院公映、尘无 1936-11-22《大晚报·每周影坛》影评引文、丁亚平《中国电影通史》评价、哑巴临终喊「打狼」 |
| 研S16 | feimu_wolf_zhihu_q.txt | 知乎张雍《空气与寓言的交织》 | 转引李少白（1936年5月国防电影口号）、陈墨《费穆电影论》儒家圣人精神、老张动摇叙事、「打狼还是不打狼，已经不再是一个选择题」 |
| 研S17 | feimu_wolf_jiangqing_wayback.html | ibseninchina 江青论文 wayback | 「directed and revised as screen-play by Shen Fu, Fei Mu and Zhou Daming」、1936 夏排练 |
| 研S18 | feimu_wolf_langshan_yao_followlyrics.txt | followlyrics 狼山谣歌词 | 全词（含「四方人呐喊」） |
| 研S19 | feimu_wolf_langshan_yao_qupu123.txt | 中国曲谱网 | 安娥词/任光曲/黎莉莉演唱 |
| 研S20 | feimu_wolf_dianying_wayback.html | dianying.com wayback 快照 | 演员表顺序首列刘琼、蓝苹/张翼/黎莉莉不按字幕顺序 |
| 研S21 | feimu_wolf_jiangqing_zhwiki_raw.txt | zhwiki 江青 | 蓝苹 1936 下半年入联华出演本片 |
| 研S22 | feimu_wolf_time1977_wayback.html | Time 1977 wayback | 负面取证：快照正文无狼/费穆字样，「Japanese refused to acknowledge...」句未直接核验 |
| 研S23 | feimu_wolf_crossroads_enwiki_raw.txt | enwiki Crossroads (1937) | 「In this way, Crossroads joins films like Blood on Wolf Mountain...」第三方英文文献 |
| 研S24 | feimu_air_essay.txt（存量复用，前代理抓） | 北京大学艺术学院转载《文艺研究》2020-5 空气说/同化论论文 | 费穆《略谈「空气」》直接引文（无「是」字版）、自我批评原话、空气「四种方式」、脚注[27]确认原刊《时代电影》1934年第6期第22页、影片矩阵含狼山喋血记 |

## 新坑与配方（本轮实测）

1. **豆瓣 subject_suggest 返回空数组 `[]` 的兜底**：`movie.douban.com/j/subject_suggest?q=<片名>` 全空（非 need_login 壳，是空数组）时，改走 `r.jina.ai/https://duckduckgo.com/html/?q=<片名>+豆瓣+movie.douban.com`，从结果 grep `movie.douban.com/subject/[0-9]+` 一次命中（本片 1461808）——别在 suggest 端点死磕。
2. **百度百科裸 item URL 404**：`baike.baidu.com/item/狼山喋血记`（无 ID）404；DDG 结果里的 `item/<词条>/3430611` 带 lemma ID 才可抓——搜索结果的 URL 直接用，别手拼裸名。
3. **jina 渲染的百度百科文本中文引号被转义为 `\"`**（如 `狼是\"山神\"管的`）——校验 norm 必须 `s.replace("\\","")` 否则必 MISS（黄土地轮繁简映射缺字的同族变体）。
4. **歌词/字幕带行内时间戳拆句**：followlyrics 每行 `[00:37.61]` 时间戳把相邻歌词句拆开——校验 corpus norm 先 `re.sub(r'\[\d{2}:\d{2}(?:\.\d+)?\]','')` 再比对，否则整句 MISS。
5. **enwiki wikilink 目标+显示文本拼合假 MISS 再例**：`since the [[Japanese invasion of Manchuria|Invasion of Manchuria]] in 1931`——初引「Japanese invasion of Manchuria in 1931」拼合目标与显示文本，校验 MISS 后改引显示文本「Invasion of Manchuria in 1931」（杨德昌轮 ㊿①同型第三例）。
6. **报告文学/媒体长文 = 1930s 原始影评引文转引通道**：搜狐号《电影北上》报告文学全文引尘无 1936 影评、公映日期、编剧始末——老民国片轮的 1930s 报刊影评常以这种方式存活在自媒体长文里（标注「经报告文学转引，原始报刊未直接核验」）。
7. **学术论文脚注 = 一手引文原刊信息的确认通道**：北大转载《文艺研究》论文脚注 [27] 直接给出费穆《略谈「空气」》原刊《时代电影》1934年第6期第22页——把「原刊未核验」升级为已确认；论文正文的费穆引文（无「是」字版）与知乎转引版（多「是」字）措辞不同，双版并记以学术版为准。
8. **zhwiki 用字核对**：首次 zhwiki 搜索把「喋」误编为「喷」（URL 编码错误）导致条目「不存在」假象——标题探测前先核对简体/繁体/错别字；费穆是消歧义页，真实条目「费穆 (导演)」。
9. **归属校验脚本假阳性句式**：对「研S# 同：「引文」」这类引文前标记的句子，按「引文后 80 字符内最近研S#」匹配会误报 6 处——人工复核全部为假阳性，归属实际正确（标记在引文前或句中）。
10. **双口径并存**：编剧署名三源（百科=沈浮费穆 / ibseninchina=沈浮费穆周大鸣 / 英维仅费穆）、片长 69/70 分钟、歌词「四方人呐喊」vs「四万人呐喊」——均并存标注不强行统一。

## 校验记录

- 186 引文 0 MISS（严格 norm 或 CJK 标点不敏感兜底命中）；英文引文必须严格命中。
- 引文修正实例：①enwiki wikilink 拼合（见坑 5）；②豆瓣 14113731 原文「在美丽的山谷的画面，哟优美的歌声中结束了全片」——初引漏「哟」，修正为原文并标 [原文如此]；③zhihu 原文「而且当她拒绝…」初引漏「她」；④12586615 原文「尤其是影片最后哑巴也张口说了一声狼」初引漏「也」——引文逐字复制后再归一，删字必 MISS。
- 自己提炼的八字短语（如「内容刚劲、手法清丽」）不占「」引号，标「原话之提炼」——引号只留给逐字引文，校验才可审计。

## 本片核心结论（供深化轮转引）

- 打狼论=国民性三派图谱（主战/绥靖迷信/麻木归咎）+ 哑巴临终开口转折；外部争议=32 位影评人联名推荐 vs 嫌隐晦 vs 文革坏样板。
- 寓言体 vs 抒情体：尘无「内容刚劲、手法清丽」；豆瓣影迷指认长镜头调度为《小城之春》奠基、低机位大天空构图。
- 狼=狼狗扮演、借狗困难（警官学校拒借→动物园）→「写实美学先天缺失」反逼以虚写实。
- 费穆导演本体仍零存量，本片报告可作《费穆_导演美学卡片》首块基石；同导演存量：feimu_xc_review_*/feimu_review_*（小城之春 20 档）、feimu_ls_review_*（本片 5 档重复）、feimu_baike.txt（费穆词条）、feimu_zhwiki_director_clean.txt。
