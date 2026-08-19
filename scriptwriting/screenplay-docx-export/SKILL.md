---
name: screenplay-docx-export
description: 剧本场次原文本 → Word 文档。识别场号/场景标题/△批注/角色对白/动作描写。
version: 1.0.0
author: Hermes (created 2026-08-19)
license: MIT
metadata:
  hermes:
    tags: [screenplay, docx, export, scriptwriting, Word]
    category: scriptwriting
    related_skills: [docx, screenplay-iteration-management, screenplay-archive]
---

# 剧本场景 → Word 文档导出

## When to Use

把按行排版的剧本原始文本（每行一个描写/对白/批注单元，无空行分隔）转成正式 Word 文档，保留剧本段落结构与字体语义。

把按行排版的剧本原始文本（每行一个描写/对白/批注单元，无空行分隔）转成正式 Word 文档，保留剧本段落结构与字体语义。

## 何时使用

- 用户给一段场次文本（场号 + 场景标题 + 动作描写 + 角色对白 + △批注），要求整理成 Word
- 需要把飞书 / 笔记里的剧本片段导出供团队审阅
- 任何「剧本原文本 → 可分发 Word」的需求

不要用于：PDF 排版（用 pdf skill）、Markdown 转 docx（用 pandoc）、结构化剧本库维护（用 screenplay-library-maintenance）。

## 剧本标记语法

输入文本通常遵循这种行级标记（无空行）：

| 标记           | 示例                                                      | 渲染样式                       |
| -------------- | --------------------------------------------------------- | ------------------------------ |
| **场次编号**   | `魔王 38` 或 `38-3`                                       | 居中粗体大字                   |
| **场景标题**   | `场2 地面战场 日 外`                                      | 居中粗体标题（Heading 2）      |
| **△导演批注**  | `△萧烬站在焦土边缘。...`                                  | 灰色斜体楷体，缩进             |
| **角色对白**   | `萧烬：（极轻，缓慢，清晰）还活着。`                      | 角色名加粗独占一行 + 台词缩进 |
| **动作描写**   | `近景固定拍摄萧烬。萧烬低头看脚下...`                     | 首行缩进宋体正文               |

识别规则用一行正则即可：

```js
const ROLE_RE = /^([^：:（(]{1,8})[：:]\s*(.*)$/;
```

允许 1-8 个非冒号/左括号字符作为角色名（兼容「萧烬」「林虽然」「白泽」等中文名）；后续用 `：` 或 `:` 引导台词。

## 核心解析规则

**每行独立成段，绝不 buffer-merge。** 剧本原文本每行就是一个语义单元（一个动作、一句对白、一条批注），没有空行分隔。如果按"累积连续非空行直到空行"的常规文本策略处理，会把所有动作描写压成一个超长段落。

```js
// ❌ 错误:连续非空行累积
let buffer = [];
for (const line of lines) {
  if (!line.trim()) { flush(buffer); buffer = []; }
  else buffer.push(line.trim());  // ← 灾难:64 行变 19 段
}

// ✅ 正确:每行独立判断
for (const line of lines) {
  const t = line.trim();
  if (!t) continue;
  if (/^\d+(-\d+)?$/.test(t)) blocks.push({ type: 'num' });
  else if (/^场\d+/.test(t)) blocks.push({ type: 'sceneHead' });
  else if (t.startsWith('△')) blocks.push({ type: 'note' });
  else if (ROLE_RE.test(t)) blocks.push({ type: 'dialog', ... });
  else blocks.push({ type: 'action', text: t });
}
```

## 排版约定

| 元素       | 字体           | 缩进             | 行距  | 备注                |
| ---------- | -------------- | ---------------- | ----- | ------------------- |
| 场次编号   | SimSun 14pt 粗 | 居中             | —     | 上下间距宽          |
| 场景标题   | SimHei 16pt 粗 | 居中             | —     | Heading 2           |
| △批注      | KaiTi 11pt 斜体 | 左缩 480 twip | 1.7倍 | 灰色 `#606060`     |
| 角色名     | SimHei 12pt 粗 | 左缩 480 twip | —     | 「角色名：」独占一行 |
| 台词       | SimSun 12pt    | 左缩 720 twip | 1.8倍 | 悬挂                |
| 动作描写   | SimSun 12pt    | 首行缩 480 twip | 1.8倍 |                     |

页面：四周 1 英寸（1440 twip）边距。页眉写「《XX》 第N场」灰色小字右对齐，页脚写页码居中。

## 交付协议

生成文档后必须：

1. **落盘到工作区可写路径**（如 `Documents/Hermes/_work/<项目名>/`），不要只生成在临时目录
2. **跑 schema 验证**：`python <hermes>/skills/productivity/docx/scripts/office/validate.py out.docx` 必须返回 `All validations PASSED!`
3. **校验段落数 ≈ 输入有效行数**（允许 ±2 浮动），不一致就说明解析出问题
4. **回报路径 + 验证结果 + 已知边角情况**

### 已知边角情况（直接交付，不追问）

- **行内嵌多对白**：原文一行里塞两个角色对白（例「白泽：能量归零了。她……白泽脸上带着笑意：逆转成功了」），按原文保留合并形态，不强行切分。在交付消息里诚实说明哪几行有此情况。
- **角色名含书名号**：如果未来出现 `《书名》：台词`，正则要放宽；当前默认不处理。
- **未安装 LibreOffice**：本机没 soffice 就跑不了 PDF 验证，跳过渲染验证但 schema 验证必跑。

**原则：交付完成 > 完美切割。** 边角问题交付时一句话说明，让用户决定要不要改，而不是用澄清问题阻塞交付。

## 验证清单

- [ ] 段落数 ≈ 输入有效行数（±2）
- [ ] 角色对白被识别为 dialog（数 `角色名：` 出现次数对得上）
- [ ] △批注行数对得上
- [ ] 场次标题 + 场次编号各自独立成段
- [ ] docx validate.py 返回 PASSED
- [ ] 文件路径告知用户

## 相关资源

- 完整生成器脚本：`scripts/generate.js`（基于 docx npm 包，参数化项目名/场号）
- docx npm 包基础用法：`hermes/skills/productivity/docx`（**只读参考**，那是 bundled skill）
- 验证脚本：`hermes/skills/productivity/docx/scripts/office/validate.py`

## 踩过的坑

1. **buffer-merge 把段落压扁**：见上文「核心解析规则」。这是本会话最重要的一条教训，64 行输入压成 19 段就被它坑过一次。
2. **PageBreak 必须在 Paragraph 内**：docx-js 的 `PageBreak` 不是顶层元素，要包在 `Paragraph.children` 里。
3. **CJK 字体必须显式声明**：docx 默认 Latin 字体，中文段落必须 `font: 'SimSun'`，否则 Word 显示成方框或 fallback 到默认中文字体（不一致）。
4. **不要 `new TextRun('\n')` 换行**：必须用独立 Paragraph 元素。