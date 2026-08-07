# 城市之光单片轮来源地图（2026-08，卓别林深化研习）

卓别林导演本体零存量，全新建档 19 项 [研S1-研S19]（+ 并行轮中途落盘 1 项未复用）。
产出：《城市之光_研习报告.md》《城市之光_技法卡片.md》（film-suite-research/研习报告/ 与 技法卡片源稿/）。
校验：_verify_citylights.py，143 引文 0 MISS。

## 存档对照（pages/）

| 编号 | 存档 | 来源 | 要点 |
|---|---|---|---|
| 研S1 | chaplin_citylights_enwiki_raw.txt (56KB) | 英维 City Lights raw | 结尾对白逐字/制作（结尾先写=center of the entire film、dance 自述、拳赛 4+6 天、380 群演、切瑞尔矛盾）/影评（Ebert 四星全文句/Agee/LA Examiner/Mordaunt Hall）/榜单 |
| 研S2 | chaplin_citylights_zhwiki_raw.txt + _clean.txt (40KB) | 中维 城市之光（裸名条目 pageid 698039） | 谢尔伍德城市论/塔可夫斯基/费里尼指涉/伍迪·艾伦曼哈顿/齐泽克/1952 视与听第 2/配乐 100+/帕迪拉诉讼 |
| 研S3 | chaplin_enwiki_raw.txt (185KB) | 英维 Charlie Chaplin raw | 个人最爱（Vance）/21 个月/塔可夫斯基英文原句/费里尼 Adam/Vance 作曲评语 |
| 研S4 | chaplin_zhwiki_raw.txt + _clean.txt (40KB) | 中维 查理·卓别林 raw | 形象演变（基石粗暴→艾萨奈温和、《银行》首创伤感结局）/艾吉 1949/基顿对比 |
| 研S5 | chaplin_citylights_criterion_jina.txt (25KB) | Criterion Giddins essay（CF 壳→jina） | 笑泪对置/只哭一次/声音幻觉/结尾三层凝视/流浪汉终结/Huff 20 主题 95 cues/Padilla |
| 研S6 | chaplin_citylights_ebert_jina.txt (8.8KB) | Ebert Great Movies 1997（jina） | 肢体即语言/两个看不见的朋友/威尼斯泪广场/100 美元细节/Chaplin vs Keaton |
| 研S7 | chaplin_citylights_baike_jina.txt (74KB) | 百度百科 城市之光（jina） | 342 遍重拍 0.95%（单源存疑）/1927-12-31 开拍口径（vs 英维 1928-12-27）/选角芝加哥说 |
| 研S8 | chaplin_wikiquote_raw.txt (23KB) | en.wikiquote Charlie Chaplin raw | "Life is a tragedy when seen in close-up, but a comedy in long-shot"（卫报讣告转引） |
| 研S9 | chaplin_citylights_ddg_subject.txt (12KB) | DDG 经 jina 定位豆瓣 subject | subject 1293908 确认；1474457=1947 同名片排除 |
| 研S10-19 | chaplin_cl_review_<id>.json/.txt ×10 | 豆瓣 rexxar 长评 | 906/403/200/57/49/43/21/18（电影手册 585 机翻）/9（戏梦巴黎台词）/3（斯科雷基机翻） |

并行轮存档：chaplin_citylights_wiki.txt（56KB，同批深化轮子代理落盘，与研S1 基本同文，未复用）。

## 校验新坑（㊿ 城市之光轮，序号与既有轮次同名并存）

1. **自闭合 `<ref name="X" />` 吞正文**：`re.sub(r'<ref[^>]*>.*?</ref>', '', t, flags=re.S)` 遇到自闭合 ref 时 `.*?` 吃到下一个 `</ref>`（中间隔整个 Reception 段）→ 4 条英维引文集体假 MISS。解法：先 `re.sub(r'<ref[^>]*/>', ' ', t)` 再剥配对 ref。
2. **jina markdown 软连字符 U+00AD**：`look­ing` 分词残留，norm 先 `s.replace('\u00ad','')`。
3. **jina markdown 斜体下划线**：`_illusion_` 替换成空格会把短语断成 `in  illusion  of` 假 MISS——`re.sub(r'[*_]+','',s)` 删成空串而非空格。
4. **MediaWiki 语言转换标记 `-{表}-`**：`强调-{表}-演` 不先 `re.sub(r'-\{([^{}]*)\}-', r'\1', s)` 则假 MISS。
5. **中维条目繁简混排**：同条目 `曼哈頓`（繁）+`最后一个场景`（简）并存——校验短语按存档原文字形直录最稳。
6. 附：中文豆瓣帖可能用半角标点断句（`情怀.对社会的关心,`），逐字连引须保留原标点或分段引+注释。

## 预设处置

- 六项任务预设全部取证成立零证伪（含泪的笑/肢体语法距离论/绅士流浪汉/结尾凝视/肢体→对白→情境演变链/大师影响链）。
- 附加预设「342 遍重拍」=百度百科单源，标存疑；「选角渠道」两说并存（芝加哥街头 vs 拳击场）。
- 预设「喜剧是距离的艺术」未取到原句 → 原句 "Life is a tragedy when seen in close-up, but a comedy in long-shot"（卫报讣告转引），中文意译标注处理。
- 喜剧题材密码本地不存在（find 全盘验证、回测报告/无喜剧类）→ 第六章以取证证据构建分析框架并声明。

## 渠道实测

- Criterion posts/2957：live CF 壳 5.5KB → r.jina.ai 一次 25KB 全文。
- rogerebert.com Great Movies：jina 直抓 8.8KB（enwiki ref 直接给出 slug=great-movie-city-lights-1931，免 CDX）。
- 豆瓣 subject_suggest 空数组 `[]` → DDG 经 jina site: 定位一次命中 1293908。
- 中维标题探测：`城市之光 (1931年电影)`/`(电影)` 全 MISS，裸名 `城市之光` 命中（好莱坞黄金期老片裸名条目形态）。
- 无公开剧本：默片剧本渠道未抓取，台词证据以英维剧情+影评人转述为准。
