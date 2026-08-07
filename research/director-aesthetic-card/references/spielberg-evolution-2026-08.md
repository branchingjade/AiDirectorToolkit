# 斯皮尔伯格手法体系深化轮来源地图（2026-08）

深化专题（类型悬念/历史严肃/家庭奇幻三线、藏-露悬念头号链）：**零存量全新建档 11 项 spiel_*（S1-S11，无主卡片自建编号第五种变体再证）** + 并行轮 22 档 jaws_* 复用；50 引文 0 MISS；校验脚本 `scripts/_verify_spielberg_deep.py`（引文清单 + S# 一致性 + 卡X 标注三合一）。

## 存档对照（关键证据位置）

| 编号 | 文件 | 内容 | 关键证据 |
|---|---|---|---|
| S1 | spiel_enwiki_raw.txt | 英维导演主条目 270KB | Method and themes 段：ordinary people/childlike wonder/flawed father figure/想象朋友自述（L157-165） |
| S2 | spiel_Jaws__film_.txt | 英维大白鲨 | L101 导演原话「the less-you-see-the-more-you-get thriller」+「more like Alfred Hitchcock than like Ray Harryhausen」+黄桶/背鳍/被迫克制；L90 美术禁红=血唯一红；L177 Frank Rich「we don't even see the shark」 |
| S3 | spiel_Raiders_of_the_Lost_Ark.txt | 英维夺宝奇兵 | L23 角色闭眼不看约柜（奇观用后果呈现）；L25 政府封存约柜=麦高芬终极藏匿 |
| S4 | spiel_JurassicPark.txt | 英维侏罗纪公园 | L64 **Koepp 承继 Jaws 技法明文链条**（T. rex offscreen）；L131 水杯波纹（奇观前凝视铺垫）；L169 127分钟仅15分钟恐龙（9模型+6CGI）；L129 地面机位=角色视点；L167 夜雨单光源=藏匿与渲染预算合谋 |
| S5 | spiel_E_T__the_Extra_Terrestrial.txt | 英维E.T. | L61 前半段大人只拍腰以下（Tex Avery）；L11 藏匿结构；L166 拒绝续集「rob the original of its virginity」 |
| S6 | spiel_SchindlersList.txt | 英维辛德勒 | L58 40%手持+「everything that for me might be considered a safety net」；L60 红衣实拍彩色后手工 rotoscope；L73 红衣意图（rail lines）；L81 黑白=「life without light」 |
| S7 | spiel_SavingPrivateRyan.txt | 英维瑞恩 | L82 **黑白方案因 pretentious 被否**（辛德勒→瑞恩显式关联）；L100 贴地手持+镜头溅血；L108 无分镜；L117 ENR 70% 去饱和 |
| S8 | spiel_Munich2005.txt | 英维慕尼黑 | L86 「prayer for peace」导演定性；L13 刺客道德争论；L99 道德扭曲主体论 |
| S9 | spiel_AIArtificialIntelligence.txt | 英维A.I. | L57 **库布里克版本结尾与斯皮尔伯格版一致**；L64 Watson「faithfully filmed without added schmaltz」；L69 模仿库布里克保密制片；L75 A.O. Scott 库布里克致敬 |
| S10 | spiel_zhwiki_raw.txt | 中维主条目 | L16/L29 早期奇观线 vs 后期严肃线**显式归类**（线定义直接证据） |
| S11 | spiel_soc.html | SoC 2003《The Question Spielberg: A Symposium Part Two》 | Keser 长镜头专文：Jaws 厨房 32s 深焦/JP 实验室 44s 后拉/Lost World 52s 开场 |

## 校验新坑四例（㊿-斯皮尔伯格轮）

1. **enwiki raw 剥壳后残留斜体标记 `''`（`''Jaws''`→`''jaws''`）致 12 假 MISS**：剥壳脚本只处理了 `<ref>`/`{{模板}}`/`[[链接]]`，`''斜体''`/`'''粗体'''` 全残留，任何含专名的短语（Jaws/T. rex/Godzilla）全部匹配失败。修复=剥壳脚本在 `[[ ]]` 剥离后补 `re.sub(r"'''(.*?)'''", r'\1', s)` + `re.sub(r"''(.*?)''", r'\1', s)`（flags=re.S）。**所有 enwiki raw 剥壳器都应包含此步**，与 killbill 轮自闭合 ref 坑并列的通用剥壳清单项。
2. **zhwiki NoteTA 转换标记 `-{焦}-` 残留致逐字引文假 MISS**：中维 raw 的 `-{...}-` 标记剥壳不去除（`其有時聚-{焦}-於兒童`），逐字引文「其有時聚焦於兒童」假 MISS。修复=引文绕开标记节引（省略号）+ 正文注明「存档 NoteTA 转换标记，节引」+ 校验按标记两侧子串分段。发现路径=校验 MISS 后 sed 查存档原文行。
3. **文档引文引号字形与存档不符（ASCII `'` vs 存档弯 `"`）致 4 假 MISS**：写文档时把存档的弯双引号（引用导演原话）误写为 ASCII 单引号；**patch 文档后校验仍 MISS——校验脚本 CHECKS 里的期望短语也要同步改**（两处都要改，脚本短语不会自动跟随文档）。norm 函数只归一弯→直，不归一单↔双。
4. **校验脚本文件加载必须优先 `_clean` 版本**：脚本按文件名子串匹配存档，第一个命中可能是 raw（含 `''`/`[[ ]]`）→ 大面积假 MISS。修复=候选列表排序 `_clean` 优先（`cands.sort(key=lambda f: (0 if '_clean' in f else 1, f))`）。

## 标题探测记录（重定向链三形态）

- `Jurassic Park (film)` → 112 字节 `#REDIRECT [[Jurassic Park]]`（film 后缀反成多余消歧，读裸名）
- `Munich (film)` → 89 字节重定向到**消歧义页** `Munich (disambiguation)#Entertainment` → 再探测 `Munich (2005 film)` 命中
- 中维「史蒂文·斯皮尔伯格」→ 40 字节 `#REDIRECT [[斯蒂芬·斯皮尔伯格]]`（简体名重定向到繁体主条目）

## 预设处置

- 任务预设引文「你越不让他看到，他越怕」**全部存档 0 命中** → 提炼句处理，锚定 S2 导演原话「the less-you-see-the-more-you-get thriller」，诚实声明注明。
- 三线片序（1975→1981→1993 / 1993→1998→2005 / 1982→2001）与真实年份**全部一致零纠正**（库布里克轮 2001 片序错误的反向案例——预设可对可错，逐节点核对纪律不变）。
- 慕尼黑「道德模糊」预设 → 细化为导演自述 prayer for peace + 批评界道德对等论双证，正文不用未取证表述。
- 任务指定《历史史诗题材密码.md》缺失 → `回测报告/盐道_历史史诗密码回测.md` 转述通道**再证**（李安轮纪律，命中3 画外呈现/后果镜头与慕尼黑画外炸弹互证）。

## 并行轮互引

- 《大白鲨_技法卡片.md》**定稿前落盘** → 按 ㊴ 升级：转引链改「经《大白鲨_技法卡片》转引，其〔研S#〕」格式；补桥段级量化锚（Ebert 接片条件「第一个小时不让鲨鱼出现」〔研S4〕、暴露阶梯「水下POV→背鳍→浮桶→局部→全貌」〔研S2〕）入演变链 1 与工具 1；诚实声明第 4 条同步更新。
- jaws_enwiki_raw.txt 与 S2 同源同文 → 同文容差不重复引用（芬奇轮同型）。
- 豆瓣长评复用 2 篇：jaws_review_1431921（希区柯克景深对照，21 有用）、jaws_review_9451871（10 编剧技巧，183 有用）——希区柯克借鉴类中文第三方观察可用于 vs 节。

## 工具箱设计要点（本轮 7 件）

威胁延迟出场（藏露悬念）/奇观前凝视铺垫（微物预警）/单一色彩高亮（红色唯一化）/孩童视点纪律（世界缩小法）/弃用安全网（记录片质感）/奇观的后果呈现（闭眼法则）/长镜头深焦叙事——每件=适用场景+取证要点+AI 提示词（标注「按取证要点编写，非原片描述」），提示词里的数字（40 分钟/12%/60%）是**按取证规律设计的建议值，非原片数据**，正文已注明。
