# 坂本龙一研习轮记录（配乐轴·东方第一轮，2026-08）

产出：《坂本龙一_制作大师卡片.md》（`_work/制作大师研习-20260809E/坂本龙一/`）。本文件记录来源地图、已验证引语锚、本轮新陷阱。

## 来源 URL 清单（17 个有效存档 + 1 失败）

| 存档文件 | 来源 | 类型 | 备注 |
|---|---|---|---|
| sakamoto_wiki_main.txt | en.wikipedia.org/wiki/Ryuichi_Sakamoto | 英文维基主条目 | 143KB，r.jina.ai 可抓 |
| sakamoto_wiki_zh.txt | zh.wikipedia.org/wiki/坂本龙一 | 中文维基主条目 | 128KB，r.jina.ai 直抓成功（本轮无需 API fallback） |
| sakamoto_criterion_interview.txt | criterion.com/current/posts/4625-sonic-memories-a-conversation-with-ryuichi-sakamoto | **一手访谈**（Criterion Current 2017） | 14KB，r.jina.ai 直抓成功 |
| sakamoto_revenant_vinylfactory_interview.txt | thevinylfactory.com/features/the-revenant-ryuichi-sakamoto-alva-noto-interview | **一手访谈**（坂本+Alva Noto） | 13KB |
| sakamoto_revenant_rollingstone.txt | rollingstone.com/music/music-features/ryuichi-sakamoto-details-gigantic-score-...-65963/ | **一手访谈** | 6.8KB |
| sakamoto_guardian_obit.txt | theguardian.com/music/2023/apr/03/ryuichi-sakamoto-obituary | 讣告 | 注意 URL 是 apr/03 不是 apr/02（apr/02 版 404） |
| sakamoto_oscars_obit.txt | newsletter.oscars.org/news/post/ryuichi-sakamoto-oscar-winning-...-dies-at-71 | 官方讣告 | 含坂本原话引用（45 cues），Oscars 域名可抓 |
| sakamoto_last_emperor_album_wiki.txt | en.wikipedia.org/wiki/The_Last_Emperor_(album) | 原声带专条 | **多作曲配乐分工的权威来源**（曲目表逐轨署名） |
| sakamoto_last_emperor_wiki.txt | en.wikipedia.org/wiki/The_Last_Emperor | 影片专条 | 奖项段 |
| sakamoto_mcml_wiki.txt | en.wikipedia.org/wiki/Merry_Christmas,_Mr._Lawrence | 影片专条 | 选角轶事/奖项 |
| sakamoto_mcml_instrumental_wiki.txt | en.wikipedia.org/wiki/Merry_Christmas_Mr._Lawrence_(instrumental) | 主题曲专条 | 影评人 Bradshaw 评语 |
| sakamoto_mcml_ptna_analysis.txt | enc.piano.or.jp/en/musics/18613 | **乐谱级分析**（日本钢琴教师协会） | 日文机翻版；引坂本自传《音楽使人自由》 |
| sakamoto_revenant_soundtrack_wiki.txt | en.wikipedia.org/wiki/The_Revenant_(soundtrack) | 原声带专条 | 乐评引语/奥斯卡资格争议 |
| sakamoto_revenant_wiki.txt | en.wikipedia.org/wiki/The_Revenant_(2015_film) | 影片专条 | 录音场地/指挥细节 |
| sakamoto_coda_wiki.txt | en.wikipedia.org/wiki/Ryuichi_Sakamoto:_Coda | 纪录片专条 | 福岛后风格转向 |
| sakamoto_last_emperor_factoids.txt | tommoody.us/archives/2017/05/16/the-last-emperor-factoids/ | 现场对谈转述（**二手**） | 64 cues 口径与 45 cues 冲突 |
| sakamoto_last_emperor_reissue.txt | thevinylfactory.com/news/the-last-emperor-score-vinyl-... | 新闻 | Erhu/传统打击乐细节 |
| sakamoto_nyt_async.txt | nytimes.com/2017/04/21/arts/music/ryuichi-sakamoto-async-interview.html | **失败** | CAPTCHA 拦截仅 238 字节 |

## 已验证引语锚（grep 通过）

- "I've always felt truth in the saying 'less is more', and strive for that in my writing."（Vinyl Factory）
- "I wrote forty-five music cues in one week."（Criterion + Oscars 讣告双源）
- "Each time is like a little journey into an unknown culture."（Criterion，配乐=学习陌生文化）
- "It's very important for me to have space in between objects."（Criterion，留白论）
- "My desire was the only rule."（Criterion，async 创作法）
- "adding music where the visual power was weak"（PTNA 引坂本自传）
- "a fantastical Oriental place, neither East nor West"（PTNA 引坂本自传）
- "glacial chords that build toward a fortissimo horizon... The score doesn't so much follow the action here as lead it"（NY Magazine Justin Davidson，经维基专条转引）
- "assembled from the music of more than one composer"（奥斯卡取消资格官方理由，维基专条）
- "an inspirationally catchy westernised pop take on Japanese music"（Guardian Bradshaw，经主题曲专条转引）

## 东方配乐轴特有发现

1. **Criterion Current 一手访谈可抓（反爬现状修正）**：Deakins 轮记录"criterion.com 反爬"——但 `criterion.com/current/posts/<id>` 栏目页 2026-08 经 r.jina.ai 直抓成功（14KB）。结论：Criterion 的 current/posts 访谈页可尝试 r.jina.ai，被拦再按 Deakins 轮顺序降级。
2. **多作曲配乐的分工取证靠原声带专条曲目表**：《末代皇帝》三人署名（坂本 9/伯恩 5/苏聪 1）逐轨列在原声带专辑维基专条（The Last Emperor (album)），是"谁写了哪首"的权威底座；汉斯·季默任 associate producer 也在此专条 Personnel 段。
3. **日本乐谱级分析源=PTNA（enc.piano.or.jp）**：日本钢琴教师协会的曲式分析（五声音阶/和声进行/动机），与 Morricone 轮的 Italian Piano 同等级；且直接引坂本自传《音楽使人自由》（2009）——日本作曲家的"分析文引自传"链路。
4. **"东西融合"的可验证配方**：坂本作曲笔记自标 pentatonic/Oriental/Japanese-like + ヨナ抜き音阶（日本去四七五声音阶）旋律 × 西方古典阻碍终止（IV→V→VI→III）和声——比"中西融合"空话更可引用的技术证据。
5. **一手访谈站补位**：thevinylfactory.com/features/ 有配乐类一手访谈（坂本×Alva Noto 谈荒野猎人），r.jina.ai 可抓；Oscars 官网（newsletter.oscars.org）讣告含作曲家原话引用。
6. **NYT 被 CAPTCHA 拦截时的补位链**：NYT Async 访谈（2017）抓不到（238B 警告）→ 用 Criterion（同内容主题）+ Rolling Stone + Guardian 讣告覆盖"癌症后创作"；**搜索摘要里的引语（如 Fennesz 评"the importance of silence in music"出自 NYT）无原文不得写入卡片**——诚实声明如实记"未取到"。
7. **弯引号陷阱新变体**：Guardian 原文用弯撇号（I don’t think I’m Japanese），grep 直撇号 0 命中——用 Python re 按 `don.{0,3}think` 通配验证。维基原文带方括号的引语（"[his] bible"）摘录时必须保留方括号形态或注明。
8. **证据纪律实例**：签名句曾写"东方音色（二胡、太鼓、笙）"——grep 后笙（shō）仅见于 2021 装置作品 TIME（主条目），非配乐，删除。乐器论断必须绑定到具体作品。
9. **双口径实例**：末代皇帝 cues 数 45（Criterion 一手/Oscars 讣告）vs 64（tom moody 现场转述博客）——卡片按一手写 45，64 仅入来源清单，诚实声明标注。

## 诚实声明必备项（本轮）

未逐帧看片/未系统听辨原声带；NYT 未取到；"伯恩写非西方主题、坂本写西方主题"为二手博客转述（一手访谈未直接出现）；PTNA 为日文机翻版；配乐总数 40+（Oscars 口径）双口径。
