# 是枝裕和《步履不停》研习轮来源地图（2026-08-07）

任务形态：单部片范本深挖（研习报告 + 8 张技法卡片，输出到 film-suite-research/研习报告 与 技法卡片源稿/）。**剧本大概率无**——本轮实测确认：IMSDb 搜索为空壳（仅回显查询词）、DDG 经 jina 只有维基/Criterion 结果、无公开英译剧本。未写剧本原文文件，诚实声明标「未取到」。

## 本轮新增存档（pages/walking_*.txt）

| 存档 | 内容 | 用途 |
|---|---|---|
| walking_criterion_lim_par.txt | Dennis Lim《Still Walking: A Death in the Family》Criterion 论文全文（2011-02-07，post 1743） | 结构/对白/「no epiphanies」「passive aggression」「crosscurrents of small talk」等核心引文 |
| walking_crit_2610_par.txt | Michael Koresky《Pain and Nourishment: Kirin Kiki》（post 2610，2013） | 厨房开场特写/躲热油/methodical love/唱片抱胸/导演 2008 年「wasn't there in time」引语 |
| walking_crit_7238_par.txt | Ben Elias《In Another Room, from Another Time》（Songbook，post 7238，2021） | **台词转述金矿**：「That wasn't me. That was Junpei.」无人听见、隔浴室门坦白全文、蝴蝶焦点后移手巾、「Just a butterfly」、录音棚还原玉米声幕后 |
| walking_beiqing_interview_body.txt | 北青报系导演访谈转帖（豆瓣小组 5626608，楼主 gawe 2009-04-25，繁体） | 一手级创作思路：初稿 8 天、剧本从早上厨房场景开始、房子当主角（80% 室内）、前后景同演+用声音创造空间、「什么事都没发生的故事」、树木希林假牙/摸刘海台词来自真实生活 |
| walking_review_2211632.txt | 豆瓣长评《逝者如斯夫》（4713 有用） | 餐桌器物/「三顿饭两个步」/告别握手「总之到哪都会牵着你」/瓷砖碎片 |
| walking_review_2184484.txt | 《真是谁也停不下的步履》（150 有用） | 「什么事都没发生」导演引语中文版 + 摸刘海台词 |
| walking_review_8939405.txt | 《人生路上步履不停，为何总是慢一拍》（820 有用） | 逐场台词转述最多：擦鞋/干净鞋子/「我挣的钱足够维持一个寡妇的生活」/「我反正也等不了20年了」/浇碑「天气很热」/遗像入全家福 |
| walking_review_1990765.txt | 木卫二《那些没赶上的事情》（277 有用） | 结尾摇升镜头明暗分析；**文末附北青报访谈小组话题链接**（渠道线索源） |
| walking_review_1952314.txt | 木卫二《总是慢上一拍》（170 有用） | 固定镜头/例外运动（追蝴蝶、吊臂摇升）；日本时报等外评转引 |
| walking_review_8349137.txt | 《这慢一拍的人生啊》（93 有用） | 「外婆的家」甩门/浴室排水口瓷砖隐喻/隔门说破出轨 |

## 新渠道实测（本轮验证）

1. **豆瓣小组话题（group/topic/<id>/）经 r.jina.ai 可取主帖全文**——非 JS 壳！导航噪音多但正文完整（访谈转帖就是主帖）。此前技能只记录了「长评=访谈转帖通道」，本轮发现**小组话题是同类的第二条通道**。发现路径：长评正文文末常附访谈转帖链接（木卫二 1990765 文末 href），扫 reviews 时连正文链接一起挖。
2. **Criterion essay 三篇全部 live curl 直抓**（posts/1743、2610、7238，UA 普通 Chrome 即可）——再次印证「别猜 post id，从影片页 HTML grep」：`grep -oE 'criterion\.com/current/[a-z0-9/_-]*(posts|features)[a-z0-9/_-]*' <影片页>.html`。
3. **HTML→文本提取改进**：Criterion 文章是单行大段，纯压空白后不可读；先 `re.sub(r'</p>','\n\n',t,flags=re.I)` + `<br>`→`\n` 再剥标签，段落可读性大幅提升（正文从约行 274 起，导航在前）。
4. **Rexxar 长评接口再次验证**：suggest（q=步履不停→id 2222996）→ reviews?sort=hotest 列表（id/useful_count/title 一眼选出 4713 有用的）→ review/<id> 全文，0.4s 间隔连抓 6 篇无压力。短评接口 comments 本次返回空（status=P 参数），不影响长评通道。

## 预设纠正（写进诚实声明的先例）

任务预设「母亲节家庭聚会」实为**长子忌日周年聚会**；预设「父子浴」片中不存在（对应场景是良多独自在父母浴室 + 父母隔浴室门对话）。**忌日年份来源矛盾**：英维基写 12 年前，Lim 与多篇豆瓣长评写 15 年前——正文不取固定值，声明中并列注明。处理方式与王家卫轮（立秋/节气字卡）同规：正文显式纠正 + 诚实声明逐条对照。

## 引文校验备注

- 「eavesdropping」在 Koresky 篇不在 Lim 篇——写报告时归错了文件，校验抓出；弯引号（' vs ’）与繁简（瀏海/刘海）会造成假 MISS，先标准化再判。
- 英文台词转述（Ben Elias 文）中文转译时注明「英文转述，中文转译」；豆瓣台词转述标「场景转述+台词」。
