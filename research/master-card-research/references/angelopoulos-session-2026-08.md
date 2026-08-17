# 安哲罗普洛斯研习轮记录（导演研习轴·欧洲作者导演第一轮）

轮次：知识库 v2.0 M1-③ 导演研习轮 2026-08-09，14 位导演并行子代理。产出《安哲罗普洛斯_导演美学卡片.md》+《安哲罗普洛斯_手法体系深化.md》写入 `C:\Users\HMSJ\Documents\Hermes\_work\v2-导演研习-20260809\安哲罗普洛斯\`。

## 模板与规范位置（导演研习轮通用）
- 卡片模板（八段结构：①风格签名 ②美学体系表 ③创作思路 ④招牌桥段 ⑤画面锚点 ⑥可复用时机 ⑦AI 提示词对接 ⑧诚实声明+来源清单）：`AppData\Local\hermes\skills\妖玉影视\_知识库\references\导演美学卡片\侯孝贤_导演美学卡片.md`
- 深化模板（演变脉络结构：作品矩阵归类→手法演变脉络（跨片看变化）→可复用工具箱→vs 其他导演→诚实声明）：同目录 `胡金铨_手法体系深化.md`
- 轮次规范：`_work\v2-导演研习-20260809\规范.md`（来源纪律：每条论断带编号、grep 验证、不编造来源、一手>二手>维基、诚实声明未逐帧看片+双口径、输出全中文）

## 来源 URL 清单（7 个存档，全部 curl 验证）
1. `angelopoulos_enwiki.txt` — enwiki `action=raw` Theo_Angelopoulos 主条目（49KB）：风格签名/影响谱系/寻父创伤/80 shots in 4 hours
2. `landscape_enwiki.txt` — enwiki `action=raw` Landscape_in_the_Mist（13KB）：剧情（寻父/一夜情真相/强暴省略/巨手/雾树结尾）、Themes 段、Karaindrou 双簧管、报纸新闻灵感
3. `eternity_enwiki.txt` — enwiki `action=raw` Eternity_and_a_Day（9KB）：垂死诗人/阿尔巴尼亚男孩/三个单词/铁丝网挂尸/黄雨衣骑车人/结局"明天=永恒和一天"
4. `soc_angelopoulos.txt` — Senses of Cinema Great Directors 专条（Acquarello，**直连** 148KB HTML → `<article>` 正则剥标签 22KB）：完整传记（war child/Red December/IDHEC）、历史/沉默/边境三部曲结构、Horton 1993 访谈长引、戛纳 1998 感言
5. `guardian_obit.txt` — The Guardian 讣告 Ronald Bergan 2012（**直连** 377KB HTML → `<div id="maincontent">` 段 6.6KB）：一手引语（1986 sequence shot 自由论、金棕榈忘词、"epic poet of the cinema"、形而上公路片）
6. `angelopoulos_zhwiki_raw.txt` — zhwiki `action=raw` 泰奧·安哲羅普洛斯（11KB）：作品风格段（行云流水长镜头/阴霾冬日/雾中风景/静水时间/诗画空间）
7. `soc_gaze.txt` — SoC Bill Mousoulis《Angelopoulos' Gaze》(2000)：摄影机"几乎总在移动"/凝视主题/与罗西里尼塔可夫斯基对比
- 失败（Cloudflare 全拦，标"未取证到"）：Criterion essay（criterion.com 与 jina 均拦）、BOMB 杂志访谈、The Artifice 深度文、SoC 旧期链接（1998 期 404，web_search 找回 2000 新版）

## 已验证引语锚（可直接复用）
- "The sequence shot offers, as far as I'm concerned, much more freedom. By refusing to cut in the middle, I invite the spectator to better analyse the image I show him..."（Guardian 转引 1986 访谈）
- "time becomes space and space becomes time."（enwiki 引 Fainaru 访谈集 p.87）
- "The only specific influences I acknowledge are Orson Welles for his use of plan-sequence and deep focus, and Mizoguchi, for his use of time and off-camera space."（enwiki 引 The Last Modernist）
- "80 shots in about four hours"（《流浪艺人》单口径）
- "the silence of history / the silence of love / the silence of God"（沉默三部曲自述）
- "We've crossed the border and we're still here. How many borders must we cross to reach home?"（《鹳鸟踟蹰》难民台词）
- korfulamu / xenitis / argathini（《永恒和一日》三个单词）
- "I belong to a generation slowly coming to the end of our careers"（1998 戛纳）
- "I had prepared a speech for the Palme d'Or. I have now forgotten it."（1995 戛纳失意）
- "The village is a complete world in miniature."（Horton 1993 访谈，SoC 专条引）
- 中文维基风格段："行云流水般的长镜头……静如止水的时间、诗画叠加的空间"

## 成文后全量引语回扫法（本轮新验证的收尾步骤，抓出 3 类真错误）
写完后从产出 md 正则提取全部引号内英文片段（`re.findall(r'[""]([^""\n]{15,})[""]', txt)`），归一化后逐一 `in` 匹配全部存档 corpus；未命中项逐条人工判断（AI 提示词/中文混合/已标注摘要级可跳过）。本轮抓到：
1. **归属错误**："the powerful symbol of the corpse as the silent accuser" 实属 Guardian（S5）非 SoC（S4）——写前逐条验证时只验了"存在"，没验"在哪个文件"
2. **词序错误**：原文 "long, slow and boring" 写成 "slow, long and boring"
3. **插入语假失败**："yellow jacketed [...] repair workers" 原文中间含 SoC 插入语 "a familiar, idiosyncratic image in Angelopoulos' cinema"——整句不连续，需 `[...]` 标注
另有：Karalis 学术书章节摘要句（"Germany has no border with Greece...Heaven has no border with Earth"）根本不在任何存档——它来自 web_search description，曾误标 [S2]，回扫抓出后改标"摘要级取证"并写入诚实声明。

## 关键陷阱
- **搜索摘要引语不得直接引用**：web_search 结果 description 里的引语可能是学术书/付费文章摘要，不在任何存档中——必须回原出处存档才能引用，否则标"摘要级取证"。
- **zhwiki API 连发 429**："You are making too many requests to the API."——直接改 `action=raw` 单条抓取即可（raw 不受 API 限流影响）；简体标题是 40B `#REDIRECT [[繁體名]]`，跟重定向抓繁体。
- **SoC 直连提取**：`re.search(r'<article.*?>(.*?)</article>', raw, re.S)` 剥标签后 22KB 正文；SoC 旧文章 URL 会 404，`site:sensesofcinema.com <人名>` 找回新路径。
- **Guardian 直连提取**：`<div id="maincontent">` 段；讣告转引的导演原话标注"经讣告转引"，非逐字一手录音。
- 安哲主条目无独立 Style 段——风格引语散在 Biography 各段（grep 关键词定位），与侯孝贤等华语导演条目结构不同。

## 安哲核心手法锚（供国风对接）
- 旅程母题四阶段：离乡（《重建》男人消失）→ 返乡幻灭（《塞瑟岛之旅》）→ 寻父即寻神（《雾中风景》虚目标）→ 一日即存在（《永恒和一日》）
- 长镜四阶段：审查省略（军政府时代）→ 自由主张（1986 访谈）→ 时空本体（time becomes space）→ 凝视伦理（Mousoulis）
- 雾=可见性政治（雾树结尾：雾散=抵达）；灰调风景+单点亮色（黄雨衣/黄夹克=流亡者移动锚点）
- 历史创伤：国家寓言（演不完的戏=循环创伤语法）→ 私人记忆（父亲 Spyros）→ 地理边界（边境婚礼）→ 存在之痛
- 导演研习深化文件的可复用工具箱五件：虚目标旅程/循环仪式/单镜时间/灰调锚点/边界乡愁（各附 AI 提示词写法）
