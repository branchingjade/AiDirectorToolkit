# 姜文《鬼子来了》单片研习轮地图（2026-08，director-aesthetic-card 第二十五轮）

## 产出
- `研习报告/鬼子来了_研习报告.md`（26.7KB，203 行）
- `技法卡片源稿/鬼子来了_技法卡片.md`（16.5KB，122 行）
- 存档：19 个 `pages/jiangwen_guizi_*`（零存量全新抓取）

## 来源清单（研S1-研S26）

| 编号 | 存档 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | jiangwen_guizi_enwiki_raw.txt | 英维 Devils on the Doorstep raw | 剧情/主题/制作（黑白+最后四分钟转彩+断头POV）/审查史/获奖/参考文献索引 |
| 研S2 | jiangwen_guizi_zhwiki_raw.txt | 中维 raw | 剧情/广电总局意见原文/尤凤伟争议/军舰行进曲 |
| 研S3 | jiangwen_guizi_baike_jina.txt | 百度百科（jina） | 创作背景/48万卷胶片/结尾红色/明格拉「上善若水」/观点周刊费里尼·库斯图里卡 |
| 研S4 | jiangwen_zhwiki_raw.txt | 中维姜文导演条目 | 靖国神社声明/鸿门宴三机位圆轨访谈/CCTV-6 播出 |
| 研S5 | jiangwen_enwiki_raw.txt | 英维 Jiang Wen | seven-year ban/Guardian 报道 |
| 研S6 | jiangwen_cnn_talkasia.txt | CNN Talk Asia 2007（Rao 采访） | 黑白「it's beautiful」/酒越陈越香/3-to-2 比例 |
| 研S7 | jiangwen_timeasia_devils.txt | Time Asia 2000-07-24 Corliss（wayback） | 两官员赴戛纳/七年禁令/I feel like Ma Dasan/电影局批评原文 |
| 研S8 | jiangwen_ward_academic.txt | Ward《New Cinemas》2004 摘要 | 「absurdity and arbitrary cruelty of war」 |
| 研S9 | jiangwen_lijie_bw.txt | Li Jie《J. of Chinese Cinemas》2012 摘要 | 黑白在彩色时代的功能/戏仿纪录片传统 |
| 研S10 | jiangwen_guizi_rt.txt | Rotten Tomatoes 评论页 | Holden NYT 评语（Closely Watched Trains/No Man's Land 谱系） |
| 研S11 | jiangwen_guizi_review_1266247.json | 豆瓣《姜文的十个为什么》（网易访谈转帖，14317 有用） | 姜文十问一手自述 |
| 研S12 | jiangwen_guizi_review_1098723.json | 豆瓣丁小云（8435） | 结尾红色自述/《前世今生》/签字订约底光/驴上马 |
| 研S13 | jiangwen_guizi_review_1038191.json | 豆瓣谷之雨《荒诞派刀法》（850） | 掸蚂蚁/道德困境/「我」=戈多/瘸腿隐喻 |
| 研S14 | jiangwen_guizi_review_9601575.json | 豆瓣壹戈《细节》（738） | 因荷而得藕/驴上马=猪吉心理/小驴吃奶蒙太奇/疯七爷 |
| 研S15 | jiangwen_guizi_review_4602184.json | 豆瓣（十个为什么重复转帖，636） | 大岛渚《饲育》对照线索 |
| 研S16 | jiangwen_guizi_review_1029099.json | 豆瓣 pepper_ann《人物性格分析》（494） | 《我的摄影机不撒谎》转引/朝日新闻/视听语言 |
| 研S17 | jiangwen_guizi_review_2141309.json | 豆瓣 Vic（105） | devils 象征/结尾手扛拍摄 |
| 研S18 | jiangwen_guizi_review_2008236.json | 豆瓣半导体（54） | 羊性/八婶子唱曲 |
| 研S19 | jiangwen_guizi_review_4966933.json | 豆瓣（56） | 装备对比/取景地（蔚县西固庄/黄花城水长城） |
| 研S20 | jiangwen_guizi_review_1039826.json | 豆瓣甩尾火狐（38） | 开头油灯/小碌碡之死 |
| 研S21/23 | jiangwen_guizi_review_7605283/9401611.json | 豆瓣短评（~400字） | ⚠️ 生态存档未入正文 |
| 研S22 | jiangwen_guizi_ebert.txt | rogerebert.com 该片 404 | ⚠️ 负取证：Ebert 无此片影评 |
| 研S24 | jiangwen_guizi_jubenpro_search.txt | juben.pro 搜索（422 失败） | ⚠️ 剧本未取证 |
| 研S25 | jiangwen_guizi_douban_search.json | rexxar search | subject id=1291858 定位 |
| 研S26 | jiangwen_guizi_rexxar_reviews.json | rexxar 长评列表 | 选稿（1924 条总数） |

## 本轮新坑与配方（比 SKILL.md 轮注更细）

1. **豆瓣 rexxar 长评 JSON 字段是 `user` 非 `author`**——首个解析脚本 KeyError: 'author' 崩溃。review 对象顶层键：id/title/useful_count/content/user/create_time/rating；作者名在 `user.name`。长评全文通道：`https://m.douban.com/rexxar/api/v2/review/{id}`（带 UA+Referer），12 篇连抓零失败，间隔 1.5s。列表通道：`https://m.douban.com/rexxar/api/v2/movie/{subject_id}/reviews?start=0&count=20&sortby=hotest`，按 useful_count 选稿。
2. **subject id 零猜号定位**：`https://m.douban.com/rexxar/api/v2/search?q=<urlencode 片名>&type=movie` → subjects.items[0].target.id + rating（豆瓣 9.3/72 万评）。比猜号/爬网页快，一次成功。
3. **同一角色人名跨影评变体**：谷之雨全文 20 次「马大山」（0 次马大三），壹戈/丁小云用「马大三」——引文必须照录原文人名并在引文后加注（「谷之雨原文用'马大山'，本报告他处统一'马大三'」）；校验清单按原文人名 grep，统一名查询会假 MISS 后误以为引文错误。
4. **同一台词双版本照录**：疯七爷台词壹戈记「我一手一个掐死两」、pepper_ann 记「我一手一个，掐把死俩……」——两版并存、分别标注来源，不合并成一个引号引文（合并=伪造引文）。
5. **英维中文译文引文轻量标注**：中文引号段若译自英维，紧接「（译文，原句 "..."）」附英文原句（本轮回 3 处：完全失去敌意/太卑劣/让皇军蒙耻）。比费里尼轮 75 段全量配对轻，但英文原句必须能过存档匹配。
6. **中维 raw 繁简差异假 MISS**：zhwiki raw 的 wikilink 目标可能是繁体（`[[日本軍國主義]]`），文档按简体引述。校验 norm 顺序：剥 wikilink → 去空白标点 → **繁简归一**（转简）→ 匹配。别把繁简差异判为引文错误（本轮 91 条中唯一"MISS"即此）。
7. **CNN Talk Asia = 中国导演英文一手访谈通道**：`r.jina.ai/http://www.cnn.com/2007/WORLD/asiapcf/07/31/talkasia.<slug>.html` 直抓 18.9KB 全文（Talk Asia 系列采访中国影人）。本轮回含黑白动机「it's beautiful」/纪录片质感/黄种人零损失/酒越陈越香/三部作品 3-to-2 比例（「One is not yet been released, one was not allowed to be released, and one was released」）。发现路径：英维 raw References 段的 cnn.com talkasia 链接。
8. **Time Asia 老报道经英维 ref archive-url wayback 直抓**：`edition.cnn.com/ASIANOW/time/magazine/2000/0724/china.jiangwen.html` 的 20110127184557 快照含审查内幕全文（两官员赴戛纳、要求交底片、七年禁令、电影局「语言冒犯/裸女/风格粗俗」批评、姜文「I feel like Ma Dasan. The film has become real life」）。老报道的审查/争议细节密度高于维基转述。
9. **学术订阅文摘要上限**：ingentaconnect（Ward 2004）与 tandfonline（Li Jie 2012）订阅全文不可得，r.jina.ai 抓摘要页（Abstract+Keywords 完整）——以摘要论点+关键词为证据上限，正文标注「仅摘要」。发现路径：英维 raw References 段期刊文献 URL 直接 jina 抓（零猜 URL）。
10. **任务预设台词 0 命中的处置模板**：「我不管你是日本兵还是国军，你们都得走」全库 0 命中——正文不写；诚实声明逐条列出（含可能的来源猜测）；用取证到的等效事实替代预设（本片：结尾转彩+断头 POV+头滚九次眨眼三次微笑，英维 [研S1]）。「全片最暴力的段落却是最安静的」同理无逐字出处→以转彩/断头视角/微笑三证据替代并声明「系本报告提炼」。

## 校验结果
- 91 条引文（手工清单逐条 grep）：90 OK + 1 繁简差异确认（非错误）
- 正文 [研S#] ⊆ 附录清单 0 越界；附录未引用编号（研S5/10/15/19/25/26）=生态/定位登记，不硬凑
- 定稿前修正 5 处：人名变体×2（马大山/马大三）、译文附原句×3、双版本台词×1
- 校验方法：正则自动提取引文配对误报率高（引号跨段/编号配对错位），**手工维护引文清单（引文原文+编号）逐条 norm 匹配存档最可靠**；norm 含 wikilink 剥壳（`[[X|Y]]`→Y）、去空白标点、去弯引号
