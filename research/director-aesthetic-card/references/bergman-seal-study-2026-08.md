# 伯格曼《第七封印》单片轮来源地图（2026-08-07）

**轮次**：导演本体零存量首轮（创作极=信仰追问/死亡隐喻/室内剧光影）。产出《第七封印_研习报告.md》+《第七封印_技法卡片.md》（7 张），校验脚本 `_verify_bergman_seal.py`，**55 引文 0 MISS**。

## 存档对照（pages/，编号 [研S1-20]）

| # | 存档 | 来源 | 关键内容 |
|---|---|---|---|
| S1 | bergman_seal_enwiki_raw.txt | 英维 The Seventh Seal raw | 剧情/主题/制作/接受全节；《魔灯》死亡之舞抢拍轶事；Täby 教堂 Albertus Pictor 壁画考证；35 天/15 万美元；Aberth 现代诗论 |
| S2 | bergman_seal_zhwiki_raw.txt | 中维 第七封印 raw（裸名直接命中，无需 (电影) 后缀） | 剧情梗概全文；「我要利用这个缓期，做一件最有意义的事」 |
| S3 | bergman_seal_criterion1171.txt | Criterion Giddins《There Go the Clowns》2009 | Jof=意识棱镜/开启艺术影院时代/1955-57 末日片单/只有本片坚持怀疑 |
| S4 | bergman_seal_criterion21.txt | Criterion Cowie 1987 | Fischer「luminous, almost hallucinatory brilliance」/冷战对应/自我驱魔 |
| S5 | bergman_seal_ebert.txt | Ebert Great Movies 2000-04-16（CDX wayback 20131030id_ 快照） | 「end with an image 非 statement」/默片亲缘/告解台词 |
| S6 | bergman_seal_wikiquote_raw.txt | **enwikiquote 片条目（台词一手金矿）** | **按序全对白**：开场对弈/告解室/草莓牛奶/锯树/火刑/死亡之舞全台词 + Quotes about 段（Woody Allen NYT 1988-09-18 带源） |
| S7 | bergman_wikiquote_raw.txt | enwikiquote 导演条目 | **死神白小丑+骷髅设计亲述**（"Bengt Ekerot and I agreed that Death should have the features of a white clown. An amalgamation of a clown mask and a skull."）；沙特尔大教堂创作观；《冬之光》构思 |
| S8 | bergman_enwiki_main_raw.txt | 英维伯格曼主条目 | 沉默三部曲/信仰主题 |
| S9 | bergman_ebert_memory.txt | Ebert《Ingmar Bergman: In Memory》2007 悼文 | **人脸名言**（1975 探班亲录："the human face is the most important subject of the cinema"）/教堂观光线（Wexler 转述 Nykvist）/单烛光拍摄 |
| S10-19 | bergman_seal_review_*.txt | 豆瓣 rexxar 10 篇长评（759/368/191/109/33/17/15/13/12/4 有用） | 历史民俗考证（S10 鞭笞者=表演道具/95% 女巫）、台词逐字记录（S11 草莓牛奶对话）、「崇拜恐惧并称之为上帝」（S13）、「我想要的是知识，而不是信仰」（S14 标题直引） |
| S20 | baike（_tmp/baike_seal2.txt） | 百度百科裸词条 jina | 质量一般仅基本信息，不承载关键论断 |

**本地转引链**：[卡塔·§5] 伯格曼评塔氏题词 "Tarkovsky for me is the greatest"；[卡塔·§1.1] 钟声=信仰（Ebert 评）；[卡卢布廖夫·第2卡] 失语章/「被灌输的教条烧毁」弧线——vs 塔可夫斯基节全部经本地深化文档转引，0 新抓。

## 新渠道/新坑（本轮实测）

1. **Criterion 页面结构换代（2026 实测，影响此后所有 Criterion 轮）**：essay 页正文容器从 entry-content/post-content 改为 **`pk-c-featured-article__*` 前缀**（Pixel Point 主题：`pk-c-featured-article__body`/`__byline`/`__title`）；旧 `<p>` 提取法对 `entry-content` 返回 0 段。**通用提取法：按 byline 作者名定位**（如 find 'Gary Giddins'）→ 截到 'Comments' → 提取 `<p>`；开头导航噪音（Icon/Share/Twitter）在提取后 strip。essay URL 仍从英维 raw External links 段 grep `criterion.com/current/posts/<id>-<slug>` 一次命中（本片 1171 + 21 两篇）。
2. **enwikiquote 片条目 = 经典外语片无剧本台词全本一手通道**：此前 Wikiquote 通道只用于华语片台词取证；本轮验证其对经典欧洲艺术片同样成立且更强——**The Seventh Seal 页 = 按出场顺序的完整对白记录**（非仅名句），含 stage direction 标记，可直接作台词一手源；页尾 **"Quotes about the film" 段带完整来源标注**（Woody Allen 评语附 NYT 1988 出处），= 评论家带源引文富矿。引用标注「Wikiquote 英译转写，中文逐字未取证」。
3. **enwikiquote 导演条目 = 导演亲述段落通道**：伯格曼条目含第一人称自述长段（死神造型设计决策原话、现场接受度验收标准），比二手转述可靠；导演轮先 grep 导演条目 raw 的「设计/创作过程」类段落。
4. **Ebert 悼文/记忆文 = 已故导演一手引文通道**：rogerebert.com/interviews/<slug> 的悼文（2007《Ingmar Bergman: In Memory》）含 Ebert 生前探班亲录的导演原话（人脸名言/单烛光），以及合作者转述轶事（Wexler→Nykvist 教堂观光线）——**导演已故时这是「亲历者录音」级证据**，优先级高于一切二手影评。
5. **中文流传名言英文回源失败的处置模板**：任务预设「光线是电影最重要的表现手段」（中文圈流传）→ 英文一手多引擎（DDG/Bing/Mojeek）全灭 → **不写入正文**，改用三则可取证替代（人脸论/教堂观光线/单烛光 + Cowie 评 Fischer），并在诚实声明逐条说明。预设只是线索，回源失败即弃，与既有纪律一致。
6. **预设纠正两例**：① 任务预设「死亡之舞=布拉格教堂壁画意象」→ 一手证据（Nyreröd 访谈经英维转引）= **瑞典 Täby 教堂 Albertus Pictor 1480s 壁画**（另有 Härkeberga 教堂），布拉格零证据，按取证结果写并声明；② 任务预设「我的一生是一次徒劳的追寻」→ 意译形态，逐字英文 = "My whole life has been coming and going and talking without point or consequence. It has been nothing."（Wikiquote 告解室段）。

## 校验脚本结构坑（写 _verify_bergman_seal.py 实测）

- **中文引文必须走独立繁简分支，勿混入英文 norm 分支**：英文引文走 `norm()`（小写/弯引号/压空白），中文引文需 `t2s()` 繁→简（中维 raw 是繁体）。把中文引文放进英文 CITATIONS 列表 → 存档侧未转简 → 假 MISS（本片「我要利用这个缓期…」首轮假 MISS 根因）。解法：CN 列表单独循环，存档侧 `t2s(norm(t))`、短语侧 `t2s(cn_norm(p))`。
- **繁简映射表补字实例**：緩→缓、義→义（「緩期」「意義」假 MISS）；多字词仍用单字映射表。
- **真 MISS 实例**：文档引文「做一件最有意的事」缺「义」字（凭记忆写短语漏字）→ 校验抓住，对照中维原文「做一件最有意義的事」修正文档。校验清单短语必须从存档原文逐字复制。
- **S# 对账**：正文引用 12 个编号全在来源表登记；登记未引用的存档（Ebert 原始页等）合法保留。
- Ebert wayback 快照正文提取：CDX 短 slug 前缀通配 `rogerebert.com/reviews/great-movie-the-seventh-seal*` 一次定位（已有配方再证）；无 meta description 时 h1 后第一个讲剧情的 `<p>` 起手。

## 验证记录

- 55 条引文（英文 51 + 中文 4，含 S1-S9 全部关键台词）0 MISS；塔可夫斯基转引链 [卡塔·§5]/[卡塔·§1.1]/[卡卢布廖夫·第2卡] 目标文档 grep 全部命中。
- 研习报告 22KB / 技法卡片 18.6KB（7 张：与死神下棋/告解室反转/死亡之舞结尾/草莓牛奶圣餐/死神造型公式/中世纪壁画语汇/视点特权）。
