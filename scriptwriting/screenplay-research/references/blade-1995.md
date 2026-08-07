# 《刀》(The Blade, 1995, 徐克) 多源取证记录

> 2026-08-07 实测。任务：深挖《刀》产出研习报告+技法卡片（妖玉影视知识库范本研习线）。
> **无公开剧本**——juben.pro 站内搜索 `/search/?SearchKeywords=刀` 确认无此片（结果全是《刀疤》《操刀伤人》等无关作品），华语片公开剧本稀缺的又一实证；全片证据走多源取证。

## 豆瓣 rexxar API 直连（本片验证的核心配方）

- 条目：`https://m.douban.com/rexxar/api/v2/movie/1401962` → 标题/评分 8.1/55158 人/aka（断刀客, The Blade）/简介 intro
- 影评列表：`https://m.douban.com/rexxar/api/v2/movie/1401962/reviews?start=0&count=30&order_by=hot` → `total` 167 + 每篇 id/标题/星级
- 影评全文：`https://m.douban.com/rexxar/api/v2/review/<id>` → `content` 字段是 HTML（`<p data-page="0">`），剥标签即全文，**未登录可读完整全文**
- 请求头：`User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15` + `Referer: https://m.douban.com/`
- **ID 定位（360 搜索法）**：`curl -s "https://www.so.com/s?q=<片名 导演 豆瓣>"`（UA + Accept-Language: zh-CN）→ 正则 `<h3[^>]*>\s*<a[^>]*href="([^"]+)"` 提取 `so.com/link?m=...` 跳转链接 → `curl -sL` + 浏览器 UA 跟随 → 页面含 `movie.douban.com/subject/1401962` 即得 ID。**旧记录"360 跳转 curl 只得 300B 壳"不成立：-L + UA 可跟随**。
- 验证 ID 的正确姿势：rexxar movie 接口返回的 `aka`/`title` 直接核对（猜 ID 再用接口验证会撞到别的片——1297598=《露西娅的情人》、1298645=《假红绡翠》，都是错 ID）。

## 证据栈（本片可用组合，华语片通用）

1. 维基中文 `action=parse&pageid=<id>&prop=wikitext`（《刀》=6929970）——演员表/奖项/票房/歌曲全；维基中文条目短，剧情细节靠英文维基
2. 英文维基（页面名要搜：`The Blade (film)` 而非 `The Blade (1995 film)`）——完整剧情/Style/Reception/后世发行
3. **Film Comment 2011 徐克访谈两篇**（本地存档 pages/tsui_filmcomment1.txt + tsui_filmcomment2.txt，徐克/港片研习常备源）——本片一手材料全在这：刀 vs 剑之辨（"dao is a heavier, more cleaver-like weapon that connotes butchery, brutality, and the hacking of flesh and bone"）、纪录片风格（"only two shots used wirework"）、开场和尚不赢（"we start off with a monk, one of the icons of justice, not really winning"）、跳轴镜头三替身+徐克掌机、结局一周拍完、受黑泽明《七武士》影响（"I was influenced by Kurosawa"）、拍完想继续此风格但去了好莱坞
4. 豆瓣影评 7 篇全文（rexxar）——选文法：列表页标题+星级挑关键词命中篇（"误解最深/断刀/江湖/独白/失落的电影"）；长文优先（4193 字那篇含残缺系统/女性视角/年代模糊学术分析）
5. **Criterion 官方页**（2026-03-31 发行 4K）——`criterion.com/films/34862-the-blade` 被 Cloudflare 挡，`https://r.jina.ai/https://www.criterion.com/films/34862-the-blade` 直出 markdown；官方简介=权威风格论断（"a whirlwind of immersive close-ups and fractured editing"、"action expressionism"、"scathing reappraisal of the wuxia genre's code of masculinity"）；**特典清单会暴露一手资料线索**（本片含 2006 纪录片《Action et vérité》徐克/许安/熊欣欣出镜 + Lisa Morton 论文——后续补证首选）
6. BAM 2014 放映介绍（wayback）——Variety 评语 + Stephen Teo 评语 + "homage to the macho Hong Kong action films of the 1960s"

## 摘录复核（本片 64 条）

- 首轮 5 处假 FAIL 全因文本层伪影：① Film Comment 英文原文用弯引号（`didn’t` vs `didn't`）——归一化须 `’→'`；② r.jina.ai markdown 斜体（`_wuxia_`）——剥 `_`；③ 一篇影评只存了 json 没转 txt（漏存）——列表/正文抓取后立即统一转 txt 落盘
- 交付 md 复核的 span 提取：`["“]([^"”]{12,})["”]` 在中文散文 md 上会抓出跨段落整块正文——过滤含换行/markdown 符号/URL/`（影评`/`review/`/`pages/` 的 span；转述类引文标 `（中译）` 防误报
- 修稿纪律：破折号 vs 句号差异（md 写 `——`、源是 `。`）按源文改 md，不许凭记忆改稿

## 交付物（film-suite-research 工作区）

- `研习报告/刀_研习报告.md`（三幕骨架/14 画面锚点/潜台词 3+2 例/动作层 5 例/3 桥段/与浪漫武侠差异表）
- `技法卡片源稿/刀_技法卡片.md`（8 张：残缺系统/断刀重生/开场反高潮/犬儒师父/纪录片式动作/终局复仇/反团圆结局/隔空独白）
- 核心提炼：**把"残缺"做成系统**（断臂+断刀+半本刀谱+无名女人）——动作语法从缺陷反推（无底盘→旋转刀法）；动作戏情绪目标从"爽"改"怕"
