# 《七宗罪》(Se7en) 版本对比案例 + 悬疑"仪式反派"题材密码（2026-08-06 实测）

## 抓取记录

- Script Slug：页面 `https://www.scriptslug.com/script/se7en-1995`（200；`seven-1995`/`se7en` 404）；PDF 直链 `https://assets.scriptslug.com/live/pdf/scripts/se7en-1995.pdf`（231KB → pdftotext 276,850 字符 / 8,545 行）
- IMSDb：`https://imsdb.com/scripts/Se7en.html`（scrtext 297KB 全文；`Seven.html` 为 559 字符空壳）
- **双源同稿**：均为 1992-01-27 Andrew Kevin Walker `"Seven", unproduced draft`（早期稿；页标 1-155，场号 2-220，宽容正则数出 200 个场景标题）
- 本地文本：`film-suite-research/_tmp/se7en_slug.txt`（行号 Lxxxx 均指此文件）；产出物：`film-suite-research/研习报告/七宗罪_研习报告.md`、`film-suite-research/技法卡片源稿/七宗罪_技法卡片.md`

## 版本指纹检测实例（怎么发现"这不是拍摄稿"）

- grep `"What's in the box"` → MISSING；grep `Detec-tive`（成片车里戏名台词）→ MISSING；grep "Ernest Hemingway" 只命中开头 epigraph 与 Somerset 中段引用，**无结尾独白** → 判定与成片终局不同
- 反例验证：`seven deadly sins` / `Gluttony` / `Sloth` / `Envy` / `Pride` 全命中 → 主题装置在早期稿已完整，文本层无损，是**版本**问题不是**损坏**问题

## 早期稿 vs 成片差异清单

| 项 | 1992 早期稿 | 1995 成片 |
|---|---|---|
| 终局 | 教堂对峙：Doe 吊起 Mills 布道 → Mills 割绳反扑被射杀 → Somerset 射断四肢+烛火焚之（"Wrath goes last" L8369）→ Mills 葬礼 → Doe 遗信 "PLOW THEM UNDER" → Tracy 搬走 | 自首 → 沙漠快递车 → 盒子（Tracy 的头）→ Mills 开枪（完成 wrath）→ Somerset Hemingway 独白（"I agree with the second part"） |
| 主角结局 | Mills 死（英雄牺牲） | Mills 活着但毁了（堕落） |
| 凶手结局 | Somerset 私刑处决（复仇可理解） | 死于 Mills 之手（主角亲手完成第七宗罪） |
| Somerset-Tracy | 有吻戏（第130场 L5804-5830） | 删除，只留暧昧与怀孕倾诉 |
| 贪婪受害者 | 画家 William McCracken（Somerset 旧识，L2052） | 律师 Eli Gould（陌生人） |
| Doe 出场 | 第 51-52 场红灯区"抱圣经路人"先行出场（L2310-2360） | 删去，自首才正面出场 |
| 中段空间 | 自首后**下水道追逐**（Doe 逃 → Mills 追 → 教堂） | **沙漠公路押送**（凶手把侦探带到无人区） |
| 结尾独白 | 无 | Hemingway 独白为成片新增 |

## 版本对比研习法（本案例确立的复用方法）

流传稿与成片差异大时，**差异表本身就是最高价值分析产出**：
1. 先 grep 成片终局台词定位版本（见上）
2. 列差异表（结局/人物/删改/新增/中段空间）
3. 问"为什么改"：Se7en 的改造方向是**更黑暗化**——执行者从 Somerset（复仇可理解）换成 Mills（主角堕落）、受害者从"只有 Mills"扩至"Tracy+胎儿"、落点从"以暴制暴的代价"变为"正义的完成=罪行的完成"。结论：**"主角赢了但完成了坏人的作品"永远比"英雄复仇"更黑暗**——悬疑终局可选此方案
4. 中段空间差异（下水道→沙漠）反映导演的空间叙事选择：从"侦探闯入凶手巢穴"改为"凶手把侦探带到无人区"

## 悬疑题材"仪式反派"密码（从 Se7en 提炼，可复用公式）

1. **仪式时间框架**：7 张星期标题卡（MONDAY→SUNDAY）= 七天七罪；标题卡=最低成本的结构脉搏（黑底白字单字卡，观众每见一卡就知凶手又进一步）
2. **装置杀人公式**：每罪=一件装置艺术，三要素：聚光灯（暴食案铝箔包灯泡聚焦尸体 L574）+ 说明书（52 张拍立得=一年腐败史 L4028 / 口红 "SHE WAS GIVEN A CHOICE" L5531）+ 时间（绑一年/给选择期限）。凶手从不"处理尸体"，只"布展"
3. **凶手即展品**：反派把自己写进作品——"I envy David Mills. Envy is my sin."（L8256-8260）；主角终局亲手完成反派预言（Mills 开枪=wrath），反转从"谁赢了"变成"作品完成了"
4. **布道式对白**：比喻升级（"hit them in the head with a sledgehammer" L7406-7418）+ 圣经考据（"no pillar of salt" L7433）+ 亵渎者回击（Godspell 八轨带 L7444-7445）制造喜剧阀防说教
5. **假安全反转结构**：自首（79%）制造"案件结束"假象 → 98% 盒子引爆——**反转要放在"问题已解决"之后**；余波不解释（不给尸体镜头、不给主角后续），只给一句反讽独白
6. **镜像空间**：凶手的公寓=思想外化（窗户被宗教剪报糊死 L5172 / 5000 本笔记 L5400 / 床头钉十字架 / 16mm 循环天堂地狱老片 L5240-5250）——侦探不需要台词解释"他是什么人"
7. **搭档一体两面**：老练（绝望的智慧）+新锐（愤怒的抵抗）；拳击场戏用身体写权力关系（Mills 出拳 Somerset 举靶，L811-900）；凶手把搭档读作同谋（"you policemen and I want the same things" L8108）
8. **城市=心理外化**：环境声系统（节拍器 vs 汽车警报 L146）+ 唯一鲜艳=罪恶的颜色（murky green / red neon / 口红七芒星）+ Somerset 独白三档递进（骷髅 L3702 → 杀的能力 L3906 → 愚蠢被供奉 L6428 → 对 Tracy 的私人版 L6703）
9. **与《老无所依》对比**：掷硬币（随机性恐怖）vs 七宗罪日历（可预测到可怕的恐怖）——仪式反派的两种极端；John Doe 的恐怖恰恰在可预测：名单、顺序、结局都公开

## 结构统计（占比推断，非作者声明）

- 200 场景 / 7 卡；第一案 6%（L522）；主题揭示 26%（L2181，Bosch 画册 "The seven deadly sins"）；Sloth 46%（L3900）；Doe 公寓 60-64%（L5090）；Pride 65%（L5531）；**自首 79%**（L6745）；车戏布道 86%（L7300）；下水道 91%（L7760）；教堂终幕 93-97%（L7909）；余波 98-100%（L8374）
- 三幕推断：发现+解码（0-55%）→ 巢穴+追踪（55-79%）→ 自首+终局（79-100%）

## 关键台词行号索引（se7en_slug.txt，供复抓/引用）

- L7406-7418 sledgehammer 布道 / L7433 "no pillar of salt" / L7444 Godspell 回击 / L7457 "You make me sick" / L7467 "Ignorant heathen"
- L8108-8116 "we want repentance" / L8144-8182 花园寓言（plow under） / L8241-8247 "I was chosen" / L8256-8260 "Envy is my sin"
- L4005 "Sloth... it's sloth" / L4028 拍立得 / L5531 "SHE WAS GIVEN A CHOICE" / L6258 strap-on 屠刀 / L5412 "sick, silly puppets" / L6817 "presto, here I am" / L8330-8342 Somerset 处决 / L8369 "Wrath goes last" / L8503 "PLOW THEM UNDER"
