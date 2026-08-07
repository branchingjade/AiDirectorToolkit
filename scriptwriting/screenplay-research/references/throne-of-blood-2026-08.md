# 《蜘蛛巢城》Throne of Blood (1957) 抓取与研习记录（2026-08-07）

研习产出：`film-suite-research/研习报告/蜘蛛巢城_研习报告.md`、`技法卡片源稿/蜘蛛巢城_技法卡片.md`（8 张）、`剧本原文/spiderweb_剧本_来源.md`。

## 渠道结果表

| 渠道 | 结果 | 备注 |
|---|---|---|
| IMSDb `Throne-of-Blood.html` | ❌ 空壳 | **7,785 字节**（与罗生门、寄生虫同款字节数，第三次验证此指纹）；grep scrtext 零正文 |
| Script Slug `throne-of-blood-1957` | ❌ 404 | |
| The Scripts Avant `movies/Throne_of_Blood.pdf` | ❌ 404 | |
| The Successful Screenwriter `Throne-of-Blood-Continuity-Script.pdf` | ❌ 404 | |
| scripts-onscreen 聚合页 | ❌ 无直链 | 200 但只列 IMDb 链接（罗生门同款形态） |
| **Internet Archive `akira-kurosawa-throne-of-blood`** | ✅ **1978 Yagin 英译全文** | `Akira Kurosawa Throne of Blood_djvu.txt` 70,534 字节直下；另有同名 PDF 676KB |
| IA 辅助条目 | ✅ 佐证 | `90-ijels-104202645-in-nature`（2026 IJELS 论文《In Nature We Trust: Reading the Atmospherics of Throne of Blood》，djvu.txt 15KB）；`micro_IA41153108_0810`（ERIC Peter E. Kane 1987 会议论文，Western Culture in Japanese Film）；`tob-commentary`/`throneofblood-jeck`（Michael Jeck 评论音轨，音频未用） |

发现路径：WebBridge Bing 搜 `"Throne of Blood" screenplay pdf` → 结果含 Scribd/pdfcoffee（付费/JS，未抓）+ IA 条目直链 → `u=` base64 解码一次拿到全部 URL。注意：**IA 全文搜索 `q="throne of blood screenplay"` 7 条全无关，`q=title:(throne of blood)` 才命中剧本条目**——剧本条目名不含 screenplay 字样。

## 版本信息

- 标题页署名：Directed by Akira Kurosawa；Screenplay by Shinobu Hashimoto / Ryūzō Kikushima / Akira Kurosawa / Hideo Oguni；Based on Macbeth by William Shakespeare (uncredited)；`Transcription into English by Lil "Baba" Yagin (1978)`。
- **流传英译本，非东宝官方拍摄稿**；与成片有出入：①Yagin 译本**从废墟合唱直接跳军议**，成片开头的城墙守卫对白（"How still it is, how strange!" 等）不在译本内——初稿曾凭记忆补写该段，行级核验抓出后删除 ②精怪为"纺纱老妇"形象 ③无莎士比亚原文台词。
- OCR 文本层质量：对白/叙述句大体可读；场景标题与括注舞台指示噪声重（KUMOTETORES=KUMOTE FOREST、TAKE TOK!S ROOM、`|`=I、`'T`/`TP`/`J`=T、`|_ord`=Lord、`kK`=K、`dimply`=dimly）。

## 关键场景行号图（throneblood_ia_doc.txt，共 3432 行）

- L13–16 废墟开场歌队判词 / L42–71 废墟全景（芦苇、绿水、朽牌"蜘蛛巢城遗迹"、悲鸣松树）
- L88–99 军议（主公 Kuniharu Tsuzuki + 军师 Noriyasu）
- L350–446 雾中迷路 + 射箭探路 + 怪笑回应（"Cobweb Forest. Like the threads of a spider, roads run in various directions and misguide the enemy." L397–400）
- L491–635 纺纱老妇预言段（"How foolish a man is! Why be afraid to plumb your own heart?" L580；"Your son is to be Lord of Kumonosu Castle hereafter." L627）
- L1081–1200 主公进驻北馆 + 浅茅"先锋前后皆靶"（L1188）
- L1336–1386 浅茅献计（"You ply the guards with warm saké containing a drug, stab our Lord..." L1371–1372；杜鹃三问 L1381–1383）
- L1419–1500 刺杀夜（血渍房/递枪 L1435–1439/"A long interval." L1445/栽赃 L1456/尖叫"Traitors!" L1481）
- L2220–2340 庆功宴鬼魂（空座坐出 Miki L2270–2271/"You devil, Yoshiaki!" L2276/浅茅圆场"Of late, our Lord becomes like this when drinking too much saké." L2300）
- L2660–2800 二次入林（骸骨堆血红花 L2724–2727/"Be calm, human ... you won't lose the battle ... unless Kumote Forest advances towards Kumonosu Castle." L2763–2766）
- L3160–3200 浅茅失智洗手（"Her expressionless face like a Noh mask" L3170/"Cannot be removed ... horrible blood stain..." L3178–3182）
- L3218–3360 森林移动 + 箭雨（"The forest has begun to move ..." L3250/第一箭擦甲 L3319/第二箭入棉甲 L3333/"Who murdered our former Lord?" L3345/万箭齐发 L3348–3350/"bristling with arrows like a hedgehog, falls headlong from the tower." L3352/揭秘=树枝伪装骑兵 L3358–3360）
- L3380–3396 废墟收尾歌队（"The attacking force was none other than the rustling reeds in the breeze..." L3392–3396）——首尾同框框架

## 结构占比（总 3432 行，程序化推断非作者声明）

弑主 ≈42%（L1500）→ 宴会鬼魂 ≈66%（L2280）→ 二次预言 ≈80%（L2760）→ 森林移动 ≈95%（L3250）→ 箭雨坠塔 ≈98%（L3350）。三幕：应验（0–42%）/崩塌（42–80%）/兑现（80–100%），前慢后快。

## 成片层取证要点（维基 Production/Reception 段，pages/throneblood_wiki_en.txt）

- 黑泽明自述："I had decided that I wanted lots of fog for this film..."（富士山坡建城，为雾选址；USMC 工兵帮忙）
- 美术村木与四郎：黑墙+大量铠甲配雾（按古代绘卷设计）
- 特技圓谷英二：森林移动场景原本更长，黑泽明删了若干树镜头
- **箭雨真箭实拍**：熟手弓手放箭，三船敏郎挥臂指示身体方向防误伤
- Olivier 赞箭雨戏；Vivien Leigh 问山田五十鈴"疯了为何身体几乎不动"（能剧身段）
- Richie："a marvel because it is made of so little: fog, wind, trees, mist"；Harold Bloom："the most successful film version of Macbeth"；Time："a visual descent into the hell of greed and superstition"
- Criterion 影片 ID = **735**（674 是 Calcutta——ID 不可猜，用 r.jina.ai 搜 criterion.com/search 拿）

## 摘录复核纪律教训（本片最贵一课）

词序模糊校验会把**凭记忆编造的整段引用**验成 PASS（"your children will not rule after you..." 每词都在稿、整句不存在，校验全过）。修复流程：①交付"剧本原文"清洗版后逐行英文回溯源文（202 行抓 2 处造假段）②所有卡片/报告引用回 raw 行级确认 ③源文没有的段落写 [中略] 中文摘要，不补英文。核验结果：26 条剧本引用 + 12 条维基/Criterion/论文引用全过；最终 202 行英文仅 2 处"失败"均为可解释 OCR 伪影（标题页换行错位、dimply 打字错）。
