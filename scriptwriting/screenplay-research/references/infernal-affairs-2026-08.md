# 《无间道》研习取证记录（2026-08-07）

无正式剧本的港片取证样板：Script-O-Rama 转录稿 + 维基 + 豆瓣 wayback。产出：研习报告/技法卡片 7 张/转录稿存档。

## 剧本获取结论
- juben.pro 名作区（/Famous/，35 部）确认无《无间道》；POST 搜索 302→411 未深究
- 正式剧本出版物线索：**维基「相关著作」节**著录《無間道前傳：劇本、編劇論述》麦兆辉庄文强剧本原著、刘嶔编著，星岛 2003-10，ISBN 9626722479（正文未取到）——查港片剧本先看维基相关著作节找出版物
- **拿到：Script-O-Rama 英文字幕转录稿全文**（~59KB / 4714 行），Wayback 2006 快照

## 转录稿发现路径（可复用）
1. scripts-onscreen.com 聚合页 `https://scripts-onscreen.com/movie/<slug>-script-links/`（curl 200）列出 Script-O-Rama 的 wayback 链接
2. 聚合页链接 URL **被截断**（`...infernal-affairs-script-transc`）→ 直抓 404；改用 CDX 查全：
   `http://web.archive.org/cdx/search/cdx?url=script-o-rama.com&matchType=domain&output=text&limit=2000&collapse=urlkey&filter=original:.*infernal.*`
3. 命中 `infernal-affairs-script-transcript.html` 快照 20061028121528 → 下载
   `http://web.archive.org/web/20061028121528/http://www.script-o-rama.com/movie_scripts/i/infernal-affairs-script-transcript.html`（64KB，200 OK）
4. URL 模式：`script-o-rama.com/movie_scripts/<首字母>/<slug>-script-transcript.html`；同页还有续集 `-2-script-transcript.html`

## 转录稿质量 / 版本指纹（重要）
- 纯字幕式对白+动作，无场景标题/景别；**数字常缺失**（"only for   years" 空格占位，引用时用 `___` 标注）；**段落重复**（天台戏出现两次，L3891 与 L4459）——结构分析勿以此稿为准，只用于对白取证
- **结尾版本指纹 = 马来西亚版**："Lau Kin-Ming... You are under arrest. Take him"（港版为电梯杀林国平+墓前敬礼）——字幕转录可能对应非港版，引用结尾前必须查指纹
- 粤语原声台词从维基「文化影响」节取（"明明話三年㗎，三年之後又三年……"、"對唔住，我係差人"）
- 可 grep 的关键戏行号：佛偈 L1-17 / 祝酒 L18-38 / 三年又三年 L437-450 / 梦里喊我是警察 L472-476 / 黄sir坠楼通报 L3136 / 天台戏 L3891-4031 / 电梯 L4085-4127 / 结尾佛偈 L4171-4180 / 被捕结局 L4695-4709

## 豆瓣经 Wayback 取证（绕过 sec.douban.com 验证）
- curl 直抓 `movie.douban.com/subject/<id>/` → 302 到 `sec.douban.com` 验证页；豆瓣搜索页 JS 渲染（`SEARCH_RESULT.renderSearchResult`）——**豆瓣一律走 wayback，别死磕**
- 豆瓣 ID 从维基外部链接节拿（无间道 = 1307914），不要猜
- CDX 查快照：`url=movie.douban.com/subject/1307914*&output=text&limit=100&collapse=urlkey` → 找 `reviews` 列表页快照（如 20150410062923）
- 单篇影评：`http://web.archive.org/web/20150410062923/http://movie.douban.com/review/<id>/` **必须 `-L` 跟随 302**（跳到实际存档时间戳）；404 = 该 id 无此时间窗快照
- **影评正文容器按年代分三型**（提取正则按序回退）：
  - 2012-2015 旧版：`<span property="v:description">` 或 `<div property="v:description" class="">`
  - 2020 新版：`<div class="review-content clearfix">`；识别法 = `og:url` 含 web.archive.org 时间戳
  - 通用正则：`re.search(r'<div[^>]*v:description[^>]*>(.*?)</div>\s*</div>', t, re.S)` → 退回 span 版 → 退回 `review-content` 版
- 影评列表快照页（旧版豆瓣）内含全部热门影评 id + 标题，一次抓列表即可选文

## Windows git-bash 路径坑（本会话实测）
- bash curl `-o /c/Users/...` → **exit 23 写入失败**；`-o C:/Users/...`（Windows 风格）正常
- Windows Python `open('/tmp/x')` 与 bash `/tmp` 指向不同目录（cygpath -w /tmp = AppData\Local\Temp，但 python 写的不在那）——**中间文件统一用 `C:/...` 绝对路径**，bash 和 python 都能读写
- CDX `filter=original:.*中文.*` 零结果（URL 存储编码问题）——用 ASCII 关键词（infernal）或时间窗（from/to）

## 摘录校验器补丁（43 段 0 FAIL 实测）
- **剥引号只剥 `"` `“` `”`，不剥撇号 `'`**（It's→Its、I'm→Im 会大面积误报）
- 分段后必须 `.lower()`（否则大写行首整段误报）
- 转录稿数字占位：摘录 `___` 先剥除再比
- 中英混合斜体块（`*英文*（中文注释）`）：has_cjk 整块过滤会漏检——改用 `[A-Za-z][A-Za-z ,\.\'\"\-—/]{13,}` 提取英文片段，再按 `.` `/` 拆段逐段 in 校验（43 段全过）
