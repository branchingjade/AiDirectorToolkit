# 钢琴家轮 2026-08 研习备忘（波兰斯基深化首片）

> 单片轮产出：《研习报告/钢琴家_研习报告.md》《技法卡片源稿/钢琴家_技法卡片.md》｜96 引文 0 MISS｜校验脚本 verify_pianist.py（film-suite-research 根目录）
> 完整来源地图见 film-suite-research/references/polanski-pianist-study-2026-08.md

## 新源通道：豆瓣长评 = 完成片逐镜记录稿（镜头号级证据）

- 实例：review/6514605（79 有用）＝曹轶译、法国《电影前台》2003 年 3 月号（总第 520 期）阿兰·米诺「根据完成片的每一个镜头加以记录整理」的逐镜记录稿，111K 字。
- 价值：无正式出版剧本的欧洲片，逐镜记录稿比剧本转帖更接近成片层——镜头号可作桥段拆解的精确锚点（本片：六块糖 474-485 / 空弹 847-853 / Ich war Pianist 1040 / 首尾重奏 1145-1173 / 三块字幕 1168-1172）。
- 纪律：文末版本注记必查（"译自法国《电影前台》杂志…由阿兰·米诺根据完成片的每一个镜头加以记录整理"）；引用须标注「完成片逐镜记录稿，非原创剧本」；台词/镜头号以该稿行号为据。
- 选稿信号：reviews 列表标题含「电影剧本」但正文是逐镜记录（镜头编号+同镜头/反打标记）；抓回先核对文末注记判断是原创剧本还是逐镜记录稿。

## 校验新坑 ㊿-钢琴家轮四例（2026-08）

1. **同前缀 .html 壳遮蔽 .txt 真档（假 MISS 集体爆发）**：Ebert 直连 403 的 Cloudflare 壳（`polanski_ebert_review.html` 1.4KB，`<title>Just a moment...`）与 r.jina.ai 真档（`.txt` 6KB）同前缀共存，find_archive 首匹配命中壳 → 40 条英文引文集体假 MISS。修复：存档选择按扩展名优先级 `.txt` > `.html` > `.json`，或显式排除 403 签名壳。
2. **{{Quote box}}/{{blockquote}} 整段引文被模板剥壳删除（㉛ 实践升级）**：片尾字幕 "All that is known is that he died in a Soviet prisoner-of-war camp in 1952" 整段在 `{{Quote box|quote=...}}` 内、波兰斯基铁丝网看电影自述在 `{{blockquote|...}}` 内——norm 剥 `{{}}` 后引文消失。修复：校验循环对存档建**双变体**（剥模板 norm / 不剥模板 norm_raw）两路都查，命中即算过。
3. **剥下划线后括号前无空格假 MISS**：`_Schindler's List_(1993)` 去 `_` 后成 `List(1993)`，短语带空格 `List (1993)` 必 MISS（norm 删括号后仍差空格）。修复：**双侧笛卡尔积变体匹配**——短语侧与源侧都生成 {原样, 去空格, 去 dash, 去空格+dash} 变体，`any(ps in ss for ps in pvs for ss in svs)`（比 ㉟② 只归短语侧更全）。
4. **测试短语凭记忆改写致 MISS（㊲ 再证）**："he would have died" vs 原文 "but would have died"——校验短语必须从文档引文逐字复制，MISS 先对照存档原文查多字/少字/换序再怀疑来源。

## 其他本轮实测

- **中维标题探测**：台港译名重定向链（戰地琴人/鋼琴戰曲 → 「钢琴家 (电影)」简体裸名无年份）；「钢琴家 (2002年电影)」404。zhwiki API 首轮 429 限流 → sleep 8-15s + curl 浏览器 UA 后恢复。
- **Ebert slug**：the-pianist-2003（发布年 2003 非上映年 2002；2002 版 404）——enwiki ref href 给真实 slug，别按上映年猜。
- **SoC 作者取证**：jina markdown 与站内搜索页均无署名时，curl 原文页 grep `itemprop="author"` 的 `<meta itemprop="name" content="...">` 一次确认（Tsiolkas《The Atheist's Shoah》/Carr 导演专条均由此取证）。
- **Criterion 负面取证**：站内搜索 "pianist" 仅模糊命中（Girard 钢琴家传记片/Jason Moran），无本片 films/ 页与 essay；英维 Home media 段佐证北美蓝光=Shout! Factory——大厂片库片预判再例。
- **Guardian API**：api-key=test + tag=film/film + 日期区间定位 2003 老影评成功，jina 直抓全文。

## 预设处置 5 项

1. 幸存者「旁观」美学 ✅（Ebert witness/Ebert survivor not hero/Tsiolkas observers of horror/Bradshaw ringside seat/豆瓣「钢琴家的眼睛就是导演波兰斯基的摄像头」）
2. 犹太区/废墟视觉 ✅（Ebert dare not play/Bradshaw miraculously undamaged piano/逐镜稿 933/1015/1032/LaSalle 黑白废墟）
3. 与辛德勒对照 ✅（Tsiolkas "six million plus one list" 系统性批判/老晃「先入为主的宣泄」/红锈宝刀侠「没辛德勒那么煽情」/Ebert 拒绝执导史实三源互证）
4. 钢琴意象 ✅（首尾夜曲对称/空弹「不弹即是弹」/"Ich bin……Ich war Pianist" 过去时自证身份）
5. 创伤自传性 ⚠️ 部分取证——「我是那场大屠杀的幸存者」未逐字取证，改用 Ebert 转述（mother's death... only his own death will bring closure）+ 百度百科三条自传痕迹（扭曲尸体/黑窗户/「走路不要跑」=父亲告诫，片中化为黑勒「别跑」）
