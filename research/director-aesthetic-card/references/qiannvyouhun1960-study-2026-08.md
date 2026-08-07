# 李翰祥《倩女幽魂》(1960) 单片研习轮来源地图（2026-08）

**产出**：研习报告/倩女幽魂1960_研习报告.md + 技法卡片源稿/倩女幽魂1960_技法卡片.md（29 存档，116 引文 0 MISS 0 wrong-file）
**核心发现**：张彻 1960-08-26 当日影评（豆瓣转帖）＝当代一手批评金矿（气氛恐怖论"青面獠牙不如面无五官"/三处实体败笔/诗境画面化/金黑服装用色）；胡金铨任本片助导；"收帐人"设定被徐克照单全收；徐克 5 岁看本片的 Film Comment 原话英文原文在 pages/tsui_filmcomment1.txt（存量复用，转引链升级为原文核实）。

## 本轮六新坑

1. **豆瓣 subject_suggest 同名多版本系列片消歧**：裸片名"倩女幽魂"只回热门版本系列（1987/1990/1991/2011/2003），老版本被霸占——查询词加年份"倩女幽魂 1960"一次命中（subject 1305606）。与张艺谋轮"裸片名优先"互补：**裸名被系列片霸占时加"片名+年份"**；改编/翻拍多次的经典题材（倩女幽魂/聊斋系/西游系）先试年份消歧。
2. **HKMDB SHA-256 工作量证明壳**：hkmdb.com 有 JS PoW 验证页（"Quick Verification Required"，curl 与 r.jina.ai 均只回 2.5KB 壳）——解法：CDX 精确 URL 列全部快照，**按 length 字段挑大快照**（2002-2004 快照仅 2KB=错误页，2022 快照 17KB=完整职员表），`web.archive.org/web/<ts>id_/<原URL>` 直抓。港片档案类站（hkmdb/hkcinemagic）默认走 wayback。
3. **HKFA（lcsd.gov.hk）旧 URL 静默死亡**：返回"Invalid URL"导航页而非 404，看似正常抓取——**enwiki ref 的 access-date 字段＝死链快照时点线索**：access-date 附近的 CDX 快照最可能完整（2018-05-18 访问 → 20180518060125 快照秒回）。抓到后必验正文含片名关键词（本页 1.7KB 提取含 "Classic Beauty" 原文）。
4. **获奖史断言三方交叉核对**：豆瓣 110 有用长评称本片"华语片第一次在戛纳得奖（技术大奖）"，与 ①张彻同日影评"以言在康城夺标……则感不足" ②SupChina "although it didn't win" ③导演 enwiki infobox 获奖记录（戛纳高等技术奖属 1962《杨贵妃》）三方冲突——**奖项/荣誉类断言必须与导演条目 infobox 获奖记录交叉核对**，高分长评可能是错记，冲突即存疑标注并列出各方原文。
5. **维基文库《聊斋志异》结构**：各篇目无独立页，故事在卷页内（真实标题"聊齋誌異/第02卷"，非"卷02"）；`formatversion=2` 的 `query.pages` 是 **list 非 dict**（判存在用 `'missing' not in v`，勿用 `.items()`）；聂小倩在卷 2 内以 `==聶小倩==` 节存在。志怪典源轮先 `list=search` 拿卷页真实标题（search 结果会被无关判决书污染，按标题形态筛选）。
6. **当代影评人转帖＝单片当代一手批评通道**：张彻 1960-08-26 影评（豆瓣转帖，标题即"张彻影评19600826"，文末附 B 站视频对照链接）给出同日代人对本片的完整技术批评——**单片轮先搜"片名+影评人姓名+日期"**，同代人批评密度（导演多面才华/恐怖方法论/摄影音乐服装逐项分评/录音缺陷）高于后世影评；引用标注"原始发表处未注明"。

## 存档清单（pages/，前缀 lhx_*）

| 存档 | 内容 |
|---|---|
| lhx_enchanting_wiki_raw.txt | enwiki The Enchanting Shadow（stub：戛纳 1960 参赛/奥斯卡申报未提名/1987 灵感来源） |
| lhx_zhwiki_raw.txt | 中维 倩女幽魂(1960年電影)：首部参加国际影展的香港彩色电影/助导胡金铨/片名出《倩女离魂》 |
| lhx_wiki_en_raw.txt + lhx_zhwiki_main_raw.txt | 李翰祥 en/zh 主条目（北平艺专/邵氏四大导演/《三十年细说从头》） |
| lhx_loti_wiki_en_raw.txt | Betty Loh Ti（Classic Beauty/戛纳评审"China's most beautiful actress"/天蟾舞台京剧家世） |
| lhx_achs_wiki_en_raw.txt | enwiki 1987《倩女幽魂》（"also inspired by the 1960 Shaw Brothers film"） |
| lhx_supchina_wb_clean.txt | SupChina Tristan Shaw 影评（wayback 快照；didn't win/特雷门琴/蓝暗色调/郑成功） |
| lhx_zhengzhengheng.txt | 郑政恒《倩女幽魂》三十年 PDF 提取（收帐人设定/徐克程小东重看旧版） |
| lhx_review_*.txt ×16 | 豆瓣 1305606 长评：张彻 1960 影评、两版对比 110 有用、逐场笔记、玉簪白莲考据等 |
| lhx_hkfa_wb.txt | 香港电影资料馆 2017 场刊 wayback（"Classic Beauty"封号原文） |
| lhx_hkmdb_wb.txt | HKMDB 3203 wayback 快照（完整职员表：King Hu 助导/Yao Min/8-18 上映） |
| lhx_liao2_ws.txt | 维基文库 聊斋志异/第02卷 聂小倩原文（但评先断后叙法/秦人/足心小孔/罗刹鬼骨/革囊剑袋/嫁宁生子） |
| lhx_subject.json | 豆瓣 subject 1305606（7.8 分/6602 人/爱情恐怖奇幻/83 分钟） |
| tsui_filmcomment1.txt | 存量复用：Film Comment 2011 Graham Fuller 徐克访谈（"5 years old…re-create the energy" 英文原文） |

## 其他备忘

- **戛纳获奖史纠偏**：1960 版参赛未获奖；李翰祥戛纳高等技术奖属 1962《杨贵妃》。
- **双口径并录**：片长 82（中维）/83（英维·豆瓣）；上映 8-17（英维）/8-18（中维·HKMDB）；唐若青/唐若菁。
- **死链处理**：festival-cannes.com 有 captcha 未取到，参赛事实以 enwiki/中维/港资料馆三方互证。
- **诚实声明要点**：李翰祥自传《三十年细说从头》未见全文（导演自述未取证到）；未逐帧看片，画面证据均标影评转述；燕赤霞唱词两版转述用字不同按存档直录。
