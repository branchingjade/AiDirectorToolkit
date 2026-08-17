# 楚原轮（Chor Yuen）· 2026-08-09

武侠轴补齐研习轮。产出《楚原_导演美学卡片.md》+《楚原_手法体系深化.md》（`_work/导演研习-20260809/楚原/`），pages/ 存档 20 个 + verify_citations.py。本文档为轮次地图：新通道、证据链、坑复证。

## 新通道（供香港老导演轮复用）

1. **HKFA Oral History Series 口述史**（`lcsd.gov.hk/CE/CulturalService/HKFA/en_US/web/hkfa/rp-oral-history-series-4-1.html`）：英文版 curl 直抓无壳；Preface 由研究者（Grace Ng/Kwok Ching-ling）执笔转述 2004 年访谈。URL 从 enwiki 主条目 ref 挖（`lcsd_gov_hk` ref）。中文版 URL 404 属正常，用英文版。楚原轮金句：
   - "Chor Yuen declared himself a romantic, which the studio allowed him ample space for expression"
   - 石琪（Sek Kei）"the 'last heir to the studio system'"；绰号 "The Studio Animal"
   - 标志物象 "the omnipresent red maple leaves (quivering leaves on bare branches in the black and white era) and the setting sun in the horizon"
   - 布景观 "Every tree or tower could be recycled in a new context, for it was the impressionistic realm Chor Yuen was interested in"
   - 价值定位 "the essence of chivalrous knights-errant was more important than historical accuracy"
   - "The narration may be winding and bizarre, but it is eventually, a lament upon this imperfect world"
2. **金像奖获奖感言 = 港导演一手话金矿**：zhwiki ref → mpweekly archive-url 直抓粤语原文（楚原 2018 感言快照 20180619142000）；即刻 App 用户转录版为第二版本（更完整但措辞出入）。双版本并存必须标注版本差异。感言常含导演自曝行业恩怨（方逸华拦拍《天龙八部》原话），一手密度极高：
   - "人生呢兩個字，就係歡聲、淚影四個字砌成……明天總比昨天好"
   - "邊個比你拍《天龍八部》？蝕咗本你有得賠咩？……楚原你根本唔識電影藝術，唔識拍電影"
   - "管他天下千万事，闲来轻笑两三声"；"不因碌碌无为而悔恨，不因虚度年华而羞耻……不负此生"
3. **香港影评库 filmcritics.org.hk 可直连 curl**（不必 wayback）：蒲锋《楚原：回首半生 青衫人老》（明报 2018）直抓全文；zhwiki ref 里的 URL 编码路径直接可用；文末带作者/刊物/年份字段，引用署名以此为准。
4. **中维港片条目名带间隔号·**：《流星蝴蝶劍 (1976年電影)》真实条目名是「流星·蝴蝶·劍 (1976年電影)」——探测先过 `action=query&titles=`（redirects=1）；港片条目常无 `{{douban|id}}` 模板（三部楚原片条目 douban id 全空）→ subject_suggest（iPhone UA + Referer: https://m.douban.com/movie/）直连兜底一次全中。
5. **SCMP paywall 头部截断再证**：文章截到 ~2.5KB 时，头部已含核心一手引文（"adapted 17 works"、"For five years, I made nothing but Gu Long pictures"——楚原 HKFA 访谈原话），用头部事实即可。

## 关键证据链（供转引）

- 楚原自述方法论（北京日报王金跃转述）："自己不过是用擅长的文艺片手法进行拍摄，注重营造浪漫的氛围，擅长编排奇诡悬疑的情节，追求华丽精致的美术风格"
- 片类定义式创作：《天涯明月刀》=奇情浪漫短篇散文；《楚留香》=007式风流侠盗侦探片；《白玉老虎》=江湖恩怨片；《三少爷的剑》=写人性的文艺片
- "邵氏出品、古龙原著、楚原导演"金字招牌；邵氏"四大帅"（李翰祥/胡金铨/张彻/楚原，中维 + 北京日报双证）
- 写意武打："对打是快到扎乱麻，绝不过多过招"（豆瓣 6142678）；"无招胜有招，一招毙命，都是高手神交时气场间的比较"（豆瓣 10100671）
- 色彩谱系金句："张彻是浓烈，张艺谋叫做浓艳，楚原呢，是浓郁"（豆瓣 1159009）
- 双口径：古龙改编 17 部（SCMP）/18 部（北京日报）；导演总量 120+（英维）/近 130（中维）——均并存标注

## 校验与对账

- 61 条引文 0 MISS（双侧 norm：压空白/删引号/繁简映射/全角标点族；笛卡尔积变体匹配）
- S# 双向对账：正文 S1-S23 ⊆ 清单、清单零孤儿号（S22/S23 初为孤儿，补引用闭环——雪国列车轮 ③ 再证）

## 坑复证

- **繁简映射表长度 assert 再证**：手写 TRAD/SIMP 时「我們家 vs 我们家里」多字（561 vs 562）被 assert 抓到——补字时多字词两侧必须逐字对齐（㉒/㊵② 的第三实例，assert 有效）。
- **校验短语必须从文档引文复制（㊲ 再证）**：手写「楚原會花心思設計片頭字幕的場面」实为文档转述非引文 → 假 MISS；替换为文档真实引文（「這種戲中人面向觀眾的自白方式，在1950年代是極之罕見的」等）后 0 MISS。
- **任务模板路径 `_knowledge` vs `_知识库`**：任务给的模板参考路径 `C:\...\skills\妖玉影视\_knowledge\references\...` 404，实际目录是 `_知识库`——先 find 全盘定位再读，别按任务路径硬读。
- 金像奖感言双版本措辞差异（明周粤语版 vs 即刻完整版）需在诚实声明标注。

## 未取证到（诚实声明已载）

百度百科楚原词条（403）；SoC Great Directors 专条（站内搜索未命中——楚原无此专条，用单片代偿）；2006 资料馆《楚原》专书全文（仅经中维转引页码）；武打镜头数/均镜时长等量化数据（无统计，不同于胡金铨 5.6s 均镜）。
