---
name: frontend-design-workflow
description: 前端设计正确工作流——LLM 做不出好设计，只能迭代出好设计。参考→生成→评审→打磨→加固五阶段。触发词：设计网页、改UI、设计评审、audit、polish、前端改版、界面重设计、UI review。
version: 1.0.0
---

# 前端设计工作流

## 核心原则

**LLM 拿设计 token（色板、字体、间距）直接生成 CSS = 垃圾。** 根因不是 skill 不够、不是 token 不够细——是 LLM 本身在视觉执行上就是弱项。间距节奏、层次感、留白重量这些东西，token 预测做不到。

正确路径：**不追求一遍生成对，追求快速迭代到对。**

## 五阶段工作流

```
参考 → 生成 → 评审 → 打磨 → 加固
```

| 阶段 | 做什么 | 用哪个 skill |
|------|--------|-------------|
| 0. 查库 | **先加载 `前端设计知识库`**——拿规范骨架：交互六套/动效参数/对比度/组件选择/状态四态，全部带权威出处 | `前端设计知识库`（土壤层，必查） |
| 1. 参考 | 确定视觉语言：色板、字体、间距、组件风格 | `popular-web-designs` 加载目标品牌模板 |
| 2. 生成 | 写初版 HTML/CSS，不求完美 | `claude-design` 或 `sketch` |
| 3. 评审 | 找出问题：层次、密度、对齐、AI 套路 | `impeccable:critique` + `impeccable:audit` |
| 4. 打磨 | 修具体问题：加胆、收噪、字体、动效 | `impeccable:polish` / `bolder` / `typeset` / `layout` |
| 5. 加固 | 边界情况、响应式、a11y、错误状态 | `impeccable:harden` / `adapt` / `optimize` |

## 关键 pitfall

- **阶段 0 不可跳。** `前端设计知识库` 是土壤层——交互逻辑/动效数值/对比度标准/组件选择都从那来，跳了=凭感觉设计。查库后两种结论都有效：发现可优化点就落地，确认已达标就留档。
- **不要停在阶段 2 就交差。** 没有 3-5，2 的产出一定是 AI 味垃圾。用户原话："没什么感觉呢，做出来的东西很烂"——就是停了。
- **用户说"用 skill"= 加载全部相关 skill，不是挑几个。** 反面案例：用户说"用前端设计的几个 skill 出方向"，只加载了 sketch + claude-design，漏了 impeccable（评审/打磨）和 popular-web-designs（参考）。用户追问"用 skill 了嘛"并命令"从 0 设计，用上所有能用的 skill"——根因不是少做一个步骤，是没有把完整工具链拉起来。impeccable 的 critique/typeset/layout/colorize 命令、claude-design 的 surface-first 和 slop-diagnostic、sketch 的 intake→variants→head-to-head 流程——少一个都会导致产出停在"能看但没打磨"的状态。
- **上下文够了≠跳过阶段 1（参考）。** 即使项目风格已知，参考阶段的价值不是在"发现新的参考"，是在"把视觉锚点写下来迫使 agent 在设计前 commit 到一个具体的色彩/材质/字体方向"。反面案例：第一次出 3 个方向（公告栏/金漆匾额/搪瓷标语），用户看了说"从 0 设计"——因为这 3 个是在没有 impeccable 的 color strategy + surface-first 约束下生成的，方向散、没根。
- **阶段 3 和 4 可以循环多次。** critique → polish → critique → polish，直到没有新问题。
- **暗色主题先确认物理场景。** impeccable 的设计法则：先写一句话——谁、在哪里、什么光照、什么情绪——再选明暗。
- **CSS clip-path 画不出可辨认的人物/动物剪影。** vision 模型会把 clip-path polygon 人形识别为"锯齿状抽象竖条"而非人。画剪影必须用 SVG `<path>` + 自然曲线（弧线肩膀、自然手臂垂度、腿的曲线），不能用纯几何多边形。同理：同色剪影叠在同色背景上 = 不可见——需要至少两层对比（亮天空/暗剪影/中灰人物）。详见 `references/silhouette-techniques.md`。
- **参考找对口品类。** TTS 工具参考 ElevenLabs（同品类），不要随便套 Linear（开发者工具）。
- **阶段 1（参考）产出必须写下来，不是脑子里过。** 反面案例：第一次做 3 个方向时"参考"在脑子里——知道项目是 1996 东北工业、有钢的琴/白日焰火/铁西区参考。但没有 commit 到纸面上：色彩策略是什么（Restrained）、物理场景是什么（暗放映厅+灰暗工业区）、字体策略是什么（仿宋/粗黑/打字机各用于什么姿态）。这些在第二次从 0 设计时才写下来，产出立刻有了根。

## 可用命令速查 (impeccable)

| 类别 | 命令 |
|------|------|
| 评估 | `critique` UX评审 · `audit` a11y/性能/响应式检查 |
| 打磨 | `polish` 收尾 · `bolder` 加胆 · `quieter` 收敛 · `distill` 精简 · `harden` 加固 · `onboard` 引导 |
| 增强 | `animate` 动效 · `colorize` 色彩 · `typeset` 字体 · `layout` 布局 · `delight` 微交互 · `overdrive` 特效 |
| 修复 | `clarify` UX文案 · `adapt` 多设备 · `optimize` 性能 |
| 迭代 | `live` 浏览器实时调 |
| 创建 | `craft` 完整流程 · `shape` 先规划 · `teach` 初始化 PRODUCT.md |
