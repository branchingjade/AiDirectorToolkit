# 侯孝贤轮来源地图（2026-08）——新增导演全新建档

产出：《侯孝贤_导演美学卡片.md》（8 节，32 编号来源 S1–S32，100 条引文 0 MISS 定稿）
校验脚本：film-suite-research/verify_hou_card.py（本轮自写，假 MISS 修复实例归入 SKILL.md 校验规则 ㉑㉒；jina 斜体 `_` 断子串已在 ⑱ 覆盖）

## 存档清单（44 个，pages/ 下）
- 维基：hou_wiki_raw.txt（en 主条目 55KB）、hou_zhwiki_raw.txt（繁体 41KB）、hou_style_wiki_raw.txt（Cinematic style 专条 404 跳过）
- 百科：hou_baike_jina.txt（133KB，含侯孝贤谈沈从文"阳光底下的事"原话转引）
- Criterion（CF 壳 → jina 全过）：hou_criterion_8407/3754/7395/8403_jina.txt（30/9.6/27/7.7KB）
- SoC：hou_soc_hou/bresson/interview/optics/puppetmaster.txt（Fergus Daly 2001 / 布列松×海上花 / 2015 戛纳圆桌访谈 / 2006 spotlight 最好的时光 / 戏梦人生）
- 豆瓣：hou_rexxar_*_list.json（5 片 reviews 列表）+ hou_review_*.txt（24 篇全文转文本）
- 检索存档：hou_soc_search.html、hou_ddg_criterion*.txt、hou_ebert_cdx.json（空）

## S# 编号对照（正文↔存档↔关键内容）
- S1 Criterion 3754 Kent Jones 对谈：拍真吃饭法/限制即自由/费里尼破框/成濑
- S2 SoC 2015 戛纳圆桌：长镜头理念原话/海上花 30 镜/真实性铁律/反心理学解释
- S3 新京报朱天文映后座谈（review/12194588）：沈从文"天的角度"/"远远的冷冷的"/戈达尔跳接
- S4 侯孝贤高峰论坛记录（review/5510260）："非演员会紧张"/"实是一切的基础"/苍凉
- S5 南国逐段拉片（review/1024650）："再远一些，再冷一些"/43 段约 50 镜/175 秒摩托长镜
- S6 吴念真自述（review/16005542）：删煽情戏
- S7 SoC 布列松文：海上花 37 镜逐一淡入淡出/无一硬切
- S8 SoC optics：均镜 82s/106s/"Who's Bazin?"/Bordwell 实务起源论
- S9 SoC Fergus Daly："shots appear empty but that's an error"/中国版画留白
- S10 Criterion 8407：沈从文 river 引文/"keep a distance, be cooler"/风柜斗殴单镜
- S11 Criterion 7395 Jean Ma：8 分钟开场单镜/北野武评吃饭/悲情城市饭桌对比
- S12 en wiki 风格段 / S13 zh wiki（长镜头空镜头固定镜位）/ S14 百度百科
- S15 剧本转帖（review/15275339，1155 行分场稿）：序场 A/B；宽美写日记场景（L302/L499/L960）但日记文字未见于转帖
- S16 拉片长评（review/13040010）：文清哑巴来历/宽美日记全文/《悲情城市十三问》引文/"拍出天意"
- S17–S32 详见卡片附录来源清单

## 渠道实测备忘（新配方/坑）
1. **subject_suggest 直连全空 → r.jina.ai 代理一次成功**：五部裸片名直连全 `[]`，经 `https://r.jina.ai/https://movie.douban.com/j/subject_suggest?q=<urlencoded>` 全部命中 id（悲情 1294194/童年 1300572/恋恋 1292330/风柜 1299436/南国 1303458/戏梦 1302941）。rexxar reviews/review 端点直连照旧 OK（iPhone UA + Referer）。
2. **Criterion Cloudflare "Just a moment..." 壳（~5.5KB）→ r.jina.ai 直抓全文成功**（4 篇 essay），无需 CDX。
3. **标题带"剧本"的长评=占位垃圾坑**：review/14634942 仅 441 字符（"哔哔哔..."占位符），抓回后核对 content 长度/正文开头再入库。
4. **zh wiki 简体条目是 #REDIRECT**：抓 `侯孝賢`（繁体）才有 41KB 正文。
5. **任务预设未证实即诚实声明**：Ebert 悲情城市 CDX 空；Criterion 单片 essay（悲情城市/童年往事等）DDG site: 搜不到——任务预设"Criterion 发行"未获证实，写入诚实声明。
6. **假 MISS 三个新源**：① jina markdown 斜体 `_Flowers of Shanghai_` 断子串（norm 加 `s.replace('_','')`）；② Criterion 引导演访谈记者插语断句（"X," he told me, "Y" 格式——引文拆段+标注，校验短语也拆段）；③ 繁简映射补字两端不同步 → `str.maketrans` ValueError（雲/云 必须同加）。
7. **reviews 标题关键词新命中**：高峰论坛/映后座谈/独家记忆 类标题=一手转述通道（5510260 侯导原话、12194588 朱天文座谈）；"我希望我能拍出自然法則底下人們的活動"这类导演原话做标题的长评=理念金矿。

## 预设纠正记录
- "侯孝贤无公开剧本" → 被 review/15275339 剧本转帖纠正（卡片诚实标注"影迷转帖，非官方出版物"）。
- "克制到无声"（用户创作参照系表述）非侯原话 → 改用可取证表述：侯"远远的冷冷的"（S3）、"苍凉"自我总结（S4 转述）、廖庆松"冰山火炉"（S24 转引）。
- 均镜/镜头数双口径并列：海上花 30 镜（S2 侯自述）vs 37 镜无一硬切（S7 学者文）。

## 未取证清单
Ebert 影评（CDX 空）、Criterion 单片 essay、SoC Great Directors 专条（站点搜索未命中）、《恋恋风尘》《风柜来的人》《童年往事》剧本、Cinematic style 专条（404）。
