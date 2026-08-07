# 《蝙蝠侠：黑暗骑士》The Dark Knight (2008) 研习记录

## 获取记录（2026-08-07）
- **渠道**：Script Slug 官方 PDF 直链**一次命中**——页面 `https://www.scriptslug.com/script/the-dark-knight-2008` → PDF `https://assets.scriptslug.com/live/pdf/scripts/the-dark-knight-2008.pdf`（400KB）。"The" 前缀片名 slug = `the-<title>-<year>`（与 shawshank 同型），IMSDb 未试即全。
- **转换**：`pdftotext -layout` → 26.0 万字符文本，141 页（formfeed 计数 = 141）
- **制作背景取证**：维基 EN 页直接 curl 可抓（`<div id="mw-content-text">` → `catlinks` 截断，去 table/ref），得 IMAX 实拍（首部主流 IMAX 片，成片 15–20% IMAX 素材）、Ledger 2008-01 去世追授奥斯卡、预算 1.85 亿/票房 10.09 亿
- **存档**：`pages/darkknight_slug.txt` + `pages/darkknight_wiki.txt`；交付三件套：`研习报告/黑暗骑士_研习报告.md`、`技法卡片源稿/黑暗骑士_技法卡片.md`（8 张）、`剧本原文/dark-knight_剧本_scriptslug.md`（YAML frontmatter + 全文）

## 版本指纹（🟢 接近成片的拍摄终稿）
- 成片结尾戈登独白完整在稿（"a silent guardian... a dark knight" + `CUT TO BLACK. CREDITS. END.`）
- Alfred 缅甸红宝石寓言在稿："Some men just want to watch the world burn"（L2920–2941）
- 审讯室 "Kill you? I don't want to kill you... You. Complete. Me." 在稿（L4309–4319）
- 无标题页日期戳；与 IMSDb 流传稿差异未比对（诚实声明已标注）

## 结构统计
- **无编号 INT/EXT 标题制**，388 场景（238 INT / 150 EXT），转场 "CUT TO:"
- 节奏律发现：暴力场面与道德问答交替泵动（劫案→要挟、营救→Alfred 寓言、决战→双船实验）——动作段之间必插伦理拷问戏
- 伦理困境升级链：审讯室暴力逼供 → 救丹特/瑞秋二选一 → 全城声呐监控 → 结尾顶罪（反派不打赢架，逼英雄自拆原则）

## 关键场景行号（darkknight_slug.txt 基准）
| 场景 | 行号 |
|---|---|
| 开场烈焰蝙蝠标志（符号先于角色） | L1–4 |
| 银行劫案小丑揭面 "...simply makes you stranger" | L241–249 |
| "Why so serious?" | L1730 |
| 香港半岛酒店 | L1750 |
| 香港跳楼（IMAX，大远景+进行时动词） | L1841–1846 |
| Alfred 缅甸寓言 + "watch the world burn" | L2920–2941 |
| 审讯室 "Kill you? I don't want to kill you... You. Complete. Me." | L4300–4330 |
| 审讯室 "You have nothing... you'll have to choose" + 报两地址 | L4408–4421 |
| 狗追车独白 "I'm a dog chasing cars... I hate plans" | L5351–5362 |
| 医院 anarchy 演讲 "Introduce a little anarchy... agent of chaos... It's fair" | L5425–5445 |
| 双船社会实验（含两船投票/争吵） | L5803–6494 |
| 囚犯 "You don't wanna die... Give it to me" + **扔引爆器出窗** | L6455–6494 |
| "madness is like gravity. All it takes is a little push" | L6615–6617 |
| 结尾顶罪 "You either die a hero..." + 戈登独白 + 砸蝙蝠灯 | L6900–7050 |

## 稿 vs 成片差异
- 铅笔魔术、医院爆炸等名场面剧本只写动作梗概，成片为视觉扩展/即兴——引用以剧本为准时标注
- **倒吊小丑**：剧本中 madness-is-like-gravity 对话发生在楼顶、小丑被交给 SWAT 带走；成片改为被倒吊悬挂在楼顶
- 成片 18-wheeler 卡车翻转名场面：剧本 grep 不到明确翻车描述，追逐段以垃圾车/装甲车写法呈现（L3837–4046）——成片视觉层断言须标【成片】

## 文本层注意
- 页脚页码（`\f 140.`）会打断跨页台词——清理 `re.sub(r'\f\s*\d+\.?\s*', ' ', ...)` 后再校验
- 角色提示符小写变体（"THE JOKER (cont'd)"）为排版伪影，非内容错误
- 摘录校验实测：md 反引号块+引号行提取 27/27 首过（唯一 FAIL 是含路径+数字混排的元数据说明行，误报）；再手工 28 条严格子串校验 28/28 全过——**两轮校验（自动提取 + 手工点名）是本片交付标准动作**

## 研习要点（交付物内已展开）
- 反派武器库 = "给你一个不可能的选择"（二选一机制把主角价值观变成武器）
- 双船桥段反套路：囚犯船先扔引爆器（"最没资格善良的人先善良"，证伪小丑"他们会互相吞噬"预言）
- 主题收束手法：牺牲写社会性死亡（被通缉/劈蝙蝠灯），主题句交给配角独白而非主角自白
