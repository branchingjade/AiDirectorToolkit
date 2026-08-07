# WebBridge 现场调试实录（2026-08，Edge 第三方 Google 登录无反应）

会话背景：Edge 里第三方网站（Tailscale）点"Sign in with Google"没反应，Chrome 正常。用户要求"用我的浏览器调试"，agent 第一轮用独立 browser_navigate 查网页被骂（"你是傻逼吗，我让你用我的浏览器调试"）。

## 已确认的技术事实（本轮实测）

### WebBridge 连的浏览器身份确认
- daemon `/status` 的 `extension_id` **无法区分 Chrome/Edge**——同一个扩展包（Kimi WebBridge）在两边安装 ID 相同（本机实测 `bnlffdbcfnanfbknnlaflhlhkocccckg`）
- 确认方法：`evaluate navigator.userAgent`——含 `Edg/` = Edge；`Chrome/151.0.0.0` 且无 Edg = Chrome
- 本机实测：WebBridge 连的是 Chrome，不是 Edge。在 Chrome 里测 Edge 的问题是无效的

### 后台 tab 假象（调试点击类问题的头号陷阱）
- WebBridge 打开的所有 tab 都是 `active:false`（后台态，list_tabs 可见）
- CDP `Input.dispatchMouseEvent`（mousePressed+mouseReleased，isTrusted=true）在后台 tab **不生效**：点完无 JS 错误、无网络请求、location 不变
- 同样，WebBridge `click`（synthetic el.click()，isTrusted=false）在 Google 类页面也无反应
- 判别方法：`list_tabs` 看 active 状态；点击前后 evaluate `location.href` + `performance.getEntriesByType('resource')` 尾部对比

### WebBridge 能力边界（实测报错原文）
- `navigate` chrome:// 或 edge:// URL → `{"error":{"code":"extension_error","message":"Cannot access chrome:// and edge:// URLs"}}`
- `cdp` 浏览器级命令（Target.getTargets）→ `{"error":{"code":"extension_error","message":"{\"code\":-32000,\"message\":\"Not allowed\"}"}}`——只允许当前 debuggee tab 的页级命令
- daemon 一次只服务一个扩展连接（/status `extension_connected` 单数），无切换浏览器接口（根路径 404）

### 切换 WebBridge 目标浏览器（唯一路径）
agent 无法自己禁用/启用扩展（chrome:// 进不去）→ 用户手动：
1. 旧浏览器 `chrome://extensions` 禁用 Kimi WebBridge
2. 新浏览器 `edge://extensions` 确认启用
3. 新浏览器打开任意网页重连 daemon
4. agent 用 `evaluate navigator.userAgent` 验证已切换

替代方案（全自动）：目标浏览器带 `--remote-debugging-port=9222` 重启（保留真实 profile），CDP 直连。

## 可复用的调试手法

### 点击后"发生了什么"的三层证据
```js
// 1) 注入错误捕获器（在触发操作前）
(() => {
  window.__errs = [];
  window.addEventListener('error', e => __errs.push('error: ' + e.message + ' @' + (e.filename||'').split('/').pop() + ':' + e.lineno));
  window.addEventListener('unhandledrejection', e => __errs.push('rejection: ' + String(e.reason).slice(0,200)));
  return 'captor installed';
})()
// 2) 触发点击后读状态
(() => {
  const recent = performance.getEntriesByType('resource').slice(-8).map(e => e.name.split('?')[0].slice(0,120));
  return JSON.stringify({href: location.href.slice(0,80), readyState: document.readyState, errors: window.__errs || [], recentResources: recent});
})()
```
判读：href 没变 + readyState complete + errors 空 + recentResources 无新增 → 点击事件根本没驱动任何东西 → 先怀疑后台 tab / isTrusted，再怀疑页面逻辑。

### 精确坐标获取（CDP 真实输入用）
页面容器误匹配（getBoundingClientRect 返回全屏尺寸）→ 用最小文本容器或 data 属性：
```js
(() => {
  const el = document.querySelector('[data-email="xxx@gmail.com"]') 
         || [...document.querySelectorAll('a')].find(a => a.textContent.includes('xxx@gmail.com'));
  const r = el.getBoundingClientRect();
  return JSON.stringify({x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2), w: r.width, h: r.height});
})()
```
CDP 点击 = mousePressed + mouseReleased 两个事件（x/y/button:left/clickCount:1）。

## 陷阱
- 用户给的 OAuth URL（accountchooser 带 state/dsh 参数）可能已过期/被消费——复现要走源头：navigate 第三方登录页 → 点"Sign in with Google" → 让 Google 生成新鲜流程
- 两个 tab 都非前台时（active:false），页面 JS 可能因 visibility 不响应——navigate 新 tab 不会自动激活窗口
- 本会话**未定位根因**（切换 WebBridge 到 Edge 的步骤尚未完成），上述全部是工具链事实，不是 Edge 问题结论
