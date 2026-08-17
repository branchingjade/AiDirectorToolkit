# 中岛哲也轮（2026-08-09，日片视觉系导演轮）——轮次地图

导演卡片+手法体系深化双文档；16 存档编号（S1-S16）；71 条引文 0 MISS。
产出：`_work/v2-导演研习-20260809/中岛哲也/中岛哲也_导演美学卡片.md` + `中岛哲也_手法体系深化.md` + `verify_citations.py`。

## 存档清单（pages/）

| 编号 | 文件 | 来源 | 关键内容 |
|---|---|---|---|
| S1 | nakashima_zhwiki_raw.txt | 中维主条目 | 广告背景/速度感、CG自述、音乐自述（70首/一年听歌）、松子「歌舞電影」标注、作品表、《阿基拉》影响 |
| S2 | nakashima_enwiki_raw.txt | 英维主条目 | 金像奖三奖、奥斯卡外语片短名单、《进击的巨人》退出、Filmography |
| S3 | nakashima_confessions_enwiki_raw.txt | 英维·告白 | 复仇结构、四视角叙事、结尾"just kidding"、非线性叙事分类 |
| S4 | nakashima_matsuko_enwiki_raw.txt | 英维·松子 | **"tragicomedy musical"官方分类**（Infoxbox 首句=类型定位直接证据）、教师背景 |
| S5 | nakashima_kamikaze_enwiki_raw.txt | 英维·下妻 | 菅野洋子配乐、Studio 4°C 动画、Rococo/Lolita |
| S6 | nakashima_kanako_enwiki_raw.txt | 英维·渴望 | 黑色线最暗端（酗酒前侦探、性暴力） |
| S7-S14 | matsuko_sat/fairy/rebel.txt、conf_reverse/mv/shot/vengeance.txt、kami_evo.txt | 豆瓣长评（rexxar） | 高饱和/反差美学/MV论/逐镜分析/跨片对比/反抗论 |
| S15 | douban_rev_16666226.txt | 豆瓣转载·**导筒 2025 HKIFF 专访中岛哲也全文** | 色彩=性格、音乐剧方法、《音乐之声》参照、广告=技术非风格、20年等待——全轮最强一手源 |
| S16 | sohu_interview.txt | 搜狐（同专访新闻化改写） | 辅助，未直接引正文 |

## 新通道（日片导演轮）

1. **华语电影节媒体专访转载 = 日导最新一手话**：2025 HKIFF 期间「导筒」（华语电影媒体）对中岛哲也的专访全文被整篇转帖为豆瓣长评（review/16666226）——含导演色彩方法论/悲惨喜剧方法原话，一手密度高于一切二手影评。发现路径：DDG 经 jina 搜「<导演名> 访谈 导演 自述 采访」，结果里 `movie.douban.com/review/<id>/` 链接即候选。**日片导演轮扫 reviews 列表标题关键词表补「专访/导筒/独家」**（与 naruse 轮 HK IFF 纪念特刊转载对谈同族：电影节=华语媒体专访日导的集中时点）。
2. **suggest 兜底新链（第三形态）**：suggest 直连空 → r.jina.ai 代理空（「告白 2010/告白 松隆子/Confessions 2010」多候选全空）→ DDG 经 jina 搜 `site:movie.douban.com/subject 片名 年份 导演` 一次命中真实 id（告白=4268598）。URL 带豆瓣自己的 `?keywod=` 拼写错误参数属正常。与 GitHub Top250（㊿摩登时代）、jina suggest（侯孝贤轮）并列。
3. **多片名长评选稿**：有用数 17/37 的低有用长评（MV论/逐镜镜头分析）直接支撑「视觉系/黑色」两大重点；「风格」「镜头分析」「反差」类标题优先。

## 两新坑（已登记 pitfalls-log ㊿-中岛哲也轮）

1. write_file 落盘校验脚本的弯引号转义**必须单反斜杠** `'\u2018'`；双反斜杠 `'\\u2018'` 落盘后是 6 字符字面量、norm 静默失效 → S15 整批 14 条假 MISS。
2. execute_code 相对路径写存档第三次再犯（坑⑦再证）：落点变体 = **并行轮目录**（`_work/v2-范本研习-20260809/壁花少年/pages/`）；校验全 MISS 才暴露；找回 = find 全盘搜文件名 + mv 归位 + 重跑校验。

## 校验结果

71 条引文 0 MISS（含 S15 修复后）。S# 对账：主卡片用 S1-S15（S16 附录标注辅助）、深化用 S1-S16，无越界无孤儿号。

## 关键素材金句（写作期高价值）

- 导演自述：「我没有明确地想用什么颜色去做，主要是通过这个人物的性格、表情去影响、展现这个画面」
- 导演自述：「如果做成一个音乐剧的话，用欢乐的形式去做一个悲惨的故事，感觉会更强烈一点」
- 英维松子 Infobox：「2006 Japanese tragicomedy musical film」
- 影评人：「拍MV出身的中岛哲也给我们带来了一部超长的MV作品」
- 影评人：「低饱和度和冷色调……这种'冷冰冰'和中岛过往的'金灿灿'虽然对比鲜明」
