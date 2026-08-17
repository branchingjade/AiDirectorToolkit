# 《后天》（The Day After Tomorrow, 2004）范本研习轮记录 2026-08-09

范本研习轮（灾难题材密码地基），产出《后天_研习报告.md》+《后天_技法卡片.md》双文件到 `_work/v2-范本研习-20260809/后天/`。9 来源编号 [研S1-S9]，两轮验证 105+74 条引语 grep 验证，实质 0 MISS（MISS 全为形态假阴性）。

## 来源 URL 清单（9 成功 + 4 失败）

| 存档 | URL | 结果 |
|---|---|---|
| tdat_enwiki_raw.txt | `en.wikipedia.org/w/index.php?title=The_Day_After_Tomorrow&action=raw` | 35KB（⚠️ 带 `(film)` 消歧义后缀的标题是 74B 重定向，去掉后缀再抓） |
| tdat_zhwiki_plain.txt | zh.wikipedia.org API `titles=明日之後_(電影)` | 15.8KB（繁体标题，简体标题可能是 REDIRECT） |
| tdat_baike_manual.txt | `baike.baidu.com/item/后天/5315859` | 浏览器 innerText 提取 9.3KB |
| tdat_script.txt | `transcripts.simpleremix.com/script.php/the-day-after-tomorrow-2004-1L3O` | 180KB HTML → 48.6KB 纯对白 |
| tdat_bbc_emmerich_txt.txt | `bbc.co.uk/films/2004/05/12/roland_emmerich_day_after_tomorrow_interview.shtml` | 直连 21KB，一手访谈 |
| tdat_blackfilm_emmerich_txt.txt | `blackfilm.com/20040528/features/rolandemmerich.shtml` | 直连 22KB，一手访谈 |
| tdat_indiewire_2019_txt.txt | `indiewire.com/features/general/roland-emmerich-day-after-tomorrow-ending-1202186519/` | 直连 509KB HTML → 11KB 文本 |
| tdat_ebert_txt.txt | `rogerebert.com/reviews/the-day-after-tomorrow-2004` | 直连 95KB → 11KB 文本 |
| tdat_usatoday2004_txt.txt | `usatoday30.usatoday.com/educate/college/firstyear/articles/20040530.htm` | 直连 32KB，科学家批评一手报道 |
| 失败 | Guardian 20 周年（URL 猜测 404）、NPR 2004 访谈（Cloudflare）、IMSDb（Cloudflare）、AOL 转载（404） | 如实标「未取到」 |

## 通道实测（2026-08-09）

- **r.jina.ai 全线 Cloudflare 挑战页**（baike/ebert/indiewire/syfy/npr/guardian/imsdb/awn/enwiki-full 全部返回 5.8KB "Just a moment"）→ **直连 curl 几乎全成功**（Ebert 95KB / IndieWire 509KB / BBC 21KB / blackfilm 22KB / USA Today 32KB / Guardian 24KB），只有 NPR/SYFY 直连也失败。与既有记录一致：jina 全线失效时先直连，别反复重试 jina。
- **百度百科浏览器通道**：browser_navigate + browser_console `document.body.innerText`——innerText 约 15KB（含导航噪音），用 `indexOf('《片名》…')` 定位正文起点，再分片 `slice(0,6000)` / `slice(6000,16000)` 取回；词条 ID 不确定时先 web_search「片名 百度百科 item」。
- **IMSDb 被拦**（壳页 7.7KB 无正文，jina 也拦）→ **transcripts.simpleremix.com 是可用替代**：`/script.php/<slug>-<年份>-<ID>`，180KB HTML，正文起点定位法=找第一个 `EXT\.|INT\.|FADE IN` 或直接取标题后；**无场景头，纯对白**。

## 新陷阱（本轮新增）

- **transcript 换行分割假阴性**：对白镜像每行带 `\n`（甚至 `\n \n`），整句匹配必失败——实例：`We were wrong.\n\nI was wrong.`、`I will come for you. Do you understand me?\n\nI will come for you.`、`What we have found\n \nlocked to these ice cores...`。对策：拆成短片段（`We were wrong.`、`I will come for you`）或验证前压换行。
- enwiki raw 链接包裹（已有记录再验证）：`[[The Towering Inferno]]` → grep "Towering Inferno of climate science movies" 假失败，取无链接部分。
- en dash：`6–8 weeks` vs 检查串 `6-8 weeks` 假失败。
- **百度百科数据存疑照录**：水箱"注入25加仑"（纽约街头水箱不可能仅 25 加仑）、"每小时八公里风速"疑换算错误——原文引用 + 诚实声明标注，不做采信论证。

## 已验证引语锚（节选，全文见产出文件）

- **剧本对白**：`evidence of a cataclysmic climate shift` / `global warming can trigger a cooling trend` / `our economy is every bit as fragile as the environment` / `Evacuate everyone south of that line` / `stay inside` / `I will come for you` / `burn whatever you can to stay warm` / `I made my son a promise` / `You made it. Of course I did.` / `We were wrong. I was wrong.` / `the Third World` / `Have you ever seen the air so clear?`
- **导演一手（BBC 2004）**：`we want people to not realise that it's all visual effects` / `photo-real effects` / `I'm stunned how many scientists` / `That's the blueprint` / `Bruce Willis character... George Bush's agenda`（政治立场金句）
- **导演一手（blackfilm 2004）**：`stay away from water and stay away from snow` / `it would crumble, but in our movie it still stands` / `That's my comment to Hollywood` / `we didn't have a real happy ending` / `a common noble person as the face against a totally extreme overwhelming enemy`
- **导演一手（IndieWire 2019 转述 Variety）**：`no real happy ending` / `if humanity keeps going like this, there will be no happy ending` / `atomic bomb or break a dam`
- **影评（Ebert）**：`profoundly silly... also very scary` / `annihilation of subcontinents` / `slash across a map` / `fly south double-time`
- **科学批评（双源 USA Today + enwiki）**：Schrag `over-the-top effects... think the whole thing is a joke`；Shepherd `D minus or an F`；Weaver `Towering Inferno of climate science movies`

## 诚实声明要点（范本研习轮清单）

- **对白级来源明确标注**：无场景头；成片有的场景镜像可能缺（图书馆烧书戏只有原声带曲目 Burning Books 佐证）
- **票房三口径并记**：$552,639,571（enwiki）/ 5.52 亿美元（百度百科）/ $542M（IndieWire 转述）——主口径取 enwiki，其余入声明
- 未逐帧看片；Guardian/NPR/IMSDb 未取到如实写

## 双文件模板要点

- **研习报告**：来源渠道表 → 一句话概括 → 结构观察（灾难三段式：预兆/降临→逃生→救援）→ 画面锚点清单（8-15 个）→ 对白手法 → 动作层写法 → 桥段设计表 → 国风可复用时机 → 诚实声明
- **技法卡片 7 张**：每张 = 大师/场景/技法/证据[来源编号]/画面锚点/可复用时机/对接 + 文末诚实声明 + 取证来源清单（对齐《星际穿越_技法卡片》模板）
- 国风对接桥接：灾难奇观地域化并联（太空站视角→钦天监/观星台）、民间预兆信号、警告者×当权者×认错闭环、封闭空间众生相容器（图书馆→荒城/庙宇/粮仓）、"雪后初晴"净化意象
