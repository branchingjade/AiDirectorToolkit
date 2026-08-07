# 维伦纽瓦深化轮来源地图（2026-08-07）

产出：《维伦纽瓦_手法体系深化.md》（技法卡片源稿/，双线矩阵：悬疑罪案线/科幻哲思线）。
手法体系深化·无主卡片变体再例：自建编号 [S1-S6]（网络存档）+ [卡X]（本地资产/并行轮存档）双轨，头部声明"若后续主卡片落盘按存档文件名映射对齐"（李安/芬奇轮同型）。

## 存档对照（pages/，零存量全新建档，英维 raw 一次全成）

| 编号 | 文件名 | 来源 | 关键内容 |
|---|---|---|---|
| S1 | dv_enwiki_raw.txt | 英维 Denis Villeneuve 导演条目 | **双线锚点金矿**：风格起点句（Starting with Polytechnique...long takes...periods of wordless silence...shallow focus, high-contrast）、身份主题五片并列句（Sicario/Enemy/Arrival/BR2049/Dune）、罪案线片目分组句（the thrillers Prisoners, Enemy, Sicario）、Ehrlich IndieWire 诺兰对比句（Christopher Nolan is the only other person...）、Scott=2049 执行制片 |
| S2 | dv_incendies_enwiki_raw.txt | 英维 Incendies | 遗嘱驱动多重揭示（双信同人）、维伦纽瓦"a modern story with a sort of Greek tragedy element"、静默片构想（even envisioning a silent film, abandoning the idea due to expense）、Howell"a commanding film of multiple revelations" |
| S3 | dv_sicario_enwiki_raw.txt | 英维 Sicario (2015 film) | 任务套任务剧情（real mission is to disrupt...）、RT 共识 taut/tightly wound、Empire beautifully murky、Jóhannsson 二连（Prisoners 之后）、三项奥斯卡提名（摄影/配乐/声音剪辑） |
| S4 | dv_arrival_enwiki_raw.txt | 英维 Arrival (film) | 选摄影师原话（strong roots in realism...not be afraid to deal with intimacy）、脏科幻（dirty...slightly boring）、调色原话（let her be pasty）、Interstellar 改结局（blueprints to an interstellar ship→power of their language，因 2014 星际穿越放弃）、Slate Wickman 诺兰对比（only intermittently stellar）、八提一得（Best Sound Editing） |
| S5 | dv_blade2049_enwiki_raw.txt | 英维 Blade Runner 2049 | Deakins 拒九机位/1.55:1 单机位 Arri Alexa XT Studio/32mm vs 14-16mm、四小时初剪自评 quite strong/too self-indulgent→定剪 more elegant、换配乐原话（needed to go back to something closer to Vangelis）、A.O. Scott unnerving calm、LaSalle 跨片语气（similar narrative tone...such as Arrival）、木马记忆真相+交还 Deckard、实景灵感（北京雾霾/孟加拉拆船厂/巴比肯） |
| S6 | dv_dune_enwiki_raw.txt | 英维 Dune (2021 film) | 延迟开发沙丘句（chose to complete Arrival and BR2049 first...employing his past experience）、IMAX Alexa LF/1.90:1/1.43:1/35mm 转印回 4K、fake documentary realism 声音（水听器录死亡谷流沙）、Zimmer 拒诺兰《信条》配沙丘、沙幕替绿幕、18 吨沙、1,200/1,700 VFX、Empire Nolan mould、Brooks multiplex-arthouse 桥梁、Collin desolate grandeur、Greenblatt grim grandeur、六项奥斯卡（含声音混音） |

清理脚本：pages/_dv_clean.py（剥 ref/模板/管道链接，保留 {{Quote}}，迭代剥最内层模板）。校验脚本：pages/_dv_verify.py（68 引文 0 MISS）。

## 并行轮存档复用（㊴ 变体）

定稿前重扫 pages/ 发现并行《沙丘》轮 villeneuve_dune_* 存档中途落盘（Ebert/Tallerico/卫报 Bradshaw+Brooks+预览文/豆瓣长评/中维条目/villeneuve_enwiki_raw.txt=与 S1 同源）。处置：
- 复用卫报 Bradshaw 影评导语一条（"has been given room to breathe, creating a colossal spectacle"，链 B 佐证），登记 [卡沙丘·卫报Bradshaw]，校验目标=存档本体。
- **"访谈"档先验内容再提取**：villeneuve_dune_guardian_interview_body.txt 名为访谈、实为 2021-10-29 预览分析文（无导演原话）——复用前 grep 导演 said/引号密度判断文章性质，别被文件名误导。
- 《降临/沙丘_技法卡片.md》仍未落盘：占位 [卡降临]/[卡沙丘]，诚实声明注明落盘后可互引升级。

## 新坑四例（本轮实测）

1. **批量抓取循环 case 命名映射无默认分支=覆盖存档**：`for u in ...; do case "$u" in *A*) f=a;; *B*) f=b;; esac; curl -o "$f" "$u"; done`——URL 不匹配任何 pattern 时 f 沿用上一轮值，curl -o 把当前内容写进上一个存档（Dune 210KB 覆盖了 blade2049 档 145KB，2049 内容丢失须重抓）。修复：case 末尾加 `*) echo "unmatched"; exit 1;;` 兜底；抓完逐档 `wc -c` 核字节数（145818 vs 210913 立即暴露错位）。
2. **重音字符归一映射漏字再例（è U+00E8）**：norm 表只映射了 é/ó/í/à，漏 è——"mise-en-scène" 假 MISS（scene vs scène）。重音映射按拉丁字母全量补齐（àáâäèéêëìíîïòóôöùúûüçñ），别只补遇见的那个。
3. **测试短语手打=假 MISS 双例**：凭印象手打 "Johan" vs 存档 "Jóhann"（既丢重音又丢一个 n）致假 MISS，而成稿文档本身是对的。纪律：测试短语必须从成稿文档复制原文；MISS 先怀疑测试短语/脚本（本例如是），再怀疑文档与存档（贾樟柯轮③同族）。
4. **[卡X] 前缀误挂网络存档编号**：正文曾写 "[卡S6]"（本地资产前缀误挂到网络存档编号）。定稿前 `grep -c "卡S" 文档` 应为 0；[卡X] 只用于本地资产/并行轮存档，网络存档一律 [S#]（转引编号三坑的第四变体）。

## 任务预设处置记录

- **片序纠正**：任务预设科幻线"降临→沙丘→银翼杀手2049"错序，实际 降临2016→银翼2049 2017→沙丘2021（库布里克轮同型：预设片序只当线索不作时间线依据）。
- **线起点纠正**：罪案线预设"焦土之城→边境杀手"，实际风格起点=《理工学院》(2009)（英维风格段明文），线内含 Prisoners/Enemy（导演条目分组原话）。
- **"慢科幻"=提炼命名**：非导演自述非既有术语；锚点=unnerving calm/四小时初剪自评/pacing 争议双面记录（批评者嫌慢 vs Dargis 认为与世界观相称）。维伦纽瓦对"慢"的直接自述未取证到。
- **密码文件缺失**：《科幻奇幻题材密码.md》本机不存在→《手心人_科幻奇幻密码回测.md》转述通道（李安/芬奇轮同型再证）。

## 未取证项（留待后续轮）

沙丘2 未单独抓页（仅导演条目总括）；囚徒/宿敌未抓片条目；Sicario 镜头量化数据未取证（无 Deakins 访谈档）；导演访谈原文档未抓（本轮引文全来自英维条目及转引一手影评）；豆瓣中文长评未抓（全英文证据）。
