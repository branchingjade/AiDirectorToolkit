# 梶浦由记研习轮记录（2026-08 · 配乐轴·日本动漫声乐系第一轮）

产出：`research_arrangement/梶浦由记.md`（编曲研习卡：定位/实证拆解/创作观/技法清单/来源）。存档：`research_arrangement/pages/`（25+ 文件：维基 raw、chordu/UG/tumblr 谱面、7 篇访谈）。

与 `sawano-session-2026-08.md`（剧伴轴）互补：本轮覆盖歌姬系/声乐系作曲家（作词作曲编曲一人全包 + 多歌姬项目），主攻「人声编排/造语/合唱」类内容取证。

## 来源地图（本轮回实测）

| 来源 | URL 模式 | 状态 |
|---|---|---|
| canta-per-me.net（梶浦粉丝站） | `/yuki-kajiura/interviews/` 索引 + `/lyrics/about-kajiurago/` 主题聚合页 | ✅ curl 直抓 70-100KB，访谈原文/英译 |
| 日文维基 action=raw | `ja.wikipedia.org/w/index.php?title=<标题>&action=raw` | ✅ 歌曲条目标题先 search API 定位（见陷阱2） |
| アニメイトタイムズ | `animatetimes.com/news/details.php?id=<id>` | ✅ curl 直抓 |
| ANIPLEX 官方新闻页 | `aniplex.co.jp/news/detail/?id=<id>` | ✅ curl 直抓，官方一手 |
| 音楽ナタリー natalie.mu | 全部页面 | ❌ urllib 405 / r.jina.ai 403 / 浏览器人机验证墙（2026-08） |
| OH-news | oh-news.net | ❌ 原站已死，域名被垃圾站占用（404） |
| リスアニ! 杂志原文 | lisani.jp | ❌ 仅目录；anime-diary.net 博客要点摘录可用（二手转述） |
| chordu | `chordu.com/chords-tabs-<artist>-<song>-id_xxx` | ✅ 机器转谱：Key/BPM/和弦池；「BPM of N」字样=该曲 BPM |
| Ultimate-Guitar 用户谱 | `tabs.ultimate-guitar.com/tab/...` | ✅ 461KB 页内嵌 tab JSON，`[ch]` 标记可正则提取 |
| tumblr 制谱博客 | `kalafina-yk-chords.tumblr.com` | ✅ 分段落完整和弦（Intro/Verse/Refrain/Chorus/Bridge） |

## 已验证引语锚（卡片引用，全部 grep 命中存档）

- 情绪波浪：「you shouldn't insert your most moving song before the most moving scene comes up...」[小圆叛逆篇官方访谈/英版蓝光小册子]
- 草稿先行：「I'd think of the overall flow, and just create the atmosphere of each score. I'd make rough demos」[同上]
- 声音入场：「the way the sound is first heard is so important... Sometimes I'll have the music start in a way that no one will notice」[同上]
- 音乐不下道德判断：「If you determine who's good or evil through music, then the viewers would think the same way」[同上]
- 造语解放：「it would not be shackled by meaning, allowing listeners free rein for imagination」[AnimeGiga 访谈]
- BGM 复用功能：「If you use actual lyrics, songs instantly take on their own meaning... can create problems when used in a different scene」[NHK Imagine-nation]
- 造语起源：「BGMに意味のある言葉をつけてしまうと、使えるシーンが制限されてしまう」[JASRAC Magazine 2025]
- 歌い手100%成功：「歌い手さんが気持ちよく歌ってくれたら100％成功です」+ 选歌手标准「声に明るさがあること/理解の速さ/伸び代」[音楽ナタリー PARADE 访谈 2023，经 canta 存档]
- BGM=読書感想文：「BGMは読書感想文だと思って書く」「歌詞の意味は、聞き手の想像に任せたい」[7ルール节目/Oggi 2021]
- 官方评论：「試行錯誤の結果作り上げたこの曲」+「let the stars fall down」=《満天》母题 [ANIPLEX 2012-04-19]
- リスアニ! vol.05 摘要：「脚本を読んで『覚悟を決めた』」「相当、メロディを抑えた」「EDはバラードと言われてたけど、作っているうちに変わった」[anime-diary.net 转述，二手]

## 勘误案例（署名核查铁律的又一实例）

- 动画 OP/ED ≠ 剧伴作曲家：《コネクト》(小圆 OP) 作曲=渡辺翔 / 编曲=湯浅篤（ClariS 单曲，2011-02-02），梶浦在小圆只做剧伴+ED《Magia》。查证法：单曲维基条目 infobox 的 Writer/arranger 行（`コネクト (曲)`、`Magia`、`To the beginning` 各有独立条目）。写作时加「勘误框」+ 梶浦本人对该曲的正面评价作对照。

## 和弦取证（歌曲侧）

- **Magia**：chordu 机器判定 Key Dm / BPM 125 / 和弦池 `A,D,Bb,F,Gm,Bb,Ab,Bb,Cm,Ab`；无人工精谱（chordwiki 403、gakufu 超时、ufret JS 渲染）→ 卡片标注「机器判定」，骨架 i–bVI–bVII（Dm–Bb–C）+ Ab 半音标「推定」。
- **to the beginning**：UG 用户谱 + tumblr（sprinterxkyrie）双谱互证，段落级一致 → 采信。分析结论：全曲 A 大调轨道内平行大小调切换（Intro C#m → Verse Am → PreChorus C → Chorus F#m/A），副歌 vi–IV–ii–V–I + G#m7b5–C#–F#m 收束，终段 C#sus4–C#–D#m 升半音。
- **双谱互证法**：两个独立用户转录的段落级和弦一致即采信；chordu 机器池作弱证据。

## 陷阱

1. **日文 HTML 词内散落空格**：「妖しい音 を奏でている弦」「す ごく妖しげな」——原文排版在日文词内插空格；验证必须「全部去空白」再匹配，只折叠空白仍 MISS（本轮 5 条首验 MISS 中 2 条即此因）。
2. **日文维基歌曲条目标题变体**：Magia 条目就叫「Magia」、ttb 在「To the beginning」（大写 T）、コネクト 在「コネクト (曲)」——action=raw 404 后用 search API（`action=query&list=search`）定位，别猜。
3. **natalie.mu**：urllib 405、jina 403、浏览器人机验证墙三层拦截——直接放弃，用 canta-per-me 存档替代。
4. **chordu 页面**：「100 % ➙ 153 BPM」滑块值=该曲机器判定 BPM；「BPM of 125」字样双重确认。
5. **引用层级**：粉丝站存档原文照录算一手引语但标注「经 canta-per-me.net 存档」；博客要点摘录标二手转述；机器转谱标「机器判定」。
6. **OH-news 类已死站**：canta 存档页仍在（`/yuki-kajiura/interviews/oh-news-magia-interview/`），原站 404 但存档可用——先查粉丝站再放弃。
