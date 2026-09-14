# 扩展 plugin-sdk 的 PR 范本（host.preview 案例）

**适用场景**：插件需要 SDK 当前没有的能力（IPC、UI 组件、host action），要走主仓库 hermes-agent PR 流程。

**前提**：当前 SDK 表面（`apps/desktop/src/sdk/index.ts`）真的没暴露这个能力——不是插件用法不对。

## 流程（dsh-settings / host.preview 案例，2026-08-20）

### 1. 调研 SDK 现状（不写代码）

- 读 `apps/desktop/src/sdk/index.ts` 的 named exports（决定了 plugin import 能拿到的全部能力）
- 读 `apps/desktop/src/sdk/runtime.ts`（shim 机制——决定 plugin 能否拿到新方法）
- 读 `apps/desktop/src/contrib/runtime-loader.ts`（plugin 加载链 + 安全约束 L116-120: "runtime plugins may only import @hermes/plugin-sdk and react"）
- 读 `apps/desktop/src/store/preview.ts` 看目标 store 的公开 API（`openPreview` 签名、`PreviewTarget` 字段、`PreviewRecordSource` 枚举）
- **判断**：能不能只改 `sdk/index.ts` 就够？还是要 IPC？答案是：store/preview.ts 已经是 renderer 内部模块、sdk/index.ts 已经 import 它——**只需改 sdk/index.ts 1 个文件**

### 2. 评估工作量（**纠正原估计**）

- 最初我说"6 文件改动"——错了。实测只改 **1 个文件（sdk/index.ts）+ 12 行**
- 之前估计过高的原因：把 IPC 路径当默认。实际上如果目标能力在 renderer 内有现成 store（`@/store/preview` 已被 sdk/index.ts import 过），就不需要 IPC
- **新纪律**：评估工作量时**先列"已有依赖"**，再算"要新增什么"

### 3. 写代码（缩进纪律）

- patch 工具的 `replace` 模式在 `old_string` 已缩进、`new_string` 缩进不匹配时**会乱掉**——常见现象是 `replace_all=false` 替换成功但实际行用了旧缩进
- **纪律**：涉及多行缩进敏感代码块时，**直接用 `execute_code` 写 Python 操作文件**，不要依赖 patch 工具的多行替换

### 4. commit + push 到 fork（gh CLI）

```bash
# 主仓库配 origin 通常指向不存在的 fork（"Repository not found"），需要先创建
git remote -v  # 看 origin 实际指向
git ls-remote origin --heads  # 验证可达

# 创建 fork（先确保 gh 已登录到目标账号）
gh auth status  # → 必须登录到要 fork 到的账号
gh repo fork NousResearch/hermes-agent --remote-name=origin
# → gh 自动创建 + 重写 origin 指向新 fork

# push（注意：fork 创建后 commit 之前 origin 不变，仍报 not found）
git push origin feat/branch-name --set-upstream
```

### 5. 开 PR（gh pr create）

```bash
gh pr create --base main \
  --head branchingjade:feat/plugin-sdk-host-preview \
  --title "feat(sdk): ..." \
  --body "..."  # 见下面的 PR 描述模板
```

**PR 描述模板**（hermes-agent 项目用 `.github/PULL_REQUEST_TEMPLATE.md`，里面"Checklist"明确要求 conventional commits + 单 PR 单改动）：

```markdown
## What does this PR do?

<一行说做了什么 + 为什么>

## Why?

<背景：用户场景 / 动机 / 为什么不能 workaround>

## How

<代码片段 + 解释关键设计决策>

## Type of Change

- [x] ✨ New feature (non-breaking change that adds functionality)

## How to Test

1. <步骤>
2. <验证期望结果>

## Checklist

### Code
- [x] Conventional commit message (`feat(sdk): ...`)
- [x] Single-file change, no unrelated commits
- [x] Diff is +N lines
```

### 6. 改 plugin 用新 API + fallback 模式（合并前可用）

**plugin 端必须做**：`hasNewAPI = typeof host.newMethod === 'function'` 探测，**没新 SDK 时走 fallback**（不让老版本用户遇到崩溃）：

```js
function handleAction() {
  if (typeof host.preview === 'function') {
    try { host.preview(url); return } catch (e) { /* 落到下面 */ }
  }
  // fallback: 老 SDK / 桌面版本无 host.preview
  navigator.clipboard.writeText(url)
}

// 面板 UI 同步显示诊断状态
jsx('span', { children: typeof host.preview === 'function'
  ? '✓ host.preview 已连接'
  : '⚠ host.preview 未就绪（需 Hermes Desktop 升级到含 PR #XXX 的版本）' })
```

### 7. 等 PR 合并 + 桌面发布

- PR 由 NousResearch 维护者审核
- 合并后要等 Hermes Desktop release 打包新 SDK（web_dist rebuild）
- **plugin 自动拿到新能力**（无需 plugin 改动，前提是 plugin 已经写好 fallback）

## 关键技术点（避免再踩）

| 坑 | 解决 |
|---|---|
| patch 工具缩进乱 | 用 Python write_file |
| origin "Repository not found" | `gh repo fork` 创建 |
| fork 创建后 origin URL 没自动更新 | gh 7.x 会自动重写；老版本手动 `git remote set-url` |
| PR 标题必须 conventional commits | `feat(sdk):` / `fix(...)` |
| plugin 直接调 `store/preview` 报错 "unsupported imports" | runtime-loader L116 硬约束，必须走 SDK |
| `openPreview` 第二参 `PreviewRecordSource` 不是 `PreviewTarget.source` | 看 store/preview.ts L21-44（target）vs L56（source 枚举）；两者是不同字段 |
| `PreviewTarget.source: string` 自由 | `'plugin'` 合法 |

## 监控 PR 状态

```bash
gh pr view 90437  # 单个 PR
gh pr list --state all --author @me  # 自己所有 PR
```

## 参考

- 实际 PR：https://github.com/NousResearch/hermes-agent/pull/90437
- fork 分支：branchingjade/hermes-agent `feat/plugin-sdk-host-preview` (commit 8a6eb8c7c)
- 主仓库：https://github.com/NousResearch/hermes-agent