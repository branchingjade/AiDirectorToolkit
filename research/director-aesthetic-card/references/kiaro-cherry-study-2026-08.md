# 《樱桃的滋味》单片研习轮来源地图（2026-08）

**定位**：阿巴斯导演本体零存量单片轮（创作极：生活流/存在追问/极简叙事）。产出：研习报告 + 技法卡片 + 本地图。编号 [研S1-16] 独立体系（无主卡片自建编号；若后续《阿巴斯_导演美学卡片》落盘按来源清单表行序映射对齐）。

## 存档清单（pages/，16 档）

| 存档 | 来源 | 关键内容 |
|---|---|---|
| kiaro_taste_enwiki_raw.txt / _clean.txt | 英维 Taste of Cherry（14KB） | Plot/Style/Reception；不同框构图+副驾驶座成因；DV 结尾；桑葚 mulberries；"He does not discuss why" |
| kiaro_taste_zhwiki_raw.txt | 中维 stub（1.9KB，真实条目名=繁体「櫻桃的滋味」，裸名简繁都 MISSING） | 片长95分/金棕榈/波士顿影评人奖；**外部連結段=Criterion Cheshire essay 精确 URL** |
| kiaro_enwiki_raw.txt / _clean.txt | 英维 Abbas Kiarostami（97KB） | "preciousness of life"三部曲自述；车内对话标志手法；Akrami 观众参与论 |
| kiaro_zhwiki_raw.txt / _clean.txt | 中维阿巴斯（30KB，真实名「阿巴斯·基阿魯斯達米」繁体，简体名重定向） | 生涯总括 |
| kiaro_taste_ebert.html/.txt | Ebert 1998 影评（wayback 20130602111405；slug=taste-of-cherry-1998 经 CDX 定位） | **负面评价代表**：an emperor without any clothes / affectation / tiresome distancing strategy / 双座位拍摄说 |
| kiaro_taste_criterion.html/.txt | Criterion Cheshire essay 2003 版（wayback 20070926223816） | "no things, only relations"；rhetorical inversion；"why he, or anyone, would want to live"；"to taste: life"；**page=2 无快照（CDX filter 空）→ 新版 essay 互补** |
| kiaro_taste_review_13981196.json → kiaro_taste_script.txt | 豆瓣长评=**单万里译全剧本**（法国《电影前台》1998.4，417 场 37KB，64 有用） | 场154二十锹土/224-229自杀定义/300-315桑葚/330樱桃台词/399-417结尾+黑屏；译者的话列阿巴斯美学清单（含"开放性的结尾"） |
| kiaro_taste_review_12780349.json | 豆瓣长评=**Hamrah Criterion 新版 essay 全译**（虹膜，11 有用） | 私人的灾难框架/罗森鲍姆引文/你无法体认我的感受/鸡蛋对身体不好 |
| kiaro_taste_review_1260273.json | 豆瓣长评 444 有用 | 不快乐也是不对的（成片台词转记） |
| kiaro_taste_review_1155897.json | 豆瓣长评 284 有用 | 三乘客递进/樱桃=生活滋味/手指头痛医案 |
| kiaro_taste_review_1242602.json | 豆瓣长评 163 有用 | 自杀史群像/二十铲报酬/痛楚不可通约 |
| kiaro_taste_review_8820767.json → .txt | 豆瓣长评=**彭明辉（清华教授）文 46 有用** | **阿巴斯访谈原话中译 [1]-[9] 编号引文**（天堂之门/极简主义/拼图/留下空格/一半就离开）；哲学性自杀框架；DV 结尾争议+意大利试播史；以阿拉之名开场 |
| kiaro_taste_review_1102286.json | 豆瓣长评 53 有用 | 汽车=最重要道具/唯一特权（成片台词）/樱桃落身（成片记忆） |
| kiaro_taste_review_3001355.json | 豆瓣长评 29 有用 | 戈达尔语转述/滤光镜土黄色 |
| kiaro_taste_review_1645497.json | 豆瓣长评 74 有用 | 民间故事重构四段式 |
| kiaro_taste_reviews_p1.json | 豆瓣 rexxar 列表 API（subject 1296177，total 405） | 选稿依据 |

## 本轮新坑/新通道（增量配方集中在本文件；SKILL.md 头部第三十六轮注解已登记指路）

1. **中维 stub 的隐藏价值**：1.9KB stub（只有 Infobox+奖项）的外部連結段直接给出 Criterion 旧 essay 精确 URL（release.asp?id=45&eid=63&section=essay）——wayback 2007 快照一次到手，免 CDX 猜 slug。徐克轮"英维 External links 段列 essay URL"的中维 stub 同效变体。
2. **Criterion 2007 快照结构**：正文无 `<p>` 全 `<br>` 分隔（`<p>` 提取 0 段是正常现象）——`essay-title` div 定位 + `<br>`→换行提取；ISO-8859-1 解码残留 U+FFFD 直接删除；**分页 essay 的 page=2 常无快照**→同片新版 essay（Hamrah）经豆瓣虹膜译稿互补。
3. **大学教授博客转帖=导演访谈原话通道**：彭明辉（清华教授）文带编号引文装置 [1]-[9] 逐条转引阿巴斯访谈中译——编号引文=学术式转录，可信度高于普通转帖，导演理念类引文首选；仍须标注"经X转引，原访谈出处未核验"。
4. **编号对账表头坑**：研习报告来源表标题=「来源渠道 + URL」、技法卡片=「取证来源清单」——对账脚本按后者切分会全量误报 not-in-appendix；先 grep 文档表头再选正则。

## 校验记录

- verify_kiaro_cherry.py：87 条引文短语（英+中）对 16 存档批量 grep，84 OK / 3 MISS 全为脚本多余测试项（非文档引文）——**文档引文 0 MISS**。
- 编号对账：used ⊆ listed，0 越界（修正对账正则后）。
- 场号修正两处：乘客序列（木板屋男人 21-24/捡破烂男人 30-37，初写 21-37 误）；自杀定义对话 224-229（初写 223-229 误）。

## 未取证项（诚实声明）

- 「电影一半是观众完成的」逐字句全存档未取证到 → 以彭明辉转引三引文（"留下空格"/"拼图"/"一半就离开"）替代。
- Criterion Cheshire essay 第二页、阿巴斯访谈英文原句、戈达尔语原文出处、Senses of Cinema 阿巴斯专条、IMDb 页。
- 成片层台词（不快乐也是不对的/唯一特权/樱桃落身）经长评转记，成片未直接核验；剧本层（树叶落脸）vs 成片层差异如实并列。
