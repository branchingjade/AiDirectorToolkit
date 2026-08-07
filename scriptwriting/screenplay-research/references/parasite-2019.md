# 寄生虫 Parasite (2019) — 抓取与结构实证（2026-08-07）

## 来源
- **Script Slug FYC 颁奖季稿**：页面 https://www.scriptslug.com/script/parasite-2019 → PDF 直链 https://assets.scriptslug.com/live/pdf/scripts/parasite-2019.pdf（377KB，pdftotext -layout 得 7,862 行 / 253KB）
- IMSDb `https://imsdb.com/scripts/Parasite.html` 与 `Parasite,-The.html` 均为 **7,785 字节空壳**（软 404，与《罗生门》空壳同形态）——勿再试
- 文本层：pdftotext 输出为 **cp1252**（0xC9 = É，如 `INT. INTERNET CAFÉ`），读文件必须 `decode('cp1252', errors='replace')` 再转 UTF-8
- 场标题制式：**编号 + 单破折号** `2 INT. SEMI-BASEMENT - DAY`（158 处，编号 2–159 连续，1 号为 `TITLE SEQUENCE OVER BLACK` 非 INT/EXT）；复合变体 `4 INT/EXT. SEMI-BASEMENT - ENTRANCE - LATE AFTERNOON`

## 版本指纹（FYC 稿 vs 成片）
- 首页：`OUTSTANDING ORIGINAL SCREENPLAY / SCREENPLAY BY BONG JOON HO AND HAN JIN WON / STORY BY BONG JOON HO`；文末 `NEONratedAwards.com` 水印 → NEON 发行方颁奖季稿
- 与成片高度一致：摩斯密码信、幻想买房（场156–158）、山顶收尾（场159）同构；结尾为 `FADE TO BLACK.` + `The End`（非 FADE OUT）
- ⚠️ **流传名句 "So metaphorical"（评石头）在本稿零命中**——成片字幕/后期措辞，引用必须标注
- ⚠️ **"Don't plan at all. Have no plan." 为 KI-TEK（父亲）所说**（体育馆大通铺，L6214–6241），网上常见误记为 Ki-Woo——以稿为准；结尾 Ki-Woo 信 `Father. Today I made a plan.`（L7749）与父亲"无计划"隔空对答
- 稿内个别对白分栏断裂（plan 对白区含 (MORE) 与页码穿插），摘录跨段须标"中段略"

## 结构实证（行号÷总行数=占比，推断非作者声明；总 7,862 行）
- 地点分布：朴家豪宅 99 场（62.7%）/ 半地下 19 场（12%）/ 其他 40 场——单空间叙事实证（对照《后窗》97.3%）
- 骨架：第一幕寄居渗透 场2–33（0–30.7%）；渗透完成 Steadicam 场61（~39.6%）；**中点=地下室发现 场74–75（52.5–53.2%，柜子滑开露钢门）**；暴雨夜 场87–100（64.6–75.1%，`The gates of poverty`）；生日派对屠杀 场118–130（82.3–88.5%，烧烤签穿腹/玩具斧变真斧）；尾声 场138–159（93.3–100%）
- 主题词定位：石头 5 处（L541 6.9% → L7754 98.6%，含场155 溪水起源闪回）；气味 21 处（L2946 37.5% → L7187 91.4%）；楼梯 67 处（0.5%–99.4%）；洪水 8 处（61.8–85.5%）；Morse 3 处（94.7–98.1%）
- 关键场景行号：Jessica 歌 L1307（16.6%）；感应灯追溯反转 场88 L5113–5119；地下室发现 L4132–4200；桌底气味羞辱 L5640–5730；摩斯破译 L7449–7512

## 可偷技法（交付物：film-suite-research/研习报告/寄生虫_研习报告.md + 技法卡片源稿/寄生虫_技法卡片.md 8 张）
1. **垂直空间即阶级**：每次反转=再下一层楼（半地下→豪宅→地下室→被淹的半地下→山顶/地下室摩斯对话）
2. **气味=阶级计量器**（五感道具）：小孩嗅裤腿喜剧梗 → 桌底听"那个味道越线"羞辱 → 对尸臭捏鼻触发斧杀——同一致爆器从喜剧升到悲剧
3. **追认性反转**（道具层）：全片"感应灯"实为被绑 Kun-Sae 撞电闸的"欢迎仪式"（场88）
4. **主题句归属**：给被生活击垮的父亲，与儿子信隔空对答
5. **玩具斧变真斧**：凶器先以无害身份出场（场61 露营用品），爆发时揭真身
6. 桌底羞辱 = 潜台词物理化：把被议论者放进听得见的位置

## 校验器 v4 方法（本片 22/22 摘录直过 + 坏例自检 FAIL）
正则通配校验器的四个坑与线性替代法详见 SKILL.md「复核纪律」新增条目——核心：**双端删除角色名后线性子串匹配**（源与摘录都删角色名+可选括注+冒号再 `in` 判断），不用 `.*?` 通配（150KB+ 源上回溯爆炸超时）。校验脚本：`pages/parasite_verify.py`（film-suite-research 工作区）。
