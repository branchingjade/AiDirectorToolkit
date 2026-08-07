---
name: spa-content-extractor
description: 批量提取任何SPA/动态网站的文档或内容。三步法：navigate → snapshot(full=true) → read_file → 按规则提取文本。并行用 delegate_task 加速。触发词：抓取网页、提取文档、SPA网站、批量爬文档、web scraping、content extraction。
---

# 通用 SPA 网页内容提取

## 铁律

1. **innerText 优先：** `browser_navigate(url) → browser_console('document.body.innerText')` 是SPA页面最可靠的文本提取方式。返回干净纯文本，无嵌套重复。snapshot是DOM树，有大量嵌套重复，仅在需要accessibility结构时使用。
2. **禁止 CORS fetch / Python requests** -- SPA 页面只能拿到空壳。
3. **每页单独提取**，一页约30秒，不贪多。
4. **批量用 `delegate_task` 并行**。子agent拥有独立浏览器实例，可以并行运行。指令必须完整：
   - 指定提取方法（innerText vs snapshot）
   - 指定是否允许点击（SPA页面可能需要）
   - 指定输出格式和路径
   - 指定页面身份验证方法
5. **验证方法后重复它。** 第一页成功后直接重复N页，不优化、不换方案、不分析。29页抓取 = 重复同一个已验证动作29次，不需要创新。

## snapshot 解析规则

snapshot 是缩进文本树。关键模式：

| 目标内容 | snapshot 模式 | 示例 |
|----------|--------------|------|
| 参数表行 | `- StaticText "参数名 类型 说明"` | config 表、API 参数 |
| 表头行 | `- columnheader "字段"` | 带结构的表格 |
| HTTP 端点 | 包含 `POST https://...` 或 `GET https://...` | API 路由 |
| 代码块 | `- code` → `- StaticText "...源代码..."` | 示例代码 |
| 列表项 | `- listitem → StaticText "..."` | 功能列表、参数枚举 |
| 段落 | `- paragraph → StaticText "..."` | 描述性文本 |

## 适用场景

- 任何 SPA 文档站（火山引擎/阿里云/飞书/Notion/GitHub）
- API 参考文档、配置手册、参数表
- 需要登录态的页面**不适用**（需走 WebBridge）
- 视觉依赖的页面（Canvas/WebGL）可用 `browser_vision` 补充

## 输出格式

```markdown
### 目标名称
```
端点 URL / 描述
```
| 字段 | 类型 | 必选 | 说明 |
|------|------|------|------|
...
```

## 模型行为对提取质量的影响

不同模型在相同任务上的表现差异显著（2026-07-21 豆包语音API抓取实测）：

| 模型 | 行为特征 | 对提取任务的影响 |
|------|----------|-----------------|
| MiMo v2.5-pro | 分析过多、执行不足，反复"优化"已验证方法 | 慢但最终完成 |
| DeepSeek v4-pro | 更容易被MoA参考模型左右，缺乏独立判断 | 方向摇摆 |

**关键教训：** 不管用哪个模型，第一条铁律不变——验证方法后重复它，不优化、不换方案。

## 已知坑

- SPA 页面默认内容 ≠ API 文档。文档内容可能在子导航项下，需查看 snapshot 全文判断
- **某些文档 URL 可能已被完全重定向** — 导航后检查页面 title 和面包屑（breadcrumb listitem）。如果 title 不是预期文档标题或 breadcrumb 指向通用页面（如"产品动态"），说明该 URL 已失效，原 API 内容无法通过旧 URL 直接访问。
- 鉴权方式不统一：目标站可能用 API Key / HMAC 签名 / OAuth
- `browser_snapshot(full=true)` 输出的 snapshot 经常超过 15000 字符被截断，**必须用返回文件路径重新 `read_file`** 获取完整内容。不要依赖 inline snapshot 提取参数表。
- `browser_console` 的表达式长度有限制（复杂 JS 或超大 payload 可能截断），但 `document.body.innerText` 一般可正常返回完整页面文本（已验证约 95KB 正常）。如需提取纯文本内容，推荐用 innerText 替代 snapshot 方式。

## 侧边栏点击法（SPA重定向页面）

某些SPA文档站的URL直接访问会重定向到通用页面（如"产品动态"），必须通过侧边栏导航才能到达API内容页。

**流程：**
1. `browser_navigate(任意一个能正常加载的API页面)` — 进入API参考模式
2. `browser_snapshot` — 获取侧边栏菜单项的ref
3. `browser_click(目标分类ref)` — 展开子菜单
4. `browser_snapshot` — 获取子菜单项的ref
5. `browser_click(具体API文档ref)` — 进入目标页面
6. `browser_console('document.body.innerText')` — 提取内容

**识别重定向页面：** 导航后检查页面标题。如果标题是"产品动态"、"产品简介"等通用页面，说明URL已重定向，需要通过侧边栏点击进入。

## �agent并行指令模板

子agent拥有独立浏览器实例，可以并行。但指令质量决定结果质量：

```
✅ 正确指令：
- 允许点击侧边栏（SPA页面可能需要）
- 指定提取方法（innerText vs snapshot）
- 指定输出格式和路径
- 指定页面身份验证方法

❌ 错误指令：
- "不要点任何东西"（SPA页面必须点击侧边栏）
- 不指定提取方法（agent自行选择，质量不可控）
- 不验证页面身份（可能提取到错误页面内容）
```

## 参考文件

此技能目录下附带以下参考文件（`skill_view(name='spa-content-extractor', file_path='references/...')` 读取）：

| 文件 | 内容 |
|------|------|
| `references/volcengine-api-docs.md` | 火山引擎豆包语音API文档站特定模式：URL重定向检测、有效/失效页面清单、参数模式、HTML表格模式 |
| `references/spa-volcengine-extraction.md` | 火山引擎文档抓取实战记录：有效方法、踩坑记录、最终文档结构 |

## HTML 表格提取

某些文档页（如错误码对照表）使用原生 HTML `<table>`，在 snapshot 中显示为：

```
- table
  - row
    - cell "列名1"
      - paragraph - StaticText "列名1"
    - cell "列名2"
      - paragraph - StaticText "列名2"
  - row
    - cell "值A"
      - paragraph
        - StaticText "值A"
    - cell "值B"
      - paragraph
        - StaticText "值B"
```

提取规则：
1. 首行 row 是表头（columnheader 或 cell）
2. 后续每行 row 是一条记录
3. 每行内逐个 cell 取值，按顺序对应列名
4. 合并写入 markdown 表格

## 页面身份确认流程

导航后立即检查 breadcrumb 确认页面身份：

```
- listitem [level=1] - StaticText "文档首页"
- generic - StaticText "产品名称"
- generic - StaticText "模块名"
- generic - StaticText "预期页面名"    ← 目标
```

如果 breadcrumb 最后一层不是预期页面名（如显示"产品动态"），当前 URL 已被重定向，原内容不可直接提取。

## 输出文件组装

批量提取多页时，每页输出到同一个汇总文件，每页包含：
1. 页面标题 + 原始 URL
2. 端点 URL（HTTP 方法+路径）
3. 原始描述（StaticText 段落）
4. 结构化 markdown 表格（参数、响应头、响应体、错误码）
5. 重定向页面标注原因
