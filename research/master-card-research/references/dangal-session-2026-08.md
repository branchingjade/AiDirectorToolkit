# 范本研习轮·《摔跤吧！爸爸》2026-08-09（体育题材第一轮）

知识库 v2.0「范本研习轮」（产《研习报告》+《技法卡片》，非人物卡片）的来源地图与通道实测。与 master-card 轮共用取证纪律：每条论断带来源编号、摘录 grep 验证、诚实声明（未逐帧看片、双口径、未取到清单）。

## 来源清单（成功 8 / 失败 5）

成功：
- 英文维基 Dangal (2016 film) —— `w/index.php?title=Dangal_(2016_film)&action=raw` 179KB wikitext。单源信息密度最高：Plot/Production/Casting/Filming/Box office/China（含中国成功因素分析）/Impact/Controversies（政治争议、巴基斯坦禁映）全有。
- 中文维基（繁体）「摔跤吧！爸爸」—— 页面 HTML 直抓 952KB（通道见下），剧情摘要比英文维基 Plot 细（含「锁工具室」「五分逆转」「哭著和解」等关键场面），与英文维基并引。
- 英文维基原型三人：Mahavir Singh Phogat（「loosely based on his life」出处）/ Geeta Phogat / Babita Kumari（注意 Babita Phogat 是重定向名，真条目 Babita Kumari）。
- 搜狐自媒体影评（sohu.com/a/724555077_121656712）—— article 标签提取，38KB→12KB clean；自媒体文内导演名有误（「尼特·比汉」），只取观点不采信其事实。
- 《生命时报》lifetimes.cn 教育评论 —— 直连可抓，提供「和全世界对抗」等媒体侧表述。
- yuwenmi 台词页（作文素材站）—— gb2312 编码，gb18030 解码；中文台词二手转述，场景标注常缺失（如「我倒是希望上帝给我一个这样的父亲」无场景说明），引用时标「二手转述」。

失败（2026-08-09 实测，直连与 r.jina.ai 均被拦，r.jina.ai 转发回 Cloudflare「Just a moment」挑战页）：
- 豆瓣 subject 页 + review 单篇（电影条目与影评单页都拦）
- 百度百科词条
- 知乎专栏（只回 650B 壳页）
- 头条号文章
- en.wikiquote.org `Dangal_(film)` action=raw → Wikimedia Error 404（维基语录条目名可能不同，未再试）

## 中文维基 HTML 直抓通道（API 限流时的替代）

`curl -sL "https://zh.wikipedia.org/wiki/<percent-encode 标题>"` 可拿 952KB 完整 HTML，无需 API、无 429。
正文提取：正则取 `<div id="mw-content-text">` 到 `<div id="catlinks"` 之间 → 剥 script/style/nav/footer → 剥标签 → html.unescape → 压空白。
⚠️ 转出文本 infobox 区域逐词拆行（每个词带换行），grep 前必须去全部空白。
⚠️ 简体标题的条目正文可能是繁体（「摔跤吧！爸爸」条目即繁体呈现），检查串用条目实际语言形态。

## 英文维基 action=raw 新坑：重定向到消歧义页

`Dangal_(film)&action=raw` 只回 88B `#REDIRECT [[Dangal]]`，而 [[Dangal]] 是消歧义页（814B，列出 Dangal (2016 film)/Dangal (1977 film)/Dangal (TV channel) 等全部候选）——读消歧义页内容即可拿正确条目名，比 API 搜索省事（API 彼时还在 429 限流）。重定向到人物的（Babita Phogat → Babita Kumari）同理，直接换标题重抓。

## 验证脚本新坑：NFKC 归一化不对称（全批假失败）

corpus 做 `unicodedata.normalize('NFKC', ...)` 而检查串没做 → NFKC 把中文全角标点（，。（））转半角 → 自然写法带全角逗号的中文检查串 49 条 35 条假 MISS（当时以为是来源缺失，实为脚本 bug）。
对策：两侧跑**完全相同**的 norm()（NFKC + 去全部空白），检查串与语料共用同一函数。
修复后 62 条摘录 0 MISS；剩余 11 条首验失败均为技能已知陷阱的再次确认：繁简变体（简体存档配繁体检查串）+ 维基链接包裹（`[[Wrestling weight classes|51 kg weight class]]`，检查串避开链接词取前后片段）。

## 电影侧取证要点（体育/家庭/社会题材轮可复用的事实锚）

- 票房双口径：中文维基 12.9 亿人民币 ≈ 2.16 亿美元（中国，中国票房最高印度电影）；英文维基 716 亿卢比（印度 511+海外 205）及中国开画日 248 万美元。
- 「松散改编」定位原文在原型条目（Mahavir）：loosely based on his life。
- 名场面（婚礼觉醒戏）两个维基剧情摘要均未载——「流传甚广的名场面」也可能无可靠剧情原文来源，诚实声明里标注「低置信/未取证」，不硬写细节。
