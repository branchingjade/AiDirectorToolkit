# 已知社区桌面插件（2026-07）

## 实用工具

| 插件 | Repo | 说明 |
|------|------|------|
| Quota Panel | `yinghuashuxia7777-oss/hermes-quota-panel` | API 余量聚合面板 — Kimi/Codex/DeepSeek 用量+余额，钉在标题栏 |
| Skill Manager | `iPotatow/hermes-skill-manager` | 技能管理器 — 侧边栏页面管理所有技能，中英文界面，同步到 Codex |
| Web Browser | `AWhileLater/web-browser-plugin` | 内嵌 iframe 浏览器面板，支持导航/书签/快捷键。⚠️ 有三处已知 bug 需手动修复：`buildAnnotationEngineScript()` 中两处字符串拼接引号未配对（SyntaxError，第 142/146 行），`BrowserPane` 中 `onCopyBoth` 简写引用不存在的变量（ReferenceError，第 1467 行）。修复方法：`community-plugin-install.md` → 调试加载失败。已确认 Hermes Desktop `webviewTag: true`，修复后正常使用。 |
| Boardstate | `100yenadmin/boardstate-hermes-plugin` | 动态看板 — 实时小组件、沙盒自定义组件 |

## 效率/工作流

| 插件 | Repo | 说明 |
|------|------|------|
| Renderline | `HeiTuz/Renderline` | 独立浏览器 + 任务感知 QC 面板 |
| Hermes Link | `gilshm/hermes-link` | Profile 间消息总线，Agent 互委派任务 |
| Petdex Bridge | `irandoku/rndk-petdex-bridge` | 生命周期事件桥接到共享 Petdex 桌面吉祥物 |

## 桌面集成

| 插件 | Repo | 说明 |
|------|------|------|
| Rainmeter | `Woodylai24/hermes-rainmeter` | Rainmeter 桌面小组件 — 实时聊天、状态仪表盘 |
| Ghostty Notify | `mom1/ghostty-notify` | Ghostty 终端桌面通知 |
| Zim Wiki | `MarkoPaasila/hermes-zim-wiki-plugin` | Zim Desktop Wiki 集成 |

## 桌面控制/自动化

| 插件 | Repo | 说明 |
|------|------|------|
| Desktop Control | `unosanity/hermes-desktop-control` | 简单桌面控制（鼠标/键盘） |
| Computer Use | `Kori-x/hermes-computer-use-plugin` | Claude Computer Use 风格操控 |
| Orgo Desktop | `nickvasilescu/hermes-orgo-desktop-plugin` | Orgo Desktop API 同机箱操控 |
| THEIA | `TREE-Ind/THEIA-UI-Computer-Use` | 视觉感知 + UI 计算机使用（Windows） |
| Hyprland | `xCaptaiN09/hermes-hyprland-plugin` | Hyprland Wayland 桌面自动化 |
| Agent UI Local | `saminkhan1/agent-ui-local-desktop-plugin` | macOS 桌面上下文 + 计算机使用 |

## 交易/金融

| 插件 | Repo | 说明 |
|------|------|------|
| Trading Dashboard | `yng3/hermes-trading-dashboard` | ETH 价格、Kraken 余额、纸交易仓位 |

## 其他

| 插件 | Repo | 说明 |
|------|------|------|
| Voice Brief | `Zver1013/voice-brief` | 双通道回复 — 全文+语音摘要、TTS 代理 |
| Dran | `alvarolizama/hermes-dran` | Dran 第二大脑集成 |
| Atlas MCP | `ksimback/hermes-atlas-mcp` | MCP 服务器，暴露 Hermes 生态目录 |

> 这些是 GitHub 上搜到的。社区仍在早期，大多数项目 star 数不高但功能完整可用。
