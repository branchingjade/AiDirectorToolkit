# 配乐大师研习轮·日本动漫剧伴轴（泽野弘之 2026-08）

产出：`research_arrangement/泽野弘之.md`（动漫风 OP 制作场景，研习卡结构：定位/编曲实证拆解/创作观/可复用技法/来源清单/诚实声明）。

## 动漫配乐轴核心铁律：主题歌 vs 剧伴署名核查
任务预设的「某动画的音乐=某作曲家」几乎必然混入主题歌（OP/ED）归属——**剧伴（BGM）与主题歌经常不是同一人**。本轮简报预设 3 处全错：
- 《紅蓮の弓矢》（进击的巨人 OP1）= Revo（Linked Horizon）词曲编，泽野只负责剧伴
- 《My Dearest》（罪恶王冠 OP1）= ryo（supercell）
- 《葬送的芙莉莲》配乐 = Evan Call（泽野日文维基作品表全文 grep「フリーレン」= -1 即证）
验证路径：①人物维基作品表（日文维基 discography「音楽担当作品」段）没有该片=高度可疑；②主题歌查歌ネット（uta-net.com）词曲编署名；③拆解改用**人物本人的剧伴人声曲/插入歌**（aLIEz/Call your name/βios 等）。勘误写入卡片诚实声明。

## 谱面来源地图（人耳转录和弦谱=拆解硬数据）
- **U-FRET 全流程（实测可靠）**：站内搜索 URL 不生效 → `web_search "ufret.jp <歌名>"` 拿 `song.php?data=<ID>` 直链 → browser_exec 打开读 `document.body.innerText` 一次拿全（和弦+歌词+作詞/作曲署名+Capo）。艺术家页 `artist.php?data=<URL编码名>` 列出该名下全部曲目（顺带确认"某曲没有谱"）。谱页署名可作词曲归属弱证据
- **chord-rinne.jp（リンネのコードブック）**：`scode.php?id=<ID>` curl 直连可抓，页面标「原曲BPM」（谱面实证级 BPM，可作第三源）；⚠️ 和弦本体 JS 渲染（innerText 只有歌词+BPM）→ 和弦标「未验证」；⚠️ 署名偶误（βios 标「作詞作曲: 澤野弘之」实为作词 Rie），一律与歌ネット交叉
- **Chordify**：机器检测可作调性弱证据（βios → C 小调系），标「机器检测」入诚实声明
- **音龍 -$Ound Dr@Gon-**（hiroyukisawano-fansite.com）：泽野粉丝站，OST 页常转引泽野自述轶事（βios 副歌=医龍1 弃稿）——「fansite 转引自述」层级引用
- BPM 站（songbpm 搜索页/songdata.io）2026-08 起全反爬/JS 渲染——BPM 从 chord-rinne 谱面取，取不到标「未验证」，不反复重试

## 曲式拆解纪律（动漫 OP 卡）
- 曲式表用**相对结构**（Intro/主歌/导歌/副歌/落段/Outro），不编秒数；每段标和声特征+能量级
- 和弦标注功能级（i/bIII/bVI/bVII/v/V）便于跨曲比对；副歌低音下行线（i-bVII-bVI-v）、sus4 蓄力解决、关系大小调暧昧（bIII-i 交替）是动漫史诗曲高频手法
- 配器分层写「听感」并标注；可复用技法清单面向制作（能量曲线/配器阶梯/主题变奏）

## 一手访谈来源（本轮 5 个全通）
- GIGAZINE 2019（gigazine.net/news/20190526-promare-hiroyuki-sawano-interview/，日语，152KB 直连）——Sawano Drop 起源（「間はアクセントになるな」）、菜单表制作、不看画面作曲，全在此
- Otaku USA 2021 / ANN 2025-11 / Anime Trending 2025-10 / JRockNews 2025-11——英语一手，直连 curl 全通
- outerhaven.net 被 Cloudflare 拦（curl 仅得挑战页）→ 放弃标「未取到」，不引用搜索摘要
- 日文维基 action=raw（161KB）信息密度极高：奖项逐年表（Newtype 剧伴赏 3 连霸等）、134 件音乐担当作品统计、曲名论（转引 natalie）——动漫配乐人轮骨架源

## 引语验证新坑（本轮回扫抓到）
- **日文「」『』直角引号**：转写时省略引号而原文带「」，norm 需剥 `「」『』`（oga-kazuo 轮已记，本轮再验证：`間はアクセントになるな` 原文带「」）
- **日文汉字假名差异是真错误信号**：`開けて` vs 原文 `空けて`（からから）——日语引语回扫时逐字核对，假名/汉字变体要回原文确认，不是一律当假阴性
- 带引号包裹的术语（“[nZk]”）检查串也要带引号，否则假 MISS
