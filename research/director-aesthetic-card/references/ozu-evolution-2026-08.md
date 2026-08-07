# 小津安二郎 手法体系深化轮 来源地图（2026-08-07，第十二轮）

产出：`film-suite-research/技法卡片源稿/小津安二郎_手法体系深化.md`（278 行/38KB）
模式：深化专题变体（跨作品矩阵）——纯存量复用零新抓取（13 主卡存档 + 4 并行轮新增存档）。

## 编号体系（本轮决策）

- 主卡片正文**无 [S#] 标记**（用「（Wikipedia《X》引…）」格式），仅文末来源清单表 14 行。
- 深化文档按**清单表行序**编 S1-S13（跳过 S14=豆瓣登录壳失败行）；附录注明「编号与主卡片清单表行序一一对应」。
- 并行轮新增存档（主卡表外）用 [卡X] 前缀：**[卡D]** ozu_tokyo_baike_jina.txt（东京物语百科：103天剧本/S&S 2012 导演票选第一/早安词条转引）、**[卡E]** ozu_tokyo_zhwiki_raw.txt（东京物语中维）、**[卡F]** ozu_latespring_baike.txt（⚠️ 弃用=韩愈《晚春》唐诗）、**[卡G]** ozu_latespring_zhwiki.txt（晚春中维：1949 电影旬报十佳第一）。
- 本地转引链：[卡A] 主卡片、[卡B] 是枝裕和_手法体系深化.md、[卡C] 侯孝贤_导演美学卡片.md。

## 演变链证据位置（关键锚点）

1. **视觉系统定型**（元素→语法→系统→减法）：
   - 1928-12-01《肉体美》首次低机位 trademark：[S1]（ozu_wiki_main）
   - 1930 年代初构图/句法实验取代好莱坞调度：「escalating experiments with composition, continuity links and film syntax, which gradually supersede Hollywood-style staging and cutting in the films of the early 1930s」[S8]（Rayns 豆腐文）
   - 1930s 中期要义就位：「By the mid-1930s, when Ozu reluctantly started making talkies and wholeheartedly embraced the 'home drama' genre... most of the tenets of his unique manner of storytelling were in place」[S8]
   - 低机位稳定实践 Bordwell 追溯至 1931–1932：[S3]（Late Spring 条目 Low angle 节）
   - 无叠化：1930s 片（东京合唱/独生子）仍有 fades → 《晚春》彻底消除 + 「a form of cheating」[S3]（cheating 段）
   - 成熟风格锁死：「not only did his mature style remain consistent, especially from Late Spring (1949) on」[S10]（Andrew，注意原文 did...remain 非 remained）
   - 战后有声片才完全发展：「a style he had not fully developed until his post-war sound films」[S1]（Legacy and style 段）
   - 彩色取消跟移：「Ozu moved the camera less and less as his career progressed, and ceased using tracking shots altogether in his colour films」[S1]
   - 量化：Bordwell「not a single reframing in all of Ozu's films from 1930 on」[S3]；小津自述「I'm not a dynamic director like Akira Kurosawa」[S3]
2. **家庭题材深化**：1936 类型转向 [S8]；1941 户田家双成功 [S1]；嫁女母题定义 [S10]（Andrew will wed or remain at home）/ [S11]（Prelinger 1950s-60s 总括）；重拍链（早安←1932、浮草←1934）[S1] 年表注释；「the central characters in his films grew older as he did」[S8]
3. **静默情感**：省略法=反 melodrama [S1]；东京物语三不拍（火车/拜访敬三/富美病倒画外）[S2]；秋刀鱼之味「the bridegroom, and the wedding ceremony, are never shown」[S4]（⚠️ 别凭印象写 "The wedding is not shown"——真实措辞是前者）
4. **演员符号**：笠智众几乎全部 [S3]；原节子六次首演=晚春 1949 [S3]、最后=1961 小早川家之秋 [S1] 年表；表演纪律「You are not supposed to feel, you are supposed to do」[S3]
5. **枕镜功能三说**：Nanbu 幕布 / Richie 只体验角色所体验 / Bordwell contiguity [S3]（pillow shot 定义段）

## 预设纠正（写入诚实声明）

- 「对称构图」：全存档 grep symmetric/symmetry 无直接文献 → 替代表述「并排构图/每镜独立完美构图」（Ebert [S6]）。
- 「我拍不出像戏剧那样的东西」：未取证到 → 近似自述「I'm not a dynamic director like Akira Kurosawa」[S3]。
- 「空镜句号」：有证据基础（枕镜三说 [S3]），但「句号」是提炼比喻，正文标注。
- 「我是卖豆腐的」：沿用主卡标注（Rayns 英译转引 [S8]，日文书名佐证 [S13]）。

## 新坑（已写入 SKILL.md）

1. **百度百科中文歧义词条碰撞**：「晚春」词条=韩愈唐诗（正文「韩愈像」暴露），27KB 看似正常——抓回核对正文主语；歧义词条登记 [卡F] 标注弃用，警示并行轮。
2. **主卡片无 S# 时按清单表行序编号**。
3. **转引编号一致性三坑**：漏 [卡X·] 前缀 / 描述文字裸 [S#] / re.findall 字符串元组需 int(n)。
4. **同批并行产出未落盘**：pages/ 已见新存档但技法卡片未落盘 → [卡X] 登记存档本身 + 诚实声明注明。

## 校验记录

- 59 条英文短语 + 7 条中文短语，三重容忍 sweep（全空白剥离+引号归一+省略号分片），修正 2 处引文措辞后 0 MISS（S4 婚礼句、S10 Andrew 时态）。
- S# 一致性：正文 [S1-S13] ⊆ 附录表，0 越界；附录 S12 登记未引（沿用主卡登记，可接受）。
- 转引编号 15 处 [卡X·S#] 全部落在被引文档登记表内（B:1-17, C:1-32）。
- 「」177/177 配对；附录文件名逐一存在性核验。

## 未取证清单

- 茶泡饭之味直接证据仅 2 条（误解母题 [S8] / 1940 军审搁置 [S1]）。
- 户田家兄妹「代际冲突」无直接文献（仅 1941 双成功 [S1]）——该线证据最弱，正文标注。
- 豆瓣渠道仍为登录壳（ozu_douban_jina.txt）。
- 麦秋横向跟移葬礼经主卡转引（未重新核验原始出处）。
