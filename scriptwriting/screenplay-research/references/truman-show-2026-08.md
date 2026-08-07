# 《楚门的世界》(The Truman Show, 1998) 抓取与研习记录 — 2026-08-07

双版本研习范本：**IMSDb 早期稿 × Script Slug 拍摄稿**对照。元叙事/自我觉醒片结构分析法 + 校验器三处新坑实测。

## 获取

| 来源 | URL | 结果 |
|---|---|---|
| Script Slug | https://www.scriptslug.com/script/the-truman-show-1998 | 页面 125KB；PDF 直链 `https://assets.scriptslug.com/live/pdf/scripts/the-truman-show-1998.pdf`（173KB）→ pdftotext 109 页/6057 行/**166 个 INT/EXT 场标题**，文本层完好，FADE OUT 收尾。标题页 `THE TRUMAN SHOW / Written by Andrew M. Niccol / Shooting Script` = **拍摄稿** |
| IMSDb | https://imsdb.com/scripts/Truman-Show,-The.html | 页面 252KB，scrtext 块 230,895 字符/6146 行，FADE OUT 收尾。**`<title>` 标签自标 `"The Truman Show", early, by Andrew M. Niccol` = 早期稿**（零成本版本检测法：curl 回先 grep `<title>`） |

## 版本指纹（grep 实证）

| 指纹 | 拍摄稿 | 早期稿 | 成片 |
|---|---|---|---|
| 名句 "In case I don't see ya..." | `In case I don't see you--good afternoon, good evening and good night.`（L6013-6015） | 无 | **"see ya" 为金·凯瑞即兴**——两版稿全句 grep "see ya" 均零命中 |
| "You were real..." | `You were real. That's what made you you so good to watch.`（L5926-5927，**笔误 "you you"**） | 无 | 成片删笔误 |
| 船名 | 无，只写 "a sail boat"（L5469 "the same boat that circled Kirk and Truman's sail boat many years earlier"） | Santa Maria ×7 | 成片 = Santa Maria |
| Sartre 灯具坠落（成片著名场景） | grep 'Sartre'/'spotlight' 零命中 | 零命中 | 成片有——稿内无此场景，未实证来源 |
| 开场 | A FOGGED MIRROR 哈气镜（L14 起） | "INT. A WOMB. DAY." 子宫内镜头 + 出生即上电视（L31 起） | 接近拍摄稿（另加 Christof 访谈开场） |
| 结局 | 天空上的门 + 鞠躬告别 + 控制室掐信号 + 雪花（L5866-6048） | 屋顶对峙：Truman 把 Christof 推向屋顶边缘，拿信封里 Sylvia 照片；蒙太奇里节目换新婴儿 **ZOE** 接棒继续播（"ZOE - Total Record Of a Human Life"）；Truman 与 Sylvia 结婚生女走向海边 | 拍摄稿版 |
| 主题落点 | 个体胜利（"--You never had a camera in my head."） | 机器吃人（"Something was real! Something had to be real!"） | 拍摄稿版 |
| 月亮意象 | "the beam of the full moon appears to be sweeping the town like a searchlight"（月光像探照灯） | "the real moon, not the planetarium projection he has been contemplating for the last thirty-four years"（真月亮 vs 天文馆投影） | — |

**核心结论：成片名句 grep 零命中 = 先怀疑"即兴/成片新增"，再怀疑版本或文本层。** 金·凯瑞即兴台词（"see ya"）就是典型案例——不是文本损坏，是拍摄期临场。

## 元叙事/自我觉醒片结构分析法（本片实证）

- **三幕占比（行号÷总行数 6057，标注"占比推断，非作者声明"）**：父亲"死而复生"被群众演员架走 L1392（23%）→ 妻子 Mococoa 穿帮 L3650（60%）→ 船头撞墙 L5832（96%）。第一幕短、第二幕极长（60% 全是"怀疑-验证-再怀疑"循环）、第三幕 10 分钟冲刺。
- **露馅三级递进节拍器（本片最核心节奏密码）**：露馅按距主角距离递进——背景层（收音机报路线与街景吻合 L2188）→ 环境层（全场同时捂耳 L2201、空教室预录童声 L2232）→ 关系层（妻子对镜头卖 Mococoa L3660、火墙+核泄漏封路 L3500）。间距渐短、证据渐硬；每次露馅后主角有"证据收藏"动作（撕杂志眼睛 L1387、录海浪 L1140、收拼图照 L5863）——觉醒靠证据链累积而非一次性反转。
- **元叙事渗透到语法层**：闪回一律格式化为 `PLAYBACK - ... As always, the flashback appears to play on a television screen.`（L1146-1149）；控制室地点名 `INT. A DIMLY-LIT ROOM SOMEWHERE. NIGHT.`（L1056，Christof 首现 ~17%）；终场 `the screen - the movie screen - goes to static`（L6047-6048）把电影银幕与剧中屏幕合一。
- **脚本明标心理节点**：`Truman experiences his first moment of doubt.`（L3508，火墙场景）——编剧把角色心理转折直接写进动作层；`(mild interest only)`（L922）导演指示进对白格式。
- **群演"程序感"写法**：`every PEDESTRIAN, MOTORIST and SHOPKEEPER along the street suddenly winces in pain and holds their right ear at exactly the same moment.`（L2200-2202）——大全景+同步动作，一个镜头完成世界观穿帮；渡轮工人打赌（L617-623）路人即观众。
- **世界边界实体化**：撞墙（L5832）→ `The sky he has been sailing towards is nothing but a painted backdrop.`（L5835-5836）→ 触摸天空 + 大笑（L5844）→ 画在彩绘天空上的门（L5866-5867）。觉醒用身体完成，不用对白解释。

## 校验器三处新坑（40/40 摘录实测，全为假 FAIL 源）

1. **pdftotext 换页符页码行打断台词连续性**：页脚形如 `\f`+空格+`17.`，会夹在台词之间（`Marlon.` 与下一句 `MARLON` 之间，L919）。统计归一化（`\f`→`\n`）不够——**校验用源侧 clean 第一步必须 `re.sub(r'\f\s*\d+\.?\s*',' ',...)`**。
2. **[sic]/版本注解写进引用块 = 自造假 FAIL**：`...good to watch. [sic——稿内笔误]` 归一化后粘连成 `good to watch sic` 不在源中。注解一律放引用块**外**（块后正文/脚注），引用块保持纯原文。
3. **动作行在源文中的位置以 grep 实证为准，不许凭记忆排序**：`Marlon takes a practice swing.`（L929）实际在 Truman 第二句台词**之后**——凭记忆把它排到两段台词之间 → 整段永久假 FAIL。排版引文块前先 dump 源文行号段。

配套管线（本片验证有效）：源侧/候选侧走同一 clean 管道（剥 CJK→剥括号→剥非单词字符→压空白→小写）；候选侧只剥**行首**角色 cue（源侧保留角色名——源文角色名是独立行，归一后天然相邻，如 `truman who are you christof i m the creator`）；`...` 分段校验（每段 ≥12 字符，逐段 in 校验）；交付前负例自检（整词篡改必须 FAIL）。

## 交付物（film-suite-research 三地同步源）

- `研习报告/楚门的世界_研习报告.md`（16 画面锚点/4 组潜台词/3 例动作层/4 桥段 + 版本对照）
- `技法卡片源稿/楚门的世界_技法卡片.md`（8 张：哈气镜元叙事开场/收音机三层证据链/Mococoa 广告话术接管/PLAYBACK 闪回即电视/撞墙实体化/话外音神学/群演程序感/门与雪花终场 + 版本对照速查表）
- `剧本原文/truman-show_剧本_来源.md`（拍摄稿全文 206K 字符，YAML frontmatter，正文无 H1，FADE OUT 收尾）
- 存档：`pages/truman_slug.pdf`、`truman_slug_pdf.txt`（6057 行）、`truman_imsdb.txt`（6146 行）、原始 HTML ×2
