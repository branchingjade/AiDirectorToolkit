# 特吕弗《四百击》单片轮来源地图（2026-08）

**第三十六轮；特吕弗导演本体并行轮同批（其存档中途落盘即复用）。本片零存量全新建档 22 项，56+ 引文 0 MISS。**

## 存档对照（研S1-19 + 卡T-*）

| 编号 | 存档 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | truffaut_400blows_enwiki_raw.txt | 英维片条目 raw 23.8KB | 五部曲/定格光学印片/片名 Wild Oats 史/拍摄地/戈达尔画外音客串/维果借用 |
| 研S2 | truffaut_400blows_zhwiki_raw.txt | 中维「四百擊」6.2KB（裸名条目，无后缀） | 谚语/巴赞去世日开拍/五部曲/结尾三长镜 |
| 研S3 | truffaut_baike_jina.txt | 百度百科经 r.jina.ai 61KB | 上映日期异说/「安托万五部曲」词条互证 |
| 研S4 | truffaut_criterion_528.txt | Criterion Insdorf《Close to Home》2014 | caméra-stylo/第一人称单数/自传对照表/定格-入案照镜像 |
| 研S5 | truffaut_criterion_3895.txt | Criterion《From the Truffaut Archives》2016 | 戈达尔「The face of the French cinema has changed」/试镜素材索引 |
| 研S6 | truffaut_ebert_live.txt | rogerebert.com live 直抓（1999 Great Movies） | 海陆之间/巴尔扎克神龛/狄更斯式警车 |
| 研S7 | truffaut_review_8496520_剧本全本.txt | 豆瓣长评=《四百下》剧本全本 42K 字（曹洸南虞译，31 有用） | 画外音贯穿/卡车+明信片结尾/「她是爱你的」被打断/四百下点题句 |
| 研S8 | truffaut_review_17157869_里维特评.txt | 豆瓣长评=里维特《在安托万家那边》全译（《电影手册》1959-05 p.37-39，13 有用） | 自传性不自大/公共的兄弟/忏悔印证虚构/绵延三镜头 |
| 研S9-18 | truffaut_review_*.txt | 豆瓣长评 10 篇（471/385/334/2179/2170/149/108/104/73/31 有用） | 拉片七处/结尾三长镜 1分27秒/谚语/空间语法/巴赞理论 |
| 研S19 | truffaut_criterion_films151.html | Criterion 片页（带 slug 的 films/151 正确） | essay 链接索引 528/3125/3895 |
| 卡T-soc | truffaut_soc.txt | SoC 特吕弗专条（并行轮存档复用） | 11月10日上午开拍当晚巴赞死/偷打字机办影迷俱乐部/「mixture of two real people」 |
| 卡T-enwiki | truffaut_enwiki_raw.txt | 英维导演条目（并行轮存档复用） | auteur theory 定义 |
| 失败 | truffaut_criterion_3125_*.html/txt | posts/3125 试镜文章 | CF 壳 + jina Cookie 声明壳，正文未取证到；存在性由 3895 索引+豆瓣长评双源佐证 |
| 负面 | truffaut_criterion_400blows.html | 并行轮产物 | films/151 猜错=Tokyo Story 完整页（title 必验再证；带 slug 的 URL 才返回本片） |

## 渠道实测

- **Criterion essay live 直连可抓**（posts/528 73KB、posts/3895 35KB）；3125 遇 CF 壳，jina 只回 Cookie 声明壳 → 标未取证到不硬凑。
- **Ebert Great Movies live 直连可抓**（`reviews/great-movie-the-400-blows-1959` 96KB，署名 Ebert 验证）。
- **enwiki raw grep `criterion.com/` 一次命中 essay+片页 URL**（posts/528 + films/151-the-400-blows），免猜 post id（阿飞轮「别猜」坑的正向实例）。
- **豆瓣 rexxar 12 篇一次连抓零失败**；列表页发现三个高价值标题形态：`电影剧本`（剧本全本 8496520 42K 字）、`翻译|...|XX评`（里维特评全译 17157869——**《电影手册》经典文章全译通道**，与虹膜译稿同族，低有用数 13 高价值）、`备忘录`（映后交流记录）。
- **并行轮共享 pages/**：开局零存量，抓取中途 truffaut_* 导演本体存档落盘（enwiki 导演条目/SoC 专条/Criterion 片页错抓），按 [卡T-*] 前缀登记复用；其中 truffaut_criterion_400blows.html 是并行轮猜 film id 错抓（内容=Tokyo Story），弃用留负面记录。

## 新坑（本轮实测）

1. **execute_code cwd=工作区根（C:/Users/HMSJ/Documents/Hermes）而非 film-suite-research**：相对路径 `pages/...` 写的 12 篇豆瓣存档全落到工作区根 pages/——技能旧坑的又一实例；**找回法**：`find . -name "truffaut_review*"` 定位后 `mv` 迁移，勿重抓。
2. **str.maketrans 两参数式不等长 ValueError**：繁简映射表手写 `str.maketrans("錢萬裏…","钱万里…")` 两串长度不一致直接抛 `ValueError: the first two maketrans arguments must have equal length`（与 ㊿② 字典式单字符键 ValueError 并列的第三形态）；繁简映射一律 `for k,v in dict.items(): s=s.replace(k,v)`。
3. **引文短语取链接目标（管道左）假 MISS**：`[[optical printer|optical effect]]` 剥壳后只剩显示文本 `optical effect`——短语写 `optical printer`（链接目标）必然 MISS；引文取词唯一合法来源=剥壳后显示文本（管道右），与杨德昌轮「拼合目标+显示文本」变体互补。
4. **é 重音归一再证**（écriture vs ecriture 假 MISS，㊹ 应用）。

## 预设处置

- 「你妈妈不爱你」0 命中：剧本层实为父亲台词「她倒是喜欢你的……知道吗，她是爱你的」被打蛋打断（成片逐字未单独核验）；按取证改写为「爱的话语无法完成」+ 安托万「我跟他们说真话，他们反正不相信，于是我决定：还是对他们撒谎的好」作反向证据。
- 「四百击」片名=多义并存：法文习语（to raise hell/胡闹）三源 + 中文流通「鞭打四百下」两源 + 美版首印 Wild Oats 史。
- 日期双口径并存：开拍日 SoC 11-10 晚巴赞死 vs 中维 11-11；上映 5-4 vs 6-3；摄影 Decaë vs Rabier。

## 剧本-成片差异（剧本全本核验，本轮重点）

- 剧本层贯穿第一人称画外音 → 成片删除（**推断**：全部拉片类来源未提及旁白 + 里维特「对话与场面调度导向直接的真实」；推断须标注）。
- 剧本结尾=卡车跳车+捡贝壳+明信片合影尾声（含片名点题句「经受着四百下冲击的道路」）→ 成片=奔跑+定格凝视；「删掉解释、信任影像」为作者电影风格证据。
- 角色名译名差异（剧本「里昂纳」vs 成片 Doinel/中维「安坦·德瓦聶」）。

## 校验记录

56+ 条引文 0 MISS；7 个首轮 MISS 中 5 假（映射缺 無顧贊當買 字/é 重音/wiki 斜体 ''/管道链接取词）2 真（措辞按存档原文修正：「该片宣告了」→「此片的誕生宣告了」；「看到大海却看不到自由」→「十三岁的安东尼能看到大海，却看不到自由」——原文用「安东尼」）。
