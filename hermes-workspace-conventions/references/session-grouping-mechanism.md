# Hermes 会话侧边栏分组机制

## 关键文件

- **分组逻辑**: `hermes-agent/tui_gateway/project_tree.py` → `build_tree()`
- **会话数据库**: `%LOCALAPPDATA%\hermes\state.db` → `sessions` 表
- **项目数据库**: `%LOCALAPPDATA%\hermes\projects.db` → `projects` 表

## 分组三级结构

```
Project (项目)
└── Repo (仓库) — 按 repo_root 或 cwd 分组
    └── Lane (分支) — 按 git_branch 或 cwd basename 分组
        └── Sessions
```

## Lane 分配逻辑 (`_place`)

1. **有 git repo** → 按 `git_branch` 建 lane，空 branch 默认 `DEFAULT_BRANCH_LABEL = "main"`
2. **无 git + 有 persisted_root** (`git_repo_root`) → 同规则 1
3. **无 git + 无 persisted_root** → `_place_by_heuristic()` → lane 名 = `base_name(cwd)`
4. **cwd 为空** → 跳过，不归入任何 repo

## 常见问题

### 侧边栏出现多个"分支"
根因：同项目下会话 `git_branch`/`git_repo_root` 不一致。

诊断：
```sql
SELECT git_branch, git_repo_root, COUNT(*) FROM sessions 
WHERE cwd = '项目路径' GROUP BY git_branch, git_repo_root;
```

修复：
```sql
UPDATE sessions SET git_branch = NULL, git_repo_root = NULL
WHERE cwd = '项目路径' 
AND (git_branch IS NOT NULL OR git_repo_root IS NOT NULL);
```

重启 Hermes GUI 生效。

### cwd=None 的会话
subagent 和部分 feishu 会话无 cwd → 不归入任何项目 → 侧边栏不可见。
这些是正常的，无需修复。

## 相关常量

```python
_TRUNK_BRANCHES = {"main", "master", "trunk", "develop"}
DEFAULT_BRANCH_LABEL = "main"
```

Trunk lane 排序优先于 feature lane。
