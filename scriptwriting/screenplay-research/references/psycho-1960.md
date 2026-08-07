# Psycho（惊魂记, 1960）— IMSDb 抓取与研习记录

（2026-08-07 实测）

## 来源

- IMSDb `https://imsdb.com/scripts/Psycho.html`：HTTP 200，194,533 字节页面；提取 scrtext 得 **167,308 字符 / 6,556 行**
- 版本指纹：稿头 `"PSYCHO" / By / Joseph Stefano / Based on the novel by Robert Bloch / REVISED December 1, 1959` —— 斯蒂法诺修订稿（非初稿、非拍摄终稿），与成片有台词级差异
- Script Slug 无该片条目（404），未再试其他源
- 成片信息：英文维基主条目（https://en.wikipedia.org/wiki/Psycho_(1960_film)）+ Britannica（https://www.britannica.com/topic/Psycho-film-1960）
- ⚠️ 不存在独立 "Shower scene (Psycho)" 维基条目：`/wiki/Shower_scene_(Psycho)` 与 `..._–_Shower_scene` 均 404，浴室戏事实在主条目内，别浪费时间

## 格式实证

- **无场号标题制**：126 处裸 INT/EXT 标题（`INT. MARY IN SHOWER`、`EXT. THE SWAMP - (NIGHT)` 等），编号正则 0 命中、裸正则 126——阿甘正传之后又一实例，确认 60 年代稿常见该方言
- **FADE OUT 行号 ÷ 总行数 = 幕界**：L2875（43.9%）/ L4131（63.0%）/ L6545（99.8% + THE END）
  - 第一幕 0–43.9%：玛丽安之幕（偷钱→逃亡→贝茨旅馆→晚餐→浴室被杀→善后→烟囱冒烟）
  - 第二幕 43.9–63.0%：调查之幕（阿伯加斯特→楼梯被杀）
  - 第三幕 63.0–99.8%：真相之幕（莱拉→地窖→精神病医生→诺曼内心→沼泽打捞）
- **结构发现（研习价值最高）**：主角死亡 = 中点反转——第一幕 43.9% 处 FADE OUT 划幕，视角从玛丽安无缝移交凶手诺曼（善后戏全程跟诺曼），观众被拖进共谋位

## 关键场景行号图（grep 定位）

- 初见/登记：`INT. CABIN ONE - (NIGHT)` L1810–1974
- 晚餐 + 窥视孔：`INT. NORMAN'S PARLOR` L2047–2501（taxidermy 独白 L2070 附近；窥视孔 L2450+：`A tiny circle of light hits Norman's face` → `Norman peeps through` → `NORMAN'S VIEWPOINT`）
- 浴室戏：`INT. MARY IN SHOWER` L2542–2623（剧本层抽象写法：`THE SLASHING / An impression of a knife slashing, as if tearing at the very screen, ripping the film`；凶手只给一帧 `a fright-wig`）
- 善后：`INT. MARY'S CABIN - (NIGHT)` L2632–2660
- 沼泽：`EXT. THE SWAMP - (NIGHT)` L2788–2869（`as if refusing to go the rest of the way` / `the small after-bubble, like a visual burp`；踩轮胎印+水管冲车痕；高角拍血衣）
- 楼梯戏：`INT. STAIRWAY AND UPSTAIRS LANDING` L4110–4134
- 精神病医生：`INT. OFFICE OF THE CHIEF OF POLICE` L6205–6263（`Norman Bates no longer exists. He only half-existed to begin with...`）
- 地窖：`INT. THE FRUIT CELLAR` L6091–6155
- 结局：`INT. NORMAN'S DETENTION ROOM - (NIGHT)` L6478–6556（毯子当披肩 + 苍蝇独白 + 沼泽打捞 `The car is coming out of the swamp.`）

## 稿 vs 成片差异（版本指纹）

- 浴室戏后诺曼台词：稿 `Mother! Oh God, what... blood, blood... mother...!` vs 成片 "Mother! Oh God, Mother! Blood!"
- 地窖戏：稿 `Ayeeeeeeeeeeeeeeeeeeeeee Am Norma Bates!` vs 成片 "I am Norma Bates!"
- 登记名：稿 C.U. - THE NAME "SAMUELS"（成片 Marie Samuels，一致）
- 窥视孔戏：稿明写 `see Mary undressing. She is in her bra and halfslip`（成片受审查删减）

## 成片实证 vs 流传数据（诚实标注范例）

- 维基主条目实测：浴室戏 1959-12-17 至 12-23 拍摄；`The finished scene runs some three minutes`；配乐 Herrmann `33% of the effect of Psycho was due to the music`；楼梯戏俯拍机位+滑轮轨道吊车专为藏反转（`owing to the overhead camera angle necessary to hide the film's twist`）；鸟符号（Crane/Phoenix/eats like a bird）
- 流传的"**45 秒 78 个镜头**"：维基主条目与 Britannica 均**未直接出现**该数字 → 标注"流传数据，未在本轮抓取源直接核实"，不得冒充成片实证
- 任务上下文给的事实也要过一遍抓取源，抓不到就诚实标注，这是本套件纪律

## 抓取/复核细节（新陷阱）

- **IMSDb 头部反框架 JS 清理**：`if (window!= top)` / `top.location.href=location.href` / `// -->` 会随 scrtext 提取进文本文件（`<td class="scrtext">` 块起点在 JS 之后）→ 清洗：从第一个标题行（如 `"PSYCHO"`）截断；尾部 `THE END` 之后的 "Writers/Genres/User Comments" 页脚也截掉
- **多源引文分轮复核**：md 同时引用剧本 + 维基时，**按来源分轮校验**——剧本引文对剧本源、维基引文对维基文本（本次 `psycho_wikipedia.txt`），维基引文在剧本源校验中白名单跳过（`startswith` 判据）；文件名/URL 反引号（`psycho_wikipedia.txt`）加扩展名 SKIP 规则（`\.(txt|html?|py|md)$`），否则被误报 FAIL
- **舞台指示位置陷阱**：`(Stops laughing)` 在台词 `A boy's best friend is his mother.` **之后**（稿内顺序），引用时不能把括注挪到台词前——复核抓出 1 处真错误
- 校验器自身：SKIP 分支必须返回二元组（`("SKIP-x", "")`），返回裸字符串会在解包处崩；SKIP 种类要进统计的 elif 分支，否则被误计 FAIL
- 复核结果：77 条剧本引文 PASS / 0 FAIL（负例自检有效）+ 维基引文 5/5

## 产出

- 研习报告：film-suite-research/研习报告/惊魂记_研习报告.md
- 技法卡片 8 张：film-suite-research/技法卡片源稿/惊魂记_技法卡片.md
- 剧本原文：film-suite-research/剧本原文/psycho_剧本_来源.md（frontmatter 6 字段、正文无 H1、FADE IN→THE END 完整）
