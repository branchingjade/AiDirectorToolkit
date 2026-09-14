---
name: visual-art-citation-workflow
description: "为已有美术规范的创作项目（国风/武侠/志怪/古装等）做文物考据+反核验+视觉落地工作流——针对美术规范的\"凭什么这么定\"\"参考谁谁长\"\"怎么落地做落地\"。触发：考据、美术考据、形象考据、文物参考、视觉考据、反核验美术设定、考据+反核验、art citation、art reference、visual research。"
version: 1.0.0
author: 妖玉
created: 2026-09-03
tags: [creative, art-citation, research, workflow, 国风, 美术, 反核验]
---

# 视觉艺术考据工作流 v1.0.0

## 🔒 门禁（加载后第一步，三问未答不进入执行）

考据不是另起炉灶——先问清楚：

1. **已有规范吗？**（美术设计规范文档已定 / /仅有口头描述 / /没有规范）
2. **考据对象是什么？**（某件器物 / 某角色服化道 / 某场景置景 / 整套色彩系统 / 全片美术风格）
3. **为什么做？**（给分镜落地做参考 / 给剧组采购做视觉凭证 / 给 CG 做可制作性反核验）

三问没答案时，不出方案——先反问：你手上正在写的这场戏卡在哪？

## 定位：创作项目的"凭什么"层（土壤+反核验）

```
规范文档（伏妖记美术设计_8more / 八美术纪律 / 等）
    ↓ "做什么"——回答"我们设定 X"
考据文档（本 Skill 产出）
    ↓ "凭什么"——回答"X 凭什么这么定、参考谁长、落地能否成立"
分镜 / 提示词 / CG 制作
```

**互补关系**：规范是执行源（剧组/美术组依此行事），考据是依据源（论证规范背后的文物/学界/制作可能性）+ 反核验（识别规范内部的冲突/不自洽处）。

## 核心工作流（5 步）

### 1. 锁定考据对象清单

**输入**：项目美术规范文档（如 `viking://resources/projects/伏妖记/06-美术设计.md/伏妖记美术设计/`）+ 飞书正本

**输出**：考据清单（人物/器物/场景/色彩 4 维）

| 维度 | 典型对象 | 考据依据源 |
|------|---------|----------|
| 器物 | 剑器、家具、法器、灯具 | 故宫数字文物库、上海博物馆、湖北省博物馆 |
| 服化道 | 直裰/道袍/锦缎/婚服 | 故宫服饰馆、明代墓葬出土实物、《明宫城图》|
| 置景 | 民居/祠堂/宫阙 | 徽州民居、唐大明宫遗址、敦煌壁画 |
| 色彩 | 主色/稀缺色/语义色 | 《芥子园画传》、唐代金碧山水、《营造法式》|

### 2. 实物+溯源（每件考据对象 4 段结构）

每件考据对象输出 4 段，**不可省**：

```
### <考据对象名>（时代 · 材质）
- 实物参考序列（表格：时代 | 实物名 | 关键形制 | 来源 URL）
- 考据（实物 → 作品设定的视觉逻辑推导）
- CG 落地要点（设定 / 落地门槛 ✅易/⚠️需预算/❌需替代方案）
- Seedance / ComfyUI 落地提示词骨架（21:9 / 色调 / 镜头 / 空气感）
```

### 3. 反核验（核心增量——规范文件反查）

**这一步是本 Skill 区别于"普通考据"的关键**。规范文件**只说"做什么"**，不查"是否合理"。考据必须反查：

- **稀缺色铁律反核验**：全片红色配额（典型"红只三处"）vs 实际红色物件（嫁衣 X2/剑穗/灼印/指尖血）——撞配额立即标决策留档
- **色彩语义分层**：金色妖力（单一色名）vs 多重含义（失控/受控/反派）——必须分层（暖金/高亮金/深金/浅金），否则观众看不出"妖力状态"
- **角色撞色**：同门师徒同色衣服 vs 视觉区分——必须拍板"色相同+色温不同"或"头饰区分"或"明暗不同"
- **CG 可制作性**：流体模拟/羽毛数百万片/特效光翼——评估替代方案（**八美术纪律 #3**）
- **形象冲突**：抽象概念（"善恶是天平"）vs 八美术纪律 #5（"妖是照妖镜"）——后者才能落地

反核验结论清单要写明 **冲突编号 + 冲突项 + 推荐路径 + 紧急度**——决策留档待用户拍板，不擅自解决。

### 4. 图源抓取+视觉验证（关键技术细节）

**反面案例（教训）**：本会话用 Wikimedia Commons `Special:FilePath/{name}` 抓图时，命中一张"Garuda_cliff_in_Tirumala"——**文件名叫 Garuda，实际是印度天然山崖，不是金翅鸟造像**。嵌入飞书后用户视觉验证才发现错——已删。

**正确姿势**（每张图嵌入前必走）：
1. Wikimedia Commons `Special:FilePath/{filename}` HEAD 探测命中 → urllib 下载本地（中文文件名用 `urllib.parse.quote` 编码）
2. 大图 ffmpeg 缩到 2400px 内（`q:v=5`，清明上河图 10MB→490KB 一次压缩）
4. **`vision_analyze` 视觉验证图片内容是否符合考据对象名**——是金翅鸟？还是山崖？是江帆楼阁？还是普通山水？
5. caption **必须明确标注"实物/仿本/真迹/某窟第几窟"**——不标就是隐性失信
6. 反核验发现名字错就**直接走 `docs +update --command block_delete --block-id <id>` 删错图**，再补正确的

**图源抓取 6 路**（按优先级）：
| 优先级 | 渠道 | 用法 |
|---|---|---|
| 1 | Wikimedia Commons Special:FilePath | 公开文物/字画高清扫描，** |
| 2 | 公开博物馆藏品页（故宫数字文物库 dpm.org.cn / 上博 shanghaimuseum.net / 国博） | 权威出处，但 lark-cli 直链会失败（403/下载限速）——需下载到本地再 `media-insert` |
| 3 | 数字敦煌开放素材库 ip.e-dunhuang.com（缩略图） | 登录后才有原图；缩略图水印重不能直接落地 |
| 4 | 公开图源聚合站（集古作网 jiguzuo.com、书格 shuge.org）| 台北故宫不让外网下载真品，**集古作网是真迹高清扫描的中转站**|
| 5 | ddgs images 反查 | **ddtext 搜不到时，image 搜索一秒命中**——本会话关键突破（359窟金翅鸟）|
| 6 | 搜内容页图片（敦煌研究院新闻稿/集古作网/baike.baidu.com） | 相对最广，需要再走一次抓 |

**失败路径处理**：
- WikiCommons 没某图 → 退到数字敦煌 → 缩略图带水印不能用 → **走集古作网/书格** → 都没有 → 标注"待用户浏览器补图"作为留档
- 不要把仿本/摹本说成真品——caption 必须区分

### 5. 飞书 docs 嵌图工作流（lark-cli 5 步）

```
① docs +media-insert --file ./相对路径 --doc <token> --width 120 --caption "<考证caption>"
   → 关键：--file 必须 cwd 相对路径（绝对路径报 unsafe file path）
② docs +update --command overwrite 不动图，但会**冲掉已存在的图块到文末**
   → 顺序：先写文本 → 最后 media-insert 图
③ docs +update --command block_delete --block-id <id> 可删错图
④ docs +update --command block_replace --block-id <img_id> --content <新caption>
   → 改 caption，但 block_replace 会把整张图块替换为文本块（图像消失）——需再重插
⑤ docs +media-preview --token <file_token> --output ./<验证文件名>
   → 用 bot 身份下载回本地 + vision_analyze 视觉验证
```

## 关键陷阱（v1.0 实战确立）

### 1. Wikimedia Commons 文件名误导

文件名是中文/英文可能完全不准。**必须 `vision_analyze` 视觉验证后才嵌入飞书 doc**。本次错抓的 Garuda_cliff_in_Tirumala 就是典型——文件名含 Garuda 但内容是印度山崖。

### 2. 飞书 markdown 图片语法 ≠ 真下载

`![alt](https://upload.wikimedia.org/...jpg)` 在 markdown 内容里不会触发飞书服务端下载 Wikimedia URL——返回 `partial_success degrade_code=2108` 警告，图位置但占空。**必须先下载到本地再 `media-insert`**。

### 3. overwrite 冲掉已插图

`docs +update --command overwrite` 会**完全替换文本+块，已 media-insert 的图片块会被冲到文末**（或消失，取决于实现版本）。**正确顺序**：先 `overwrite` 写文本 → 再 `media-insert` 图。

### 4. block_replace 会替换整块

`docs +update --command block_replace --block-id <img_id> --content <新caption>` 会**把整张图替换为 caption 文本块**（图像消失，caption 仅文字）。改 caption 必须**先 media-insert 新图 + block_delete 旧图**两步。

### 5. lark-cli --file 必须相对路径

`--file C:/...绝对路径` 报 `unsafe file path: --file must be a relative path within the current directory`。**绝对路径要走 cwd 相对路径**（或先用 `shutil.copy` 拷到 cwd 子目录）。`--output` 同理。

### 6. ddgs 装包方式

ddgs 不在 Hermes venv 默认包——`uv pip install --python <hermes-venv>/Scripts/python.exe ddgs`（**ddgs**，不是 duckduckgo-search 也不是 ddgo）。新装后**下次新对话**生效，当前对话已固定用旧后端。

### 7. 嵌入飞书前**必须先 vision_analyze**

每张图嵌入飞书前**必须 `vision_analyze` 验证内容**——文件名不可信，特别 Wikimedia Commons 中文文件名。本会话错抓 Garuda 教训。

### 8. 反核验决策不擅自解决

发现冲突（F001-F008 编号）→ 写进 MOC 反核验结论清单，**不擅自改规范**——用户拍板后再落。常见冲突类型：

- 稀缺色配额撞（红只三处 vs 实际四件红物件）
- 角色撞色（同门师徒同色衣服）
- 色彩语义分层不够（单一色名多重含义）
- 实体形象违背八美术纪律 #5（抽象概念做成具象符号）
- 设定道具不进剧情使用（白骨头颅"表现的不好"）

## 配套生态

- **飞书 docs 写操作**：`lark-doc` skill（**lark-doc 是 hub-installed protected**，只读其 references；不要尝试改它的 SKILL.md）
- **Obsidian 同步**：项目目录作 git 归档层（非权威源），写入后 `git add + commit + push`
- **OpenViking 公共空间**：项目美术考据可挂 `viking://resources/projects/<项目>/13-美术考据/` 作为团队共享索引
- **图源聚合站汇总**：见 `references/常用图源.md`（v1.0 实战清单）
- **飞书 docs 嵌图细节**：见 `references/飞书嵌图工作流.md`（lark-cli 5 步）

## 参考

- `references/常用图源.md` — Wikimedia/数字敦煌/集古作网/书格 等 6 路图源实测清单（含失败路径）
- `references/飞书嵌图工作流.md` — lark-cli 5 步嵌图+删图+改 caption（含 overwrite 冲图陷阱、block_replace 替换整块陷阱）
- `references/反核验清单模板.md` — F001-F008 模板（稀缺色配额/角色撞色/色彩语义分层/实体形象/道具使用）
- `references/视觉验证步骤.md` — vision_analyze 验证图片内容的 5 步（含 Wikimedia 中文文件名不可信、敦煌研究院缩略图水印重）