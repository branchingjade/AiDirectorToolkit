# 美术指导奚仲文研习轮记录（美术轴·华语香港，2026-08）

产出：《奚仲文_制作大师卡片.md》（_work/v2-大师卡-20260809/奚仲文/）。结构对齐叶锦添卡八段；90 条引语 grep 验证 0 MISS。

## 来源 URL 清单（10 存档）

| 编号 | URL | 说明 |
|---|---|---|
| S1 | `https://zh.wikipedia.org/w/index.php?title=奚仲文&action=raw` | 中文维基人物条 19KB（获奖全表/作品年表） |
| S2 | `https://en.wikipedia.org/w/index.php?title=Yee_Chung-man&action=raw` | 英文维基（注意小写 m！大写变体只回 44B #REDIRECT） |
| S3 | `https://cinehello.com/stream/147669` | 金马大师课演讲全文（影视工业网转载，一手）——jina 被 Cloudflare 拦，直连 curl 97KB HTML + bs4 提取 15.9KB |
| S4 | `https://ent.sina.com.cn/m/c/2007-11-23/09391803903.shtml` | 新浪 2007 投名状专访（一手）——gb18030 解码 |
| S5 | `https://www.filmarchive.gov.hk/documents/6.-Research-and-Publication/06-02-Filmmakers-Search/English/YEE-Chung-man_e.pdf` | 香港电影资料馆 Filmmakers Search 官方 PDF（pymupdf 提取） |
| S6 | `https://zuniseason.org.hk/sc/zlive/yee-chung-man/` | 进念二十面体官方简介——HTML 正文嵌模板（PHP warning 前缀），bs4 只出 302B，关键词定位+剥标签正则提取（正文约在字节 23400+） |
| S7 | `https://en.wikipedia.org/w/index.php?title=Curse_of_the_Golden_Flower&action=raw` | 黄金甲条目（奥斯卡提名确认/金像奖获奖/菊花意象/烂番茄评语） |
| S8 | `https://en.wikipedia.org/w/index.php?title=Center_Stage_(1991_film)&action=raw` | 阮玲玉条目（勘误用：Best Art Direction – Pok Yuk Mok） |
| S9 | `https://zh.wikipedia.org/w/index.php?title=香港電影金像獎最佳服裝造型設計&action=raw` | 金像奖服装造型历届条目（勘误用：第 12 届获奖=张叔平/余家安，朴若木《阮玲玉》仅提名） |
| S10 | `https://baike.baidu.com/item/奚仲文/1992749` | 百度百科（浏览器通道，innerText 空→用快照文件） |

## 署名查证/勘误案例

- 简报称奚仲文担任《阮玲玉》美术指导 → **查证不成立**。路径：①中文维基金像奖奖项条目（第 12 届服装造型获奖=张叔平/余家安《笑傲江湖II東方不敗》，提名含朴若木《阮玲玉》）②英文维基片条目（Best Art Direction – Pok Yuk Mok）③人物条作品列表无此片。港片奖项归属优先查中文维基金像奖奖项条目（比 IMDb/百度百科快），与曹久平轮"百度百科电影词条职员表"互补成港片双通道。

## 已验证引语锚（全部 grep 通过）

- 倩女幽魂："我不是要你做一个古装片，我就是要你做一个感觉是时装的古装片"（徐克语）/"以前的古装片一定有绣花，我们就不用"/"整套衣服不要用很多颜色，黑的黑、白的白"/"你拿奖都是靠我那个垃圾袋"（程小东）
- 黄金甲："一定要极致，要做到色彩丰富得不得了的那种"（张艺谋）/"太含蓄啦，可不可以色彩再丰富一点"→"我们现在的宫女已经变成妃子皇后了，那你怎么办？"/"全部颜色都在那个布景上了……有什么颜色就放什么颜色，有什么图案就放什么图案，我自己觉得很俗气"/"因为要黄金，所以一定要用铜制，铜很沉、很重"/"几个人都拿不动"（巩俐凤冠吊威亚）
- 投名状："做完一部颜色乱七八糟的电影，突然接着做《投名状》就是黑漆漆了"/"黑色和血色就足够了"/"地狱不可能金光闪闪"/"穿得越破烂越真实，要一种身在地狱的感觉"（陈可辛）/3000 万服装成本/50 万黄金铠弃用
- 方法论："无论怎么写实都是不写实的，一定就是看起来有点像，可是再看着它又不是真正那些人穿的服装"（甜蜜蜜）/"都是把人家的东西拿过来用的……好像唐诗念三百首之类"/"我真的不是大师"/"都是人与人的关系，不是看你做的东西"/高锰酸钾做旧（张叔平传授）
- HKFA 官方史评（倩女幽魂）："minimalist silhouette of evanescent beauty" / "breaking new grounds for the field of art direction in period films of the 1980s"
- 黄金甲 S7：菊花=the golden flowers；黄巢《不第后赋菊》S7 只存英译（"the whole city will be clothed in golden armour"）——中文原句未取证不写入卡片

## 双口径

- 金像奖最佳美术指导：中文维基 8 次（含 2007 黄金甲）vs HKFA 官方文档 7 次；服装造型 7 vs 6 次——按中文维基全表写、注明官方口径。
- 百度百科外文名 "Chung-Man Hai" 与维基/HKFA "Kenneth Yee Chung-Man" 不一致（百度疑误，取维基口径）。

## 验证陷阱新增（本轮实测）

1. **PDF 提取断行**：pymupdf 每行末尾 \n → norm 必须先 `re.sub(r'\s+',' ')` 压空白（首验 5 MISS 中 2 条此因）。fitz 弃用警告 → `import pymupdf`。
2. **enwiki action=raw 大小写变体**：`Yee Chung-Man` 回 44 字节 `#REDIRECT [[Yee Chung-man]]` → 跟重定向目标。
3. **wikitext 双括号链接**：`[[Double Ninth Festival]]` 使检查串假 MISS → norm 加 `re.sub(r'\[\[([^\]|]*)\]\]', r'\1', s)`。
4. **zhwiki API 限流**：返回 278 字节 "You are making too many requests" → 改 action=raw 即通。
5. **百度百科 innerText 空**：JS 渲染词条 `document.body.innerText` 返回 0/35 字符 → 用浏览器快照文件（browser-snapshot-*.txt）read_file/grep。

## 未取到

百度百科经 jina（Cloudflare）；黄金甲色彩分析文（百度文库付费）；《投名状》英文维基条目（未抓，S3+S4 已覆盖）。
