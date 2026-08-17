# Dashboard 插件 UI 整改模式（channel-sessions 2026-08-10 实战沉淀）

channel-sessions v1.7 按「前端设计知识库」审视整改 12 项 + 4K 适配 + 排版收紧，以下为可复用模式与用户拍板结论。

## 用户拍板：筛选选项默认全部展开（推翻折叠规范）

- 事件：按知识库「组内 ≤7-9 个，超出用『更多』折叠」（Hick/Miller）给会话人筛选（50+ 选项）做了默认折叠，用户看完直接否掉——「默认全部展开排列」。
- 结论：**本用户工具 UI 的选项/参数一律默认全显**（「参数常显不折叠」铁律 > 规范折叠建议）。筛选区选项再多也平铺，用排序（计数降序）保持紧凑，不做「更多/收起」。
- 教训：给本用户做「折叠/收纳」类设计前先问；被否后直接删除折叠逻辑（revert commit f903b54）。

## 4K 适配 zoom 方案（JS 物理分辨率检测，2026-08-10 落地）

CSS 媒体查询在 4K + Windows 缩放（150%）下失效（CSS 视口 2560 ≥ 断点）。落地方案：

```js
// 模块顶层（插件 IIFE 内）：
const SCREEN = (function () {
  try {
    const dpr = window.devicePixelRatio || 1;
    const cssW = window.innerWidth || 1920;
    return { physW: window.screen.width * dpr, cssW };
  } catch (e) { return { physW: 0, cssW: 1920 }; }
})();
const ZOOM = SCREEN.cssW >= 3000 ? 1.25 : SCREEN.cssW >= 2400 ? 1.1 : 1;   // 4K100%→1.25；4K150%/2K→1.1
const WIDE_DEFAULT = SCREEN.cssW >= 3000 ? { left: 260, mid: 520 } : SCREEN.cssW >= 2400 ? { left: 240, mid: 480 } : { left: 208, mid: 400 };
```

- 根容器 `style={{ zoom: ZOOM }}`（Edge/Chrome 支持；Firefox 不支持——dashboard 场景可接受）。一行放大全部布局+字号，不用改每个 px 类。
- **拖动分隔条 delta 必须除以 zoom**：`onChange(clamp(startW + (e.clientX - startX) / zoom, min, max))`，否则 zoom 下拖动速度失真。
- 动态默认栏宽：宽视口自动放大默认值（260/520），用户拖过的 localStorage 值仍优先。
- 消息流限宽：详情区 `max-w-[1100px] mx-auto`，4K 全屏详情栏 3200px 时不拉成长行；气泡 max-w 85%→75%。
- 拖动存储的是布局 px（未 zoom），重开时 zoom 重新计算一致。

## UI 整改可复用模式（全部验证过）

| 模式 | 做法 | 依据 |
|---|---|---|
| 批量操作 | 选择模式（行首原生 checkbox + 批量条：全选/置顶/归档/删除/退出），前端**串行循环调单条接口**（bulkMutate），失败中断+横幅提示 | Material Data tables 批量工具条 |
| 防重复提交 | `busy` 状态绑定所有操作按钮 `disabled`（行内 emoji 按钮 + 头部 Button 都绑） | Nielsen #1 |
| 确认浮层替代 window.confirm | SDK 无 Dialog/ConfirmDialog → 自绘 fixed 浮层（bg-black/50 + 卡片），Esc/遮罩关闭 + 焦点陷阱 | NN/g「确认框不如撤销」（删除等破坏性操作可保留确认） |
| 焦点陷阱 | `useTrapFocus(ref, active)`：keydown Tab 时在弹窗内 querySelectorAll 可聚焦元素首尾循环 | WCAG 2.4.3 |
| 骨架屏 | 结构已知的列表/消息区用灰条 `animate-pulse`（SkeletonRow/SkeletonBubble），不用转圈 | NN/g Skeleton Screens |
| 列表行键盘可操作 | 整行 `<div role="button" tabIndex={0} onKeyDown Enter/Space>`（行内含按钮时不能用 button 嵌套 button）+ `focus-visible:ring-2` 可见焦点 | WCAG 2.1.1/2.4.7 |
| 空态区分 | 筛选无结果 → 「没有匹配的会话 + 清除筛选」按钮；真没数据 → 「无会话」 | NN/g Empty States |
| 错误态 | 列表加载失败给「重试」按钮（load 抽成 useCallback 复用）；操作失败用行内红色横幅（opError state）替代 alert | Nielsen #9 |
| 搜索双语义提示 | 本地过滤 + Enter 全库搜索共用一个框时，placeholder 写清楚「筛选标题/人 · 回车搜消息」 | 认知负担最小 |

## 关键坑

- **列表行 div+onClick 是键盘不可操作的硬伤**（WCAG 2.1.1 A 级）——用 div+onClick 选中的列表必须补 tabIndex+role+onKeyDown，或改用可聚焦元素。
- SDK 无 Dialog/ConfirmDialog/DropdownMenu，浮层全部自绘 fixed div。
- 原生 checkbox 样式用内联 `style={{ accentColor: "var(--color-primary)" }}`（Tailwind accent-* 类可能未编译）。
- 改动 className 后必跑 `scripts/audit-classes.py`（用 Windows 路径传 web_dist_assets，MSYS /c/ 路径会 glob 0 文件）；补 style.css 转义选择器用 Python 写文件（patch 工具会双重转义 `\`）。

## 进行中会话判定（is_active，2026-08-10 实测）

用户把状态「活跃」定义为**正在进行的会话**（监控语义），不是「未置顶未归档」兜底档。数据层判据（channel-sessions 后端 service.py 实测）：

- state.db `sessions` 表**没有 is_active 列**（Hermes 自己的 /api/sessions 前端 interface 有该字段但 web_server 不返回）。
- 可靠判定：`ended_at IS NULL AND last_activity_at > (now - 300)`。
- ⚠️ **last_activity_at 是秒单位浮点**（不是毫秒）——用 `time.time()*1000` 对比会 0 命中。
- ⚠️ **ended_at IS NULL 不可单独用**：实测 626 会话中 227 个 ended_at NULL，但近 5 分钟真活跃的只有 3 个——大部分是历史遗留未正常结束的僵尸会话。必须带 5 分钟活跃窗口（与 Hermes cron runs 的 is_active 一致，web_server.py:11966 `< 300`）。
- SQL 免传参实现：`(ended_at IS NULL AND last_activity_at > (CAST(strftime('%s','now') AS REAL) - 300)) AS is_active`。
- 状态四档优先级：`archived > is_active > pinned > normal`（归档最优先；置顶∩进行中归「进行中」）。行内进行中指示用绿点 `●`（内联 style #34d399，零类依赖）。

## 筛选单向层级联动（用户拍板 2026-08-10）

全维度互联动（选平台后会话人计数变、选人后平台栏只剩 1 个选项）被用户否定——「下层选了之后，上层不要变」。正确行为：**上层过滤下层，下层不反向收缩上层**（选「平台=飞书 + 会话人=徐学环」后，平台栏仍显示全部平台）。

实现：`DIM_ORDER = ["q", "platform", "type", "person", "status"]`；统计维度 k 的选项计数时只应用 `DIM_ORDER` 中排在 k **之前**的维度筛选（`for i < DIM_ORDER.indexOf(k): apply(DIM_ORDER[i])`）。列表过滤仍是全维度 AND。

## 后端改动须重启 dashboard（不只是 rescan）

plugin_api.py / service.py 在 web_server 进程内 import（`Mounted plugin API routes` 日志），**改后端必须重启** 9120 才生效——manifest/rescan 只覆盖前端插件发现，不重载 Python。重启：`schtasks /End /TN HermesDashboard` → PowerShell 精确 kill `--port 9120` 的 python → `schtasks /Run` → poll `/api/dashboard/plugins` 200。前端 dist 静态文件则只需浏览器硬刷新。

## 页面「卡住」排查链（服务健康 ≠ 页面健康，2026-08-10 实测）

用户报「插件页面一直卡着」时，按此顺序取证再下结论：

1. `curl -s -o /dev/null -w "%{http_code} %{time_total}" http://127.0.0.1:<port>/api/dashboard/plugins` —— **后端 API 响应时间**（<0.1s = 服务健康）。
2. `netstat -ano | grep :<port>` —— 找 **CLOSE_WAIT/FIN_WAIT_2 悬挂连接**；`tasklist /FI "PID eq <pid>"` 确认悬挂连接归属（本案例是用户 Edge 浏览器，不是 gateway）。
3. `grep agent.log` 对照 **dashboard 重启时间线**（`Mounted plugin API routes` 出现次数 = 重启次数）——重启会打断浏览器活动请求，浏览器**不自动重试**已发出的 fetch → 页面转圈直到手动刷新。
4. `grep "Sessions will not survive" agent.log` —— 若重启后有该警告 = 登录态失效，页面 401 挂起（secret 已配置则无此警告）。
5. 结论典型：**后端健康 + 浏览器旧连接悬挂 + 近期重启** = 让用户硬刷新（Ctrl+Shift+R）即恢复；刷新后还卡才查前端代码。
