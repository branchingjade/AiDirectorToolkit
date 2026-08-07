# 特吕弗《朱尔与吉姆》单片研习轮来源地图（2026-08）

**轮次定位**：特吕弗导演本体零存量首轮；创作极=三角恋/自由与束缚/爱情哲学。产出《朱尔与吉姆_研习报告》+《朱尔与吉姆_技法卡片》（独立 [研S1-28] 编号体系，无主卡片，若后续主卡片落盘按来源清单表行序映射对齐）。**174 条引文 0 MISS**（校验脚本 技法卡片源稿/_verify_jj.py，双层校验：手工短语清单全量匹配 + 文档自动提取反查）。

## 存档对照（28 档 + 失败留档）

| 编号 | 文件 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | trf_jj_enwiki_raw.txt | 英维《Jules and Jim》raw | 剧情/奖项/Vincendeau/Crowther 转引/GoodFellas 影响 |
| 研S2 | trf_jj_zhwiki_raw.txt | 中维《朱尔与吉姆》raw | 制作幕后（15 人/7→3 次/全员到场）=《弗朗索瓦·特吕弗》江苏文艺 2011 书转述；审查史 1961-11-24 禁 18 岁以下 |
| 研S3 | trf_jj_frwiki_raw.txt | 法维《Jules et Jim (film)》raw | **特吕弗开拍前一年自述判词**（hymne à la vie et à la mort）；改编方法明说（旁白直读小说原文=回应《法国电影的某种倾向》）；Martin Lefèbvre 13 幅毕加索画=时间标记分析；Lubitsch《Sérénade à trois》对照 |
| 研S4 | trf_enwiki_raw.txt | 英维《François Truffaut》raw | Kael 全文引/Thomson/《两个英国女孩》互文（注意原文用法语片名 "Jules et Jim"） |
| 研S5 | trf_zhwiki_raw.txt | 中维《法蘭索瓦·杜魯福》raw | 生平/巴赞长镜头/「明天的电影」宣言 |
| 研S6 | trf_jj_criterion.txt | Criterion essay（John Powers，2005 DVD/2014 修订） | 特吕弗原话（"The book overwhelmed me…"）/凯瑟琳分析/360° 摇拍/审查事件/Sarris 引语 |
| 研S7 | trf_jj_guardian2022_clean.txt | 卫报 Bradshaw 2022 五星重评 | 旋风意象/manic pixie dream girl/错过之约/Le Tourbillon 歌词引 |
| 研S8 | trf_jj_guardian2000_body.txt | 卫报 Derek Malcolm「世纪之片」2000 | 老男人心智写青年电影/「They left nothing behind them」 |
| 研S9 | trf_jj_ebert_wayback.txt | Ebert Great Movies（wayback 20120920023530） | 旋转木马开场/25 年飞掠/定格快照/「Watch us, Jim!」/赫塞尔自白 |
| 研S10 | trf_jj_nyt1962.txt | NYT Crowther 1962 首评（wayback 20201116024334id_） | 「配乐承载情感」/「arch and arty study」 |
| 研S11 | trf_jj_baike_jina.txt | 百度百科（jina） | 跳切/定格手法概括/母题/「朱尔，看着我们」/罗什-特吕弗交往史 |
| 研S12 | trf_jj_newwave_jina.txt | newwavefilm.com 专页（jina） | 制作全史：Helen Scott 信/莫罗原话/赫塞尔来信全文/多米诺定格逐镜描述 |
| 研S13-27 | trf_jj_review_*.txt | 豆瓣 rexxar 长评 15 篇（6-1226 有用） | 见下「通道发现」；含特吕弗序 6637007、剧本全本 7607913、歌词帖 5948257 |
| 研S28 | trf_jj_tourbillon_frwiki.txt | 法维《Le Tourbillon (chanson)》 | 特吕弗选歌原话（Rezvani 转述：「une femme qui hésite entre les hommes」）/SACEM 联署史/45 转发行 |
| — | trf_jj_britannica_jina.txt | britannica.com/topic/Jules-and-Jim | ❌ jina 403（AbuseAlleviationError，域名级限流非内容问题） |
| — | trf_jj_filmtracks.html | filmtracks.com | ❌ JS 壳无正文 |
| — | trf_jj_whistle_*.txt | Bing/DDG 定向搜索 | 「口哨主题」预设专项搜索零命中（失败留档） |

## 通道发现（本轮新增六条）

1. **fr.wikipedia = 法国片/法语导演一手通道**：frwiki 片条目密度高于英维——导演开拍前自述判词（特吕弗 1961 年「hymne à la vie et à la mort」原句）、改编方法论明说（旁白直读小说原文=对《法国电影的某种倾向》等价场景改编法的正面回应）、学术分析（Lefèbvre 毕加索画作=时间标记+心境镜像）。**法语单曲独立条目**（Le Tourbillon (chanson)）含选歌缘由、SACEM 联署史、唱片发行信息。法国片轮 grep 优先级：frwiki 片条目 > enwiki 片条目；主题歌先查 `fr.wikipedia.org/wiki/<歌名>_(chanson)`。
2. **豆瓣长评=导演亲撰序言中译通道**：review/6637007（仅 6 有用）整篇转帖特吕弗为《祖与占》小说写的中译序——1955 年书摊发现、「让观众无法做出情感上的选择」美学纲领、「三人间纯粹的爱」。低有用数高价值再添一例；选稿关键词表补「序/自序/前言」。
3. **歌词帖=主题歌全文通道**：review/5948257（8 有用）Le Tourbillon 法语原文+中译交错排版全文——支撑「歌词结构=关系结构=剧作结构」分析（相遇-分离-重逢-再分离=三人关系循环）。选稿关键词表补「歌词/主题曲/歌」。
4. **豆瓣长评=中译剧本全本**：review/7607913（50 有用）姜东译全本（题铭诗/旁白/全场次），与 Simon and Schuster 1968 英译本同体系（enwiki 引 Fry 译本 pp.11-100 互证）——剧本层证据唯一来源。
5. **中维条目制作节=导演书转述金矿**：中维片条目制作/发行节整段转述《弗朗索瓦·特吕弗》（江苏文艺出版社 2011，ref 带页码）——15 人剧组、先拍次要场景、每镜 7→3 次、全员到场营造氛围、审查裁定与首映观众数。
6. **爱情密码对照经回测报告转述**：《爱情题材创作密码.md》本机无原文 → 《回测报告/雨季不再来_爱情密码回测.md》逐条转述（李安轮同型再证）。对照产出「**捆绑型悲剧**」=爱情密码第二形态（vs 五范本「错过型」）：重心戏=毁灭行动而非吵架、结局=解脱的重量而非遗憾、表达通道第三型=文学旁白直读原著。此类补密码缺口的分析框架须在诚实声明标注「非密码原文、非导演自述」。

## 校验 norm 管道五新坑（入 _verify_jj.py 实测）

1. **wayback 换行拆开属格 `'s`**：Ebert wayback 提取 "Jeanne Moreau\n's" 压空白后成 "moreau 's"（**空格在撇号前**）——norm 须 `re.sub(r" 's", "'s", s)`；方向写反（`"' s "`）则漏修，属格短语必假 MISS。
2. **软连字符断词**：Criterion 类 HTML 提取文本含 U+00AD（"film his\xadtory"），引文 "film history" 必假 MISS——norm 第一步 `s.replace('\u00ad','')`。
3. **删引号后残留双空格**：删除引号字符后其两侧空格留下 "and  jules and jim  is"（双空格），单空格短语假 MISS——norm 末尾（删标点/引号**之后**）必须再 `re.sub(r'\s+',' ',s)` 折叠一次。
4. **head-N 短语兜底掩盖真差异**：前 12 字兜底把「…与那尊使朱尔与吉姆…」vs 存档「…与那尊使朱尔**和**吉姆…」误判为通过（单字差异恰在兜底窗口外）——**取消短头兜底，改全量匹配**；合法摘录（省略号拼接）单独拆碎片句逐条验证。
5. **转帖剧本错字须逐字保留**：中译剧本转帖含错字（撤谎/撒谎、眼晴/眼睛、一一/——），引用必须按存档原文+「原文如此」标注，不可自动纠正（纠正必 MISS）。grep 定位时也按存档字形搜。

## 预设处置

- **「口哨主题音乐」未取证到（完整处置例）**：27 档全量 grep「口哨/whistl/siffl/哼」0 命中 + Bing/DDG 定向搜索无果 → 以可证实的音乐结构替代：旋转木马开场（Ebert）、Le Tourbillon 主题歌（歌词=关系结构）、Delerue 配乐承载情感（Crowther）；诚实声明逐条对照，不虚构口哨动机。

## 其他留档

- **NYT wayback 快照可用性不同**：`web/2022id_/<url>` 返回 gzip 二进制乱码；先 CDX 查真实时间戳（`cdx/search/cdx?url=…&output=json&limit=10`），取 20201116024334id_ 即得干净 TimesMachine 全文——同一 URL 不同快照可用性不同，二进制时换时间戳而非放弃。
- **法维引文含撇号/重音**：norm 的字符白名单须覆盖 `\u00c0-\u024f`（Latin-1 Supplement+Extended-A），否则法文引文（l'impossibilité）被整段删除。
- **豆瓣长评=台词帖**（5520415，4 有用）可补剧本无行号台词的另一种形态（主题句「我们玩弄生命的源泉，却失败了」双帖互证：1503079 标题+5520415 正文）。
