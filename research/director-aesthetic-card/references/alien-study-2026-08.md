# 《异形》(Alien, 1979) 单片研习轮来源地图（雷德利·斯科特补代表作）

- 创作极：封闭空间恐怖 / 藏-露悬念 / 生物设计
- 产出：《异形_研习报告.md》《异形_技法卡片.md》（film-suite-research/研习报告/ 与 技法卡片源稿/）
- 20 存档 [研S1-20]，零存量全新建档（无 scott_*/alien_* 前缀存量）；单片轮独立 [研S#] 编号（站台轮先例），技法卡片与研习报告共用同一编号
- 校验：113 引文 0 MISS（pages/_verify_alien.py）

## 渠道实测（关键位置）

- **enwiki Alien (film) raw 173KB 全量**：Design/Creature effects/The alien/Sets/Cinematic analysis 全节齐备。斯科特「The most important thing in a film of this type is not what you see, but the effect of what you think you saw」+「Every movement is going to be very slow...」在 The alien 节；「Gothic castle or World War II submarine」在 Sets 节；「fourth act」咬头结局在 Filming 节；罗林斯慢节奏论在 Post-production 节；破胸细节/培根画/Crohn 病在 Creature effects 节。
- **zhwiki 「異形 (電影)」19KB**：简体「异形 (电影)」MISSING→繁体一次命中（探测三候选）；{{cquote}} 标语块、937 号特别指令、灵感来源节（欧班农「很多人都想知我從哪裡抄襲，真相是我從所有地方抄襲」、Nostromo=康拉德小说）。
- **Ebert**：CDX `rogerebert.com/reviews/alien-1979*` 空、`great-movie-alien-1979` 20130413123201 快照 14.8KB 一次到手（Great Movies 2003 文，16 段）；Ebert 1979 原评无 CDX 条目→经 enwiki Critical reception 节转引（「one of the scariest old-fashioned space operas」）。**豆瓣 review/5708848 = Ebert 2003 文全中译**（译 Elegie挽歌）——外文影评中译全本=豆瓣长评通道再例，选稿关键词表可补「伊伯特/Ebert/评《》」类标题。
- **Guardian**：enwiki ref 挖 URL 直抓三篇——2009-10-13 making-of-alien-chestburster（Empire 转刊口述史 22 段：斯科特「If an actor is just acting terrified, you can't get the genuine look of raw, animal fear」、韦弗「when you're surprised, that's gold」、欧班农「This jet of blood, about 3ft long, caught her smack in the kisser」）、Bradshaw 2019 重评（「we never have a clear notion of what the alien actually looks like until the very last shots」）、Dr Alien PhD 2019（「only ever seen in glimpses」「a straightforward riveting thriller」）；另 2025-08-28 斯科特访谈（自己当自己批评家/故事板工作法/8-11 机）。enwiki ref 的 2003 features URL 已 404，留档。
- **IMSDb 早期稿直抓**：`imsdb.com/scripts/Alien.html` 217KB，scrtext 1 块 128KB。**`<title>"Alien", early draft, by Dan O'Bannon` = IMSDb 草稿形态首例**——先 grep 'scrtext' 确认有正文后必看 `<title>` 判定草稿/拍摄稿，草稿差异结论只能标「早期稿」。本稿价值：中性角色表原文「The crew is unisex and all parts are interchangeable for men or women」（性别翻转剧本级铁证）、SNARK/金字塔蛋室/Roby 结局、无艾许（grep Ash 0 命中=机器人角色为制片人 Giler/Hill 后期添加的旁证）。
- **豆瓣 rexxar**：subject 1300868 一次命中（suggest 端点，老片无年份歧义）；398 篇长评；选稿 11 篇（1201 有用封闭空间论 1331668 / 549 有用女性主义 14263476 / 230 有用颜色隐喻 16286700 / 199 有用与猫无关 5667236 / Giger 设计 7833132 / 细节性暗示 14388725 / Ebert 译 5708848…）。

## 新坑三例（本轮实测）

1. **zhwiki {{cquote}} 模板剥壳吞引文假 MISS（校验实现级）**：zhwiki raw 的标语块是 `{{cquote|在太空裏，沒有任何人會聽得到你的慘叫聲。<br>...|'''標語由芭芭拉·吉布斯...'''}}`——norm 的 `\{\{[^{}]*\}\}` 模板剥除把整块 cquote 内容删掉，含目标引文的短语必假 MISS。修复：剥模板前先 `re.sub(r'\{\{[Cc]quote\|(.*?)\}\}', lambda m: 占位符, s, flags=re.S)` 保存内容（`\u0001Q%d\u0001` 占位符），剥完其余模板后还原（与 ㊿③ enwiki Cquote 同族，本条是 zhwiki raw 变体+占位符还原实现；enwiki 的 {{Cquote}} 用 `re.findall` 提取拼回文尾，zhwiki 用占位符原位还原，两法都验过）。排错顺序：假 MISS 先查 norm 是否吞了引文模板，再怀疑来源。
2. **人名跨影评变体二型：引文写入文档前先 grep 存档字形**：豆瓣 14263476 通篇「瑞普利」，成片通行译名「蕾普利」——文档按通行译名写引文→校验 MISS，返工一行。与姜文轮「马大山/马大三」同族但教训升级：**引用中文长评原文前先对该存档 grep 人名实际字形，照录原文+加注异体，别等校验再返工**（文档侧写错字形是校验 MISS 的最常见自查项）。
3. **豆瓣 rexxar 翻页 count=30 陷阱**：`reviews?start=30&count=30` 返回 `{"start":30,"count":30,"total":0,"reviews":[]}`（total 变 0）；改 `start=20&count=20` 正常。翻页恒定 count=20、start 步进 20。

## 预设处置与数据纪律

- 六项预设（藏-露/封闭空间/吉格生物设计/蕾普利反套路/断头晚餐戏/公司资本恐怖）**全部取证成立零证伪**——取证纪律双向生效再证。
- 「异形全片仅出现约 4 分钟」通行说法：全部存档（英维/中维/11 篇长评）无逐字依据（英维仅 Director's Cut 增减 4 分钟删除片段）→ 诚实声明不硬凑，改以可验证证据链（斯科特原话+罗林斯节奏论+Bradshaw 残像论+Siskel「final shape least scary」反证）支撑藏-露论述。
- 数字双口径：Ebert 2003 原文「Special Order 24 (Return alien lifeform, all other priorities rescinded)」vs 中维「937 號特別指令」——并列注明，不强行统一（成片对白未逐字取证）。
- 开场计时两说并存：1201 有用长评「前六分钟内没有一个人物出场」vs 17 有用长评「近 10 分钟没一句对白」——影迷计时，未逐帧核对，正文双注。
- Criterion 负面取证：criterion.com 站内搜索 "alien" 经 jina 仅返回无关影片（福斯/迪士尼版权片无标准收藏版），与华纳大厂片同型。
