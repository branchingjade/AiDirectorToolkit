# 风之谷单片轮 2026-08（宫崎骏《风之谷》1984）来源地图

> 单片研习轮：产出《风之谷_研习报告.md》（33.6KB，10 章）+《风之谷_技法卡片.md》（22.9KB，8 卡）。校验脚本 `pages/_verify_nausicaa.py`：72 引文 0 MISS（含繁简/引号/空白/wikilink 双向归一）。

## 存档清单（pages/）

| 编号 | 文件 | 内容 |
|---|---|---|
| 研S1 | nausicaa_en_raw.txt | 英维 raw（新抓 78KB）：Plot/Production/Influences and themes/Gliders/Warriors of the Wind/Manga/Reception |
| 研S2 | mzk_wiki_zh_nausicaa.txt | 中维「風之谷 (電影)」存量 92KB = 宫崎骏深化文档 [S4] 同档（企划书 quote box/结局三方案/圣女贞德自评/ゴムマルチ/荻原学术批评/押井守批评） |
| 研S3 | miyazaki_wiki_en_raw.txt | 英维宫崎骏主条目（存量 205KB） |
| 研S4 | ebert_nausicaa.txt | RogerEbert.com「From the Valley of the Wind」（2012-12-14）——⚠️ 作者 Michael Mirasol 非 Ebert |
| 研S5 | nausicaa_reviews.json | 豆瓣长评列表（subject 1291585，653 条） |
| 研S6-12 | nausicaa_rev_*.json ×7 | 长评 1005538/2861907/1179068/7465162/7640514/8593580/8672014 |
| 研S13 | guardian_ghibli_rank.txt | 卫报《Every Studio Ghibli film – ranked!》Nausicaa 条目（第 11 位） |
| 负面 | crit_films_sitemap.xml / ebert_search.txt | Criterion sitemap 全列表 / RogerEbert 站内搜索 |

## 渠道实测（新技三例）

### ① Criterion sitemap 定位法 = essay 负面取证的标准动作
criterion.com 搜索页/API 全站 CF 壳；DDG/Bing/Mojeek 全反爬（202/验证码/Captcha）时，Google 403——
- `curl http://sitemap.criterion.com/index.xml`（robots.txt 公开、无 CF 壳，Sitemap 指向独立子域名）→ 8 个分表（films/current/posts/top10s/boxsets/authors...）
- `curl http://sitemap.criterion.com/films.xml` = 306KB 全部 1712 部影片 URL
- `grep -i <片名>` 0 命中 = **Criterion 未发行该片，essay 渠道负面取证成立**。风之谷轮：nausicaa/mononoke/totoro/ghibli/miyazaki/spirited 全 0——宫崎骏北美发行史 New World(1985)→Disney(2005)→GKIDS(2017+)，Criterion 从未做过。**动画/独立发行片（GKIDS/Janus 外）优先走此负面取证**，省掉整个 essay 搜寻。
- 补充：criterion.com/films/<id> 详情页直连无壳（猜错 id 返回 "Shop All Films" 无关页，title 必验——好家伙轮坑再证）；sitemap 有命中时 URL 即真实 films 页，再 grep current/posts 拿 essay。
- 注意：Criterion 的 essay 只覆盖其自己发行的片——"Criterion essay" 作为任务预设渠道时，先 sitemap 证存在再找 post id，别直接猜。

### ② RogerEbert.com「Far Flung Correspondents」= 客座专栏，作者不一定是 Ebert
- 站内搜索（jina 抓 `rogerebert.com/search?q=<片名>`）结果面包屑 "Roger Ebert › from-the-valley-of-the-wind" 是**栏目归属不是作者**；正文文末 byline 才是作者："Michael Mirasol tweets at @flipcritic"。
- 文章 URL 段是 `far-flung-correspondents/<slug>` 而非 `reviews/<slug>`（猜 reviews/ 路径 404）。
- 2012-2013 Ebert 病中期"回顾旧片"长文多为 Far Flung 客座稿（含客座作者 video essay 嵌入），引用前必读文末署名；抓到后全文 grep byline（"Michael Mirasol"/"tweets at"）确权。
- 补充：Ebert 本人是否评过某片 = 站内搜索确认（风之谷：Ebert 无评，仅 Mirasol 稿 + 星战影响 feature 文）。

### ③ jina × web.archive.org 永久 403 + CDX 不稳定
- **jina 对 web.archive.org 匿名访问永久 403**（AbuseAlleviationError："blocked until Sun Sep 30 2035 ... DDoS attack suspected"）——CDX 查询/wayback 快照绝不走 r.jina.ai。
- web.archive.org/cdx 当天多次 503/429/000（超时）——sleep 10-20s 重试；可用性 API（archive.org/wayback/available）同样会 429。
- Ebert slug 探测失败时的替代路径：rogerebert.com 站内搜索（jina）定位真实 slug/栏目段，比 CDX 通配更快更稳。

## 其他实测

- **豆瓣**：subject id 用 `/j/subject_suggest?q=<片名>` 探测（风之谷=1291585，勿猜）；rexxar reviews 列表（`/rexxar/api/v2/movie/<id>/reviews?start=0&count=30&sortby=hot`）+ `/j/review/<id>/full` 全文 JSON 均正常；长评按 useful_count 排序选稿（1179/661/648/214 有用四篇为核心）。
- **卫报**：Guardian Content API 搜 nausicaa 无独立影评（只有 Ghibli 全片排名文 2020-01-28）——直接抓排名文条目即可；jina 渲染丢署名，引用标媒体+日期不署名。
- **jina 429 限流**：连续请求触发 RateLimitTriggeredError（响应含 retryAfter 秒数）——sleep 30-45s 重试即可，非环境故障。

## 校验坑（本轮新增细节）

- **中维 raw 清洗必须迭代剥 [[wikilink]]**（`while '[[' in t: re.sub(r'\[\[([^\[\]]*)\]\]', lambda m: m.group(1).split('|')[-1], t)`）——`[[昆蟲]]`、`[[衣服|衣裳]]`、`[[聖女貞德]]`、`[[泛靈論|萬物有靈論]]` 断词直接假 MISS（本轮 15 条 MISS 的根因）；`&nbsp;`→空格；norm 管道删全部引号（含英文斜体 `''` 残留与繁体『』）——`''Dune''` 斜体残留会把 "answer to Dune" 断成假 MISS。
- 引文短语必须从交付文档逐字复制：本轮 2 条假 MISS 是短语侧抄错（"took off" vs 原文 "to take off"、"Suzuki, is a high point" vs "high point in the film"）——㊲ 再证。

## 任务预设纠正（写入报告诚实声明）

1. **Criterion essay 渠道不存在**——负面取证（宫崎骏北美发行史），报告标注"Criterion 从未发行本片"。
2. **Ebert 影评渠道实为 Mirasol 客座稿**——Ebert 本人未评过风之谷；引用按作者署名。
3. 深化文档对照发现：腐海=超自然物件规则链（工具→法则→人心镜像）的**真正起点**——"世界法则本身（可被理解）"，森林神是其"不可理解"的下一代形态；风之谷=幽灵公主前身（世界观语法层）。

## 产出

- 研习报告：`film-suite-research/研习报告/风之谷_研习报告.md`
- 技法卡片：`film-suite-research/技法卡片源稿/风之谷_技法卡片.md`（8 卡：腐海生态辩证/理解者主角/滑翔翼/巨神兵/王蟲情绪信号/预言收束/声音道具化/世界观先行）
