# 《蜀山传》单片研习轮来源地图（2026-08-07）

## 轮次定位

- 徐克补代表作单片轮（创作极=仙侠/特效先驱/东方玄幻），产出《蜀山传_研习报告.md》+《蜀山传_技法卡片.md》
- 前置资产：《徐克_手法体系深化.md》《徐克_导演美学卡片.md》——本片=深化文档「志怪浪漫线·数字特效转折」节点
- 编号体系：独立 [研S1-25] + 来源表「对应深化文档」列映射（研S23/24/25=深化 [S2]/[S1]/[S11] 存量复用）
- 任务预设四项（御剑飞行/人剑合一/门派体系/2001 特效里程碑与成败）全部取证成立零证伪；深化文档 8 项对照全证实

## 存档清单（19 新抓 tsui_zu_* + 3 存量复用）

| 存档 | 内容 |
|---|---|
| tsui_zu_enwiki_raw.txt | 英维 The Legend of Zu（预算 HK$90M/票房 HK$11,757,088/Miramax 未院线/80 分钟美国版/电影节撤片/徐克 disaster 转引/条目挂 Unreliable sources 模板 2026-04） |
| tsui_zu_zhwiki_raw.txt | 中维「蜀山传」（演员表/金马金像奖项/1600 特效镜头四家美国公司/2000-06 实景完成） |
| tsui_zu_zhwiki_render.html | 中维渲染页（豆瓣 id 1308338 由此 grep 定位） |
| tsui_zu_reviews.json | 豆瓣长评列表 total=198（先验 total 再采信） |
| tsui_zu_rev_*.txt ×12 | 豆瓣长评 316/274/204/115/72/64/38/35/25/19/9/1 有用（含《语录》1 有用=影迷记录台词通道再例、负面样本 35/25 有用） |
| tsui_zu_lovehk_clean.txt | LoveHKFilm Kozo 影评（负面但承认视觉壮观/美术设计） |
| tsui_zu_hku_schroeder.pdf/.txt | **HKU Press Schroeder《Tsui Hark's Zu》2004 官方 PDF 预览 25 页**（一手学术层） |
| tsui_zu_novel_enwiki/zhwiki.txt | 原著《蜀山剑侠传》条目（1932/500 万字/329 回未完成） |
| tsui_zu_ebert_search.txt | Ebert 负面取证（rogerebert.com 站内搜无本片专评） |
| tsui_zu_crit_search.txt | Criterion 负面取证（242 字节无命中） |
| tsui_zu_rt.html | RT 页面（**数值弃用**：内嵌多电影 JSON，tomatometer 多个值归属不明） |
| tsui_filmcomment1/2.txt、_soc_tsui.txt | 存量复用（=深化 [S1][S2][S11]，FC 灾难自述/特效纪实/SoC 新世界原话） |

## 新通道：HKU Press 学术书官方 PDF 预览（港片学术专著一手通道）

- **发现路径**：英维 ref 引 Andrew Schroeder《Tsui Hark's Zu: Warriors From the Magic Mountain》(HKU Press 2004) → DDG 搜 `"HKU Press" <书名>` → 结果 uddg 参数直接给出 `hkupress.hku.hk/image/catalog/pdf-preview/<ISBN>.pdf`（ISBN 9789622096516）
- **提取配方**：`pip install pymupdf` → `pymupdf.open().get_text()` 一次到手；25 页≈目录+系列序+引言（Chapter 1 开头）+结论（Chapter 5）开头，学术层一手
- **本轮回馈**：引言含「1983 版=香港本地首部直接雇佣好莱坞特效人才」「徐克好莱坞受挫→90 年代末回蜀山世界做数字后继」演变链；结论含「空间→时间」母题裁决（Legend of Zu 把对空间的执迷转为对时间的关切——数字合成失重中对历史重量的呼喊）
- **局限**：仅预览页（第 2-4 章正文未获取），引用须声明「预览可得内容」
- 港片导演轮优先查此通道（HKU Press 有 Hong Kong Film Classics 系列专著）

## 新坑三例

1. **豆瓣 subject id 探测三坑**：① `subject_suggest` 端点可直挂 404 `traversal_error`（被禁）——别纠缠，改抓 **zhwiki 渲染页** grep `subject/[0-9]{6,9}` 拿真实 id（raw 里 `{{douban}}` 模板可能无 id 参数、渲染页才有）；② **猜的 id 可能命中别片**——1308825 实为《欢乐之家》(2000)；**错 id 信号 = reviews 接口返回 total=1 且仅 1 条无关评论**（正常热门片应 100+）；③ 抓回 reviews 列表先验 total 与评论标题再采信。
2. **zhwiki API 429 限流（"You are making too many requests"）→ `w/index.php?title=<T>&action=raw` 带浏览器 UA 兜底**——与「raw 挂走 API」互为反向兜底；API 探测失败先 sleep 10-15s 再试或直接换 raw 端点。
3. **RT tomatometer 归属不明弃用**：rottentomatoes.com 页面内嵌多部电影 JSON（`"tomatometer":(\d+)` 匹配到 8 个值），单值 grep 无法归属本片——og:description 只能确认页面主题，数值弃用并诚实声明。

## 标题形态补充

- **繁体条目=重定向存根反向形态**：中维「蜀山傳」raw 返回 `#REDIRECT [[蜀山传]]{{簡繁重定向}}`（42 字节）——简繁反向（多数情况是简体→繁体重定向），读重定向目标再抓；「蜀山传」真实条目名是**简体**（与喋血双雄轮同型再例）
- enwiki 真实标题 The Legend of Zu（srsearch `Legend of Zu film Tsui` 一次命中，裸名无 (film) 后缀）

## 百度百科歧义新变体

- 裸词条 `item/蜀山传` 重定向到 **1983 前作《新蜀山剑侠》**词条（系列前作歧义，非同名异作）——系列片轮注意裸词条可能命中前作，需 DDG 定位或弃用

## 校验记录

- 84 引文 0 MISS；3 条假 MISS 全由 norm 修复：
  - ① 中文引号「“道”是无法传授的」——norm 删除表补 `“”`（此前只删《》「」【】）
  - ② wikitext 斜体标记 `''Zu Warriors''`（`''` 残留使短语 `under the title zu warriors` 不匹配）——norm 补 `s.replace("''", ' ')` + 标点前空格清理
  - ③ 校验短语漏词（"overstuffed doesn't begin" vs 原文 "doesn't even begin"）——短语从文档逐字复制，别凭记忆
- 校验脚本结构：norm 双侧套用 + 期望存档关键词列（expect）+ 笛卡尔积式匹配（存活性）

## 未取证清单（写入诚实声明）

- 徐克「当一个人得到永恒……」原话=豆瓣长评转引（原始访谈出处未核到）
- 1600+ 特效镜头的独立统计（中维口径；Film Comment 只给「超过魅影危机」比较级）
- RT tomatometer 数值、美国 80 分钟版删减清单、豆瓣评分接口（长评转述 6 分多）
- 本片无公开剧本（juben.pro 未查；台词=影迷《语录》帖分级标注）
- 后世仙侠影响链（万剑齐飞/御剑飞行/元神碎片化）=观察级推断，无第三方并列文献
