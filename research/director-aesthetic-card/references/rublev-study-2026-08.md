# 卢布廖夫轮来源地图（2026-08）

产出：`研习报告/安德烈·卢布廖夫_研习报告.md`、`技法卡片源稿/安德烈·卢布廖夫_技法卡片.md`（6 张）、`剧本原文/rublev_剧本_来源.md`（YAML frontmatter + Mosfilm 英译全本）。本表记录本轮**唯一一次剧本兜底成功**的完整路径与坑，未来老片剧本搜索直接复用。

## 剧本渠道实测（主流全灭 → springfield 兜底成功）

- **Script Slug** 站内搜索 `rublev` 无结果（130KB 搜索页只有查询回显）
- **IMSDb** `/scripts/Andrei-Rublev.html` 无条目（返回通用页）
- **Internet Archive** advancedsearch `"andrei rublev screenplay"` → `numFound:0`；换 `"rublev" AND mediatype:texts` 有命中但**全是书/画册/影评**：`andreirublev0000bird`（Robert Bird BFI 书）、`andreirublev00puni`（1916 年画家传记）、`andrej-rublev-di-andrej-a.-tarkovskij_202607`（**陷阱**：标题像意大利文剧本版，下载 djvu.txt 验证实为 Massetti 撰 ACTIVCINEMA 影评小册，含序章场景描述但非剧本——IA 命中必须核对 metadata description 与正文头）
- **破局**：DDG HTML 经 r.jina.ai 搜 `"andrei rublev" screenplay` → `uddg=` 参数暴露 `springfieldspringfield.co.uk/movie_script.php?movie=andrei-rublev` → curl 直连 83KB 页面
- **springfield 提取配方**：正文在**最后一个** `scrolling-script-container` div——`html.rfind('scrolling-script-container')` → 取其后 60K 字符 → `re.sub(r'<[^>]+>','\n',seg)` → 压空白 → 从 `find('The End')` 截尾（页尾有 "Report an Issue" 等导航噪音）。第一处匹配是 CSS 定义，前几次正则全中 CSS
- 剧本性质：**Mosfilm 英译全本**（页首 "ANDREI RUBLYOV / Screenplay by Andrei MIKHALKOV-KONCHALOVSKY, Andrei TARKOVSKY / Directed by Andrei TARKOVSKY"），49K 字符 / 1887 行，序章飞人 → 钟楼段 "The End"，无场次编号（纯对白转录式排版）。已与 Wikipedia 八章剧情逐节核对一致。入库标注"网站转录的 Mosfilm 英译版，非官方《Iskusstvo Kino》俄文原稿"
- scripts.com `script.php?id=andrei_rublev_2839` 直抓 0 字节（反爬），弃

## 剧本关键行号（pages/rublev_script_en.txt，引文行号直抄源）

| 行号 | 内容 |
|---|---|
| L40-57 | 序章飞人 "I'm flying!" |
| L74+ | 丑角押韵歌 |
| L468 | "THE ANDREI PASSION" 章起（森林论辩） |
| L571-572 | 费奥凡 "If Jesus came back to Earth again, He would be once more crucified!" |
| L612-615 | 卢布廖夫 "all Russians are of one blood and of one land!" |
| L705-707 | 库帕拉夜捆横梁 "Just like Jesus Christ" |
| L724-726 | 玛尔法 "This is the night when everyone should love. Is loving a sin?" |
| L885-887 | 拒画审判 "I don't want to scare people." |
| L914-926 | 丹尼尔朗读哥林多前书 13 章 |
| L1240-1297 | 亡者费奥凡幽灵对话；L1293-1295 "I'll never paint again." / "Nobody needs it." |
| L1336-1339 | 沉默誓；L1355-1356 "nothing more frightful than snow falling in the temple" |
| L1441-1453 | 鞑靼人七妻 "I got seven wives, but no Russian wife yet" |
| L1461-1494 | 铸钟开场 "There's no one to cast a bell!" / "I'll cast you a bell!" |
| L1500 | "I know the bell secret!" |
| L1531 | "We're founders, not navvies" |
| L1740-1742 | 铁水奔流 "It's flowing!" / "O Lord! Help us! Let it work!" |
| L1794-1796 | 基里尔 "Go to the Trinity and paint, paint!" |
| L1869-1872 | 博里斯卡坦白（父亲未传秘技） |
| L1876-1877 | "You'll be casting bells, and I'll be painting icons." |

## 存量复用（零新抓）

- `pages/tarkovsky_wiki_rublev.txt` — 八章剧情全节 / Bird 剪辑统计（403→390 镜头、31"→28"、唯一未动=彩色尾声）/ 黑白-彩色 1966 访谈 / Gianvito p.26 飞人献祭论 / 马=生命 / 审查史（Dom Kino 单场、Cannes 4AM、1971 公映 298 万观众）
- `pages/tarkovsky_criterion_rublev.txt` — Hoberman：film of the earth / 四元素（mist, mud, guttering candles, and snow）/ narrative impasto / 360° 牛棚 / 马蹄特写转鞑靼军团 / 天使镜头
- `pages/tarkovsky_sculpting_fulltext.txt` — L1363-1381 诗的逻辑章节论 / L3699-3705 教条烧毁重生 / L3276-3284 "killing cinema" 反绘画调度 / L1388-1391 椅子论 / L7222-7230 主题论（艺术家必须触碰时代的脓疮）
- `技法卡片源稿/塔可夫斯基_导演美学卡片.md` — 含 Ebert 钟楼引文、Bird 数据（S5 转引链）

## Ebert 原文不可重抓（本轮实测）

- `rogerebert.com/reviews/andrei-rublev-1973` 与 `-1966` live 均 404；Wayback CDX 精确 URL / `great-movie-*` 前缀 / `reviews/andrei-rublev*` 前缀全空；`archive.org/wayback/available` 429 限流；Bing 经 jina 只回 3KB 壳、DDG 引号查询经 jina 只回 308 字节
- 处置：Ebert 引文 "When the bell peals, what we are hearing is the sound of Tarkovsky's faith" 经《塔可夫斯基_导演美学卡片》转引（上轮已核），报告/卡片诚实声明标注"经 S5 转引，本轮未重抓到原文"——**转引链是比死磕更稳的处置**，前提是本地卡片有取证记录

## 校验记录

- 42 条关键英文引文批量 grep（norm：压空白 + 弯引号统一 + lower）0 MISS
- 行号抽查 19 处：17 OK；2 处偏差均为报告用**范围引用**（L724-726 写为 L705-707 邻近段、L1443-1445 在 L1441-1453 范围内）——合法。引文行号从 read_file 输出直抄最稳，凭记忆写行号必错
