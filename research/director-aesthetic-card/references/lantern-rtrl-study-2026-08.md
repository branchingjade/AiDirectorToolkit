# 大红灯笼高高挂研习轮来源地图（2026-08）

无公开剧本华语片（张艺谋《大红灯笼高高挂》，1991）取证全流程实测。产出：研习报告 + 7 张技法卡片，24+ 条引文校验 0 真 MISS。

## 存档清单（pages/ 前缀 lantern_*）

| 存档 | 内容 | 取证价值 |
|------|------|---------|
| lantern_review_{id}.json × 8 | 豆瓣长评全文 | 主证据源 |
| lantern_reviews_all.txt | 合并剥 HTML 版 | grep 用 |
| lantern_ebert_review.html/.txt/body.txt | Ebert 1992 影评（Wayback 快照） | master shot/offstage 老爷/Technicolor 金句 |
| lantern_enwiki_plot.txt / crit.txt | 英文维基 Plot/Critical response 提取 | 剧情流程/音轨曲目名 |
| lantern_juben_search.html | juben.pro 搜索 | 剧本未收录确认 |
| lantern_sogou.html | Sogou 结果页 | 知乎帖线索（未达） |
| lantern_zhihu_search.txt | 知乎安全验证页 | 失败留档 |
| lantern_ddg_interview.html | DDG 202 anomaly 壳 | 失败留档 |
| 复用存量 | yimou_wiki_Raise_the_Red_Lantern.txt、yimou_zhwiki_rtrl.txt、yimou_wiki_Zhang_Yimou.txt、yimou_zhwiki.txt | 张艺谋轮既有存档 |

## 渠道实测

1. **豆瓣 rexxar 选稿策略（关键）**：reviews 列表（`sortby=hot`）拉 20 条后**按标题关键词挑**：构图/色彩/镜头/空间/仪式/结构/细节/赏析——命中即逐篇拉全文。本次 8 篇命中（5832 有用的「其实只有一个女人」直接给出仪式动作序列「抬灯入院，点火，燃灯，悬挂…」+台词转引+五女人五阶段结构；1973 有用的「赏析电影」给出四色体系+俯拍封闭构图+锤脚声配乐+「没有春天」；388 有用的「色彩与构图」给出轴对称/纵深/死人屋）。**高有用数 + 技法关键词标题 = 影评分析金矿**，比漫无目的拉热门强得多。
2. **Ebert 影评 URL 家族再发现**：真实 slug 是 `rogerebert.com/reviews/raise-the-red-lantern-1992`（不是 great-movie-raise-the-red-lantern-1991）。CDX `url=rogerebert.com/reviews/raise-the-red-lantern*`（无 matchType=prefix）直接返回 2013-2016 快照列表，取 2016 快照 83KB 全文。wayback available API 当时 429 限流，CDX 无碍。
3. **Sogou /link?url= 失效形态**：curl 抓 link 页只能拿页脚备案链接（JS 跳转）；Jina 渲染同样拿不到；WebBridge navigate 后跳回 sogou.com 首页（链接过期或需 cookie）。知乎帖线索（「剧本这么改」「为什么不拍老爷正脸」）最终未达——标注未取到，不纠缠。
4. **知乎搜索 = 安全验证页**（jina 渲染返回「进入知乎/系统监测到您的网络环境存在异常」）——知乎搜索/站内检索通道确认不可用，问题页直链才是唯一可能通道。

## 引文校验案例（写卡片纪律强化）

- 「规条例」被凭记忆写成「规条条例」——**多字/少字的假引文**，校验脚本 grep 出 MISS 后对照存档原文修正。教训：写卡片引文必须从存档逐字复制（含标点），不许凭记忆补字，哪怕只差一个字。
- 「淡出鏡後」vs「淡出镜后」= 繁简假 MISS（已知坑再次验证），grep 原文确认后按繁转简转写并可在声明里注明。

## 未取到清单

- 张艺谋一手访谈原话（DDG 限流/Sogou 失效/知乎验证墙）——创作思路用中文维基评述「光影、构图、色彩均十分讲究，文化气息十足，象征意味浓厚」+ 影评人分析推断，诚实声明标注
- 剧本原文（juben.pro 未收录）
- 台词均为豆瓣长评转引（非逐字剧本稿），已在声明标注
