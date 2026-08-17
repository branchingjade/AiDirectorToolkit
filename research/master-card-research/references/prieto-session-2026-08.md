# Rodrigo Prieto（罗德里戈·普列托）研习轮记录 · 2026-08-09E（摄影轴·李安补）

产出：《罗德里戈·普列托_制作大师卡片.md》→ `_work/制作大师研习-20260809E/罗德里戈·普列托/`（pages/ 存档 25 文件）。

## 来源 URL 清单（对应卡片 S1–S14）

| 编号 | URL | 通道 | 结果 |
|---|---|---|---|
| S1 | https://en.wikipedia.org/wiki/Rodrigo_Prieto | 维基 API | 24KB wikitext（完整片单+奖项） |
| S2 | https://en.wikipedia.org/wiki/Brokeback_Mountain | 维基 API | 125KB（含李安 DGA 2010 引语） |
| S3 | https://en.wikipedia.org/wiki/Lust,_Caution | 维基 API | 48KB（infobox 摄影署名+金马提名） |
| S4 | https://en.wikipedia.org/wiki/Silence_(2016_film) | 维基 API | 84KB（斯科塞斯作品确认） |
| S5 | https://mande.net/btl/awards/dp-rodrigo-prieto-qa | 直连被 Cloudflare 拦 → r.jina.ai 两次 | 首抓截断（止于 "even more invisible. Th..."）→ **重试得全文 22KB**（三脚架规则/月光戏/胶片选择/客串男妓全在后半段） |
| S6 | https://www.studentfilmmakers.com/a-conversation-with-award-winning-cinematographer-rodrigo-prieto-asc-amc-lust-caution-wins-best-film-and-best-cinematography-at-the-64th-venice-film-festival-by-jacqueline-b-fro/ | 直连 curl | 300KB HTML（色戒长访谈，李安镜头习惯/紫色黄昏/DI 论/掌机看表演） |
| S7 | https://www.focusfeatures.com/article/production_notes___lust__caution | 直连 curl | 197KB（官方制作笔记：killer light/港沪色彩编码/不拍帅梁朝伟） |
| S8 | https://variety.com/2008/scene/awards/rodrigo-prieto-3-1117978325/ | 直连 curl | 563KB（homage to film noir/李安分工论/SNAPSHOT） |
| S9 | https://variety.com/2006/scene/awards/rodrigo-prieto-2-1117935666/ | 直连 curl | 565KB（李安车里打电话/Arricam+Cooke S4/Kodak 5245/5246） |
| S10 | https://www.interviewmagazine.com/film/rodrigo-prieto | 直连 curl | 37KB（读剧本两遍法） |
| S11 | https://colorculture.org/brokeback-mountain-cinematography-analysis/ | 直连 curl | 368KB（二手，chameleon 论，带商业 LUT 推广） |
| S12 | https://en.wikipedia.org/wiki/Life_of_Pi_(film) | 维基 API | 82KB（摄影=Claudio Miranda 查证） |
| S13 | Claudio Miranda 英文维基 | 仅搜索摘要 | 未存档（诚实声明 7） |
| S14 | Sundance Collab 简介 | 仅搜索摘要 | 色戒威尼斯金奥赛拉奖确认 |

## 已验证引语锚（写入卡片的核心英文摘录）

- 李安选人（DGA 2010，维基转引）："I think he's versatile, and I wanted somebody who could shoot quickly [...] he was able to give me the tranquil, almost passive look I wanted for Brokeback. I believe a talent's a talent"
- 断背山视觉方向："He wanted something very serene and limpid—that was his word"；"even more trying to step back and be even more invisible"
- 三脚架规则："there would be no shots with dollies, no handheld, no crane—just tripod. We broke the rule a couple of times."
- 月光戏目标："not get distracted by the lighting but to feel that you are there"；灯光方案 "a light on a crane very far in the distance with a gel to give a slight blue-green tint"
- 三地胶片："50 ASA, daylight balance stock... basically no color filtration... very pristine image"；小镇 250 ASA "a touch grayer"；德州 500 ASA "more saturated. Texas had to have more color"；Variety 器材表 "clean grain let us capture the transparency of the air"
- 李安分工论（色戒）："He'll choose a lens and angle and camera movement that will enhance what he has to say. My involvement has more to do with lighting and film stock and filters and that type of texture than with the grammar of the film language."
- 李安镜头习惯："master shot with a 27mm; a 25 is too wide angle, medium shots will be 50mm, close ups 75mm"
- 黑色电影自述："It's sort of a homage to film noir, but we wanted it to be our own version of it... Instead of using hard lights and shadows, we used bigger, softer sources."
- killer light："a flickering amber glow in his eyes, reminiscent of the glow of the red-hot embers of a poker used to burn people... It added a touch of insanity to Tony's gaze."
- 不拍帅："In the past, when I worked with Tony, it was always about making him look handsome. On Lust, Caution, for the first time, it was not about that."
- 港沪色彩编码："we wanted a film noir look, yet realistic... what she's doing in Shanghai is as real as it gets"
- 紫色黄昏："there is no DP in the world that will light this huge street with purple light, it's impossible. We have to use this ambient light and make it purple in color grading."
- 断背山无 DI："we did not do a DI, because Ang was skeptical of DI's"
- 掌机看表演："it's to see the performance... Several times I have cried on camera"

## 简报归属勘误（三处，写入诚实声明 2）

1. 《少年派》(2012)：摄影=Claudio Miranda（凭此获奥斯卡），普列托未参与 → 人物主条目完整片单无此片 + S12 交叉。
2. 《沉默》(2016)：斯科塞斯作品（普列托摄影），非李安 → S1 片单 + S4。
3. 《爱情与灵药》(2010)：不在普列托片单，无证据 → S1。
修正表述：「李安好莱坞时期两部作品（断背山/色戒）的摄影」，不用「御用」。

## 本轮验证的新技巧（已补入 SKILL.md 正文）

1. **引号归一化批量验证**：corpus 与检查串统一 replace 弯引号（U+2018/2019/201C/201D）+ em dash + lower() 后再 in 匹配——73 条摘录一次跑完，7 条首验假 MISS 全为弯引号变体，归一后 0 MISS。
2. **r.jina.ai 截断重试**：mande 首抓截断，同 URL 重试（--max-time 90）得全文——截断是渲染波动，先重试再放弃。
3. **维基 API 批量+429**：en API 循环连发 429；间隔 5-8s 降速重试可过；redirects=1 自动跟重定向；missing 字段快速终结标题试错。

## 未取到（如实声明）

- theasc.com《断背山》(2006-01)/《色戒》(2007-10) 原文（订阅制）
- 中文维基无普列托独立条目（兩個中文名变体均查无）
- Claudio Miranda 条目全文（仅搜索摘要）
- ASC 2011 色戒视频访谈（无文字转录）
- filmlifestyle.com 摘要与维基奖项冲突（声称「获奥斯卡」vs 4 次提名）→ 判定不可靠来源弃用
