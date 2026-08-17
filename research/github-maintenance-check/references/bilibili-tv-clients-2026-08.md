# B站 TV 客户端生态盘点（2026-08-09 GitHub API 实测）

数据来源：`api.github.com/repos/<owner>/<repo>` 的 pushed_at/archived/stargazers_count + releases 列表，2026-08-09 逐一实测。用户是影视从业者，看片/研习场景可能反复用到。

## 活跃维护（近 1-2 个月有提交，2026-08 时点）

| 项目 | 最后版本/日期 | star | 特点 |
|---|---|---|---|
| **BT**（chinasoul/BT） | v0.9.32 / 2026-08-03 | 1.4k | Kotlin 原生 TV 客户端；安卓 4.4+（老盒子友好，api19-22 兼容包）；播放器细节派：CDN 锁死/多线测速、章节/高能、UP 记忆倍速、浅色主题、开机密码；README 极简，功能要扒 release notes |
| **MyTVB/MyBili**（qianxuntudou-ops/MyTVB） | v1.6.10 / 2026-08-05 | 227 | 像素级对齐已归档的 BLBL（界面成熟度有继承）；内容形态派：直播+CCTV 央视 1-17 套遥控器切台、抖音模式（上下滑推荐）、互动视频、青少年模式、AkDanmaku 弹幕防挡；minSdk 23（安卓 6.0+）；代码由 Codex/智谱 AI 编写（作者自述） |
| **bilibilitv1.6.6-repair**（qidian55） | 2026-06-13 | 2.6k | 官方经典 1.6.6 版修复（官方 TV 版失效后的老牌救星），兼容安卓 4.0.4 |
| **BBLLV5**（swyefun/BBLLV5） | 2026-06-10 | 1.5k | BBLL 停更后的修复续作（反编译续命）；已知坑：csrf 失败/卡黑屏→清数据、source error→切 AVC/AV1、登录几小时被风控→换登录方式 |
| **BV 修改版**（Frost819/bv） | 2026-06-09 | 3.4k | 原版 aaa1115910/bv 大陆不可用的 fork 修复 |

## 排除（2026-08 时点）

- **BBLL 原版**（xiaye13579/BBLL）：17.4k star 但 2025-02-28 v1.5.2 后停更——star 高≠维护中的经典反例
- **aaa1115910/bv 原版**：README 自述"不能在大陆用"
- **blbl**（cat3399/blbl）：archived 已归档（MyTVB 是它的 AI 复刻延续）
- **peacefulprogram/BilibiliTv**：archived
- 其他低活性 fork：Leelion96/bv（2025-11）、dlee20081/BV（2025-07，2 star）

## 选型要点（2026-08 时点结论）

- 安卓 5.1 以下老设备 → 只能 BT
- 要直播/央视/上下滑刷视频 → MyTVB
- 追求播放器细节（锁 CDN 线路/倍速记忆/章节高能）→ BT
- 两个都是每周一版在更，可都装各用几天再留

## 候选发现捷径

- **oldsento/bilibili-client-software-collection**：第三方 B 站客户端收集列表（2026-06 更新），TV/安卓/PC/LG webOS 全覆盖，README 带更新时间——先看它再逐个 API 验证
- 贴吧 bilibilitv 吧：用户反馈"都用不了了"的第一现场，可作为停更/失效信号
- 共同风险：个人封装官方 API，B 站一收紧风控就集体失效——推荐时明说，选近 2 个月还在更新的
