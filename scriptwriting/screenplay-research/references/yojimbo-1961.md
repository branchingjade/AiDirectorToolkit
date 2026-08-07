# 《用心棒》Yojimbo (1961) 抓取与研习记录（2026-08-07）

## 剧本获取：三主库全灭 → rapetuation.com 直链

| 渠道 | 结果 |
|---|---|
| IMSDb `scripts/Yojimbo.html` | HTTP 200 但 **7,785 字节空壳**（同《罗生门》软 404 形态，`wc -c` 判壳） |
| Script Slug | 404 |
| The Scripts Avant / The Successful Screenwriter | 404 |
| Internet Archive 搜 `Yojimbo screenplay` | 无剧本条目（仅电影视频/原声条目） |
| **rapeutation.com `YOJIMBOKUROSAWASCREENPLAY.pdf`** ✅ | 14.9MB 扫描 PDF，文本层完整可提取（48KB/1312 行） |

**发现路径**：DDG HTML 版经 r.jina.ai（`https://r.jina.ai/https://html.duckduckgo.com/html/?q=...`）搜 `"Yojimbo" screenplay pdf`，结果页 `uddg=` 参数直接给出 rapetuation 直链——比 Bing（返回 ck/a 跳转壳）更易提取。

## 版本指纹：Tara Carreon 转录稿（关键识别）

PDF 标题页特征（未来 Toho/日影片照此识别）：
- 标题 `"YOJIMBO" -- ILLUSTRATED SCREENPLAY`
- `[Transcribed from the movie by Tara Carreon]`
- `© 1961 Toho Co., Ltd.` + `English subtitled version © 2006 Toho International Co., Ltd.`

**性质**：成片对白转录稿（英文版），含少量 `[舞台指示]` 方括号；**无场景标题/镜头指令/景别**。分析纪律：对白/结构可做，景别与纯视觉断言标【成片层】+ 引影评佐证（Ebert 亲证狗叼断手开场：「Almost the first thing the samurai sees when he arrives is a dog trotting down the main street with a human hand in its mouth」）。

## 多源取证栈（无分场剧本时的标准配方）

- Criterion essay：`criterion.com/current/posts/60-yojimbo-west-meets-east`（Sesonske 2006，经 r.jina.ai 过 Cloudflare）
- Ebert Great Movies：`rogerebert.com/reviews/great-movie-yojimbo-1961`（wayback `web.archive.org/web/2023/` 前缀直抓）
- 维基 EN raw（`Yojimbo`，注意 `Yojimbo (film)` 是重定向）+ 维基 ZH（条目名用繁体 `大鏢客`，简体 `用心棒` 是重定向）
- 成片画面（狗叼断手等）二手佐证：DDG 片段（cinemadual / ihatedblackandwhitemovies）

## 转录稿关键行号表（行号 = 剧本原文/yojimbo_剧本_rapeutation.md 正文）

| 场景/台词 | L |
|---|---|
| 「棺材匠，两口棺材——不，三口」 | L290–291 |
| 竞价 3→50 两「后面加个零」 | L302–313 |
| Orin 偷听背叛「50 两全拿回来」 | L331 |
| 命名「桑畑三十郎（30 岁桑田）……快四十了」 | L366–367 |
| 拒战「你想打？自己打」 | L406 |
| 「问题是，谁会先捧着钱来？」 | L469 |
| 停战分析「赌徒停战只为准备更大的仗」 | L590 |
| 「这镇子又像锅一样滚起来了」「这出新戏你写的？」「一半，卯之助写了另一半」 | L744–751 |
| 棺材匠「打到这份上，棺材都不用了」 | L955 |
| 权爷「你不是真坏，你只是装坏」 | L968 |
| 递枪请求「没有枪我浑身不自在……只打了两发，没子弹了」 | L1279–1290 |
| 「我会在地狱门口等你」 | L1310 |
| 判词「你去上吊吧」/「这镇子总算安静了」「后会有期」 | L1317–1322 |

## 研习要点（信息差主导单主角）

- **没有真双雄**：两派老板只是「互相猜疑的两只手」，主角是棋盘外执棋人；戏份不靠出场时间靠「知情权」——他永远知道全局（刺客/Nui/谁杀六守卫），两派只知道一半，他只做三件事：卖情报（两头卖）、伪造现场（拆屋嫁祸）、制造人质危机。
- 动作序列「搅局→旁观→再搅局→旁观→收尾」，坐看节点 = 钟楼/棺材。
- 暴力记账法：杀人 = 棺材订单（商业语言），烈度峰值用「计数器失灵」（棺材卖不动）表达。

## 产出

- `研习报告/用心棒_研习报告.md`、`技法卡片源稿/用心棒_技法卡片.md`（7 张）、`剧本原文/yojimbo_剧本_rapeutation.md`（YAML frontmatter + 正文无 H1）
- 摘录复核：76 跨度 0 FAIL（v8 方法，见 SKILL.md）
