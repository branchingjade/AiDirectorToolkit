# 实战案例：Edge 里 Google 登录点了没反应，Chrome 正常（2026-08）

## 用户环境
- Windows 10 + Clash Verge TUN 代理（系统流量自动走代理）
- Edge 151.0.4129.59 + Chrome 并存，都装了多个扩展

## 症状
- Edge 里 Google 登录"点了没反应"（无跳转、无报错）；Chrome 完全正常
- 用户排除扩展嫌疑（"与插件无关"）——按铁律跳过扩展层直接往下游排查

## 实测证据（全部本机取证）
| 检查项 | 结果 | 结论 |
|---|---|---|
| google 直连 curl | 302 秒通 | 网络/代理排除 |
| 显式代理 7897 curl | 302 | 同上 |
| Edge 扩展清单 | 14 个；Edge 独有：Video Download Helper / Listen 1 / bilibili 下载助手 / 图流 / 网盘重命名 / 云音乐 | 注入型扩展多，但用户已排除 |
| Chrome 扩展清单 | 仅 Augmented Steam / Just Black / ShareX / Kimi WebBridge | 对比基准 |
| tracking_prevention | 未显式设置=默认平衡 | 排除 |
| popups 例外 | `"popups":{}` 无例外 | 排除 |
| TokenBroker 服务 | RUNNING | 排除（Edge 特有 WAM 依赖） |
| 组策略 BrowserSignin | 无 | 排除 |
| Edge 版本 | 151.0.4129.59 | 不旧 |

## 结论
网络/策略/系统集成全排除 → 最大嫌疑（微软官方文档第一优先级 + 微软 Q&A 社区实证）：
1. Google 的 OAuth cookie/凭据损坏（点击后跳转链静默断裂 = "没反应"）
2. Edge 设置/配置文件损坏（Q&A 中"重置设置立刻修好"）

修复阶梯：只清 google.com 站点数据 → 重置 Edge 设置 → 新建配置文件。**用户尚未回传哪个生效**——修复有效性未在本案例验证，阶梯有效性来自微软官方文档与社区实证，非本机确认。

## ⚠️ 结论被推翻（同日晚间第二现场）
用户再次报"点了没反应"，截图显示地址栏有 ABP 红色图标 → 重新取证发现：
- **Edge 装了 Adblock Plus 4.43.0 且启用**（Secure Preferences `disable_reasons=[]` = 启用），权限含 `webRequest` + `declarativeNetRequestWithHostAccess` + `<all_urls>`，完全能静默拦截 Google OAuth 请求
- 上一轮"Edge 无广告拦截类扩展"是**误判**：grep manifest.json 的 `"name"` 只拿到 `__MSG_name__` 国际化占位符，ABP 的真实名字藏在 `_locales/<locale>/messages.json`——清单漏了它
- 截图里卡片顶部 Google 小图标"加载异常显示为占位"＝有资源被拦的现场证据
- 用户排除扩展的依据是 agent 给的错误清单——"用户说与插件无关"不能当免检牌

**真实根因**：Adblock Plus 拦截了 Google 登录页部分资源，点击账号的跳转/资源请求被静默吞掉。修复：ABP 暂停屏蔽（Pause blocking）→ 刷新重试；长期加白名单 `accounts.google.com`、`*.googleusercontent.com`。
**教训**：扩展清单必须用脚本审计（scripts/chromium-extensions.py，解析 i18n 名 + 拦截权限 + 启用状态），grep name 不可靠；页面资源加载异常（占位图标）= 拦截现场。

## 搜索引擎抓取笔记（本案例踩坑）
- Bing 搜索页被 bot 检测返回空 body（browser_navigate 后 body 为空）——直接弃用
- DuckDuckGo HTML 版（html.duckduckgo.com）可 curl 抓标题，但重复请求很快限流（第二次即空）
- lite.duckduckgo.com 同样限流；Reddit search.json 拒无 key 请求（返回非 JSON）
- learn.microsoft.com 等官方文档站 curl 友好，直接 curl + HTML 标签剥离取正文，无需浏览器

### DDG 结果提取（标题 + 真实 URL）
```bash
Q="Edge+google+sign+in+click+no+response"
# 标题
curl -s --max-time 20 "https://html.duckduckgo.com/html/?q=$Q" -A "Mozilla/5.0" \
  | grep -oP 'class="result__a"[^>]*>[^<]+' | sed 's/.*>//' | head -20
# 真实 URL（结果链接是 /l/?uddg=<urlencode> 跳转）
curl -s --max-time 20 "https://html.duckduckgo.com/html/?q=$Q" -A "Mozilla/5.0" \
  | grep -oP 'href="[^"]*uddg=[^"]*"' | sed 's/href="//;s/"$//;s/&amp;/\&/g' \
  | python -c "import sys,urllib.parse; [print(urllib.parse.unquote(u.split('uddg=')[1])) for u in sys.stdin if 'uddg=' in u]" | sort -u
```
要点：`-A "Mozilla/5.0"` 必须有；URL 需解 uddg 参数 + 反转义 &amp;；限流后等一会儿或用别的源（官方文档站直连）。

## 来源
- 微软官方：https://learn.microsoft.com/en-us/troubleshoot/microsoft-edge/security/troubleshoot-sign-in-issues
  （根因清单：缓存凭据/cookie 损坏、密码/MFA、组策略、网络端点、冲突配置文件、版本旧、WAM/TokenBroker）
- 微软 Q&A 同款问题：https://learn.microsoft.com/en-us/answers/questions/5575434/
  （版主方案：清 cookie→禁扩展→站点权限→重置设置→无痕；用户实证"重置设置立刻修好"）
