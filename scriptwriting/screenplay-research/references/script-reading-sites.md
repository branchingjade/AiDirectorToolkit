# 知名影视剧剧本阅读渠道（2026-08 调研）

用户场景：**阅读**著名影视剧的完整剧本（学习/参考），非剧本交易。全部渠道本调研中实测或经来源验证。

## 一、国内渠道（国产剧/国产片剧本为主）

### juben.pro（华语剧本网/中国编剧网）《剧本名作》
- URL：https://www.juben.pro/Famous/
- 国内稀缺的知名剧本阅读站。实测栏目内容（2026-08）：
  - 贾樟柯《小山回家》(1995)、沃卓斯基《黑客帝国》**中英对照**（独家）、贾玲《你好，李焕英》(2021)（独家）、乔乔的异想世界(2019)、荒野猎人、鸟人(2014)、托尼·厄德曼、婚姻故事、她(2013)、摄影机不要停、造梦之家、史蒂夫·乔布斯(2015) 等
  - 分类：豆瓣评分排行 · 原版剧本 · 奥斯卡获奖剧本
  - 短剧名作也有（《家里家外》79集）
- **权限实测（2026-08-05 登录验证，三次纠错：免费直读→登录即全→登录+VIP 才全→实际分页可读全本）**：未登录/免费会员登录后都**只读前 N 场试读**（《你好，李焕英》试读 9 场 3332 字符，页面标注全文 31990 字；《婚姻故事》同）。登录后还需点击「阅读剧本正文」按钮（`.btn-readBodyContent`）展开正文。**2026-08-05《摄影机不要停》实测推翻了"全文需 VIP"：正文按页加载，免费账号可逐页读完全本**——分页 URL 模式 `https://www.juben.pro/writing/{id}-{page}-ccontent-hpdefault.html`（第 1 页即原 `{id}.html`；页数看页脚"1 2 3 … N"）；每页 `document.getElementById('mainContent').innerText` 提取（WebBridge evaluate，navigate+提取循环），《摄影机不要停》13 页 32125 字符、场景 1–111 含结尾彩蛋完整读全，无需 VIP/积分。**"全文需 VIP"可能因作品而异——先试分页：页脚出现"下一页"就继续翻，既不要把首屏当全文，也不要在试读处放弃**。试读部分仍即国内标准格式实证范本：`1、职工医院新生儿室，日，内`（场号+地点+时间+内外）、对白人名+冒号无引号、画外音中文标注（`贾晓玲（画外音）：`）
- **质量实测（2026-08-05 抽查 4 部）**：国外片剧本为**专业译者译成国内标准格式的中文译本**——《荒野猎人》44747字译/曹轶、《鸟人》43977字译/吉晓倩、《婚姻故事》46883字译/闵泽霖（`内景，农舍，夜`）；《黑客帝国》104130字中英对照（站点诚实标注 DeepSeek 翻译未核对，授权版见 New Market Press 2000）——**学国内标准格式的最佳范本库**
- 来源：知乎回答「有什么网站可以找到国内电视剧剧本？」明确说"华语剧本网《名作》栏目发布了部分国内知名电视剧剧本和大量的国内外知名电影剧本"（https://www.zhihu.com/question/357488781）
- 结论：看国产剧/国产片剧本，juben.pro 名作栏目就是稀缺渠道，不用换。

### 豆瓣
- 搜「剧名+剧本」，有网友发布部分电视剧剧本（知乎回答推荐）。零散但偶有好货。
- ⚠️ 2026-08-05 实测：搜索接口不稳定（返回「获取搜索结果失败: 错误103」），作补充渠道，不作主渠道。

### juben98.com 剧本网
- URL：http://www.juben98.com/
- 中国剧本投稿交易门户；栏目含影视剧本/短剧剧本/小品剧本/剧本教程。班叔（微博 185 万粉博主，原传媒老跟班）推荐：「提供了丰富的剧本资源，涵盖电影、电视剧、话剧、小品、相声等多种类型」（https://weibo.com/5198011111/Op36censC）
- 定位偏投稿/交易+资源，名作类内容需自行确认。

## 二、国外渠道（原版剧本，2026-08 全部验证 HTTP 200）

| 网站 | URL | 定位 |
|---|---|---|
| IMSDb | https://imsdb.com | 互联网电影剧本数据库，最老牌最全，经典到现代，按体裁分类，免费网页阅读 |
| Script Slug | https://scriptslug.com | 现代大片+热门剧集，排版规范带分场；热门美剧（继承之战/最后生还者等）比 IMSDb 全 |
| SimplyScripts | https://www.simplyscripts.com | 电影+电视剧+广播剧+未制作剧本+奥斯卡获奖剧本，带讨论板 |
| Go Into the Story | https://gointothestory.blcklst.com | Black List（好莱坞黑名单）旗下，Scott Myers 主编；剧本库+每日写作拆解，适合从业者学手艺 |
| John August | https://johnaugust.com | 知名编剧（大鱼/查理与巧克力工厂）公开自己作品+创作过程 |
| The Daily Script | https://www.dailyscript.com | 老牌电影剧本库，按标题 A-M/N-Z 浏览 |
| MovieScriptsAndScreenplays | https://www.moviescriptsandscreenplays.com | 按字母序的电影剧本库，多为 PDF |
| Scripts.com | https://www.scripts.com | 社区投稿型大库（STANDS4 网络），质量参差，次级来源 |
| Internet Archive | https://archive.org | 扫描件剧本兜底（OCR），如卧虎藏龙 Schamus 修订稿 |

来源：万兴喵影文章「15个下载电影剧本资源的网站」（https://miao.wondershare.cn/article/homemade/movie-scripts.html，2025-05 发布）。

## 已死/不可用渠道（2026-08-05 全量实测，勿再试）

| 渠道 | 状态 | 实测 |
|---|---|---|
| The Script Lab（thescriptlab.com） | ❌ 已关闭 | 浏览器 ERR_CONNECTION_CLOSED |
| Screenplays for You（sfy.ru） | ❌ 已挂 | 浏览器 ERR_EMPTY_RESPONSE |
| 剧本联盟（juben68.com） | ❌ 域名死 | 只剩 phpstudy 默认页 |
| 奥斯卡官网剧本页（oscars.org/screenplays） | ❌ 无集中剧本 | 404；提名剧本 PDF 不集中发布 |
| No Film School（nofilmschool.com） | ⚠️ 403 反爬且非剧本库 | 教育媒体站，无剧本库 |

## 交易平台（非阅读渠道，勿混淆）

抖几句 doujiju.com、万众编剧网 wzbj1616.com、原创剧本网 ju20.com、script.wendong.work、varoo.cn——全是投稿/交易定位，不是「看名作剧本」渠道。

## 三、检索方法（搜索引擎全反爬时）

2026-08 实测：Bing（验证挑战）、DuckDuckGo HTML 版（首次成功、二次即限流 HTTP 202）、Mojeek（验证码）在代理下全被反爬挡。

成功路径 = Kimi WebBridge（localhost:10086，继承用户登录态）：
1. navigate `https://www.baidu.com/s?wd=<URL编码查询词>`
2. evaluate 提取结果：`document.querySelectorAll('#content_left h3 a')` 拿标题+href
3. 百度结果 href 是 `baidu.com/link?url=...` 跳转链接——navigate 过去才拿得到真实 URL（如知乎/微博）
4. Windows 下请求体含中文必须 write_file 写 JSON 文件 + `curl.exe -X POST --data-binary @file`，shell 内联会破坏中文
5. **evaluate code 里的中文同样会损坏**：中文正则字面量/字符串直接写进 code 会报 `SyntaxError: Unexpected identifier '登录'`（传输中被破坏）——改用 `\uXXXX` 转义写 ASCII 安全版本（如 `/\u6ce8\u518c/`），或用 DOM 查询避开中文（如检测导航区按钮文本用 `document.querySelector('header').innerText` 后按需比对）
