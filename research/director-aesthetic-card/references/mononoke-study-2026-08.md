# 《幽灵公主》(Princess Mononoke, 1997) 单片研习轮来源地图（第二十九轮，宫崎骏补代表作）

2026-08-07 实测。产出：研习报告 + 8 张技法卡片（`研习报告/幽灵公主_研习报告.md`、`技法卡片源稿/幽灵公主_技法卡片.md`）；零存量全新建档 21 个 `pages/mononoke_*` 存档；107 引文 0 MISS（校验脚本 `pages/_verify_mononoke.py`）。

## 渠道实测（结论先行）

| 渠道 | 结果 | 判据/备注 |
|---|---|---|
| enwiki raw `Princess Mononoke` action=raw | 124KB 一次成功 | 制作硬数据（144,000 赛璐璐/80,000 原画/5 美术监督按昼夜分工/最终镜头 1997-06 完成）全在 Production 段 |
| zhwiki 探测 | 「幽灵公主」=`#重定向 [[魔法公主]]`（繁体/台译名） | 简体候选=重定向存根，读重定向目标再抓（简体条目存在但指向繁体主条目的又一实例） |
| 豆瓣 rexxar | subject 1297359（suggest 裸片名一次命中）；reviews total 1690 | 13 篇长评全文落盘；**2885488（1430 有用）[转]访谈帖 = Nausicaa.net 英译访谈的中文转帖**，Q&A 结构逐段对应可双语互证 |
| **Nausicaa.net** | `miyazaki/interviews/m_on_mh.html` 18KB 英译全文 + `miyazaki/mh/MakingOfMH/Part1.html` 77KB / `Part2.html` 91KB | **吉卜力/宫崎骏一手通道**；slug 猜不出来（试了 on_mononoke/mononoke/m_on_mononoke 全 404），DDG 经 jina `site:nausicaa.net miyazaki mononoke interview` 的 `uddg=` 一次定位；http 需 `-L` 跟 301；Part3 不存在（404） |
| Ebert | CDX 前缀通配 `url=rogerebert.com/reviews/princess-mononoke*` 定位真实 slug `princess-mononoke-1999`（非 Great Movies 命名规律）→ 2013 快照 `id_` 直抓 | 现站该 slug live 404（Page Not Found）；wayback available API 429 时 CDX 可用；正文提取用 h1 后段落+「Cast and crew」截尾（侧栏其他影评 `<p>` 污染，先按 Mononoke/Ashitaka 关键词定位正文起点） |
| Guardian | Content API `q="princess mononoke"`（带引号）无专文 essay；裸 `q=princess mononoke` 被 "princess" 泛词污染 | 2020《Every Studio Ghibli film – ranked!》含 Mononoke 专段（Miriam Balanescu）可作第三方文献；正文提取须跳过页面 JSON-LD 块 |
| 百度百科 | `item/幽灵公主` 经 r.jina.ai 48KB | 电影主词条正确（非歧义碰撞） |
| Criterion | 未发行本片（北美版权在米拉麦克斯/迪士尼线）→ 无 essay | 负面取证：大厂片库片预判（迷魂记轮同型），以 Nausicaa.net 一手资料替代 |

## Nausicaa.net 吉卜力通道配方（本轮最大发现）

- 访谈英译：`https://www.nausicaa.net/miyazaki/interviews/m_on_mh.html`（"Miyazaki on Mononoke-hime"，Theater Program 1997，Ryoko Toyama 译）——副标题 "It's not bad people who are destroying forests." 即主题句；「没有坏人」「nature's night, given form」「low-ranked god」英文原句全在此。
- 制作日记：`miyazaki/mh/MakingOfMH/Part1.html`（"How Mononoke Hime Was Born"）+ `Part2.html`——特殊分镜纸（每页 3 放大格）、42 张赛璐璐=3.5 秒上色、背景布料纹样一致性、E-konte 开画四分之一等密度美学/工作法硬证据；Part3 404。
- 书目页 `miyazaki/books/mh/` 列出相关书籍（《もののけ姫 ロマンアルバム》223 页制作日记等），可作延伸线索。
- 发现路径：enwiki raw refs grep `nausicaa\.net` 拿域名 → DDG 经 r.jina.ai `site:nausicaa.net <导演> <片名> interview` 搜 slug（别猜路径）；抓回后 `<title>` 验证。
- 中维条目「作品設定/作畫美術/主題」节=无剧本动画片一手转述金矿（企划书 quote box 原文、邪魔神灵感自述「毛细孔仿佛会爆发长出邪恶的东西」、押井守/梅原猛评论、铃木敏夫宣传战）——千与千寻轮同款，宫崎骏轮复用。

## 校验新坑（㊿-幽灵公主轮，2026-08；与巴里·林登/盗梦/雪国列车/奉俊昊/迷魂记/恐怖分子/麻将/希区柯克轮 ㊿ 同名并存、以轮次标注区分）

① **quote box 内嵌 nihongo 模板整体吞文**：`{{quote box|...|quote={{nihongo|中文|日文}}|source=...<ref>{{cite book|...}}</ref>}}`——nihongo 正则写成 `\{\{nihongo\|([^|}]*)(\|[^}]*)?\}\}` 时，日文段以 `}}` 结尾、可选组 `[^}]*` 贪婪吃掉一个 `}`，导致 `\}\}` 不匹配 → nihongo 原样留下 → 随后模板剥壳把整块（含中文 quote）删除 → 引文假 MISS。解法（手术式，先于模板剥壳）：`re.sub(r'quote=\{\{nihongo\|([^|]*)\|[^}]*\}\}', r'quote=\1', s, re.I)` 再 `re.sub(r'\{\{quote box\|', ' ', s, re.I)`——拆开模板本体后 quote 内文保留为普通文本。
② **[[File:...]] 管道段吞字幕（㊱-吴宇森轮 File 嵌套坑的管道段变体）**：`[[File:X.png|thumb|CAPTION|upright=1.1|alt=...]]` 内层链接剥完后，通用 `[[...]]` 剥壳按 `split('|')[-1]` 取**最后**管道段（alt 文本），字幕 CAPTION 丢失（"3D rendering was used to create writhing demon flesh..." 引文假 MISS 即此因）。解法：wikilink 迭代循环内先处理 File 模板——`re.sub(r'\[\[File:[^\[\]]*\]\]', lambda m: m.group(0).split('thumb|')[1].split('|')[0] if 'thumb|' in m.group(0) else ' ', s, re.I)`（取 thumb| 后的字幕段），再做通用剥壳。
③ **模板剥壳必须迭代**：外层模板（quote box 等）含内层花括号时，单次 `re.sub(r'\{\{[^{}]*\}\}','')` 剥不掉（引擎已越过起点）→ 残留 `{{quote box|...` 前缀破坏子串匹配。解法：`for _ in range(10): s2 = re.sub(...); if s2 == s: break`。
④ **繁简映射缺字新实例**：時→时、開→开、佈→布、驗→验（「平時」「開始」「佈满」「体驗」假 MISS）——⑧ 类缺字持续发生，映射表按轮补字，校验短语侧与存档侧同管道。
⑤ **验证短语必须与成稿引文逐字一致**：成稿已把「毛孔」修正为「毛细孔」（存档原文）而测试短语仍写「毛孔」→ 假 MISS——先查测试短语是否同步了成稿的修正，再怀疑来源；括号插入语（"Oh this person (characters) should not say such things"）在 norm 删括号后，测试短语要含括号内词（characters）。

## 存档清单（pages/mononoke_*）

| 编号 | 文件 | 内容 |
|---|---|---|
| 研S1 | en_raw.txt | 英维 raw（制作硬数据/剧情/主题/Napier/Ebert 转引/吉尔伽美什灵感） |
| 研S2 | zh_raw.txt | 中维「魔法公主」raw（企划书 quote box/美术作画/角色身世/反应/铃木敏夫） |
| 研S3 | nausicaa_interview.txt | Nausicaa.net 访谈英译全文（无反派英文原句/山兽神设计/火枪史观） |
| 研S4/研S5 | making_Part1.txt / making_Part2.txt | 制作日记英译两卷 |
| 研S6 | ebert.txt | Ebert 1999 四星影评（2013 wayback 快照提取，5.8KB） |
| 研S7 | rev_2885488.txt | 豆瓣访谈中文转帖（=研S3 同文） |
| 研S8-17 | rev_12721386/6408883/16713481/16693615/16700920/9289770/1185417/1086295/2974428/1274693.txt | 豆瓣长评（票房/致敬链、麒麟兽阴阳、原题、结局对白、台词摘抄、思想透视等） |
| 研S18 | baike.txt | 百度百科（r.jina.ai 48KB） |
| 研S19 | guardian.txt | 卫报 2020 排位文 Mononoke 专段 |
| 研S20 | rev_9703353.txt | 豆瓣长评（Chris 观影记忆「嘴角满是猩红的鲜血」引文出处） |

## 跨片对照与互引

- 与《千与千寻》签名对照（不战斗的主角→战斗的主角 / 无反派双机制 / 名字契约 vs 诅咒头颅符号 / 服务业异界 vs 战争世界）见研习报告第五节；千与千寻资产（spirited-* 存档、千报告/千卡片）为本轮对照基准。
- 并行轮《宫崎骏_手法体系深化.md》定稿前落盘 → 互引链：其 [S3]=mzk_wiki_zh_mononoke.txt 与本轮 [研S2] 同源独立抓取中维条目，诚实声明注明。
- 名台词「我想以没有仇恨的眼睛看世界」仅影迷记录层级（英维 grep unclouded 零命中），未升格为剧本/官方台词证据。
