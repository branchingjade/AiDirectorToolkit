# 知识库 → agent 可用（土壤层 skill 化，2026-08-10 定稿）

> 来源：前端设计知识库建设实测（本会话子代理验证）。适用：任何「建了知识库但担心 agent 用不上」的场景。

## 核心认知

**Obsidian 是给人查的，agent 不会自动读。** 知识库建在 vault 里 ≠ agent 会用它——0 次加载 = 引用缺失（知识没进 agent 流程），不是资产冗余。让知识库真正被 agent 使用，必须走 skill 通道（参照妖玉影视知识库模式）。

## 三层落地

1. **土壤层 skill 化**：`~/AppData/Local/hermes/skills/<分类>/<知识库名>/SKILL.md` 正文放**速查表**（浓缩全部规范的决策值+权威出处，agent 加载即用），`references/` 放**详版文档**（按需 skill_view 加载）。skill 的 description 前 57 字符必须带触发词（任务相关词，保证 agent 扫描 skill 索引时命中）。
2. **流程 skill 挂钩子**：在管辖该类任务的流程 skill（如 frontend-design-workflow）加「阶段 0 查库」强制步骤——查库后两种结论都有效：发现可优化点就落地，确认已达标就留档。流程 skill 是 agent 实际加载的入口，钩子挂在这里才保证每次任务必经。
3. **同级 skill 显式路由**：同类工具/命令 skill（如 impeccable）在 description 尾部 + 正文开头各加一句「规范依据见 <知识库名>」——防止 agent 只拉起命令层而漏了规范源头。

## 正本唯一

**skill references/ = agent 正本**（agent 加载的是 skill 目录）；Obsidian 分区 = 人读归档镜像（MOC 顶部标注正本位置）。改文档 → 改 skill 正本 → 同步 Obsidian 镜像。双份漂移 = 死资产。

## 验证实际加载（必须实测，不靠自报）

- **索引可见性**：`skills_list` 确认新 skill 实时进索引（无需重启）
- **加载链实测**：delegate_task 派一个子代理执行代表性任务（独立会话=最新索引，模拟真实用户），读 live transcript（`~/AppData/Local/hermes/cache/delegation/live/<deleg_id>/task-0.log`）看它的 `skill_view` 调用链——确认自动加载了知识库 skill 及其 references。子代理自报不可信，要看转录里的实际 tool 调用。
- **长期监控**：`skills/.usage.json` 自动记录每个 skill 的 `last_used_at`（skill_view 即记录）——新 skill 无需手动注册；knowledge-usage.py 定期统计，0 加载会暴露。

## 同类 skill 干扰判断

设计类/同类 skill 同时在场 ≠ 干扰。判据：**同层多副本才是重复**（如两个「规范速查」skill 抢戏）；跨层（土壤=知识/流程=步骤/工具=命令/素材=参考）是分工不是重复。触发词重叠检查跳过 'design' 等泛词，只看具体功能词重叠。真正的治理点是同级新增时触发词撞车，以及命令类 skill 的 description 过广导致过度拉起。

## 实测结果（2026-08-10 前端设计知识库）

- skills_list 实时可见 ✅
- 子代理任务自动加载链：frontend-design-workflow → 前端设计知识库（含 3 个命中 references）→ popular-web-designs/linear 模板 → impeccable，共 11 次 skill_view，claude-design/sketch/design-md 被正确跳过（设计方案任务不需要生成 HTML）
- usage.json 自动记录 last_used_at ✅
- 附带发现：impeccable 23 命令中 11 个 reference 文件缺失（SKILL.md 声明但磁盘没有）——第三方 skill 的引用完整性要抽查（对照 `grep -oE "reference/[a-z-]+\.md" SKILL.md` 与 `ls reference/`）
