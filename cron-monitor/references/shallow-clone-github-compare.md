# Shallow Clone + GitHub Compare API

Hermes Agent 安装目录 `~/AppData/Local/hermes/hermes-agent` 是 shallow clone（depth=1），`git log HEAD..origin/main` 只显示顶层合并提交，无法列出具体功能提交。

## 检测是否 shallow clone

```bash
git -C ~/AppData/Local/hermes/hermes-agent rev-list --count HEAD
# 返回 1 → shallow clone
# 返回 >1 → 正常 clone
```

## 获取完整提交列表

```bash
# 1. Fetch 获取 old_sha→new_sha
git -C ~/AppData/Local/hermes/hermes-agent fetch origin
# 输出: 1c4cc00f7..5445e42b8  main -> origin/main

# 2. 用 GitHub Compare API（免认证即可用）
curl -s "https://api.github.com/repos/NousResearch/hermes-agent/compare/<old_sha>...<new_sha>" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Total commits:', d.get('total_commits'))
print('Ahead by:', d.get('ahead_by'))
for c in (d.get('commits') or [])[:80]:
    msg = c['commit']['message'].split('\n')[0]
    print(c['sha'][:9], msg)
"
```

## 字段说明

| 字段 | 含义 |
|------|------|
| `status` | `ahead` 或 `behind` |
| `ahead_by` | base 领先 head 的提交数 |
| `total_commits` | 总提交数 |
| `commits[].sha` | 完整 SHA |
| `commits[].commit.message` | 提交消息（第一行为标题） |

## 备选方案

如果不想依赖 GitHub API，可以 `git fetch --unshallow` 获取完整历史（首次需下载 ~200MB）：

```bash
git -C ~/AppData/Local/hermes/hermes-agent fetch --unshallow origin
```

之后 `git log HEAD..origin/main --no-merges` 即可正常工作。
