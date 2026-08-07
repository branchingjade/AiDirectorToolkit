# Suno 纯器乐影视配乐指南

## 核心挑战
Suno 默认倾向加人声。做纯器乐配乐时必须反复在 Style 和 Lyrics 标签中强化"no vocals"。

## Style 字段配方

### 必须包含
- `instrumental, no vocals, no singing` — 放在 Style 开头
- 乐器+质感：`solo harmonica`, `sparse piano`, `lo-fi raw recording`
- 动态弧线：`begins as X, gradually Y, ends with Z`
- 空间感：`empty factory hall natural reverb`, `analog tape warmth`

### 禁止出现
- 任何歌手/人声描述（包括 `male vocals` `female vocals` `vocalist`）
- `cinematic` / `epic` / `beautiful` — 模糊且无指导力
- 品牌名/艺术家名

## Lyrics 字段策略

即使无人声，也必须用结构标签引导段落：

```
[Intro]
[Instrumental - solo harmonica, single long note]

[Verse]
[Spare melody, four bars only]

[Outro]
[Fade to silence]
[End]
```

可用标签：`[Instrumental]` `[Instrumental Break]` `[Quiet arrangement]` `[Gradual swell]` `[Slow build]` `[Fade to silence]`

## 角色主题设计原则

长剧配乐不写"场景音乐"——写角色的音乐动机：

- 每个核心角色一个主题乐器+一个核心音程
- 所有主题共享同一调性或音程关系（如三度+五度下行），保证世界观统一
- 片段变奏：同一段旋律，不同集里换环境声做底（心跳/缝纫机/风声）

## 质量三条

1. **经得起单曲循环** — 独立作品，不是画面附庸
2. **离开画面也能成立** — 关掉屏幕，脑中自动浮现场景
3. **不替观众做感情决定** — 旋律不"告诉"你该哭了

## 对比：歌曲 vs 配乐

| 维度 | 歌曲（原 Skill 覆盖） | 纯器乐配乐（本文档） |
|------|----------------------|---------------------|
| Style 字段 | 需要歌手描述 | 强调 instrumental, no vocals |
| Lyrics 字段 | 写完整歌词 | 只用结构标签 |
| 结构 | ABABCB 等歌曲结构 | 散→聚→散，不拘传统 |
| 长度 | 3-4 分钟 | 完整版 2-3 分钟，片段 30-45 秒 |
