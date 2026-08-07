# 黑泽明轮来源地图（手法体系深化第九例，2026-08-07）

产出：`film-suite-research/技法卡片源稿/黑泽明_手法体系深化.md`（290 行/44KB，19 取证来源，附来源表）。
对照资产：`黑泽明_导演美学卡片.md`（第八轮前产出）、七武士/乱/罗生门技法卡片（本地）、胡金铨/徐克深化专题（4.x 对比节转引链）。

## 本轮新抓存档（pages/）↔ 内容要点

| 存档文件 | 来源 | 关键内容 |
|---|---|---|
| kurosawa_wiki_Throne_of_Blood_v2.txt | Wikipedia《Throne of Blood》（新抓） | 黑泽明点名要雾自述（「我早就决定这部电影要很多雾」+富士山坡因常雾而选）、黑墙衬雾（Muraki）、真箭射三船（三船挥臂示意移动方向）、圆谷英二特效（森林移动，黑泽明嫌长剪掉若干镜头）、Noh（yaseonna 老女面/笛鼓）、Richie「雾风树霾」、Prince 水墨比、Harold Bloom「最成功的麦克白电影版」、因威尔斯 1948《麦克白》延迟、Legacy 段记 1985 再改编 Lear |
| kurosawa_wiki_Yojimbo.txt | Wikipedia《Yojimbo》（新抓） | 玻璃钥匙/红收获来源之争（Desser/Farber vs Richie）、杉野嘉雄（天真正伝香取神道流）剑术编排、Sanjuro 续集缘起（Hibi Heian 改写）、「无名人」原型、Leone 抄袭诉讼、Michael Wood 配乐评论（「他头脑的声音」）、两部同款旧和服同族徽 |
| kurosawa_wiki_Sanjuro.txt | Wikipedia《Sanjuro》（新抓） | 九人浪人组社会喜剧（老手被年轻人拖累）、「好刀收在鞘里」（藩夫人）、终局血喷=有意实验（1980 访谈，黑泽明嘲笑复制者）、「出鞘的刀」镜像双雄、续集西部元素弱化 |
| kurosawa_criterion_yojimbo.txt | Criterion《Yojimbo: West Meets East》（Sesonske，新抓全文） | 「Yojimbo, by Shane out of Scarface」、「道德热忱够多了，我来让你看看我有多西」、主角近 Sam Spade 非 Shane、恶党=黑帮片产物、暴力「快得眨个眼就错过」、「最长的暴力场景没有人类受害者（作舞台布景）」、Leone「几乎逐镜抄袭」 |
| kurosawa_criterion_sanjuro.txt | Criterion《Sanjuro: Return of the Ronin》（Sragow，新抓全文） | 年轻武士几何队形 vs 三十郎瘫/挠/打盹（群像调度直接证据）、「像镰刀切入敌群」、「抽象而圆形的美」、终局决斗的恐怖与美 |
| kurosawa_criterion_yojimbo_jina.txt | 误抓存档：URL 实指 Criterion Kagemusha 影评《From Painting to Film Pageantry》 | 内容仍有用（画家出身/分镜传统/四年脑内执导/1960 年代起「日本 Lear」执念），已如实标注；对应正片链接在正文中说明 |
| kurosawa_wiki_Throne_of_Blood_v2.txt 前身 kurosawa_wiki_Throne_of_Blood_.txt | Wikimedia 404 错误页（旧轮标题猜测失败） | 真实条目名就是 `Throne of Blood`（无年份消歧），猜测 `Throne_of_Blood_` 尾下划线等变体全 404 |

## 本轮实测的抓取配方（新，均验证可用）

### 1. Criterion 旧 post 数字 ID 会重定向到无关 essay（大坑）
- `criterion.com/current/posts/360-yojimbo-west-meets-east` → 实际返回 **Kagemusha** 影评；`posts/150-throne-of-blood-shakespeare-transposed` → 返回 **The Ruling Class** 影评。旧 ID 早已换页，slug 也不能信。
- 解法（两步，实测有效）：
  1. CDX 按 urlkey 过滤 + collapse 去重找真实快照：
     `curl "http://web.archive.org/cdx/search/cdx?url=criterion.com/current/posts*&filter=urlkey:.*yojimbo.*&limit=10&collapse=urlkey"`
     （此 filter=urlkey 模式对 criterion 域有效——与 playbook 里 theguardian 通配 403 的坑是不同域不同表现）
  2. 抓 `https://web.archive.org/web/<timestamp>id_/<原URL>`（`id_` 返回原始 HTML，无 Wayback 头尾注入），python 从正文标记（如 "Related Films"）截取，`re.sub(r'<[^>]+>',' ')` + `html.unescape` + 压空白。
- 抓后必须验证：查 `<title>` 或正文首句作者/篇名，别信 URL slug（黑泽明轮两次误抓都靠 title 发现）。

### 2. Wikipedia REST plaintext 端点 404 → 用 prop=extracts
- `en.wikipedia.org/api/rest_v1/page/plaintext/<Title>` 对 Throne of Blood / Yojimbo (film) / Sanjuro 全部返回 404 JSON。
- 可用替代（支持一次多条目）：`https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&format=json&titles=<T1>%7C<T2>&redirects=1`
  ⚠️ 多标题请求里缺失/重定向条目 extract 为空（实测三标题只回 Sanjuro）——**逐条单查最稳**，别信批量结果。

### 3. execute_code 与 terminal 的 cwd 不同（存盘坑）
- terminal `cd pages/` 之后，execute_code 里 `open('相对名','w')` 写到的是会话工作目录（~Documents/Hermes），不是 terminal 的 cd 目标——本轮回文件多花一步 mv。
- 规则：execute_code 写文件一律用绝对路径；或写后立即核对 `find ~ -name <文件>`。

### 4. r.jina.ai 挡 web.archive.org，直连可行
- jina 抓 wayback 返回 403 AbuseAlleviationError（匿名访问被 DDoS 保护拦）→ 不用 jina，`curl -L` 直连 `web.archive.org/web/<ts>id_/<url>`（带 Mozilla UA）成功。

## 本轮关键产出（后续轮次可直接复用）

- **天气三级演变证据链**：罗生门雨（Ebert「雨毫不含糊分开现在与过去」+自传黑墨水雨+**晴天/阴天平行拍摄日程**——黑泽明按天气分轨拍片）→ 蜘蛛巢城雾（自述点名要雾+黑墙衬雾+Richie「以少成多：雾风树霾」）→ 乱云（Jim's 雷云预告↔血日落首尾对仗；「等云数周」注明 Ran 拍摄期实际没等）。旁证：野上照代回忆录书名《Waiting on the Weather》。
- **多机位三级**：七武士（Richie p.104/Kobayashi p.250：三机不同角度、为捕捉群众动量）→ 罗生门（Kauffmann「从一段飞向另一段」+407 镜头）→ 乱（Jim's「经常三机同拍、不同镜头不同机位」）；中间站影武者 5000 群众演员→成片 90 秒（Lucas 语）。
- **莎剧日本化三招**：换容器（蜘蛛巢城 Noh 化麦克白，Yamada 被要求当日本经典演）→ 换时代（恶汉甜梦 Hamlet 进财阀办公室）→ 换魂（乱 Lear+毛利元就传说融合+补前史「Shakespeare gave his characters no past」+秀虎=我）。
- **群像调度三级**：七武士动作即面试（S36–45 本地卡片）→ 椿三十郎几何队形 vs 散漫主角（Sragow）→ 乱焦点后置、大军成抽象色块（Prince 评论轨）。
- 「让演员只演一次」= 提炼句（黑泽明原话未取证到），事实基础=三机同拍不同角度+剪辑自由描述。

## 未取证/待办清单
- 黑泽明「让演员只演一次」原话（本轮未取证到，正文已标提炼句）。
- Criterion Prince《Throne of Blood: Shakespeare Transposed》essay：post 150 重定向错误后未再追正确快照（维基转引 Prince 已够用，可留待）。
- 中文渠道（豆瓣/百科）依然全挂，同导演美学卡片声明。
- 同批次并行产出坑：任务称「蜘蛛巢城/用心棒/椿三十郎技法卡片同批并行产出」，但落盘时目录中没有——**跨代理批次产物可能晚到，引用前先 ls 核对，并在诚实声明注明以维基/Criterion 为据待互校**。
