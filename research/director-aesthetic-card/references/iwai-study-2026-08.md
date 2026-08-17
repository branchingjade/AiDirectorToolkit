# 岩井俊二轮（2026-08-09，日式青春/唯美导演轮）

导演美学卡片 + 手法体系深化双文档轮。产出落盘 `_work/v2-导演研习-20260809/岩井俊二/`，存档 32 个。

## 本轮通道矩阵（日片/青春唯美导演轮可复用）

- **Metrograph Journal 访谈 = 日本导演一手通道（本轮第一顺位）**：`metrograph.com/shunjiiwai-minsookim/` 直抓 237KB HTML 无壳，<article> 提取 14KB 全文——2026 年岩井 4K 回顾展（Metrograph 迷你回顾展）配套对谈，含一手金矿（情书原是黑白 Ozu 式电视剧、佐佐木昭一郎"以纪录片风格拍虚构"师承、寺山修司 8mm 模仿、不给演员详细指导）。发现路径：DDG/Bing 搜 `"<导演名>" metrograph OR journal interview`；Metrograph 是纽约独立影院，做导演回顾展/重映时必查其 Journal 栏目。
- **上海青年报 epaper = 华语媒体一手访谈通道**：`why.com.cn/epaper/webpc/...` 直连 curl/urllib 可抓（56KB），标题带"唯美"的深度专访含导演原话（"要拍出像音乐一样流动的画面"）；jina 429 时直连原站优先。
- **界面新闻 = 一手访谈通道**：`jiemian.com/article/<id>/` 经 r.jina.ai 直抓 20KB 无壳，文内嵌导演原话+创作背景（书信起源/哀而不伤/后期配乐流程）。
- **开放学术期刊 PDF = 导演视觉美学研究通道**：Dean Francis Press（deanfrancispress.com）等开放获取期刊有《A Study of the Visual Aesthetics of Japanese Director Iwai Shunji》类论文，pymupdf 提取 29KB——学术级定性（过曝+颗粒=家用 DV 质感=documentary quality、物哀 material sadness），密度高于一般影评，且常带导演身份/运动定位句（"flag-bearer of Japan's New Cinema Movement"）。
- **豆瓣 suggest 直连全空 → r.jina.ai 代理**：本轮再次验证（侯孝贤轮同款），一次全中情书 1292220/四月物语 1292371/花与爱丽丝 1308820。
- **⚠️ 豆瓣 subject id 猜错教训再证**：凭记忆猜 1308856 实为《爱情黑盒子》（Little Black Book），suggest 输出被截断导致误用——suggest 结果必须完整读回，id 用前核对 title/year 字段。

## 本轮新坑

- **zhwiki 条目简繁混排（引文必须逐字 grep）**：岩井俊二 zhwiki 条目正文是简体（"他凭借1995年青春爱情电影"）但框架/其他段是繁体——不能按条目语言假设引文字形。写引文时凭印象用了繁体「憑1995年青春愛情電影」→ 校验 MISS；grep 原文发现是简体。**任何引文先 grep 原文再落笔，简繁以存档实际字形为准**。
- **PDF 提取文本的断行连字符 = 假 MISS 源**：学术论文 PDF 提取后 "documentary qual-ity"（行尾断词），norm 需 `s.replace('-','')`（与 ⑱ 软连字符 U+00AD 同族，PDF 是显式 '-' 断行）。
- **wikilink 剥壳再证**：`[[High-definition video|HD]] [[digital video]]` 不剥壳时 "shot on HD digital video" 假 MISS——⑦ 的独立实例，norm 正则 `\[\[([^\]|]*\|)?([^\]]*)\]\]` 保留管道后显示文本。
- **插入字假 MISS**：短语「他凭借1995年…」vs 原文「他却凭借1995年…」（原文多「却」）——MISS 先查原文确切措辞（⑥ 同族），别急着怀疑来源。
- **反例取证纪律（预设"手持摄影"的处置升级）**：预设"手持摄影（纪录片感）"未获直接证据，但找到**反面证据**——影迷逐帧分析指出《四月物语》奔跑戏"采用了一个居中的固定机位拍摄"（非手持）。处置：① 取证替代事实链（师承佐佐木纪录片式拍虚构 + 莉莉周 DV 颗粒纪实质感 + 导演纪录片作品）② 反例写进诚实声明 ③ 正确定位改为"媒介层纪实质感+画面层唯美构图"——比单纯标"未取证到"更进一步，供后续轮参考。

## 验证结果

62/62 引文校验通过（opencc t2s + wikilink 剥壳 + 断行连字符删除 + 引号归一）；S1-S25 编号卡片/深化双文档共用一套，一致性 ALL OK。修正 4 处：简繁字形 1、搜索摘要误引→存档原文替换 1（画面锚点"白窗帘"引文来自 web_search 摘要非存档，改用存档 S13/S16 确切措辞）、"把时间"→"将时间"逐字 2。

## 存档清单（pages/）

维基 5（enwiki/zhwiki 主条目 + 情书/四月物语/花与爱丽丝片条目）、百度百科 jina、一手访谈 3（jiemian/why/metrograph）、学术 PDF、豆瓣长评 10 篇 + 列表 JSON 3 个、负面取证 2（SoC 搜索页无专条、Midnight Eye 索引无访谈）。
