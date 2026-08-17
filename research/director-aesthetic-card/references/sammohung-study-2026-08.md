# 洪金宝轮（Sammo Hung）研习记录 · 2026-08-09

> 武侠轴武指三大家收官轮。产出《洪金宝_导演美学卡片.md》+《洪金宝_手法体系深化.md》（_work/全链条研习-20260809/洪金宝/）。取证纪律同全轮（每条论断带 S 编号、原文 grep 验证 0 MISS、诚实声明）。
> 本记录只记**新通道/新坑/可复用引语锚**，通用流程见 SKILL.md 主体。

## 港片武指/喜剧动作导演轮来源地图（本轮验证）

### 新通道（此前未记录或未验证）
1. **新京报武行专题经中国日报网 exchange RSS 直抓**（`ex.chinadaily.com.cn/exchange/partners/77/rss/channel/cn/...`，2021-09-09 滕朝《用身体对抗好莱坞 老港武行，从不说不》）——武行文化一手转述金矿：洪家班"剪威亚"（《鬼打鬼》陈龙被踢飞撞屋梁、专人剪断威亚求真实坠落）、"洪金宝骂成龙跳钟楼"（《A计划》）、四大班底斗法（刘家班/袁家班/洪家班/成家班）、武行"Never say no"。**港片武指/动作片轮第一顺位通道**（百度百科"用身体对抗好莱坞"词条同文转载）。
2. **腾讯新闻 rain 频道深度人物稿**（`news.qq.com/rain/a/<id>`）——港星金像奖/颁奖季后专访转述通道，含一手引语（洪金宝"其实我很想再拍《五福星》，但是有的'星'已经走了"、"我找五个你不认识的人去做五福星，你会到戏院看吗？"）。直连 curl 带 UA 可抓（64KB）。
3. **头条 toutiao.com/article/ 直连是 JS 空壳**（72KB 无正文）——r.jina.ai 可取全文（6.3KB）。自媒体文章：数据（宾尼 63 场 58 KO、《黑带》杂志"史上最精彩打斗场面第二"）一律标二手，找不到原始出处写「未取证到」。
4. **豆瓣影评 movie.douban.com/review/<id>/ 经 r.jina.ai 直抓全文成功（本轮 2/3）**——与 Rexxar API 并列的豆瓣长评通道，jina 不再一律是登录壳；1 篇 404（页面已删，非反爬）。坑：搜索快照给 m.douban.com 域的 review URL 可能 404，换 movie.douban.com 同 id 重试。
5. **港星英文访谈三站**：flexiblehead.blog（Owen Williams，Empire 杂志访谈重刊，2014——含"动作喜剧让人开心""招牌是体型"原话；该系列与甄子丹同模板）、THR hollywoodreporter.com（2023 Filmart，Mathew Scott——"快乐的独裁者"/胡金铨师承/漫画灵感/信任原则）、lifestyleasia.com（AFA 颁奖季，数据+格言）。搜港星英文访谈优先这三站。

### 通用通道（复验）
- 英维主条目 366KB HTML：正文从「Film career」起、TOC 重复段跳过（章节名首次出现常在目录，取第二次出现位置）；Legacy/Personal life 段在文末。
- 中维主条目：作品表含逐片票房（洪金宝条目 1961-1990s 全表）——**中维票房数据可作"某片年度票房第几"的裁决源**。
- 片条目（败家仔/叶问）比人条目更细：《叶问》英维 "Stunts and choreography" 段含获聘原因（1978《赞先生与找钱华》+《败家仔》咏春经验）与洪金宝原话 "With my mouth."；《败家仔》中维含金像奖最佳武术指导四人名单（洪金宝/元彪/林正英/陈会毅）与香港电影资料馆"百部不可不看的香港电影"第 016 位。
- 百度百科人物主词条本轮 403 + jina 仅获消歧义页（`item/洪金宝` 是多义词）——如实声明；片词条（`item/快餐车/2768723`）经 jina 可取全文（10.5KB，含专业评价段）。

## 本轮坑（新增/再证）

- **urllib 抓中文 URL 报 `'ascii' codec can't encode characters`**：不是网络错误——urllib.request.Request 不接受未编码中文。必须 `urllib.parse.quote(url, safe=":/?&=%")`（jina 代理 URL 连目标 URL 一起 quote）后再请求。curl 不受此限但 jina/百度类走 urllib 时必踩。
- **页面体积不是内容证据（再证）**：头条 72KB=JS 空壳、jina 6.3KB=正文；豆瓣直抓 2964 字节=反爬壳、jina 4KB=全文。抓回先看头 200 字符判断是壳还是正文。
- **grep 验证 HTML 存档先剥标签**：验证函数=剥 `<[^>]+>` → 压空白（`re.sub(r'\s+',' ')`）→ `re.escape` 片段 + 上下文窗口打印。32 项 0 MISS。
- **双口径标注实例**（写进诚实声明）：
  - 《败家仔》年份三口径：中维 1981（通行）vs Empire 访谈中洪金宝口述 "1983" vs 英维《叶问》条目 "1982's The Prodigal Son"——采用 1981，其余标注。
  - 1985 年香港票房冠亚军：腾讯稿称"《夏日福星》和《最佳福星》两片包揽了1985年的票房冠亚军"；中维票房数据显示 1985 冠亚军为《福星高照》（30,748,643）与《夏日福星》（28,911,851），《最佳福星》（23,109,809）是 1986——媒体稿与票房数据矛盾，双口径并列不强行统一。
  - 《快餐车》动作指导署名：百度百科"成家班" vs 头条"洪金宝作为动作导演"——按"导演统筹+成家班挂名"处理并标注。
- **首部纯功夫喜剧三说并存**（与袁和平轮同口径）：刘家良《神打》1975 / 洪金宝《三德和尚与舂米六》1977（英维限定语 "what many feel to be the first"）/ 袁和平 1978 双片引爆。

## 三大家武指体系对比转引链（本轮用法，可直接复用）

- **对比节优先复用本地卡片**：袁和平侧引《袁和平_手法体系深化.md》4.2「vs 洪金宝」表与 4.3 三大家总表（标注"袁卡片引 [S#]"）；刘家良侧引《刘家良_导演美学卡片.md》（"My only aim... to exalt the martial arts"/反威亚/训练戏 1 小时），标注"刘卡片引"。**不重复抓取已入库人物**。
- 三大家一句话框架（本专题提炼，事实基础在表内）：刘家良=武术的传教士（门派正宗）、洪金宝=身体的杂技演员（奇观与笑声）、袁和平=动作的发明家（语言与情感）。⚠️ 提炼句与导演原话分离，注明事实基础。

## 已验证引语锚（洪金宝一手原话，后续轮可直接复用）

- "I like action comedy... I like them because I like to make people happy."（Empire 访谈）
- "I don't really have a signature move. My signature is my size. I love to do a lot of things so people will be shocked."
- "I don't retire. If you stop moving you will die."
- "King Hu was like an uncle, but more."（胡金铨师承）
- "the truth is I am a happy dictator on set. I am in charge but I am authentic."（THR）
- "I read a lot of comic books... make it seem real on the screen."（漫画灵感）
- "With my mouth."（被问如何与甄子丹合作设计《叶问》动作）
- "其实我很想再拍《五福星》，但是有的'星'已经走了，我心里很难过。"（腾讯 2024）

## 未取证到清单（本轮）

百度百科洪金宝主词条（403/消歧义）、Criterion 2024 访谈视频文字稿（仅节目简介）、《黑带》杂志"史上最精彩打斗场面第二"原始出处（仅头条转述）、洪金宝中文个人长篇访谈原文（南方人物周刊/澎湃类）。
