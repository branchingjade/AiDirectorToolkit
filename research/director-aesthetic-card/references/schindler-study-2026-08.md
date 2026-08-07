# 斯皮尔伯格《辛德勒的名单》单片轮来源地图（2026-08）

任务：导演本体零存量首轮，创作极=历史灾难/黑白克制/救赎叙事。产出研习报告+技法卡片（film-suite-research/研习报告/、技法卡片源稿/），30 存档 S1-S30、39 个 pages 文件，六项任务预设全部多源取证成立零证伪，79 引文 78 命中（3 条为校验脚本自身预期错误非文档错）。

## 存档对照（S1-S30 完整清单见研习报告附录）

主力证据档：
- S1 英维 Schindler's List raw 112KB（黑白/红衣/蜡烛导演原话、40% 手持、72 天、rotoscope、Talmud 戒指、Bartov/Wilder/Polanski）
- S2 中维「辛德勒的名单」raw 29.7KB（发展史/象征意义/获奖）
- S3 Ebert 1993 原评 7.4KB（jina 过 CF 壳）
- S4 Ebert Great Movies 2004 重评 9.2KB
- S5 NYRB John Gross 1994 21KB（jina 直抓）
- S6 EW 1994 幕后长文 21.7KB（直连 275KB HTML 提取）——导演原话金矿
- S9 英维斯皮尔伯格主条目 270KB（反犹童年/让导前后/朗兹曼凯尔泰斯批评）
- S11 豆瓣长评 6140406 = 雪舟译剧本全本 65KB（场 1-263）

## 本轮新坑（复用清单）

1. **Ebert 同片双版本并存**：rogerebert.com 对同一部片有 `reviews/<slug>`（原评，如 schindlers-list-1993）与 `reviews/great-movie-<slug>`（Great Movies 重评）两篇**内容完全不同的文章**，都要抓、不能只抓一个。原评含首映评论（"best he has ever made"/福楼拜 God-universe 引文/184 分钟），重评含多年后重看的结构概括（双人传/手推车寓言/黑白转彩色段落描写）。jina 均可过 CF 壳。
2. **ew.com 幕后长文直连可抓**：275KB HTML 直接 curl 成功（带桌面 UA + Accept: text/html），**先试 r.jina.ai 反而 exit 56**——EW 类好莱坞杂志幕后长文优先直连。正文提取：article 容器 → 剥标签 → 从首个角色名/片名关键词起取到 "Read More" 止。EW 1994《How Spielberg brought it to life》= 导演原话金矿（no crane shot / pink and white / Camille moment / 55 setups / 128 幸存者）。
3. **中维条目名新形态**：「辛德勒的名单」= 简体裸名无后缀无消歧义（探测三候选：裸名/裸名 (电影)/裸名 (電影) 只有裸名命中）。与「喋血双雄 (1989年电影)」「色，戒 (電影)」「非常母親」并列的第四种标题形态——先 API 探测再抓。
4. **好莱坞主流片「长评=中译剧本全本」通道再添一例**：review/6140406 雪舟译 65KB 全本（场 1-263，场 255 戒指致辞独白完整）——此前剧本转帖多为华语/艺术片（站台/甜蜜的生活/东京物语），好莱坞大片同通道成立，选稿时勿因"大片有官方剧本"假设跳过。
5. **百度百科电影词条剧情简介可能角色错乱**：本片词条把费因斯角色写成「艾蒂希」、魏斯勒写成演员——剧情证据用维基、百科仅取幕后花絮条目（质量分层：花絮/选角/制作数据可信度高于其剧情段）。
6. **Guardian Content API 带撇号标题搜索 0 命中**：`q=schindler's list` 返回 total 0（撇号/引号干扰），换不带撇号词或放弃该通道，别当 API 死。
7. **NYRB 老影评 = 高密度英文评论通道**：nybooks.com/articles/<日期>/<slug>/ 经 r.jina.ai 直抓 21KB 全文（约翰·格罗斯 1994，含"黑白决定最重要"断言/隔离区=超越敖德萨阶梯/墓碑"redeems everything"）。英维 ref 域名 grep 可发现（nybooks.com）。
8. **豆瓣 rexxar reviews 列表翻页空壳**：start=40/60 返回 53 字节（JSON 解析报 Expecting value），前 40 条对热门片已够用，出现 53 字节即停翻页，不是网络故障。
9. **Criterion 负面取证再证**：环球大厂片无 Criterion essay，站内搜索经 jina 只回 cookie 壳（2.5KB）——按大厂片预判直接跳过搜索或留档即可。

## 校验纪律实例

- 校验 79 条 78 命中；3 条提示均为校验脚本自身预期错误：① "the actual survivors and their children" 只在 S4 不在 S1（文档挂 S4 正确）；② "almost unwatchable" 双源 S1/S6 都有（文档挂 S6 正确）；③ "flew 128" 拼写应为 "fly 128"（文档无此短语）。——MISS 先查脚本预期再怀疑文档（与既有纪律一致）。
- 卡片附录来源清单与研习报告共用 S 编号；技法卡片正文引用 13 个编号 ⊆ 附录表 14 项，对账通过。

## 未取证（后续轮可闭环）

- New Yorker Terrence Rafferty 1993 影评原文（旧 URL 404，仅经英维转引两句）
- 卫报/其他英媒 1993 长评原文（Guardian API 撇号 0 命中 + 猜测 URL 404）
- 剧本英文原稿（本轮只有中译全本 S11）
- 卡明斯基摄影访谈原文（仅英维转引一句 timelessness）
