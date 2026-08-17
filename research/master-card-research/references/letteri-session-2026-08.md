# Joe Letteri 研习轮记录（视效轴·第一轮，2026-08-09）

产出：《莱特里_制作大师卡片.md》于 `_work/v2-大师卡-20260809/莱特里/`。任务预设四大重点（维塔数码/咕噜/阿凡达/金刚）全部覆盖，无简报归属勘误（本轮简报本身准确）。

## 视效宗师来源地图（VFX 轴，本类任务可复用）

1. **维塔官网官方文案=准一手金矿**：`wetafx.co.nz/films/filmography/<片名>` 的影片页直接给官方定义句（King Kong 页："Kong is a CG title character who delivers a very complex performance without the aide of dialogue... around four million hairs"；Avatar 页："computer generated filmmaking had reached the point where it could carry the story, and maintain suspension of disbelief, through an entire movie"）。⚠️ **全站 Next.js JS 渲染**——bs4 提取只剩 158B，必须用「关键词窗口法」（见 SKILL.md 来源技巧）或直接 grep 原始 HTML。
2. **行业工会杂志 VFX Voice（vfxvoice.com）人物综述=一手自述金矿**：VES Georges Méliès 奖得主综述文（Naomi Goldman 采写）含大段本人自述（"Gollum was a breakthrough..." 突破论、"I don't draw, I don't paint..." 数字图像论、Muren 师承段、侏罗纪着色器段）。检索式：`vfxvoice.com <人名> <奖项名>`。直连 curl 可抓。
3. **奖项季访谈站**：Gold Derby（`goldderby.com/feature/<人名>-<片名>-vfx-interview-<id>`）与 IndieWire 的 VFX 主管访谈是常规一手源（含代际技术细节："The first Avatar utilized the same system that Weta had developed for Gollum"、APFSA 取代 FACS）。两站均为 WordPress/JS 混合，直连 curl 可抓，正文用关键词窗口法读。
4. **fxguide（fxguide.com）技术长文**：APFS 面部管线专文（`fxfeatured/exclusive-joe-letteri-discusses-weta-fxs-new-facial-pipeline-on-avatar-2/`）含 178 肌肉纤维曲线、jaw 主控引语。fxguide 直连 curl 可抓。
5. **内部人第一人称回忆=一手内部视角**：AWN《Gollum and Me: My Precious Experience》（Bay Raitt，咕噜首席模型师）给管线工业化引语（5pm 发布/次日晨 dailies/100+ shots）与「视效隐身论」——比本人自述更能证明组织级手法。
6. **电影维基条目 Production 段/公司维基条目**：Wētā FX 条目（action=raw，64KB）给公司史=人物史（1993 创立《罪孽天使》、2001 Letteri 加入、2021 Unity 16.25 亿美元收购工具部门更名 Weta FX、Avatar: Fire and Ash 3,132 镜头/12.48 亿渲染小时）。
7. **二手转引站**：alleycatscratch.com 等老站整段转引 Letteri 原话（Kong 情感状态面部系统）——可用但必须标「二手转引，原出处未取到」。

## 已验证引语锚（46 条卡片侧 0 MISS，本轮全过）

- VFX Voice：Gollum 突破论全文、subsurface scattering 首次、数字角色哲学、数字图像论、"always referring back to 'how does this thing happen in the real world'"（Muren 师承）、Star Trek VI 首镜实拍做不出
- Awards Daily 2013 Hobbit 访谈：Gollum 时期动捕实验（"weren't sure how much of it was Andy [Serkis]..."）、Hobbit 首场动捕戏、"you really have to have a good foundation on the physicality of a scene"
- AWN Bay Raitt：pipeline insane pace、100+ shots、"being invisible"
- Weta 官方页：Kong 无台词复杂表演/400 万毛发/CityBot、Avatar 整片 CG 承载叙事
- alleycat 转引：Kong 情感状态系统、"next generation of the facial system we built for Gollum"
- MovieWeb 2006：加入维塔动机（"I was really interested in working on Gollum"）、"went from Lord of the Rings right into King Kong"
- Gold Derby：Avatar1 rubbery、"We wrote an entirely new facial system based on a neural network"
- IndieWire：虚拟摄像机（"integrated it with Jim's ideas of the virtual camera"）、APFSA 取代 FACS
- fxguide APFS：jaw 主控、"It is basic calculus"、178 muscle fiber curves
- Weta Influencers 文（IndieWire Desowitz 转载，二手）："audiences couldn't tell that it was a CG character"

## 本轮坑（已回写 SKILL.md）

- JS 渲染型官网正文提取失败→关键词窗口法（来源技巧新条目）
- 维基管道链接贪婪正则 bug + norm 缺 HTML 标签剥除→10 条假 MISS（验证陷阱新条目）
- r.jina.ai 全批 Cloudflare 挑战页→直连 curl 一轮 9/9 成功（既有兜底链再验证）

## 双口径与诚实声明要点

- 奥斯卡 6 座（enwiki 2026 口径）vs VFX Voice 2018 写 4 座；VES 6（VFX Voice）vs 4（enwiki）——按时间口径分别标注
- 中文维基无 Joe Letteri 条目（API missing）、百度百科「乔·莱特里」安全验证拦截（2.5KB）——中文源未取到
- 原文笔误照录：VFX Voice "Randall Brodsky"（疑 Mandelbrot 之误）、Gold Derby "capture the actors which a stereo camera rig"（疑 with）——不擅自修正，声明里注明
- 未取到：alleycat 转引原出处、2009 阿凡达制作期 fxguide 长文（以官方页+Gold Derby 覆盖）

## 存档 URL 清单（pages/，13 文件）

enwiki raw（Joe Letteri/Wētā FX）、vfxvoice.com Georges Méliès 综述、awardsdaily.com 2013 Hobbit 访谈、awn.com Gollum and Me、wetafx.co.nz（films/filmography/king-kong、/avatar、articles/influencers-joe-letteri）、movieweb.com 2006 Kong 访谈、alleycatscratch.com Kong 2005、goldderby.com Way of Water、indiewire.com Way of Water 专访、fxguide.com APFS 专文。
