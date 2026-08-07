# 编剧/银幕写作理论调研 · 维基来源地图（2026-08 实测）

任务方（或需求方）常给出"想当然"的维基 URL，实际指向错条目。本表为编剧创作层四个主题（人物/类型/对白/结构）的已验证条目映射与陷阱。

## 人物塑造
| 主题 | 正确条目 | 陷阱/要点 |
|---|---|---|
| 人物刻画总论 | `Characterization` | ⚠️ `Character_creation` 是 RPG 词条（掷骰/加点/职业模板），页面自带跳转 "see Characterization"。需求方给的 URL 常指这个错条目 |
| 角色类型学 | `Character_(arts)` | round/flat（Forster）、dynamic/static、亚里士多德 ethos"角色即抉择"、荣格原型 |
| 弧光 | `Character_arc` | 弧光与三幕并行：激励事件→第一转折点→戏剧性问题→高潮作答 |
| 配角/陪衬 | `Foil_(narrative)` | 词源=垫宝石的箔片；反派可兼 foil；副线可作主线 foil；straight man |
| 前史/创伤 | `Backstory` | Orson Scott Card 记忆倒叙规则（不能凭空巧合，须被当下事件触发） |

## 类型惯例
| 类型 | 条目 | 关键段落 |
|---|---|---|
| 总纲 | `Film_genre` | "conventions, iconography, settings, narratives, characters and actors"；观众期待是构成要素 |
| 悬疑 | `Suspense` | 两种悬念：结果不确定（who/what/how）vs 结果必然（等待 when） |
| 误导线索 | `Red_herring` | 假线索必须"看似可信"（seemingly plausible） |
| 爱情 | `Romance_film` + `Meet_cute` | 障碍谱系（钱/病/歧视/心理/家庭）；meet-cute 铁律（Axelrod 台词） |
| 动作 | `Action_film` | 奇观 vs 叙事之争（Bordwell/King/O'Brien）；Tasker 主题；三幕=生存/抵抗/复仇 |
| 恐怖 | `Horror_film` | "dread of not seeing / horror of seeing"；jump scare 反套路制造持续不安；不协和音 |
| 喜剧 | `Comedy_film` | 大团圆惯例（dark comedy 除外）；farce/slapstick/sitcom 机制 |
| 结构史 | `Dramatic_structure` + `Three-act_structure` | Freytag 五段；亚里士多德实为两幕（complication+dénouement）；戏剧性问题列表 |

## 对白体系
| 主题 | 正确条目 | 陷阱/要点 |
|---|---|---|
| 对白写作 | `Dialogue_in_writing` | ⚠️ `Dialogue_in_fiction` 404（页面已删）；`Dialogue` 是通用沟通条目（哲学/传播学，别用）。要点：Sloane 铁律"对白必须同时干多件事"、said 话标 vs said-bookisms |
| 潜台词 | `Subtext` | 斯坦尼斯拉夫斯基源头；on-the-nose 批评；电影潜台词六手法清单 |
| 交代/信息 | `Exposition_(narrative)` | infodump 与 idiot lecture（"As you well know..."）禁忌；incluing（Jo Walton 定义） |
| 独白 | `Monologue` | 四类型：active/interior/dramatic/narrative；罗马喜剧 linking monologue=时间压缩 |

## 序列 + 副线
| 主题 | 正确条目 | 要点 |
|---|---|---|
| 结构理论全集 | `Screenwriting` | 最值钱的一页：含 Frank Daniel 八序列法（"sequence approach"节，2+4+2 序列对应三幕，每序列=迷你三幕、序列解决=下一序列启动情境）、Syd Field 范式节拍页数表（midpoint ~p60、pinch I/II ~p45/75、plot point 定义）、Bordwell/Thompson 四幕（《碟中谍3》每幕时长实测） |
| 副线 | `Subplot` | ⚠️ `B_story` 301 重定向到本页，二者同一条目，引用合并。要点：副线四区分标准（戏少/事件少/世界影响小/角色次要）；Mr. Robot 副线改写主线障碍交织范本 |

## 工具坑（本次实测）
- **search_files 在 Windows 主机对 `C:/...` 路径报 "系统找不到指定的路径"**（目录+glob 形式同样失败）→ 改回 terminal grep（MSYS `/c/...` 路径可用）。read_file 不受影响，可继续用。
- **并行任务同页同名提取覆盖**：本任务页目录里已有并行 agent 的 pro-writing-subplot.txt；覆盖前核对来源 URL 相同（同页同内容）即无害。原则：不删他人文件，同名覆盖仅限同 URL。
