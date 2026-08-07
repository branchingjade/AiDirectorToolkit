# 《大白鲨》单片研习轮来源地图（2026-08，斯皮尔伯格）

**零存量全新建档**（pages/ 无任何 Spielberg/Jaws 存档；`spielberg_sl_enwiki_raw.txt` 实为《辛德勒名单》条目，前缀误导，未复用）。19 存档 [研S1-研S19] 对照，106 引文 0 MISS（校验脚本 `_verify_jaws.py`，zhconv 繁→简 + 双侧删引号 + html.unescape + 空白归一）。

## 存档 ↔ 来源对照

| 编号 | 存档 | 来源 | 关键内容位置 |
|---|---|---|---|
| 研S1 | jaws_enwiki_raw.txt（170KB）+ jaws_enwiki_clean.txt（74KB） | 英维 Jaws (film) Featured article raw | lead 三要素段；Filming（机械鲨故障/4小时/开场重写/背鳍/黄桶/159天）；Music（两音/汤米·约翰逊/笑谈/心跳呼吸/撕裂破裂/高潮无音乐）；Themes（白鲸记/哥斯拉/人民公敌/水门）；Scholarly criticism（Heath/Britton/Biskind/Gabler/Jameson）；Box office（409屏/$7M/$100M/78天/租片纪录）；Legacy（AFI 35位台词/盖洛普） |
| 研S2 | jaws_zhwiki_raw.txt（99KB）+ jaws_zhwiki_clean.txt（22KB） | 中维「大白鯊 (電影)」全繁条目（英维全译） | 编剧（"你得找艘更大的船"即兴）；拍摄（"看得越少/天赐良机/自然程度"三连、开场线缆改写、159天）；音乐（全译）；主题（白鲸记遇人民公敌/水门+易卜生）；宣传（180万/70万电视广告/海报"必须到鲨鱼下方"）；Gabler 三角 |
| 研S3 | jaws_soundtrack_enwiki_raw.txt（41KB）+ jaws_soundtrack_clean.txt | 英维 Jaws (soundtrack) | "brainless... like the shark"、威廉姆斯反驳"the sophisticated approach"、"sometimes the best ideas"、Ravel 渊源、"half as successful"、dark timbre |
| 研S4 | jaws_ebert_greatmovie.txt（16 段） | Ebert Great Movies: Jaws（Wayback 20130602104254） | "more talked about than seen"、接片条件、炸弹理论、浮桶/码头戏、"galley"、印第安纳波利斯、"summer releasing season"、POV+音乐绑定 |
| 研S5 | jaws_ebert_1975.txt（6 段） | Ebert 1975-06-20 影评（Wayback 20140416070130） | "We need a bigger boat"、"scared of the water"、三主角、真鲨/机械鲨镜头 |
| 研S6 | jaws_guardian50_interview.txt（7KB） | Guardian 2025-09-12 Spielberg 50 周年访谈（live 直抓） | hubris 原句/12 英里/"career virtually over"/呕吐/$260.7M |
| 研S7-19 | jaws_review_*.txt | 豆瓣长评 rexxar API（subject 1294941，181 篇） | 见研习报告附录 |

## 选稿与标题

reviews 列表（hotest 前 90 条）关键词：编剧技巧/暑期档/花絮/反智主义/灾难片/作者性/西部片/恐惧/40周年/名场面。**音乐类关键词在 abstract 零命中**（配乐分析缺席豆瓣热评，用英维/中维音乐节补位）。「当恐惧来自水下五十米」（17610246，1 有用）低有用数高价值（开场声音分析）。

## 本轮新坑/实测

1. **中维「大白鲨」= 大白鲨物种词条（Speciesbox）**，电影条目是全繁「大白鯊 (電影)」——探测 `大白鲨|大白鲨 (电影)|大白鯊|大白鯊 (電影)` 只有裸名命中且是物种；list=search `大白鯊 電影` 才定位真实标题。物种/电影同名歧义 + 简繁双轨，探测序列要包含。
2. **rogerebert.com 经 jina 也吃 Cloudflare 壳**（5.7KB "Just a moment"）→ CDX 精确 slug 快照 2013-2014 可用；快照含侧栏其他影评段落，正文定位 = 找到开头段索引（meta description 首句或已知首段）后**按段落索引区间截取**（1975 文 paras 25-30；GM 文 paras 26-41），比关键字截断稳。
3. **Guardian live 直抓可用**（353KB HTML），正文正则 `<div[^>]*class="[^"]*article-body[^"]*"` 起、`after-article|submeta|content-footer` 止，`<p>` 提取 24 段 7KB；jina 反而被 CF 壳挡。
4. **zhconv 需 `python -m pip install zhconv`**（裸 pip 装到别的解释器）；校验繁→简用 `convert(s,'zh-cn')`。
5. **引文归属错挂自查一例**："He would continue to devote close attention to characters..." 实为 Ebert GM 文（我把它挂到 enwiki），校验 expect 文件列即捕获——沿用诺兰轮 expect_keys 思路。
6. **任务预设纠正**："Brody 海滩戏'更大的船'即兴" → 台词场景是出海后 Orca 船侧（非海滩戏），即兴有据（中维编剧节+豆瓣花絮双证）；Ebert 1975 记作 "We need a bigger boat"，AFI 通行版 "You're gonna need a bigger boat"（双版本照录）。
7. **jaws_bruce_enwiki_raw.txt = #REDIRECT**（25B）→ 无独立词条，机械鲨素材全部在 Jaws (film) 条目内。

## 未取证清单

- 逐镜声音设计（开场"无声"仅到 Tylski 音乐分析层面）；斯皮尔伯格原话多为维基转引（卫报访谈为唯一一手直抓）；百度百科/Criterion（环球片，未逐页核验）；剧本原文（无公开存档）；豆瓣音乐类长评（abstract 零命中）。
