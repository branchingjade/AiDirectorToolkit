# 《摩登时代》(Modern Times, 1936) 单片研习轮来源地图 — 2026-08

**卓别林导演本体首轮（零存量全新建档）**。产出：《摩登时代_研习报告.md》+《摩登时代_技法卡片.md》（单片研习独立 [研S1-18] 编号体系，导演本体存档同轮落盘供深化轮复用）。

## 存档对照（pages/cha_*，47 个文件）

| 编号 | 文件 | 来源 | 关键内容 |
|---|---|---|---|
| 研S1 | cha_enwiki_raw.txt | en.wikipedia Modern Times (film) raw（32.6KB） | 档案/Plot/Production/Music/Reception/Restoration |
| 研S2 | cha_zhwiki_raw.txt | zh.wikipedia 摩登時代 raw（3.4KB 简略条目） | 上海上映、AFI 名单、声音策略 |
| 研S3 | cha_criterion_essay.txt | Criterion posts/1656「Modern Times: Exit the Tramp」Saul Austerlitz（wayback 2022-01-28 快照 31KB→clean 13.1KB；live+jina 均 CF 壳） | 有声片过渡、1931 原话、Ferguson 四段论、phantom screws、喂食机、塔蒂影响、origin story |
| 研S4 | cha_ebert_modern-times-1972.html + cha_ebert1972_live.txt | Roger Ebert 1972-01-25 原评（rogerebert.com live 83KB，JSON-LD 三证）；wayback 版 37KB 同存 | 机器奴役人寓言、机器代言人声、嘉宝注脚 |
| 研S5 | cha_nfr_vance.pdf + cha_nfr_vance_blocks.txt | LOC NFR essay by Jeffrey Vance（节选自《Chaplin: Genius of the Cinema》2003）；pdftotext 版 cha_nfr_vance.txt 双栏交错不可校验，blocks 版为校验档 | 片头字幕、swan song、无字歌唯一开口、结尾对白、Smile 起源、好莱坞最后默片 |
| 研S6 | cha_filmsite.html + cha_filmsite_clean.txt | filmsite.org/mode.html（45KB） | 背景参考（拍摄期口径与英维冲突） |
| 研S7 | cha_enwiki_dir.txt | en.wikipedia Charlie Chaplin raw（185KB，导演本体存档） | satire on industrial life 原话、Larcher 定性、5.15 事件、Robinson 巅峰论 |
| 研S8 | cha_zhwiki_dir.txt | zh.wikipedia 查理·卓别林 raw（40KB，导演本体存档；「查理·卓別林」为重定向） | 政治左倾、FBI 档案、1952 离美 |
| 研S9-17 | cha_review_<id>_<tag>.txt（9 篇） | 豆瓣 rexxar API（subject 1294371） | 1262992(1129)/3423264(567)/1849652(448)/5402003(288)/5631970(57)/8550648(64)/17572965(1)/10108467(5)/13090421(6) |
| 研S18 | cha_top250.csv | GitHub Mayandev/where-is-douban250 | subject id 1294371 定位（Top250 #88，9.3 分） |
| — | cha_probe1.json / zhprobe_raw.txt / cha_douban_suggest.json / cha_ddg_douban.txt / cha_bing_jina.txt / cha_bing_rss.xml / cha_ebert_search.html / cha_ebert_try.html / cha_probe_rev.json | 探测与负面取证留档 | 标题探测/Ebert slug 探测/搜索失败记录 |

## 关键引文位置（写文档前直接 grep）

- 「a satire on certain phases of our industrial life」→ cha_enwiki_dir.txt（Louvish p.257 转引）
- 「grim contemplation on the automatisation of the individual」→ cha_enwiki_dir.txt（Larcher p.64）
- 「working the assembly line until he becomes the assembly line」「phantom screws」「buttons on a woman's dress」「being shoveled a steady diet of metal nuts」「a chicken as a funnel」「the machine that is mankind's true opponent」「all of Jacques Tati's work springs from this segment」→ cha_criterion_essay.txt
- 「enslaving of man by machines」「channeled through other media」「after Garbo spoke」→ cha_ebert1972_live.txt
- 「marks the only time the Tramp ever spoke」「talking in any one language is meaningless in all others」「Buck up! We'll get along!」「Hollywood's last silent film, represents the end of an era」「was created to promote the reissue」→ cha_nfr_vance_blocks.txt
- 「18 frames per second」「silent speed」「machinery with only consideration of profit」「The Nonsense Song」→ cha_enwiki_raw.txt
- 羊群→人群蒙太奇/「Well，you're a free man.」（全角逗号）→ cha_review_5402003；「完全有理由成为电影史上最伟大最经典的蒙太奇」→ cha_review_1262992

## 渠道实测备忘（2026-08）

- **r.jina.ai 本轮整体失效**：criterion.com、baike.baidu.com、duckduckgo.com、bing.com 经 jina 全部返回 Cloudflare「Just a moment...」壳（5-6KB 签名）——jina 通道退化，wayback CDX + id_ 快照为第一兜底。
- **豆瓣 subject id 新通道**：`j/subject_suggest` 空数组（已知退化）+ 搜索引擎全灭 → `api.github.com/search/repositories?q=douban+top250`（免登录）→ Mayandev/where-is-douban250 的 where-is-top250.csv 含片名/年份/评分/subject URL 一次命中 → rexxar reviews 端点按影评内容确认归属。
- **Ebert Great Movies 版不存在（负面取证）**：great-movie-modern-times-1936 等多 slug live 404 + CDX 通配空；Ebert 对本片只有 1972 重映原评（live 可直连，JSON-LD 作者/日期验证）。
- **Criterion live 直连可开页但正文 CF 壳**：wayback CDX `criterion.com/current/posts/1656*` 命中 2022 快照 31KB 全文。
- **PDF 双栏交错坑**：LOC NFR essay 经 pdftotext 双栏文本逐行交错、压空白后引文仍被拦腰截断——`fitz.open()` + `page.get_text("blocks")` 按 `(round(y/10), x)` 排序重提取即恢复连续；norm 补 `re.sub(r'-\n','',s)` 合并断词连字符。
- **全角标点族坑**：豆瓣长评「Well，you're a free man.」全角逗号无空格 vs 引文半角逗号+空格假 MISS——norm 补全角标点族转换 + `re.sub(r'([,.;:!?])(?=[A-Za-z])', r'\1 ', s)`。
- 中维条目名「摩登時代」裸名即可（无后缀）；「查理·卓別林」重定向到「查理·卓别林」（简体主条目）。

## 预设对照结论

- 流水线异化（拧螺丝痉挛）✓ / 机器吞噬人（卷入齿轮）✓ / 喂食机 ✓ / 大萧条+有声片过渡 ✓——全部成立。
- 「末班台词（'微笑'）」✗ 精确化：唯一开口是无字歌 gibberish song；结尾对白是字幕 "Buck up! We'll get along!"；《Smile》为 1954 年重映配词主题歌。「微笑」作为意象/主题歌成立、作为台词不成立（详见研习报告 §5）。

## 校验记录

98/98 引文 0 MISS（verify 脚本 `pages/_verify_chaplin.py`）；S# 双向对账无孤儿无越界（研S14 孤儿号已补正文引用闭环）。
