# 波兰斯基深化轮来源地图（2026-08）

跨作品演变矩阵（手法体系深化）零存量全新建档轮。产出：《波兰斯基_手法体系深化.md》（技法卡片源稿/，16 存档 S1-S16 自建编号，第五种编号变体——导演无主卡片）。

## 存档对照（pages/polan_*，本轮新抓 16 项）

| 编号 | 存档 | 内容 |
|---|---|---|
| S1 | polan_enwiki_raw.txt | 英维导演主条目 Roman_Polanski（162KB raw：WWII/Holocaust 童年 @3902/9397、「Get lost!」父亲诀别 @9824、Pianist 自述 @40833、Apartment Trilogy 定义 @29547、Chinatown 叙述 @26848） |
| S2 | polan_rosemary_enwiki_raw.txt | 英维《罗斯玛丽的婴儿》（暗门/隔墙阴谋） |
| S3 | polan_tenant_enwiki_raw.txt | 英维《怪房客》（Kafka influence 段/结局复制 Simone/Staben 德评引文） |
| S4 | polan_chinatown_enwiki_raw.txt | 英维《唐人街》（Themes 段 neo-noir/fatalism/bleak ending） |
| S5 | polan_repulsion_enwiki_raw.txt | 英维《冷血惊魂》（POV/墙裂/手从墙出/RT consensus） |
| S6 | polan_pianist_enwiki_raw.txt | 英维《钢琴家》（Szpilman 自传/躲藏序列） |
| S7 | polan_zhwiki_raw.txt | 中维导演主条目「羅曼·波蘭斯基」（公寓三部曲/影响源=布努埃尔+考克多+克鲁佐+希区柯克） |
| S8 | polan_rosemary_zhwiki_raw.txt | 中维「魔鬼怪嬰」（18 字节 redirect 存根→目标条目名） |
| S9 | polan_chinatown_zhwiki_raw.txt | 中维《唐人街 (電影)》 |
| S10 | polan_pianist_zhwiki_raw.txt | 中维《钢琴家 (电影)》（战地琴人） |
| S11 | polan_crit_repulsion_1207.txt | Criterion essay "Repulsion: Eye of the Storm"（Bill Horrigan，wayback 139KB） |
| S12 | polan_crit_rosemary_2535.txt | Criterion essay "Rosemary's Baby: It's Alive"（wayback 100KB） |
| S13 | polan_crit_rosemary_2541.txt | Criterion essay "Stuck with Satan: Ira Levin on the Origins"（wayback 111KB，Levin 亲述锚定现实句） |
| S14 | polan_ebert_rosemary.txt | Ebert 1968 影评（horrifyingly inevitable 核心句） |
| S15 | polan_ebert_tenant.txt | Ebert 1976 影评（差评，浴室窗回望/建筑恶意机制描述） |
| S16 | polan_ebert_chinatown.txt | Ebert 1974 影评（great movie 版本） |

并行轮共享 pages/ 出现 57 档 polanski_* 存档（唐卡/钢琴卡轮：baike×5、豆瓣长评×10、SoC 专条 3 档 94KB、guardian、enwiki/zhwiki）——深化文档定稿前重扫确认《唐人街_技法卡片.md》《钢琴家_技法卡片.md》已落盘，但**未及补 [卡X] 转引链升级与「写作时未落盘」表述更新**（工具上限遗留，下轮先补）。

## 本轮新坑三例

1. **write_file 内容转义残留坑**：write_file 的 content 里写 `\"`（转义引号）会被逐字落盘为反斜杠+引号（136 处），引文提取正则 `"([^"\n]{25,500})"` 全灭、批量校验整片假 MISS。修复 `doc.replace('\\"','"')` 后 0 反斜杠即通过。与盗梦轮「write_file 弯引号规范化」坑同族（那坑是弯引号变直引号；本坑是转义残留）——**写长文档落盘后先 `doc.count('\\"')` 探测，非零即修复再校验**；且 patch 工具替换时 new_string 里也不能带 `\"`（二次引入同坑，实际发生）。
2. **HTML 存档 norm 缺 html.unescape 假 MISS**：Ebert wayback 抓的是原始 HTML，正文含 `&#8217;`/`&#8220;` 实体；norm 管道先 `htmlmod.unescape(s)` 再归一撇号/引号，否则 couldn't/couldn&#8217;t 形态断匹配（本轮 couldn't help her 即此因）。凡是 wayback 直抓的 HTML 存档（Ebert/Criterion/报纸）norm 首步必须 unescape。
3. **vs 节转引引文的校验目标=对方文档本体**：vs 节转引对比导演深化文档的引文（There is no terror in a bang / the less-you-see / He filmed without using Steadicams）不在本导演 polan_* 存档里——校验时把对方深化文档文件加入 NORM_ARCH 存档集（`archives['希区柯克深化'] = open(...)`），而不是豁免；这是麻将轮「主卡片中文转述引文校验把主卡片本体入存档集」（㊿③）向 vs 节转引的扩展。

## 预设修正与诚实声明要点

- 任务预设「黑色宿命线（唐人街→冷血惊魂）」**归线修正**：冷血惊魂 1965 经〔S1〕Apartment Trilogy 定义实为封闭空间线第一部；黑色宿命线以唐人街为唯一逐片取证代表，死亡与少女/影子写手为片单级证据（逐片手法未取证到）。
- Ebert 冷血惊魂/钢琴家影评 CDX 定位与直抓均失败（wayback 限流），未纳入存档——诚实声明第 4 条。
- 怪房客 Criterion essay 未取证（站内搜索 403/CF 拦截），诚实声明第 5 条。
- 中维条目名探测：罗斯玛丽的婴儿=「魔鬼怪嬰」（失婴记/罗丝玛丽的婴儿均 redirect 到它）；怪房客/冷血惊魂中维无独立条目（srsearch 0 命中）。

## 校验记录

58 英文引文 0 MISS（vs 节 3 条转引经对方文档本体校验）；S1-S16 正文↔附录双向对账零孤儿零越界；3 处真错修正（Criterion 措辞 at the heart of its lunatic premise / Ebert we are wrenched / 英维 He reveals that）；1 处 en dash（–→—）按存档原文修正；中文引文仅 1 条真引文（中维公寓三部曲句），分片校验通过，其余「」段为提炼句不参与校验。

## 通道备忘

- zhwiki API srsearch 429 限流 → 退回 `https://zh.wikipedia.org/w/index.php?title=X&action=raw` 直抓 + 读 redirect 存根拿真实条目名（18 字节 `#redirect [[魔鬼怪嬰]]` 即条目名线索）。
- rogerebert.com live 403（CF）→ wayback CDX 定位（`filter=statuscode:200&fl=timestamp,original&collapse=digest`）→ `https://web.archive.org/web/{ts}/{orig}` 直抓；CDX 频繁超时需 tries+间歇 sleep（4-5s）重试。
- Criterion 站内搜索经 r.jina.ai 也 403 → 改从 enwiki raw 的 External links/refs 挖 posts 链接（Repulsion 1207、Rosemary 2535/2541 均由此拿到）→ wayback 直抓 essay。
- Ebert 正文提取：HTML 去 script/style/tag 后 html2text，正文起点=标题行首次出现处（wayback 横幅在标题前）。
