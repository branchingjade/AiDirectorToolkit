# DSH 插件生态速查（2026-08-18）

> 来源：awesome-dsh-plugin（5200+ 收录）+ DSH 源码包
> 详细推荐见 Obsidian：`工具与集成/DeepSeek Harness 插件指南.md`

## 核心必装

| 插件 | 用途 | 安装 |
|------|------|------|
| dsh-market | 可视化插件市场 | `dsh plugin --profile web add dshmarket` |
| dsh-effort-slider | 推理强度滑块 | `dsh plugin --profile web add dsh-effort-slider` |
| modlens | 视觉模型接入 | `dsh plugin --profile web add modlens@3.17.2` |
| dsh-skill-picker | 技能选择器 | `dsh plugin --profile web add dsh-skill-picker` |
| dsh-hud | 状态面板 | `dsh plugin --profile web add dsh-hud` |

## 体验增强（按需）

dsh-model-search / dsh-file-mentions / dsh-auto-collapse / dsh-alive / dsh-sysmon / dsh-composer-expand / dsh-spotlight / dsh-trail / dsh-plan-switch

## 生态索引

- [awesome-dsh-plugin/awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin) — 社区精选
- [dsh-market/dsh-market](https://github.com/dsh-market/dsh-market) — Web UI 插件市场
- [awesome-dsh-plugin.com](https://awesome-dsh-plugin.com) — 在线浏览

## 注意

- 影响能力层的只有 **modlens**（视觉）+ DSH 本体包；其余 90% 是 Web UI 美化类
- headless 模式不需要任何 Web UI 插件
