# 铃木清顺轮（2026-08-09，日片大正浪漫/超现实导演轮）

导演卡片 + 手法体系深化双文档轮（输出 `_work/v2-导演研习-20260809/铃木清顺/`，19 存档 suzuki_*，90 条定向引文 86 HIT 0 真 MISS）。核心对象：大正浪漫三部曲（流浪者之歌 1980/阳炎座 1981/梦二 1991）、日活 B 级期（1956-1967）、解雇-封杀-复出史。

## 新通道（日片导演轮可复用）

- **SoC 无 great-directors 专条时的第一代偿源 = festival-reports 分类专文**：`?s=<导演名>` 搜索命中 `2000/festival-reports/suzuki/`（Stephen Teo《Seijun Suzuki: Authority in Minority》2000，31KB）——含**导演原话转引链**（歌舞伎三要素自述 "patterned his films after traditional Kabuki and its three points of departure: the love scene, the murder scene and the battle scene"、超现实自述 "Why make a movie about something one understands completely?"，两者都转引 Vancouver Sun 1991 Katherine Monk 采访，尾注给了出处）、色彩符号体系（红白=义理/黄=性）、每镜一两种主色、人工布光随情绪变色、gesaku 传统（佐藤忠男）。发现路径 = SoC 站内搜索页 grep `suzuki` 链接；与朴赞郁轮⑥"cteq 单片专文代偿"并列：**festival-reports 与 cteq 都是专条缺位时的代偿源**，festival-reports 常是导演级总览（信息密度更高）。
- **Midnight Eye slug 新格式再验证（今敏轮记录的 /interviews/<slug>/ 第二例）**：铃木的 slug 是 `midnighteye.com/interviews/seijun-suzuki/`（2001 威尼斯访谈：色彩=把戏/电影是手工品/时间地点无所谓/B 级片自由度/音乐防无聊）。⚠️ **英维 External links 段记的旧 URL `midnighteye.com/interviews/seijun_suzuki.shtml` 已 404**——按新格式 `<slug>/` 抓，旧 .shtml 链接别信。
- **Guardian 老文章（2006）直抓无壳**：`theguardian.com/film/2006/jun/30/1` urllib 直连 200，`article-body-commercial-selector` div 正则提取 8.5KB 全文（"I was never rebellious... I was just mischievous!"/entertain the audience/粉蓝西装/蝴蝶 femme fatale 全在此）——英维 ref 里发现的 URL 直接抓，不用 jina。
- **豆瓣 rexxar 对日片老片裸片名 suggest 全中**：`流浪者之歌`/`阳炎座`/`梦二`/`杀手烙印`/`东京流浪者` 五个裸片名一次全命中 subject id；热门长评列表拉回后按标题关键词（美学/歌舞伎/形式主义/超现实/大正）选稿，9 篇高价值长评全文一次到手（含《流浪者之歌》全本中译剧本 review/6667087，田中阳造/洪旗译，26KB 分场证据）。
- **日片中文影评作者通道**：不一定驴驴（原载 Mtime，review/1165325，47 有用）与鬼脚七（原载《看电影》2014，review/6649141，69 有用）的 Mtime/杂志影评整篇转帖在豆瓣长评——**日导轮中文一手密度最高的二手源**（大正时代史/泉镜花新派剧传统/FirumuKabuki 称谓/木村威夫美术全在此），扫列表时按作者名关键词（不一定驴驴/鬼脚七/午夜场/看电影）优先抓。

## 新坑

**① 同名异片 subject 双命中（本轮最大坑，差点误挂数据）**：豆瓣 subject_suggest 对裸片名「流浪者之歌」返回**两个 subject**——`1303525` = 库斯图里卡《流浪者之歌》1988（EMIR KUSTURICA）与 `1401329` = 铃木清顺《流浪者之歌》1980。两个都拉了 reviews 列表（同 pinyin 前缀碰撞的 subject 级变体），写作时一度把库版的「142 分钟院线版与 270 分钟导剪版」讨论（review/16002588）当铃木版数据写进诚实声明——靠定稿前数据核对发现（该讨论片长与英维铃木版 145 分钟矛盾）。**处置三件套**：① suggest 多命中时按年份/导演核对归属再拉 reviews；② reviews 列表 title 里带年份的（如"142分钟院线版与270分钟导剪版的差异"）先确认 subject id 再引用；③ 发现的同名异片警示写进诚实声明（"该数据属于库斯图里卡版，与铃木清顺 1980 版无关，本文未采用"）。与英雄轮「pinyin 前缀跨片碰撞」、小津轮「百度百科歧义词条」同族：**中文渠道同名实体按 subject id 核验，别按片名猜归属**。

**② 自写 strip_html 提取未 unescape = HTML 实体假 MISS**：SoC festival-reports 文直接剥标签提取后残留 `&#8220;`/`&#8217;`/`&quot;`（"Why make a movie..."整条假 MISS）、Guardian 残留 `&#x27;`（"Making films for me..."假 MISS）——**凡自写剥标签提取的存档，norm 第一步必须 `html.unescape()` 或手动替换实体表**（&#x27;/&#8217;/&#8220;/&#8221;/&quot;/&nbsp;/&mdash;/&ndash;），与 ⑯「jina markdown 无实体」互补：jina 源没这问题、自提取 HTML 源必有。

**③ 任务预设三部曲成员错误 → 诚实声明显式纠正**：任务预设「大正三部曲=流浪者之歌/阳炎座/悲愁物语」——实际《悲愁物语》（A Tale of Sorrow and Sadness, 1977）是复出前高尔夫题材片，非三部曲成员；第三部为《梦二》(1991)。三部曲成员定义有英维三片条目互证（"surrealistic psychological dramas and ghost stories linked by style, themes and the Taishō period (1912-1926) setting"）。**预设片序/成员错误时，以多源互证的条目定义为据，纠正写入诚实声明**（库布里克深化轮「预设片序时间线错误」同族）。

## 引文校验备注

- 90 条定向引文 86 HIT；4 条 MISS 中 1 条实体转义假 MISS（见坑②）、3 条是写作侧转述非逐字（「镜头衔接十分跳跃」vs 存档「镜头衔接十分跳跃」/「让人最终放弃了分辨真实和虚幻的企图」——按存档原文逐字修正后 0 MISS）。
- 自动提取引文（正则抓引号段）产生 52 条假 MISS（跨行/括号内容/提示词块误当引文）——**判定以手写定向短语清单为准**（⑬ 纪律再证），自动提取只当线索。
