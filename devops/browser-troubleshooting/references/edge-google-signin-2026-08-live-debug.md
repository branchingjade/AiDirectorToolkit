# Edge Google 登录「点了没反应」现场调试实录（2026-08 第二波）

背景：上一轮（本目录 edge-google-signin-2026-08.md）从配置文件层面排查，结论倾向 cookie/凭据损坏。本轮用户截图 + 要求「直接用我的浏览器调试」，用 Kimi WebBridge 在真实 Edge 里复现，**推翻了 cookie 结论，锁定新方向**。

## 复现

- WebBridge `find_tab(active:true)` 借用户当前标签（url 必填）→ `snapshot` 看到账号链接 → `click` → URL 纹丝不动 → 「点了没反应」稳定复现

## 关键诊断（按证据强度排序）

1. **`document.body.innerText` 首行「正在加载」** → 页面卡在骨架屏，核心 JS 从未执行
2. **performance entries 资源级判读**：gstatic 核心 JS `transferSize=0, encoded=0, proto=""`（连接从未建立）；同页 lh3 头像 `proto=h3, transfer=98272`（正常连接）→ **按域名分组掐连接**的特征
3. **WebBridge network list**：页面主文档 200 ✓；gstatic JS/图标/字体 + google.com favicon 全部 `completed:false`、状态 `?` ✗（多次刷新稳定复现；fonts 曾一次 200 = 间歇性）
4. **对照组**：干净 CDP Chrome（9222 headless）打开同一 URL → 正常跳转 signin/identifier（JS 执行成功）→ 同一网络下 Chrome 好 Edge 坏，问题锁定 Edge 本身

## 排除项（各有实证）

- **网络/代理**：curl 直连 + 代理 200 秒通；Edge 第一方导航到 gstatic JS 地址 → 1MB 源码正常下载
- **服务器 CORS**：curl 带 `Origin: https://accounts.google.com` → `Access-Control-Allow-Origin` 正确返回
- **CSP**：同源 fetch 读主文档响应头 → 显式允许 `https://www.gstatic.com`（script-src 白名单内有）
- **扩展规则文件**：5 个启用扩展（FDM/ABP/Video Download Helper/猫抓/Augmented Steam）grep 规则 JSON → 无任何 gstatic/google 拦截规则 → **用户说「跟 ABP 没关系」是对的**

## 头号嫌疑（未最终定论，诚实标注）

Edge 特有设置（Chrome 全无）三件套：
- `enhanced_tracking_prevention.enabled=true`
- `enable_do_not_track=True`
- `browser.clear_data.cookies=True`（退出清 cookie）

验证法：`edge://settings/privacy` 跟踪防护 平衡→基本 → 刷新再点。恢复=实锤。下一步若无效：临时禁用拦截类扩展做二分实验。

## 工具坑（本轮实测）

- **页面内跨域 fetch 全失败（含百度/GitHub）= CSP connect-src 污染**，不能用来测网络；no-cors 也一样。测网络只用 curl 或第一方导航
- **Google 登录页 `require-trusted-types-for 'script'`** → 动态注入 script（`s.src=` 和 `setAttribute` 都抛 TrustedScriptURL 异常）
- 「动态 script 成功」的对照实验**必须在同一页面上下文做才有效**——本轮曾在 gstatic 第一方页测成功（同源），设计缺陷，作废
- WebBridge `network detail` 需要 requestId 且会失效（No data found）；`cdp` 通道不支持事件订阅，拿不到 loadingFailed errorText
- **「能显示账号」≠「页面活着」**：账号列表是 SSR 预渲染 HTML，JS 停了照样显示——点击块没反应正是 JS 未执行的症状，不是按钮坏了
