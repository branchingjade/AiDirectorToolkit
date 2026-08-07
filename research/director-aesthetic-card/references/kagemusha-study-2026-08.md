# 《影武者》单片研习轮来源地图（2026-08-07）

**轮次属性**：黑泽明补代表作单片轮（创作极=战国史诗/替身悲剧/色彩奇观）。黑泽明深化文档在库（黑泽明_手法体系深化.md），本轮与其做「影武者→乱」对照（任务预设片序纠正：影武者 1980 早于乱 1985）。

## 产出
- 研习报告：`film-suite-research/研习报告/影武者_研习报告.md`（~40KB，九节）
- 技法卡片：`film-suite-research/技法卡片源稿/影武者_技法卡片.md`（~21KB，8 节模板+附录）
- 校验脚本：`film-suite-research/verify_kagemusha_citations.py` —— **131 引文 0 MISS**

## 存档对照（film-suite-research/pages/）

| 编号 | 存档 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | kagemusha_enwiki_raw.txt（24584 B == 存量 kurosawa_wiki_Kagemusha.txt 同源复核） | enwiki Kagemusha raw | 制作段（Lucas 5000 群众→90 秒/胜新太郎换角/志村乔遗作+Criterion+18 分钟）/剧情全弧/奖项。**无 Themes 节：无 dream/Furinkazan 字样** |
| 研S2 | kagemusha_zhwiki_raw.txt | zhwiki 影武者 (電影)（繁体条目；裸名「影武者」=概念词条非电影） | 179 分钟/又名影子武士/票房 26.8 亿/剧情（含终幕旗沉湖）/演员表 |
| 研S3 | kagemusha_ebert1980.txt | Ebert 1980 原评（wayback 20130618110029，h1 起提取 13 段） | not Lord Shingen/illusion creates reality/终幕捞旗/融资史 |
| 研S4 | kurosawa_criterion_yojimbo_jina.txt（存量复用） | Criterion《Kagemusha: From Painting to Film Pageantry》（URL 误指 Yojimbo，内容已核对） | 画家出身/分镜画/调色板随心境变暗/Japanese Lear |
| 研S5-16 | kagemusha_review_<id>.json | 豆瓣 rexxar 长评 12 篇（5047179 499 有用…10446298 5 有用） | 见产出文档附录 |
| 研S6 | kagemusha_review_5790512.json → kagemusha_script_full.txt | **长评=剧本全本再添一例**：李正伦译《影子武士》164 场（岩波书店 1979 版），33KB | 场号级证据主矿 |
| 研S17 | kagemusha_reviews.json | rexxar 列表（total 290） | 选稿依据 |

## 关键通道与坑（本轮实测）
- **zhwiki 裸名「影武者」= 概念词条**（替身词条，非电影）；电影条目在繁体「影武者 (電影)」（1980年电影 形态 404）。zh API 429 限流→`w/index.php?title=&action=raw` 带 UA 可用。
- **豆瓣 subject id**：`movie.douban.com/j/subject_suggest` 返回 `[]` 空数组（费穆狼山轮同型）→ DDG 经 r.jina.ai 搜 `site:douban.com/subject 影子武士 1980` 解出 **1303067**。片名用「影子武士」（zhwiki {{douban|title=影子武士}} 佐证）。
- **enwiki Kagemusha 无 dream/Furinkazan/色彩节**（当前修订 24584 B）——梦与色彩证据全靠剧本+影评。
- **开场梦未见于剧本**：剧本场 1 直接从三人议事开始；成片开场梦为成片层添加（影评 5047179 描述：赤备/彩云/与家康追逐）。诚实声明已注明。
- **Ebert 快照无 meta description**：h1「Kagemusha」起提取 <p> 到正文末段；侧栏（Abrams Star Trek 等）在正文后部，需按内容截断（本片正文 13 段，之后全是侧栏）。
- **预设三项处置**：①「我不是武田信玄」未逐字取证到（剧本「我不是」三处皆非）→ Ebert「But he is not Lord Shingen」+剧本场 91 梦替代；②「织田蓝/德川绿」未取证到（剧本只写武田侧四色：风黑/林绿/火红/山金+红毛布旗；疑与《乱》阵营色彩混记）→ 诚实声明；③「梦的三段式」为解读层→ 取证三处梦节点（开场梦/场91-92噩梦/坠马=梦醒 10431132）。
- **预设片序纠正**：任务「色彩运用从乱到影武者」→ 实际影武者(1980)→乱(1985)，对照节按真实年份写（库布里克轮同例）。
- **剧本自注=方法论金矿**：场 123 夜战段剧本直接写「还必须让观众想象出眼睛看不见的部分」——以虚写实是黑泽明写在剧本里的战争方法论。
- **双重源交叉**：场 82 竹丸背旗铭（剧本）↔ 场 121「不动如山！」（剧本）；信廉台词长版（16239108）/短版（5815687）并存，逐字以字幕为准。
- 校验新坑：无（131 条 0 MISS；Criterion 存档下划线 `_Ran, Dreams,_` 需进 PUNCT 删除表——markdown 斜体残留在 norm 里会假 MISS）。

## 未取证清单
- 织田/德川联军服色（成片层色彩，需逐帧看片）
- 开场梦逐镜头结构（成片层，仅影评描述）
- 「本体都去了，影子如何存在」逐字台词（影评转述）
- 宫川一夫病倒/佐藤胜离开（仅豆瓣单源）
