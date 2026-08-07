# 预览面板（preview pane）——内嵌浏览器架构与登录态

实测日期：2026-08-07。来源：磁盘取证（`%APPDATA%\Hermes\` 目录结构 + cookie 库大小/时间戳）。

## 是什么

Hermes 桌面 app 聊天旁的内嵌浏览器面板。工具：`open_preview` / `read_preview`（desktop_ui 插件，deferred tools 需 tool_search 加载）。

## 核心事实：无登录态

- **独立 Electron 分区**：存储 `%APPDATA%\Hermes\Partitions\hermes-browser\`（注意是 **Roaming/APPDATA**，不是 LocalAppData）。
  - 根目录 `%APPDATA%\Hermes\Network\Cookies` 是桌面 app 自身的 cookie 库；预览浏览器用的是 `Partitions\hermes-browser\Network\Cookies`，两者不同。
- **不继承用户 Chrome/Edge 登录态**：与真实浏览器 cookie 完全隔离。相当于无痕窗口。
- **登录态判定法（不靠猜）**：
  ```bash
  stat "$APPDATA/Hermes/Partitions/hermes-browser/Network/Cookies"
  # 20480 字节 = 空库（Chromium 空 cookie 库大小）；再看最后修改时间——停在首次使用日说明之后再没写过
  ls -la "$APPDATA/Hermes/Partitions/hermes-browser/Local Storage/leveldb/"
  # 数百字节 = 基本空
  ```
  实测：cookie 库 20480 字节、最后写入停留在 7月28日（首次使用日）；当天 open_preview 打开百度后仍未变化 → 无任何登录 cookie。
- **手动登录后可持久化**：在预览面板里登录某站，cookie 写回 hermes-browser 分区，下次打开还在——但只在该环境有效，与日常浏览器互不相通。

## 结论模板（回答用户"预览面板有登录态吗"）

预览面板 ≈ 无痕窗口：公开页面/本地 HTML 预览够用；需要登录态的抓取（知乎/豆瓣/百度反爬）仍走 **Kimi WebBridge**（用户真实浏览器）——预览面板和内置 Playwright 都解决不了登录问题。此结论与浏览器铁律一致：需要登录态/复现调试一律 WebBridge。

## 按窗口显示的行为

- `open_preview` 工具说明明确 "The pane opens for the current window only"。
- **远程场景**（B 机 Hermes 桌面版连本机 serve 9119，用户在 B 机看预览）：本机 `open_preview` 返回 success，但本机 `read_preview` 报 "No preview tab is open" **是正常现象**——预览开在远端窗口，不代表打开失败。验证靠用户肉眼确认远端窗口内容（或让用户描述页面）。
- `read_preview` 读不到 ≠ open_preview 失败：先区分"预览开在哪个窗口"再判断。

## 与浏览器三层架构的关系

browser-control skill 的 agent-browser / CDP / WebBridge 三层是 agent 侧的浏览器栈；预览面板是**桌面 app UI 侧**的第四种浏览器环境，互相独立。选层逻辑不受影响：登录态需求 → WebBridge。
