# 《千与千寻》(Spirited Away, 2001) 抓取记录 —— 吉卜力/无剧本动画片多源取证配方

2026-08-07 实测。产出：研习报告 + 8 张技法卡片 + 剧本原文合集（film-suite-research/研习报告、技法卡片源稿、剧本原文）。

## 渠道实测（结论先行）

| 渠道 | 结果 | 判据 |
|---|---|---|
| IMSDb `Spirited-Away.html` | 200 但**空壳**（scrtext 仅 559 字符，Writers/Genres 空白） | grep scrtext 长度，不是 HTTP 状态 |
| IMSDb `Spirited-Away,-The.html` | 200 但同样 559 字符空壳 | 双 URL 都 200 时必须都验 scrtext |
| Script Slug `spirited-away-2001` | 404 | 未收录 |
| The Scripts Avant `movies/Spirited_Away.pdf` | 200，351KB，**实为字幕/配音转录稿** | 非分场稿，见指纹 |
| Internet Archive `spirited-away-movie-script` | **日文原版全台词集**，`/download/<id>/千と千尋の神隠し_djvu.txt` 直下 79KB | OCR 文本，场次齐全 |
| screenplaydb.com | 000（两种 slug） | 已死，勿再试 |
| WebBridge localhost:10086 | `extension_connected:false` | 未连时跳过，别硬试 navigate |

## 版本指纹（字幕转录稿识别法）

Scripts Avant 稿：
- 页尾标注 `Original subtitles uncredited / Timecodes from 1:30:00 by Stavr0`
- 正文含 `<timer: missed line>` 占位符（转录者自己也没听清）
- 人名粉丝拼写：Yobaba（汤婆婆）/ Hakura（白龙）/ Nigihayami Kohakunus（赈早见琥珀主）
- **缺结尾戏**：止于出隧道（"Don't look back" 告别后直接进片尾歌），**无猪群考验一场**
- 1153 行 / 33,384 字符 / 无 FADE 标记

IA 日文稿：
- 《千と千尋の神隠し 全台詞集》，OCR 噪声大（字间插空格、错字：子肘→子豚、東われる→奪われる、湯法婆→湯婆婆、和物→動物、琉斑川→琥珀川）
- **场次齐全**：含猪群考验（「この中からおまえのお父さんとお母さんを見つけな。チャンスは一回だ」）、契约消失（「ボン!と消える契約書」）、告别（「うん、きっと。/ きっとよ。」）、出隧道
- 舞台提示以「」标注

**核心教训：一份转录稿缺场 ≠ 全片缺场——先查另一语种稿**。EN 稿可读性好但缺结尾，JP 稿 OCR 乱但完整，双稿互补即覆盖全片。

## 无剧本动画片的证据栈配方（产出研习报告时）

1. **结构观察** = 转录稿场次顺序 + 维基 EN `Plot` 段 + 维基 ZH `故事简介` + 制作资料里的**原案结局**（千与千寻：原案是千寻白龙合力击败双婆婆的决战，因片长弃用改无脸男主线——"不战斗"是设计自觉，ZH 维基「作品設定」节有完整记录）
2. **画面锚点** = 每个锚点必须带证据（转录稿台词 / 维基制作资料 / 影评转述），并标注"本代理未逐帧看片"；景别断言一律标【成片】或注明来源
3. **对白手法** = 双语对照（EN 配音稿 ≠ JP 原版：英配由 Hewitt 夫妇按口型改写，且**结尾新增日版没有的对话**——"A new home and a new school? It is a bit scary." / "I think I can handle it."）；引文按语种标注
4. **ZH 维基「作品設定」「場景」「作畫、美術」「音效」节是无剧本动画片的一手转述金矿**：世界观规则（语言=力量、名字=自由、霜月祭、父母变猪=泡沫经济成年人）、原案结局、美术基准色（赤色、木桥浓赤）、实录音效（龙鳞声=敲击云母、澡堂流水=草津温泉）
5. **影评取证** = Ebert wayback（`web.archive.org/web/2023/https://www.rogerebert.com/reviews/<slug>`）——"He permits himself silences and contemplation, providing punctuation for the exuberant action" 这类节奏观察直接引用

## JP OCR 检索法

- 检索前 `re.sub(r'\s+', '', s)` 去全部空白（OCR 在字间插空格，带空格 find 必失败）
- 用假名/汉字片段而非整句（整句会被 OCR 错字破坏）
- 引用校注：改错的字标注「已校」，诚实声明里披露错字对照表；不改稿内原貌

## 摘录复核记录

- EN 转录稿 43/43 连续子串命中（反引号 span 提取 → ` / `、`...` 拆段 → 逐段 in 校验）
- **多源引文必须按来源文件路由**：研习报告同时引了转录稿 + Ebert + 维基，Ebert 引文要对 ebert 存档文件验——拿转录稿当唯一源会误报
- JP 16 条：13 条去空白后精确命中 + 3 条为已披露 OCR 校注
- 拼接引文：跨缺失文本用 `...` 显式标注（如 `Heave! Heave! ... A bicycle? That's what I thought. Now heave!` 不许直连）

## 关键台词双语对照宝库（可直接复用）

| 场景 | EN 转录稿 | JP 原版（OCR 已校） |
|---|---|---|
| 契约 | `That's a contract. Put your name there and I'll let you work. But if you say, "I want to go home," or "No," I'll turn you into a pig.` | `契約書だよ。そこに名前を書きな。働かせてやる。その代わり嫌だとか、帰りたいとか言ったらすぐ子豚にしてやるからね。` |
| 夺名 | （见上） | `今からおまえの名前は千だ。いいかい、千だよ。分かったら返事をするんだ、千!` |
| 名字规则 | `Call yourself Sen, but keep your real name. ... When she takes your name, you'll forget the way back... I can't remember mine, either.` | `湯婆婆は相手の名を奪って支配するんだ。...名を奪われると、帰り道が分からなくなるんだよ。私はどうしても思い出せないんだ。` |
| 自报真名 | （英配此段不同） | 千尋`私の本当の名前は、千尋っていうんです。`銭婆`ちひろ。いい名だね。自分の名前を大事にね。` |
| 无脸男 | `I'm lonely. I'm lonely. You don't know where you live? I want Sen! I want Sen! Take the gold.` | — |
| 河神 | `Heave! ... A bicycle? That's what I thought. Now heave!` | — |
| 猪群考验 | （EN 稿缺此场） | 湯婆婆`この中からおまえのお父さんとお母さんを見つけな。チャンスは一回だ。ピタリと当てられたらおまえたちゃ自由だよ。` |
| 告别 | `Will we meet again? Yes, hopefully. -- Hopefully? -- Hopefully... Now go on. Don't look back.` | 千尋`またどこかで会える?`ハク`うん、きっと。`千尋`きっとよ。`ハク`きっと。さぁ行きな。振り向かないで。` |
| 白龙真名 | `That river's name was Kohaku River. Your real name is... Kohaku River. Chihiro, thank you. My real name is Nigihayami Kohakunus.` | `私の本当の名は、ニギハヤミコハクヌシだ。` |

## 产出格式注意

- 剧本原文交付文件：YAML frontmatter + 正文**不加 H1**（setext `====` 下划线标题也是 H1，要降级 H2+）
- 存档：`pages/spirited-away-savant.txt`（EN）、`pages/spirited-jp-dialogue.txt`（JP）、`pages/spirited-wiki-en.txt`、`pages/spirited-wiki-zh.txt`、`pages/spirited-ebert.txt`、`pages/spirited-wiki-sections.txt`、`pages/spirited-wiki-zh-sections.txt`
