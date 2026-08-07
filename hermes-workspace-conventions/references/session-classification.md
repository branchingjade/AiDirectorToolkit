# 会话分类策略

## 数据源

`state.db` 的 `sessions` 表，非 cron/非 subagent 的条目（约 184 条）。

## 分类字段

| 字段 | 可靠性 | 说明 |
|:---|:---|:---|
| `git_repo_root` | 高 | 仅 116 条有值，且 95% 指向 `Hermes` 目录。只能区分顶层仓库（Hermes/KnowledgeBase/AiDirectorToolkit）。 |
| `cwd` | 高 | 覆盖略多于 git_repo_root。有 worktree 路径可区分 Blender/Eagle 子上下文。 |
| `title` | 中 | 飞书来源无 cwd 时唯一依据。长度有限，有歧义。 |
| `source` | 辅助 | 用于区分飞书/桌面/终端来源，不直接决定项目归属。 |
| `parent_session_id` | 辅助 | subagent 可通过此字段链回到父会话的项目。 |

## 分层匹配策略

```
第一层：结构化路径匹配
  ├─ git_repo_root 非 Hermes 目录 → 直接归属
  └─ cwd 中的 worktree 路径 → 单独分组

第二层：标题关键词匹配
  ├─ 犬子无双：角色名/地名/剧情关键词
  ├─ Blender/3D：blender/Mixamo/MB-Lab
  ├─ 飞书集成：飞书*/gateway/openclaw
  ├─ 黑盒语音：黑盒/heychat
  ├─ AI绘画/视频：ComfyUI/超分/RunningHub
  └─ KnowledgeBase/Obsidian

第三层：兜底 → Hermes 平台
  └─ 以上都不命中 → Hermes 平台（85 个，含配置/运维/测试等杂项）
```

## 输出格式

Markdown 表格，存 `~/Documents/Hermes/会话分类.md`。为静态快照，会话新增/删除后需手动更新。

## 踩坑

- **projects.db 无 parent_id**：不支持子项目树。不要在 projects.db 建层级关系。
- **飞书会话缺 cwd**：63 条飞书会话无 cwd，仅靠标题分类。边界模糊的保守归 Hermes。
- **blender-mcp 会话混入犬子无双讨论**：关键词匹配无法处理多主题交叉会话。保持原始归属。
- **Hermes 桶太大**：85 个会话可按「运维配置」「技能与MCP」「测试」再拆，但边际收益递减。
