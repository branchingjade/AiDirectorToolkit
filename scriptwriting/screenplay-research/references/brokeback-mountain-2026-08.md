# 《断背山》(Brokeback Mountain) 抓取与研习记录 — 2026-08-06

## 来源与版本

- 页面：https://scriptslug.com/script/brokeback-mountain-2005
- PDF 直链：https://assets.scriptslug.com/live/pdf/scripts/brokeback-mountain-2005.pdf （curl -A Mozilla 可下，1.6MB）
- 版本：2003-02-01 稿（"February 1, 2003"），Larry McMurtry & Diana Ossana 改编自 Annie Proulx 短篇；与 2005 上映版有出入（如 Lureen 电话中 Ennis 问 "He married down there?" 措辞不同），引用须注明版本
- IMSDb 版（imsdb.com/scripts/Brokeback-Mountain.html）2026-08-06 整页壳化：HTTP 200 但正文 grep 零命中——未取到，换 Script Slug 成功

## 文本层质量与提取工序（本片为 Script Slug 损坏第二例）

- `pdftotext -layout` 输出 6341 行 / 237,924 字符
- **编码陷阱**：提取文本为 cp1252/latin-1，python 必须 `io.open(path, encoding='cp1252', errors='replace')` 读（UTF-8 读报 UnicodeDecodeError）
- **损坏模式**：场景标题大量乱码（严格正则只识别 32 处，实际 160+ 场）；个别字母级乱码：times→tirr,es、LANDSCAPE→LA'NDSCAPE、JACK→JACJ: 等；**对白完整可精读**
- **结构统计策略**：场景标题统计不可靠 → 放弃精确场景数，改用「年份标记（场景标题中的 (19\d\d)）+ 主题词 grep 行号/总行数 = 结构占比」做三幕推断
- **摘录验证**：15 条关键摘录用「清理非字母数字 + lower 后子串模糊匹配」抽查 = 9 直过 + 6 定位确认，全部可溯源（精确 `in` 校验会因字母乱码误报）

## 时间骨架（年份标记 7 处 + 首尾）

1963 春招工（L95-210，Jack 19 岁）→ 1963 夏断背山 → 1963 秋下山分别（L1886）→ 1963 冬婚礼（L1991）→ 1964 Jack 回来被拒（L2005）→ 1966 农场小屋（L2215）→ **1967 重逢**（L2863）→ Earl 童年创伤闪回（L3319）→ 1970 学校礼堂（L3429）→ 1975 离婚（L3708）→ 1976 打架夜（L4347）→ 1980 篝火（L4383）→ 1983 Jack 死（39 岁，L5581）→ Twist 父母家（L5752）→ 发现衬衫（L5922）→ 结尾挂衬衫+明信片（L6302-6336）

## 关键场景定位（行号 = 2003-02-01 稿 pdftotext 版，供后续会话直接跳读）

| 场景 | 行号 | 取证要点 |
|---|---|---|
| 招工/初见 | L95-210 | "Then the two ignore one another completely" |
| 篝火夜聊 | L1178-1186 | "most I've spoke in a year"（沉默者人设台词） |
| 帐篷第一夜 | L1373-1411 | "WE PULL AWAY TO THE NIGHT LANDSCAPE... ONLY HEAR THE SOUNDS"（亲密戏听觉留白） |
| "I'm not no queer" | L1517-1538 | 双重否定=肯定；"Me neither." |
| 流血扭打 | L1837-1851 | 鼻血沾 Jack 衬衫袖——结尾衬衫血渍伏笔（31% 处埋，94% 处回收） |
| 下山分别 | L1886-1987 | "Well, see you around, I guess."/"Right." + 巷子跪雪锤墙（语言体面/身体真相） |
| 明信片 | L2888-2928 | "The hand trembles ever so slightly"；"fishing buddies" 谎言+声音渐弱 |
| 重逢 | L2945-3029 | 穿最好衬衫等待；"WE DO NOT SEE the kiss; WE ONLY SEE ALMA'S POV... JACK'S hat falls off"；"sonofabitch, sonofabitch" |
| Earl 闪回 | L3313-3348 | 沟渠尸体/轮胎撬棍/九岁男孩的脸 |
| quit you | L5241-5330 | "Count the damn few times we been together in twenty years."；"I wish I knew how to quit you."；"years of things unsaid and now unsayable" 蒸汽比喻；"nothing ended, nothing begun, nothing resolved" |
| 死讯电话 | L5561-5666 | 骨灰台词（"some pretend place where the bluebirds sing"）；"The huge sadness of the northern plains rolls down upon ENNIS" |
| Twist 父母家 | L5752-5897 | 父亲复述 Jack 梦想；第二次闪回 "the bloodied face is not EARL'S: it is JACK'S" |
| 发现衬衫 | L5922-5970 | "the pair like two skins, one inside the other, two in one"；"There is no real scent, only the memory of it" |
| 结尾 | L6302-6336 | 挂起衬衫+明信片；"Jack, I swear..."; 窗外北方荒原 |

## 产出

- 研习报告：film-suite-research/研习报告/断背山_研习报告.md
- 技法卡片 8 张：film-suite-research/技法卡片源稿/断背山_技法卡片.md
- 剧本原文：film-suite-research/剧本原文/brokeback_mountain_2005.pdf / .txt

## 本片研习定位（爱情题材密码）

克制二十年范本——对比《婚姻故事》的激烈（语言爆发）与《花样年华》的留白（从未发生），断背山是中间态：发生但不说。核心招式：爱设配额（二十年六次相聚）、亲密戏剧本层写死"不给看"（拉远/旁观者 POV/帽子落地）、一物定情（衬衫套衬衫）、环境即情感（蒸汽/山/平原）。
