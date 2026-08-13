# Suno Craft Playbook

创作流程精华合集（提炼自 NuNaught/suno-songwriting-skill，Apache-2.0）。写作规范全部与主 SKILL.md 一致，这里补细节。

---

## 1. 澄清访谈（新歌/大改/翻译必读）

### 什么时候必须问

新歌、重大改写、带口味决策的翻译/改编、要 Suno-ready 交付物时，**默认先访谈**。只有用户 brief 已显式覆盖所有关键输入才跳过。

**Sketch 模式豁免**：用户明确要"快速草稿/初稿/脑暴/第一版"时，收齐 5 项就出（交付范围、主题/前提、主 genre、歌词人称、禁忌内容），明确标注"这是 sketch"，用户说"定稿/打磨/导出"再回到完整访谈。

### 关键输入（必须显式收集，不许推断）

subject/premise、story angle、lyric perspective（人称）、emotional endpoint、primary genre、vocal identity、vocal style、target duration、section structure、required content（含确认无）、forbidden content（含确认无）。Suno-ready 还要 BPM/tempo feel、key/mode。

### 访谈节奏

- 每轮最多 5 个问题，**每题只问一个类别**（不许"118 BPM 小调全 pop 结构气声女中音"这种打包题）
- 每问带 2-4 个建议答案 + 每个答案解释会改变什么，前缀 a) b) c) d)，末尾留 "Let's Brainstorm" 选项
- 每轮开头给紧凑状态块：

```markdown
Intake so far:
- Collected: ...
- Still needed: ...
- Low-impact details I can infer later: ...
```

### 关键输入审核关卡（出词前必经）

写歌词/style prompt 前，先给两组紧凑审查：

```markdown
Critical inputs to review:
- User decisions: ...
- Best-judgment decisions: ...
```

末尾直接确认："Reply 'approved' to generate, or tell me what to change." 审查通过前不许同一条回复里带歌词/标题/style prompt。

### 常见失败模式

- 用户只给主题/genre/情绪就开写完整四件套
- 一个问题得到部分答案后就继续，vocal identity 还未知
- 人称、vocal identity、vocal style 三者混为一谈
- 假设全藏心里不展示 intake snapshot

### 长度启发式（用户没给时长时的默认量）

- 30-60s：hook-first demo，8-16 行
- 1-2 min：紧凑歌，16-28 行
- 2-3 min：标准全曲（默认），28-48 行
- 3-4 min：扩展全曲，40-64 行
- 4+ min：叙事/舞曲/前卫/影视向，加段落须服务概念

---

## 2. Style Prompt 公式

### 默认公式（简单/短 prompt）

```
signature sound or style, primary genre, BPM, key, support styles, vocal identity, instrumental roles, lyric premise, production texture
```

例：`glass-bright acoustic hook, modern indie folk, 92 BPM, G major, subtle chamber-pop support, warm alto lead, fingerpicked guitar carries pulse, cello swells answer choruses, lyrics about choosing hope after loss, organic close-room production`

### 扩展公式（高控制/rich brief）

```
[genre stack]. [emotional/lyric frame] with [vocal identity + vocal style + vocal trajectory]. [instrument and sound palette]. [production texture]. [arrangement arc and section behavior]. [lyric premise]. [duration].
```

### 长度与顺序

- 紧凑 prompt：20-55 词；rich prompt：55-95 词
- 最重要的放最前（signature sound / genre anchor / vocal identity / production texture / lyric premise 谁最定义结果谁在前）
- BPM 和 key 紧跟 genre；主 genre 在 support 前；人声在乐器前（除非 riff/groove 主导）
- duration 放最后
- BPM/key 没给时选一个符合 genre+mood 的合理值，别省略
- 乐器用角色描述："guitar carries pulse"、"808 anchors chorus"、"strings answer vocal"，不只列乐器名

### 组件顺序（rich prompt 参考）

1. genre stack（主 genre 先，fusion 前先给 anchor）
2. emotional/narrative frame（音乐在讲什么情绪，不是话题）
3. vocal identity（歌手配置/音域/合声/合成或自然）
4. vocal style + trajectory（唱法如何随歌曲变化）
5. instrument/sound palette
6. production space（raw/glossy/organic/cinematic、宽度、混响、失真）
7. arrangement motion（build/drop/breakdown/climax/outro 能量路径）
8. lyric frame（一句话前提/说话人/意象域）
9. duration

### 避免

- 不兼容 genre 长清单
- 无音乐含义的抽象形容词
- 用户没要求就写 negative prompt
- 把 lyrics 已有细节全部重复
- 把 rich brief 压成泛泛 20 词
- 人声有 arc 却压成静态标签
- 只列乐器无 production/motion/情绪上下文

### 变体生成

换**音乐前提**（acoustic/intimate、glossy pop、darker cinematic、dance/club、live band、retro era），不许只换形容词。

---

## 3. 人声方向（Vocal Direction）

强人声 prompt ≠ "male singer" / "soulful voice"。是一组坐标：range、tessitura、weight、timbre、phonation、register behavior、vibrato、ornamentation、diction、rhythmic feel、emotional stance、production texture、section-by-section movement。

### 坐标工作流

1. 提取用户约束（歌手身份、genre、情绪、语言、era、禁项）
2. 填核心维度，**只挑 5-8 个**写进 prompt，挑最影响结果的
3. 化解矛盾：如"气声亲密 stadium 高音"→ 拆段：verse 气声、chorus 开嗓 belt
4. 人声居中时放 prompt 靠前

### 紧凑人声短语模板

```
[vocal role], [range/tessitura], [vocal weight], [timbre], [phonation], [register behavior], [vibrato/ornamentation], [articulation/diction], [rhythmic feel], [emotional stance], [production texture], [movement behavior]
```

例：`smoky alto, low-set tessitura, breathy close-mic phonation, delayed vibrato, soft consonants, behind-the-beat phrasing, haunted confessional tone`

### 轻量短语库（普通需求直接用）

- `smoky alto, close-mic delivery, soft consonants, delayed vibrato`
- `bright tenor, clean pop diction, smooth mix voice, polished harmonies`
- `warm baritone storyteller, relaxed phrasing, light rasp, intimate room`
- `gospel-soul lead, open-throat chorus lift, melismatic touches, choir responses`
- `indie-folk duet, conversational delivery, natural harmonies, minimal processing`
- `rap lead, crisp consonants, confident pocket, sparse ad-libs`
- `chamber soprano, clear head voice, restrained vibrato, reverent tone`
- `rock mezzo, controlled grit, chesty chorus lift, live-band presence`

### 常用维度值速查

- **Timbre**: bright/dark/smoky/metallic/glassy/woody/nasal/airy/velvet/honeyed/raspy
- **Phonation**: breathy/clear/pressed/speech-like/creaky/growled/distorted
- **Register**: chest-dominant/mix-dominant/head-dominant/falsetto-forward/break-embracing/seamless
- **Vibrato**: straight-tone/narrow fast/wide slow/delayed/dramatic
- **Ornamentation**: none/scoops/slides/melisma/mordents/cries/blues bends
- **Phrasing**: legato/clipped/behind-the-beat/ahead-of-the-beat/rubato/conversational/chant-like/syncopated
- **Ensemble role**: solo lead/call-and-response leader/choir anchor/harmony stack/duet-like self-response/narrator/gang vocal leader
- **Dynamic shape**: flat intimate/terrace dynamics/slow crescendo/sudden burst/final surge/decrescendo after peak

### 守则

- 艺人引用 → 转成坐标（era+genre lane、vocal delivery、instrumentation、groove、production texture、emotional tone），不写艺人名
- 原创人声身份不得模仿真实歌手
- accent/dialect 只做宽泛 diction 描述，禁 caricature/种族刻板
- 歌词里只用 section 标签承载表演 cue，全局人声坐标放 style prompt

---

## 4. 标签嵌合硬规则

**歌词里每个括号标签都必须是 section 标签**；所有表演/运动/编曲 cue 嵌进 section 标签内部，不许独立成行或内联进歌词行：

- ✅ `[Verse 1 - Whispered]`、`[Pre-Chorus - Rising Tension]`、`[Chorus - Big Chorus, Group Response]`、`[Outro - Afterglow]`
- ❌ 独立行 `[Whispered]`、内联 `[spoken]` 放歌词句中

### 克制规则

- 大部分完整歌曲：标准 section 标签 + **4-8 个** enriched cues
- 用运动 cue 时每 section 1-2 个
- 不要给每个声部纹理都打标签——全局人声方向交给 style prompt
- 优先在结构关键处打：intro、pre-chorus lift、第一段 chorus payoff、bridge/breakdown 对比、final chorus、outro
- 生成忽略标签 → 简化，不是加更多
- 不用生僻/自造标签，除非用户要实验

### 运动/能量标签族（嵌进 section 用）

- Energy: `[Slow Build]` `[Rising Tension]` `[Release]` `[Final Surge]` `[Afterglow]`
- Pulse: `[Free Time]` `[Rubato Entrance]` `[Pulse Emerges]` `[Locked Groove]` `[Half-Time Shift]` `[Double-Time Lift]`
- Texture: `[Drone Bed]` `[Sparse Percussion]` `[Full Rhythm Section]` `[Layered Harmonies]` `[Ostinato Bed]` `[Noise Wash]`
- Vocal: `[Spoken Intro]` `[Chanted Hook]` `[Melismatic Lift]` `[Group Response]` `[Harmony Stack]`

### 结构模板（嵌 cue 示例）

Pop：`[Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Pre-Chorus] [Chorus] [Bridge] [Final Chorus] [Outro]`
EDM：`[Verse] [Pre-Chorus] [Build] [Drop] [Verse 2] [Build] [Drop] [Bridge] [Final Drop]`
Rap：`[Intro] [Verse 1] [Hook] [Verse 2] [Hook] [Bridge] [Final Hook]`

---

## 5. 翻译/多语言

优先级：意义与情绪弧 > 目标语言自然措辞 > 可唱节奏与重音 > 押韵/音韵 cohesion > 逐字忠实。

- 配既有旋律：近似保留音节数，重音词放强拍
- 全新外语歌词：意译习语，不逐字直译
- 双语歌：决定哪门语言占 hook、哪门承担叙事细节
- 常见双语模式：英文 verse + 西班牙语 chorus（hook 强调）；母语 verse + 英文 post-chorus chant；双语 duet 对位；句内 code-switching
- 括号 section 标签默认保持英文
- 防机器翻译腔、防为押韵硬造别扭句法、用目标语言文化自然的意象

---

## 6. 艺人引用转换（copyright-safe）

用户点名艺人时提取：era+genre lane、vocal delivery、instrumentation、groove、production texture、emotional tone，写成具体 style/vocal/production 描述符。禁止直接写艺人名/歌名/专辑名。
