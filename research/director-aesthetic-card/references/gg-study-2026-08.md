# 《消失的爱人》(Gone Girl, 2014) 单片研习轮来源地图（第三十一轮，芬奇补代表作）

创作极：叙事操控 / 婚姻战争 / 媒体共谋
产出：`film-suite-research/研习报告/消失的爱人_研习报告.md` + `技法卡片源稿/消失的爱人_技法卡片.md`（6 张卡片）
校验：76 条校验短语 0 MISS，[研S1-18] 双向对账无孤儿号（脚本 `_verify_gg.py`）

## 存档对照（18 项，gg_* 前缀）

| 编号 | 存档 | 来源 | 关键内容 |
|---|---|---|---|
| [研S1] | gg_enwiki_raw.txt | 英维 Gone Girl (film) action=raw 57.5KB | Production（Flynn 改编/50 takes/tragedy vampirism/服装）/Music（Reznor {{blockquote}} 一手引文：insincere façade/instill doubt）/Reception（Rothman heroes and villains aren't people but stories）/Themes 性别争议全景（Jezebel/Time/NYRB/Guardian） |
| [研S2] | gg_zhwiki_raw.txt | 中维「消失的爱人 (2014年电影)」API revisions 15.9KB | 条目正文**分节简繁混排**（剧情段繁体/制作票房段简体）；noteTA 台译「控制」港译「失蹤罪」 |
| [研S3] | gg_ebert.txt | RogerEbert.com **Matt Zoller Seitz** 影评 2014-10-02（meta description 定位法提取 8.6KB） | 五部短片论/表演性陈述/preposterous thriller/one step ahead/结尾=冷笑话/sick film, often brilliant |
| [研S4] | gg_review_script.txt | 豆瓣长评 14304813 中译剧本全本（艺馨译 73K 字符 2747 行） | 全片剧本：L1-18 开场画外音/L64 日记独白首句/L139 日记生产线 272 篇/L146-155 Cool Girl 独白+变身仪式/L157 计划时间表/L192 自杀改找工作/L244 战士对峙/L261 首尾对称 |
| [研S5-14] | gg_review_*.txt | 豆瓣长评 10 篇（8158/6175/4864/234/100/210/177/550/146/82 有用） | 秒切剪辑/双轨切换/反转前置/中产表演论/斯特林堡对照/反转链序列/apathy 论/表演人格时代 |
| [研S15] | gg_ddg_criterion.html | DDG site:criterion.com（14KB 反爬壳） | 弃用：anomaly/challenge 签名、零 result 链接 |
| [研S16] | gg_criterion_search.txt | criterion.com 站内搜索经 r.jina.ai（14KB） | 负面取证完成：仅 Carrie Coon 专访提及本片，无专属 essay |
| [研S17-18] | gg_douban_suggest.json / gg_rexxar_reviews.json | 豆瓣 API | subject id=21318488（裸片名一次命中）；长评 total 2848 |

## 本轮新坑/新通道（实测）

1. **RogerEbert.com 死后影评作者陷阱**：Ebert 2013-04 去世；2014 的 Gone Girl 影评=Matt Zoller Seitz（RogerEbert.com 主编）。抓回先验 JSON-LD `"author"` + `"datePublished"` + 文末 byline（三证一致才定归属）；引用按作者署名写「Seitz（RogerEbert.com）」而非「Ebert」。引文 grep 校验抓不到作者错误——归属类错误靠写作时核验（与 ㊾ 双版本归属同族，扩展到"站点默认作者"维度）。
2. **Criterion 负面取证流程细化**：DDG HTML site: 查询返回反爬壳（页面含 anomaly/challenge 字样、零 result 链接）→ 换 **criterion.com 站内搜索端点 `criterion.com/search?q=<片名>` 经 r.jina.ai 直连**（14KB 全文含文章列表）——命中仅"提及本片"的访谈即确认无专属 essay。福克斯/华纳等大厂片库片直接走此流程，别花多轮硬找（迷魂记轮负面取证流程的 DDG 反爬变体）。
3. **豆瓣长评=中译剧本全本再添一例**：review/14304813（艺馨译，2747 行）——Gone Girl 有正式出版剧本，影迷全文转载；剧本场景号+行号可直接作证据（与站台 5762548/悲情城市 15275339/东京物语 5759765/巴顿·芬克 7611902 同族）。
4. **中维条目名第四形态：简体带年份**：「消失的爱人 (电影)」简繁双 MISSING → list=search 命中「消失的爱人 (2014年电影)」（简体+年份消歧）——与繁体条目/重定向存根/去间隔号并列的新形态；探测序列照旧先 list=search。条目正文**分节简繁混排**（剧情段繁体、制作票房段简体）——㊸ 句内混排的分节级变体，引用时按段落实际字形直录。
5. **execute_code 与 terminal cwd 不一致再证**：execute_code 运行在 session 工作目录（C:\Users\<user>\Documents\Hermes），terminal 的 cd 不继承——execute_code 里写文件必须用绝对路径（黑泽明轮同坑，本轮第二次命中；首跑 8 个豆瓣存档全因相对路径 FAIL）。
6. **中维引文定稿前复核字形**：初稿把繁体存档引文（質疑尼克與自己的孿生妹妹瑪歌）写成简体（质疑/孪生/玛歌）——校验脚本用繁体短语能命中（证明引文在存档里），但**文档引文字形必须与存档一致**（逐字直录纪律，⑧/⑭ 补充：不只校验命中，文档侧也要按存档字形写）。

## 关键取证通道（复用配方）

- enwiki {{blockquote}} 模板=一手引文富矿（Reznor 配乐指令整段在内）——㉛ 提醒"剥模板会删引文"，校验脚本对存档建双变体（剥/不剥模板）
- 校验脚本 norm 需要：`''` 斜体标记剥离 + `[[管道链接]]` 剥壳（保留管道后正文）+ 弯引号归一 + 去书名号/括号 + 全空白剥离——本轮首轮 MISS 6 条全为 norm 缺件（`''` 未剥/`[[ ]]` 未剥）+ 校验短语笔误（代词写错/凭记忆造句）
- 反转前置结构证据：剧本 L139-157 ≈ 全片 1/3 处（"反转不在结尾在 1/3"=编剧技法金矿，进技法卡片 02）
- 对照资产：婚姻故事卡片（"不站队契约"→本片是"假不站队"陷阱）、花样年华卡片（留白 vs 全面爆发）——婚姻战争两极对比框架

## 预设核对（5 项全成立零证伪）

双视角结构（日记本 vs 现实双轨）✓ / 叙事翻转（中段真相揭穿站位转移）✓ / 媒体审判（Ellen Abbott 贯穿 10+ 次 + tragedy vampirism 芬奇原话）✓ / 婚姻战争日常化恐怖（对照婚姻故事/花样年华）✓ / 信息差操控精密计算（时间戳系统+50 takes+Seitz one step ahead）✓

## 诚实声明要点（详见产物文末）

- 未逐帧看片；剧本为影迷转载译本非官方稿；Criterion 无 essay（负面取证）；芬奇原话经英维转引（NPR/LA Times 原刊未直抓，措辞以英维 blockquote/转引为准）
- 「魔术的第三个步骤」台词剧本零命中（影迷引用）；「我为你难过，每天醒来扮作你这副模样」=小说句非电影剧本句——两句均不当作剧本证据
- 对照婚姻故事/花样年华为分析框架，无第三方并列文献
