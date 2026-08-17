# 制作大师卡片研习轮工作流（2026-08-09 和田惠美轮 / Schoonmaker 剪辑轮实测）

任务形态：为制作岗位大师（声音/美术/服装设计等）产出《<大师>_制作大师卡片.md》，一轮多位大师并行（子代理各产一份）。属「导演美学卡片」同族卡片轮，但对象是制作岗位而非导演——来源组合与取证侧重不同。

## 启动步骤

1. **读规范与模板**：规范在 `_work/制作大师研习-<日期>/规范.md`（8 节结构、来源纪律铁律、工作目录约定）；模板参考**上一轮**已入库卡片——不要死磕技能库里 `_knowledge/references/制作学科/大师卡片/` 路径（可能未同步），先 `find` 全盘找 `*杜笃之*` 之类上一轮卡片（实测在 `_work/制作大师研习-20260808/杜笃之/`）。
2. **建目录**：`_work/制作大师研习-<日期>/<大师>/` + `pages/` 子目录存原始抓取（HTML + 提取 txt 都留）。
3. **模板 8 节结构**（对齐规范）：①专业签名（一句话）②美学体系（手法|成片实例|取证来源表格）③创作思路（原话+出处）④招牌作品拆解（1-2 部）⑤可复用时机（映射目标类型的表格，标注"分析框架非本人自述"）⑥AI 提示词对接（EN + 中注，按取证要点编写非原片描述）⑦诚实声明 ⑧附录来源清单（编号|存档文件|来源|关键内容）。
4. **来源编号纪律**：S1–Sn 贯穿全文，每条论断带编号；附录表与正文编号一一对应。

## 服装设计大师来源组合（和田惠美轮实测）

| 来源形态 | 实战表现 | 价值 |
|---|---|---|
| 英文维基（en.wikipedia.org/wiki/<名>） | curl 直抓 ✓ 134KB | 生平/奖项表/作品年表/获奖年份（13 提名 6 获奖） |
| 中文维基 | 路径 URL 报「标题无效」→ 走 action API（配方见下） | 华语圈奖项细节（金像奖历年）+ 一手访谈线索（ref 区含 LA Times 专访 URL） |
| 讣告（Guardian obituary） | curl 直抓 ✓ | **引语金矿**：历年本人原话（奥斯卡致辞、创作观、原则性拒片）+ 制作数字（工期/件数/预算） |
| 行业媒体访谈（路透传真经 Backstage 刊载） | curl 直抓 ✓ | 本人核心信条原文（"What the costume must express is character"） |
| 大报人物专访（LA Times / 第一财经中文） | 直抓 ✓ | 工作方法细节（自染、织机、色阶执念）+ 合作者（导演）评语 + 轶事 |
| Criterion essay | /films/ 页 curl 拿壳 → **r.jina.ai 代取 ✓**；essay 全文 /current/posts/<id>-<slug> 也走 r.jina.ai ✓ | 作品美学定位（权威影评视角） |
| 影迷深度分析（Deep Film Analysis 等 rewatch-guide） | 直抓 ✓ | 结构性分析（如《乱》三兄弟色系映射 Taro 黄/Jiro 红/Saburo 蓝）——**必须标注"影迷分析"**，具体对应关系仅一处给出时与访谈/影评交叉印证 |
| 影评博客悼文（Film Experience） | 直抓 ✓ | 颁奖夜细节、合作导演评语、读者评论（有时含制作量洞察） |

## 服装设计大师特有问题

- **服装数量双口径**：《乱》近千套（卫报）vs 1400 套群演军服（Ran 英文维基）vs 千余套（LA Times）——口径不同（总数 vs 群演军服），**并列列出不调和**，诚实声明节说明。
- **访谈简化 vs 成片叙事**：和田自述《英雄》"只用了红、白、蓝三种色调"与影评通行的五色段落（红白蓝绿黑）说法并存——双口径如实列出，不替她圆。
- **成片视觉断言必须声明未逐帧看片**：三兄弟色系=性格命运的"成片表现"来自影评/影迷分析而非本人逐帧验证——拆解节引用时保留署名。
- **工艺细节优先取本人自述**：染织/手作/材料是服装大师的方法论核心（"All the sample dying I do myself... In all cases"），比奖项列表更有复用价值。
- **剧作解读陷阱**：不要用外部来源的剧情分析冒充服装设计分析——只取与服装/色彩/材质直接相关的论断。

## 本轮实测配方

### zh.wikipedia 非 ASCII 标题修复

```bash
curl -sL -A "$UA" --get --data-urlencode "action=parse" --data-urlencode "page=和田惠美" --data-urlencode "format=json" --data-urlencode "prop=wikitext" --data-urlencode "formatversion=2" "https://zh.wikipedia.org/w/api.php"
# .parse.wikitext 即正文（含模板/表格需自解析）；ref 段可挖一手访谈 URL
```

路径 URL（`/zh-hans/和田惠美`）直抓返回「标题无效 / invalid UTF-8」错误页；`--data-urlencode` 避免 curl 对中文标题的编码问题。英文条惯用的 `prop=extracts&explaintext=1` 在 zh wiki 同样可用但返回渲染文本；`prop=parse&prop=wikitext` 胜在保留 `<ref>` 引用区（= 一手来源 URL 金矿）。

### HTML→txt 提取

无 bs4 时用 sourced-web-research 自带 `scripts/extract_text_stdlib.py`，或内联 Python HTMLParser：跳过 script/style/nav/header/footer/aside，块级标签注入换行，折叠空行。卫报等大站抓回后先 wc -c 确认 >10KB 再提取。

### 英文站弯引号 grep 验证陷阱

卫报正文用弯撇号（doesn’t / American’s），直撇号模式 grep 必 MISS——**验证模式去掉撇号**（用 "figure doesn" 会 miss，改用 "six in the morning" 这类无撇号子串），或先做弯引号→直归一化（见 quote-verification.md）。中文引语验证直接用原句片段（"就算没有钱，我们自己付钱"）无此问题。

## 剪辑/声音大师来源组合（2026-08-09 Schoonmaker 轮实测）

| 来源形态 | 实战表现 | 价值 |
|---|---|---|
| 英文维基主条目 | r.jina.ai 代取 ✓ 80KB | 奖项纪录（9 提名 3 获奖=双纪录）、领奖致辞转引（"he edited this film with me every minute of the time... pure gold"）、工会受阻生平（1970s 无法署名）、完整片目 |
| **Art of the Cut**（Steve Hullfish 采，剪辑师第一访谈品牌） | 两个托管站均 r.jina.ai ✓：provideocoalition.com（2017《沉默》）、borisfx.com（2023《花月杀手》） | 逐字问答、信息密度最高：工作流程（dailies 共看/降序 selects/冷眼原则/试映 12 次）、工具观（Lightworks 控制器与 24 轨同步参考系统/绝不用 temp music）、动作戏技术细节（rheostat 变速/48–120fps/动物呼吸声） |
| **CineMontage**（Editors Guild 工会官方刊物） | r.jina.ai ✓ | 剪辑师专属行业媒体：导演-剪辑合作机制原话（"He thinks like an editor on the set... 50 percent of my work"） |
| 翠贝卡座谈报告（No Film School 详细版 + Cinephilia & Beyond 转录版） | r.jina.ai ✓ | 同一座谈两手交叉印证：拳击戏主观节奏（赢/输两种语法、多档慢镜、手抽帧）、声音剪辑细节（一拳一音、动物声、40 声轨）——**区分"转录"与"转述"**，转述版论断与详细版对照后再引用 |
| 老访谈（1991 Wide Angle/Closeup 双段逐字问答） | 直抓 ✓ 33KB | 方法论金矿：剪辑室关系、分歧案例（镜子戏 15 take 冷暖之争）、"I get credit really for what he does" |
| 一般媒体访谈（HuffPost 2013 自述 / The Quietus 2016 / Den of Geek 2016 / Guardian 2023） | r.jina.ai ✓ | 本人自述信条（"search for the truth... never explain"）、纪录片训练背景、Powell 遗训（"Never explain and always try to be ahead of your audience"） |
| Criterion essay | 旧 URL（posts/1571）已失效跳首页 → **搜索确认正确 post id（813）再抓**；r.jina.ai 取到正文但**作者署名行丢失** | 影评定位（"hailstorm of body blows"观感），非剪辑技术分析——只作地位佐证，作者信息缺失写入诚实声明 |
| 二手解读（StudioBinder / Far Out Magazine） | r.jina.ai ✓ | 仅作背景参考，具体论断不单独作为依据 |

### 剪辑大师特有问题

- **导演-剪辑分工论断要归位**：拳台尺寸/机位/节奏蓝图是导演的构想，剪辑师的任务是"让它更可信"（"my job is to make it MORE believable"）——卡片论断区分"导演构想"与"剪辑实现"，别把导演功劳算给剪辑师（她本人反复强调这点）。
- **成片技术断言（慢镜档位/抽帧/声轨数）优先取本人访谈原话**（48/72/96/120fps、40 tracks、rheostat），影评/二手文作交叉印证。
- **"剪辑=表演再创作"类概括语**：无逐字原文的概括（如网传"剪辑是表演的再创作"）标注为概括，附最接近的一手表述（"We go for performance and emotion"）——不许当逐字引语。
- **未逐帧看片声明必写**：成片表现描述（拳台尺寸、变速段落位置）全部来自访谈/转述，未经画面核对。

### r.jina.ai 批量并发抓取（省调用核心模式）

terminal 工具禁止 `&` 后台，逐条 curl 会烧光调用预算 → **execute_code + concurrent.futures.ThreadPoolExecutor(max_workers=5) + urllib** 一次抓 10 页落盘 pages/（本轮 22 秒完成）。抓取函数要点：`https://r.jina.ai/<目标URL>`、UA 用 Mozilla/5.0、异常捕获返回 ERROR 不中断整批。

### 噪声页正文定位

HuffPost 等门户 81KB 中前 170 行全是导航/广告 → `grep -n "Interviewed by\|THELMA SCHOONMAKER"` 定位访谈锚点，read_file 精确段；多个小文件正文一次读完用 execute_code 截断打印（每文件 6.5KB 窗口 + [TRUNCATED] 标记）。

### grep 验证三陷阱（Schoonmaker 轮实测，0 MISS 收尾）

1. **r.jina.ai 提取保留 markdown 强调符**：`removed _by hand_`——引文按原文含标记匹配，或改用无标记子串（"frames are removed to give a stuttering aspect"）。
2. **弯引号（U+2019）**：源文 it’s/you’re 弯撇号，直撇号模式 grep MISS——本轮写卡后修了 4 处（it's like a puzzle 等）；最省做法是引文直接从存档文件复制，或先归一化。
3. **验证后修卡闭环**：写卡后跑全量 `for q in "<引文>"; do grep -l "$q" pages/*.txt; done`，MISS 项逐个核对源文件原文 → patch/脚本替换修正 → 复验全绿。更省的做法：写卡前先列引文清单批量 grep。

## 工具预算纪律

50 次调用上限：读规范+模板 2-3 次 → 并行搜索定 URL（3-4 次）→ 批量 curl 抓 4-6 页（2-3 次）→ 提取+精读（3-4 次）→ 写卡（1 次）→ grep 验证（2-3 次）。**先抓核心来源再写，写不完也要先落盘 pages/**。被拦来源（如日文站 CINRA、奥斯卡演讲原文）如实写「未取证到」，不编造。
