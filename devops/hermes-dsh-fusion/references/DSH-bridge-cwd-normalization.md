# DSH 桥 cwd 规范化：`/c/Users/...` → `C:\Users\...`

> 2026-08-19 实测。桥传 MSYS 风格路径，DSH 把它字面存储为 `C:\c\Users\HMSJ\...`，
> 导致 session.cwd 错、workspace 错裂为多个（"creator" + 伪 "Hermes" 工作区）。

## 现象

桥调 `session.create` 后立刻 `session.prompt` 返回 `session-not-found`，但
`workspace.create` 返回正常（DSH 对同一 path 幂等）。

拉 `/api/workspace.list` 看到两份工作区指向同一项目：

| 工作区 | path | sessions |
|---|---|---|
| creator | `C:\Users\HMSJ\Documents\Hermes` | 44 |
| **Hermes**（伪） | **`C:\c\Users\HMSJ\Documents\Hermes`** | 2 |

session.cwd 实际值：

```json
{"requestedCwd":"C:\\Users\\HMSJ\\Documents\\Hermes",
 "existingCwd":"C:\\c\\Users\\HMSJ\\Documents\\Hermes"}
```

DSH 把 `/c/Users/HMSJ/Documents/Hermes` 当字面值，没去 MSYS 前缀，
直接拼成 `C:\c\Users\HMSJ\Documents\Hermes` 存进数据库。

## 根因

DSH web 8080 服务在 Windows 上运行，**不会自动识别 MSYS 风格的 POSIX 路径**。
桥从 bash 拿到 `/c/Users/HMSJ/Documents/Hermes`（MSYS 缩写），原样传给
`workspace.create({"path": cwd})` 和 `session.create({"cwd": cwd})`：

- `workspace.create` 收到 `C:\c\...`（错，但 DSH 用 path 字面值建工作区，
  不做 Windows 路径规范化——又因为字符串值"不冲突"被允许创建）
- `session.create` 收到同 path → session.cwd = `C:\c\...`
- session.cwd 指向 `/c\...` 工作区，而 `workspace.create` 之前返回的
  `ef9bd119-...`（creator 工作区 path=`C:\Users\HMSJ\Documents\Hermes`）
  和 session.cwd 不匹配 → session 落到伪 Hermes 工作区

## 修复

**桥加 `_normalize_cwd()` 函数，在 `_ensure_workspace()` 内部用规范化值，
session.create 用 workspaceId 而非 cwd（避免双重传递）：**

```python
def _normalize_cwd(cwd):
    """把 MSYS 风格路径 /c/Users/... 规范成 Windows 原生 C:\\Users\\...

    避免 DSH 把 /c/ 误处理成字面值 \\c\\。
    """
    if not cwd:
        return cwd
    s = str(cwd).replace("/", os.sep).rstrip("\\/")
    if len(s) >= 3 and s[0] == os.sep and s[2] == os.sep and s[1].isalpha():
        s = s[1].upper() + ":" + s[2:]
    return s


def _ensure_workspace(cwd):
    try:
        norm_cwd = _normalize_cwd(cwd)
        val = rpc("workspace.create", {"path": norm_cwd})
        return (val or {}).get("workspace", {}).get("workspaceId")
    except Exception:
        return None
```

session.create **优先用 workspaceId**（已经是 v2.1 桥的设计）：
带 workspaceId 创建 → DSH 内部按 workspace 的 path 字段而非请求 cwd
确定 session 归属，规避路径规范化歧义。

## 验证

```bash
# 1. 端到端走桥
python scripts/dsh_bridge.py run "/c/Users/HMSJ/Documents/Hermes" \
  "hi" --route normalize-cwd-verify

# 2. 看 workspace.json 确认归到正确工作区
python -c "
import json
d = json.load(open(r'C:/Users/HMSJ/.dsh/storages/workspace.json'))
for wid, w in d['tables']['workspaces'].items():
    if 'hi' in str(w):
        print(w.get('title'), w.get('path'))
"

# 期望输出：creator C:\Users\HMSJ\Documents\Hermes
```

## 清理历史脏工作区

修复后**已经存在**的伪 Hermes 工作区（path 含 `\c\`）不会自动消失——
DSH 没有 move/attach RPC。需要：

1. 备份 `~/.dsh/storages/workspace.json`
2. 关 DSH web（避免内存状态覆盖磁盘改动）
3. 编辑 JSON：把脏工作区的 `sessionIds` 移到正确工作区（按 path 匹配）
4. 删除脏工作区 entry
5. 重启 DSH web

**该操作有 5 个 cron 短期不受影响**（DSH 内存工作区状态会因 cron session.create
重建时刷新）。脏工作区通常只含几个验证会话，业务影响小——可以推迟到下次维护窗口
做，**不必立即修**。

## 诊断口诀

`session-not-found` + 桥能调通 `workspace.create` + DSH 启动无报错：
- 先查 workspace.list 看 path 字段有没有 `\c\`
- 查 session.cwd（通过 `session.create` 用同 id 试重，返回的 `existingCwd`）
- 命中 `C:\c\...` 模式 → MSYS cwd 未规范化，跑上面修复

## 复发风险

⚠️ 任何调桥的脚本（cron prompt / DSH 任务书 / shell 脚本）传 cwd 时若用
POSIX 风格 `/c/Users/...` 而非 Windows `C:\Users\...`，桥的 `_normalize_cwd`
必须先走。这条铁律放进 hermes-dsh-fusion skill 的"坑"章节。