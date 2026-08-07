---
name: browser-troubleshooting
description: 浏览器问题排查——登录失败/点击没反应/一个浏览器好另一个坏。触发词：浏览器登录、Edge坏Chrome好。
---

# 浏览器问题排查（Windows）

## 适用场景
- 浏览器里登录（Google/微软/任意 OAuth）点了没反应、报错、反复跳回
- 同一网站浏览器 A 正常、浏览器 B 异常（Edge vs Chrome 最常见）
- 扩展干扰、站点数据损坏、设置损坏类问题

## 核心方法：差异分层法
"浏览器 A 好、浏览器 B 坏" → 网络和网站本身基本排除 → 问题在 B 独有或 B 与 A 不同的层。逐层排查，**每层都要本地证据，不猜**。

对 Chromium 系（Edge/Chrome），按层排除：
1. **网络层**：curl 实测目标域名（直连 + 显式代理各一次）——通就排除
2. **扩展层**：对比两浏览器扩展清单，差异=嫌疑。**优先排查带拦截权限的扩展**：广告拦截器（Adblock Plus/uBlock/AdGuard，权限含 webRequest/declarativeNetRequestWithHostAccess/<all_urls>）能静默掐断 OAuth 跳转链，表现正是"点了没反应"；注入型（视频下载/音乐/助手类）其次。**判别铁证：无痕窗口正常=扩展/缓存问题**（InPrivate 默认禁用扩展）
3. **设置层**：Edge 特有 tracking prevention（Strict 会拦 OAuth 跨站跳转）、弹窗拦截
4. **系统集成层**（Edge 特有，Chrome 不依赖）：TokenBroker/WAM 服务状态
5. **策略层**：组策略 BrowserSignin（0=禁用登录）
6. **数据层**：cookie/凭据损坏、设置/配置文件损坏——**最常见根因，微软官方文档第一优先**

"点击没反应"= OAuth cookie 跳转链断裂的典型表现（静默失败），不是按钮坏了。

> ⚠️ **2026-08 第二波修正**：点击没反应还有第二种机制——**页面停在骨架屏、核心 JS 从未执行**（`body.innerText` 首行「正在加载」；账号列表是 SSR 预渲染 HTML，"能显示账号"≠"页面活着"；performance 里核心 JS `transferSize=0, proto=""`）。此时排查方向不是 cookie，是**跨站资源被策略掐断**（见下「真浏览器现场调试」）。两种机制先区分再排查。

## 先拿本地证据（bash）
```bash
# 网络：直连 + 显式代理各测（302 即通）
curl -s -o /dev/null -w "%{http_code}\n" --max-time 10 https://accounts.google.com
curl -s -o /dev/null -w "%{http_code}\n" -x http://127.0.0.1:7897 https://accounts.google.com

# Edge TokenBroker 服务（Edge 登录依赖，Chrome 不用；STATE 4=RUNNING 正常）
sc query TokenBroker

# 组策略登录限制（无输出=默认允许）
reg query "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v BrowserSignin || echo "无限制"

# Edge 版本（Application/ 下数字目录=版本号）
ls "/c/Program Files (x86)/Microsoft/Edge/Application/" | grep -E '^[0-9]+\.'

# 扩展清单 ⚠️ 不要用 grep manifest.json 的 name——i18n 扩展的 name 是 __MSG_name__ 占位符，
# 广告拦截器（Adblock Plus 实测）会因此被漏掉，得出"无广告拦截"的错误排除结论（2026-08 翻车案例）。
# 用脚本审计（磁盘目录为准 + 解析 _locales 真实名 + disable_reasons 判断启用 + 标记拦截权限）：
python "$HOME/AppData/Local/hermes/skills/devops/browser-troubleshooting/scripts/chromium-extensions.py" all
# 快速判断：输出里带「★广告拦截器」或「拦截权限」的扩展 = 能静默掐断 OAuth 跳转链的头号嫌疑

# Edge 设置（Preferences JSON）：tracking_prevention 0=基本/1=平衡/2=严格，grep 不到=默认平衡
grep -o '"tracking_prevention":[^,}]*' "$HOME/AppData/Local/Microsoft/Edge/User Data/Default/Preferences"
grep -o '"popups":{[^}]*}' "$HOME/AppData/Local/Microsoft/Edge/User Data/Default/Preferences"
```

## 判别分水岭：无痕窗口
InPrivate（Ctrl+Shift+N）里复现操作：**无痕正常=扩展/缓存问题；无痕也坏=设置/系统层**。一句话分流，先做这个。

## 真浏览器现场调试（用户在场时最高优先级证据）
配置文件考古（上面 bash 段）是间接证据。**用户能配合时直接驱动他的真实浏览器复现**——用 Kimi WebBridge 层3（browser-control skill）借用户当前标签页操作：

> ⚠️ **2026-08 第三波实测：WebBridge 现场调试的三个前置**（不确认就调 = 结论可能是假的）：
> 1. **先确认 WebBridge 连的是哪个浏览器**：`/status` 的 extension_id **无法区分 Chrome/Edge**（同一扩展包在两边 ID 相同）。必须 `evaluate navigator.userAgent`——含 `Edg/` = Edge，纯 `Chrome/` = Chrome。实测 WebBridge 连的是 Chrome（UA `Chrome/151`），差点把 Chrome 里的测试结果当成 Edge 的结论
> 2. **后台 tab 假象**：WebBridge 打开的 tab 全是 `active:false`（后台态），CDP `Input.dispatchMouseEvent` 真实输入（isTrusted=true）在后台 tab **不生效**——点任何东西都"没反应"（无 JS 错误、无网络请求、location 不变）。这是假象不是真问题。判别：先查 `list_tabs` 看 active 状态
> 3. **synthetic click 假象**：WebBridge `click`（el.click()，isTrusted=false）在 Google 类严格页面可能无反应——skill 已知限制，别把它当结论

> **切换 WebBridge 到另一个浏览器**（daemon 一次只服务一个扩展连接）：agent **无法自己禁用/启用扩展**（WebBridge 不能 `navigate` chrome:// 或 edge:// 页面，`cdp` 浏览器级命令如 Target.getTargets 被拒 Not allowed）→ 必须用户手动：① 旧浏览器 `chrome://extensions` 禁用 Kimi WebBridge ② 新浏览器 `edge://extensions` 确认启用 ③ 新浏览器打开任意网页重连 daemon。切换后用 UA 验证。替代方案：**CDP 直连目标浏览器**（真实 profile，端口 9223+——**别用 9222，那是 agent Chrome 的**；完整流程 + 全部坑见 cdp-browser-debugging skill，含"真实 profile 拒绝开端口 → 复制登录数据到临时 profile 的 A/B 诊断法"）

1. `find_tab`（`active:true` + url 必填）借用用户正开着的出问题标签
2. `snapshot` 找元素 → `click` 复现「点了没反应」
3. `evaluate` 读诊断铁证：`document.body.innerText`（首行「正在加载」=JS 未执行）、`performance.getEntriesByType('resource')`（看 `transferSize`/`proto`）
4. `network start` + `list` 看请求完成状态（`completed:false` + 状态 `?` = 请求未完成）

**资源级判读**（本轮实测规律）：
- 失败资源 `transferSize=0, proto=""`（连接从未建立）vs 同页成功资源 `proto=h3`（正常连接）→ **按域名分组掐连接**，指向浏览器策略拦截（Edge 增强跟踪防护），不是网络
- 页面主文档 200 但 gstatic/google 域静态资源全挂 → 跨站嵌入资源被策略拦
- **对照组**：同一 URL 用干净 CDP Chrome（9222 headless）打开，正常=问题锁定 Edge 特有层
- 验证设置差异：对比 Edge/Chrome 的 `Preferences` JSON（`enhanced_tracking_prevention`/`enable_do_not_track`/`browser.clear_data.cookies`——Edge 有 Chrome 无=嫌疑）

完整实录见 `references/edge-google-signin-2026-08-live-debug.md`。WebBridge 工具链边界（UA 身份确认/后台 tab 假象/cdp 限制/浏览器切换流程）见 `references/webbridge-live-debug-2026-08.md`。

## 修复阶梯（成本从低到高，每步后重试）
1. **只清目标站点 cookie**：`edge://settings/siteData` → 搜域名 → 删除（不动其他网站登录态）
2. **重置浏览器设置**：`edge://settings/reset` → "将设置恢复为默认值"（书签/密码/历史不动）——社区实证"重置后立刻修好"
3. **新建配置文件**：`edge://settings/profiles` → 添加个人资料 → 新配置登录测试（能成=旧配置损坏弃用）

## 坑
- **用户说"与插件无关"不能直接跳过扩展层**（2026-08 翻车案例）：上一轮用户排除扩展，agent 跳过扩展层直奔 cookie 损坏结论；实际上 Edge 装了 Adblock Plus 且启用，manifest name 是 `__MSG_name__` 占位符，grep 清单漏了它——广告拦截器一直在掐 Google OAuth 请求。用户排除只能信一半：**必须用脚本（chromium-extensions.py）复核扩展清单 + 权限 + 启用状态**，确认无拦截权限扩展后才能排除。截图里浏览器地址栏/工具栏出现广告拦截图标（红盾/红圈白手），或页面资源加载异常（如图标显示为占位符）＝拦截正在发生的现场证据
- 搜索引擎反爬（2026-08 实测）：Bing 直接空页（bot 检测）、DuckDuckGo HTML 可抓但很快限流、Reddit API 拒无 key 请求。抓资料优先 curl 官方文档站（learn.microsoft.com 等对 curl 友好），搜索引擎只用来找 URL。DDG 提取技巧见 references/edge-google-signin-2026-08.md
- **页面内 fetch 实验会被 CSP 污染**（2026-08 实测）：Google 登录页 CSP connect-src 极严，页面内跨域 fetch（连百度/GitHub 都失败）——fetch 失败**不能**证明网络不通，它只证明 CSP 放行与否。测网络用 curl（直连+代理）或第一方导航，别用页面内 fetch
- **动态注入 script 受 TrustedScriptURL 限制**：Google 登录页 `require-trusted-types-for 'script'`，`s.src=` 和 `setAttribute` 都会抛错。动态加载对照实验要在真实页面上下文设计，注意 CSP 干扰
- **"跟 ABP 没关系"双向教训**：用户说无关时不能直接跳过扩展层（见上），但**也不能当用户错了**——本轮实测 5 个启用扩展的规则文件里确实无 gstatic 规则，用户是对的。判定标准永远是本地证据（grep 规则文件/无痕窗口），不是用户立场
- **用户说"用我的浏览器调试"= 用 WebBridge 驱动他的真实浏览器，不是 agent 自己的浏览器栈**（2026-08 用户原话"你是傻逼吗，我让你用我的浏览器调试"——agent 先用独立 browser_navigate 查网页被骂）。查资料可以用独立浏览器，但**复现/调试浏览器故障必须进用户真实浏览器**。WebBridge 不能访问 chrome:// 和 edge:// URL、cdp 只允许页级命令（浏览器级命令 Not allowed）、打开的 tab 全后台态——这些限制先知道，别在调试中途撞墙
- **问题没定位前不要把 WebBridge 的中间观察当结论**（2026-08 实测）：后台 tab 假象 + synthetic click 假象叠加时，"点击没反应、无错误、无请求"三个证据全齐也可能是假的——先排除 tab 前台性（list_tabs 看 active）和输入真实性（isTrusted）再下判断

## 来源
- 微软官方 Edge 登录排障：https://learn.microsoft.com/en-us/troubleshoot/microsoft-edge/security/troubleshoot-sign-in-issues
- 微软 Q&A 同款问题（Edge 登不了 Google、Chrome 能）：https://learn.microsoft.com/en-us/answers/questions/5575434/
- 实战案例：references/edge-google-signin-2026-08.md
