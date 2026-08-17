# 声音设计师 Gary Rydstrom 研习轮记录（声音设计轴第一轮，2026-08-09）

产出：《里德斯特罗姆_制作大师卡片.md》（`_work/v2-大师卡-20260809/里德斯特罗姆/`，33.6KB，八段结构对齐 Murch 模板）。

## 声音设计师来源地图（本轴通用，非仅 Rydstrom）

1. **designingsound.org 是索引不是正文**：2011 访谈页/2009 七月专题页只有摘要+外链；「Full interview here」指向 **USO Project blogspot**（`usoproject.blogspot.com/2011/06/interview-with-gary-rydstrom.html`）——完整访谈全文在 blogspot，**直连 curl 带 UA 可抓**（jina 对该站返回 242B stub）。音频/播客型声音设计师先找这类「访谈转录博客」。
2. **行业杂志死链走 Wayback 直连**：mixonline.com 旧访谈 404 后，`http://web.archive.org/web/2011/http://mixonline.com/recording/interviews/audio_gary_rydstrom/` **带 UA 直连 curl 取回全文**（jina 无法代理 archive.org，直连即可）——Mix 2004 Tom Kenny 访谈是声音哲学宝库（variation 第一定律/沉默=零/枪声管弦乐法/声音是电影关键部分）。老牌声音设计师的 Mix/Post Magazine 访谈常已死链，Wayback 直连是主通道。
3. **播客 AI 转录=免费全文**：Tonebenders 每期发布 AI 生成转录且**分页**（`tonebenderspodcast.com/<期号>-<slug>/2/` 为第二页），方法论大段常在后页；转录可用但诚实声明须标「AI 转录，可能有转写错误」。播客主页的节目简介（description）本身也常含直接引语。
4. **NPR 广播访谈文章页内嵌完整转录**：`npr.org/<日期>/<id>/<slug>` 页面正文即全文转录（含主持人与嘉宾直接引语），jina 可抓。
5. **官方站访谈**：starwars.com《Phantom at 25》系列=卢卡斯影业人物一手访谈；skysound.com 人物页=官方履历+完整获奖表（与维基奖项表交叉核对）。
6. **Vulture 直连 curl 可抓**：jina 返回 242B stub 时带 UA 直连 1.6MB HTML 成功，python 剥标签即正文（恐龙声音揭秘文=声音构造细节金矿）。
7. **filmsound.org 文章档案**：老牌声音设计资料站（Notes on Sound Design 等），jina 可抓，含直接引语。

## 已验证引语锚（摘录，完整清单见产出卡片的来源清单）

- 「Silence can be thought of as a type of sound. It's like when somebody years ago figured out that zero was a number.」（USO + Mix 两处）
- 「There's a danger in processing sound too much. I believe the best sound effects come from the best raw recordings, and are tweaked as little as possible.」（USO）
- 「Sound is emotion. Not just music, but all sound.」（USO）
- 「take a sound and slow it down: It becomes much bigger」（Vulture；师承 Burtt Rancor=奇瓦瓦狗慢放）
- 雷龙=驴约德尔慢放成歌：「like all good sound design, it's made from a non-beautiful source, which is donkeys」（Vulture）；NPR 版「sounds like song」
- T-Rex 吼=小象高频+虎低频（NPR/Vulture）；迅猛龙=交配陆龟/马/鹅/发情公海豚（Vulture）
- 「I think of sound design as an emotional thing. And not as a technical thing... a way to generate an emotion.」（Tonebenders p2）
- 「your first law of sound is to always have variation... the essential building block, is change」（Mix 2004）
- 枪声三层配器：「the high snap of a pistol... the low boom of a cannon... the midrange of a canyon echo. You orchestrate it.」（Mix 2004）
- 「What's the movie trying to do?」先感受电影再定声音（Tonebenders p2）
- 玩具箱工作法：「I always thought of it like a toy box. I tell the editors...」（Tonebenders p2）
- 飞车赛纯音效+引擎脉搏+Surround EX 脑后声+与《命运之决斗》音乐的「negotiation」（starwars.com）
- 「I felt like a spy, watching a lot of directors.」（USO）
- 拉塞特评 Luxo Jr.：「taught him how sound can be a partner in the storytelling of a film」（designingsound/USO）

## 防误植（声音轴特有）

- **角色边界**：Rydstrom 在《幽灵的威胁》《克隆人的进攻》是 re-recording mixer（音效轨混音），音效设计主导=Ben Burtt——写「星战声音」必须按混音师角色写，不得把音效设计功劳并入。
- **招牌声音归属交叉验证**：著名「地震炸弹」（seismic charge）声音系 Burtt 概念（Wookieepedia 专条：「audio black hole」1977 年起构思）——不记到 Rydstrom 名下。声音归属用特许经营维基（Wookieepedia 等）交叉验证。
- **视频型来源**：SoundWorks Collection 等只有视频简介文字（Facebook 视频页），标「未转录，仅确认存在」；不写未经来源支持的细节（如怪物公司门声录音过程）。

## 抓取/验证新变体

- **jina 242B stub**：r.jina.ai 偶发返回 ~240 字节极短 stub（非 Cloudflare 页、无 "Just a moment" 字样）——当批多个 URL 同时 242B 即 jina 通道问题，直接换直连 curl 带 UA，绝大多数站（blogspot/vulture 等）直连通。判据：`wc -c` < 500 即换通道。
- **markdown 强调符陷阱再中**：starwars.com 存档 `_Phantom Menace_ was the first _Star Wars_ movie mixed at Skywalker Ranch`——强调标记拆断连续串，loose grep（`mixed at Skywalker Ranch`）通过。已有记录，复现确认。
- **批量验证循环**：`for q in "..."; do grep -l -i "$q" *.txt; done` 对全库扫一遍引语存在性，快且直观；失败项再单独 looser 模式复查。

## 诚实声明要点（声音轴必备项）

未听辨原声带（所有听感描述引自访谈原文并保留出处）；音频/视频访谈未听录；「某声音如何做」的细节没有文字来源时不写不猜；AI 转录标注；角色边界（设计 vs 混音）写明。
