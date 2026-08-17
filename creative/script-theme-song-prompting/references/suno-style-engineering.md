# Suno Style 字段工程化（2026-08-13《魔王》OP《命名天亮》实测）

用户（影视从业者，审美门槛高）会直接说「编曲太屯了」「我想要高级感」「人声太廉价」「音高不要到6组」——Suno 提示词的土味/廉价感来自配方，以下对照可查。

## 一、土味配方 → 高级感替代（编曲描述）

**土味配方（用户当场否）**：double-kick drum assault + brass in unison + full choir underneath + doubled dense distorted riff = 「土味史诗燃」全套标配，游戏广告/廉价 OP 味。

**高级感五手法**：
1. 晶莹音色：shimmering music-box textures / electric piano（日系高级感 signature，替代普通钢琴+弦乐配置）
2. 琶音合成器流动层：arpeggiated synth, sixteen-note shimmer（主歌就能感到东西在走，不靠鼓也有推进感）
3. 副歌骤停留白：everything drops away for one breath, only the vocal, then drums and strings slam back（高级感大招，比堆乐器高级）
4. 空间感：wide stereo field, lush reverb, airy pad（人声不贴脸，像在空旷大厅唱）
5. 有机弦乐：organic strings（真乐器质感，非 MIDI 塑料味）

克制但不平庸的表述词：clean, transparent, restrained, never cluttered, room to breathe, no instrument pile-up——副歌高潮靠弦乐厚度+鼓推进+人声爆发，不靠乐器轰炸。

## 二、人声去 AI 感

廉价感来源 = 声线描述笼统（powerful female vocal）+ 无「人味」指示。

**加人味关键词**：audible breath / subtle rasp / natural vibrato / emotional cracks / live vocal take feel / natural vocal imperfections / slight rasp at peaks
**禁词**：smooth / polished / perfect（越完美越假）

**少女感声线**（用户拍板方向）：young, clear, transparent, fresh, natural, unaffected——**禁 cute / kawaii / moe / childish**（触发廉价萌音）。少女感来自音色本身，不来自做作。

**音域约束**（用户用音乐术语提：「音高不要到6组」= C6≈1046Hz 海豚音/花腔区；「不想要特别的高音」= 无高音高潮）：
- 落成英文：melody stays in a low-mid range, no high-note climaxes, intensity through weight and grit, not pitch
- Suno 默认会飙高音，必须显式约束；副歌爆发靠力度和撕裂边缘（gritty edge），不靠音高
- 关联：早期版本里的 "octave-high vocals"（终副歌）写法要删，改成 emotional intensity through layered choir/string depth

## 三、1000 字符压缩法（Suno v4.5+ Style 字段上限）

压缩原则：**删修辞冗余，保留全部约束**。约束=定位/BPM/调性/段落行为/音色/人声/音域——一个不能丢。
删：as if in a large empty hall / precise sound design / sixteen-note / slow / comfortable 这类修饰词。
验证：脚本数 `len(text) <= 1000`（实测从 1123 → 996，两轮到位）。

## 四、参照曲分析数据模板（STYX HELIX 实例）

分析参照曲 → 转 Style 的可复用数据：
- 调性：B 小调（和弦谱人耳转录为准：乐句落点 Bm 主和弦 + F#7 属和弦 + bIII=G/IV=A 在自然小调内；机器检测 SongBPM/SongData 互相矛盾不可信）
- BPM：123（SongBPM 与 SongData.io 一致）
- 核心进行：Bm–G–A（i–bIII–IV），副歌变体 Bm–G–A–F#m7
- 招牌手法：间奏半音下行低音线 B–A#–D–C#–C–B–G#–G；副歌前 A#→C→D 半音逼近
- 转 Style 时保持 123 BPM（中速沉稳=宿命悲壮，不调快）；「副歌更燃」靠力度和层次不靠提速
