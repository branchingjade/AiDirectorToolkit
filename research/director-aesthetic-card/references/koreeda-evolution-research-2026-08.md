# 是枝裕和轮来源地图（2026-08，第九轮手法体系深化）

产出：`film-suite-research/技法卡片源稿/是枝裕和_手法体系深化.md`（269 行，7 节：作品矩阵速览/创作路线三线/手法演变四脉/工具箱 9 件/对比定位/诚实声明/来源清单）

## 本轮特征：纯存量复用，零新抓取

17 个 `pages/koreeda_*.txt` 存量覆盖全部证据（是枝裕和导演美学卡片轮已备好），本轮仅：
- 读存量 + 本地资产
- 补证《小偷家族》季节循环：grep 剧本整理稿 `_tmp/kazoku_full.txt` 拿季节行号
- 未抓任何新网页（豆瓣/百度百科均未重试）

## 存档↔内容对照（S1-S17，与主卡片共用编号表）

| # | 文件 | 内容 | 本轮关键用途 |
|---|---|---|---|
| S1 | koreeda_wiki_main.txt | 主条目：纪录片履历 | 纪录片线履历 |
| S2 | koreeda_wiki_shoplifters.txt | 小偷家族条目 | 海边/公交追跑结局、拍摄始于 2017-12、"小黑鱼"引文、Time Out"modern-day Ozu" |
| S3 | koreeda_wiki_stillwalking.txt | 步履不停条目 | 蝴蝶戏、闪前收束、Ebert"小津传人" |
| S4 | koreeda_wiki_nobodyknows.txt | 无人知晓条目 | 拍一年/按时间顺序/公寓租一年（时间方法铁证）、行李箱埋葬、discreet camera（经维基转引日本时报） |
| S5 | koreeda_guardian2015_wb.txt | Guardian 2015 访谈 | "更接近成濑与肯·洛奇"、细节论、食物即家庭、填补空缺论 |
| S6 | koreeda_mubi2009_wb.txt | MUBI 2009 访谈 | "dry, light"调性论 |
| S7 | koreeda_japantimes_wb.txt | Japan Times 2018 | 无血缘家庭论（戛纳获奖后） |
| S8 | koreeda_deadline_wb.txt | Deadline 2018 访谈 | 家庭定义演变链条（如父如子→小偷家族）、home drama 类型自觉、宽视角 |
| S9 | koreeda_criterion_lim.txt | Criterion: Dennis Lim《Still Walking》essay | 餐桌=玛德琳、纪录片反哺虚构（无人知晓←另一种教育）、成濑对比 |
| S10 | koreeda_criterion_kiki.txt | Criterion: Koresky（树木希林） | 刮胡萝卜皮开场、祭坛入画边缘 |
| S11 | koreeda_criterion_afterlife.txt | Criterion: 是枝裕和《下一站，天国》小说后记英译 | 一手："把虚构拍得像纪录片"、"你不是我"、500 人采访 |
| S12 | koreeda_criterion_alinmemoriam.txt | Criterion: Viet Thanh Nguyen《After Life》essay | "尊重距离"、"几乎没有音乐"、素人出演 |
| S13 | koreeda_guardian_shop_review.txt | Guardian 影评（Bradshaw） | "细笔触" |
| S14 | koreeda_guardian_shop_review2.txt | Observer 影评（Kermode） | "发光的摄影驯化残酷"、滚手指手势 |
| S15 | koreeda_lwl.txt | Little White Lies 影评（Webb） | 冷水面→做爱、静默崩塌 |
| S16 | koreeda_baike.txt | 百度百科（jina） | 群像同框（经百科转引新浪）、侯孝贤影响 |
| S17 | koreeda_criterion_sw.txt | Criterion《Still Walking》条目页 | 官方简介"simple gestures and domestic routines"（最轻动作表述） |

本地资产：[卡A] 导演美学卡片、[卡B] 小偷家族技法卡片（场次拆解）、[剧本] `_tmp/kazoku_full.txt`（juben.pro 79 场）、[卡C] 小津卡片、[卡D] 杨德昌卡片。

## 四脉演变的取证结构（可作后续轮模板）

1. **最轻动作**：四级下压表（S17 切菜=唤起一生 → S5 食物即家庭 → S15 冷水面→做爱 → S2 海边死亡），每级单列证据；提炼句"重量不变，动作越来越小"标注为本代理归纳。
2. **家庭定义**：**导演自述即完整链条**（S8：如父如子"血缘vs共处时间"→小偷家族"超越血缘"；S5 填补空缺论）——最强证据形态，无需推断。
3. **时间方法**：三级演变（S4 实拍一年=制作伦理 → S3/S9 一天+闪前=叙事结构 → 剧本+[S2] 季节循环=容器）；剧本 grep 见下。
4. **生死观**：S4 行李箱埋葬 vs S2 "不会孤独地死" vs S3 扫墓仪式——死亡从"事实"变"关系注脚"。

## 剧本 grep 取证配方（本轮新技巧）

```bash
grep -n -E "冬天|下雪|雪|夏天|夏季|春天|樱花|季节|天气|冷|热" "_tmp/kazoku_full.txt"
# 命中：场1-2 冬夜捡尤里（"真冷啊…好像要下雪了"）、场749 海边（"抱怨天气很热"）、
#       场1062-1100 雪中离别（"街道上铺满了雪…我们堆雪人吧"）→ 季节循环双证（+英维剧情）
```

要点：事实层（剧本行号+维基剧情）与意图层（"导演自觉以四季为结构"）分开标——意图层无导演原话，标「未取证到」。

## 未取证清单（延续主卡片）

- 豆瓣影评：JS 登录壳，未取证到（koreeda_douban_shoplifters*.txt 留档）
- 海边"奶奶口型说谢谢"：中文影迷圈流传，全部英文渠道未提及，维持未取证
- "最轻动作"术语：导演无此命名，用等值原话 dry, light / simple gestures and domestic routines
- 四季结构为导演自觉：无原话，仅剧本+成片证据（本代理归纳）

## 对比节做法

vs 小津/杨德昌：完全复用本地两张导演卡片（[卡C][卡D]）的已取证事实，对比判断标注"本代理归纳"；导演自我定位（S5"更接近成濑与肯·洛奇"）与 Lim 学术对比（S9）单列——零新抓取完成对比节，验证"优先复用本地已有导演卡片作转引链"纪律。
