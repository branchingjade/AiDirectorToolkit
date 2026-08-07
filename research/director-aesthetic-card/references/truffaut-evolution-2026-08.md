# 特吕弗深化轮来源地图与校验管道五坑（2026-08）

**轮次**：手法体系深化专题·无主卡片变体（特吕弗无《导演美学卡片》主卡片→自建 S1-S27 + [卡X] 双轨编号，李安轮同型）。
**产出**：`film-suite-research/技法卡片源稿/特吕弗_手法体系深化.md`（三线矩阵：童年自传/爱情哲学/类型致敬；演变 A 作者电影自觉六阶段；演变 B 安托万贯穿四机制；8 件泛用工具箱；vs 戈达尔/侯麦三系对照）。
**结果**：92 引文 0 MISS（87 存档 + 5 卡片/回测转引），校验脚本 `_verify_truffaut_deep.py`。

## 存档对照（pages/truffaut_*，S1-S27）

| 编号 | 存档 | 来源 | 要点 |
|---|---|---|---|
| S1 | truffaut_enwiki_raw.txt | enwiki François Truffaut | alter ego/作者论定义/黑衣新娘 homage/戈达尔决裂 20 页信/「joy or agony」 |
| S2 | truffaut_zhwiki_raw.txt | zhwiki 法蘭索瓦·杜魯福 | 安托万五部曲定义（-{}- 模板内）/1957「第一人称」预告/語錄节「明天的电影将是爱」 |
| S3 | truffaut_soc.txt | SoC Great Directors（Juan Carlos González A. 2003） | 「Truffaut was cinema」；安托万混合体原话；六部致敬片清单；amour fou=疯狂+死亡惩罚；1967 苦涩原话；野孩子十年回应原话；侯麦俱乐部 |
| S4-S8 | truffaut_400blows/julesjim/dayfornight/pianist/brideworeblack_enwiki_raw.txt | enwiki 电影条目 | 定格光学推近/Vigo 整段借用；love triangle；metafictional；noir 致敬+艺术商业沉思；Herrmann 配乐+Ebert 联姻句 |
| S9-S10 | truffaut_antoinedoinel/antoinecolette_enwiki_raw.txt | enwiki 系列条目 | alter ego 定义（街头互认）/20 年跨度 |
| S11-S13 | truffaut_400blows/julesjim/dayfornight_zhwiki_raw.txt | zhwiki 电影条目 | 中维条目（正文未直接引用，附录已注明） |
| S14 | hitchtruffaut_wikipedia.txt（存量） | enwiki Hitchcock/Truffaut 书条目 | 「Rear Window is not about Greenwich Village」；成书动机 |
| S15 | truffaut_criterion_400blows.txt | Criterion 片页 | essay 作者=David Bordwell（正文 URL 未定位，仅摘要） |
| S16-S20 | truffaut_400blows_review_*.txt | 豆瓣长评 | 里维特评四百击全译（《电影手册》1959.5）/戴锦华作者论/新浪潮特征 334 有用/段落拉片/巴赞理论 |
| S21-S24 | truffaut_jj_review_*.txt | 豆瓣长评 | 1226 有用石像登场+唐吉诃德闭环/存在主义/《朱尔与吉姆》剧本转帖 40KB |
| S25 | truffaut_dfn_review_1137212.txt | 豆瓣长评 | 日以作夜；戈达尔不满转述；导演自嘲台词 |
| S26-S27 | truffaut_pi_review_*.txt | 豆瓣长评 | 特吕弗「无主题电影」采访原话转引；类型反讽观察 |
| S28 | truffaut_br_review_4886900.txt | 豆瓣长评 | 「只得其形未得其神」；特吕弗/戈达尔虚构观对照 |

**本地转引链**：[卡四百击·研S#]（四百击_技法卡片已落盘）；[卡朱尔与吉姆·研S3/研S9/研S18]（朱尔与吉姆_技法卡片**写作中途落盘**→定稿重扫升级互引，判词「Jules et Jim est un hymne à la vie et à la mort...」）；[卡希区柯克·S2/S9]（希区柯克深化文档）；[卡剧情作者]（《剧情作者电影密码.md》不存在→回测报告《渡口_剧情作者密码回测.md》中途落盘=密码结论转述载体，带密码章节号「一、作者电影的定义」等）。

## 校验管道五坑（本轮回填 SKILL.md 因超 100KB 上限转存此处）

1. **zhwiki `-{...}-` 转换模板不可整删**：显示文本在模板内（`組成-{zh-hant:安端·達諾; zh-cn:安托万·杜瓦内; ...}-五部曲` 整删丢「安端·達諾」）。剥壳正则匹配 `-\{([^{}]*?)\}-` 后取 `zh-cn:`/`zh-hans:` 段值，无则删空；引文侧按剥壳后显示文本直录（写繁体字形会被剥壳后简体文本假 MISS）。
2. **`{{模板}}` 剥壳必须保留管道最后段**：`{{link-fr|飛吻 (1968年电影)|Baisers Volés|飛吻}}` 整删吞显示文本 → `lambda m: m.group(1).split('|')[-1]`。
3. **enwiki raw `<blockquote>` HTML 标签**（Ebert 长引文整段在内）：ref 成对删 → Blockquote 模板保内文 → 其余模板管道末段 → wikilink 迭代 → `<[^>]+>` 剥 HTML → `''` 斜体删。顺序错了整段假 MISS。
4. **双语 norm 共享拉丁归一**：中文句内夹法文（「（la vérité）」、法文判词）时短语判 en 管道、整档判 zh 管道，两侧 é→e 不一致必假 MISS。抽公共 `latin_norm()`（é/è/ê/à/ç/œ→oe/U+2019 弯撇号）供 norm_zh 与 norm_en 共用。
5. **繁简转换默认 zhconv**（`from zhconv import convert`，`convert(s,'zh-cn')` 放 norm_zh 首位）：手写映射表逐轮缺字（談論/正統/標誌/達諾/歲戀 反复踩），zhconv 一次到位。

## 新通道

- **j/search_suggest**（`https://www.douban.com/j/search_suggest?q=<词>` + `-H "Referer: https://www.douban.com/"`）= rexxar 搜索全灭 + j/subject_suggest 空数组时的免登录 subject id 第二兜底（朱尔与吉姆=1292338/射杀钢琴师=1298095/黑衣新娘=1303544 三连中）。已并入 references/douban-rexxar-api.md。
- 定稿前重扫范围再扩展：**回测报告/ 目录**（技能 ㊴ 已覆盖技法卡片源稿/+研习报告/；本轮密码回测中途落盘于回测报告/，重扫补上才闭环任务指定资产缺口）。

## 预设核对结果（可复用结论）

- 三线矩阵预设全成立；类型致敬线证据最硬（SoC 六片清单+enwiki 逐片 homage）。
- 「从新浪潮宣言到商业类型回归」修正：绿屋=对作者论本身的致敬（Ebert/Rosenbaum），类型回归是作者论的辩证完成非妥协。
- 日以作夜=爱情哲学线转向点（爱女人→爱电影），非终点；终点为隔墙花。
