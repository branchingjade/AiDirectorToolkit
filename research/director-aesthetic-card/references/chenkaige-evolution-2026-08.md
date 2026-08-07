# 陈凯歌深化轮来源地图（2026-08-07）

手法体系深化·**无主卡片变体第五例**（李安轮同型）：陈凯歌无《导演美学卡片》主卡片 → 自建 S1-S11（网络存档）+ [卡X]（本地资产）双轨编号，文档头部声明「若后续主卡片落盘按来源清单表行序映射对齐」。

## 存档对照（pages/）

| 编号 | 文件 | 内容 |
|---|---|---|
| S1 | chen_enwiki_raw.txt | 陈凯歌导演条目 enwiki raw（**双线锚点**：首段 "Chen is known for his visual flair and epic storytelling"；"radical stylistic turn"=无极第三方观察非导演自述；荆轲刺秦王 "an epic involving the legendary King of Qin"） |
| S2 | chen_zhwiki_raw.txt | 陈凯歌导演条目 zhwiki raw（创作弧线句 L68："1984年凭其处女作《黄土地》蜚声国际……1993年凭《霸王別姬》在国内外票房口碑双收"——**显示文本繁简独立坑**：霸王別姬=繁「別」嵌简句） |
| S3 | chen_yellowearth_enwiki_raw.txt | 黄土地 enwiki raw（存量）：dumb photo 静态美学（张艺谋自述经转引）、有限图像库/山水画传统、土黄黑红白四色票、symbolic silence、求雨、翠巧结局切空景 |
| S4 | chen_yellowearth_zhwiki_raw.txt | 黄土地 zhwiki raw（存量，简体） |
| S5 | chen_farewell_enwiki_raw.txt | 霸王别姬 enwiki raw：epic historical drama 定位、五段历史时期结构、double visual experience、Ebert/Canby/Hinson 引文（经条目转引） |
| S6 | chen_farewell_zhwiki_raw.txt | 霸王别姬 zhwiki raw（繁体）："投影出歷史與文化在大時代的演變下" |
| S7 | chen_farewell_criterion_essay.txt | **Criterion essay posts/8546 经 r.jina.ai 直抓**（Pauline Chen《All the World's a Stage》2024）=戏台容器一手金矿：追光变审讯光柱/固定机位静态二维/restlessly moving crowds/新旧社会回响/panoramic historical sweep |
| S8 | chen_promise_enwiki_raw.txt | 无极 enwiki raw："2005 Chinese epic fantasy film"、RT consensus 负面 |
| S9 | chen_promise_zhwiki_raw.txt | 无极 zhwiki raw（**同文件双向繁简混排**：L26 繁句嵌简、"影片设定在一个东方架空历史的世界"；L28 整行简体"第一部奇幻类题材的商业大片"；L79 {{cquote}} 内文"把历史场景虚化，在虚幻的历史舞台上表现生与死，爱与恨"） |
| S10 | chen_monstercat_enwiki_raw.txt | 妖猫传 enwiki raw："a surreal reimagining"、幻术重建盛宴、"A set costing US$200 million and five years"、"its emotional truth remains" |
| S11 | chen_monstercat_zhwiki_raw.txt | 妖猫传 zhwiki raw（简体）："瑰丽奇幻的视觉呈现和虚实交织的叙事"、"幻术之中亦有真相"、"基本还原了唐代古城风貌"；置景三口径（数月建造 vs 耗時6年複製長安城=ref 标题） |

## 线定义直接证据新位置：enwiki 导演条目首段

深化轮线定义优先扫 **enwiki 导演条目首段**——"known for X and Y" 句式一次锚定双线/多线身份（陈凯歌轮："visual flair and epic storytelling" = 视觉象征线+时代史诗线的第三方直接定义，非自行归纳）。与宫崎骏轮「zhwiki 主条目总括句」、奉俊昊轮「首段片目类型标签」互补：en 首段管身份双线，zh 中段管创作观总括。

## 本轮新坑四例（校验实现级）

1. **{{cquote}} 模板内文被通用 {{}} 剥壳吞掉必 MISS（㉛ 的 cquote 变体）**：中维 raw 的 {{cquote|...}}（华东师大教授评《无极》「艺术风格」节整段引文）被 `\{\{[^{}]*\}\}` 连同内容一起剥掉 → 2 条引文假 MISS。解法：norm 先 `re.sub(r'\{\{(?:cquote|blockquote|quote)\|([^{}]*)\}\}', r'\1', s)`（迭代至稳定）再剥其余模板——zhwiki 引文模板是 cquote，不是 enwiki 的 blockquote。
2. **{{Cite}} ref 标题里的引文 norm 必 MISS → RAW_CHECKS 特例直验**：「耗時6年複製長安城」整句在 {{Cite web|title=《妖貓傳》耗時6年複製長安城...}} 的 title 参数里，任何模板剥壳都会删掉 → 校验脚本加 RAW_CHECKS 列表（短语直接 `in` raw 文本），不经过 norm。
3. **S# 双向对账脚本 str/int 集合假报越界（㉟③ 同族第三实例）**：`re.findall(r'\[S(\d+)\]', doc)` 提取的是字符串集合 {'1','3',...}，与 FILES 键集合 {'S1','S3',...} 直接相减 → 全部假报「越界」+「孤儿」。解法：`used_nums = {int(x) for x in ...}`，`all_nums = {int(k[1:]) for k in FILES}`，先 int() 再比较。
4. **wikilink 显示文本繁简独立于条目整体方向**：zhwiki 简句里 `[[霸王別姬 (電影)|霸王別姬]]` 显示文本是繁「別」——校验短语必须按**剥壳后显示文本字形**直录（「1993年凭《霸王別姬》在国内外票房口碑双收」），按句子其他部分的简/繁方向猜必 MISS（⑧/㊸ 的显示文本级扩展：不只文件级/句内级，wikilink 内部也自成字形）。

## 预设验证与修正

- 「容器演变 土地→戏台→幻境」逐节点成立，且**无极补齐中间环节**（"把历史场景虚化，在虚幻的历史舞台上"）——任务预设两跳变三段。
- 「视觉从极简到华丽」细化为同原则两极（大色块+仪式化不变，色票从贫瘠自然色到人工华丽色）——非断裂。
- 时代史诗线任务预设四片主链采纳；《荆轲刺秦王》(1999) 英维同为 epic，列旁证节点。
- 双线交汇点提炼句：「拍历史必先造一个视觉容器」（容器论为提炼句，导演自述未取证到）。

## 未取证清单

- 「容器」概念=提炼句，陈凯歌本人表述未取证到；霸王别姬/无极/妖猫传镜头级量化数据（均镜/镜头数）未取证；妖猫传「以倭代唐」仅中维单源；无极 "radical stylistic turn"=第三方观察非导演自述；荆轲刺秦王/梅兰芳等未纳入矩阵。
- 任务指定《历史史诗题材密码.md》本机不存在 → 经《盐道_历史史诗密码回测.md》转述通道（李安轮同型），密码原文未直接核验。
- 并行《霸王别姬/黄土地技法卡片》写作时未落盘 → [卡X] 占位登记，落盘后补互引链。

## 校验脚本要点（verify_chen_deep.py）

- 56 条引文 0 MISS（55 条 norm 校验 + 1 条 RAW 特例），S# 双向对账 0 越界 0 孤儿。
- norm 管道：keep_quotes（cquote/blockquote/quote 保内文）→ strip_refs（先自闭合再成对再孤儿）→ HTML 标签/unescape → jina markdown 链接 → 迭代剥 [[ ]]（封顶 50）→ 迭代剥 {{ }} → 剥 _* 斜体标记 → 弯引号归一后删英文双引号（**保留撇号**：Cuiqiao's 等属格不能删）→ 压空白 lower；zh 管道另删「」『』《》…——·
- 中文短语无条件删引号（恐怖分子轮 ㊿①），繁简按存档字形直录不映射。
