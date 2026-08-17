---
name: song-analysis
description: 分解歌曲的调式/和弦/曲式结构时用。公开和弦谱定调、BPM 交叉验证、按谱面分段。
version: 1.0.0
author: hermes-curator
license: MIT
tags: [music, analysis, chord, key, song-structure]
---

## When to Use

用户问「分解这首歌」「这首歌什么调/什么和弦进行/曲式怎么走」，或需要为配乐/创作参考分析一首歌时。影视从业者场景：配乐参考、模仿写作、向用户讲清一首歌怎么构成。

# 歌曲分析（调式/和弦/曲式分解）

将一首歌分解为：调性（key）、和弦功能骨架、曲式结构（Intro/主歌/副歌/间奏/落段/终副歌）。用于配乐参考、模仿写作、向用户讲清一首歌怎么构成。**带证据来源下结论**——每项数据挂来源，分析性结论与乐理事实分开标注。

## 核心流程

### ① 抓公开和弦谱（人耳转录谱 = 定调第一依据）

**动漫/日曲纯 curl 快路线（2026-08 实测，优先于此，无需浏览器）**：
- **songbpm.com 服务端渲染可直 curl**：`https://songbpm.com/<artist-slug>/<song-slug>`（无 @ 符号；slug 靠猜：artist 用英文名如 ikimonogakari/lisa/myth-roid，歌 slug 试变体 blue-bird/aoi-tori/gurenge/styx-helix，404 就换）。「Song Metrics」的 dl 区块 = Key / Duration / Tempo (BPM)，正则 `<dt>..</dt><dd>..</dd>` 提取。⚠️ 它的 Key 是机器频谱判定，与谱面常冲突（STYX HELIX 报 A、谱面 Bm）——只采信 BPM/时长
- **chordu.com 搜索摘要即和弦数据**：web_search「chordu <歌名> chords」，结果摘要含「emphasize these chord progressions: <和弦序列>」「key of <调>」「start slowly at <半速> BPM and progress to the original tempo of <实际 BPM>」——和弦序列+调+**半速律动证据**一次拿全；页面本体 HTML 可 curl（完整谱面 JS 加载，但摘要 + HTML 内和弦 token 频次统计够定和弦池）
- **ultimate-guitar.com 官方 tab 可 curl**：和弦文本直接可见（青鸟实测：Cadd9-D-Em / Am7-D-G / Cmaj7-B7-Em / Em7-D-Cadd9-G）；大型 tab 页（400KB+）内嵌 `[ch]和弦[/ch]` 标记，正则可提取分段落（Intro/Chorus/Solo/Bridge 全标）
- **tumblr 制谱博客 = 日曲分段落和弦金矿（2026-08 梶浦轮实测）**：日系歌手常有专门制谱博客（例：kalafina-yk-chords，制谱人同时投稿 UG）——`<blog>.tumblr.com/post/<id>/` 直连 curl 可抓完整分段落和弦（Intro/Verse/Refrain/Chorus/Bridge 全标，适合直接做曲式表）；**双谱互证法**：UG 用户谱 + tumblr 独立转录，段落级和弦一致即采信（to the beginning 两谱在 Am 主歌 / F#m–A 副歌 / 终段 D#m 完全互证）；chordu 机器和弦池（Key+BPM+和弦序列）作弱证据，标注「机器判定」
- **移调互推法**：chordu 给 Gm 版 + UG 给 Em 版 → 统一转度数（i–VI–III–VII）跨源一致即定原调（青鸟实测：→ F♯m–D–A–E）
- U-FRET（ufret.jp）：JS 渲染 curl 拿不到 → browser_exec 读 `document.body.innerText`。**两个实测坑（2026-08 泽野轮）**：①站内搜索 URL（/search?q= 与 /search?word=）不生效，只回热门榜——正确路径：`web_search "ufret.jp <歌名>"` 拿 `song.php?data=<ID>` 直链，或 `artist.php?data=<URL编码艺术家名>` 艺术家页一次性列出该名下全部曲目链接（顺带可知"某曲没有谱"）；②谱页顶部标注「作詞/作曲」署名，**抓谱时顺带核对词曲编归属**（动漫曲「主题歌 vs 剧伴」作者常不同，见 master-card-research 剧伴轴铁律）
- **chord-rinne.jp（リンネのコードブック）备选**：`scode.php?id=<ID>` 直连 curl 可抓，页面标「原曲BPM」（谱面实证级 BPM，可作 BPM 交叉验证第三源）；⚠️ 和弦本体 JS 渲染（innerText 只有歌词+BPM），和弦需浏览器或标「未验证」；⚠️ 页面署名偶有误（βios 标「作詞作曲: 澤野弘之」，实为作词 Rie）——署名一律与歌ネット（uta-net.com）交叉
- 抓不到直接标注「未验证」，别反复重试：ChordWiki（Cloudflare 403）、j-total.net search.cgi（UTF-8/EUC-JP 均返回同一空结果页）、gakufu.gakki.me（超时）、chordify.net（403）、Wayback（无存档）
- 完整命令/提取脚本/站点状态表/已验证三曲数据集：见 `references/chord-sites-curl-routing.md`

### ② 定主调（key）

判据按权重：
1. **乐句落点**：每段（尤其副歌收束/反复句）落在哪个和弦 = 主和弦 i
2. **属和弦**：V7→i 的解决（如 F#7→Bm），V7 里的导音是和声小调特征
3. **音阶归属**：其余和弦（bIII/IV/VI 等）是否都在该调自然音阶内
4. **排除相对大调**：乐句不落相对大调主和弦、且有属→主解决，即判小调

### ③ BPM / 时长交叉验证

- SongBPM（songbpm.com/@artist/song）、SongData.io、Gemtracks 三源交叉；多数一致取之，单源偏离如实标注
- 机器 key 检测（SongData 的 Camelot、SongBPM 的 key）**只作参考**——半音进行/借用和弦多的歌，频谱检测器会被带偏（STYX HELIX 实测：SongData 报 D♭ minor、SongBPM 报 A major，互相矛盾且与谱面 Bm 不符）。与和弦谱矛盾时以谱面为准，诚实标注分歧

### ④ 曲式结构分解

- 按谱面歌词分段：Intro / A1 / B段 / 段尾连接 / 副歌 / 间奏 / A2 / 落段 / 终副歌 / Outro
- 每段标和声特征（支柱循环、半音进行、属和弦处理）
- **不编精确秒数**——没有逐秒证据就给相对结构，或标「约」

### ⑤ 输出格式

- 基本信息（BPM/拍号/时长/署名，带来源）
- 调性判定证据链（判据逐条列出）
- 和弦功能骨架（支柱循环）
- 曲式表（段落 | 内容 | 和声特征）
- 招牌手法 2-3 条：乐理事实 → 听感贴合（标注「这句是分析，非硬数据」）
- 全部来源 URL 列出

## 调性判定速查

- 主和弦 = 出现频率最高 + 乐句落点（不是第一个和弦）
- 小调识别：i–bIII–IV 循环（如 Bm–G–A）、i–bVI–bVII、属和弦 V7 的导音强牵引
- 间奏半音下行低音线（クリシェ，如 B–A#–D–C#–C–B–G#–G）= 低音每步逼近主音，常见于 J-Pop 间奏，**不是调性偏移**
- 低音半音逼近（如 A#→C→D）：导音不解决到主音反而上冲 bII/bIII，听感「扭曲推进」，动画 ED 常用

## Pitfalls

- U-FRET 页面「Capo 2 ★簡単弾き」是简易版建议，**不是原调**（谱面和弦已是原曲キー）
- 机器 key 检测互相矛盾时别硬取一个——以人耳转录和弦谱为准
- 日本流行乐小调套路：i–bIII–IV 循环 + 属和弦 V7 牵引
- 结论里区分「乐理事实」（谱面可证）与「听感解读」（创作意图）——后者明说「这是分析」

## 参考示例

- `references/styx-helix-analysis.md`：STYX HELIX（Re:Zero ED1）完整分解——B 小调判定全流程 + 半音下行间奏 + i–bIII–IV 骨架
- `references/chord-sites-curl-routing.md`：纯 curl 和弦数据源路由——songbpm/chordu/UG 抓取命令与提取正则、各站点封禁状态表、移调互推法、已验证三曲数据集（青鸟/红莲华/STYX HELIX）
- `templates/anime-op-breakdown-card.md`：编曲拆解卡模板（基本参数/曲式能量表/配器进出表/招牌手法/能量曲线/Suno Style 翻译）——Suno 动漫风主题曲创作场景直接套用
