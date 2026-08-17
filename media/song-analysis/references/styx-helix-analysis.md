# 示例：STYX HELIX 完整分解（Re:Zero ED1）

> 2026-08-13 实战产出。用作 song-analysis 工作流的完整范例——展示证据链、分歧处理、输出格式。

## 基本信息

- 出处：TV 动画《Re:ゼロから始める異世界生活》ED1，2016-05-25 发行，MYTH & ROID
- BPM 123，4/4 拍，全长 4:50（SongBPM 与 SongData.io 一致；Gemtracks 报 122 为近似）
- 作词·作曲署名 MYTH & ROID（U-FRET 谱面；实际制作核心为 Tom-H@ck 编曲/hotaru 作词，公开署名以 MYTH & ROID 为准）
- 注：BEMANI wiki 的「STYX HELIX (Digi-Rock Remix)」BPM 128 是官方 Remix 版，非原曲数据，勿混用

## 调性判定：B 小调（B minor）

证据链（U-FRET 和弦谱，人耳转录）：
1. **乐句落点**：全曲乐句几乎全部收在 Bm——每遍副歌收束「Re:start」都回到 Bm
2. **属和弦**：F#7（V7）反复解决到 Bm，F#7 的 D# 是和声小调导音
3. **音阶归属**：G（bIII）、A（IV）均在 B 自然小调音阶（B C# D E F# G A）内
4. **排除相对大调 D 大调**：乐句不落 D，且 F#7→Bm 的属主解决是 i 调特征

⚠️ 机器检测分歧（诚实标注）：SongData.io 报 D♭ minor（Camelot 12A）、SongBPM 报 A major——两源互相矛盾且均与谱面不符。原因：这首歌半音进行/借用和弦密集（间奏下行低音线、A#→C→D 上行），频谱 key 检测器被带偏。**以和弦谱为准**。

## 和弦功能骨架

- 支柱循环：**Bm – G – A**（i – bIII – IV），日本流行乐小调王道进行
- 副歌变体：Bm – G – A – F#m7（i – bIII – IV – v）

## 曲式结构

| 段落 | 内容 | 和声特征 |
|---|---|---|
| Intro | 钢琴/弦乐铺底 | Bm 主和弦悬置 |
| A1（英语主歌） | "Oh please don't let me die / Ready for your touch" | G–A–Bm–A 循环 |
| B段（日语） | 「眩む時計 刻む命…」 | G–A–Bm，F#m7 |
| 段尾连接 | 「消えてしまうの？」 | Bm→A#→C→D 低音半音上行 |
| 副歌 | "don't let me die… / 君を砕くこの悲しみが…" | G–A–Bm–A / G–A–F#m7–Bm |
| 间奏 | 器乐 | Bm→A#dim→Dm→C#dim→Cm→Bdim→G#m→G7 半音下行低音线 |
| A2 / 副歌2 | 「甘い香り放つ…」 | 同前 |
| 落段 | 「あの日々には戻れない 時は強く悲しく強く」 | G–A–Bm–A 渐弱 |
| 终副歌 | "And we'll die pray for a new day / 消えないで" | 全曲最高张力，G–A–Bm 收束 |

## 招牌手法

1. **间奏半音下行低音线** B–A#–D–C#–C–B–G#–G：低音每步爬向主音，A#dim 是导音减七（Bm 的属功能替代），下行「爬不回 B」的悬置感对应歌词「螺旋/轮回」意象——这句是分析，非硬数据
2. **A#→C→D 半音逼近**：导音 A# 不解决到 B，反而冲到 bII（C）再上 bIII（D），听感「扭曲推进」

## 来源

- U-FRET 和弦谱：https://www.ufret.jp/song.php?data=31619
- SongBPM：https://songbpm.com/@myth-roid/styx-helix （123 BPM / 4:50 / A major——key 判断存疑）
- SongData.io：https://songdata.io/track/3eMSc4SiAVxPWa70ViA6QB （123 BPM / 4:51 / D♭ minor——key 判断存疑）
- Gemtracks：https://www.gemtracks.com/resources/bpm-and-key/view-song.php?song=styx-helix （122 BPM）
- BEMANI wiki（Digi-Rock Remix，BPM 128，非原曲）：https://wiki.bemani.cc/index.php?title=STYX_HELIX_(Digi-Rock_Remix)
