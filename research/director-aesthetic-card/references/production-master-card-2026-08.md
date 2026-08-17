# 制作大师卡片变体 · Burtt 轮 2026-08-08 轮次记录

制作大师研习轮（制作学科·声音/剪辑/配乐/美术）首个实测轮：Ben Burtt（音效设计）。同轮还有 Walter Murch / 杜笃之 / 久石让（并行子代理）。

## 轮次目录与产物

- 轮次根：`C:\Users\HMSJ\Documents\Hermes\_work\制作大师研习-20260808\`（规范.md 在此）
- 本子代理产物：`Burtt\Burtt_制作大师卡片.md`（22KB）+ `Burtt\pages\` 5 个原始存档
- 最终入库目标：`_知识库/references/制作学科/大师卡片/`

## 存档清单（pages/）

| 文件 | 来源 | 关键内容 |
|---|---|---|
| burtt_hollywoodreporter_locarno.txt | THR 2024-08-13（Locarno Vision Award 专访，一手） | 有机声原话/R2D2 人声注入 50%+50%/维达呼吸=水肺调节器/光剑=USC 放映机+CRT+摆动麦克风/瓦力试镜说服 Steve Jobs/Wilhelm 命名故事/声音完成幻象/AI 观 |
| burtt_filmsound_editorsnet.txt | EditorsNet 2002-05-17（Skywalker Ranch，一手） | 光剑=放映机马达+电视显像管干扰原话/"Think outside the box"意外美学/编辑+声音双职 |
| burtt_symbolicsound_walle.txt | Symbolic Sound「the eighth nerve」2024-09-05（一手） | Kyma 伪影当素材/WALL-E=人声+机器/"give the impression of what WALL-E was thinking through sound"/"R2-D2 movie" |
| burtt_filmsound_starwars.txt | FilmSound.org《Sound Design of Star Wars》汇编（二手，引 Film Sound Today 语录） | organic 原话/TIE=大象叫/步行机=冲床+链条/楚巴卡=海象/光剑/爆能枪=拉线/陆地飞车=高速路+吸尘器管/Ewok 语=藏蒙尼改制+"emotional clarity"/太空船=空调声放慢/R2=50%电子+水管口哨 |
| burtt_wiki_raw.txt | 英文维基主条目（2026-08-08 抓取） | 生平/4 奥斯卡/音频黑洞（静音强化巨响）引文/ARP 2600/E.T.=摄影店老年女士/作品年表 |

来源编号 S1-S5 + S6（Google Play《Making Waves》简介，检索快照未存档）。

## 关键方法论成果

1. **预设名言归属证伪**：任务预设「音效是电影的一半」——grep 全部 Burtt 存档 0 命中后，web_search 定位到该句是 George Lucas 与 Coppola 在纪录片《Making Waves: The Art of Cinematic Sound》(2019) 中的宣言（Google Play 影片简介原文 "Francis Ford Coppola and Lucas both declare, 'Sound is half the movie!'"）。处理：不写入 Burtt 正文，改用其本人原话 "it's the sound that completes the illusion and can alter the illusion of the picture"（THR 访谈），诚实声明逐条对照。同类坑先例：卓别林轮（名言不存在）——本次是"名言真实但说话人换人"的变体，更隐蔽。
2. **校验假 MISS 实例**：验证脚本对语料做了 `.lower()` 但短语未 lower → 大片假 MISS；修正为双侧同一归一管道后 33/37 通过，剩余 4 个 MISS 均为引号变体（弯引号’ vs 直引号'）与原文拼写错误（"motel rrom" 原文如此）——不是真 MISS。印证 ㉘ 与 ⑰。
3. **Windows 中文路径**：curl -o 写 `_work/制作大师研习-20260808/...` 报 exit 23；search_files 对同一路径报 IO error。全程改 Python（urllib + ssl 免验证上下文 + open 读写 + Python 内 grep）后稳定。该主机后续轮次（杜笃之/久石让/Murch）同路径，直接用 Python。
4. **视频访谈处理**：StarWars.com / SoundWorks Collection / A Sound Effect 均为视频/播客媒体，无文字转录，标「未取证到」并注明媒体形态；E.T. 声音=老年女士细节仅维基转述（S5），一手未取到，如实声明。

## 对同轮/下轮的可复用面

- Walter Murch：filmsound.org 有大量 Murch 文章/访谈（站内 "Walter Murch Articles" 区），《眨眼之间》可走 Internet Archive；《现代启示录》声音设计访谈多。
- 杜笃之：华语声音设计，通道应转向豆瓣访谈转帖/台湾媒体（放映周报、电影年鉴），对应导演卡片中文渠道坑全适用。
- 久石让：配乐大师，通道=宫崎骏/北野武相关访谈（吉卜力轮已有通道经验）+ 音乐行业刊（Billboard/日本访谈）。
- 妖/志怪声音设计对接点（Burtt 卡第 5 节已写）：人声基底+自然素材+伪装处理公式、Ewok 语真实语言改制法、"familiar things you can not quite recognize immediately"可信度公式、音频黑洞静音法、瓦力"声音=思想外显"法——国风志怪轮可直接引用该卡片。

---

# 久石让轮 2026-08-08 轮次记录（配乐·制作大师）

同批制作大师研习轮第二个实测轮：Joe Hisaishi（配乐）。产出 `久石让\久石让_制作大师卡片.md`（22KB，S1-S12）+ `久石让\pages\` 26 文件。

## 存档清单（pages/）

| 文件 | 来源 | 关键内容 |
|---|---|---|
| hisaishi_wiki_raw.txt | 英文维基主条目（374KB raw HTML→clean 32KB） | 生涯/北野武 7 部合作清单（A Scene at the Sea 1991–Dolls 2002）/minimalist→orchestral 风格/流媒体数据（One Summer's Day 1.09 亿+、Merry-Go-Round 1.58 亿+）/2008 武道馆 25 周年音乐会（1200+ 音乐家、售罄） |
| hisaishi_dazed_interview.txt | Dazed 2023-12-22 一手访谈 | "basic, simple composer"/"可在家弹"/不私人社交秘诀/raw emotions 而非政治/评论者"inner voice"观察 |
| hisaishi_crunchyroll_interview.txt | Crunchyroll 2023-07-25 一手访谈 | 极简主义发现史（Terry Riley 冲击→Reich/Glass/Pärt）/渡边岳夫门下/理解角色故事画面先行/创作作息 |
| hisaishi_variety_interview.txt | Variety 2024-01-05 一手访谈 | 宫崎骏首次不让他看片/"I leave it all up to you"/Ask Me Why 生日短曲变主旋律（片中出现三次）/"I don't write music for the characters"（为世界写作）/前半钢琴+弦乐、塔中更大 |
| hisaishi_latimes_interview.txt | LA Times 2023-11-29 一手访谈（Tim Greiving） | 强主旋律传统总结（melody centric）/《苍鹭与少年》repeating patterns/1984 风之谷首次合作（跳椅讲分镜）/storyboard 阶段进入、配乐与动画同步/"I did not want to describe emotions or scenes through music"/与角色保持距离/Terry Riley 事件 |
| hisaishi_awardsdaily_interview.txt | Awards Daily 2023-12-01 一手访谈 | 鹭鸶出场逐件删乐器到单钢琴音/音乐不做角色解说/40 年不私人社交 |
| hisaishi_guardian_proms_review.txt | Guardian 2025-08-15 Proms 评论 | 2025 BBC Proms 首秀/"John Williams of anime"/"colourful post-minimalism"/指挥 Reich《沙漠音乐》 |
| hisaishi_minimalism_analysis.txt | Classical Source 2025-08-14 Proms 评论 | 《世界末日》=911 后访问 Ground Zero 所作（五乐章）/DG 发行 |
| hisaishi_zhwiki_raw2.txt | 中文维基主条目（URL 编码后成功） | 艺名源自昆西·琼斯（Kuishi Jō→Hisaishi Jō）/简约主义乐派/国立音乐大学师从岛冈让/与宫崎骏、北野武、大林宣彦合作 |
| kikujiro_wiki_raw.txt | 英文维基 Kikujiro 专条 | 原声带 12 曲目（Summer 6:26 等）/独奏大提琴+独奏小提琴编制/北野武父亲原型 |
| hanabi_wiki_raw.txt | 英文维基 Hana-bi 专条 | 与北野武第四次合作/原声带 42:14（Hana-bi 7:09）/管乐+弦乐编制（大管/单簧管/长笛/口琴/双簧管）/威尼斯金狮/Metacritic 83 |
| hisaishi_criterion_heron.txt | Criterion Daily《苍鹭与少年》（2023） | 电影本体评论（影评佐证，非配乐专论） |

来源编号 S1-S12。弃用存档（全部 404/抓错，登记在卡片诚实声明）：redbull.com 久石让访谈、BBC Culture《菊次郎》文章、ClassicFM"Totoro 主题 20 分钟"访谈、Criterion posts/3313（抓错为 Sundays and Cybèle essay）、enwiki Joe Hisaishi in Budokan（无此条目）、zhwiki 未编码 URL 无效页。

## 关键方法论成果

1. **预设修正两例**：①任务预设「旋律即角色」被一手自述推翻——"I don't write music for the characters. I really write the music according to the world that Mr. Miyazaki built."（Variety 2024）；②「菊次郎钢琴主导」无官方证实（维基记载编制为独奏大提琴+小提琴+弦乐），改用"Summer 钢琴版流传最广+钢琴为创作本位"的分析性表述。均写入诚实声明——与导演卡片「预设只是线索」纪律同源。
2. **中文维基 URL 未编码坑**：`curl zh.wikipedia.org/wiki/久石让`（未编码）静默返回「标题无效」页（34KB 看似正常，`<title>标题无效` 才暴露）；`urllib.parse.quote` 编码（`%E4%B9%85%E7%9F%B3%E8%AE%A9`）后一次成功。比 404 更隐蔽。
3. **引文校验**：31 条关键短语批量验证，仅 1 条 MISS 且为弯引号变体（don't vs don’t，Variety 存档用弯引号）——grep 确认后通过；两处"归属错挂"（I leave it all up to you 实际在 Variety 不在 LATimes）靠跨文件验证发现，卡片标注 [S4][S5] 双源正确覆盖。
4. **大 HTML 提取模式**：维基 374KB raw → 剥标签 → 按句切分（`(?<=[.!?]) `）→ 关键词过滤（minimalist/melody/Kitano/曲名）→ 5-10KB excerpts 文件再读，避免 read_file 全量读单行文本。
5. **音乐类 URL 猜测命中率极低**：RBMA/BBC/ClassicFM 三处猜测 URL 全 404——配乐访谈文字版常不存在，404 即标未取证到，不耗轮次。

## 对下轮的可复用面

- Walter Murch：filmsound.org（同 Burtt 轮结论）+《眨眼之间》IA 全文。
- 杜笃之：中文渠道（豆瓣访谈转帖/台湾媒体），导演卡片中文渠道坑全适用。
- 未来配乐/作曲大师轮：颁奖季访谈（Variety/LA Times/Awards Daily）是第一顺位一手通道；维基 Soundtrack 专节=编制事实；流媒体播放量=旋律记忆点量化证据。


---

# 制作大师卡片变体 · 杜笃之轮 2026-08-08 轮次记录（华语声音设计）

同轮第三位（Burtt 之后并行）：杜笃之（Tu Duu-chih）——侯孝贤/杨德昌御用录音师。此前 Burtt 轮预判"通道应转向豆瓣访谈转帖/台湾媒体"，实测成立并扩展。

## 轮次目录与产物

- 产物：`杜笃之\杜笃之_制作大师卡片.md`（151 行，S1-S18 编号，55 处 [S#] 引用）+ `杜笃之\pages\` 18 个存档（16 来源 + 1 PDF + 检索快照）
- 五大重点：①华语声音美学（写实传统/环境声）②侯孝贤合作（悲情城市同步收音/聂隐娘声景）③杨德昌合作（牯岭街声音分层）④声音即历史（台湾语言分层）⑤可复用时机（国风志怪/历史）

## 存档清单（pages/，精选）

| 文件 | 来源 | 关键内容 |
|---|---|---|
| du_taipeitimes_2001_text.txt | Taipei Times 2001-06-17《Fathering sync sound》专访（一手，直抓无壳） | 同步录音之父/70% 台湾电影/晾衣竿吊杆+毯子包摄影机/悲情城市首部全同步/侯借债赠设备/"You make great sound" |
| du_sina_taiwanvoice_text.txt | 新浪转载《南都娱乐周刊》2010-01-25 专访（一手；⚠️ GB2312 编码，见下） | 琼瑶配音批判/演员本尊声音（林青霞）/棉被包摄影机录李天禄/两麦克风一录音机完成悲情城市/侯两句话（培养新人、帮没钱的导演）/导演适配论"一动一静"/张海律评语言分层 |
| du_douban_shengse_text.txt | 豆瓣小组转帖·张靓蓓《声色盒子—音效大师杜笃之的电影路》（大块文化） | 塔可夫斯基事后配音榜样/《海滩的一天》张艾嘉配音连呼吸声/日式地板拟音/恐怖分子"这是事后配音！"/"符号"论 |
| du_filmasia_masterclass_text.txt | Film Asia 2025-03-15 香港大师班报道（AFA Academy 主办，含直接引语） | 洗车场金属门+排风扇低频/汽油桶模拟佛像/人耳辨速度重量/"技术是仆人"金句/《默视录》减法混音/44 提名 13 奖 |
| du_filmcomment_hou_text.txt | Film Comment 2015·侯孝贤《The Assassin》访谈（一手） | 唐代鼓声三千击声景考据/文言文对白挑战（"couldn’t rely on the dialogue"） |
| du_criterion_brighter_summer_day_text.txt | Criterion·Godfrey Cheshire 牯岭街 essay（经 wayback 存档直抓） | 收音机播毕业名单/猫王崇拜声景 |
| du_soc_cityofsadness_text.txt | Senses of Cinema 2003 cteq | 开场黑屏裕仁投降广播+烛光分娩 |
| du_thepaper_nieyinniang_text.txt | 澎湃转载腾讯娱乐戛纳专稿（秦川玺） | 聂隐娘"虫鸣、风声、树叶摩挲"贯穿/无声后环境声涌入 |
| du_medium_languages_text.txt | Medium·Kevin Ding《Languages as Cultural Signifier》（jina 代理） | 悲情城市五语言清单（台/日/沪/国/粤） |
| du_hku_assassin.pdf | HKU Press《The Assassin》专书 PDF 预览（37 页） | ⚠️ 预览版正文不全（杜笃之仅见索引 100/108/122），只引可见段落 |
| du_zhwiki_text.txt / du_enwiki_text.txt | 中英维基主条目 | 生平/十三座金马/技术里程碑年表 |
| du_ntdtv_2012_text.txt | 中央社 2012-11-05（经新唐人转载） | 半夜独采巷弄雨水声/讲座报道 |

## 关键方法论成果（本轮新坑/新通道）

1. **GB2312/GBK 老站编码坑（新浪实测，新）**：新浪 2010 老页面 meta 声明 `charset=gb2312`，按 UTF-8 硬解码产生乱码+替换符+NUL 字节 → 转换文本后 read_file 直接误判 "Binary file"。解法：下载后先 `re.search(r'charset=["\']?([\w-]+)', head)` 检测编码再 `data.decode(enc, errors='replace')`；转文本时过滤控制字符（`''.join(ch for ch in txt if ch >= ' ' or ch == '\n')`）。**老中文媒体站（新浪/搜狐/网易旧页）默认怀疑 GBK 系编码**。
2. **站点级封锁的处置（locationsound.cn 实测）**：同期录音网对当前网络 SSL UNEXPECTED_EOF 连接被拒（urllib/浏览器均失败），r.jina.ai 也 422——判定为站点封锁而非工具故障。处理：不纠缠，其核心故事（杨德昌半夜带杜爬山录汽车声）在已抓到的新浪一手访谈原文中逐字存在（"我们两个真的半夜两三点收工后，带着录音器跑到山上去找这些声音"），**以一手替代印证 + 诚实声明注明"该站未获存档、核心内容经一手访谈证实"**。搜索快照（DDG 摘要）可作线索但不可引原文。
3. **学术出版社 PDF 预览版坑（HKU Press 实测）**：hkupress.hku.hk 专书 PDF 直抓 + pymupdf 提取可用，但**预览版只有部分页**——杜笃之仅出现在书末索引（书页 100/108/122），正文章节不在预览内。教训：PDF 提取后先确认正文覆盖（grep 关键词命中索引≠正文可引），引用仅限可见段，诚实声明"预览版"。
4. **豆瓣搜索被污染时的替代**：web_search 查"豆瓣 长评"返回色情/无关垃圾（反爬污染）——别硬搜，用已知豆瓣 URL 模式直抓（本轮豆瓣小组话题 group/topic/31779394 直连成功，印证步履不停轮"小组话题=r.jina.ai 直抓主帖"通道；Rexxar API 仍是长评主通道）。
5. **校验执行**：38 条引文验证，2 处修正——① "把喇叭放到水壶里"实属 S5（豆瓣转帖）而验证脚本误查 S4（新浪），**MISS 先核对引文归属存档再怀疑来源**（印证 ⑤/expect_keys 纪律）；② Film Comment 原文 "couldn’t" 为弯引号，卡片引文改与原文逐字一致（印证 ㉝）。其余 36 条一次通过。
6. **声音设计大师的行业 masterclass 报道 = 新引语通道**：AFA Academy（亚洲电影大奖学院）每年颁奖季前办大师班，Film Asia/官方站报道含大师直接引语（2025 杜笃之香港大师班即例）——**声音/后期类大师优先查 afa-academy.com + filmasia.net**；台湾官方传记站 taiwancinema.bamid.gov.tw 有英文档案页。

## 对后续轮次的可复用面

- Walter Murch：filmsound.org "Walter Murch Articles" 区（Burtt 轮已注）；《眨眼之间》Internet Archive。
- 久石让：吉卜力轮通道 + 音乐行业刊。
- 华语声音/剪辑/美术大师通用通道：台北时报专访（taipeitimes.com 直抓无壳）→ 新浪/网易人物专访（注意 GBK）→ 豆瓣小组传记/访谈书转帖 → 中央社（新唐人/大纪元转载）→ AFA Academy masterclass → Criterion/SoC essay 侧证。
- 杜笃之卡 §5/§6 的国风志怪对接（语言分层=政治分层、古代声景逆向工程、低频心理压迫、汽油桶拟音）可直接被后续创作轮引用。
