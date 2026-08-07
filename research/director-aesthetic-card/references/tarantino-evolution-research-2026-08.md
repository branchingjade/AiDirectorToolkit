# 昆汀手法体系深化轮来源地图（2026-08）

产出：`技法卡片源稿/昆汀_手法体系深化.md`（深化专题·**无主卡片变体第三次再证**（李安/宫崎骏轮同型）：自建 [S1]-[S7]，编号=存档文件名，头部声明「若主卡片落盘按来源清单表行序映射对齐」）。三线矩阵 + 4 演变链 + 8 泛用工具箱 + vs 科恩兄弟「话痨炸弹 vs 沉默冷枪」。

## pages/ 存档对照（本轮新抓 7 档，全部英维 action=raw）

| S# | 存档 | 关键内容 |
|---|---|---|
| S1 | tarantino_main_wiki.txt（导演主条目） | Style 段=英维版跨片总括金矿：violence is so good / Because it's so much fun / FiveThirtyEight 量化（落水狗 10 死亡 421 脏话 vs 姜戈 47 死亡 262 脏话）/ blends aesthetic elements 总括 / 非线性片单+「Tarantino Effect」批评界命名 / mundane conversations 三例（Royale with Cheese / Like a Virgin / Delfonics）/ 两个电影宇宙论 / 虚构品牌清单 / 60-70s 音乐 / 「I don't write their dialogue, I get them talking to each other」 |
| S2 | tarantino_pulp_wiki.txt | Narrative structure 段：7 parts / 时间序 4,2,6,1,7,3,5 / 1 与 7 重叠双视点 / Parker「circular events」/「circular narrative」/ 金表来历 / 公文包 / Ezekiel 演讲第四 |
| S3 | tarantino_reservoir_wiki.txt | 非线性+Rashomon 对比 / plot out of chronological order / 闪回结构 / 割耳+Stuck in the Middle with You / 50s feel+70s music / Melville 片名自述 / multiple homages |
| S4 | tarantino_killbill1_wiki.txt | exploitation 配方清单 / anime+黑白段落 / Shaw Brothers+ShawScope+crashing zoom / Dargis「blood-soaked valentine」/ 分类 American nonlinear narrative films+rape and revenge |
| S5 | tarantino_basterds_wiki.txt | alternate history 定义句 / {{quote box}} 内导演原话「my spaghetti Western but with World War II iconography」/ LaPadite 审讯+Jew Hunter / 酒馆戏口音暴露 / Operation Kino / Mendelsohn「Rewrites the Holocaust」/ Rosenbaum 批评 / 剧本工作标题 |
| S6 | tarantino_hollywood_wiki.txt | fairy tale 立意 / Abraham「revisionist storytelling」/ Schindel 怀旧 / 结尾 stunt flamethrower+Tate 邀酒 / 跨片互文（烧纳粹=无耻混蛋结局）/ Red Apple 香烟跨片 |
| S7 | tarantino_django_wiki.txt | {{blockquote}} 内导演原话「a Southern」+America's horrible past / 波士顿环球标题 blows up the spaghetti western / Fellerath 配方观察 / Revisionist Western 分类 |

## 本地转引链

- [卡低俗小说]《低俗小说_技法卡片》：环形收束=同一空间「下一秒」/重复即弧光/拖延式悬念/闲谈立人/讽刺死法
- [卡科恩深化]《科恩兄弟_手法体系深化》：vs 节五维对比全部科恩侧证据（绝望于暴力 S2/暴力源自误解 S7/trashing plans S13/Ethan 论 Jerry S3/16 分钟音乐+安全网 S2/Burwell 无视画面 研严肃·S16）
- [卡犯罪密码回测]《码头的秩序_犯罪黑帮密码回测》：定位光谱三档（浪漫化↔写实化↔荒诞化）——密码原文未直接核验（李安轮同型转述通道）

## 校验配方（88 引文 0 MISS，脚本见会话记录）

- **双语料校验**：每档存档 norm 两版——「剥模板版」+「raw 版」（只剥标签/链接/压空白、不删模板）；任一命中即通过。必须双版：导演原话常包在 {{quote box}}/{{blockquote}} 模板内，剥壳版会整段删掉
- norm 要点：弯引号→直引号后**整体剥离引号字符**（含撇号）；`{{lang|xx|text}}`→text 保留后再剥壳；`while '[[' in s` 循环先 `new=re.sub(...)` 判 `new==s` 再赋值（残缺 [[ 会死循环）
- 引文提取正则按文档引号约定：「([^」]+)」+ 含 [A-Za-z]{3} 过滤（中文文档英文引文包在「」里，不是英文引号）
- 科恩转引短语对《科恩兄弟_手法体系深化》文档本体校验（跨库）
- 节引分片：… 分割后每段 ≥12 字符；**省略号后起头不得借用原文相邻词**（「a 'Quarter Pounder'」实为「a McDonald's 'Quarter Pounder'」节引，冠词 a 属 McDonald's——修正引文措辞而非放宽校验）

## 本轮新坑

1. **英维 action=raw 冒号标题坑**：未百分号编码的 `Kill_Bill:_Volume_1` 返回 147 字节 `#REDIRECT [[Kill Bill: Volume 1]]` 循环自指壳；含冒号/空格标题必须百分号编码（`Kill%20Bill%3A%20Volume%201`）直抓
2. **Wikipedia API 429 限流**：sleep 20s + curl 重试即可（urllib 直连 API 会 429，action=raw 端点更稳）
3. 引号形态不一假 MISS（'X' vs "X"）→ 整体剥离
4. {{lang}} 模板吞词 → 内容保留规则
5. `while '[[' in s` 残缺 [[ 死循环超时 → 先判同再赋值
6. 无主卡片变体第三次再证（编号=存档文件名）

## 未取证项（诚实声明已载，后续轮可闭环）

- Basterds 五章节标题结构（英维条目未列章节名，仅剧本工作标题「Once Upon a Time In Nazi-Occupied France」经 Film Stage 引用出现）
- Kill Bill Volume 2 未抓（Volume 1 存档已够）
- 「我从每部电影里偷」类名言未在存档取证到（以 blends aesthetic elements 代替）
- 昆汀论科恩兄弟一手桥缺失（vs 节纯分析框架）
- Jackie Brown / Hateful Eight 仅主条目一句，无单片存档
