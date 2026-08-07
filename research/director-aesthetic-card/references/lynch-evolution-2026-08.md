# 林奇手法体系深化轮 · 轮次详情与新坑（2026-08-07）

> 轮次：跨作品演变矩阵（手法体系深化变体）。产出：技法卡片源稿/林奇_手法体系深化.md + 地图 film-suite-research/references/lynch-evolution-2026-08.md
> 校验：82 英文引文 0 MISS（脚本 film-suite-research/_verify_lynch_deep.py）

## 轮次概要（供参考/对照）

- 零存量全新建档：8 档 pages/（英维 David Lynch 主条目 + Eraserhead/Blue Velvet/Twin Peaks/Mulholland Drive/Inland Empire + 中维大衛·林奇），S1-S7 自建编号（无主卡片变体第五型）。
- 双创作线：小镇噩梦线（橡皮头→蓝丝绒→双峰）/ 好莱坞梦魇线（失速公路→穆赫兰道→内陆帝国）。**双线定义直接文献=英维导演主条目 Themes 段一次给全**（"the folksiness of small town America collided with utter depravity..." vs "the celluloid dreams of Los Angeles [against the] bitter realities..."）——深化轮线定义优先扫导演主条目 Themes/Style 段，一次拿双线。
- 梦的语法五阶段演变链：生理恐怖（橡皮头，音乐入梦原点）→欲望结构（蓝丝绒，"a dream of strange desires"）→叙事装置（双峰，"破解梦境找出凶手"）→结构容器（穆赫兰道，愿望满足+创伤泄漏）→无梦者之梦（内陆帝国，Upanishad 蜘蛛引文=终点锚）。每阶段带林奇原话/带引文献锚点。
- 声音设计链：工业底噪（橡皮头，Splet 一年音效）→歌曲入梦（蓝丝绒 In Dreams）→firewood 柴火法（穆赫兰道，Badalamenti 10-12 分钟慢速音轨取碎片）→声音揭穿幻觉（Club Silencio "No hay banda"=马格里特《这不是烟斗》音乐版）。
- 预设处置：任务预设「小镇噩梦线（橡皮头→蓝丝绒→双峰）」中橡皮头小镇属性**证伪**（实为工业城市公寓，费城工业记忆为美学原点）→修正为「工业城市噩梦→小镇噩梦」两段式写入诚实声明；「好莱坞梦魇线（穆赫兰道→内陆帝国）」**修正起点**=失速公路 1997 为三部曲首环。
- vs 今敏/费里尼梦境三系：梦魇之梦/剪辑之梦/剧场之梦；三家共享铁律「影像层必须实」+「梦境无标记」（独立发明）；提炼句=费里尼布景搭梦/今敏剪辑穿梦/林奇恐惧做梦。

## 新坑（本轮四例）

### 新坑 1 · enwiki API 429 限流 → `?action=raw` 直连兜底
- 现象：`api.php?action=query&prop=revisions&rvprop=content` 批量抓取（连抓 6 条）触发 HTTP 429 Too Many Requests。
- 解法：改 `https://<lang>.wikipedia.org/wiki/<标题>?action=raw` 直连 wikitext，请求间 sleep 3s 稳定连抓（本轮 8 档全成）。`action=raw` 是轻量端点，不受 API 配额频控影响。
- 重定向：返回 `#REDIRECT [[目标]]` 存根照样可辨（读目标条目名再抓），与 API redirects=1 探测互补。

### 新坑 2 · `{{blockquote}}`/`{{quote}}` 模板内文被通用剥壳吞掉
- 现象：`while '[[' in s` 通用模板剥壳会把 `{{blockquote|Ideas are like fish...}}` 整段吞掉——钓大鱼引文 4 条假 MISS。
- 解法：校验前先 `re.sub(r'\{\{blockquote\|(.*?)\}\}', r'\1', raw, flags=re.S)`（quote 同法）保内文，再做通用剥壳。与陈凯歌轮 cquote 吞文同族，本条为通用 recipe（blockquote/quote 两模板名都先保）。
- 变体：`{{Cite magazine |title=...}}` 标题引文同理被剥壳吞掉（Rolling Stone 讣告标题即此例）——对「标题即引文」用 **RAW 直验通道**：不经模板剥壳、只做 norm 的原始文本再匹配一次（S5-RAW 模式，与陈凯歌轮 RAW_CHECKS 直验同族）。

### 新坑 3 · 校验 norm 去引号字符
- 现象：存档侧 `a "poisonous valentine to Hollywood."` 带内嵌引号、文档侧短语不带（或反之），假 MISS。
- 解法：`re.sub(r'[\'"`]', '', s)` 加入双侧 norm。引号三形态归一（㊿）之后再加这层——三形态归一处理「引号本身是什么形态」，去引号处理「引号出现在短语中间而非两端」。

### 新坑 4 · 跨文档编号与本文 S# 混编的校验正则
- 现象：正文同时存在本文 [S#]（S1-S7）与并行轮产物 [卡穆兰·研S#]（数字同样是 1-22）——裸 `\[S(\d+)\]` 会把研S# 误算进本文编号越界检查。
- 解法：本文 S# 一致性正则用负向断言 `(?<!研)\[S(\d+)\]` 排除研S#；或先单独提取 [卡X·研S#] 集合，从本文 S# 集合中剔除。与「转引编号一致性校验三坑」③（字符串元组 int 化）并列，同为脚本侧先怀疑。

## 本轮渠道实测备忘

- **导演主条目 Themes/Style 段 = 跨片总括金矿**：英维主条目 Themes 段一次拿到双线定义+产业母题+1950 年代观+直觉观+Upanishad（与宫崎骏轮 zhwiki 主条目总括句互补——en 侧重批评共识与引文富集，zh 侧重生平）；深化轮新抓第一优先仍是导演主条目 raw。
- 并行轮共享 pages/：写作中途《穆赫兰道》并行轮 20+ 档落盘（lynch_md_*），定稿前《穆赫兰道_技法卡片》《穆赫兰道_研习报告》落盘（S1-S22 编号）——按 ㊴ 纪律补 [卡穆兰·研S#] 双向转引链并升级诚实声明 1；字节数相同 md5 不同的存档=同文异版（lynch_enwiki_main vs raw），正文以 raw 为准。
- 任务指定《梦境超现实题材密码.md》本机不存在 → 回测报告转述通道（李安轮同型）；Criterion《欲望之痛》为酷儿电影史长文非专属 essay，标注不升格。

## 蓝丝绒单片轮 2026-08-07（中断，供续跑轮复用）

> 林奇《蓝丝绒》单片研习轮（创作极=小镇表面/地下暴力），因代理迭代上限中断：**两份产出文件（研习报告+技法卡片）未写入**。以下取证状态与通道记录可直接续跑。

### 已存档（pages/ 可复用）
- `lynch_bv_enwiki_raw.txt` 65.8KB（英维 Blue Velvet (film) raw，含 production/themes/legacy 段）+ `lynch_enwiki_main.txt` 230.9KB（英维 David Lynch 主条目）
- `lynch_bv_zhwiki_raw.txt` 7.8KB（中维「藍絲絨」）+ `lynch_zhwiki_main.txt` 30.2KB（中维大卫·林奇）
- `lynch_bv_baike_jina.txt` 55.4KB（百度百科蓝丝绒词条，含「平静外表下隐藏的性、暴力、犯罪和权力」直接印证小镇表面/地下母题）

### 标题形态学（中维）
- 真实条目名 = 繁体**「藍絲絨」**无后缀；「蓝丝绒 (电影)」「藍絲絨 (電影)」「蓝丝绒」三候选全 MISSING——探测序列先繁简裸名后后缀。
- **手写 %XX 编码必错（絨=%E7%B5%A8，手写 %E7%B5%B8 是「綸」整链 404）**；生成式写法：`URL="https://zh.wikipedia.org/w/index.php?title=$(python -c "import urllib.parse;print(urllib.parse.quote('藍絲絨'))")&action=raw"`。
- **rest_v1 Not_Found 错误正文会显示服务端解码后的标题**（`The specified page (藍丝綸) does not exist`）——404 时先读错误正文解码结果逐字比对定位编码手误，再怀疑标题形态（蓝丝绒轮 3 次手写编码错全由此定位）。

### 新通道：Wikidata = 同名消歧 + 硬数据锚点
- `action=wbsearchentities&search=<片名> film&language=en` 区分电影/歌曲/专辑同名实体（Blue Velvet 歌 vs Q660950="1986 film by David Lynch" 一次定位）。
- `Special:EntityData/<Q>.json` claims 字段：P345=IMDb id、P577=首映日、P2047=片长（121/119 双口径并存）、P136=类型、P750=发行方——正文硬数据可直接引用（蓝丝绒：tt0090756 / 1986-09-19 北美 / 双口径 121·119）。
- ⚠️ 豆瓣 id 属性（P9829）常缺失（本片无），勿依赖 Wikidata 拿豆瓣 id。

### 豆瓣 id 定位全渠道失败记录（续跑轮先读 douban-rexxar-api.md 的验证端点节）
- j/subject_suggest 空数组（简繁/中英四形态全 `[]`）、rexxar suggestion 退化（只回 2025-26 无关新片）、search.douban.com 经 jina 只回两部周边纪录片（27058856/37228575，本体不在结果）、m.douban /v2/search 需登录（code 103）、api.douban.com/v2 需 apikey（code 104）。
- **百度搜索经 jina 兜底可用**：`r.jina.ai/https://www.baidu.com/s?wd=<词>` 40KB 结果页，baidu /link?url= 跳转壳可 `-L` 跟随拿真实 URL；但**第三方快照里的 id 不可信**（「1298697-豆瓣 7.6-蓝丝绒」实为盗版站假 id，rexxar /v2/movie/1298697 返回 need_permission 证伪）。
- 未完成项：Ebert 影评（great-movie-blue-velvet-1986 待 CDX 定位）、Criterion essay（本片无 Criterion 发行，Current 搜索待负面取证）、豆瓣长评（subject id 未确认，可改从英维 ref 的影评原文替代）。
