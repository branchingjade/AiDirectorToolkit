# 斯科特深化轮来源地图（2026-08-07）

手法体系深化变体·跨作品演变矩阵（斯科特暂无《导演美学卡片》主卡片 → 自建编号变体，李安轮同型）。
产出：`技法卡片源稿/斯科特_手法体系深化.md`（198 行、35.8KB）；校验脚本 `_verify_scott_deep.py`（留存于 film-suite-research/）。

## 存档对照（S1-S8 自建编号，对应 pages/ 存档）

| 代号 | 存档 | 本文关键证据位置 |
|---|---|---|
| [S1] | scott_alien_wiki.txt（新抓） | truckers in space（受 Star Wars 启发背离洁净未来）、Nostromo 800ft tug+2 英里炼油平台、1/24 缩尺模型→模具翻铸→放大图纸→木/玻璃钢建造、58ft 起落架+斯科特让两个儿子站上去做比例尺、Camberra 轰炸机残件拼走廊、sets claustrophobia and realism、The Duellists→Alien 接手 |
| [S2] | scott_gladiator_wiki.txt（新抓） | 马耳他实建约 1/3 斗兽场高 52 feet (16 m)、其余 2/3+高度数字补足、Ouarzazate 奴隶/沙漠/角斗学校戏、现场持续改稿征求编剧制片演员意见、**「150 days of gladiatorial games」=剧情内数字非拍摄天数** |
| [S3] | scott_kingdom_wiki.txt（新抓） | Ouarzazate（角斗士/黑鹰坠落同地）、实景耶路撒冷布景（Arthur Max 设计）、Ebert 转引「实景前景+CG 背景/人马延伸」句、MPC 440 VFX shots+DNEG/Framestore、剧场版被剪 45 分钟、194min 导演剪辑版「This is the one that should have gone out」、Empire「pieces missing from a beautiful but incomplete puzzle」 |
| [S4] | scott_napoleon_wiki.txt（新抓） | shot in just 62 days、林肯大教堂/布莱尼姆宫实拍、战役序列获评 |
| [S5] | scott_thelma_wiki.txt（新抓） | buddy comedy-drama 定位、reimagines the buddy film、rescripting gender roles of the road movie、结尾 accelerate over the cliff and fly off to their deaths、Khouri 最佳原创剧本+Scott 最佳导演提名 |
| [S6] | scott_hannibal_wiki.txt（新抓） | Scott became attached while directing Gladiator (2000)（史诗间隙接手恐怖续作=题材跳跃硬证据）、praised the performances and visuals but inferior to Silence of the Lambs |
| [S7] | scott_martian_wiki.txt（新抓） | 布达佩斯巨型摄影棚 20 套布景、Wadi Rum 替身火星外景 8 天、3D 摄影机、真土豆隔壁棚种植错期匹配生长阶段、NASA involvement 专节、最佳视觉效果提名（无 VFX 分工明细——诚实声明） |
| [S8] | blade_wiki_en.txt（存量复用） | backlot 2019 LA street sets、Bradbury Building、Metropolis 剧照给模型镜头取景、Trumbull/Yuricich+Stetson 首席模型师、tech noir、Hong Kong on a very bad day、Hopper Nighthawks/Métal Hurlant/Sant'Elia、50 nights of shooting in the rain、版本史（测试放映加旁白/1992 DC/2007 Final Cut）、**库布里克《闪灵》直升机航拍素材给银翼杀手结尾**、诺兰看数百遍、主题段 foreboding and paranoia |

[卡银翼] = 银翼杀手_技法卡片.md（底本 1981-02-23 Fancher & Peoples 剧本稿）：开场眼睛世界观压缩器、V-K 审讯、tears in rain 版本注、折纸独角兽。

## 校验新坑 ㊿-斯科特轮四例

1. **write_file/patch 参数反斜杠+引号转义序列 → 字面反斜杠残留**：内容里写反斜杠+引号组合（如转义引号）会被写成字面反斜杠（文档出现双反斜杠+引号），引文校验正则把反斜杠吞进引文 → 全量 MISS；patch 的 old_string 带反斜杠必匹配失败。处置：清理脚本 `doc.replace(BS+BS+Q, Q).replace(BS+Q, Q)`（先双后单）后再 patch；写内容一律用裸引号。定位残留：扫描 `doc[i]==chr(92)`。
2. **英维渲染文本 [ n ] 引注打断句子**：`tech noir [ 178 ] subgenre`、`actors. [ 12 ] Some dialogue`——完整句引文 norm 后不匹配。处置：引文截于打断点 + 注明「存档原文 X 与 Y 间插引注 [n]，引文截于 X」，不硬拼。
3. **校验脚本英文引文提取阈值**：0.85 太严——含逗号/括号/空格的长句字母占比可低至 80%（如 118 字符长句字母 ~95 个）。0.6 合适。另排除：首字符非 ASCII（AI 提示词块、附录表行误匹配）、含竖线/星号/反引号者。
4. **vs 节说明文字裸写转引编号撞号**：vs 节导语写「其 [S2]/[S3]/[S9]」——诺兰侧编号与本文自建 S# 撞号，裸 [S2] 不触发越界误报但语义错位（比越界更隐蔽）。处置：说明文字与附录表统一写全 [卡诺兰·S#] 前缀（小津轮三坑①的撞号维度延伸）；S# 双向对账脚本的越界检查只能抓超范围号，抓不了撞号——需人工扫 vs 节裸编号。

## 预设修正（写入诚实声明）

- 「科幻黑色线」的黑色仅属《银翼杀手》单片（tech noir 出处）；《火星救援》=生存喜剧调性。线共性修正为：硬质世界构建工艺+密闭空间生存压力（飞船/Hab 皆压力容器）。线名改「科幻/黑色线」。
- 《角斗士》「150 days of gladiatorial games」=剧情内数字（康茂德设 150 天角斗赛），非拍摄天数——数字核对 pass 须区分剧情内数字与制作数据。
- 任务指定《历史史诗题材密码.md》不存在 → 回测报告《盐道_历史史诗密码回测.md》转述通道（回测基准六范本不含斯科特片，仍可借「个体被历史穿过」框架条目做对照）+ 诚实声明「密码原文未直接核验」。

## 内容要点（跨片矩阵）

- **三线**：科幻/黑色线（异形→银翼杀手→火星救援）；历史史诗线（角斗士→天国王朝→拿破仑）；类型混搭线（末路狂花→汉尼拔，硬证据=拍角斗士期间接手汉尼拔）。
- **演变链 1 世界构建五阶段**：1/24 模型翻铸（异形）→ 模型+实景街道混合（银翼杀手）→ 实建 1/3+数字 2/3（角斗士）→ 实景前景+CG 背景（天国王朝）→ 全棚景+实景外景+真道具（火星救援）。提炼句：实体永远优先、数字永远补位。
- **演变链 2 空间即压力四形态**：飞船（异形）/城市（银翼杀手）/角斗场（角斗士）/生存舱（火星救援）——提炼命名，非导演自述。
- **演变链 3 版本控制**：1982 被剪（旁白+快乐结局）→ 1992 workprint 催生导演剪辑版 → 2007 Final Cut；天国王朝被 Fox 剪 45 分钟 → 194min 导演剪辑版正名。vs 库布里克：库布里克删解释，斯科特补版本。
- **演变链 4 导演方法**：现场改稿（角斗士 script constantly changing）+ 效率（拿破仑 62 天）。
- **vs 库布里克/诺兰技术执念三系**：完美主义（库布里克 30 吨离心机/70-80 条）/实拍原教旨（诺兰 360° 走廊/VFX 镜头数）/世界构建（斯科特 1/3 斗兽场/440 VFX）。两代交接真实桥段：库布里克航拍素材给银翼杀手结尾 + 诺兰自述看银翼杀手 hundreds of times——跨导演真实互动证据比风格对比更有力。

## 失败/未取证清单

- 火星救援 VFX 分工明细：英维存档无（仅提名），以布景/外景/3D 摄影/真土豆数据佐证，「数字做远景」为推断表述。
- 汉尼拔制作细节证据密度低（仅接手时机+评论定性）。
- 角斗士无拍摄天数直接数据；天国王朝导演剪辑版 194min（DVD）/189min（首批蓝光）双口径并存。
