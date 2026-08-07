# 伯格曼手法体系深化轮来源地图（2026-08）

## 轮次概况
- 零存量全新建档：18 存档 [S1-S18]（自建编号变体，无主卡片）；复用存量 4（[卡塔]/[卡黑]=本地深化文档转引、[卡T1]=tarkovsky_wiki_main.txt、[卡T2]=tarkovsky_sculpting_fulltext.txt）；豆瓣 3 长评。
- 产出：`技法卡片源稿/伯格曼_手法体系深化.md`（三线矩阵/2 演变链/7 泛用工具箱/vs 塔可夫斯基+黑泽明两对比节）。
- 校验：169 条精选引文 + 9 条复合引文中段 = 178 项 0 MISS；S# 双向对账 0 越界；脚本留档 `pages/_verify_bergman_deep.py`。

## 存档对照表（pages/）
| 编号 | 文件 | 内容 | 关键证据 |
|---|---|---|---|
| S1 | bergman_enwiki_raw.txt | 英维主条目 | 三部曲 1964 自撰说明（**在 {{efn}} 内文**）、八岁失信仰（Kalin）、Bergman on Bergman「沉默=宗教时代终结」、Nyreröd 最看重三部、保留剧团、九岁木偶演斯特林堡、S.D.G. |
| S2 | bergman_seventh_enwiki_raw.txt | 英维第七封印 | 忏悔室独白、Faith is a torment、America「七部影片」、广播剧死神=虚空、Täby 1480s 壁画、死亡之舞剪影 |
| S3 | bergman_wild_enwiki_raw.txt | 英维野草莓 | 灵感自述+Images 证伪句、考试梦判词（Erikson）、和解梦、Gamla stan 黎明实拍 |
| S4 | bergman_winter_enwiki_raw.txt | 英维冬日之光 | Algot「God's silence worse」、室内乐三幕、无配乐、教堂光研究一个月、屋顶布景、**Nykist 误拼（[原文如此]）** |
| S5 | bergman_persona_enwiki_raw.txt | 英维假面 | chamber pieces、Images 两段原话、14 词、融合脸、9 周住院、弃完整剧本、备选片名（Sonat för två kvinnor）、蜘蛛神脚注 |
| S6 | bergman_scenes_enwiki_raw.txt | 英维婚姻场景 | 六集 282 分钟、一周一集、小室内布景、预算 1/3、自传取材 |
| S7 | bergman_fanny_enwiki_raw.txt | 英维芬妮与亚历山大 | 退休声明、happy and privileged、Canby/Ebert/Hatch（Tempest/Prospero） |
| S8 | bergman_zhwiki_raw.txt | 中维主条目 | 三部曲段、假面=两部最重要之一、斯特林堡剧场年表 |
| S9 | bergman_ebert_winterlight.txt | Ebert Great Movies | rigorous simplicity、无镜头运动、六分钟特写、面孔=长镜主体 |
| S10 | bergman_criterion_persona.txt | Criterion Elsaesser | chamber play、脸/手/镜母题、平面化空间、光的池塘、Thomson 引语、舞台改编清单 |
| S11 | bergman_criterion_winterlight_full.txt | Criterion Peter Cowie | chamber films、削剪纪律、Communion 规则、exorcism 结语 |
| S12 | bergman_criterion_fanny.txt | Criterion Björkman | 玩偶剧院开场、show the joy 日记、妻子/情妇句、1954 童年根、320/188 分钟 |
| S13 | bergman_criterion_fanny2.txt | Criterion Bildungsroman | bildungsroman 定性 |
| S14 | bergman_persona_zhwiki_raw.txt | 中维假面小条目 | 未逐字引用（登记） |
| S15 | bergman_persona_review_maojian.txt | 豆瓣 毛尖 468 有用 | 年份细节（1956 法罗岛）与档案（1965 拍摄）不符，不采用 |
| S16 | bergman_persona_review_chenmo.txt | 豆瓣 沉默的虚妄 103 有用 | 不在乎商业转述（与 S5 英文同源）、打光变化、双独白 |
| S17 | bergman_persona_review_jingzhong.txt | 豆瓣 镜中的假面 23 有用 | 承上启下定位（信仰线→婚姻题材） |
| S18 | kurosawa_ikiru_enwiki_raw.txt | 英维生之欲（本轮新抓） | 75 天期限、死亡中段结构（Oguni 改）、秋千+Gondola no Uta、托尔斯泰渊源 |

## 校验 norm 管线四坑（本轮新增，SKILL.md 主体已满 100K 限制，细节存档于此）
1. **自闭合 ref 吞正文**：enwiki raw 里 `<ref name="X"/>` 无配对 `</ref>`，`<ref[^>]*>.*?</ref>` 会从某开口 ref 一路吞到下一个 `</ref>`（假面条目 96 个 ref 直接吞掉 4.8 万字节正文）；且**可引用事实常住在 ref 内文里**（Nykvist 教堂光研究一个月就在 `<ref name="Nykvist">` 内）——正确顺序：先剥自闭合 `<ref[^>]*/>`，再只剥标记 `</?ref[^>]*>` 保留内文；纯引注 ref（内文 `{{cite ...}}` 整块）才整块删。⚠️ 杀死比尔轮记过 `<ref/>` 吞正文，但本轮的**修复配方**（先自闭合→再标记→cite 块单独删）是新产出。
2. **模板分族处理**：`{{tsl|en|X|显示}}`/`{{link-en|...}}` 先抽显示文本再剥花括号（否则 `tslen...` 残渣断子串）；`{{efn|...}}`/`{{Blockquote|...}}` **保内文**（伯格曼 1964 三部曲自撰说明整段住在 efn 里，误删=丢一手证据）；`{{sfn|...}}`/`{{rp|...}}` 纯引注整块删（残渣插在词间断子串，如 `andcriesandwhisperssfnsteene2005inthehighestregard`）。
3. **通用 HTML 标签剥壳对 OCR 全文致命**：`<[^>]+>` 或 `<[a-zA-Z/][^>]*>` 遇到无闭合的孤 `<` 会吞掉整个剩余文件（Sculpting OCR 全档仅 1 个孤 `<` 即全灭，`Bergman is a master with sound` 等 9 条全 MISS）——非 HTML 源（OCR/markdown）一律不剥标签；剥之前先 `count("<")` 判断文件形态。
4. **残留字符归一**：软连字符 U+00AD（trans­parency）、`&nbsp;`、jina markdown 下划线斜体（`_Persona_`）、管道符 `|`（模板内文残留）全进剥离清单；变音符号（ä/ö 等）**保留**，校验短语必须带变音符号（Sonat för två kvinnor）。

## 其他新坑/通道
- **并行卡片自编号与本文 [S#] 撞号**：并行《第七封印_技法卡片》自编号 [S6] 恰与本文 S6（婚姻场景存档）撞号——转引并行卡片一律写「卡片自编号 [S6]」显式消歧，防 S# 双向对账误报（小津轮转引三坑第四变体）。
- **未取证项升级时机（㊴ 延伸）**：并行卡片落盘后除补互引链外，立即回查本文诚实声明「未取证项」清单逐条闭环——「野草莓开场棺材梦」原标未取证（enwiki 无 coffin 逐字），经并行卡片桥段一（四段式梦魇开场，含棺中自己，其 [研S10/3/12] 存档）升级为已取证，正文同步改引 [卡研野草莓]。
- **Criterion essay 作者确认**：jina markdown 头无作者时抓 HTML 的 JSON-LD `"author"` 字段（Winter Light=Peter Cowie）；essay URL 定位=enwiki raw grep `criterion.com` 一次命中（Persona=posts/3116、Winter Light=612、Fanny=346/347）。
- **豆瓣**：subject_suggest 空数组变体再证（假面/野草莓/芬妮全灭）；DDG `movie.douban.com/subject` 兜底一次命中（假面=1294438，280 长评，热门首位=毛尖 468 有用）；毛尖长评的年份细节不可当事实源。
- **一手桥（vs 节最强锚点）**：塔可夫斯基 1972 十部最爱（含冬日之光/野草莓/假面）+Bergman「Tarkovsky for me is the greatest」引语都在既有 tarkovsky_wiki_main.txt；Sculpting in Time 六段伯格曼论述行号 5196（剪辑签名）/6312（Shame 演员论）/6904（声音）/7167（假面重看）/8142（呼喊与细语）/9008（处女泉雪落睫毛）——OCR 错字「aways」「(1 have seen」按 [原文如此] 处理并在诚实声明注明。

## 预设处置
- 三线全部证实：信仰线=伯格曼 1964 三部曲自撰说明原文（+本人"未预谋三部曲、后带保留接受"修正）；室内剧线=chamber play/chamber films 三处直接文献；记忆自审线=Images「That's a lie...」原话+导演日记「show the joy」。
- 「冬日之光灰色决定」→ 未取证到逐字 grey 表述，以 rigorous simplicity/unblinking/whittles down 替代（诚实声明注明，不硬凑）。
- 「野草莓棺材梦」→ 并行卡片落盘后升级已取证。
- 毛尖长评年份 1956 vs 档案 1965 → 不采用。

## 未取证清单（供后续轮复查）
- 伯格曼对黑泽明直接评价（vs 节为分析框架，非导演互评）
- 「萨拉邦德片名源自斯特林堡室内剧」（存档仅载 2003 准续集事实）
- 《呼喊与细语》《秋日奏鸣曲》单片细节（红色系统、母女对质）未逐片取证
- 《假面》中文全剧剧本（沈语冰译，豆瓣 review/5165768）存在但未逐字引用
- Nykvist 固定搭档起始年份（1953/1960 均未逐字取证，仅"creative partnership"与 Fårö 1961=Nykvist 建议）

## 备注
- 《剧情作者电影密码.md》本机不存在（find 全盘验证）——阿巴斯轮同型再证，任务指定密码文件缺失时按李安轮纪律处置。
- SKILL.md 主体已达 100,462 字符（上限 100,000），**无法再向正文追加**——后续轮次的新坑/通道一律进本类 references/ 文件或 round-log；建议背景 curator 对 SKILL.md 做一次瘦身（变体纪律节多枚超长子弹可压缩或外移）。
