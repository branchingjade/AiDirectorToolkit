# 冰血暴 (Fargo, 1996) — IMSDb 抓取记录 + 结构实证（2026-08-06）

## 来源与版本

- **IMSDb 主源**：`https://imsdb.com/scripts/Fargo.html` → 123,796 字节 HTML → scrtext 提取 102,877 字符 / 5,369 行（文本层干净）。本地 `pages/screenplay-fargo-imsdb.txt`
- **Script Slug 交叉验证**：`https://www.scriptslug.com/script/fargo-1996`；PDF 直链 `https://assets.scriptslug.com/live/pdf/scripts/fargo-1996.pdf?v=1729114906`（1,251,662 字节）→ pdftotext 160,886 字符。**文本层有 OCR 噪声**（`sur.rivors`/`OUt`/`brandM-7new`/`M-7`）——只作交叉验证，不作精读源
- **版本指纹**：IMSDb 稿（无日期页，署 "a screenplay by Ethan Coen and Joel Coen"）与 Script Slug November 2 稿同稿——开头真实故事文本、结尾 "Two more months"/"Hold; fade out." 双源一致，且与成片基本一致（科恩自编自导）。稿内拼写错误保留 [sic]：`occured`（L20）、`as it if were`（L4982）、`Grimsurd`（L1110）、`BISMARK`（L5189）、`Brainderd`（L2700）、`INCORPORTATED`（L1189）
- 双源交叉：IMSDb 102,877 字符 vs Slug 160,886 字符（含版式空格，不可直接比）；判据 = 首场文本一致 + 结尾 FADE OUT/Hold fade out 一致 ✓

## 格式实证（新方言：无编号大写短语标题制）

- 310 个全大写行，但 **INT/EXT 前缀仅 22 处、零编号**——严格/宽容 INT 正则都只数出 22 处，必须改用「全大写短语行」统计：`re.match(r'^[A-Z][A-Z .\'/]{2,40}$')` + 过滤角色名全大写（MARGE/JERRY/CARL/GRIMSRUD/LOU/WADE/STAN/NORM/VOICE/COP/CUSTOMER/MIKE/SHEP/CLERK/WOMAN/MAN 等）→ 剩 ~130 地点/镜头标题
- 标题即镜头指令：`THROUGH A WINDSHIELD`（L106）/`THEIR POV`（L1154）/`HIGH SHOT OF MARGE'S HOUSE`（L2646）/`CLOSE ON TELEVISION`（L1047）/`CLOSE ON CARL SHOWALTER`（L4213）；单字标题 `PLATE`（L1789）/`BLACK`（L1418）/`WHITE`（L462）
- 双 FADE OUT 假结尾结构：L4076 `FADE OUT`（Carl 雪夜远去=假结尾）→ L4078 `HOLD IN BLACK` → L4080 `HARD CUT TO: BRIGHT`（第二天，第三幕重启）；L5169 `FADE OUT:`/L5171 `FADE IN:`（Jerry 落网小节）；L5358 真结尾 `Hold; fade out.`（散文式标注，非大写行——真结尾 grep 要搜 `Hold; fade`）
- 三幕占比推断（行号 ÷ 5369）：一 L17–1430（26%，建置）/ 二 L1430–4076（50%，追查）/ 三 L4080–5369（24%，收束）——标注"占比推断，非作者声明"

## 关键场景行号索引（主题词 → 场景）

- 开场真实故事文本 L15–21；FLARE TO WHITE L22；雪中车破幕 L29；拖着的 Cutlass Ciera L32
- 酒吧交易 L100–210（"I've peed three times already" L143；"burnt umber Ciera" L155；"You want your own wife kidnapped?" L236）
- TruCoat 客户戏 L508–540（"Yah, but that TruCoat" ×5）；Wade 办公室谈佣金 L1191–1260
- 绑架 L1085–1185（咬拇指 L1098；"Unguent." L1105 / "I need ... unguent." L1113；Grimsurd [sic] L1110）
- 州警被杀后切 Marge 家：AN OIL PAINTING 伏笔 L1710–1716（蓝翅鸭 teal + 未完成灰鸭 mallard）→ 结尾三美分邮票 L5291–5294 回收
- Marge 出场 L1735–1817（"There in a jif" L1748；BRAINERD POLICE 臂章 L1794）；GUNDERSON HOUSE L1813
- 雪沟脚印推理 L1968–2000（"There's two of 'em, Lou!" L1977；"For Pete's sake" L1996）
- 名台词 "hunnert percent on your policework" L2070–2072；"DLR?" 经销商车牌推理 L2078–2079；J2L 4685 笑话 L2090–2093；白色公路 L2103–2105（"cutting a landscape of flat and perfect white"）
- Mike Yanagita 电话 L2660–2735（"how are you doon?" L2723）；TruCoat 推销变体 L2739–2746
- 车行一访 L3308–3398（"I'm carrying quite a load here" L3325；plops into the chair L3327；"Home a Paul Bunyan and Babe the Blue Ox" L3361）
- Shep 暴打 Carl L3700–3717（"Smoke a fuckin' peace pipe" L3710）；Carl 电话威胁 L3719–3771；Wade 车库独白 L3780–3790
- 雪地埋钱 L4248–4282（identical fence posts 重复句式 L4263–4269；"plants a couple of sicks" [sic] L4278）
- 车行二访 L4366–4540（"get snippy with me" L4474；"damned lot count" L4503；"Aw, what the Christ!" L4526；Scotty 手风琴相框 L4535–4537；"looks around, for some reason, at the ceiling" L4540）
- Carl 缺牙分赃爆发 L4730–4826（SHPLITTA L4779；NOTISH ISH L4790；SHOT INNA FAISH L4791；THIRTY-SHIKSH HOURZH L4794；"Are we shquare?" L4811/4816）——身体损伤写进台词发音
- 碎木机 L4920–5010（butter churn 比喻 L4981–4982 [sic]；"sprays small wet chunks" L4989；Carl 尸体 L5009–5010）
- 抓捕 L5015–5095（"Stop! Police!" L5017；Halt ×3 L5051/5058/5067；瑞典语骂街 L5071；"On your belly" L5081–5083）
- Marge 结尾独白 L5107–5137（"accomplice in the wood chipper" L5109；"For a little bit of money" L5123–5124；"There's more to life than money" L5129；"here ya are, and it's a beautiful day" L5135–5137）
- Jerry 落网 L5180–5250（"flesh quivers ... keens in short, piercing screams" L5239–5240；boxer shorts 爬窗 L5234）
- 结尾邮票 + "Two more months" L5280–5358

## 摘录复核实测（48/48 交付）

- 首轮 195 条 → 4 条失败，均为真实差异非校验器误报：①原文 `as it if were`（我写成 as it were）②原文 `Don't you dare fuckin'`（漏 dare）③④折行连字符（`straight- ruled`/`rack- and-pinion`，归一化后带空格）——用 norm.find 定位 ±120 字符上下文，按原文改
- md 级复核（`> ` 行提取）前置清洗：剥 `[sic]`、`**`、中文括号行号注释（`（L1113）`）、成对引号、em dash、` / ` 段拼接符；跳过含 http/元数据行
- 跨省略号拼接（"AN OIL PAINTING — ... We track off..."）用 ELLIPSIS 标记 token 法：双方 `\.{3,}` → ` ELLIPSIS `，按 token 拆段逐段（≥12 字符）去空格 in 校验
- 反向自检：故意改写真实台词（"I am not sure...a hundred percent"）确认校验器返回 False，防 0 FAIL 虚报
- 校验脚本：`_tmp/final_check4.py`（本次会话临时脚本，模式已写入 SKILL.md 正文）

## 产出（研习报告 + 技法卡片，存项目目录非 skill）

- `film-suite-research/研习报告/冰血暴_研习报告.md`——黑色幽默机制（荒诞日常并置/伪纪实开场/大智若"拙"/反派之蠢/口音社区感/雪地空间）+ 与老无所依对比表 + 画面锚点 12 个 + 诚实声明
- `film-suite-research/技法卡片源稿/冰血暴_技法卡片.md`——8 张卡片（白屏开场/伪纪实文本/错误比喻句/优先级错乱/重复句式空间/大智若拙审问/口音拼写/画面伏笔）
