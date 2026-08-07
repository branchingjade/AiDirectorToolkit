# 谢晋《芙蓉镇》单片轮来源地图（第三十三轮，2026-08）

**轮次类型**：单片研习轮（时代反思/底层命运/人性史诗创作极）；谢晋导演本体零存量，全新建档 36 个。产出《芙蓉镇_研习报告.md》+《芙蓉镇_技法卡片.md》，独立 [研S#] 编号体系（映射列登记并行轮 [并1-2] 与存量 [卡姜文·姜文百科]）。

## 存档对照表（pages/xj_*）

| 编号 | 存档 | 来源与关键内容 |
|------|------|---------------|
| 研S1 | xj_hibiscus_enwiki_raw.txt | 英维 Hibiscus Town（"scar drama"、Time Out Adair 引文、奖项、164 分钟） |
| 研S2 | xj_xiejin_enwiki_raw.txt | 英维 Xie Jin（父母自杀 2002 访谈、贾樟柯评论、宋祖德事件；ref 挖出 Jump Cut 访谈与 MIS 链接） |
| 研S3 | xj_jumpcut_int.txt | **Jump Cut no.34 1989 谢晋一手访谈全文**（Da Huo'er 纽约采访；福特/勒鲁瓦/罗姆影响、"儿不嫌母丑"乐观主义原话、姑祖母守寡故事、70 遍《偷自行车的人》、对第五代评价）——本轮第一金矿 |
| 研S4 | xj_mis_peoplesdirector.txt | Moving Image Source Leo Goldsmith 2008《The People's Director》（"Survive by any means, as cattle and horses do"、**Zhu Dake "Xie Jin's model" 英文一手记载**、第五代批评原句、万人悼念） |
| 研S5 | xj_osu_hibiscus.txt | OSU Kirk Denton 课程材料（Marchetti 四要素风格定义 "aesthetic crucible"、"bourgeois humanist"） |
| 研S6 | xj_chinaorg.txt | china.org.cn 英文简介（"distorted and alienated individualities"） |
| 研S7 | xj_furongzhen_zhwiki_raw.txt | 中维《芙蓉镇》条目（剧情全述、"伤痕与反思电影"+"谢晋模式"直接证据、**ref 含 CNKI 学术文献**、成本票房、奖项表、王村更名） |
| 研S8 | xj_xiejin_zhwiki_raw.txt | 中维谢晋条目（《谢晋电影选集》"反思卷：天云山传奇、牧马人、芙蓉镇"） |
| 研S9 | xj_xiejin_baike_browser.txt | 百度百科谢晋词条浏览器快照（姜文评谢晋原话、黄蜀芹尹鸿综合评、《人物》杂志评） |
| 研S10 | xj_sfa_wb.txt | **上海电影家协会石川《说不完道不尽的〈芙蓉镇〉》2015**（选角/编剧掌故、"脸谱化"导演回应、王秋赦原型=钟惦棐"流氓无产者"回信、石牌坊三件道具、吊脚楼实拍、成本酬金）——幕后级一手转述 |
| 研S11-34 | xj_review_*.txt（24 篇） | 豆瓣长评 2645~4 有用（wokanliao=亲历者vs第五代、xingshi=性史、shenti=谷燕山阉割、zhengzhi=食色互喻、shishi=白对联、guanchang=平反签字、minge=民歌歌词、jiachangban=加长版 30+ 删减处、chongduxiejin=钟惦棐/朱大可转述、kongjian=空间调度+谢晋"不能忘记"转引、renwujianxi=首尾米豆腐呼应、shenggikou=牲口台词） |
| 存量 | jiangwen_guizi_baike_jina.txt | 姜文百科（"1987年，在电影《芙蓉镇》中崭露头角，获第10届大众电影百花奖最佳男演员奖"）——姜文对照锚点 |
| 并1 | xj_rev_谢晋和第五代.txt | **并行谢晋导演轮中途落盘**（代际年龄对照：谢晋 43 岁 vs 张艺谋 16-26/陈凯歌 14-24；"横跨第三、四、五三代"孤例论）；同文也出现在并行牧马人长评 xj_muma_review_9790654.txt |
| 并2 | xj_rev_我对导演艺术的追求.txt | 并行轮存档（谢晋自述选集摘录 p82-87："没有简单化的英雄，没有脸谱化的坏蛋"——与"戏曲五行选角"并置成人物观张力） |

## 六新坑（校验/通道实现级）

1. **豆瓣 rexxar 搜索端点需登录**：`m.douban.com/rexxar/api/v2/search?q=...` 返回 `{"msg":"need_login","code":103}`（92 字节壳）；免登录定位 subject id 必须走 `movie.douban.com/j/subject_suggest?q=<URL编码>`（手机 UA 即可，返回 JSON 数组按 year 选条；芙蓉镇=1297880）。先试 j 端点，别再踩 rexxar search。
2. **archive.today 对 curl 弹 CAPTCHA → 原站直连**：archive.ph 快照页返回 "One more step" CAPTCHA 壳；同一篇 Jump Cut 老文（ejumpcut.org/archive/onlinessays/JC34folder/XieJinInt.html）**原站直连成功 19KB**（latin-1/iso-8859-1 解码；英维 ref 的 archive.today 链接只是障眼法，站点本体还活着）。老学术站（ejumpcut 等）优先直连原站，archive.today 只作最后手段。
3. **中文老站 wayback 快照编码别猜 GBK**：sfa.org.cn 快照（web.archive.org 20231229121121id_）先按 gb18030 解码全乱码（"璇翠笉瀹岄亾..."），实测为 **UTF-8**。解码循环：for enc in [utf-8, gb18030, gbk, big5]: try decode → 以关键词命中（"芙蓉"/"谢晋"）为判据，先入为主必翻车。
4. **jina 403 时百度百科走浏览器，正文在快照文件里**：r.jina.ai 被限流 403 时，browser_navigate 到 baike.baidu.com 可用；但 **console 的 `document.body.innerText` 返回 0**（快照上下文问题），可靠路径是读 `C:/Users/HMSJ/AppData/Local/hermes/cache/web/browser-snapshot-<hash>.txt` 快照文件（116KB 含全文，可直接 grep "人物评价"等章节）。百度百科词条导航栏 ref 编号（如 [ref=e650]）标注了章节位置，`grep -n` 定位高效。
5. **write_file 落盘文档引号被规范化为直引号**：write_file 会把中文弯引号 `"` `"` 规范成 ASCII `"`。自动引文提取器的正则必须同时配直引号与弯引号（`r'[""]([^""\n]{6,90})[""]'` 两种形态都写），否则整批引文被当成跨行垃圾误报；且提取结果要排除含 markdown 标记（`**〔〕[]`）的假引号对。
6. **norm 管道补两类删除**：①**半角标点也要删**（`!`/`,`/`.`——文档"活下去！"对存档"活下去!"（半角!）假 MISS）；②**删空格而非压空格**（`re.sub(r'\s+','')`——存档"反思卷： 天云山传奇"冒号后空格 vs 引文无空格假 MISS；只 `re.sub(r'\s+',' ')` 压成单空格不够）。

## 并行轮覆盖同前缀存档坑（新变体）

并行谢晋导演轮中途落盘 xj_rev_*.txt 系列（18:40-18:48），且**我自抓的 xj_review_shenggikou_8624937.txt 被补全/覆盖**（初读 2081B 无"牲口"→ 校验时 6193B 完整）——与"中途新增存档"（聂隐娘轮）不同，本轮是**同前缀文件被覆盖**。纪律：引文校验循环内重新读盘（不要用早先 read 的缓存文本）；发现 xj_rev_* 后按 [并N] 前缀登记进来源清单（[并1-2]），金矿（代际对照/谢晋自述摘录）补入正文并标注"并行子代理落盘，出处 URL 未登记"。

## 预设处置记录

- ✅ "反思电影"代表作 / 四清→文革跨度 / 扫街母题 / 活下去主题 / 导演语法：全部多源取证成立（Adair "ranges from '63 to post-Gang of Four'"、中维"伤痕与反思电影"、2645 有用"亲历者 vs 第五代"、牲口台词双源互证=影迷记录+ MIS 英文箴言）。
- ⚠️ "1986《电影艺术》'谢晋模式'论战"**载体未取证到**：实际可证载体=中维 ref 的 CNKI 学术文献（窦旸《走出"谢晋模式"》《电影新作》1990 第 1 期、杨春凤等《从〈芙蓉镇〉看谢晋电影风格》《电影文学》2010）+ 朱大可批评（豆瓣长评 1604299 转述 + MIS 英文一手记载 "the form that critic Zhu Dake derisively called 'Xie Jin's model'"）+ 钟惦棐《谢晋电影十思》"时代有谢晋而谢晋无时代"（豆瓣转述）。《文汇报》为 1986 主战场之一属通说未逐字取证。**教训：论战类预设先查中维 ref 的 CNKI 链接（zhwiki 条目 ref 常挂学术期刊元数据页），比搜索引擎可靠**。
- ⚠️ "每个中国人都欠谢晋一个道歉"**未取证到直接出处**：搜索引擎全线反爬（必应空结果、百度验证码、DDG anomaly、startpage anubis、s.jina.ai 403）→ 写入诚实声明并列相关事实（第五代批评、宋祖德事件、万人悼念），不采信为事实表述。

## 校验记录

83 条手写引文清单 + 6 条并行/复核引文 = 0 MISS（norm 含：剥 wikilink 管道 `[[反右运动|右派]]`→显示文本、删空格、删全/半角标点、删引号书名号）。自动提取 152 条剩余 MISS 全为合法分类（节引省略号分片、提炼句、自译引文[英文原句已过]、AI 提示词、任务预设说法）。编号对账：正文 21 个 [研S#] 全部在清单内，无越界。

## 通道备忘

- **上海电影家协会 sfa.org.cn** = 华语老片幕后一手转述通道（发现路径：中维 ref 域名 grep `sfa.org.cn`；石川文含选角/道具/实拍掌故，导演原话级密度）；wayback 快照可用。
- **MIS（movingimagesource.us）**：SSL 证书 hostname 不匹配（www），用 `http://` 或 `ssl.CERT_NONE` 直抓；Leo Goldsmith 谢晋纪念长文=论战英文一手记载集中地。
- **china.org.cn 老文直连可抓**（http 即可）。
- 论战/批评史类中文预设的取证组合拳：中维 ref CNKI 转引 + 英文纪念文一手记载 + 豆瓣长评转述，三级互证，缺一级标"未取证到"。
