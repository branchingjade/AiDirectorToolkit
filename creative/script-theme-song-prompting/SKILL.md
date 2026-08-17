---
name: script-theme-song-prompting
version: 1.0.0
description: "给影视剧本写主题曲/OP/ED的Suno提示词时用。触发词：主题曲、OP、ED、片尾曲、给剧本写歌。"
---

# 剧本 → 动漫主题曲 Suno 提示词（Script Theme Song Prompting）

用户为影视剧本/动画项目要主题曲、OP、ED、战斗插曲时使用。已完整读过剧本的会话直接采锚点，无需重读；剧本审读流程见 `script-review` skill。

## 参考曲 → 风格提示词工作流（2026-08-13 实战：STYX HELIX 分解）

用户给一首参考曲要求「按这个风格」做 Suno 提示词时，先分解参考曲再写提示词，分解结论要有证据：

1. **调式判定：和弦谱优先于机器检测**。动漫/日曲先走纯 curl 快路线（命令与提取见 `song-analysis` skill 的 `references/chord-sites-curl-routing.md`）：songbpm.com 直 curl 歌曲页拿 BPM/时长 → chordu.com 搜索摘要拿「和弦序列 + key + 半速起练 BPM」→ ultimate-guitar 官方 tab 拿和弦文本，移调版统一转度数互推原调（STYX HELIX 实测：Bm–A–C#m–E，i–VII–ii–IV）。U-FRET（ufret.jp，JS 渲染，browser_exec 读 innerText）→ ChordWiki（Cloudflare 拦）→ J-Total（search.cgi 返回空结果页）为备选/已死路线。机器检测源（SongBPM/SongData.io/Gemtracks）报的 key 常互相矛盾且被半音进行带偏（STYX HELIX 实测：机器报 D♭ minor / A major 互相打架，实际是 B minor）——判定依据：乐句落点主和弦（i）+属和弦（V7 解决）+ bIII/IV 是否在自然小调内。BPM 取多源一致值（123 vs 122 取多数）。
2. **结构分解表**：按和弦谱的歌词分段列出 Intro/Verse/Pre-Chorus/Chorus/间奏/Bridge/Outro 各段的和声特征，招牌手法单独拎出（如半音下行低音线、半音逼近主音）。
3. **转成 Suno Style**：把调性/BPM/乐器/人声/能量曲线翻译进 Style 字段。改燃的常用手段：副歌失真吉他 riff 加倍+双踩底鼓+弦乐铜管齐奏+女声撕裂感+合唱垫底；结构增强用落段 Bridge（炸→静→更炸，终副歌成唯一最高点）。

## 段落情绪双通道定调（用户拍板模式）

用户会逐轮单维度微调（「只调整副歌」「让开头再温柔一点」「更改结构」）——每轮只改被点名的段落，其余保持原样，交付标注【改动点】diff 式列表。最终用户会拍板段落情绪映射（如「[Intro]到[Verse 1]温柔悲伤 / [Pre-Chorus]宿命感 / [Chorus]燃起来」）——此时**情绪写进两处**：Style 字段按段落标注 + 歌词字段结构标签内嵌（`[Verse 1: Soft, Sorrowful]`），双通道强化 Suno 理解。情绪的音乐语言：温柔悲伤=稀疏钢琴+耳语气声；宿命感=半音上行逼近+弦乐长音+钟声+鼓渐入；燃=失真吉他+双踩+铜管+合唱。

## 核心方法

1. **原创项目跳过「查现成 OST」步**（该步只适用于已有作品/改编作品——songwriting-and-ai-music skill §8 第 0 步）。原创剧本直接进创作。
2. **采锚点（从剧本挖）**：
   - **钩子句**：角色标志性台词直接做副歌钩子——「我是堡主，你是欠债人」「条例作废了」这类原话比新写口号更有辨识度，观众一听就想起剧。
   - **情绪锚点**：催泪独白（如「可是我想你了，我也想妈妈了」）→ ED；决战台词（如「给我关机」）→ 战斗曲。
   - **意象**：道具（平底锅/计算器/项圈）、场景（枯石榴树开花）、关系（欠债人→家人）——这些是歌词画面的来源。
3. **按用途分版本，每版独立 Style + 歌词**（不是一版多改）：
   | 用途 | 风格方向 | 典型锚点 |
   |---|---|---|
   | 主 OP | 燃系 J-rock + 交响，快 BPM，女声带态度 | 收编/反收购/打 Boss |
   | 片尾 ED | 抒情 ballad，钢琴+弦乐，脆弱→温暖 | 家庭羁绊/和解/开花 |
   | 日常搞笑曲 | 快节奏搞怪 pop，木管+铜管，chibi 感 | 食堂/搬砖/直播 |
   | 战斗插曲 | 史诗交响金属，爆裂人声+合唱 | 季终决战/绝境翻盘 |
4. **中文歌词铁律**（Suno 发音）：
   - 数字写中文（「八千万」不写 8000万）。
   - **角色名是最高发音失败率**——唱错就换音近写法重投（萧烬→小进）。
   - 结构标签 [Verse]/[Chorus]/[Bridge]/[Outro] 必加，否则 Suno 默认平铺。
   - Style 字段写英文（Suno 更吃英文风格词），歌词写中文，标注 Mandarin vocals。
5. **交付形态**：每版给「Style 字段 + 歌词字段」两块可直接粘进 Custom Mode 的完整提示词，再加一条投喂提示（发音修正策略：人名唱错→音近改写重投）。

## 实战案例（《魔王》中剧 43 集，2026-08）

四版成品钩子句映射表：

| 版本 | 钩子 | 出处 |
|---|---|---|
| OP《我是堡主》 | 「我是堡主，你是欠债人」 | EP1 收编台词 + EP29 收购反收编 |
| ED《石榴树开花了》 | 「枯了二十年，又长出新芽」 | EP40 石榴树开花 + EP35 地下室独白 |
| 搞笑曲《一人五块》 | 「一人五块，吃饱就行」 | EP5 食堂五块钱预算 |
| 战斗曲《给我关机》 | 「给我——关机！」 | EP42 对至高神 |

风格字段可复用模板：

```
OP:  "Anime opening theme, epic J-rock with symphonic orchestra, 170 BPM,
      driving electric guitars and soaring strings, powerful female lead
      vocal with attitude, heroic choir, explosive build, Mandarin vocals"
ED:  "Emotional anime ending theme, tender J-pop ballad, 78 BPM, gentle
      piano and warm strings, soft breathy female vocal, bittersweet hopeful"
搞笑: "Playful comedic anime song, quirky fast pop, bouncy woodwinds and
      brass stabs, 140 BPM, cheerful chibi vibe, group harmonies"
战斗: "Epic cinematic battle anthem, symphonic metal with orchestra, 165 BPM,
      thunderous drums, raw belting female vocal, full choir chanting bridge"
```

完整四版歌词（含 [Intro]/[Verse]/[Chorus] 结构标签）见 2026-08-08 魔王 5.1 剧本审读后会话，可作为模板复用——把钩子句、意象、用途三列替换成新项目即可。

## 用户偏好

- 用户要「多来几版」= 至少 4 版不同用途/风格，不是同一版微调。
- 每版标注用途（OP/ED/日常/战斗）+ 锚点出处（哪集哪句），用户能直接决策投哪版。
- 不要只给一段提示词——完整可投的 Style + 歌词才是交付物。
- **用户会自己写歌词**（「王冠与魔王」是他自写的），agent 的角色是填结构标签+编曲 Style+提示词工程——不要把用户自写的词重写，只逐字填入结构。
- 歌词填入结构标签时：情绪词保留在标签内（`[Verse 1: Soft, Sorrowful]`），无词段（[Intro]/[Instrumental Break]/[Outro]）留白=器乐，Suno 不会加词。
- 中文歌词避开「不是X，是Y」句式（用户 AI 感判定标准，会当场否）。
- **歌词创作质量标准（2026-08-13《魔王》OP《命名天亮》实测，9 轮迭代教训）**：
  - 禁止三类「死法」：①口号化（「我认我护我主」「比神明更硬」=尬，喊口号≠燃）②口语直白（「打完回家吃饭」「站着赢」=小学生作文/土）③角色展示排比（「一人把火烧成白昼/中间的人伸出手/说跟我走」=游戏角色介绍+组队邀请，用户原话「这又是什么狗屎」）
  - 禁止讲故事——歌词是情绪和意象，不是剧情摘要（「钥匙落进掌心/隔壁住着三只怪物」=叙事，被否；用户原话「不要讲故事，我要的是歌曲」）
  - 要求：段内押韵（自然押韵，不为押韵硬造对仗——「神说心是祸/魔说心是错」就是强行对仗的反面教材）；**无主语/无人称代词**（你我他/我们他们全删，动作直接落：「蘸着深渊的墨，把判词改成战书」——用户拍板禁令）；意象从作品内部发明（判词/名字/天亮/战书），不用烂俗意象（「灯」太常见被否，用户追问「为什么是灯呢」）
  - 艺术气息 = 留白不解释：点破不如漏出（「有人把命揉进火焰」不说破是谁；「每跳一下都是一声想你」用具体动作漏出真相）
  - 参照范本 = 用户自己的词《王冠与魔王》：身份意象（「一人是深海咒印/一人是烈火之名」）+ 情感落点（「却对我低声说醒来」）——静态意象 + 关系温度，不是动作展示（把X锻成Y=技能介绍）
  - 意象链闭环是高级形态：《命名天亮》名字链——刻在深渊无人唤 → 神明焚尽名姓 → 满城诵着名姓 → 把名字种成太阳，一首歌讲完「从无名到成光」
- **共创节奏**：风格/BPM/人声/编曲逐项和用户确认，用户说「别着急给我」= 不要抢跑交付最终版，等用户说「汇总」再合盘（连续两轮提前交最终版会惹恼用户）。创作类会话用户要「一起考虑」，先摆选项让他拍板，再动手。
- 歌词迭代三版以上失败：先诊断根因（尬=口号+强行押韵+用力过猛；土=口语+俗套意象；主题不对=挖错了故事层，如挖到父亲真相线但用户要的是并肩逆命；角色展示=介绍人物），不要盲目换写法——停下来确认方向/主题。
- 音域约束会以音乐术语提出（「音高不要到6组」= C6/1046Hz 海豚音区；「不想要特别的高音」= 无高音高潮）——Style 里落成：melody stays in a low-mid range, no high-note climaxes, intensity through weight and grit, not pitch。Suno 默认会飙高音，必须显式约束。
- Style 字段工程化（土味/高级感配方对照、人声去 AI 感、少女感声线、音域约束、1000 字符压缩法、参照曲分析模板）见 `references/suno-style-engineering.md`。
- 提示词/歌词成品直接放聊天框内（纯文本呈现），不包代码块。
- Suno Style 转 ACE Studio 时：ACE 没有 Style 字段，走 Inspire Me 文字描述（把 Style 翻译成完整歌曲描述）+ 手动工程参数（BPM/Chord Track/声库/Vocal Controls/乐器轨/歌词每音符一音节+`-` 连字符 melisma）。
