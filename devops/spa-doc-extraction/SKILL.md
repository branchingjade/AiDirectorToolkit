---
name: spa-doc-extraction
description: SPA文档站内容提取——可靠方法与常见陷阱。触发词：SPA文档、文档站抓取、动态渲染页面提取、VuePress/Docusaurus。
category: devops
---

# SPA 文档站内容提取

## 核心方法

```javascript
browser_navigate(url)
browser_console('document.body.innerText')
```

**这是唯一可靠的方法。** innerText 是浏览器原生纯文本，不受 a11y 树嵌套污染。

## 决策原则

1. **不分析，直接执行。** 方法成功过就重复它。简单重复任务不是优化问题。
2. **预检清单。** 动手前花10分钟验证：工具能力边界（能否并发、能否点击、能否认证）、第一个页面的完整流程、约束条件、已验证方法的预期耗时。
3. **决策规则：**
   - 已验证方法可用 → 重复它
   - 已验证方法太慢 → 先问用户能否接受
   - 用户不能接受 → 测新方法（不假设可行）
   - 新方法失败 → 回到已验证方法，不继续试
   - 连续失败3次 → 停下来重新评估任务定义
4. **目标错位检测：** 用户要求"完整性"时不要自行优化成"速度"。先确认用户真实需求。

## 常见 SPA 文档站特征

- VuePress / Docusaurus / ReadTheWorks / MkDocs
- URL 重定向到默认页（如"产品动态"、"首页"）
- 内容通过 JS 动态渲染，`requests.get()` 只能拿到空壳
- 侧边栏导航是 SPA 路由，需要点击才能切换页面

## 提取策略

### 直接 innerText（推荐）
```javascript
document.body.innerText
```
- 返回浏览器渲染后的纯文本
- 包含所有动态加载的内容
- 不受 snapshot 嵌套树污染

### Snapshot 提取（备选）
```
browser_snapshot(full=true)
read_file(返回的 snapshot 路径)
```
- 会生成嵌套的 a11y 树
- 可能重复/交叉/截断内容
- 适合需要元素引用（ref）的交互场景

## 已知陷阱

### 1. 并行 agent 可用但指令必须精确
**事实：** `delegate_task` 子 agent **每个都有独立浏览器实例**，可以真正并发。
**关键：** 子 agent 指令必须明确具体 URL、点击哪个侧边栏、用 innerText 不用 snapshot。不要给"不要点任何东西"的禁令——SPA 页面必须点击导航。

### 2. SPA 重定向
**问题：** 部分 URL 重定向到默认页（如"产品动态"），不是 API 文档页。
**解决：** 点击侧边栏菜单项导航到正确页面。

### 3. requests.get() 空壳
**问题：** SPA 页面 `requests.get()` 只能拿到 500 chars 的空壳 HTML。
**解决：** 必须用浏览器渲染后提取 innerText。

### 4. CORS 拦截
**问题：** 浏览器内 JS `fetch()` 跨域失败。
**解决：** 不要用 `browser_console` 批量 fetch，用 `browser_navigate` 逐页访问。

### 5. snapshot 嵌套污染
**问题：** a11y 树会重复同一行几十次、交叉重叠不同页面内容。
**解决：** 用 `browser_console('document.body.innerText')` 替代 snapshot。

### 6. 中文政府/法规页编码错误（browser_navigate 直接抛异常）
**问题：** 部分中国大陆政府/法规站（GBK 或混合编码响应）会让 `browser_navigate` 报 `'utf-8' codec can't decode byte 0xb2 ...` 而无法导航（2026-08 在 flk.npc.gov.cn、sousuo.www.gov.cn 实测）。
**解决（已验证）：** 用 CDP 绕过浏览器工具的解码层——先 `browser_cdp Target.getTargets` 拿到现有 tab 的 targetId，再 `browser_cdp Page.navigate {url, target_id}`，随后 `browser_cdp Runtime.evaluate {expression: 'document.body.innerText', returnByValue: true, target_id}` 读渲染后正文。

### 7. Vue 站点的 JS 点击不可靠
**问题：** 对 Vue SPA（如 flk.npc.gov.cn 的 `div.result-item` 行）用 JS `element.click()` 不触发其路由跳转；点击还可能把结果页开成新标签页（`window.open` 到 `/search` 路由），误导后续操作。
**解决思路：** 优先用 a11y 快照的 ref + `browser_click` 走真实输入通道；若仍无效，考虑直接构造目标 URL（SPA 深链）而非点击。

### 8. 懒加载页面 innerText 返回空串
**问题：** 部分 SPA（火山引擎文档站实测）正文懒加载，首帧 `document.body.innerText` 返回空串，`browser_console` 读不到内容，容易误判"页面未渲染"。
**解决：** 等待 2-3 秒或重新 `browser_navigate` 后再取；备选 `browser_snapshot(full=true)` 走 a11y 树（结果被截断时完整内容在返回的缓存 txt 路径，用 `read_file` 续读）。

## 工作流示例

```python
# 1. 导航到页面
browser_navigate("https://docs.example.com/api/users")

# 2. 提取纯文本
content = browser_console('document.body.innerText')

# 3. 保存到文件
write_file("page1.txt", content)

# 4. 继续下一页（串行）
browser_navigate("https://docs.example.com/api/orders")
content = browser_console('document.body.innerText')
write_file("page2.txt", content)
```

## 与其他工具的配合

- **Kimi WebBridge：** 需要登录态时使用，每个 agent 独立本地 Chrome
- **browser_snapshot：** 需要元素引用（ref）时使用，如点击按钮、填写表单
- **execute_code：** 后处理提取的文本，如解析 JSON、提取参数表
