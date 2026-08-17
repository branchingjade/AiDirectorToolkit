# 深作欣二导演轮（2026-08-09，日片黑帮/暴力导演轴）

> 产出：《深作欣二_导演美学卡片.md》+《深作欣二_手法体系深化.md》（`_work/v2-导演研习-20260809/深作欣二/`）；77 条引文 0 MISS；坑见 pitfalls-log「㊿ 深作欣二导演轮」条。

## 来源通道实测

| 通道 | URL 形态 | 结果 | 说明 |
|---|---|---|---|
| enwiki 主条目 raw | `en.wikipedia.org/w/index.php?title=Kinji_Fukasaku&action=raw` | 29KB ✅ | ⚠️ `Fukasaku_Kinji` 是重定向存根（28B）→ 目标 `Kinji_Fukasaku` |
| Midnight Eye 访谈 | `midnighteye.com/interviews/kinji-fukasaku/` | 25KB ✅ | 一手金矿：fable 论/「给年轻人的问候」/15 岁战争经历/代沟/反复兴抵抗/R-15 抗议。索引页 `midnighteye.com/interviews/` grep `interviews/<slug>/` 找 URL |
| enwiki 系列条目 raw | `title=Battles_Without_Honor_and_Humanity&action=raw` | 28KB ✅ | jitsuroku eiga 定义/任侠片对照/新闻片字幕（Nerdist）/群像剧共识/35–40 天拍摄/广岛方言 |
| enwiki 单片条目 raw | `title=Battle_Royale_(film)&action=raw` | 90KB ✅ | 寓言/代沟解读/Bradshaw/A.O. Scott/swan song/禁映/国会干预。⚠️ RT 引文在 `{{Rotten Tomatoes prose|...}}` 参数内→校验需剥/不剥模板双变体 |
| 日文维基主条目 raw | `ja.wikipedia.org/w/index.php?title=深作欣二&action=raw` | 26KB ✅ | 作風段=创作观转述+原话引录金矿（暴力を描くことで暴力を否定しよう/文芸アクション/平和は結構なことだが…） |
| 日文维基片条目 raw | `title=仁義なき戦い_(映画)&action=raw` | 404 ❌ | 真实条目名未定位，用 API `action=query&titles=` 探测再抓（别猜） |
| 中文维基 stub | API `titles=深作欣二` | 2.5KB ✅ | 仅定位性信息（第二代导演/作者派/商业片数量最多），作風内容靠 ja wiki |
| 中文维基单片 | API `titles=大逃殺_(電影)` | 40KB ✅ | ⚠️ 同句繁简混排（「這情況如請脫衣舞孃…」+「对日本國會议员」）；嘲讽议员引文转引《中国时报》梁良 |
| 豆瓣 subject id | `movie.douban.com/j/subject_suggest?q=<裸片名>` | ✅ | 无仁义之战=1394518、大逃杀=1292444（iPhone UA + Referer） |
| 豆瓣长评 | rexxar `m.douban.com/rexxar/api/v2/movie/<id>/reviews` + `/review/<rid>` | ✅ | 关键：3702808（107 有用，义理人情分析金矿）/7574007（美能幸三原型）/1080823（1094 有用）/14148854（刘慈欣评论转帖，⚠️正文截断）/5120630（144 有用，BR 规则三件套） |
| SoC 站内搜索 | `sensesofcinema.com/?s=fukasaku` | 无专条 ✅ | 负面取证：无 great-directors 专条；结果仅其他文章提及 |
| 百度百科 | 直连 + r.jina.ai | 403 ❌ | 按「未取证到」登记，不纠缠 |

## 已验证引文锚（写作核心）

- **一手（Midnight Eye 2001）**："This film is a fable…youth crime is a very serious issue in Japan" / "To me, these are greetings to the young people. Those were my words to the next generation of young people" / "Looking back to when I was fifteen I went through a certain period and experience. For this film I posed myself the question 'How would that be for these young people?'" / "I had doubts. Under that kind of situation where would the government be taking the whole nation?…That was very much clear in my films of the seventies." / "since the burst of the bubble economy…So I set Battle Royale within this context of children versus adults." / "The fact that adults lost confidence in themselves, that's what is shown in the film."
- **日文维基转述**："暴力を描くことで暴力を否定しよう"（以暴写反暴）/ "荒唐無稽やウソの物語をいかにリアルに仕上げる"（文芸アクション真实论）/ "平和は結構なことだが、その中で人間が衰弱してしまっているのではないか"
- **enwiki 转引**：BAMPFA "turbulent energy and at times extreme violence express a cynical critique of social conditions and genuine sympathy for those left out of Japan's postwar prosperity" / Nerdist "newsreel style" / Dennis Lim "drain criminal netherworlds of romance, crush codes of honor underfoot" / Bradshaw "a metaphor for the anguish of adolescent existence" / "perhaps the finest cinematic swansong ever conceived"

## 可复用要点

- **任务预设「暴力美学」标签**：取证后按深作本人「以暴写反暴」（ja wiki 转述）与影评人「新闻片/实录」（enwiki）重写该维度，诚实声明里逐条对照——预设只是线索，取证才是答案。
- **义理人情主题证据链**：3702808 长评「'仁义已死'绝非'仁义该死'」+ enwiki「ninkyō eiga vs jitsuroku eiga」类型断裂 + 7574007 回忆录原型。
- **日片导演轮顺序**：ja wiki 主条目作風段 → Midnight Eye 访谈（若存在）→ enwiki 主条目 → 豆瓣长评（义理/暴力主题靠影迷分析补）。
