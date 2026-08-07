# 大红灯笼高高挂单片轮 2026-08（张艺谋续篇；宅院空间/女性悲剧/色彩仪式创作极）

产出：`film-suite-research/研习报告/大红灯笼高高挂_研习报告.md` + `技法卡片源稿/大红灯笼高高挂_技法卡片.md`（8 卡片）。前置：《张艺谋_手法体系深化.md》在库 → 报告新增「与深化文档对照」节（色彩叙事线定位/四色基调=状态编码/对称宅院=家规→宫殿=极权/仪式尺度演变/美与压迫同框），对照节直接转引深化文档原文并标注其行号。

## 来源档 S1-S14（pages/ 存档）

| 档 | 来源 | 存档 | 要点 |
|----|------|------|------|
| S1 | zh.wikipedia 条目（繁体） | yimou_zhwiki_rtrl.txt | 剧情/获奖/主创/「淡出镜后」暗喻论/侯孝贤监制/欧洲票房 |
| S2 | en.wikipedia 条目 | yimou_wiki_Raise_the_Red_Lantern.txt + lantern_enwiki_plot.txt + lantern_enwiki_crit.txt | 音轨曲目名=结构证据（Summer/Autumn/Winter/Next Summer/Fifth Mistress/Songlian's Madness）/每日点灯机制/死人屋史 |
| S3 | en.wikipedia Zhang Yimou | yimou_wiki_Zhang_Yimou.txt | 1990s 沿革 |
| S4 | zh.wikipedia 张艺谋 | yimou_zhwiki.txt | 「光影、构图、色彩均十分讲究」 |
| S5 | Roger Ebert 1992（Wayback） | lantern_ebert_body.txt | master shot/offstage 老爷/beneath the beauty/Technicolor 之说 |
| S6-S13 | 豆瓣长评 rexxar API（5832/1973/1703/388/101/181/123/1706 有用） | lantern_review_*.json | 五女人五阶段/四色基调/唱段原文/安提戈涅 |
| S14 | Michael Koresky「Local Color」（Reverse Shot 2020-12-10，Great Beyond 专题） | lantern_reverseshot.txt | 四季结构/色彩驱动叙事/Technicolor 误传更正/侯孝贤监制 |

## 新坑四例（本轮的 grep 校验陷阱）

1. **豆瓣 rexxar JSON 不能对原始文件 grep**：文件内容是 `\uXXXX` unicode 转义。校验必须先 `json.loads` + 递归 walk 收集全部字符串值再拼接。rexxar JSON 文本含 `<div id='content'>` 等 HTML 残留，拼接前用 html.unescape。
2. **zh.wikipedia 存档是繁体 + 内嵌 wiki 链接符**：简体引文校验前必须 ①去掉 `[[X]]`/`[[X|Y]]`（人名/片名全被链接包裹，如 `[[侯孝賢]]`、`[[釜山影展]]`，不剥离必然 MISS）；②做繁转简字符映射（维护一个针对引文的 trad→simp PAIRS dict，`str.maketrans` 两串不等长会 ValueError——用 dict 逐字替换更稳）。
3. **标点宽度与两侧归一**：norm() 必须同时作用在存档侧和**查询侧**（只归一存档、查询带空格/全角标点 → 假 MISS）。归一表：弯引号→直引号、？→?、！→!、，→,、去掉「」『』、去全部空白。
4. **Ebert Wayback 正文不含星级**：old rogerebert.com URL 404，Wayback 快照正文只有日期没有「四星」标记 → 上轮报告的「四星」元数据无法取证，本轮已从来源表删除并写入诚实声明。原则：**存档正文没有的元数据不写**，宁可删标注不可留未取证声明。

## 其他可复用发现

- **Criterion 无 essay 时的兜底**：Criterion Collection 未发行/未收录的片子，用 DDG `reverseshot + "片名" + 影评人名` 找 Reverse Shot 归档文（URL 模式 `reverseshot.org/archive/entry/<id>/<slug>`）；经 Criterion Daily 推荐的文章在 criterion.com search API 的 contentPages 里也能搜到（本片即经「Did You See This?」帖确认存在）。Koresky 文同时提供学者级更正：Ebert 的 Technicolor 之说是媒体误传（实属前作《菊豆》）。
- **音轨曲目名=结构证据**：enwiki soundtrack track list（House of Death/Fifth Mistress/Songlian's Madness）直接证实结局情节，比剧情段更好引用。
- **已有初稿的轮次 = 校验-修订而非从零**：先读既有文件，再逐条 grep 全部引文；本轮修正 5 处：S13 引文多字（「其面目身影」→「面目身影，难见其形」）、S10 三段台词合并失真（改为逐字三 blockquote）、技法卡片 6 唱段归属（屋顶唱《桃花村》非《苏三起解》；闹鬼留声机只放《御碑亭》）、封灯引文 S7→S11、Ebert 四星删除。
- **繁转简校验的边界**：中维奖项年份/数字为中文数词（第四十八届=第48届），校验串用组件分拆验证（如「第四十八届威尼斯国际电影节最佳导演银狮奖」整句匹配即通过），不必逐字。
