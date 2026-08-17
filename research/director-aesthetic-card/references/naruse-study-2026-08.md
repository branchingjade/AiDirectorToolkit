# 成濑巳喜男导演轮（2026-08-09，日片导演轮；双文档：导演美学卡片+手法体系深化）

产出：《成濑巳喜男_导演美学卡片.md》《成濑巳喜男_手法体系深化.md》（已入库 `_知识库/references/导演美学卡片/`）
存档：`导演研习-20260809B/成濑巳喜男/pages/`（40 文件，naruse_* 前缀）
校验：156 条引文 0 MISS；S1-S20 双向对账闭环（复用主卡片编号，深化文档不另起炉灶）

## 本轮新通道（日片导演轮适用）

1. **Criterion 站内搜索页 = essay URL 发现一手通道（直连 curl 可过）**：
   `curl -A "<浏览器UA>" "https://www.criterion.com/search?q=<导演名>"` → 200/179KB（urllib 同 URL 403、curl 200——UA 形态差异）；
   `grep -oE 'current/posts/[0-9]+-[a-z0-9-]+'` 一次拿到全部 essay URL，**含 The Daily 总论帖**（成濑轮 8797 "The World Betrays Us" 即此命中，该帖汇聚侯孝贤/Pedro Costa/Lopate/Fujiwara/黑泽明多人评语引文——回顾展 announcement 帖是导演轮高密度二手源，信息密度常高于单片 essay）。
2. **availability API 429 限流时 CDX 精确 URL 查询仍可用**：`web.archive.org/cdx/search/cdx?url=<精确URL>&output=json&limit=5&collapse=urlkey` → 拿 timestamp → `https://web.archive.org/web/<ts>id_/<原URL>` 直抓。与「CDX 通配 403」互补：精确 URL 免通配符，429 后走 CDX 不纠缠 availability。
3. **SoC 站点搜索一次拿全家族**：`sensesofcinema.com/?s=<导演名>` 结果页除 GD 专条外，**同页含多篇 cteq 单片文 + DVD 套装文**（成濑轮：great-directors/naruse-2 + cteq repast/flowing/mother + 2007 DVD 文四篇一次定位）——别只抓专条，cteq 文常含同题材导演对比（《流》cteq 含 Costa 三导引言 + 与沟口《赤线地带》同年同题对比）。
4. **HK IFF 纪念特刊转载的导演×主演对谈 = 日导一手话通道**：成濑极少接受采访（英维：「He gave very few interviews」），《浮云》开拍前成濑×高峰秀子对谈（《日本体育日报》1954-12-24，经《HK IFF 成濑巳喜男110年纪念特刊》转载）即豆瓣长评 7694712——成濑自述《浮云》完整剧情链+「林芙美子女士的小说通篇渗透着女性的哀愁」等原话。日片导演轮选稿关键词表补 **对谈/纪念特刊/110年**。
5. **华语文学文本 = 日导定评通道**：朱天文《荒人手记》对成濑 vs 小津的文学化定评（「成濑却自身参予，偕运命一起流转，他一生爱好是天然」）以豆瓣长评 1001477 形式存在——华语作家写日导的段落可作中文评论界的权威二手。
6. **日片中译剧本全本可能以豆瓣长评转帖存在**：《浮云》电影剧本（水木详子编剧稿/傅昌文译，139KB）即长评 7491473；⚠️ 剧本主角译名可能与通行译名不同（「由纪子」= 雪子 Yukiko），引用时区分剧本层/成片层（片尾字幕「花的生命短暂而痛苦」在剧本 0 命中、仅成片层有）。

## 坑（本轮复发/新发现）

1. **㊶ ref 吞正文复发**：自建校验脚本用 `re.sub(r'<ref[^>]*>.*?</ref>', '', s, flags=re.S)` 处理英维 raw，遇自闭合 `<ref name="..."/>`（enwiki raw 大量此类）且文件无配对 `</ref>` 时，正则从首个 ref 一路吃到文件尾——S1/S19/S20 三条引文集体假 MISS（"a more spectacular mode of melodrama" 等明明在存档）。修复 = **先 `re.sub(r'<ref[^>]*/>','',s)` 删自闭合，再成对删，再兜底删残留开/闭标签**（四步顺序不能省）。坑库 ㊶ 有记录但校验纪律正文无警示——本轮写卡时仍踩，SKILL.md 已补一行（见正文）。
2. **同日抓多篇豆瓣长评时引文归属错挂**：小津名言「我拍不出来的电影有两部」实存于 2870422（爱比死更冷），初稿校验 expect 写成 S11（1699771）假 MISS——两篇长评同轮下载、read_file 批量返回时按输出顺序误判归属；校验 MISS 先按 ⑤/expect_keys 换文件核验（本站台轮 S12/S13 误挂同型第三次复发）。
3. **小津名言双版本**：「a real masterpiece」（日记，经 Criterion 转引，可核验）vs 流传版「我拍不出来的电影有两部」（豆瓣转述，逐字原始出处未核验）——并行记录不混用，写进诚实声明。
4. **Criterion The Daily 帖正文提取**：wayback id_ 快照（72KB HTML）用 `<article>` 容器剥标签（与 SoC 同法）即得干净正文；作者在 `<title>` 后的 byline 行（David Hudson）。

## 核心证据链（卡片引用密度最高的几条）

- 成濑名言「世界背叛我们」：Richie & Anderson《日本电影》1959 转引（SoC GD 脚注 3）+ Lopate 2007 引（Criterion 8797）双源
- 黑泽明评剪辑：SoC GD 脚注 9（Bock 1979 转引短版）vs Criterion 8797 完整版——两版本措辞不同，逐字取自哪版标哪版
- 四次登楼减法结构：Criterion 7394（Moeko Fujii 2021）逐次拆解 + 豆瓣 14064976 中文细读互证
- 小津三方对比句式：Fujiwara 2005「if Mizoguchi's long-take... if Ozu's reverse-shot patterns... Naruse's varied and distinctive rhythms」经 Criterion 8797 转引
- 无宣泄结尾三例：《饭》/《楼梯》/《流》+ 徒劳体力活动（气球/梦露舞/耕田）——SoC GD
- 自任剪辑证据：Masters of Cinema 三片无剪辑师署名（SoC DVD 文）

## 未取证到（诚实声明已登记）

百度百科（jina 403 限流）、Criterion《浮云》独立 essay（站内搜索无）、Ebert 影评、「成濑受沟口直接师承」直接证据（仅蒲田同期有据——任务预设「师承」降级为「同代谱系+女性电影谱系对比」）。
