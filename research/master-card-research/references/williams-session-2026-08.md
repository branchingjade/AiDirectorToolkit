# 配乐大师 John Williams 研习轮记录（2026-08-09）

配乐轴第一轮（此前轮次均为视觉工种：DP/调色/剪辑）。产出《约翰·威廉姆斯_制作大师卡片.md》，模板为《久石让_制作大师卡片.md》（同在 `妖玉影视\_知识库\references\制作学科\大师卡片\`）。

## 配乐大师来源地图（比视觉工种多两类：音乐分析文章 + 原声带专条）

| 来源类型 | 实例 | 价值 | 通道 |
|---|---|---|---|
| 深度杂志长访谈（一手） | New Yorker 2020-06 Alex Ross《The Force Is Still Strong with the "Star Wars" Composer John Williams》 | 本轮最高价值一手源：旋律 5-6 秒原则、调性 D 大调、简单旋律最难写、"needed to write"、60+ leitmotif（Frank Lehman 统计）、"probably a little overwritten" | r.jina.ai 直抓成功（24KB，paywall 可过） |
| 维基主条目 refs 段 | John Williams 主条目 | 转引 Ross/King 访谈原话（"seventeen-year-old kid"、Jaws 轶事、"they're all dead"）——维基正文自带一手引语引用，可当二手转述用 | r.jina.ai（174KB） |
| 原声带/影片维基专条 | Star Wars (soundtrack)、Schindler's List (soundtrack) | 编制（乐团/独奏者）、录音场次、曲目表（含时长）、获奖；**片内 diegetic 时代音乐清单**（辛德勒专条列了 Por Una Cabeza/Erika/Bach/Billie Holiday 等十几首）——历史题材"时代声音并置"论据来源 | r.jina.ai |
| 音乐分析文章 | ClassicFM《What makes the Star Wars soundtrack so good?》、medici.tv《Leitmotif Explained》 | 评论者分析：leitmotif 变奏五件套（fragment/tempo/orchestration/harmony）、节奏技法（三连音对比长音/切分） | r.jina.ai 直抓 |
| 乐迷站 | jwfan.com | 音频访谈**无文字转写**——只能标"未听录"，别当文字源引用 | r.jina.ai（10KB 仅简介） |
| Fandom/Wookieepedia | starwars.fandom.com Force Theme | 正文常不渲染（已有 Fandom 坑）——本轮直接跳过，用维基主条目主题清单覆盖 | 未取 |
| 中文维基 | 约翰·威廉斯条目 | 中文细节独有：Jaws"大提琴两音符"、AFI 百年配乐排名（SW 第1/Jaws 第6/ET 第14，唯一三部上榜作曲家） | r.jina.ai（135KB） |

检索式：`"<人名>" interview <年份> site:newyorker.com/classicfm.com`；配乐分析用 `site:classicfm.com <人名/片名> analysis`、`medici.tv leitmotif <人名>`。

## 本轮新坑（已并入 SKILL.md 或值得复用）

1. **markdown 强调符破坏 grep 验证**：r.jina.ai 存档是 markdown 化正文，引语内单词可能带斜体标记——"it's what you *needed* to write" 存档为 `it's what you _needed_ to write`，grep "needed to write" 假失败 0 命中。对策：grep 片段时去掉可能被强调的单词，或先 grep 无强调词的部分；「应命中却 0 结果」先怀疑格式标记（弯引号之外第二号嫌疑人）。
2. **引语归属必须逐文件核验**：诚实声明初稿把 "two-note double-bass ostinato" 误归英文维基（实际是 New Yorker 的表述，维基写 "two-note ostinato"，中文维基写"大提琴"）——写入来源清单前，每条引语的措辞差异逐文件 grep 核验；同物多口径（大提琴/低音提琴）在卡片里三说并存、各归其源，不强行统一（与杜可风轮"中英维基数字口径"同类处理）。
3. **配乐轮诚实声明必备项**：①音频访谈未听录要声明（乐迷站/播客常见）；②音乐学阐释（"小提琴代表犹太民族"类）未在来源中取证到就绝不写入，只写可取证事实（Perlman 独奏、拒接轶事）；③"某曲听起来如何"全部引自评论者文字并保留出处。

## 已验证引语锚（Williams 轮，可直接复用）

- "Eighty or ninety per cent of the attention is focussed elsewhere. The music has to cut through this noise of effects. So, O.K., it's going to be tonal. It's going to be D major. The tunes need to speak probably in a matter of seconds—five or six seconds."（旋律简洁论，S2）
- "these genuine, simple tunes are the hardest things to uncover, for any composer"（S2）
- "People assume it's what you wanted to write, but it's what you _needed_ to write."（S2）
- "I have been in the big river swimming with all of them."（淡化 Wagner，S1）
- "I really think you need a better composer than I am for this film" / "I know, but they're all dead."（辛德勒轶事，S1）
- "John Williams has been the single most significant contributor to my success as a filmmaker."（斯皮尔伯格 2012 致敬，S2）
- "Jones did not perish, but listened carefully to the Raiders score. Its sharp rhythms told him when to run..."（斯皮尔伯格论动机=行动指令，S1）

## 来源清单（pages/ 存档）

S1 英文维基主条目（174KB）、S2 New Yorker 2020 Ross 访谈（24KB）、S3 Star Wars (soundtrack) 维基（47KB）、S4 ClassicFM 星战分析（9KB）、S5 medici leitmotif（20KB）、S6 Schindler's List (soundtrack) 维基（17KB）、S7 中文维基（135KB）、S8 jwfan 音频访谈页（10KB，未听录）。未取：franklehman.com/starwars（主题目录）、Wookieepedia Force Theme（Fandom 反爬）。
