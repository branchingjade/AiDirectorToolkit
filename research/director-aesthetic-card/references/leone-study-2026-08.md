# 莱昂内轮（2026-08-09，西部轴，导演卡片+手法深化双文档）

轮次详情：`_work/全链条研习-20260809/赛尔乔·莱昂内/`，产出《导演美学卡片》+《手法体系深化》，90 条引文 0 MISS。

## 通道矩阵（本轮实证）

- **英维 raw 批量直抓**（urllib 免验证 SSL + 浏览器 UA）：主条目 + 五部代表片条目（OUATITW/OUATIA/GBU/Fistful/Few Dollars）一次脚本全下。主条目**无 Style 节**时风格证据去单片条目（GBU 有 Cinematography/Music 节、OUATITW 有 Music 节）——导演主条目结构因片而异，别等主条目。
- **SoC Great Directors**：slug `/2002/great-directors/leone/`（Dan Edwards, 2002, Issue 22）。站点搜索页 `?s=<导演名>` 直抓 166KB，grep `great-directors` 定位真实 slug（不要按 firstname-lastname 猜）；正文 `<article>` 容器提取。
- **Guardian Content API 找文章 URL**：`content.guardianapis.com/search?q=<导演名>&tag=film/film&api-key=test` 一次 30 条，命中 2024 两篇（OUATIA at 40 / Man with No English）；按标题筛掉无关同名（Sierra Leone 国家名噪音）。
- **豆瓣 subject_suggest 直连**（iPhone UA + `Referer: https://movie.douban.com/`）一次全中五部片 id（西部往事=1293394/荒野大镖客=1302522/黄昏双镖客=1295586/黄金三镖客=1401118/导演条目=1013894）。⚠️ **r.jina.ai 代理对 `movie.douban.com/j/subject_suggest` 直接 403**——jina 是兜底不是第一顺位，suggest 族先直连。
- **rexxar `/v2/movie/<id>?ck=&for_mobile=1` 单调用核身份**：1297574 返回「英雄本色 | 1986」——pinyin 碰撞（西部往事 xibu_wangshi 猜错）当场暴露，免掉 reviews 拉错片的浪费。与蓝丝绒轮同端点，本轮的教训是**猜 id 后必核，别省这一步**。
- **Criterion 负面取证**：搜索页直连 403、r.jina.ai 也 403（CF 壳）；CDX `url=criterion.com/current/posts*&filter=urlkey:.*leone.*&limit=30&collapse=urlkey` 一次返回 3 条（全是 The Daily 简讯），无单片 essay——**因为莱昂内影片版权在 MGM/华纳，Criterion 根本没发行**。启示：大厂版权片先查发行方，再决定要不要找 Criterion essay。

## 新坑/新配方

1. **Guardian 正文提取**（leone_guardian_ouatia40.txt 328KB raw）：
   - 失败尝试：`article-body-commercial-selector` div 配对正则（只取到 870 字符）→ 长行过滤（nav 菜单混入 8KB 噪音）。
   - 成功配方：`raw.find('article-body-commercial-selector')` 起 → `raw.find('data-gu-name="most-viewed"')` 截尾 → `re.findall(r"<p[^>]*>(.*?)</p>", seg, re.S)` → 剥标签+unescape → 过滤 `len>80` → 6KB 正文。
2. **CJK 引文校验 norm 补两件**（本轮 6 条 MISS 全由此类）：
   - ① 弯单引号 `‘ ’`（U+2018/2019）也要剥——豆瓣转帖常「'死亡之舞'」式嵌套引号，只剥 `“ ”` 假 MISS（"为了这部死亡之舞…"整条 MISS 即此因）。
   - ② 半角标点归一全角（`replace(',','，')` 等）——转帖常半角混排（"等待,爆发"），⑮ 的"成对收录"落实为双向归一。
   - ③ 转帖错字按原文直录：豆瓣 1353127 原文「无意义的死去」（的非地），文档初写「地」→ MISS；改按原文直录 + 〔原文如此：转帖作"的"〕标注。
3. **zhwiki 译名重定向**：`塞尔吉奥·莱昂内` 探测返回 `#重定向 [[塞吉歐·李昂尼]]{{译名重定向}}`——action=query 探测的 redirects 字段为空时，raw 内容本身可能就是重定向存根，读 54 字节内容即知（与巴顿·芬克轮"读 #REDIRECT 直接抓目标名"同族）。
4. **转引层级**：莱昂内「死亡之舞」自述、「福特地平线」对比、「莫里康内开拍前已写配乐」均只经豆瓣长评转引，标注转引不升格；「My films are basically silent films」经 Guardian 2024 报道引述（一手报道引导演原话，但非原始音像）。

## 本轮最有价值的证据形态

- **逐镜分镜表**（豆瓣 review/4850412《西部往事》片段分镜解析）：景别/运镜/镜头内容/时长/声音五列表格——对峙戏"特写等待 4–38 秒+无配乐+数秒爆发"的结构性证据，比任何影评描述都硬。
- **数字多口径并列**：开场时长三口径（逐镜表约 6 分钟 / 影迷"接近20分钟" / 英维 4 天拍摄日程）不强行统一；OUATIA 269/251/229/139 四版本口径三源互证。
- **一手原话核验清单**：Cinema must be spectacle…myth [S1]、Old West as it really was [S6]、silent films [S8]、European's eyes [S5]、黑泽明信 "it is my film" [S23]——五条撑起创作思路节，全部 grep 验证通过。
