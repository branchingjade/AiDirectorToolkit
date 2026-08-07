# 电影技法调研来源地图（2026-08 实测）

任务形态：从 5-6 部高分电影提取具体技法实例（主题结构/潜台词/空间隐喻/视觉叙事/色彩情感/大场面调度），产出带来源 URL 的中文笔记。经典案例实证笔记见 `_work/film-theory/经典案例实证.md`。

## 四级来源分工

| 层级 | 站点 | 提供什么 | 实例 |
|---|---|---|---|
| 1 事实层 | Wikipedia 电影条目 | 剧情/制作记录/主题引用/影史数据（AFI 台词排名、拍摄天数、耗片尺数） | 七武士终战多机位+长焦、148 工作日、13 万英尺胶片（en.wikipedia.org/wiki/Seven_Samurai） |
| 2 阐释层 | rogerebert.com | 影评人对技法功能的解读（旁白功能、象征场景、调性结构） | Ebert 评肖申克：旁白=观察者通道、"灰色底色让关键事件活起来" |
| 3 技术层 | ASC Magazine (ascmag.com) | 摄影师亲述：滤镜/凝胶型号、灯光方案、画幅/镜头决策 | 银翼杀手2049 Vegas 橙红 = Lee 790 Moroccan Pink + 105 Orange 滤镜组、250 太空灯、Pink Joi 用 40×30ft LED 屏做交互光源 |
| 4 意图层 | 导演访谈（rogerebert.com/interviews/ 等） | 创作意图直接引语 | 奉俊昊：寄生虫是"stairway movie"、豪宅按人物动线设计、结尾"确认射杀"（확인사살） |

抓取顺序建议：Wikipedia 先行（事实骨架）→ 影评（阐释）→ 贸易刊物/导演访谈（技法细节）。三者在笔记中分别支撑"是什么/为什么有效/怎么实现"。

## 抓取要点（2026-08 验证）

- Wikipedia 直接 curl OK（~150KB/页），用 `scripts/extract_text_stdlib.py` 提取，grep 关键词段落。
- rogerebert.com 直抓 403（Cloudflare 壳 ~600B）；r.jina.ai 也被挡（403 "Just a moment"）。恢复路径：
  1. `curl -s "http://archive.org/wayback/available?url=<原URL>"` 拿最近快照直链 → `curl -L` 快照；
  2. 快照也没有（URL 本身 404）→ CDX domain+filter 找真实 slug：
     `http://web.archive.org/cdx/search/cdx?url=<域名>&matchType=domain&filter=urlkey:.*<关键字>.*&collapse=urlkey&limit=30&output=text`
     ⚠️ `matchType=prefix` 实测返回空，domain+filter 必中。
- ascmag.com 直抓 202 壳；Wayback 快照可用。文章含编辑注（[Ed. note]）等补充信息，摘录时保留原文。
- criterion.com 直抓返回 200 但 JS 重定向到无关影片（如 Elephant Boy）——提取后核对标题，货不对板直接弃用。
- 已知真实 slug：寄生虫影评 = rogerebert.com/reviews/parasite-movie-review-2019（`/parasite-2019` 是 404）；肖申克影评 = /reviews/the-shawshank-redemption-1994。

## 多片对比笔记模板

- 来源清单表格：# 编号 / 站点 / URL / 本地存档路径（标注 Wayback 抓取的快照时间戳）
- 每片一节：技法名（是什么）→ 场景与实现（怎么实现）→ 来源 [S#] 标注 + 英文原文摘录（引号保留）
- 附加节（可选）：跨片横向对比（如"空间隐喻"在寄生虫/七武士中的不同用法）
- 文末：抓取说明——403/404/跳转/失败源如实标注，绝不凭记忆补内容

## 本地存档约定

- 原始 HTML 与提取 txt 分开存：`pages/case-<电影名>.html|.txt`、影评 `ebert-<片名>.txt`、访谈 `bong-interview.txt` 等。
- 用户 film 调研共享目录 `_work/film-theory/pages/` 混有其他任务产物（theory-writing-* 等）：只认自己本次生成的前缀文件，不删不碰他人文件。
