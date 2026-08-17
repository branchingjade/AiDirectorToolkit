# 豆包音频生成 API（POST /api/v3/tts/create）速查

来源：docs.volcengine.com/docs/6561/2550782（2026-07 抓取）+ 多轮实测。

## 端点与鉴权

- `POST https://openspeech.bytedance.com/api/v3/tts/create`
- Header：`X-Api-Key`（新版控制台单头鉴权）；可选 `X-Api-Request-Id` 追踪

## 关键行为（实测，文档没写清）

- **成功响应没有 `code` 字段**，只有 `audio`/`url`/`duration`。判错：`code = data.get("code"); if code is not None and code != 0`。**禁止**写 `data.get("code", -1)`——成功时缺省 code 会被误判成 -1。
- 成功字段：`audio`(base64) / `url`(CDN 链接，2h过期) / `duration`(变速后) / `original_duration`(原始=计费时长，上限120s) / `subtitle`(需 enable_subtitle=true)
- **图片参考与音频参考互斥**：不能同传
- 纯文本生成模式：不传 references，音色完全由 text_prompt 中的自然语言描述决定（非"默认音色"）

## 请求体

| 字段 | 说明 |
|------|------|
| model | `seed-audio-1.0`（中英）/ `seed-audio-1.0-multilingual`（18语种 + text_prompt 时间轴控制 `[2s:5s]`） |
| text_prompt | ≤3000 字符；纯文本 / `@音频N` 引用参考音频（从1编号，最多3条） |
| references[] | 音频≤3条，每条≤30s≤10MB（wav/mp3/pcm/ogg_opus）；图片≤1张≤10MB（jpeg/png/webp）。组合：纯文本 / 文本+图片 / 文本+音频 |
| references[].speaker | 音色ID，与 audio_data/audio_url 互斥 |
| audio_config.format | wav（用户默认）/ mp3 / ogg_opus / pcm |
| audio_config.sample_rate | 默认 44100；可选 48000/44100/40000/32000/24000/16000/8000 |
| audio_config.speech_rate / pitch_rate / loudness_rate | 默认 0，范围 -100~100 |
| audio_config.enable_subtitle | bool |
| watermark | object，`{}` |

## 限流

10 并发 + 5 次/分钟 + 20000 字符/分钟。输出最长约 120s。

## 部署案例：doubao-tts-server（v3.0，2026-08-10）

项目正本：`~/Documents/Hermes/Projects/doubao-tts-server/`（git 分支 `v2.2-dual-panel`）
NAS 运行：`192.168.1.2:8000`（Docker + compose，重启自恢复，容器名 doubao-tts）

**架构：** FastAPI wrapper → doubao_client → 豆包语音 API。SQLite 持久化 + **音频落盘**都在 Docker volume（`/data`，AUDIO_DIR 默认 `/data/audio`）。

**v3 新增能力：**
- **音频永久持久化**：生成时 base64 落盘 `/data/audio/{id}.{format}`，历史播放/下载走本地 `/audio/{id}`（CDN 2h 过期链接只留档 audio_cdn 字段）——修复了历史音频 2h 后失效的 bug
- **批量生成**：`POST /tts/batch`（SSE 流式），两种模式：`texts` 显式分段 / `text` 长文本自动切分（按空行→句子边界→硬切，单段 ≤300 字≈75s，`app/text_splitter.py`）
- **字幕 SRT**：enable_subtitle 结果存库，`GET /audio/{id}/srt` 导出（subtitle JSON → SRT，时间单位毫秒，兼容秒）
- **限流自愈**：进程级节流（间隔 ≥12s 满足 5次/分钟）+ 429/5xx 自动重试（15/30/60s 退避，`_Throttle`）
- **前端 v3**：批量进度条（SSE 逐段推送）、分段结果卡片、历史批次徽标、生成中可停止（AbortController）、老记录无本地文件不显示播放

**接口：**
- `GET /` — Web UI（双栏：左输入+结果+历史，右参数面板常驻）
- `POST /tts` — 单条 JSON（含字幕）
- `POST /tts/batch` — 批量 SSE（texts/text 二选一）
- `POST /tts/simple?text=...` — 简化 query 参数版
- `GET /history` — 历史（本地 URL 注入）
- `GET /audio/{id}` / `?download=1` / `/srt` — 本地音频播放/下载/字幕
- `DELETE /history/{id}` / `DELETE /history/batch/{batch_id}` — 删除（连带音频文件）

**测试：** `tests/smoke_v3.py`（42 项 mock 全链路）、`tests/verify_live.py`（真实 API 8 项）、`tests/deploy_nas.py`（base64 管道部署+重建）。部署后必跑 verify_live 真实验证。

**交互重设计（v3.1，2026-08-10，按前端设计知识库规范）：**
- 删除 confirm() 弹窗 → 行内二次确认（点→变红「确认删除」3s 失效，NN/g 撤销优于确认框）
- 批量/单条失败 → 就地红色错误卡+错误信息+重试按钮（错误就地可行动，batchCtx 单段重试替换卡片）
- 单条生成 → 不确定进度条「正在生成…通常 10-30 秒」（加载>1s 进度提示）
- 历史播放 busy 时禁止+提示，播放标注「历史」来源（不覆盖结果区）
- 批量完成 → 底部工具条「下载全部 N 段」（逐段触发）
- 无障碍：音色字段 aria-label、上传槽 role=button+tabindex+键盘触发、全交互元素 focus-visible outline
- 4K 适配关键经验：用户 4K+150% 缩放+浏览器 75% 缩放 → 视口 3403px，物理像素检测只判 is-3k；wrap 必须 calc(100vw-80px) 自适应视口，面板 minmax(360px,22vw)，scale 1.3 补偿浏览器缩小

**v4.0 配音工作台（2026-08-10，grilling 设计树收敛后落地）：**
- **四视图 SPA**：侧边栏常驻+可折叠（localStorage 持久化）导航 生成/工作台/历史/音色库
- **生成页**（纯生成保留）：单条/批量/错误卡重试/下载全部，结果卡「→ 工作台」送入当前项目
- **工作台**：轻量项目（localStorage）+ 纵向块列表（角色下拉来自音色库/文本可编辑→dirty 状态/拖拽排序）+ sticky 连播控制条 + **试变体**（数量可调默认2，差异①当前②音调+10，卡片「用这个」替换块音频）
- **历史页**：独立视图，搜索（300ms 防抖）+状态筛选+「→ 工作台」
- **音色库**：命名音色 CRUD（speaker ID / 参考音频 base64），工作台角色下拉联动
- **余额显示**：`GET /quota` 调火山 OpenAPI——Service=`speech_saas_prod`、Region=cn-north-1、`open.volcengineapi.com`、SignerV4 签名（volcengine SDK `pip install volcengine`，版本 1.0.x 非 1.9x！）；ResourcePacksStatus(Version=2025-05-20, POST body ResourceIDs[]) + QuotaMonitoring(Version=2025-05-21)；**资源 ID（volc.service_type.XXXXX）是账号特定的**，文档示例 10029 实测返回 Packs 空/配额 0/0；本地兜底=历史表 original_duration 统计今日/本月时长。compose environment 必须显式加 VOLC_AK/VOLC_SK（.env 文件不会自动进容器）
- **⚠️ 火山监控 API 完整结论（2026-08-11 实测两轮，commit 16f0e17 + 6852da3）**：
  - `ResourcePacksStatus`（资源包剩余，Version=2025-05-20）：**ProjectName 是必选参数**（只传 ResourceIDs 报 500 InternalError；补 ProjectName/Types/PageSize 后 HTTP 200）。返回 `Packs[].Harvest{PurchasedAmount,CurrentUsage,Unit}` + `TotalHarvests[]`，剩余=购买-已用，Unit 实测为 characters/seconds 等
  - `QuotaMonitoring`（配额查询，Version=2025-05-21）：**官方 QuotaType 仅 qps/concurrency/qpm/tpm**（传其他值虽 200 但全 0 无意义；不传默认 concurrency 全 0）。查的是配额不是用量，时间范围建议 ≤7 天（文档明确）
  - `UsageMonitoring`（调用量查询，这才是用量）：**Mode=daily 是必选参数**（漏了报 InvalidParameter——曾误判「参数不明」）；UsageType 实测支持 text_words/duration/characters（时长包看 duration），返回按天 `{Day, Value, UsageType}`
  - **资源 ID 三连坑（已全部解掉，2026-08-11 终版，commit dfa52c7）**：①ResourceID/BlueprintID 必选，**OpenAPI 无法枚举账号资源**（ListAPIKeys/ServiceStatus 均不带资源信息）；②真实 ID 格式 `volc.service_type.XXXXX`，**获取唯一路径=借用户浏览器登录态调控制台内部 API**：WebBridge evaluate fetch `https://console.volcengine.com/api/top/speech_saas_prod/cn-north-1/2025-05-20/ListServiceTypes`（POST 空 body，header 带 `X-CSRF-Token`=cookie `csrfToken` 值）→ 响应 Items[].ResourceID 全量服务列表；③**资源包实例号 ≠ ResourceID**——用户从控制台拿的 `SeedAudio1.02000000863924357890` 是 `Packs[].InstanceNumber`（创作版-时长包30分钟），传入 RPS 返回 200 但 TotalCount=0、QM/UM 直接 500。**本账号 seedaudio 真实 ID = `volc.service_type.10074`**（Name=「创作版」UsageType=audio_duration，.env 已更新）；**ResourcePacksStatus 必须带 Types=`["access","quota","prepaid"]` 否则返回空**；UsageMonitoring 的 UsageType 实测应为 `audio_duration`（单位=小时）。实测余额：免费礼包 60分钟-已用14.64 + 创作版30分钟 = 剩余 75.4分钟
  - 控制台入口：API Key 管理页 `https://console.volcengine.com/speech/new/setting/apikeys?projectName=default`（新版控制台路径，文档链接可挖）
  - 📎 完整调试笔记（参数表/资源ID识别/控制台内部API探测路径/WebBridge操作技巧）见 `references/volc-quota-api.md`
- **素材管理（2026-08-11，commit fbcbc65）**：`/assets` 素材列表（有本地文件的记录，语义化名/时长/大小）、`/assets/rename` 语义化重命名（`{id}_{YYYYMMDD}_{音色}_{文本前12字}_{时长}s.{fmt}`，幂等，同步 db.audio_file）、`/assets/export` 批量 zip（zip 内语义化名）；audio_path 优先 db.audio_file 并兼容 `{id}.`/`{id}_` 前缀；前端历史页「素材管理」弹层（全选/导出/重命名）；Hermes 侧 CLI `scripts/tts_assets.py`（list/export/rename，`TTS_HOST` 环境变量覆盖）。⚠️ 部署大文件（page.html 99KB+）必须 base64 分块（每块 60KB）——单条命令行 ~132KB 超 SSH channel 限制；绿联 NAS SFTP 看不到 /volume1/docker/（共享根映射怪癖），别走 sftp
- **AI 配音助手（2026-08-11，commit d143f97）**：工作台内置专职 AI 助手——架构：前端聊天面板（工作台底部，自动附带项目/块/音色上下文）→ TTS 后端 `/chat` 代理（专职 system prompt：文本润色/角色音色/生成策略/素材管理，可用 curl 调 /assets 等 API）→ 本机 Hermes **API Server**（OpenAI 兼容，端口 8642）。本机配置：`~/.hermes` 即 `$LOCALAPPDATA/hermes/.env` 加 `API_SERVER_ENABLED=true` + `API_SERVER_HOST=0.0.0.0`（默认 127.0.0.1，NAS 访问必须 0.0.0.0）+ `API_SERVER_KEY=<openssl rand -hex 32>`（弱 key 拒绝启动）；**compose 必须显式注入 HERMES_API_URL/HERMES_API_KEY**（.env 不自动进容器，两次踩坑）。⚠️ gateway 重启：schtasks /End 杀不净（PID 不变），须 `taskkill /F /PID <gateway_pid>` 再 `schtasks /Run /TN Hermes_Gateway`；API_SERVER_KEY 传 NAS 用 python 拼接（shell $VAR 在远端不展开）
- **数据上云 + Eagle 打通（2026-08-12，commit cb2e824）**：①projects/voices 存 NAS sqlite（db.py 新表 + GET/PUT/DELETE API），前端 initData 首启 localStorage→NAS 迁移、写操作 400ms 防抖同步、离线回退本地；②删除改 toast 撤销（5 秒窗口）；③生成页历史区块升级完整检索（搜索/筛选/分页）；④**Eagle 4.0 集成关键坑**（实测）：API base `http://localhost:41595/api`，`Access-Control-Allow-Origin: *`（GET 可直连）；**导入端点是 `item/addFromURL`**（createFromURL/createFromPath 已 404）；**POST 必须 `Content-Type: text/plain`**（JSON 会触发 CORS preflight OPTIONS，Eagle 不响应 → Failed to fetch）；**下载 404 的 URL 也返回 `{"status":"success"}`（假成功）**——调试时用真实存在的素材 id；重复文件处理=发送前 `GET /api/item/list?limit=5000` 按 `size` 字段查重（Eagle item.size 与素材 size 一致，同素材必然命中），命中则跳过不弹窗；name/annotation/tags 参数不可靠（Eagle 可能改写，如 115→「铁门」）；Eagle 库文件在 NAS 共享盘（HMSJ_B.library）
- **助手入口精灵图标（2026-08-11，commit 725a900）**：助手入口从工作台内嵌横条改为**全局悬浮 orb**——fixed 右下 22px、50px 圆形径向渐变球体 + 🤖（hover 上浮蓝色微光、打开时呼吸光环脉冲 `@keyframes orbPulse`）+ 点击弹出浮窗（390px 右下 `pop` 动画 `transform-origin:bottom right`、头部标题/功能说明/✕ 关闭、消息区、输入框）。全页面可见（生成/工作台/历史/音色库），不再局限于工作台。**前端 UI 目测法**：本机 FastAPI 起不来（hermes venv pydantic 损坏，系统 3.12 也带损坏 site-packages）时，`python3 -m http.server <port>` 起静态服务直接开 page.html + browser_vision 验证（图标悬浮/面板弹出/布局）——无需后端依赖，改前端最快要路径
- **精灵可拖动 + 面板锚定（2026-08-11，commit 929da13 + 9f498a4）**：①拖动实现——orb `mousedown` 记起点，document `mousemove/mouseup` 跟随，**4px 移动阈值区分点击/拖动**（超阈值=拖动不打开面板，松手位置即记，`left/top` 覆盖默认 right/bottom；`touch-action:none` 防触屏滚动；子元素 `pointer-events:none` 防事件抢占）；②面板定位跟随精灵——展开时精灵上方居中，**居中放不下（clamp 偏移大）锚点翻转改侧弹**（精灵偏右→面板贴左 `r.left-pw-10`、偏左→贴右 `r.right+10`，垂直居中，窗口 resize 重定位）；③展开 UI 细节：头部（图标+标题+副标题+关闭）、状态栏（🟢 已连接 Hermes）、消息气泡不对称圆角（助手左下尖 `12px 12px 12px 4px`/用户右下尖）、thinking 闪烁点动画、输入框 focus 蓝环、底部 kbd 快捷键提示
- **UI 评估方法论（2026-08-11 实测，浏览器工具双通道）**：**browser_vision 视觉模型会误读深色 UI**——深灰气泡 rgb(26,29,33)+浅白字被描述成「白色浅色模式」、暗色面板被说成「右上角浅色便签」。判断颜色/对比度/位置/重叠**必须以 browser_console 读 `getComputedStyle` + `getBoundingClientRect` 为准**（截图只给人看、不给判断）。⚠️ CDP 模拟点击/拖动：dispatchEvent MouseEvent **不传 clientX/clientY 时默认 0,0**——mousedown 在 A 点、mouseup 在 (0,0) 会被 4px 阈值误判为「拖动」→ 面板不打开，这是测试脚本坑不是产品 bug（真实鼠标不动坐标不变）；模拟交互必须给 mouseup 传同坐标。⚠️ 窄视口（如 778px 无头窗口）下 fixed 定位 clamp 到边界会让面板「看起来」与锚点分离错位，实为大屏正常——下结论前先查 `window.innerWidth` 排除视口假象。⚠️ **toast 生命周期 2.5s**：UI 操作后验证 toast 文案，等待必须 <2.5s（`time.sleep(1.5)` 再查）——sleep(4)/sleep(6)/sleep(8) 都会显示「none」误判为功能没触发（2026-08-12 踩两次）；要验证异步副作用（如 Eagle 入库）则 toast 检查后单独长轮询 API 确认，两者分开
- **「按钮不存在」≠ DOM 没有——先查 CSS 可见性（2026-08-12 f354bc6 教训）**：用户说「没做按钮吗，导入 Eagle 的、下载按钮也没有」时，按钮其实在 DOM 里，但 `.hc-ops` 是 `opacity:0; pointer-events:none`（hover 才显示，v4.3 的「hover 滑出」设计）——用户不 hover 就以为没做。修复=主操作按钮常显（`opacity:.92; pointer-events:auto`），hover 只做增强不隐藏。排查顺序：`querySelector` 数按钮 → `getComputedStyle` 查 opacity/pointer-events → 确认是否 hover-gated。**用户对「主操作藏进 hover」零容忍——工具 UI 操作按钮默认常显，hover 滑出只适合纯装饰性操作区**
- **浏览器缓存 API 响应会制造幻影 bug**：动态 JSON 端点（/history 等）无 `Cache-Control` 头时浏览器启发式缓存旧响应——后端修了 download_url 但页面仍渲染旧数据（「下载按钮没有」假象之二）。修复双保险：后端 `return JSONResponse(..., headers={"Cache-Control":"no-store"})`（注意 JSONResponse 要显式 import）+ 前端 `fetch(url,{cache:'no-store'})`。排查「数据没更新」先排除浏览器缓存，别急着改后端逻辑
- **两个相似列表模板可能不一致**（生成页「生成历史」loadGenHist vs 历史页 loadHist）：同款卡片有两份模板，补按钮只改一份，用户看到的另一份仍缺。`grep` 两个函数确认都改；`querySelector('.hist-card')` 全文档取到的第一张卡可能是**生成页的**（DOM 常驻即使视图隐藏）——验证时按 `#genHistList` / `#hList` 精确选择器查，别只信一个列表
- **UI 铁律**：不用 prompt()/confirm() 原生弹窗（行内表单+armed 二次确认）；试变体数量上限 3（限流 5/min）
- **UI 审计优化（2026-08-11，commit 未编号，知识库驱动）**：加载 `前端设计知识库` skill 6 份 references（UI交互/暗色主题/组件/状态/布局/表单）+ `impeccable` skill 作评估基准，逐页 browser_vision 截图评审四视图+助手面板，共修 8 项：
  - **focus 态对比度**（WCAG 1.4.11）：全站输入框 focus 从 `var(--faint)`（~2.3:1）改为 `var(--focus)` 蓝色 + `box-shadow:0 0 0 1px` 光环（≥3:1）
  - **导航选中态左侧标记**（Material 3）：`.nav-item.active::before` 2px 白色竖条（`left:0` 不能用负值——sidebar `overflow-y:auto` 会裁剪）
  - **`prefers-reduced-motion` 降级**（WCAG 2.3.3）：全局 `@media(prefers-reduced-motion:reduce)` 关闭非必要动画
  - **空状态加图标**（NN/g 三件套）：工作台 📋 / 历史 📜 / 音色库 🎤 + `.empty-icon` 样式
  - **助手面板与精灵间距**：bottom 86px→90px（精灵 50px+22px=72px 高度区，面板需留 18px+ 间隙）
  - **消息气泡对比度**：`--surface2` → `--surface3` + `--line2` 边框（对比度 ≥3:1）
  - **滑块标签宽度**：2.4rem→2.6rem（「语速」不挤）
  - ⚠️ **`replace_all=true` 在 CSS 里批量替换的坑**：`var(--faint)` → `var(--focus);box-shadow:...` 误伤 6 处非 focus 语境（hover 边框/文字色/sentinel 色/空状态色）——批量替换只适合确定唯一语境的值（如 focus 态），多语境公共变量必须逐个验证

**v5.0 数据上云 + Eagle 打通（2026-08-13 轮，用户「协作性质为0」「真正打通eagle」）：**
- **项目/音色从 localStorage 上 NAS**（`db.py` 新增 `projects`/`voices` 表 + `main.py` CRUD：`GET /projects`、`PUT /projects/{id}`、`DELETE /projects/{id}`、`/voices` 同构；blocks 存 JSON 字符串）。前端异步化模式：**`initData()` 启动拉 NAS → NAS 空且 localStorage 有则一次性迁移推送 → 写操作 400ms 防抖全量 upsert（`persistProjects`/`persistVoices`）→ 失败回退 localStorage 并 toast「NAS 连接失败·已用本地数据」**；localStorage 保留作离线镜像。注意 persist 是 upsert 不删——**删除必须显式调 DELETE API**（delProject/delVoice 里 fetch DELETE + 撤销时 PUT 恢复）
- **删除交互进化：armed 二次确认 → toast 撤销**（v3.1 的 armed 已是过去式，2026-08-13 全部替换）：`toastUndo(msg, onUndo)` 5 秒窗口带「撤销」按钮（蓝色描边 `.toast.undo`），撤销恢复数据+重新同步。项目/块/音色可撤销；**历史记录不可逆保持 armed**。NN/g「撤销优于确认框」完整落地
- **生成页历史完整检索**：`loadGenHist()` 从 limit=10 升级为分页（30/页）+「加载更多」+ 搜索框（300ms 防抖 `ghSearchKey`）+ 状态筛选；空状态区分「还没有记录」vs「没有匹配的记录」（历史页加「清除筛选」按钮 `clearHistFilter`）
- **Eagle 4.0 真正打通**（本机 Eagle localhost:41595，`Access-Control-Allow-Origin: *` 支持跨域）：素材面板加「→ Eagle」按钮 + 连接状态徽章（`checkEagle()` 调 `/api/application/info`）。⚠️ **Eagle 4.0 API 三坑（2026-08-13 实测）**：①`createFromURL` 已废弃（404）——正确端点是 **`/api/item/addFromURL`**（POST {url,name,website,tags}，Eagle 自己下载 URL）；②**Eagle 不响应 CORS preflight（OPTIONS 404）**——浏览器 POST + `Content-Type: application/json` 必被拦（Failed to fetch），**用 `Content-Type: text/plain` + JSON body 绕 preflight**（服务器端 json 解析不依赖 content-type，实测 success）；③apiToken 在 `/api/application/info` 的 `preferences.developer.apiToken` 字段。详细端点探测表见 `references/eagle-api.md`
- **视觉体系收敛**：导航 emoji → 16px SVG 线性图标（stroke=currentColor 跟随主题）；12 处高频语义色 → 根变量 `--err-border/--err-bg/--ok-border/--accent-border/--accent-bg`（JS 批量替换时按精确串匹配，勿用 replace_all 误伤——见上文 UI 审计坑）
- ⚠️ **本地 JS 语法检查**：hermes venv/系统 3.12 的 pydantic 损坏起不了 FastAPI，但**改完 page.html 先 `python3` 提取 `<script>` 内容 → `node --check` 验证**（大改后必做，省一次部署往返）

**v5.1 平台化增量（2026-08-13，commit 8593bee）**：
- **音色参考音频落盘**（避免 sqlite 膨胀几十 MB）：base64 → `/data/voice_audio/{vid}.wav`，库存文件名；`PUT /voices` 带 `audio_b64` 自动落盘、`GET /voice_audio/{vid}` 播放端点、`list_voices` 检测存量 base64 自动迁移（`is_base64_like`：长度>4000 且无路径字符）；前端 playVoice 按 value 是否含 base64 分流（文件→端点 / 老数据→data URL）
- **数据备份导出/导入**：工作台工具栏「导出备份/导入备份」——项目+音色 JSON 一键导出（`{type:'tts-workbench-backup'}` 带版本）合并导入（按 id 覆盖）；audio 音色 value 导出时标 `[audio-file]`（音频文件不入备份，导入后需重建）
- **批量 Eagle**：素材面板「发送选中到 Eagle」——**同一快照查重**（eagleItems 缓存一次拉全量）+ 循环 addFromURL + 导入成功把 `{size,name}` 塞回快照防批内重复 + 汇总 toast（新增/跳过/失败）
- **助手操作闭环**：`_ASSISTANT_SYSTEM` 注入可执行命令（容器内 `curl http://127.0.0.1:8000/assets|/history|/quota|/assets/export|/assets/rename|DELETE /history/{id}`），助手从「给建议」升级为「能办事」——但删除/批量操作必须「先说明将执行什么，再执行」
- **SVG 收尾**：空状态图标（📜🎤🔍📋）+ 助手 orb/面板头 🤖 → SVG 线性图标（stroke=currentColor，`.empty-icon svg{2.2rem}`）；orb 的 SVG 用 `stroke="#f1f3f5"` 固定色（球体深底上 currentColor 不可见）

**v5.2 交互改造（2026-08-13，commit d60ff00，用户「批量发送 Eagle 做到外面」「历史面板的功能生成页面都要有」）：**
- **批量操作入口做到面板外**（用户原话「这是交互逻辑的问题」）：批量 Eagle 不再藏在素材管理弹层——历史页工具栏 + 生成页头各放「批量发送 Eagle」按钮，点击进入**卡片选择模式**（可复用模式）：
  - 状态：`_batchMode` + `_batchSel` Set；`batchEagleMode()` 切换并 toggle `.batch-mode` class（两个列表都切）+ 显示底部固定操作条 `.batch-bar`（「已选 N 个 · 发送选中到 Eagle · 取消」）
  - 卡片：`.hc-chk` 右上角选择圈（批量模式才显示）、`.sel` 蓝色高亮（`border-color:var(--focus)` + ring）
  - **点击分流**：卡片 onclick 改 `toggleBatch(id,this)&&openDetail(id)`——批量模式返回 false 短路不打开详情，普通模式放行
  - 发送后自动退出选择模式 + toast 汇总（新增/跳过/失败）
- **「历史面板的功能生成页面都要有」落地法**：生成页头补齐「素材管理」按钮（openAssets 弹层原本只在历史页工具栏）——**同一功能在多个视图出现时，逐个视图检查入口，别只加主视图**
- ⚠️ **批量操作前必须确保数据源已加载**：`exportSelectedToEagle(ids)` 卡片模式直调时 `_assets` 可能为空（只有打开素材面板/点单张 Eagle 才加载）→ 全部 `a` 找不到 → 全 fail（实测「失败 2」）。修复：函数开头 `if(!_assets.length)await fetch('/assets')` 兜底加载——**任何批量函数都要自备数据源加载，不依赖调用方**（这也呼应 f354bc6 教训：别假设前置状态）
- **批量查重快照模式**：批量循环用同一 `eagleItems()` 快照查重，成功导入的 `{size,name}` 现场 push 回快照防批内重复——比每发一个重新拉全量快一个数量级
- ⚠️ **v5.2 的「卡片选择模式」（模式开关式）已被用户否定（2026-08-13 当日，commit 529f9c9）**——用户原话「批量发送 Eagle 就直接权限了，逻辑不对，找同类对标」。**模式开关式交互（点按钮进入选择模式 → 模式里点卡片=选中、不打开详情）违反行业标准，被重构为常驻复选框方案**，见下方 v5.3

**v5.3 多选交互对标重构 + 平台化四件套（2026-08-13，commit 529f9c9 + ec302c5）：**
- **多选交互对标结论（用户「找同类对标」后的行业标准，Eagle/Finder/Notion/剪映素材库共性）**：①**选择能力常驻**——不是模式开关，复选框随时可用；②**勾选与打开解耦**——点卡片本体=打开详情，点复选框=选中，互不干扰（模式开关违反这条：行为突变）；③**选中即出操作条**——底部浮动条「已选 N · 全选本页 · 发送 · 清除」自动出现。落地：`.hc-chk` 右上角常驻复选框（hover 加深 opacity .55→1，`.sel` 蓝色描边+ring，`::after{content:"✓"}`），`onclick="event.stopPropagation();toggleChk(id,this)"` 与卡片 `onclick="openDetail(id)"` 互不干扰；工具栏「批量发送 Eagle」= 有选中直接发、无选中提示。**「批量 X」这类交互一律对标此模式，禁止再做模式开关**
- **A. AI 助手写权限**（从建议升级为动手改）：`_ASSISTANT_SYSTEM` 注入 `PUT /projects/{pid}`（**blocks 必须全量提交**——先 GET 拿完整 blocks → 改目标字段 → 全量 PUT 回）、`PUT /voices/{vid}`、增删项目；执行规则「修改前先说明 我将修改 XX（原值→新值）」；修改后告知用户已更新
- **B. 多设备冲突检测**（数据上云后的协作地基）：`PUT /projects` body 加 `base_updated_at`（客户端上次加载的版本戳）→ 服务器版本更新则 `409 {conflict:true, current:{最新数据}}`；前端 persist 带版本、409 时 toast「检测到其他设备修改，已加载最新版本」+ 用 current 替换本地。⚠️ **版本戳必须微秒精度**（`strftime("%Y-%m-%d %H:%M:%S.%f")`）——秒级在同秒两次 PUT 时时间戳相同、冲突检测失效（pytest 抓出）。响应返回 `updated_at` 供前端更新基准
- **C. 生成预设**：参数面板顶部「预设」下拉（自定义/解说腔 12,-4,6+字幕/旁白 -8,-8,-2+字幕/角色对白 4,8,0/音效 0,0,0）→ `applyPreset()` 设滑块+字幕+存 `prefs.preset`，`applyPrefs` 恢复下拉（不重放参数，仅回显）
- **D. 工程收尾**：`/assets` 分页（limit/offset + 前端「加载更多」，`_aOff/_aMore/_aLoading` 状态机）；**独立测试环境**——项目 `.venv`（Python 3.12）绕过 hermes venv pydantic 损坏；⚠️ **PYTHONPATH 环境变量指向 hermes-agent venv 会污染任何新 venv**（`python -m pytest` 加载 hermes 的损坏 pydantic_core → ModuleNotFoundError）——跑测试前 `unset PYTHONPATH`；`tests/test_api.py` 9 测试（health/quota 结构/projects CRUD/冲突 409/voices CRUD/音频落盘/history/assets 分页/备份契约），`TestClient` + 环境变量指向 tempfile 目录隔离真实数据
- **历史记录删除保持 armed 确认**（不可逆操作不加撤销）；项目/块/音色可撤销（toastUndo）

**v5.4 存为音色 + README（2026-08-13，commit f4f5b5c）：**
- **历史音频一键存为音色**（配音工作流闭环）：历史卡片/生成历史卡片「存为音色」按钮 → `POST /history/{id}/save-as-voice {name,note}`：`audio_store.audio_path(id, audio_file=...)` 拿完整路径 → `_file_to_b64` 转 base64 → `save_voice_audio(新vid, b64)` 落盘 → `db.upsert_voice(vid, name, "audio", fname, note)`；前端 prompt 命名 + 重拉 /voices 刷新音色库
- ⚠️ **两类可泛化 bug（部署前必查）**：①**「返回文件名 vs 返回路径」混淆**——`audio_file_of()` 返回文件名（无路径），`os.path.exists(src)` 按相对路径找 → 永远 False（cwd 是 /app 而文件在 /data/audio/）；凡拿文件做 exists/read 必须用返回完整路径的函数（`audio_path()`）。②**跨模块函数漏模块前缀**——main.py 里 `_file_to_b64(src)` 裸名调用（定义在 audio_store）→ NameError 500；同文件引用其他模块函数 grep 确认 `module.` 前缀
- **README.md 落地**：架构图（NAS↔Hermes API Server↔Eagle 三层）、功能清单、API 清单（16 端点）、部署（环境变量/compose 显式注入/部署脚本）、测试说明（unset PYTHONPATH + .venv）、踩坑索引（指向本文件）、目录结构
- **测试坑**：`db.save()` 返回 AUTOINCREMENT id——测试里假设固定 id（如 990）会 404，必须用返回值 `rid = db.save(...)` 再 `f"/history/{rid}/..."`；commit 前先跑 pytest（曾把带失败测试的 commit 推上去再补修）

**v4.1/v4.2 补丁（2026-08-10 同日）：** 生成页结果区下加「最近生成」区块（最近 10 条，`loadGenHist()`，单条/批量生成成功后自动刷新）；历史页与最近生成的行内预览改为 **Eagle 风格波形条**（`WaveEngine`，替代 `<audio controls>`）：
- Web Audio `decodeAudioData` 取 240 峰值点 → canvas 竖条波形（`<canvas>` 2x DPR 高清）
- 交互：居中 ▶ 播放按钮（播放时隐藏+波形行进）、**点击波形任意位置 seek**、播放进度白色高亮（rAF 更新）、右下角时长
- 性能：IntersectionObserver 可见才 fetch+decode（懒解码省流量）、峰值 Map 缓存（同 URL 只解码一次）、单 AudioContext 复用
- 波形点击 `stopPropagation` 防触发行展开；`.wave` 容器 `data-url`/`data-dur`，渲染后统一 `WaveEngine.init(container)` 扫描初始化
- 无本地文件的老记录不显示波形（正确降级）

**v4.3 历史页 Eagle 预览图网格（2026-08-10，用户「历史全部以预览图为主做成类似eagle的逻辑」）：**
- 历史页/最近生成从行列表 → **多列卡片网格**：`grid-template-columns:repeat(auto-fill,minmax(clamp(200px,20vw,260px),1fr))`（4K 3403px 视口实测 11 列，Eagle 素材库同款密度）；生成页小号 `minmax(clamp(170px,15vw,200px),1fr)` 保持视觉统一
- 卡片结构：`hc-wave`（大波形 52px，无音频灰条占位 28px）→ `hc-text`（-webkit-line-clamp:2 截断，点击展开）→ `hc-meta`（时间/批次徽标/时长+本地标记）→ `hc-ops`（**hover 滑出**：opacity 0→1 + translateY 4px + pointer-events 切换，内含 SRT/下载/→工作台/删除）
- 失败记录卡片 `.fail` 红边框；加载更多按钮保留（无限滚动）
- 坑：视图 display:none 时 `.wave` 的 clientWidth=0 → canvas 白屏 → `Math.max(clientWidth,170)*2` 兜底 + 解码回调里按实际宽重置绘图缓冲区

**v4.4 详情缩放面板 + 无限滚动（2026-08-10，用户「预览图占大头/原生缩放/看全部参数」）：**
- **预览图占大头**：卡片波形 52px→76px，卡片 minmax 加宽到 `clamp(220px,21vw,280px)`，`cursor:pointer`
- **点击卡片 → 生成详情 modal**（`.detail-overlay` fixed 遮罩 + `.detail` 980px 卡）：大波形（150px 高）→ 完整文本 → 信息网格（生成时间到秒/时长/状态/LogID/批次/本地音频 6 项）→ 参数网格（模型/格式/采样率/语速/音调/音量/字幕/音色/参考音频/参考图片 10 项）→ 操作（下载/字幕/→工作台/删除）
- **参数展示零后端改动**：历史表 CREATE TABLE 本就存全参列（model/speaker/format/sample_rate/speech_rate/pitch_rate/loudness_rate/enable_subtitle/has_audio_ref/has_image_ref），`/history` SELECT * 直接带出，前端 `_histCache` Map 存渲染过的 item 供 openDetail(id) 取
- **波形原生缩放**：峰值缓存升级为**双分辨率 `{hi:1200点, lo:240点}`**（解码一次，lo 由 hi 下采样）——卡片用 lo，详情用 hi；详情 zoom 1x/2x/4x/8x（ZOOMS 数组 + index 切换），窗口滑条 `detailWin` 控 offset 平移（window 占比 = offset×(1-1/zoom)），点击 canvas 全局比例 seek（`globalRatio=offset+ratio/zoom`），播放蓝进度线
- **无限滚动**：`IntersectionObserver(rootMargin:'600px')` 观察 hMore 哨兵 → 自动 loadHist()（hMore=false 时显示「已加载全部」），替换「加载更多」按钮；搜索/筛选仍触发 reset 加载
- 最近生成 head 加「查看全部 →」按钮跳历史页；Esc 关闭详情（document keydown）
- WebBridge evaluate 不支持返回 Promise —— 异步查询拆三步：`evaluate 切视图` → sleep → `evaluate 同步查 DOM`

## v4 工作台设计稿（2026-08-10 grill 决策树，用户拍板）

**形态**：A（ElevenLabs 块列表工作台）+ D（Suno 卡片试听变体）融合 + 保留纯生成页。

**视图结构**（侧边栏常驻+可折叠，折叠状态 localStorage 持久化）：
1. **生成**：纯生成页（输入+参数面板常驻+结果卡+批量下载/播放），不叠历史
2. **工作台**：项目下拉（新建/切换/重命名/删除 armed 确认）+ sticky 连播控制条（▶全部/⏸/第n块/上下块，播放时当前块高亮+滚动跟随）+ 纵向块列表（HTML5 拖拽排序）
3. **历史**：全屏列表+常驻搜索+筛选（全部/成功/失败），行操作含「送入工作台」
4. **音色库**：命名音色条目（名称+类型 speaker/参考音频+值+备注），工作台角色下拉与试变体差异都从这取

**核心交互**：
- 双向流转：生成页结果→「送入工作台」追加到当前项目；工作台块→重新生成/试变体
- 块卡片：序号+角色下拉+可编辑文本（编辑后状态「已修改·未生成」）+时长+状态徽标+五操作（▶/试变体/重新生成/下载/删除）
- 试变体：数量可调默认 2，就地展开卡片对比（①当前参数 ②音调+10 或换音色），「用这个」替换
- 数据模型（localStorage 三份）：Project{id,name,blocks} / Block{id,text,voiceId,audioUrl,status:未生成|生成中|已生成|失败|已修改} / Voice{id,name,type,value,note}
- **后端零新增接口**——现有 /tts /tts/batch /history /audio 全覆盖

**grill 教训**：用户选型要「具体参考」——给真实产品 UI 布局形态对比（ElevenLabs Studio 时间线/剪映内嵌/魔音工坊单段/魔音卡片流），配 ASCII 布局图+适合场景+对豆包 API 适配度，不给抽象概念选项。

## 余额显示（v4 健康区需求，事实已查证）

火山语音有余额/用量查询接口（API 参考→资源包/Quota 分类）：
- `ResourcePacksStatus`（资源包状态，返回 TotalHarvests 限额+Packs 资源包剩余，Version=2025-05-20）
- `QuotaMonitoring`（Quota 查询）/ `UsageMonitoring`（调用量查询）
- **鉴权 = 火山引擎 OpenAPI 签名体系（Action/Version + AK/SK）**，不是 openspeech 的 X-Api-Key——需用户提供火山控制台 AccessKey/SecretKey 配 .env（VOLC_AK/VOLC_SK），未配置时健康区降级显示「余额未配置」
- 「本日已用」可本地算（历史表 original_duration 求和），无需额外接口

**「用户看不到新版」排查链**（2026-08-10 两次实锤，部署后必查）：
1. 先验证服务端：磁盘源文件 / 容器内文件 / 端口实际响应三处 grep 新特征字符串（如 `retrySeg`），确认部署到位
2. HTML 响应加 `Cache-Control: no-store`（F5 必拿新版，别只让用户 Ctrl+Shift+R）
3. **布局/样式改动刷新即见；交互逻辑改动要操作才触发**——用户 F5 看外观没变说「没什么变化」时，用 Kimi WebBridge 实际操作演示（触发删除确认/生成进度+截图），或明确告知「点 X 看变化」，不是部署失败

**v4.5 打磨层（2026-08-10，用户「基本功能ok，接下来优化ui排版/交互/美观度」=功能冻结后纯视觉轮）：**
- **流程**：WebBridge 截四视图 → vision_analyze 专业评审（排版/对比度/控件/层级）→ 对照前端设计知识库规范筛选（**用户偏好硬约束：白按钮唯一重色不引入品牌色、参数常显不折叠、密度直给**——评审建议的折叠面板/品牌色直接否决）→ 在 `<style>` 末尾**追加「打磨层」覆盖规则**（不动功能/结构，风险最小，可整体回滚）
- 高价值项（实测有效）：自定义滚动条（暗色 10px 半透明 thumb）；侧边栏背景分层 #0b0c0e + active 左侧 2px 白色指示条（::before）；主按钮 pill→10px 圆角+inset 高光+悬停光效；参数面板 h3 分组线（border-top 分隔）；卡片 hover 浮起（translateY -2px + 0 8px 28px 阴影）+ 文本点亮 + 播放按钮 scale 放大；统一缓动 `cubic-bezier(.2,0,0,1)`（Material Motion，禁线性）
- **滑块已填充轨道坑**：`input.style.background` 对 range 无效——轨道是伪元素，必须 CSS 变量 `--track-fill` + `::-webkit-slider-runnable-track{background:var(--track-fill,...)}`，JS `setProperty('--track-fill', linear-gradient(to right, 亮 0~v%, 暗 v%~100%))`，`oninput`/初始化时调用
- 验证：vision 复评确认六项改进生效、无新视觉问题后收尾提交

**v4.3 视觉风格升级 B+C（2026-08-10，用户对 v4.2 打磨层反馈「没感觉有什么优化」→ clarify 后选 B 视觉换代+C 密度空间）：**
- **元教训（第二次「没感觉」类反馈，区别于 v3.1 的缓存/交互触发）：纯视觉微调（滚动条/hover/边框/间距/对比度）静态观感用户扫一眼感知不到，会当场说「没感觉有什么优化」**——不是部署问题（先 curl 验证字节数+no-store 排除缓存），是打磨层面选错了。正确路径：承认微调不可感知 → clarify 问优化层面（布局重排/视觉风格换代/密度/对标参考）→ 按所选做「一眼能看出变了」的结构级改动
- **B 视觉换代组合拳**（实测让用户满意）：①根变量换代——圆角阶梯 `--r:10px/--r-sm:6px/--r-lg:16px`、背景三层 `--surface:#0d0f11/--surface2:#131518/--surface3:#1a1d21`、文字对比度校准 `--fg:#f1f3f5/--muted:.62/--faint:.34`、正文 15px/1.6 行高基线 ②参数面板整块 → **独立分组卡片**（`.pgroup` 每组一卡：background surface + border line2 + hover 边框反馈 + h3 小字 uppercase；旧 h3 border-top 分组线规则改 `.panel>h3` 限定裸 h3 防冲突）——火山体验中心式模块化，是最大的「看得见」变化 ③输入区沉浸式（min-height 38vh/字号 1.06rem/行高 1.8）
- **C 密度空间**：历史网格 minmax 收紧（clamp(190px,18vw,250px)）→ 4K 更多列；无限滚动实测自动加载 60 卡（2 页无感）
- 约束不破：白按钮唯一重色（评审建议的品牌色否决）、参数常显不折叠、8pt 网格

**v5.5 子界面排查重构（2026-08-13，commit d971a42，用户「排查所有的子菜单，盘点有哪些需要重构的」「ui丑也是要改的」）：**
- **排查方法论**：①`grep` 列出全部次级 UI（overlay/form/panel/卡片模板）②浏览器实测每个的真实 DOM（按钮集/布局/disabled 态/`getComputedStyle`）③**功能一致性检查**——同一数据的所有呈现面板操作集对齐主列表（详情面板只有 [下载/工作台/删除] 而历史卡片有 6 操作 = 缺陷）④视觉丑点一并修（用户明确「ui丑也是要改的」，不只功能）
- **六项重构落地**：
  1. **详情面板操作补齐**：openDetail 的 ops 数组加 `→Eagle`（histToEagle）/`存为音色`（saveAsVoice），与历史卡片操作集完全对齐
  2. **音色选择统一**：生成页 `sSpeaker` 改 `<input list="voiceDl">` + `<datalist id="voiceDl">`——`renderVoices()` 同步重建 datalist（speaker 类型 option value=音色 ID，audio 类型 value=音色名+「（音频）」标注）——生成页与工作台块共用一套音色数据，消除双轨脱节
  3. **块卡片操作区独立行**：`block-ops` 从 `block-head` 内移出（head 只留 拖拽/编号/角色下拉/状态/时长），按钮改 `h-btn` 小号（▶试听/试变体/生成 primary 蓝底/删除 err），`margin-top:.55rem` + `:disabled{opacity:.35}`——解决 4 按钮+下拉+状态全挤一行的视觉拥挤（实测按钮文字带换行符=flex 挤压）
  4. **素材弹层工具栏双行**：`.asset-toolbar` 改 `flex-direction:column`，拆 `.asset-ops`（全选/ZIP/重命名/批量Eagle）+ `.asset-status`（eagle-badge margin-left:auto + 格式提示）——解决 6 元素 wrap 乱
  5. **音色表单 grid 布局**：`.vf-row` 挤压行 → `.vf-field{display:grid;grid-template-columns:84px 1fr}`（label 右对齐+控件），窄屏 520px 单列；音频类型 `vTypeChange()` 切 `vValueRow`(none)/`vFileRow`(grid) 显隐——解决「名称+类型+值挤一行」+ 冗余输入框
  6. **参数面板参考区合并**：「参考音频 ×3」+「参考图片（与音频互斥）」两 pgroup 合并为「参考素材」一组 + `.ref-hint` 互斥提示——7 组→6 组
**v5.6 视觉体系重构（2026-08-13，commit 456952d，用户「所有页面依然是很丑」）：**
- **元教训（第三次「丑」类反馈，比 v4.3 更进一步）**：用户两次「很丑」——v5.5 局部组件重构（操作补齐/布局重排）后仍说「所有页面依然是很丑」= **局部调整无效，必须设计令牌级重构**。完整方法论见 `design-system-refactor` skill（触发/诊断/根因/重构顺序/验证）
- **致命 bug 先修**：`:root` 里 `--err-border:var(--err-border)` **自引用循环**（之前把 rgba 收敛为语义变量时手滑）→ 浏览器视为无效值 → 错误/成功/强调色边框全部悄悄失效。排查：grep 定义行 `var(--xxx)` 出现在 `--xxx:` 右侧
- **重构四步（一次全改全局生效）**：①设计令牌——圆角 `10/6/16 → 8/6/12`（Linear 式小圆角）、对比度 `muted .62→.68 / faint .34→.42`、间距令牌 `--sp-1..5`（4/8/12/16/24px）、状态色修正 ②组件体系——**两档按钮制**：`.btn`/`.h-btn` 同系（surface2 底+边框+`var(--r-sm)` 6px+500 字重+hover 提亮 surface3）、`.btn.primary` 白底黑字唯一重色、`.btn.err` 红系；`.gen` 主按钮 999px→8px ③图标——侧边栏 SVG stroke-width 2→1.5 统一线条 ④胶囊清扫——`grep border-radius:999px`：按钮/搜索框/下拉/播放条/批量条/折叠按钮全改 6-8px，**保留合理胶囊**（进度条/状态标签 badge/toast/滚动条/滑块轨道）
- **验证**：真实截图（capture_screenshot）+ vision_analyze 前后对比（重构前「按钮样式混乱/间距无规律/图标混杂」→ 重构后「明显更专业，接近 Linear/Notion」）；用户有 Hermes 桌面预览面板（open_preview）可边改边看
- **高频丑点清单（同类工具排查直接查这几处）**：卡片头操作+下拉+状态挤一行、工具栏多元素 wrap 乱、表单首行多输入挤压、同数据多面板操作集不一致、操作按钮 hover 才显示、:root 变量自引用、胶囊按钮 999px 滥用、muted/faint 对比度不足、**信息参数纵向摞成单列长列表（默认改网格卡片，见 v5.7）**

**v5.7 详情面板 + AI 助手面板细节修复（2026-08-13，commit 3010ab4 + dfa9caa + cd16be5）：**
- **「参数还是很丑，全是纵向摞起来的」→ 信息网格化铁律**：详情面板 10 个参数纵向 10 行 → `.detail-params{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:8px}` + `h4{grid-column:1/-1}` 占整行——**任何「标签+值」列表信息（参数/属性/元数据）默认用网格卡片排布，禁止单列纵向摞**（用户两次因纵向列表说丑）。实测 10 参数 3 列 4 行，vision「简洁专业、层次清晰」
- **LOGID 类超长标识符**：`word-break:break-all` 强制换行三行 → `overflow:hidden;text-overflow:ellipsis;white-space:nowrap` + `title` 属性悬停完整显示；grid 项加 `min-width:0` 防溢出
- **空值/零值区分**：未设置字段显 `—`（`(v===''||v==null)?'—':String(v)`），真实 0 显 `0`——不能混淆「默认」与「未设置」
- ⚠️ **JS 通用坑：`esc()` 的 `s||''` 吞数字 0**（0 是 falsy → 变空串）——渲染数值字段必须 `String(v)` 后再进 esc，排查「值为 0 的字段显示空白」先查 esc/`||''` 链
- **AI 助手面板同理规整**：头部 4 元素挤一行（图标+标题+长副标题+关闭，副标题截断）→ 只留 图标+标题+关闭（黄金三角）；能力文字降级到**状态行**（`.ai-status` 升级为独立信息条：surface2 底+下边框+绿点+绿色「已连接 Hermes」+右对齐能力小字「润色·音色·生成·素材」）；输入框圆角 10px→var(--r)。**「同理 X 页面」= 同一设计语言推广到所有同类面板，头部/状态行/输入区三件套结构统一**
- 验证：`browser_exec` 事件序列模拟（`dispatchEvent(mousedown/mouseup)` 同坐标）打开 orb 面板 → capture_screenshot → vision_analyze 确认「设计成熟、完全不存在丑或乱」

**v5.8 AI 面板分栏重做（2026-08-13，commit cd52a1a，用户「滚动条有问题，分栏设计也很蠢，参考Runninghub的」）：**
- **聊天/助手类面板纵向堆叠（头部/状态/消息/输入一摞）= 用户否定的「蠢分栏」**——参考 RunningHub「主区+右侧栏」思路改**左右分栏**：面板 400→540px，`.ai-main`（头部/状态/消息/输入，flex:1）+ `.ai-side` 138px 快捷栏（border-left 分隔 + surface2 底）——**任何功能面板默认主区+侧栏，禁止全纵向堆叠**
- **右侧快捷栏内容**：①「快捷能力」5 个 chips（润色旁白/音色建议/生成策略/素材操作/导出备份）——`aiChip(k)` 查 `AI_CHIPS` 预设提问 map 填入输入框直接 sendAiMsg（**预设提问 chip 是助手类面板的高频可用模式**）②分隔线 ③「工作台上下文」实时摘要（项目名/块数·已生成/音色数/素材数，`updateAiCtx()` 在 toggleAssistant 打开时刷新）——侧栏数据要随打开刷新，不能静态
- **滚动条修复**：`.ai-msgs` 覆盖全局 10px 滚动条 → **6px 细条 + thumb 更亮（rgba .18→hover .3）**（窄面板里 10px 全局滚动条突兀）；`.ai-side` 5px——**浮窗/窄面板内部滚动容器必须单独定义细滚动条，别吃全局宽度**
- 定位联动：面板变宽后 `positionPanel()` 用 offsetWidth 自动适应（540px 在窄视口 clamp/锚点翻转逻辑不变）
- 验证：DOM 实测 main 402px+side 138px 无缝衔接（`getBoundingClientRect` mainRight===sideLeft）、chips 数、上下文文本；vision「分栏清晰、功能区协调、滚动条自然、无缺陷」

**v5.9 AI 面板收尾（2026-08-13，commit fb96170 + c0a76fd）：**
- **「分栏左下角完全没用」根因（布局树实测，猜不到必须查）**：`.ai-input textarea{flex:1}` + flex 容器默认 `align-items:stretch` → **textarea 被拉伸到 260px**（布局树：`.ai-input` h=285、textarea h=260、`ai-input-hint` 被挤出面板外裁掉 y=556>494）——「左下角大片空白」其实是输入框被拉超高。修复：textarea 显式 `height:44px;min-height:44px;max-height:100px`（多行输入仍可撑开）+ `.ai-input{align-items:flex-end}`（按钮贴底、textarea 不被拉伸）；消息区 `min-height` 140→56px 内容自适应。**通用排查法：布局异常（元素莫名超高/内容被裁）直接 `getBoundingClientRect` 打印布局树各元素 y/h，一眼定位是谁撑爆——别靠猜**；flex 子项显式设 height/min-height 是防 stretch 的标准手段
- **AI 面板视觉打磨（vision「档次感非常明显提升——从功能聊天框变成专业工具交互组件」）**：
  - **气泡系统**：助手 4/14 圆角（左上尖）+ 边框 + 微阴影，用户白底右对齐（14/14/4/14）；每条带时间戳 `.ai-msg-time`；`**加粗**` markdown（**先 esc 再 replace 正则，防 XSS**——注入内容被转义）
  - **头部**：图标升级 30px 蓝色渐变圆角徽章（`linear-gradient(135deg,rgba(99,133,255,.28),.08)` + accent-border）+「在线」绿徽章（ok-border+ok-bg 胶囊）
  - **文案去技术黑话**：「已连接 Hermes」→「服务正常 · 随叫随到」（用户对内部技术名黑话零容忍）；欢迎语重写为无黑话完整句子+能力列表（· 分点）；placeholder 精简「说需求，比如：润色这段旁白…」；上下文「项目：/片段 N · 完成 N /音色 N 个/素材 N 条」——**内部工具 UI 文案面向普通用户，禁用服务名/内部术语**
  - **快捷栏 chips 加图标**：✎♪⚙▤⬇（emoji 前缀做功能识别，提升点击意图）
  - 状态行/输入区/气泡三件套与主界面设计语言统一（圆角 var(--r)、surface 色系、白底主按钮）
- **验证闭环**：`browser_exec` dispatchEvent(mousedown/mouseup 同坐标) 打开面板 → capture_screenshot → vision_analyze 前后对比；DOM 实测（`getComputedStyle`/`getBoundingClientRect`）仍为判断依据，vision 只做观感确认

**v5.10 AI 面板「破而后立」（2026-08-13，commit e615913，用户「必须破而后立」）：**
- **元教训（第四次「丑」反馈后的终极信号）**：v5.8 分栏+v5.9 打磨后用户仍说「我对助手现在的前端很不满意」+「必须破而后立」——**连续多轮增量修补全被打回 = 用户要求整体推倒重写**，此时停止一切补丁，从零重设计（新 HTML 骨架 + 全新 CSS 块 + 升级 JS 渲染），一次性交付。破而后立的标志：用户用「破而后立」「推倒」「重做」「不满意」这类否定当前结构的词，而不是具体指出某处\n- **重写后结构（560px 纵向五段，与 v5.8 分栏的差异）**：`.ai-head` 紧凑单行（渐变图标 28px + 标题 + 「在线」徽章 + **清空对话按钮** + 关闭）→ `.ai-ctxbar` **项目上下文 pill 条上移**（项目名 + 片段/完成/音色/素材 四个 pill，从右侧栏底部移到头部正下——上下文是助手会话的「眼睛」，必须打开即见）→ `.ai-body` 分栏（左 `.ai-msgs` flex + 右 `.ai-side` 快捷能力 140px）→ 输入区 → 提示行。上下文条与快捷栏分离：**数据性信息放顶部条（pill 紧凑横排），功能性操作放右侧栏（chips 竖排）**\n- **轻量 markdown 渲染器 `renderMd()`**（消息从纯文本升级为结构化渲染）：先 `esc()` 全量转义 → 依次处理 ```代码块``` → `行内代码` → `**加粗**`/`__加粗__` → `*斜体*`/`_斜体_`（正则带前后置断言防误伤）→ `-·• ` 列表行转 `<ul><li>` → `---` 分隔线 → 换行 `<br>`。**安全顺序：先 esc 再替换标记**（注入的 `<script>` 已被转义成实体）；用户消息只 esc 不渲染（renderMd 仅 assistant）。CSS：`pre` 深底代码块、`code` 行内浅底、`li` 缩进、`hr` 分隔\n- **「参考 X 产品」的正确姿势（用户「先总结一下RunningHub」的教训）**：用户连续两轮说「参考 RunningHub」时，我凭记忆猜 RH 是「主区+侧栏」分栏并照做了——用户最后要求「先总结一下 RunningHub」= **参考必须基于真实调研，不凭记忆猜**。做法：browser_exec 打开目标产品官网/项目页/画布页 → capture_screenshot 多页 → vision_analyze 逐页拆解（布局/导航/组件/配色/可借鉴点）→ 输出设计语言总结给用户确认 → 再动手。登录墙内界面（如 RH 画布）看不到时，明确告知只能总结可见页面 + 记忆中的结构，不编造\n- **RunningHub 设计语言实测总结（首页 + RHTV 项目页）**：①配色——近纯黑底 + **荧光绿单一高饱和强调色**（主按钮/高亮/标签），亮黄/亮粉仅营销元素；②组件——**卡片无边框**靠圆角（12-16px）+阴影分层（vs 我方全带边框）、按钮两档（实色主操作+白底次操作）、视觉优先（卡片先放素材图）；③布局——顶栏导航（品牌-导航-操作）+ 全宽主区、主区**非对称栅格**（1大+2小）避免单调、画布界面左侧功能栏+中间画布+右侧参数。⚠️ **用户对主操作按钮色有既定偏好（白底唯一重色）与 RH 荧光绿冲突——涉及主色变更必须让用户拍板，不擅自换**

**登录态浏览器控制：Chrome DevTools MCP 替代 WebBridge（2026-08-13，用户「WebBridge总是掉，有没有其他替代」→ 找 GitHub/Hermes 社区）**：
- **结论**：`ChromeDevTools/chrome-devtools-mcp`（npm 包 `chrome-devtools-mcp`，49K⭐ Google Chrome DevTools 官方团队维护）是 WebBridge（Kimi 第三方 daemon+扩展，易掉）的稳定替代——**`--autoConnect` 选项直接连用户正在运行的 Chrome 默认 profile**（Chrome ≥144，全部登录态可用，连接时 Chrome 弹权限框用户点 Allow），等价 WebBridge 的继承登录态且官方维护
- **安装接入**：`npm install -g chrome-devtools-mcp` → `hermes mcp add chrome-devtools --command "C:\\Users\\HMSJ\\AppData\\Roaming\\npm\\npx.cmd" --args "chrome-devtools-mcp@latest --autoConnect"`——⚠️ **Hermes 服务进程 PATH 不含 npm 全局目录**，`--command npx` 报 [WinError 2]，必须用 npx.cmd 完整路径；连接失败时交互问「Save config anyway?」用 `echo y |` 管道应答，配置以 disabled 保存待启用
- **一次性启用（用户操作）**：Chrome 地址栏 `chrome://inspect/#remote-debugging` 开启远程调试 → `hermes mcp test chrome-devtools` → 弹权限框点 Allow。之后 agent 可控制用户真实浏览器（含 RH 等登录态网站）
- 其他候选：`microsoft/playwright-mcp`（36K⭐）——persistent context 需指定 userDataDir（独立 profile 需二次登录），不如 autoConnect 直接


