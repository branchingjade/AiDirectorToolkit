# 部署后 UI 验证与宽屏适配（doubao-tts v3 实战，2026-08-10）

豆包 TTS v3 部署 + 4K 适配排障全程沉淀。适用于「NAS 服务部署后验证 UI / 用户报布局错乱」。

## 1. 用户报「没有任何变化」= 先查服务端，再查浏览器缓存

**服务端三查**（都过 = 服务端就是新版）：
1. 磁盘源文件：`grep -c '新版特征字符串' /volume1/docker/<项目>/app/page.html`
2. 容器内文件：`docker exec <容器> grep -c '特征' /app/app/page.html`
3. 端口实际响应：`curl -s http://127.0.0.1:8000/ | grep -c '特征'`

**根因通常是浏览器缓存**：FastAPI `HTMLResponse` 不带 `Cache-Control` 时浏览器 F5 命中旧缓存。
修复：`return HTMLResponse(f.read(), headers={"Cache-Control": "no-store"})`，加后普通 F5 即见新版。
诊断注意：uvicorn 对 HEAD 返回 405（`allow: GET`）是正常，验响应头用 `curl -s -D - -o /dev/null`，别用 `curl -sI`。

## 2. 部署后 UI 验证用 Kimi WebBridge（用户真实浏览器）

- `browser_navigate` 云后端**连不上 NAS 内网**（os error 10060）
- headless Chrome `--screenshot` 在超大窗口（3840×2160）下**连续不产图**，不可靠
- 用户原话「你可以用我的浏览器直接看啊」——WebBridge 是唯一可靠验证

流程：
```bash
# navigate 开 tab（group_title 写用户语言）
{"action":"navigate","args":{"url":"http://192.168.1.2:8000/","newTab":true,"group_title":"豆包TTS适配排查"},"session":"<任务名>"}
# screenshot 落盘后 vision_analyze 看
{"action":"screenshot","args":{"format":"png","path":"C:/.../ui_real.png"},"session":"<任务名>"}
# evaluate 查 computed style 定位布局根因（一锤定音）
{"action":"evaluate","args":{"code":"(() => { const cs=getComputedStyle(document.body); return JSON.stringify({screenWidth:screen.width, dpr:window.devicePixelRatio, physicalPx:screen.width*(window.devicePixelRatio||1), bodyClass:document.body.className, panelW:getComputedStyle(document.querySelector('.panel')).width, gridCols:getComputedStyle(document.querySelector('.grid')).gridTemplateColumns, wrapW:getComputedStyle(document.querySelector('.wrap')).maxWidth, innerWidth:window.innerWidth}); })()"},"session":"<任务名>"}
```

**Windows 铁律**：请求体必须写文件再 `curl.exe --data-binary @file` POST（管道内联会损坏非 ASCII）；每次用唯一文件名；用完即删。

## 3. 4K 判档三因素叠加失准（用户报「布局错乱/双栏比例不对」）

**实测数据**：用户 4K + Windows 150% 缩放 + 浏览器手动缩放 75% → `dpr=1.125`、`screen.width=2560`、`physicalPx=2880`、`innerWidth=3403`。
`detectScreen()` 按 physicalPx 判档只触发 is-3k → wrap 锁固定 `max-width:1480px` → 3403px 视口左右各留 ~960px 大空白；面板 `clamp(...,360px)` 占比仅 13%；scale 1.15×0.75=0.86 字号显小。

**修复三件套**（已在 doubao-tts v3 验证通过，WebBridge 复测 70/30 协调无空白）：
1. wrap 改 `max-width: calc(100vw - 80px)` 自适应视口，**不用固定 max-width**
2. 面板 `--panel-w: minmax(360px, 22vw)`（is-3k）/ `minmax(420px, 24vw)`（is-4k）相对视口加宽
3. `--scale` 提升到 1.3/1.45 **补偿浏览器缩小**（目标 scale×浏览器缩放≈1:1 实际显示）

**两条附坑**：
- CSS 变量定义了必须真被 `calc()` 消费——`--scale:1.35` 定义后无任何 calc 引用 = 白写，4K 下控件不放大
- 改版重写必须保留原有适配逻辑——v3 重写丢了 v2 的 `@media(min-width:2560px){grid 1fr minmax(360px,28vw)}` 面板加宽规则 = 回归 bug

## 4. 主栏防溢出

宽屏下 grid 主栏用 `minmax(0,1fr)` 而非 `1fr`——长内容（超长文本/音频卡）不会撑破 grid 容器导致横向溢出。
