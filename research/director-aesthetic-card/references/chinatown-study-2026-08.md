# 《唐人街》单片研习轮来源地图（2026-08，波兰斯基补代表作首轮）

**创作极**：黑色电影 / 宿命论 / 类型重构。零存量全新建档 32 项（研S1-32），128 引文 0 MISS（校验脚本 `verify_chinatown_citations.py`，见 film-suite-research/）。

## 本轮新通道

- **NFR 论文 PDF = loc.gov 一手学术通道**：`https://www.loc.gov/static/programs/national-film-preservation-board/documents/<slug>.pdf` 直接 curl（~850KB）→ `pip install pypdf` → `PdfReader` 逐页 `extract_text()`。美国片/国家电影登记表轮优先查（本片 James Verniere 论文 12KB，含「grinning skull」「Fate 定义」「从不持枪」「左眼母题链」「70 年代镜头之眼」自传引文等一手密度极高内容）。发现路径：英维 External links 段列出 PDF URL。
- **Criterion 无 essay 时的 Daily 书评代偿**：criterion.com/current/posts/<id> 的「February Books」类月度书评文章常整段评论《The Big Goodbye》式单片制作史书——340 页初稿、Sylbert「The point is the girl dies. That's his whole life.」等金句由此拿到（发现路径：站内搜索「chinatown」时 Daily 文章命中）。
- **英维条目 {{AI-generated}} 标记处置策略**：raw 头部发现该模板时——仅单源支持的论断降级为「英维转引」并显式标注；核心分析性论断须 Ebert/NFR/豆瓣多源交叉验证；硬数据（提名/票房/日期）正常引用。
- 豆瓣长评=中译剧本全本再添一例（5874564 舍人译 49,931 字，含人物表+grass-glass 谐音/克劳斯=十字架译者注）；波兰斯基回忆录中译=豆瓣长评通道（2972372）。

## 关键证据位置

- 波兰斯基结局自述：「I knew that if Chinatown was to be special... Evelyn had to die」→ 研S1 Script 节（回忆录转引）；中译 → 研S21
- 「a film about the '30s seen through the camera eye of the '70s」→ 研S30（NFR 引波兰斯基自传）
- 汤纳「my eventual conflict with Roman... ghoulishly bleak climax」→ 研S5（Ebert 引汤纳剧本序言）
- 结尾：Walsh「Forget it, Jake. It's Chinatown.」→ 研S7；中文「忘了它吧，杰克。这是在唐人街。」+吉蒂斯呢喃「管得越少越好」→ 研S9；成片升拉镜头/左眼中枪 → 研S30+研S15
- 「She's my sister and my daughter!」逐级递进 L4586-4602 → 研S7
- 首尾环形结构 → 研S10（注意原文用「吉蒂」非「吉蒂斯」）
- 左眼母题链（尾灯→弹孔→瑕疵→中枪）→ 研S30；拉片子时间码 → 研S15（割鼻 43:02/结尾 2:03:42-2:10:30）
- 水台词「Either you bring the water to L.A. or you bring L.A. to the water.」→ 研S7

## 剧本 vs 成片差异（三源对照法）

IMSDb 转录稿：中枪右眼、结尾无「as little as possible」呢喃；成片/NFR 论文/拉片子长评：左眼（带瑕疵那只）、有呢喃。差异并列标注，不强行统一。

## 校验新坑 ㊿-唐人街轮五例

1. **loader ref 正则顺序坑**：`re.sub(r"<ref[^>]*>.*?</ref>", ...)` 会先匹配自闭合 `<ref name="dvd" />`（`[^>]*` 可吞 ` /`），`.*?</ref>` 一路吞到下一个 `</ref>`，整段正文（含 Script 节引文）被误删。**必须先剥自闭合 ref 再剥配对 ref**（与 ㊶ 未闭合 `<ref` 吞正文同族，本轮为自闭合形态）。
2. **{{quote box}} 贪婪前缀吃引文坑**：`\{\{[Qq]uote[^{}]*\|(.*?)\}\}` 的贪婪 `[^{}]*` 把 `...|quote=引文本体|` 全部吃掉，group(1) 只剩 `source=...` 段，引文随模板剥除整体丢失。解法：惰性匹配 `[^{}]*?` + `seg.split("quote=",1)[1].split("|source=")[0]`；且 kept 与正文**合并后再统一清洗**（否则 kept 内残留 `<ref>`/`[[链接]]` 造成假 MISS）。
3. **PDF 断词连字符坑**：LOC 论文 PDF 提取文本带行尾断词连字符（momen-tum/be-lieve/Christian-ity/antici-pating/Mul-wray）——校验变体集加「去连字符」变体即全过（双侧都要加）。
4. **源文献原文错字留档法**：NFR 论文引台词作「You make think you know...」（make 应为 may，错字[原文如此]）——校验按错字原文建档（证明引文确实如此），正文按正确措辞引用并在诚实声明标注差异。
5. **豆瓣长评人物译名与报告用名不一致坑**：3572351 用「吉蒂」非「吉蒂斯」、5874564 用「克劳斯」非「克罗斯」、6532813 用「找得见」非「找见」——引文必须逐字用存档原文，叙述层才用统一译名（与 ⑧ 繁简映射同族：先怀疑措辞再怀疑来源）。

## 未取证清单

- Criterion 无本片 essay（站内搜索负面取证）；BFI 页面 404
- 「Roman was right.」仅英维单源转引，未回源英文访谈
- 波兰斯基回忆录/自传原书未核验（英文经英维/NFR 转引，中文经豆瓣长评转引）
- 「波兰斯基最爱《钢琴师》《唐人街》」仅豆瓣长评转述，未核验，未入正文
- 340 页 vs 180+ 页初稿双口径并存，未定论
