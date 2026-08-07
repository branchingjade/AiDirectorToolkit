# 张艺谋轮来源地图（手法体系深化，2026-08-07）

手法体系深化变体第九例（张艺谋）。前置：`张艺谋_导演美学卡片.md`（含"色彩倒推故事"发现）；本轮主题=跨作品演变（色彩分区/对称构图/人海调度/女性悲剧四条链）。产出：`技法卡片源稿/张艺谋_手法体系深化.md`（263 行，16 组来源）。

## 本轮新增存档（pages/，15 个）

**英文维基 raw 5**（一次 curl 全成）：
- `yimou_wiki_Red_Sorghum__film_.txt` — 金熊、颠轿剧情、顾长卫引文 "The use of red showcases the rich vitality of the sorghum fields"（引 Yvonne Ng, Kinema 1995）、Rodekohr "Human Wave Tactics" 哈佛专章、张艺谋导演阐述（"The sense of legend makes this film attractive"）
- `yimou_wiki_Ju_Dou.txt` — 染坊、Technicolor（注意原文是 "vivid [[Technicolor]] process" 带链接括号）、中国首部奥斯卡提名、国内禁映
- `yimou_wiki_The_Story_of_Qiu_Ju.txt` — 隐藏摄像机街景、Ebert "more information about the lives of ordinary people"、金狮、巩俐沃尔皮杯
- `yimou_wiki_To_Live__1994_film_.txt` — 戛纳评审团大奖+葛优影帝、禁拍两年、皮影戏自加（小说没有）、张艺谋访谈转述（"era without hope"）、服装随 1940s→1970s 朴素化
- `yimou_wiki_Not_One_Less.txt` — 新现实主义/纪录片风、"people playing variations of themselves"（演员真名演真职业）、隐藏摄像机+自然光、阿巴斯影响、金狮、戛纳退赛

**中文维基 raw 5**：红高粱（花轿/金熊/尿酒传奇）、菊豆、秋菊打官司、活着、一个都不能少。⚠️ 标题变体：`一個都不能少_(電影)` 51 字节失败，**简体 `一个都不能少` 成功**——与阿飞轮相反方向，简体 404 换繁体、繁体 404 换简体都试。

**豆瓣长评 5**（Rexxar API，含 JSON 存档）：
- `yimou_douban_review_8282529.json` 《浅析〈大红灯笼高高挂〉的色彩与构图》388 有用 — **"本片构图多采用轴对称，陈府的大院拍的方方正正……就像陈府那些个看不见的条规条例"=对称构图直接证据**；色彩四阶段（暖→大红→阴冷→全白）
- `yimou_douban_review_1027697.json` 《光明下的黑暗》1706 有用 — 灯笼/大红/家庭/雪地/戏子五组反差
- `yimou_douban_review_1404075.json` 《其实只有一个女人》5832 有用 — 五女人五命运（雁儿渴望/颂莲徘徊/梅姗抗争/卓云臣服/大太太心死）
- `yimou_douban_review_1017337.json` 《原始生命力的崇拜》2029 有用 — 颠轿仪式拆解、九儿啜泣止节奏、宗教式野合构图
- `yimou_douban_review_10379896.json` 《红色生命史诗》63 有用 — 红色意象三阶段（大红→浅粉→结尾日食血红）

另存长评列表 2 份备用：`yimou_douban_rtrl_reviews.json`、`yimou_douban_hgl_reviews.json`。

## 渠道实测（本轮新增经验）

1. **subject_suggest 查询坑**：`q=英雄 张艺谋`/`红高粱 张艺谋`/`英雄`/`英雄 2002` 全部返回空；裸片名 `大红灯笼高高挂`、`秋菊打官司` 成功。→ **常见短片名+导演名/年份组合不可靠，先试裸片名**。
2. **豆瓣 id 兜底来源 = 中文维基条目外部链接的 `{{豆瓣|<id>}}` 模板**：红高粱 id 1306505 由此一次取得（grep zhwiki raw 的 `豆瓣|` 模板即可）。suggest 失败时优先此路。
3. **猜 id 危险**：凭记忆猜 1291546 拉长评，实际是《霸王别姬》——英雄的豆瓣 id 本轮未取到，正文标"未取证到"，不硬凑。
4. **长评选题启发**：视觉美学/技法类研究扫标题关键词 **色彩/构图/对称/意象**（本轮 8282529 因此命中轴对称直接证据）；访谈类扫 访谈/节选/对谈（已有规则）。列表按 useful_count 排，>300 有用的优先抓全文。
5. 豆瓣长评 JSON 的 content 字段含 `<div id='content'>` 包裹和 `[img=N:C]` 占位符——剥标签后即为正文。

## 校验脚本要点（本轮实测，防假 MISS）

- **先 strip `[[` `]]` 再比短语**：维基 raw 的 "vivid [[Technicolor]] process" 会把 "vivid Technicolor process" 断成假 MISS（Ju Dou 案例）。
- **繁简映射表必须覆盖短语全部字**：缺 麗→丽、顏→颜、種→种 等常见字导致假 MISS（"华丽有余"因缺 麗 映射假 MISS；"五種顏色"因缺 顏 假 MISS——后者未在正文引用，属脚本多余检查）。
- 大小写双方 lower（"The sense of legend" vs "the sense of legend"）。
- **长中文校验脚本别用 bash heredoc**：大字典+中文引号报 "unexpected EOF while looking for matching `'`"——write_file 落盘再 `python 脚本.py` 执行（本轮实测 2 次 heredoc 失败后改落盘成功）。

## 未取证清单（已写进卡片诚实声明）

- 英雄/黄金甲"对称构图"直接文献（影评明说"对称"二字）未取到——大红灯笼有"轴对称"原文，后两段仅构图证据+分析延伸
- 英雄豆瓣 id / 英雄豆瓣长评未取到
- 三线划分（色彩叙事/仪式大场面/写实人文）与"女性悲剧母题"= 分析框架，非张艺谋自述；但 zhwiki 张艺谋条目"影片一改张艺谋以往的风格，采取了纪实风格、偷拍、大量采用非职业演员"证明写实线的独立性是当时媒体共识
- 各片精确镜头数/均镜时长未取证到

## 关键引文位置（grep 关键词 → 文件）

| 引文 | 存档 |
|---|---|
| 轴对称/方方正正/条规条例 | yimou_douban_review_8282529.json |
| never clearly shown（老爷不示人） | yimou_wiki_Raise_the_Red_Lantern.txt |
| exists solely for the eyes（Ebert） | yimou_wiki_Raise_the_Red_Lantern.txt |
| era without hope / at the mercy of others | yimou_wiki_To_Live__1994_film_.txt |
| human wave tactics（Rodekohr 章） | yimou_wiki_Red_Sorghum__film_.txt |
| 纪实风格、偷拍 / 完全采用非职业演员 | yimou_zhwiki.txt（张艺谋主条目） |
| 10,000 soldiers / cleaned with mechanical efficiency | yimou_wiki_Curse_of_the_Golden_Flower.txt |
| approach the throne a little closer（Ebert 英雄） | yimou_ebert_hero.txt |
