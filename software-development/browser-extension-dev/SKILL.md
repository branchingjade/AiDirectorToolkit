---
name: browser-extension-dev
description: Chrome/Edge 浏览器扩展开发环境搭建与模块化重构。当用户需要开发/优化/重构浏览器扩展时使用。触发词：浏览器插件、Chrome扩展、油猴脚本、MV3、content script、扩展开发。
---

# 浏览器扩展开发

零依赖、纯 JS、模块化开发 Chrome/Edge 扩展的标准工作流。

## 项目结构

```
project/
├── build.sh                 ← cat 拼接构建脚本
├── .gitignore               ← 忽略 dist/
├── src/
│   ├── manifest.json
│   ├── bridge.js            ← MAIN world 脚本（不进模块合并）
│   ├── popup.{html,css,js}  ← 弹窗（独立文件）
│   ├── content-styles.css
│   ├── icons/
│   └── modules/             ← content.js 拆分模块
│       ├── config.js        ← 常量/配置
│       ├── <algorithm>.js   ← 纯算法（如模糊算法）
│       ├── <feature>.js     ← 功能模块
│       └── main.js          ← 入口（IIFE 包裹）
└── dist/                    ← 构建产物（Chrome 加载此目录）
```

## 原则

- **纯 JS + JSDoc**：不引入 TypeScript 编译步骤，用 JSDoc 注释获得 VS Code 类型提示
- **cat 拼接**：模块按依赖顺序 cat 拼接为单个 content.js，零构建依赖
- **Shadow DOM 隔离**：扩展 UI 全部放在 Shadow DOM 中，避免与页面样式冲突
- **dist 不入库**：`.gitignore` 忽略 dist/，只版本管理 src/

## build.sh 模板

```bash
#!/bin/bash
set -e
SRC="src" && DIST="dist"

# 拼接 content.js
cat "$SRC/modules/config.js" \
    "$SRC/modules/algorithm.js" \
    "$SRC/modules/feature-a.js" \
    "$SRC/modules/feature-b.js" \
    "$SRC/modules/main.js" \
    > "$DIST/content.js"

# 复制静态文件
cp "$SRC/bridge.js" "$DIST/"
cp "$SRC/manifest.json" "$DIST/"
cp "$SRC/popup.html" "$SRC/popup.css" "$SRC/popup.js" "$DIST/"
cp "$SRC/content-styles.css" "$DIST/"
mkdir -p "$DIST/icons" && cp "$SRC/icons/*" "$DIST/icons/"
```

## 工作流

```
改 src/ → bash build.sh → Chrome 刷新页面
```

Chrome 加载：`chrome://extensions` → 开发者模式 → 加载已解压 → 选择 `dist/`

## UI 设计预览

当需要探索扩展 UI 方向时：
1. 在 `.design/` 目录创建独立 HTML，包含 2-3 个方案并排展示
2. 用内联 CSS（不用外部样式表）确保可独立打开
3. 用 `start "" path` 在浏览器打开让用户对比
4. 确定方向后，将样式写入 Shadow DOM 的 `STYLES` 常量中

## 模块拆分粒度

| 模块类型 | 内容 | 示例 |
|----------|------|------|
| config | 常量、默认值、枚举 | `DEFAULT_HOSTS`, `BLUR_PRESETS` |
| algorithm | 纯算法函数，无 DOM 依赖 | StackBlur, 图片处理 |
| feature | 功能逻辑 + UI | 工具栏类、面板管理 |
| main | IIFE 入口 + 事件绑定 | `document.addEventListener("click"...)` |

## Pitfalls

- Chrome MV3 content script 不支持 `<script type="module">` 直接 import，所以用 cat 拼接而非 ES module
- bridge.js（MAIN world）不能合并到 content.js（ISOLATED world），需独立加载
- **content script（ISOLATED world）看不到页面 JS 设置的 expando 属性**（如 React 的 `__reactFiber$xxx`）——`Object.keys(element)` 返回空。凡是要扫描 React fiber、调用页面内部函数（如平台写入函数）的，必须放 MAIN world bridge.js 里做，content 走 postMessage 协议。完整方法见 `references/react-spa-extension-adaptation.md`
- **适配 React SPA 画布时，平台权威写函数通常可从 fiber 的 `memoizedProps` 找到**（如 `onNodeDataPatch`），但调用时 `allowFields` 参数必须显式传，否则平台默认字段白名单会过滤目标字段（静默无效）；且这类函数只拦 UI 入口、不拦数据写入，可绕过平台的 UI 锁定。详见 `references/react-spa-extension-adaptation.md`
- manifest.json 中 `host_permissions` 必须包含目标站点的完整域名
- Shadow DOM 的 `mode: "closed"` 防止页面 JS 访问扩展 UI 内部
- **禁止在 bridge.js 中劫持全局构造函数（Proxy、Promise、Array 等）**——bridge.js 在 `document_start` 运行于 MAIN world，任何对 `window.Proxy` 的修改会影响页面自己的 JS bundle（如 Vue 3 的响应式系统），导致 SPA 白屏/初始化失败。此类 patch 需在独立测试扩展中验证，绝不能直接改现有的生产 bridge.js。
- **误改 bridge.js 后的回滚**：`git checkout src/bridge.js && bash build.sh`，然后去 `chrome://extensions` 刷新扩展即可恢复。
