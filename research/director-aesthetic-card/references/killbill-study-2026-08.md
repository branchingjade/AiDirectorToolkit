# 杀死比尔（Kill Bill Vol.1&2, 2003-2004）单片研习轮来源地图（2026-08）

昆汀·塔伦蒂诺补代表作轮（复仇/类型混搭/暴力美学创作极）。低俗小说已在知识库，昆汀导演本体待补。24 存档全部新抓（本片零存量），产出《杀死比尔_研习报告.md》+《杀死比尔_技法卡片.md》，引文 100/100 校验 0 MISS（pages/_verify_killbill2.py）。

## 存档对照（研S1-24，单片研习独立编号体系）

| 编号 | 存档文件 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | kb1_enwiki_raw.txt | 英维 Kill Bill: Volume 1 raw | 制作/剪辑/配乐/影响/袁和平/动画段/黑白段/名单由来/拆分辩护原话 |
| 研S2 | kb2_enwiki_raw.txt | 英维 Kill Bill: Volume 2 raw | Weinstein 拆分决策/白眉/五步穿心掌/Elle 杀 Budd/RZA+罗德里格兹 |
| 研S3 | qt_enwiki_raw.txt | 英维 Quentin Tarantino raw | 「both volumes combined regarded as a single film」 |
| 研S4 | kb_zhwiki_raw.txt | 中维 杀死比尔 raw | 剧情/演员表/制作/配乐/致敬/「暴力美学」代表作标签 |
| 研S5 | kb2_zhwiki_raw.txt | 中维 追殺比爾2：愛的大逃殺 raw | 演员表（刘家辉）/粤语国语日语 |
| 研S6 | qt_zhwiki_raw.txt | 中维 昆汀·塔伦蒂诺 raw | **暴力娱乐化定义**/暴力美学 vs 奥利弗·斯通 |
| 研S7 | ebert_kb1.txt | Roger Ebert Vol.1 影评 (2003) | 复仇引擎/动画段 NC-17 逻辑/黄衣量子物理/雪园彩色 |
| 研S8 | ebert_kb2.txt | Roger Ebert Vol.2 影评 (2004) | 续集=完成/4:3 活埋/白眉/整片大于两部 |
| 研S9 | ebert_kb_whole.txt | **Matt Zoller Seitz** WBA 影评 (2025) | 五章×2/镜像结构/动画段加长/B.B. 揭示移除 |
| 研S10 | guard_kb1_review.txt | 卫报 Peter Bradshaw Vol.1 影评 | 肾上腺素注射器 |
| 研S11 | guard_kb2_observer.txt | Observer French Vol.2 影评 | ⚠️ 与研S13 同文不同 URL（未入正文） |
| 研S12 | guard_b83eed6d.txt | Observer French Vol.1 影评 | 章节标题=布莱希特/题词/黄衣/雪园/北京片厂 |
| 研S13 | guard_fcd0251f.txt | Guardian French Vol.2 影评 | 五章仅一章在亚洲/Morricone/寻女/超人对话 Feiffer |
| 研S14 | guard_73cc5475.txt | 卫报 Steve Rose 长文 (2004) | grindhouse 定义/80 部灵感/修罗雪姬模板/动画段功能 |
| 研S15 | douban_kb1_rev_暴力弱者慎入.txt | 豆瓣长评（1141 有用） | 黑白教堂/动画段/结尾浴室顶拍 |
| 研S16 | douban_kb1_rev_失败的暴力美学.txt | 豆瓣长评（1634 有用） | 反论：只有暴力没有美学/动画段例外 |
| 研S17 | douban_kb1_rev_配乐汇总.txt | 豆瓣长评（335 有用） | 全部拼贴曲目+位置+功能（配乐记忆开关） |
| 研S18 | douban_kb1_rev_向张彻致敬.txt | 豆瓣长评（95 有用） | 报仇一定要冷静/张彻粉丝/独臂刀类型建制 |
| 研S19 | douban_kb1_rev_性与刀.txt | 豆瓣长评（78 有用） | 女杀手/暴力美学恋物批判（女性主义反面） |
| 研S20 | douban_kb1_rev_镜头语言.txt | 豆瓣长评（49 有用） | 仰拍权力关系/雪园白衣客体化 |
| 研S21 | douban_kb1_rev_爱情复仇B级片.txt | 豆瓣长评（8 有用） | 北影厂摄影棚/桃桃淘电影公众号 |
| 研S22 | douban_kb2_rev_服部半藏的刀.txt | 豆瓣长评（1121 有用） | **10 卷章节列表**（每章复仇对象）/复仇主题/张彻粉丝 |
| 研S23 | douban_kb2_rev_超人对话.txt | 豆瓣长评（201 有用） | 超人理论全文（IMDb 转录） |
| 研S24 | douban_kb2_rev_日风中国味.txt | 豆瓣长评（71 有用） | 卷一日本风/卷二中国味/白眉邵氏粗糙画质 |

本地转引：[卡低俗] 技法卡片源稿/低俗小说_技法卡片.md（章节式结构/环形收束/拖延式悬念）。

## 本轮新坑（已补进 SKILL.md ㊿ 家族，此处存详细实例）

1. **enwiki raw 自闭合 `<ref name="..."/>` 吞噬正文坑**：校验 norm 里 `re.sub(r'<ref[^>]*>.*?</ref>', '', s, flags=re.S)` 遇自闭合 ref（如 `<ref name="Otto-2004" />`）无配对 `</ref>`，`.*?</ref>` 一路匹配到下一个真 `</ref>`，中间正文（含目标引文）被整体删除 → 假 MISS。首轮 100 条引文 23 MISS，过半由此产生（如「The choreographer Yuen Woo-Ping...」整句消失）。**修复：先 `re.sub(r'<ref[^>]*/>','',s)` 剥自闭合，再剥成对 ref**。诊断签名：raw grep 命中但 norm 后找不到。
2. **rogerebert.com live 经 r.jina.ai 直抓可行**：直连 403 CF 壳；CDX 通配查询返回空/403、availability API 429 限流时，jina 是第一顺位（三篇全过，含 2025 年新评）。**新评页面内链接直接给出 Ebert 原评真实 slug**：Seitz 2025 WBA 评内链 `reviews/kill-bill-volume-1-2003` 与 `kill-bill-volume-2-2004`——免 CDX 猜 slug（Ebert 老评 slug 规律 `kill-bill-<名称>-<年份>` 的又一实例）。
3. **jina markdown 无 byline → 作者验证回抓原始 HTML 验 JSON-LD**：`grep -oE '"author":\s*\{[^}]*\}'` 取 `"@type":"Person","name":"Matt Zoller Seitz"`——2025 年 WBA 影评是 Seitz（RogerEbert.com 主编）非 Ebert；Ebert 本人 2013 年已逝，2003/2004 原评的 jina 页 Published Time 显示 2023 是站方重发时间，正文仍为 Ebert 原作（V2 中「Of the original 'Kill Bill,' I wrote:...」自引可证）。三证法（JSON-LD+datePublished+byline）在 jina 通道下降为 JSON-LD 单证即可决。
4. **中维人名异体字坑**：「昆汀·塔伦蒂诺」（汀）与「昆丁·塔伦蒂诺」（丁）是不同条目——API titles= 传错字返回 missing，action=raw 报 Wikimedia Error 壳；以 `list=search&srsearch=` 结果标题逐字复制为准。与杨德昌轮「简体反例」同族。
5. **豆瓣 rexxar 长评 author.name 可空（None）**：引用只标有用数不署名。另：subject_suggest 裸片名「杀死比尔」一次全中（1291580/1291584/10756537 WBA）。

## 预设纠正（写入诚实声明）

- **「雪地战黑白」证伪**：黑白段=青叶屋 Crazy 88 大屠杀（避 NC-17 评级，enwiki [研S1]/中维 [研S4] 双证）；雪地决战为彩色（French「an exquisitely composed sequence」[研S12]、Ebert 雪园外景描述 [研S7]）。任务预设把两段混了。
- **「青蜂侠造型」拆解**：黄衣+头盔+机车=李小龙《死亡游戏》造型 [研S1][研S7]；「青蜂侠」在片中是**配乐**（Al Hirt《Green Hornet》小号，O-Ren 车队登场 [研S17]）；大卫·卡拉定选角=致敬其本人 1970 年代《功夫》剧集 [研S12]。
- **「复仇是一场旅程」未取证到导演原话**：改用死亡名单地理旅程（德州→冲绳→东京→墨西哥）+名单结构源自《无耻混蛋》索珊娜设定平移 [研S1]+主题位移至寻女 [研S13] 替代。

## 关键证据位置备忘

- **章节制（每卷五章共十章）**：enwiki raw Plot 段**无章节标题**（grep Chapter 只中 External links 的「Chapter 3: The Origin of O-Ren」）——结构证据靠 Seitz「Each half has five chapters」[研S9] + French「only one of its five chapters is set largely in Asia」[研S13] + 豆瓣 10 卷列表 [研S22] 三源。
- **暴力娱乐化定义**（暴力美学 vs 写实暴力分界）：中维昆汀条目「其血腥畫面不著重寫實與恐懼感…將暴力娛樂化」+「而不是像奧利佛·史東…反思社會制度」[研S6]。
- **土法血浆**：enwiki Filming 段灭火器+安全套（张彻式）[研S1]+中维同段 [研S4]。
- **动画段功能**：Ebert NC-17 逻辑原话 [研S7]；Production I.G/中泽一登 [研S1]。
- **北影厂**：French「stunning set created in the Beijing Film Studios」[研S12]+豆瓣「影片的大多数亚洲场景都在北京电影制片厂摄影棚完成的」[研S21]。
- **复仇清单来源**：enwiki Writing 段索珊娜「a list of Nazis she would cross off as she killed」→转移给新娘 [研S1]。
- **超人对话出处**：French 指出逐字取自 Jules Feiffer 1965《The Great Comic Book Heroes》[研S13]；全文转录见豆瓣 [研S23]。

## 校验记录

100 引文 0 MISS（`pages/_verify_killbill2.py`，norm 含管道链接剥壳/自闭合 ref 先剥/模板/斜体/jina markdown 链接；中文引文含「」《》去壳+全角括号转半角）；补 4 条新引文（研S3/10/19）全过。双文档 [研S1-24] 编号对账：正文引用 23 号、卡片引用 15 号，零越界；孤儿号仅研S11（与研S13 同文，清单已标注）。产物：《杀死比尔_研习报告.md》（22.8KB）+《杀死比尔_技法卡片.md》（13KB，含 AI 提示词对接 8 条）。
