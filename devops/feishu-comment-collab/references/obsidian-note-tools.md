# Obsidian 笔记工具权限模式（评论 agent 用）

## 权限范围（按协作体系 admin/worker 分级）

| 操作 | admin（妖玉） | member（worker） |
|---|---|---|
| 项目目录（伏妖记/ 等） | ✅ | ✅ |
| 剧本库（共享素材） | ✅ | ✅ |
| Hermes运维（凭据/ops 类） | ✅ | ❌ |
| 成员画像 | ✅ | ❌ |
| 搜索范围 | 全 Vault | 仅当前项目 + 剧本库 |

member 允许根：当前路由项目目录 + `_MEMBER_ALLOWED_ROOTS = ("剧本库",)`（代码常量）。

## 路径穿越防护模式

```python
def _normalize_rel(rel_path):
    rel = rel_path.replace("\\", "/").strip().lstrip("/")
    candidate = (VAULT_ROOT / rel).resolve()
    candidate.relative_to(VAULT_ROOT)   # 越界抛 ValueError → 拒绝
```

- 先 resolve（吃 `..`）再 relative_to 容器校验——双重防穿越
- 只放行 `.md`/`.markdown` 后缀
- 实测：`../../Windows/System32/x.md` 被拒

## 上下文传递（thread-local）

- `collab.set_commenter(open_id)` / `collab.set_project(project)` 由 feishu_comment.py 在 agent 运行前设置
- 工具 handler 读取做角色/范围判断
- project 从会话 key 解析：`comment:{project}:{user}` 的第二段（`comment:doc:...` 表示未路由，project=None → member 只能读剧本库）

## 搜索实现要点

- 文件名命中优先；内容匹配只扫每个文件前 4000 字符、命中数达 limit*3 后停止内容扫描（防慢）
- 跳过隐藏目录（`.obsidian` 等）
- 单次读取截断 8000 字符，尾部标注全文长度

## 工具注册

- 文件放 `tools/feishu_comment_obsidian_tools.py`，`registry.register(name, toolset="feishu_comment", schema, handler, check_fn=...)`
- 工具发现机制：registry 自动扫描 `tools/` 目录所有 .py（有 `tool_discovery_cache.json` 缓存，新文件自动重建），无需手动注册 import
- toolsets.py 里 `feishu_comment` toolset 的 tools 列表要同步加新工具名
