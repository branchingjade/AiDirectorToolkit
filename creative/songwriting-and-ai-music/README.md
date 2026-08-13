# Songwriting & AI Music（v2.0）使用手册

给 Suno AI 写歌的完整手艺包：**歌词 + Style 提示词 + 人声设计 + 标签规范**。v2.0 起从"能写出东西"升级为"系统级创作流程"（合入 NuNaught/suno-songwriting-skill 方法论精华）。

## 什么时候用（自动触发）

以下请求会自动加载本 skill，无需手动指定：

- 「写首歌」「写歌词」「给 XX 写主题曲/OP/ED」
- 「Suno 提示词」「帮我写个 style prompt」
- 「改编/恶搞这首歌」「翻译歌词」

## 核心流程

```
0. 先搜：给已知影视/游戏/角色写歌 → 先查官方 OST 是否存在（QQ音乐/网易云 API）
1. 澄清访谈：新歌/大改默认先问 ≤5 个问题（每题一个类别）
2. 概念/hook 先行 → 3. 拆原曲骨架（parody） → 4. 素材脑暴 → 5. 套结构
6. 试唱校音节 → 7. 写 style prompt → 8. 打标签 → 9. 生成 3-5 版 → 10. 择优续写
```

**访谈不是审问**：brief 给得全（主题/角度/人称/情绪/风格/时长/人声/禁忌）就跳过；给得薄才问。想快速出草稿就说「先来版 sketch」——只问 5 项就动笔，明确标为非成品。

## 三个硬规则

| 规则 | 内容 | 反例 → 正例 |
|---|---|---|
| **标签嵌合** | 歌词里所有括号标签必须是段落标签，表演/氛围 cue 嵌进段内 | ❌ `[Whispered]` 独立行 → ✅ `[Verse 1 - Whispered]` |
| **数量克制** | 每段 1-2 个 cue，整首 4-8 个 enriched cues | 打满标签=干扰生成，宁少勿多 |
| **艺人转换** | 风格描述不写艺人名，转成特征坐标 | ❌ "James Bond style" → ✅ "1960s Cold War spy thriller brass" |

## Style 提示词两档公式

- **紧凑档（20-55 词）**：签名音色, 主风格, BPM, 调性, 支撑风格, 人声, 乐器角色, 歌词前提, 制作质感
- **扩展档（55-95 词）**：风格堆叠. 情绪框架+人声轨迹. 乐器音色. 制作空间. 编曲走向. 歌词前提. 时长
- 乐器给**角色**不给名单：「guitar carries pulse」优于「guitar」
- 变体必须换音乐前提（acoustic/glossy/cinematic/dance），不许只换形容词

## 人声方向（v2.0 新增，影视角色歌利器）

不是"女声/男声"，是坐标束：音色/发声/声区/颤音/装饰音/咬字/律动感/情绪姿态。普通需求直接用现成短语：

- `smoky alto, close-mic delivery, soft consonants, delayed vibrato`（烟嗓低音）
- `warm baritone storyteller, relaxed phrasing, light rasp, intimate room`（说书人男中音）
- `gospel-soul lead, open-throat chorus lift, melismatic touches, choir responses`（福音灵魂主唱）

## 文件结构

| 文件 | 内容 |
|---|---|
| `SKILL.md`（21KB） | 主手册：结构/押韵/parody/音标技巧/工作流 |
| `references/suno-craft-playbook.md`（10KB） | 深度版：访谈机制、style 公式详解、人声维度全表、标签族、翻译指南 |
| `references/instrumental-scoring-suno.md` | 纯配乐：影视/长剧角色主题、防 Suno 乱加人声 |

## 常见坑提醒

- **先上网查再动笔**：给《三国》写歌前先查——赵季平《关羽之歌》已存在，直接给原曲
- **英文音标**：专有名词先 30 秒小样测试，"Nous"→"Noose" 式拼写矫正
- **扩展漂移**：用 Extend 续写时风格会跑偏，续写时重申 genre/mood
- **访谈确认**：出词前会给 "User decisions vs Best-judgment decisions" 审查卡，回 "approved" 才生成

## 版本记录

- **v2.0.0（2026-08-13）**：合入 NuNaught 方法论——澄清访谈门槛、Style 双公式、人声坐标体系、标签嵌合硬规则、翻译指南；新增 `references/suno-craft-playbook.md`
- **v1.x（2026-08 前）**：基础创作手艺（结构/押韵/parody/Suno 提示词/音标技巧/纯配乐）
