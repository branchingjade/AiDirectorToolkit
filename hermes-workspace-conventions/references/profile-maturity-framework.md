# 画像体系成熟度评估框架（2026-08-08，NN/g 取证）

用户问题「客观分析什么才是成熟的画像体系，要有依据」——评估任何画像体系（成员画像/用户画像/persona）是否成熟的五标准，依据 Nielsen Norman Group《Personas Are Living Documents: Design Them to Evolve》(Maddie Brown, 2023, nngroup.com/articles/personas-are-living-documents/) + Wikipedia Persona (UX) 词条。

## 五标准（NN/g 反证推导）

| # | 标准 | NN/g 依据 | 反例（=失败信号） |
|---|------|-----------|------------------|
| ① | **画像必须被使用** | 失败原因第一条 "Personas were created, but not used" | 写完没人读=不存在 |
| ② | **画像必须能演进** | "personas are merely a representation of data, and data can change"；"never created to be updated"=失败 | 不可更新的画像=死数据；但过度更新也是病（稳定性与灵活性要平衡） |
| ③ | **画像必须是数据的表示** | Wikipedia：persona 基于 "statistical analysis and qualitative observations"；NN/g："a representation of data" | 无数据支撑的画像=臆想（编造） |
| ④ | **画像格式必须易更新** | "Uneditable File = Immutable Data"——PDF 暗示终稿，难编辑格式=数据被判死刑 | 精美但难改的格式（PSD/海报）会过时且无人用 |
| ⑤ | **稳定性与灵活性平衡** | "stability of personas over time is critical to their ability to be remembered and internalized... personas need to be flexible enough to accurately represent the organization's current users" | 全稳定=过时；全灵活=记不住 |

## 本机画像体系对照（2026-08-08 实测评估：4/5 达标 → 反馈闭环补齐后 6/6 达标）

- ① 使用闭环 ✅：IM+评论双通道注入（get_profile_meaningful），每次交互进 bot 上下文
- ② 可演进 ✅：实时 OBSERVATION 沉淀 + cron 批量 + 矛盾检测拦截错误更新 + 定期勘误复核（比 NN/g 建议的"响应业务变化才更新"更激进——持续观察驱动，更实时但更依赖观察质量）
- ③ 数据驱动 ✅：每条观察来自真实会话（IM/评论）带日期；空模板明确标「待沉淀」不编造
- ④ 易更新 ✅：Markdown 纯文本 + git 版本管理；frontmatter 只留基础设施（open_id/updated/tags）无复杂结构
- ⑤ 稳定性平衡 ✅：稳定偏好进「沟通偏好/擅长领域」（不轻易变），一次性事件进「协作备注」（流水），能力≥2次才升级——自动分界
- ⑥ 反馈闭环 ✅（2026-08-08 补齐）：gateway 注入日志（`[Feishu-Collab] Profile injected for <名> (<open_id>), <N> chars`）为统计源；健康检查脚本新增三块——**3b 画像使用率**（近 N 小时注入次数，反映画像是否真被 bot 读取）、**3c 画像生命周期**（活跃成员画像 >14 天未更新 = stale；>30 天无活动 = 🧊 冷却待归档评估）、**3d 画像时效匹配**（画像 mtime vs sessions 表最近活动时间，差 >7 天 = 滞后）

## 剩余差距（未来迭代方向）

| 差距 | 说明 | 成熟体系对应 |
|------|------|-------------|
| 单一数据源 | 画像只来自 bot 观察，缺成员自述/用户拍板的交叉验证 | 成熟画像多为多源（行为+自述+访谈） |
| 使用率只统计不归因 | 3b 能数注入次数，但不知 bot 实际参考画像多少、画像对回复质量影响多大 | 需端到端效果归因（难，暂缓） |

## 评估方法论（怎么用这个框架）

被问「画像体系/记忆体系成不成熟」时：逐条对照五标准给结论（达标/部分/缺），每条带证据（本机机制对应），最后列差距。**不要只给结论**——用户要求「有依据」，每标准必须给出引用来源或本机实测证据。

## 框架复用：创作知识库使用率（2026-08-08 全链路审视落地）

用同一思路审视其他链路时，发现创作知识库（妖玉影视 _知识库，土壤层）是最像"画像改造前"的链路——建了不知道用没用。已补反馈闭环：

- **脚本**：`~/AppData/Local/hermes/scripts/knowledge-usage.py [days]`——从 state.db 统计 skill_view 实际加载了哪些知识库文件
  - 数据源：messages 表 role='tool' 消息，content 是 skill_view 结果 JSON（**注意字段名是 `file` 不是 `file_path`**；SQL 过滤用 `LIKE '%妖玉影视知识库%'` 而非 `LIKE '%skill_view%'`——结果 JSON 不含 "skill_view" 字样）
  - file 值带 `references/` 前缀需归一化（split("references/",1)[1]）
  - 输出三块：主本加载次数 / references 文件加载次数（按目录归类）/ 潜在僵尸资产（state.db 现存记录中从未加载）
- **cron 接入**：知识库每日巡检（22:00，job d466e0d36bc2）新增步骤6 使用率统计，报告格式追加 `| 知识库使用率: 主本X次/文件X个/僵尸X个`
- **使用价值**：被反复加载的=土壤养分（该继续深化）；0 次加载的=引用缺失（知识存在但没进创作流程，该在 skill 的知识库先行流程里补引用），**不是清理依据**——知识库是蒸馏的知识，存在即价值
- **注意盲区**：state.db 可能已清理早期会话，"从未加载"指现存记录范围，不绝对等于建库以来从未用过

## 框架复用：全链路审视方法论（2026-08-08 十三链路实证）

用户「用这个思路审视其他链路」——把画像五标准推广到评估任意数据链路。可复用流程：

1. **盘点全部链路**：Obsidian 各目录（_hermes/画像/路由/名单/评论会话/日志/剧本库/项目资产/知识库）+ Hermes 运行时（Hindsight/MEMORY 镜像/kanban/补丁管理）+ 飞书正本。`du -sh` + `find | wc -l` 拿体积/文件数实证
2. **每条链路收集四个证据**：谁读它（使用闭环）、数据从哪来（数据驱动）、格式可否更新（易更新）、有无检查机制（反馈闭环）——每条给具体命令/文件/日志作证，不凭印象
3. **分类**：🟢 A 类（健康+反馈闭环）/ 🟡 B 类（健康但反馈弱）/ 🔴 C 类（有问题）
4. **找系统性缺口（关键）**：多个 B/C 类链路的共同根因往往是一个——2026-08-08 实证：镜像 diff、MOC 计数、看板日报、成员名单四链路共缺**一致性校验**，补一个 archive-consistency.py 同时覆盖四条。先找共性再逐个修
5. **防误判**：①`ls` 不递归会漏看子目录（日志"只有 2 个文件"误判，实际 4 篇日报在 W1/W2 下）；②子代理/cron 自报不可信，必须独立复验数据层；③**看板日报断更≠故障**——先查该链路是否本就低频（kanban 是 AI worker 工具），低活跃链路的"停更"是正常态不是断链，硬报只会变噪音
6. **验证未完不下定论**（用户纠正）：评估类结论在验证完成前保持"验证中"，不删监控、不写死 memory、不宣布定论

输出模板：链路全景表（A/B/C 分类+每条实证）+ 核心发现（系统性缺口）+ 结论（已解决/最该补的下一个/待验证）。

全链路审视发现 B/C 类链路共缺**一致性校验**（剧本库 MOC/镜像 diff/看板日报/成员名单上游），补一个脚本覆盖四条：

- **脚本**：`~/AppData/Local/hermes/scripts/archive-consistency.py`——四项检查
  1. MEMORY/USER 镜像 vs 真源 diff（`_hermes/memory/` vs `~/AppData/Local/hermes/memories/`）
  2. 剧本库 MOC 声明数 vs 磁盘实际（华语/海外 × 原文/报告，MOC 头部的"中文剧本 X 份 + 研习报告 Y 份"正则解析）
  3. 看板日报新鲜度（**活跃度感知**：仅当任一 board 近 7 天有新任务时才检查 `协作/任务看板日报.md` mtime；看板闲置跳过不报噪音——kanban 是 AI worker 工具任务本就低频，日报断更≠故障）
  4. 成员名单 vs 画像 open_id 对应（名单 11 人 ↔ 画像 11 份）
- **cron 接入**：每日巡检步骤7，报告格式追加 `| 归档一致性: ✓全部通过/⚠️详见`
- **首跑真实发现**：MEMORY.md 镜像滞后 2472 字符（当天改记忆、昨晚 cron 同步未赶上）——证明检查抓到真实问题；已手动 cp 修复
- **设计要点**：检查为主、修复靠 cron 既有同步（步骤1）+ 手动；不自动改 MOC（计数不符需人判断是 MOC 过时还是文件缺失）
