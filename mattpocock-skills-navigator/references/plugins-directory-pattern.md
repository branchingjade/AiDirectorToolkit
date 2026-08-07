# 插件目录架构模式

通过 grilling 确定的插件管理目录结构。类型优先、工作型、按需扩展。

## 设计决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 位置 | `~/Documents/Hermes/Plugins/` | Hermes 工作目录下，agent 直接访问 |
| 模式 | 工作型 | 频繁增删改，非纯存档 |
| 组织 | 按类型分层 | 用户知道"找油猴脚本"而非"找最近装的" |
| 扩展 | 按需增删子目录 | 避免过度预设计 |

## 目录结构

```
Plugins/
├── README.md               # 根说明
├── browsers/
│   ├── extensions/         # Chrome/Edge .crx 或解压目录
│   ├── userscripts/        # Tampermonkey .user.js
│   └── userstyles/         # Stylus .user.css
├── tools/
│   ├── comfyui-nodes/      # ComfyUI 自定义节点
│   ├── touchdesigner/      # TD .tox 组件
│   └── vscode-extensions/  # VS Code .vsix
└── scripts/                # 批量管理脚本
```

## 每个插件子目录规范

```
<plugin-name>-v<version>/
├── README.md               # 名称、版本、来源、安装方式
├── <插件文件>               # 扩展/脚本文件
└── ...
```

## 使用模式

- **Agent 操作**（主）：`ls Plugins/browsers/extensions/` 即可，在工作目录下
- **手动安装**（次）：File Explorer 打开目录 → 浏览器加载已解压
- **脚本引用**：路径变量存一次，长或短无差别
