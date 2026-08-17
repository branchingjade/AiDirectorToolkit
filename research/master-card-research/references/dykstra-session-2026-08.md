# John Dykstra 研习轮记录（视效轴·星战/运动控制轮，2026-08-09）

任务：产出《戴克斯特拉_制作大师卡片.md》（v2 大师卡轮），产出物在 `_work/v2-大师卡-20260809/戴克斯特拉/`。视效轴既有轮次：Letteri（维塔系）、Muren（ILM 系数字）、Harryhausen（定格/实体）——本轮=星战运动控制/实体微缩补位。

## 来源 URL 清单（12 存档，15 文件）

| 编号 | 文件 | URL | 通道 |
|---|---|---|---|
| S1 | dykstra_wiki_wikitext.txt | en.wikipedia.org API `John Dykstra` | API raw |
| S2 | dykstraflex_wiki_wikitext.txt | API `Dykstraflex` | API raw |
| S3 | dykstra_asc1977.txt | theasc.com/magazine/starwars/articles/starwars/mm/（Wayback `2020id_`，帧页面 pg1-4） | **帧页面逐帧** |
| S4 | dykstra_cnet.txt | cnet.com/culture/john-dykstra-star-wars-anniversary... | 直连 curl |
| S5 | dykstra_awn_spiderman2.txt | awn.com/vfxworld/spider-man-2-conversation-visual-effects-guru-john-dykstra | 直连 curl |
| S6 | dykstra_vfxvoice.txt | vfxvoice.com/pivotal-technology-how-the-dykstraflex-tranformed-the-vfx-industry-and-movies/ | 直连 curl |
| S7 | dykstra_lucasfilm_dykstraflex.txt | lucasfilm.com/news/lucasfilm-originals-the-dykstraflex/ | 直连 curl |
| S8 | dykstra_theforce.txt | theforce.net/episode2/story/Interview_with_John_Dykstra_63312.asp | 直连 curl |
| S9 | dykstra_denofgeek.txt | denofgeek.com/movies/the-den-of-geek-interview-john-dykstra/ | 直连 curl |
| S10 | spiderman2002_wiki_wikitext.txt | API `Spider-Man (2002 film)` | API raw |
| S11 | spiderman2_wiki_wikitext.txt | API `Spider-Man 2` | API raw |
| S12 | ilm_wiki_wikitext.txt | API `Industrial Light & Magic` | API raw |

通道实测：r.jina.ai 全批 Cloudflare 挑战页（5.9KB "Just a moment"）→ 直连 curl 全通（cnet 297KB/awn 87KB/lucasfilm 68KB/vfxvoice 161KB/theforce 56KB）；维基 API 循环连发一次 429 后重试成功；ASC 原站直连 228B sgcaptcha 挑战 → Wayback `2020id_` 帧页面（542B frameset）→ 解析 `<frame src>` 逐帧抓 pg1-4 全文。

## 已验证引语锚（82 条检查串：70 归一化直接命中 + 12 人工回查确认，全部真实存在）

- **ASC 1977 亲撰（S3）**："In June of 1975, I was contacted by George Lucas and Gary Kurtz"（drop cap 残留 "I n"）；"In the entire film there are some 365 miniature and photographic effects shots"；"In eight months we brought the facility in Van Nuys, California, from an empty warehouse to an incredibly versatile system"；"the horizontal 8-perf 35mm format similar to VistaVision"；"seven axes of motion"；"The shattering nature of the foam allowed us to use much smaller, slower-burning explosive charge… both contributing to the scale of the explosion"；"came from a cut Battle Sequence, made up of excerpts from war movies"；"the appearance is that of real time photography"；"in-house system would be the only way that consistency of quality and control"
- **CNET 2017（S4）**："Youth and ignorance"；"We borrowed technology from everywhere"；"Computers at that time were the size of several refrigerators and had the power of a calculator"；"It was knobs and buttons"；"One of the most difficult things to do is to light a miniature in a way that makes it look real"；"The process in a weird way informed the story in those days"；"You had to pare down your enthusiasm for exceptional images to what you could achieve"；"an embarrassment of riches"；"The process was as much the reward for us as the final product"
- **AWN 蜘蛛侠2 2004（S5）**："a sense of the reality of the situation"；"take you from the guy-next-door world into his superhero world"；"Spider-Cam to photograph the real world"；"One of the interesting things about film is it's an incredibly dense medium"；"the key to this film is a verisimilitude… There's something that comes from photographing real things"；"There were mechanical tentacles wherever the character had to come into intimate contact with them… it was done with a puppet"；"The CGI tentacles took over from that point on"；"we used very little motion capture for our Spider-Man character"；"Water is difficult because it doesn't scale worth a damn"；"being an engineer to being more of a designer"
- **VFX Voice 2026（S6）**："People have subliminal survival systems"；"That is what the Dykstraflex was involved in, to get all the subtle cues you have in real life"；"The key was to figure out a way to integrate the motion of the camera in multiple axes"；"To move with acceleration with the motion control system was something no other system could do"；Knoll："The D-Flex was a real revolution"；"Even though we used the miniature for only 16 shots, they made all the other shots look better"；"We can get a look with a miniature physical object and lighting that's surprisingly hard to do with computer graphics"；"Of the 800 people who viewed the simulation, many refused to believe that models were used"；Muren："John [Dykstra] must have recognized that we needed to be able to slow things down and speed them up"；Morris："It was a transitional link between the photochemical and mechanical technologies"
- **TheForce/AICN 2003（S8）**："Each movie is a composite"；"free association employment"；"much more a story about this character and much less a story about a world"（mojibake：It?s / I?d / wasn?t / the? STAR WARS）
- **Den of Geek 2008（S9）**："we didn't build a company – we built a solution to a problem"；"TTL logic and there was no CPU to speak of in it"；"I prefer the idea of going into something with challenges"；"you simply can never complete the composite because you always scratch an element"；"I don't think George wanted me up there"；"had been a total flop, it still would have been a raging success for us"（原文 `[Star Wars]` 方括号内带换行）；"seven or eight suppositions or hypotheses that had to prove right"
- **片目维基**（S10）："He convinced Raimi to use computer-generated imagery (CGI) for many of the physically impossible stunts"；"none of the shots were 100% computer-generated"；"ballet in the sky"；（S11）："using the real versions was always preferred to save money"；"each scene was always filmed first with Edge FX's creations to see if CGI was truly necessary"；"The CGI versions were scanned straight from the real ones"；"make the weakest shot of the second movie look as good as the best shot of the first movie"；"four foam rubber tentacles"

## 本轮新增验证陷阱（已回写 SKILL.md 第 5 步）

1. **wikitext 自闭合 ref 陷阱**：`<ref[^>]*>.*?</ref>`（re.S）把 `<ref name="eight"/>` 当开标签、吞到下一个真 `</ref>`，误删正文→S10/S11 共 4 条假 MISS。对策：先剥 `<ref[^>]*/>` 再剥成对 ref；或 MISS 时回查原始文件 find()。
2. **转录站撇号 mojibake `?`**：TheForce.Net 等把 `'` 转成 `?`，归一化需清 `?` 或片段避开撇号。
3. **旧杂志 drop cap 残留**："In" → "I n"，引文取避开残留的子串 + 诚实声明注明校正。
4. wayback availability API 连发 429 → 不等预检直接 `web/2020id_/` 试抓。
5. 帧页面逐帧抓取超出正文页数会得 Wayback 脚本页（头部 `Wayback Machine /* @licstart`，~35KB），判据看头部。

## 卡片要点锚（供后续轮次参照）

- 专业签名：先造系统再造镜头；实体为基底+运动控制为语法+观众潜意识物理校验。
- 拆解一：ILM 创立（1975.6 Lucas 约谈/Trumbull 推荐/Van Nuys 仓库 8 个月/365 镜头/八部门分工）；Dykstraflex（第一个数字运动控制摄影系统/七轴/加速度独门/硬连线 TTL 无 CPU/28 层光学合成/二战空战素材定镜头/泡沫爆炸=尺度语言）；与 Lucas 冲突双口径（维基解职说 [Citation needed] vs Dykstra "I don't think George wanted me up there"）。
- 拆解二：蜘蛛侠 1/2——Spider-Cam 真拍纽约（4000 英尺/22 层到离地 1 英尺）；无 100% CG 镜头；章鱼博士触手实体法则（接触戏木偶/中近景实体远景 CG/CG 从实体扫描/先拍实体版再判 CG）；几乎不用动捕；码头 CG 水"doesn't scale"；面具角色肢体语言。
- 可复用对接（国风志怪）：接触戏实体锚点/巨物尺度缩比/运动模糊即真实/面具无面妖肢体表演/约束催生创意/多层合成信息密度。
