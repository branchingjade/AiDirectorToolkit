# Deakins 研习轮记录（2026-08-09C 轮）· 摄影指导 Roger Deakins

产出物：`_work/制作大师研习-20260809C/Deakins/Deakins_制作大师卡片.md` + pages/ 49 份存档。结构对齐 Murch 模板八段。

## 本类任务可用 URL 模板（本轮验证过）
- 维基 wikitext（最稳）：`https://en.wikipedia.org/w/index.php?title=<页名>&action=raw` —— 无 Cloudflare、44–146KB 完整正文，refs 段带原文 Wayback 存档链接（可反查被墙原文）
- IMDb fullcredits via Wayback：`https://web.archive.org/web/2020id_/https://www.imdb.com/title/<ttid>/fullcredits`（BR2049 726KB / 1917 456KB 完整表）
- 播客 RSS（libsyn）：`https://<show>.libsyn.com/rss` —— Team Deakins 368 集 1.16MB，标题+官方 show notes 一包拿全；剧集页 `https://teamdeakins.libsyn.com/<slug>` 可直连（notes 与 RSS 一致）
- 可直接 curl 的新闻站（808KB 级全文）：deadline.com、inews.co.uk、abc.net.au、studiobinder.com、motionpictures.org
- Wayback availability 预检：`https://archive.org/wayback/available?url=<url>`（连发 429 限速，间隔 3s+）

## 反爬/失效地图（本轮实测，2026-08）
- theasc.com（ASC《Uncanny Valley》/《Designing the Future》）：直连 403（75KB 统一 403 页）；r.jina.ai 被 Cloudflare 拦；Wayback 无快照 → 内容经维基 BR2049 条目 Cinematography 节转引使用（二手）
- criterion.com（Fargo 页）：反爬拦截页 5.4KB；Wayback 无快照 → 如实标「未取到」
- arri.com 旧新闻页（Lighting Blade Runner 2049）：404，仅导航菜单（plain 10KB 全是菜单项）
- rogerdeakins.com /faq/：已下线 404；「Looking at Lighting」BR2049 灯光拆解页正文会员限定（"This content is restricted to site members"）——官网菜单可证栏目存在，但正文抓不到
- teamdeakins.com：默认 WP 占位页（hello-world/sample-page），真实存档在 teamdeakins.libsyn.com
- r.jina.ai：本轮对维基/IMDb/ASC/Criterion 全部返回 Cloudflare "Just a moment..."（~5.7KB 统一大小），不可作首选

## 署名查证结果（IMDb fullcredits，grep 验证）
- BR2049（tt1856101）：Roger Deakins = director of photography (as Roger A. Deakins)；supervising digital colorist = **Mitch Paulson**、second digital colorist = **Joel McWilliams**、digital intermediate producer = EFILM（与 Sonnenfeld 轮查证一致，无 Company 3）
- 1917（tt8579674）：Roger Deakins = director of photography + camera operator: "a" camera；James Ellis Deakins = digital workflow consultant

## 已 grep 验证的关键引语（存 pages/ 对应文件）
- Deadline 2018-02-26（deadline_deakins_br2049_plain.txt）："pools of light"、"feel alive"×2、"bare bulb"、"hardly see past 20 feet"、"The light is real. That's what it was actually like."、"never going to light it like the original film"、"exactly what I'm exposing on the set"、"moving light"×3
- inews 1917（inews_1917_plain.txt）："technique overwhelms the story and the content"、"nine minutes long"、"extended, uncut takes"×2、"like I was shooting a documentary"
- ABC（abc_1917_plain.txt）："imperceptible"、"six-to-eight minutes"、"enter a bunker"
- StudioBinder（studiobinder_1917_plain.txt）："hidden match cuts"、"foreground elements"、"flares"
- Team Deakins RSS（teamdeakins_rss.xml）："not make it a gimmick"×2、"natural light"×6（Fargo 专集简介 "supporting the performances using natural light"）

## 关键事实（写卡片骨架）
- 简报「15 次奥斯卡提名」勘误：维基 = **16 次提名 2 次获奖**（第 14 次=BR2049、第 15 次=1917 获奖；第 16 次=Empire of Light 未获奖）——卡片按维基写并加勘误条目
- BR2049 画幅：维基单口径「1.55:1 + Alexa XT Studio + Master Prime 球面镜头」（转引 ASC），ASC 原文未取到无法交叉验证；IMAX 版 1.9:1（维基）；成片院线画幅数据未 grep 到，未作论断
- 1917：全球首部 Alexa Mini LF；Arri Signature Primes 40mm 主镜/35mm 隧道掩体/47mm 河流段；唯一显性切黑在 66 分钟（Schofield 昏迷，Mendes "two movements" 原话）；最长单镜 9 分钟；隐藏剪辑三招（前景过画/人物过画/黑暗满帧）

## 遇到的坑
- Wayback `id_` 无快照时返回「Wayback Machine」着陆页（~151KB，`<title>Wayback Machine</title>`，文件头是 JS）——先 availability API 预检，或看标题/开头判断，别把着陆页当正文存档
- archive.org availability API 连发即 429——间隔 3s+
- 官网「Looking at Lighting」类页面 plain 提取后 5KB 全是菜单+论坛组件——先 grep 原文 HTML 的 `<p>`/alt/title 判断正文形态（会员墙/图片画廊/纯菜单）
- IMDb 角色行：姓名 `<a href>` 与文字分两行，`grep -B4` 常看不到姓名（中间隔 `<td>...</td>`），用 `grep -B10` 再筛 name
- 弯引号 grep 假失败照旧（通配符/无引号片段匹配）
