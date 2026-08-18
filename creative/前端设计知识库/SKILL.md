---
name: frontend-design-knowledge-base
description: 前端设计知识库（土壤层）——交互/动效/暗色/布局/组件/表单/状态/无障碍规范速查，全部带权威出处（NN/g/Material/WCAG/Fluent）。做前端工作时必查：设计网页、改UI、组件、布局、分栏、暗色主题、表单、动效、无障碍、前端改版。
version: 1.0.0
tags: [前端设计, 知识库, 规范, ui]
platforms: [linux, macos, windows]
---

# 前端设计知识库

> **土壤层 skill**：所有前端/UI/网页设计任务的第一站。先查速查表定骨架，再按需加载 references/ 详细文档。
> 正本唯一：**本 skill 的 references/ = agent 正本**；Obsidian 归档镜像在 `Documents/KnowledgeBase/Obsidian Vault/前端设计/`（人读层，改动以 skill 为准后同步）。

## 触发条件

做以下任何事，必须先加载本 skill：
- 设计/改版网页、面板、插件 UI、组件库
- 定色彩/暗色主题、布局分栏、表单、动效、状态设计
- 前端设计评审（audit/polish/加固）

## 一、交互总纲（六套逻辑速查）

| 套 | 逻辑 | 出处 |
|---|---|---|
| 感知认知 | 格式塔分组 / Hick（选项少决策快）/ Fitts（目标大近易点中）/ Miller 7±2 / Jakob（沿用惯例） | Hick 1952 / Fitts 1954 / Miller 1956 |
| 可用性启发式 | 状态可见 / 识别优于回忆 / 一致性 / 防错 / 快捷键 / 美学极简 | Nielsen 10 Heuristics（NN/g 2024） |
| 设计心理学 | Affordance / Signifier / Mapping / Feedback / Constraint / Consistency | Norman《设计心理学》1988/2013 |
| 平台系统 | HIG / Material 3 / Fluent 三套工业规范 | Apple / Google / Microsoft |
| 交互实证 | 无限滚动给浏览型、分页给查找型；撤销>确认框；3点击规则是谣言 | NN/g 2018/2019/2003 |
| 动效逻辑 | 见下节 | Material / RAIL / WCAG |

## 二、动效速查（直接抄数值）

| 项 | 值 | 出处 |
|---|---|---|
| 时长分级 | 微交互 100-200ms / 常规 200-300ms / 页面级 300-400ms / 上限 500ms | Material Motion |
| 缓动 | 标准 `cubic-bezier(0.2,0,0,1)`；进=减速、出=加速；**禁用线性** | Material Motion |
| 用途 | 只做四件事：反馈/引导注意力/空间连续性/因果叙事 | NN/g 2013 |
| 编排 | 错峰入场、父子因果、共享元素过渡 | Material / UX in Motion 2017 |
| 无障碍 | 非必要动效可关 `prefers-reduced-motion`（WCAG 2.2 2.3.3 AA） | W3C |
| 性能 | 60fps=16ms 帧预算；只动 transform/opacity | Google RAIL |

## 三、暗色主题速查

| 项 | 值 | 出处 |
|---|---|---|
| 底色 | 极暗但非纯黑（Linear `#08090a` 系） | NN/g 2020 暗色研究 |
| 对比度 | 正文 4.5:1 / 大文字与 UI 组件 3:1 / AAA 7:1 | WCAG 1.4.3 / 1.4.11 / 1.4.6 |
| 豁免 | 禁用态（disabled/inactive）不要求对比度 | WCAG |
| 层级 | 明度分层代替阴影（暗色下阴影不可见）；聚焦用 outline | Material Elevation / WCAG 2.4.7 |
| 唯一重色 | 每屏一个主操作（白底按钮/主色），其余收敛 | Material 主色 + Nielsen #8 |

## 四、布局与分栏速查

| 项 | 值 | 出处 |
|---|---|---|
| 密度 | 8pt 网格（间距/尺寸全 8 倍数），紧凑可 4px 步进 | Material Layout |
| 栏数 | ≤3：单栏阅读 / 双栏工具（主 60-75%）/ 三栏创作（导航≤240+参数 280-360） | Material + 本工作区基准 |
| 参数常显 | 工具型默认展开，折叠是用户主动行为，不默认折叠 | 本工作区铁律 |
| 分隔条 | 双击重置、方向键调宽（10px 步进）、命中区≥16px、内容栏 min320/参数栏 min240 max480 | Fluent 2 Splitter / WAI-ARIA |
| 持久化 | 记住栏宽+折叠状态（按用户×按视图），比例存，给恢复默认 | Nielsen #6 |
| 窄屏 | 三栏→抽屉→单栏；4K+Windows 缩放用 JS 测物理分辨率（CSS 媒体查询失效） | 本机实测 |

## 五、组件速查（选对再实现）

| 场景 | 用 | 别用 | 出处 |
|---|---|---|---|
| 阻断确认/关键错误 | 弹窗 Dialog | 内容>1屏 | Material |
| 编辑详情/边看边填 | 抽屉 Sheet | 一次确认 | Material |
| 轻量解释 | 气泡 Tooltip | 承载操作 | HIG |
| 破坏性操作 | 撤销机制 | 「你确定吗」确认框 | NN/g 2019 |
| 立即生效设置 | 开关 Switch | 后面还要点保存 | Material |
| 多项选择/批量 | 复选框 | 开关 | Material |
| 互斥≤5 | 分段控件/单选 | 下拉 | Material |
| 数据表格 | 表头冻结、行操作悬停、批量工具条 | 全列等宽 | Material Data tables |

## 六、表单速查

| 项 | 值 | 出处 |
|---|---|---|
| 标签 | 永远可见，占位符不能当标签 | NN/g 2014 |
| 校验 | 格式类边输边查、失焦查、提交总查+聚焦首错；不边打字边报 | NN/g |
| 默认值 | 合理默认+记住上次值；敏感字段不预填 | Nielsen #6/#7 |
| 错误 | 行内显示、具体可行动、红色+图标双通道、不清空输入 | Nielsen #9 / WCAG 1.4.1 |
| 无障碍 | 每输入必有 label、错误 aria-describedby、Tab=视觉序 | WCAG 1.3.1/3.3.2/2.4.3 |

## 七、状态速查（四态齐全是成品标准）

| 态 | 做法 | 出处 |
|---|---|---|
| 加载 | 骨架屏>转圈（结构已知用骨架）；>1s 提示、>10s 可取消 | NN/g |
| 空 | 图标+一句话+动作；区分「真无数据」和「筛选无结果」 | NN/g Empty States |
| 错误 | 就地+重试+保留上下文 | Nielsen #9 |
| 成功 | Toast 轻量反馈；可逆操作本身状态变化=反馈，不弹 | Material Snackbars |
| 工程 | 显式四态状态机；请求竞态用序号/Abort；防抖 300ms | 工程实践 |

## 八、参考库

54 个真实设计系统（Linear/Stripe/Vercel/Sentry...）速查与加载：`references/真实设计系统参考库.md`（完整 54 个模板目录 + 选型速查 + 字体替代表）。

## references/ 文档（按需加载，正本）

| 文件 | 内容 |
|---|---|
| `references/UI交互设计逻辑与动效.md` | 总纲详版：六套交互 + 动效全参数 |
| `references/暗色主题设计.md` | 色彩系统/对比度硬标准/层级 |
| `references/布局与信息架构.md` | 密度/栅格/F-Z 阅读/导航 |
| `references/分栏与可拖动分区设计.md` | 分隔条/折叠/持久化/窄屏降级 |
| `references/组件设计模式.md` | 组件决策树/弹窗抽屉气泡 |
| `references/表单设计.md` | 标签/校验/默认值/错误 |
| `references/状态与反馈.md` | 加载/空/错误/乐观更新 |
| `references/可访问性与跨屏适配.md` | WCAG 条款表/键盘/4K 缩放 |
| `references/真实设计系统参考库.md` | 54 个设计系统速查 |

## 工作流对接

- 完整五阶段流程见 `frontend-design-workflow` skill（参考→生成→评审→打磨→加固）——阶段 1 参考时先查本库定规范骨架
- 具体模板加载见 `popular-web-designs`（54 个系统 HTML/CSS 模板）
- 设计过程与品味见 `claude-design`
