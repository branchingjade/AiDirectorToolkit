# Hell Grind 全 AI 长片实证工作流（Higgsfield 开源，2026-08 研读）

95 分钟全 AI 长片的**官方公开生产档案**——成本结构、选中率、提示词工程、角色一致性方案全部有实据，是行业里少见的"整片级实证样本"。视觉生成用的正是 Seedance 2.0（与 AI提示词助手 2.0 主本同代）。

## 影片与成本

- 95 分钟动作奇幻，2026-05 戛纳放映（非官方场次，租商业影院 Cinéma Olympia，Marché du Film 名义）
- 15 人团队（导演/摄影/剪辑），哈萨克斯坦阿拉木图，14 天完成
- 总成本 ~$500K：**GPU 云计算 $400K（80%）+ 人力 $100K（20%）**——成本结构已反转：钱几乎全烧在生成废片上
- **官方选中率：16,181 次生成 → 253 段采用（64:1，约 1.6%）**——整片级别官方披露的唯一实证数字，段级失败率仍无官方数据
- 视觉生成：Higgsfield Soul Cinema/Soul Cast（私有角色锁定工具）+ Dreamina Seedance 2.0
- CEO Alex Mashrabov 原话：整个过程"像玩老虎机"
- 开源内容：全部 prompt、角色模型 seed、原始生成文件、shot list、19 分钟幕后拆解、Claude Skill（约 30 秒可部署）

## 管线（14 天流程）

```
剧本 → 自定义自动化系统把剧本页直接转成 3000 词级机器提示词
     → Soul Cast/Soul Cinema 锁角色
     → Seedance 2.0 批量生成（CS 2.0 模型、15s/段、每次输出 4 段）
     → 人工挑选（64:1）
     → 剪辑成 95 分钟
```

核心思想：把影视制作语言翻译成机器可执行的**数字指令**，再用海量生成+人工挑选消化随机性。

## 四段式提示词结构（官方 Claude Skill 生成）

1. **@锚定资产**：`@Roco` `@Monster` 标签 + 外貌简述链接参考图，让模型认同一角色——反角色漂移第一道锁，**低成本方案（参考图+标签，不走 LoRA/训练）**
2. **空间坐标（米）**：机位/距离明确数字，如"从 8 米移到 4 米，高度从 3 米降到 2 米"
3. **动作时间码（秒）**：动作节点精确到秒——"0.5 秒抬手、1.5 秒戴盔、3 秒站直"
4. **严格规则**：硬约束，防模型在不该发挥处自由发挥

## 提示词工程原则（官方总结）

- **数字 > 形容词**：不说"快速推近"，说"3 倍于典型电影 dolly 的速度"；模型对形容词反应差、对数字反应好
- **动作拆半秒步进**：复杂动作分解成 0.5s/1.5s/3s 时间节点
- **人群三层表达**：前景清晰人物 + 中景密集人群 + 雾中剪影，代替数字描述
- **生成参数**：CS 2.0、每段 15 秒、每输出 4 段、无隐藏设置
- **至少跑 4 次生成**：区分"随机失败"与"提示词本身有问题"，别拿单次结果调 prompt

## 最贵一课：否定式提示词会反噬

- 想让怪物手里没刀，写"no handheld object, no knife handle" → 模型仍加了一只握剑的手。改**正向描述**"抬臂，让画面清楚显示手里什么都没拿"才解决
- 打斗戏有"游戏过场感"，写十几遍"not a game, do not use CGI" → 模型记住 "game" 这个词，反而越做越像游戏。解法：正面描述光影/材质 + **多机位剪辑**（50mm 环绕 / 24mm 低角度 / 85mm 特写 / 35mm 广角混切）——单镜头本身天然像游戏过场

## 与 Seedance 提示词主本对接点

1. **时间码规范**：与 Seedance 2.5 整数秒时间戳同一思路、更细颗粒度（半秒步进）
2. **@锚定标签**：低成本角色一致性实证方案，与 skill 正文"LoRA 微调+参考图池"互为补充（不训练 vs 训练两条路线）
3. **否定式 vs 正向描述**：真金白银验证"禁止"会反噬——对照 AI提示词助手主本负面控制章节，优先正向描述

## 来源

- [Wikipedia - Hell Grind](https://en.wikipedia.org/wiki/Hell_Grind)（成本/团队/工具/戛纳放映）
- [WSJ - This Cannes Film Cost $500,000 to Make. $400,000 Was AI Compute Costs](https://www.wsj.com/cio-journal/this-cannes-film-cost-500-000-to-make-400-000-was-ai-compute-costs-a823b08d)
- [CNBC TV18 - AI makes a feature film in 14 days](https://www.cnbctv18.com/technology/ai-makes-a-feature-film-in-14-days-higgsfield-shares-its-500000-filmmaking-process-with-creators-19962632.htm)（2026-08-05，管线+自动化转换系统）
- [st-hakky - Higgsfield Releases Blueprint for AI Feature Films](https://book.st-hakky.com/en/news/higgsfield-ai-film-14-days)（3000 词 prompt、选中率、成本拆解）
- [gate.com - Higgsfield burns $500k ... open-sourcing all prompts](https://www.gate.com/news/detail/higgsfield-burns-500k-to-produce-a-95-minute-ai-film-open-sourcing-all-23335137)（2026-08-10，四段式结构+最贵教训+FAQ）
- [GitHub OSideMedia/higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill)（社区打包 32 子技能，含 Hell Grind feature-film pipeline，非官方）
