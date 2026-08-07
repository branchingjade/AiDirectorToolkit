# 《母亲》(Mother, 2009) 单片研习轮来源地图（第二十八轮）

奉俊昊补代表作轮，创作极=小镇犯罪/母性执念。产出：`研习报告/母亲_研习报告.md` + `技法卡片源稿/母亲_技法卡片.md`（均落盘）。校验脚本 `技法卡片源稿/_verify_mother.py`（84 条引文 0 MISS）。

## 存档对照（22 编号来源，新抓 19 + 存量回源 3）

| 编号 | 存档文件 | 内容 |
|---|---|---|
| 研S1 | bong_mother_enwiki_raw.txt | 英维 Mother (2009 film) raw 全条目（剧情/演员/上映/奖项表/RT 96%） |
| 研S2 | bong_mother_zhwiki_raw.txt | 中维「非常母親」raw（noteTA 译名表/获奖） |
| 研S3 | bong_mother_baike_jina.txt | 百度百科「母亲/5596814」69KB 全量（剧情/角色介绍/幕后花絮/变形镜头制作/影片评价） |
| 研S4 | bong_mother_reviews.json / reviews2.json | 豆瓣 reviews 列表（total 524，首页即高有用） |
| 研S5-20 | bong_mother_review_<id>.json ×16 | 豆瓣长评全文：2438716(2623)/2911050(521)/2534265(271)/2574129(243)/2599596(117)/12724280(106)/2961443(70)/4203620(69)/12959601(64)/2507744(42,木卫二)/2994054(12)/6256187(12)/16543114(2)/16717508(2)/3271890(3,王书亚转帖)/3011137(2,英文) |
| 研S21 | bong_mother_ebert.txt | Ebert 影评 wayback 快照 20140723171100（reviews/mother-2010）全文 16 段 |
| 研S22 | bong_mother_nyt_dargis.txt | NYT Manohla Dargis 影评 wayback 快照 20150423111345 全文 |
| 存量 | bong_indiewire_commentary.txt | 主卡 [卡S10]，雨自述英文原句回源 |
| 存量 | bong_mom_wiki.txt | 主卡 [卡S3]，Tizzard 深渊母题英文原句回源 |
| 存量 | bong_guardian_int2020.txt | 主卡 [卡S8]，横纵对照英文原句回源 |

## 关键证据位置

- **结尾反转链**（英维 Plot 段）：儿子石头误杀雅中→母亲扳手杀目击者+焚屋（`Fearing for her son, the mother bludgeons the collector with a wrench and sets fire to his house`）→宗八顶罪（`hears he does not have a mother to fight for him`）→结尾针灸盒回归+巴士群舞（`She begins to dance with the other parents on the bus`）
- **母性执念定性**：Dargis "a monumental, ferocious performance" / "a dreadful manifestation of a love so consuming it all but swallows the world"；Ebert "a force of nature" / "a remorseless parent defending her fledgling"
- **幽默更少更冷**：Dargis "if somewhat less generously than in 'The Host'"；RT consensus "As fleshy as it is funny... plenty of eerie visuals"
- **小镇封闭**：英维 "a small town in southern South Korea"；Ebert "In a village"；影迷 "离奇诡谲的小镇谋杀案"
- **制作层**：百度百科幕后制作=奉俊昊首次用变形镜头 2.35:1；为金惠子量身定做（NG18 次/时隔十年）；人物名「道俊」改自元斌真名「道振」

## 本轮新坑（三例，已入 SKILL.md 正文）

1. **中维简体候选全灭→台港译名探测**：「母亲 (2009年电影)」简繁+「(电影)」四候选全 MISSING、list=search 亦无命中——真实条目名=台译「非常母親」（`titles=非常母親|骨肉同謀&redirects=1` 一次命中）；raw noteTA 块即译名对照表（zh-cn:母亲 (电影)/zh-hk:骨肉同謀/zh-tw:非常母親）。韩/日片常以台港译名存在（雪国列车→末日列車、寄生上流同型）。
2. **NYT 2010 wayback 快照长行过滤提取法**：71KB 快照无 `<p>` 无 articleBody 等 class——剥标签→按行拆→`len>80` 长行过滤→跳过首行浏览器升级提示（"NYTimes.com no longer supports Internet Explorer 8"）→15 长行 5.5KB 正文到手（含 Dargis 全部金句）。NYT 引号是弯引号需 norm 删引号。
3. **转引链英文回源三例（⑤b）**：主卡中文转引（雨自述/深渊小巷/横纵对照）校验短语必须写英文原句（IndieWire 'rain in either "Okja" or "Snowpiercer"' / mom_wiki 'train tunnel in Memories of Murder, the alley in Mother' / Guardian 'a horizontal counterpart to Parasite's vertical class stratification'），命中即升级「英文原文核实」。

## 预设验证结果

六项任务预设全部取证成立零证伪：母性执念、结尾反转（儿子真凶+母亲焚尸灭迹）、小镇封闭性、金惠子表演、黑色幽默与悲情混搭（幽默更少更冷）、犯罪悬疑结构。影迷反读（2961443 拾荒老人为凶）与官方剧情冲突，作现象记录不采信。

## 渠道备忘

- 百度百科「母亲」裸词条=日剧《Mother》(2010) 歧义（电影 vs 电视剧同名）——`item/母亲/5596814` 经 DDG site: `母亲 奉俊昊 2009` 定位，抓回后 grep 奉俊昊×52/金惠子×29/元斌×17 确认归属。
- Criterion 影片页猜 ID 30914 返回 "Shop All Films" 壳（无本片 essay 的旁证）；DDG 仅命中导演 Top 10 列表。
- 豆瓣 suggest 裸片名「母亲」一次命中 subject 3036460（2009/마더），与同名日剧 4303624 区分。
- Ebert CDX：`rogerebert.com/reviews/mother-2010*` 精确前缀通配一次定位（mother-1997 为另一部片，勿混）。
- 中维获奖段引用：青龙最佳影片/最佳男配角/最佳灯光、亚洲电影大奖最佳电影/最佳编剧/最佳女主角（繁体直录校验）。
