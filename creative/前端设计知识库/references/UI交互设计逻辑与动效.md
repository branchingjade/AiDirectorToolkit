---
tags:
  - 前端设计
  - UI
  - 交互
  - 动效
date: 2026-08-10
---

# UI 交互设计逻辑与动效（权威背书）

> 2026-08-10 | 面向：前端工具 / 网页 / 插件界面设计
> 来源标注：训练知识（经典著作与官方文档，内容稳定，可按出处核对）

## 一、速览：六套逻辑各管什么

| 套 | 名称 | 管什么 | 权威出处 |
|---|---|---|---|
| 1 | 感知与认知法则 | 人怎么处理信息、做决策 | 格式塔学派、Hick/Fitts/Miller 原始论文 |
| 2 | 可用性启发式 | 怎么评估一个界面好不好用 | Nielsen Norman Group（NN/g） |
| 3 | 设计心理学原则 | 怎么造一个好用且不难懂的产品 | Don Norman《设计心理学》 |
| 4 | 平台设计系统 | 工业界成体系的交互规范 | Apple HIG / Material Design / Fluent |
| 5 | 交互模式实证 | 具体套路哪些有效、哪些是谣言 | NN/g 眼动与行为研究 |
| 6 | 动效逻辑 | 动效的时长、缓动、编排、无障碍 | Material Motion / Apple HIG / WCAG / RAIL / Disney 12 原则 |

## 二、套1：感知与认知法则（人脑怎么工作，设计的前提）

| 法则 | 一句话逻辑 | 权威出处 |
|---|---|---|
| 格式塔五原则 | 邻近、相似、闭合、连续、共同区域——人自动把相近的元素归为一组 | Wertheimer/Koffka，格式塔心理学，1910s |
| Hick 定律 | 可选越多，决策越慢；关键场景要砍选项 | W. E. Hick, 1952 |
| Fitts 定律 | 目标越大、离得越近，越容易点中；常用按钮放大、放角落风险高 | P. M. Fitts, 1954 |
| Miller 7±2 | 工作记忆一次只能装 5-9 个组块，超了要靠分组/分页消化 | G. A. Miller, 1956 |
| Jakob 定律 | 用户把其他产品的习惯带进来，新界面沿用惯例=零学习成本 | Jakob Nielsen / Laws of UX |

## 三、套2：可用性启发式（评估界面，Nielsen 10 条里最常抓人的 6 条）

| 启发式 | 含义 | 出处 |
|---|---|---|
| 系统状态可见 | 任何操作都要有即时反馈（加载/成功/失败） | Nielsen 10 Heuristics, 1990/1994，NN/g 2024 修订版 |
| 认知负担最小 | 用「识别」代替「回忆」——把选项摆出来，别让用户记 | 同上 |
| 一致性与标准 | 同义词、同操作全站统一，遵循平台惯例 | 同上 |
| 防错优于纠错 | 阻止错误发生，比报错后再恢复强 | 同上 |
| 灵活与高效 | 快捷键、批量操作给老手，别让新手绕路 | 同上 |
| 美学极简 | 少即是多，多余信息稀释有效信息 | 同上 |

同源还有 Shneiderman《设计用户界面》的 8 条黄金法则（1986/2016），核心重合：一致性、快捷方式、明确反馈、防错、轻松撤销、用户主导、减少记忆负担。

## 四、套3：设计心理学原则（Don Norman《设计心理学》1988/2013）

| 原则 | 逻辑 | 落地示例 |
|---|---|---|
| Affordance 可供性 | 物体形态暗示它能怎么用 | 按钮长得像能按的 |
| Signifier 能指 | 明确告诉用户怎么用 | 图标+文字标签，不靠猜 |
| Mapping 映射 | 控件与结果的空间关系要直观 | 上箭头=上移 |
| Feedback 反馈 | 每个动作都有结果可见 | 点击变亮、保存有提示 |
| Constraint 约束 | 限制不可能的操作，防错靠设计 | 不可用项置灰 |
| Consistency 一致性 | 同样的事同样的做法 | 删除确认全站同一种 |

## 五、套4：平台设计系统（工业界最权威的成体系规范）

| 系统 | 出处 | 一句话定位 |
|---|---|---|
| Apple HIG | developer.apple.com/design | 内容优先、层级清晰，macOS/iOS 交互基准 |
| Material Design 3 | m3.material.io | 基于实体的动效与材质隐喻，组件+状态最完整 |
| Microsoft Fluent | learn.microsoft.com/fluent-ui | 密度优先，桌面生产力工具的控件范式 |

## 六、套5：交互模式实证（NN/g 研究结论，能直接抄的套路）

| 模式 | 结论 | 出处 |
|---|---|---|
| 无限滚动 vs 分页 | 内容发现型（信息流/浏览）用无限滚动；查找定位型（列表/搜索结果）用分页——无限滚动牺牲定位能力 | NN/g, "Infinite Scrolling Is Not for Every Website", 2018/2024 |
| 阅读模式 | 浏览型页面用户扫 F 型/Z 型路径，关键信息放路径上 | NN/g 眼动研究, 2006/2017 |
| 撤销 vs 确认框 | 「撤销」比「你确定吗」更好——确认框打断流，撤销给后悔药 | NN/g, "Never Use a Warning When You Mean Undo", 2019 |
| 3 点击规则 | 已被证伪——用户不怕多点几次，怕每次点击无反馈、不确定 | NN/g, "The 3-Click Rule Is a Myth", 2003 |
| Kano 模型 | 功能分三档：基本型（没有就骂）、期望型（越多越满意）、兴奋型（惊喜点）——资源优先投基本型 | Noriaki Kano, 1984 |

## 七、套6：动效逻辑（Motion Design）

### 7.1 动效的用途（先问为什么动，再谈怎么动）

动效在界面里只做四件事：

| 用途 | 说明 | 出处 |
|---|---|---|
| 反馈 | 操作有反应，系统状态可见 | Nielsen 启发式 #1 |
| 引导注意力 | 新内容/变化处动一下，人眼自动捕捉运动 | NN/g "Animation for Attention and Comprehension", 2013 |
| 空间连续性 | 元素从哪来、到哪去，用户保持空间认知 | Material Design Motion / Apple HIG |
| 因果叙事 | 动作→结果用动效连起来，用户理解变化原因 | NN/g, 同上 |

反例：为动而动、全程匀速平移、所有元素一起动——NN/g 明确警告过度动画伤害可用性与性能。

### 7.2 时长分级（先定时长，再谈缓动）

Material Design 官方数值（m3.material.io/styles/motion）：

| 元素大小 | 时长 | 典型对象 |
|---|---|---|
| 小（100-200ms） | 微交互 | 开关、复选框、气泡、图标反馈 |
| 中（200-300ms） | 常规过渡 | 卡片、列表项、弹层 |
| 大（300-400ms） | 页面级 | 全屏页切换、抽屉 |
| 强调（可达 500ms） | 大型场景 | 转场叙事、首屏展示 |

原则：**位移越大、时长越长**（与 Fitts 定律的距离-时间关系同源）；所有动效不超过 500ms，超过=用户等待感。

### 7.3 缓动曲线（Easing，动效质感的核心）

| 曲线 | 用途 | 出处 |
|---|---|---|
| 标准曲线 cubic-bezier(0.2, 0, 0, 1) | 默认：元素在场景内往返 | Material Design Motion |
| 减速曲线（emphasized decelerate） | 进入场景——快起慢停，物体到达感 | Material Design Motion |
| 加速曲线（emphasized accelerate） | 退出场景——慢起快走，离场干脆 | Material Design Motion |
| 线性 linear | 禁止用于 UI 运动——机械感、无生命力 | Material / Apple HIG 共识 |

底层美学来自迪士尼动画：**缓入缓出（Slow in / Slow out）是 12 原则之一**，自然界没有匀速运动的物体（Frank Thomas & Ollie Johnston, The Illusion of Life, 1981）。

### 7.4 编排原则（多个元素怎么配合动）

| 原则 | 逻辑 | 出处 |
|---|---|---|
| 错峰（Stagger） | 同组元素依次入场，不齐动——齐动=广播体操，错峰=有节奏 | Material Design Motion |
| 因果链 | 子元素跟着父元素动（parenting），先因后果 | UX in Motion Manifesto, 2017 |
| 共享元素过渡 | 点击卡片→展开详情，卡片本身变形过渡，用户不迷路 | Material Design Motion（spatial continuity） |
| 遮蔽/克隆/视差 | 层级遮挡、内容克隆、背景差速——营造空间深度 | UX in Motion Manifesto, 2017 |

### 7.5 无障碍：动效必须可关（硬性合规）

| 要求 | 内容 | 出处 |
|---|---|---|
| WCAG 2.2 标准 2.3.3 | 非必要动效必须能被用户关闭（AA 级，2023 年生效） | W3C Web Content Accessibility Guidelines 2.2 |
| CSS 实现 | `@media (prefers-reduced-motion: reduce)` 关闭非必要动画 | W3C / 浏览器标准 |
| 眩晕风险 | 大幅视差、持续抖动、缩放脉动可能诱发前庭不适，属于真实伤害不是风格问题 | NN/g 无障碍研究 |

### 7.6 性能铁律（动效的物理底线）

| 铁律 | 数值 | 出处 |
|---|---|---|
| 帧预算 | 60fps = 每帧 16ms 内完成 | Google RAIL 模型（web.dev/rail） |
| 只动 transform/opacity | 走 GPU 合成，不触发重排重绘；不动 width/height/top/left | Google RAIL / 浏览器渲染标准 |
| 动画帧率达标检查 | DevTools Performance 面板看 Frames 是否为绿色满帧 | Chrome DevTools 文档 |

## 八、你的工具偏好 ↔ 权威依据（实战对照）

| 既定偏好 | 对应逻辑 | 依据 |
|---|---|---|
| 记住上次的视图/筛选/搜索词 | 识别优于回忆 | Nielsen 启发式 #6 |
| 无限滚动替代分页 | 浏览型内容用无限滚动 | NN/g 2018/2024 |
| Ctrl+Enter 快捷键、参数常显 | 灵活高效 + 不折叠=减少回忆负担 | Nielsen 启发式 #7、#6 |
| 暗色高密度、白底按钮唯一重色 | 美学极简 + 突出唯一主操作 | Nielsen 启发式 #8 / HIG |
| 大目标易点中（按钮够大） | Fitts 定律 | Fitts, 1954 |
| 动效落地默认值 | 微交互 100-200ms + 标准缓动曲线 + 只动 transform/opacity + 尊重 prefers-reduced-motion | Material / RAIL / WCAG |

## 九、来源清单

**书**：Norman《The Design of Everyday Things》(1988/2013)；Shneiderman《Designing the User Interface》(8th ed. 2016)；Yablonski《Laws of UX》(2019/2024)；Thomas & Johnston《The Illusion of Life》(1981，迪士尼 12 原则)

**机构**：NN/g（nngroup.com）——10 启发式原文、无限滚动/撤销/3 点击/阅读模式/动效研究；W3C——WCAG 2.2 标准 2.3.3；Google——Material Design 3 Motion、RAIL 模型

**官方文档**：Apple HIG、Material Design 3、Microsoft Fluent

**原始论文**：Hick 1952、Fitts 1954、Miller 1956、Kano 1984

**动效专项**：Issara Willenskomer《UX in Motion Manifesto》(2017)——12 个动效模式（easing/offset&delay/parenting/transformation/value change/masking/overlay/cloning/obscuration/parallax/dimensional/darting）
