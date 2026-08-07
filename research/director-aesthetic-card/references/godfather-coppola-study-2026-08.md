# 教父·科波拉单片导演层深化轮（2026-08）

单片轮（产出《X_研习报告》+《X_技法卡片》），导演本体零存量。任务预设五焦点全部取证成立零证伪：婚礼群像调度（Willis「two rhythms」原话 + Tavoularis「tableau shots」+ 剪辑师 Reynolds 交叉剪辑证词 + 豆瓣逐镜拉片双源）、迈克尔弧线（Ebert 明确定位医院夜「I'm with you now」为转折点）、暗光摄影（Willis「dirty yellow feel」「sometimes you'd see his eyes, sometimes not」原话 + Ebert Tessio 光线叙事）、跨代叙事（Kael 原评「the span is only from 1945 to the mid-fifties」经 enwiki 转引）、黑帮密码对照（Ebert「closed world」论 + 本地《码头的秩序_犯罪黑帮密码回测》承接）。

## 存档（22 档 pages/coppola_*，独立 [研S#] 编号）

- enwiki The Godfather raw 173KB / enwiki Francis Ford Coppola raw 169KB（Kael 原评大段转引在此）
- zhwiki `教父 (電影)` raw 44KB（简体重定向→繁体重抓）/ zhwiki 法蘭斯·福特·哥普拉 raw 12KB
- Ebert 双文 live 直抓：Great Movies essay（closed world 论）+ 1972 首评（rotogravure tint）
- Telegraph Philip Horne 2009 采访（wayback 快照→长行过滤 clean）——Ruddy/科波拉原话集中地
- New Yorker Michael Sragow 1997「The Making of The Godfather」（wayback 854KB→长行过滤 clean 41KB）——**导演层核心金矿**：Willis/Tavoularis/Reynolds/Zinner/Towne 全部一手转述
- Guardian Danny Leigh 2022 五十周年 + Bradshaw 2022 重评（Guardian API 发现 URL→live 直抓→data-gu-name="body" 提取）
- Criterion 站内搜索负面取证（criterion.com/search?q=godfather live 直抓 208KB，无教父 essay——派拉蒙版权）
- 豆瓣 rexxar 8 长评（7389/6945/3594/2177/1237/710/139/150 有用，含逐镜拉片两篇）+ subject_suggest JSON

## 四新坑（含修复配方）

### ① 校验脚本 raw string 的 Unicode 转义字面化 → 弯引号假 MISS（本轮 8 条假 MISS 全因此）
校验脚本整体包在 r'''...''' 里时，`"\\u2019"` 是字面 6 字符反斜杠序列而非 Unicode 弯引号——`s.replace("\\u2019", "'")` 什么都不替换，Ebert/New Yorker 等全弯引号文本的所有引文全部假 MISS。
**修复**：norm 的替换表必须用真转义——写普通字符串（非 raw）或 `chr(0x2019)`；写完先跑一条已知弯引号引文（如 "I'm with you now"）自测 norm 生效。
**同族**：校验短语若横跨弯引号（如 `famous "baptism massacre" is tough`）必假 MISS——短语避开引号段，改用引号外子串（`is tough, virtuoso filmmaking: the baptism provides...`）；enwiki raw 校验短语同样避开 `[[wikilink]]` 段（`[[family saga]]` → 用 `and a metaphor for capitalism in america`）。

### ② Ebert live 新版页（2026）正文定位
rogerebert.com live 直连可抓（教父轮两次 118KB/110KB 真 HTML，`<title>` 含片名即验证）；新版页面**无 post-content/entry-content class**（grep 定位法失效）。
**修复**：`<article id="post-<数字>" class="...review...">` 是影评正文容器，从该 article 起剥标签即得全文（`<footer|</article>` 截尾）；旧 wayback 定位法（meta description/h1）仍适用于快照。

### ③ 写死路径原位覆盖存量产物 → [卡X] 自引用悬空
任务指定输出路径与存量文件相同（如《教父_技法卡片》《教父_研习报告》已有剧本层 v1，本轮导演层 v2 覆盖）时，新文件引用旧层结论（[卡教父研习]）会指向已不存在的文件。
**修复**：覆盖前把旧层核心结论（三幕表/统计/引文）并入新文件成为「存量摘要」章节（§12），版本头声明「v1 核心结论已并入 §n」，引用标注指向该摘要而非外部文件；编剧稿层卡片原样保留为合并文件第一部分。

### ④ 豆瓣 subject_suggest：jina 代理被 CF 挑战壳挡
兜底链原为「direct 空 → jina 代理」；教父轮实测 direct 返回 2 字节空、jina 返回 5.8KB "Just a moment..." CF 挑战壳。
**修复**：兜底链补一档——iPhone UA + `Referer: https://m.douban.com/movie/` 直连 `movie.douban.com/j/subject_suggest` 一次成功（与 rexxar reviews 配方同族；教父 subject id=1291841 由此确认）。

## 其他实测通道

- **New Yorker wayback 全页 854KB**（Condé Nast 现代页）：长行过滤（>60 字符）提取 41KB 正文，与 NYT 老报纸快照同族
- **Guardian 正文提取**：`<div data-gu-name="body">` 容器剥标签（或长行过滤兜底）
- **pinyin 前缀碰撞再例**：pages/gf_* 全属《好家伙》并行轮（gf_=Goodfellas），教父存量只有 godfather-1972.txt 剧本——开局盘存量必须核对内容归属，新轮用 coppola_* 前缀
- **好家伙轮存档转引**（vs 节）：gf_criterion_7103.txt Criterion Daily 对比句（"David Lean–like pageantry" vs "shock to the system"）、gf_nyt_banality.txt NYT 1990 对比句——跨轮转引以存档文件名为标注，内部编号未知不硬造

## 产出

- 研习报告/教父_研习报告.md（v2 导演层深化 330 行，含 §12 剧本层存量摘要）
- 技法卡片源稿/教父_技法卡片.md（v2 合并：第一部分剧本层 8 卡存量 + 第二部分导演层 7 卡）
- 校验：_verify_godfather.py（EN 110 条 0 MISS）+ _verify_godfather_zh.py（ZH 27 条 0 MISS）
