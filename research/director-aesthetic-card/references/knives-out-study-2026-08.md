# 利刃出鞘轮（Knives Out 2026-08-09）实测记录 — v2.0 范本研习轮（推理探案·现代本格）

## 轮次背景（新任务形态）

- 任务：v2.0 范本研习轮（14 部片 × 7 题材，为题材密码打地基），单片产出《X_研习报告.md》+《X_技法卡片.md》，写入 `_work/v2-范本研习-20260809/<片名>/`，pages/ 存原始抓取；规范见该目录 `规范.md`（来源纪律铁律：每条论断带来源编号、原文摘录必须从存档 grep 验证、未逐帧看片要声明）。
- 与导演美学卡片轮差异：**无主卡片、无深化文档**——编号直接用 [S#] + 文末来源清单表即可，不必套 [研S#]（[研S#] 用于有主卡片的单片研习轮，见 SKILL.md 单片研习纪律）；技法卡片 = 5-8 张卡，每卡带原文摘录[S#]/画面锚点/可复用时机（泛用+国风对接）。

## 新通道/配方

1. **Script Slug 剧本 PDF 直链（本轮最大发现）**：scriptslug HTML 页是 JS 壳（125KB 但 `scrtext`/`scrolling-script`/`FADE IN` 全 0 命中），但 **`https://assets.scriptslug.com/live/pdf/scripts/<slug>.pdf` 直链可用**——《利刃出鞘》slug=`knives-out-2019`，157KB PDF（125 页、13.6 万字符剧本全文）一次到手。流程：curl 落盘 → 验 `%PDF` 头 → pypdf 提取转 txt（`pypdf` 若未装先 pip install -q）。先试 HTML 页 grep 正文标记，0 命中即转 PDF 直链，别在 HTML 上耗轮次。
2. **批量抓取编排（execute_code + curl 直连优先）**：一个脚本内循环 `curl -sL -m 45 -A <浏览器UA> -o pages/<名> <url>`，size<3000 再走 r.jina.ai 兜底。本轮 IndieWire/Vulture/EW/Deadline/NPR/RogerEbert/Guardian/Slate **八源全部直连成功**（Vulture 1.6MB、Deadline 810KB、EW 269KB 大 HTML 也可直接清洗），无一需 jina——大厂新闻站（含 Vulture 这类 Vox Media）直连优先于 jina，jina 是兜底不是第一顺位。
3. **enwiki raw 全量 ref 挖掘选源**：`re.findall(r'\|\s*url\s*=\s*([^\s|}]+)', raw)` 一次列出全部 ref URL（本轮约 200 条），按一手（导演/演员访谈）> 影评 > 维基转述排序选抓 8-10 个即可覆盖全部重点。`<ref name=iw1>{{Cite web...` 这类命名 ref 的定义里直接含一手访谈 URL（本轮 iw1=IndieWire Filmmaker Toolkit 结构访谈，全轮最强一手源）。
4. **中维剧情段 = 完整剧情一手转述**：zhwiki raw「劇情」段（1.6K 字）逐事件覆盖全片（含兰森调包药瓶/弗兰勒索/伸缩刀结局），可作画面锚点的成片侧佐证；与剧本差异处（如剧本结尾玛尔塔在"门口" doorway vs 中维"站在二樓庭院"）按双口径并列 + 诚实声明。

## 新坑/校验变体

- **剧本引文"角色名行"格式坑**：剧本角色名独占一行（`LINDA\nAlan take that piece of paper`），引文写成 `LINDA: Alan...`（加冒号）必假 MISS——norm 双侧删 `:`（连同 `,` `;`）后再比。
- **台词被动作提示行打断**：`MARTA\nThat's right, Fran's dead.\nto Ransom( )\nAnd you just confessed...` 整句含 `to Ransom( )` 提示行必 MISS——按 ⑬ 分片校验（"That's right, Fran's dead" + "And you just confessed to her murder" 分别比对）。
- **引文内自己加的标点**（"DAWN. The grounds" vs 原文换行 "DAWN\nThe grounds"）：分片短语（"The grounds of a New England manor"）校验，别整句比。
- **成片道具层 vs 剧本层差异必须 grep 验证后声明**：本轮 "My House, My Rules, My Coffee" 杯子台词在剧本全文 grep 零命中（属成片道具层），不入正文证据，写进诚实声明。
- 校验统计参考：48 条整句（47 OK + 1 条非正文引用复核通过）+ 30 条分片（0 MISS）才定稿；[S1-S11] 与来源表对账一致。

## 产物结构（供同轮其他片子参照）

- 研习报告 9 节：来源编号表(含失败记录) → 一句话概括 → 结构观察 → 画面锚点清单(8-15 个, 标注"以剧本+维基+影评为据") → 对白手法 → 动作层写法 → 桥段设计(2-3 个) → 可复用时机(对接国风创作, 泛用导向, 每条带证据出处) → 诚实声明(未逐帧看片/剧本层差异/维基二手/量化数据双口径)。
- 技法卡片 7 张：每张卡 = 技法定位 + 原文摘录[S#]（英文原文+中文译） + 设计逻辑 + 画面锚点 + 可复用时机(含国风对接) + 附录来源清单表 + 诚实声明。
- 抓取失败也留档：Script Slug HTML（JS 壳）、纽约客/NYT 影评（付费墙）→ 来源表记「未取证到」。
