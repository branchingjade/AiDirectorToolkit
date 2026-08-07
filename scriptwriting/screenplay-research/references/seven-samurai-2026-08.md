# 《七武士》剧本获取记录（2026-08-05，黑泽明群像/动作研习）

## 结论速览
- ✅ **可用全文源**：The Scripts Avant `https://thescriptsavant.com/movies/Seven_Samurai.pdf`（188 页 PDF，`pdftotext -layout` 全量提取 10,275 行 / ~398K 字符，首尾完整，"THE END" 在文末）
- 内容：**Donald Richie 英译流传版**（Written by Akira Kurosawa & Shinobu Hashimoto & Hideo Oguni, Translated by Donald Richie；mypdfscripts.com 转制 PDF）——非日文原稿，引用须注明版本
- ❌ IMSDb `https://imsdb.com/scripts/Seven-Samurai.html`：HTTP 200 但**空壳页**（scrtext 仅 68 字符，Writers/Genres 空白）——死条目勿再试
- ❌ Script Slug `https://www.scriptslug.com/script/seven-samurai-1954`：404；站内搜索页 `/search?search=...` 也是 404 兜底页——未收录该片
- ❌ Shore Scripts `https://www.shorescripts.com/wordpress/wp-content/uploads/2018/10/sevens-1.pdf`：202 + 229 字节（反爬）
- ❌ IA `akira-kurosawa-collection_20260211`：只有影片 m4v/mp4，无剧本

## 发现路径（难找剧本的可复用流程）
1. 大库探活：IMSDb 空壳 + Script Slug 404（slug 猜 `seven-samurai-1954` 不可用）
2. WebBridge 真实浏览器走 Bing：`"seven samurai" screenplay pdf full text`（curl 裸 Bing 会验证挑战）
3. 结果命中**聚合站** `https://scripts-onscreen.com/movie/seven-samurai-script-links/`（WordPress 页，静态可 curl）
4. 聚合页列出直链：`thescriptsavant.com/movies/Seven_Samurai.pdf` ✓ 下载成功

## 格式特征（程序化粗读要点）
- 场景：**连续编号标记 `\f 37.`**（行首纯数字+句点），S2–S187 共 186 个标记，S1=片头字幕——无 INT./EXT.，`^\d+\s+(INT|EXT...)` 正则失效，改用 `^\s*(\d{1,3})\.\s*$`
- **景别/运镜/音乐提示全部写进正文**（"Dissolve into long shot...", "Medium close-up of KIKUCHIYO...", "Music out."）——Richie 译本保留了黑泽明的分镜思维，动作层分析可直接引用景别词
- 转场系统：Wipe to / Dissolve to / Fade in on / Music in-out 内嵌正文

## 文本层噪声（引用/统计前注意）
- "Sak�" 应为 "Saké"（S76）
- "visible handing over the edge of the bed" 应为 hanging（S119，OCR 错字）
- 摘录复核方法：全文 `re.sub(r'\s+',' ')` 归一化后逐条 `in` 校验；本片 26 条摘录复核 22/26 首轮命中，修正 1 条 OCR 噪声后 26/26——**OCR 噪声条目按上下文校正并在笔记里注明**

## 结构发现（供研习报告参考，占比推断非作者声明）
- 三幕：组队 0–26.4% / 备战 26.4–88.7% / 决战 88.7–100%（动作戏只占最后 12%）
- 七人组队完成于 S43–50（~23–26%）；中点 = S73–78 Kikuchiyo 铠甲独白（38.8–42.0%）
- 三场战斗：夜袭磨坊 S119–127（64–67.7%）/ 水田诱敌 S134–145 / 雨战终局 S166–183
- 死亡顺序=队伍功能拆除：Heihachi（士气，S123）→ Gorobei（智囊，S169）→ Kyuzo（胜利欢呼瞬间，S181）→ Kikuchiyo（最后冲锋，S183）
- 产出物：`film-suite-research/研习报告/七武士_研习报告.md` + `技法卡片源稿/七武士_技法卡片.md`
