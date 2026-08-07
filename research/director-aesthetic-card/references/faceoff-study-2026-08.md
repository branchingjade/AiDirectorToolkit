# 《变脸》(Face/Off, 1997) 单片研习轮来源地图（第十七轮，吴宇森补代表作）

## 产出
- 研习报告: film-suite-research/研习报告/变脸_研习报告.md（110 行）
- 技法卡片: film-suite-research/技法卡片源稿/变脸_技法卡片.md（121 行，6 张卡）
- 编号体系: [研S1]-[研S20] 独立单片编号 + 「对应主卡」映射列（存量源 4 个映射到吴宇森主卡清单表）

## 新抓存档（pages/woo_faceoff_*）
| 文件 | 内容 |
|---|---|
| woo_faceoff_enwiki_raw.txt | en.wikipedia Face/Off 全 raw（37KB，Writing/Casting/Filming/Soundtrack/Influence/Critical response/Box office） |
| woo_faceoff_zhwiki_raw.txt | zh.wikipedia 奪面雙雄（简体标题 变脸_(1997年电影) 为重定向，API 返回 `#REDIRECT [[奪面雙雄]]`、revid None 但非 missing——revid None ≠ 条目不存在，读 content 的 #REDIRECT 目标再抓） |
| woo_faceoff_imsdb.html/.txt | IMSDb 英文拍摄稿 "Revised 9/10/96"（正文在 `<td class="scrtext">` 内，正则提取后 192KB）——**1997 好莱坞大片拍摄稿可直抓**，纠正"IMSDb 多为空壳"的印象 |
| woo_faceoff_review_6284171.txt | 豆瓣长评=曹轶译中译剧本全本（1941 行，50KB，27 有用、列表第 11 位——低有用数剧本长评坑再次应验） |
| woo_faceoff_review_*.txt | 豆瓣长评 14 篇全文（Rexxar API，含拉康镜像理论长文 4569431 等） |
| woo_faceoff_baike_2343510.txt | 百度百科《变脸》主词条（83KB，幕后花絮金矿：斜杠片名/Erewhon=nowhere 反写/磁力靴 180 双 13 磅/快艇戏原为终极标靶设计/凯奇拒演/绿屏改实拍/镜宫） |
| woo_faceoff_suggest.json / reviews.json / reviews2.json | Rexxar 列表存档（subject id 1292659 裸片名 suggest 一次命中） |

## 关键配方（新）
1. **豆瓣长评=好莱坞片剧本中译全本通道（通道新实例，此前仅华语/欧洲/日本片）**：review/6284171 标题即《变脸》电影剧本，正文署"文/迈克·韦布、迈克尔·科勒里 译/曹轶"，与 IMSDb 英稿同稿系（开场旋转木马逐字对应）→ **双稿互证法**：英稿+中译同稿系可放心作剧本证据；但主角名不同（英稿 JON ARCHER / 中译与成片 Sean Archer）→ 中译应译自更新稿；终局也不同（双稿=枪击+螺旋桨毁脸；成片=鱼枪 speargun）→ 剧本版 vs 成片差异写入诚实声明。
2. **百度百科多同名条目 id 定位**：裸词条 `item/变脸` 直连 403、jina 404（多同名条目无自动重定向）→ DDG 经 jina 搜 `site:baike.baidu.com 变脸 吴宇森 1997` 提取候选 id（2343510/11072998/2343527）→ 逐个抓取后 grep 片名/导演频次分辨主词条（2343510: 1997×24/Face-Off×2/吴宇森×44）。
3. **成片台词 vs 剧本台词层级**："好像是在照镜子，但其实不是""看来我们还是做自己比较合适""I'm the king" 仅影迷长评记录（4569431），剧本双稿均无——标"影迷记录台词"层级；"我要你每次照镜子，看见的都是我的脸" 剧本有据（中译 L1871/英稿 L6087）——标剧本台词。反向使用：剧本台词 + 影评描述交叉证实成片画面（教堂白鸽：剧本无鸽，靠 Salon 专访吴宇森亲口 + 3 篇影评）。
4. **预设证伪实例**："水上飞机"（seaplane）全来源零记载→实际名场面为快艇追逐（speedboat chase，MTV 奖官方定名+San Pedro 实拍+Vulture 替身论）；"镜屋枪战"预设取证成功（剧本 L1377-1381/英稿 L4505-4522 + 4 篇影评 + 百科"镜宫"）。

## 校验坑（新，已并入 SKILL.md ㊶㊷）
- 未闭合 `<ref>` 吞正文：zhwiki 吴宇森条目 17 开 14 闭、3 个未闭合，naive `.*?</ref>` 正则把"屈伏塔翻身"段删光 → strip_refs() 逐对扫描修复（先删自闭合、逐个配对、未闭合只删开标签）；enwiki 同坑（RT consensus 被吞）。`&nbsp;` 实体断匹配（"$100&nbsp;million"）→ html.unescape 修复。
- 剧本破折号 "-----" vs "——"：引文块假 MISS 2 处，逐字恢复 "-----" 后 0 MISS。
- 节引分片正则扩展：`re.split(r'…+|-----+', p)` 覆盖省略号与连字符两类分隔符（原 ⑬ 只拆省略号）。

## 校验记录
- 101 条定向引文短语：首轮 95/101（6 MISS 全为清洗 bug 3 + 测试短语笔误 2 + 引号形态 1），修复后 101/101。
- 文档「」引文块自动提取复核（≥8 字）：首轮 8 块 4 MISS（全为节引+破折号假 MISS），升级 find_quote_split 后 8/8。
- S# 一致性：正文 [研S1]-[研S20] ⊆ 来源表，无越界。

## 会话脚本（pages/ 留存，可作下轮模板）
- _woo_faceoff_fetch.py — Rexxar 长评批量抓取（剥标签前先 `re.sub(r'</p>|<br\s*/?>','\n',c)` 保段落）
- _woo_faceoff_verify.py — 101 短语双语校验（strip_refs/unescape/繁简映射/全空白剥离/引号删除/双侧变体）
- _woo_faceoff_blockcheck.py — 「」引文块自动提取 + 节引分片复核（find_quote_split）

## 未取证清单
- Ebert 影评原文页未直抓（经英维 Critical response 段转引原话，已标注"经英维转引"）
- 成片台词 "好像是在照镜子，但其实不是" 等未逐帧核对（影迷记录层级）
- 拍摄日期双口径：英维 1997-01-04 开拍 vs 中维 1996-10-31 开拍——并存不统一
