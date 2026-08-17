# 本地补丁投递官方（upstream contribution）

2026-08-08 实测全流程（NousResearch/hermes-agent，PR #81493 / #81494 均 OPEN+MERGEABLE）。
本地补丁生命周期的最后一步：打补丁 → Obsidian 归档 → **投递官方** → 合并后移除本地 diff。

## 1. 投递前评估：分层

| 层 | 判据 | 动作 |
|----|------|------|
| A 可投 | 通用 bug fix，与用户环境无关 | 投 PR |
| B 不投 | 依赖用户环境（vault 路径/成员名单/画像/多用户权限模型）、用户架构决策（如 PROJECT_MEMO 移除）、用户偏好（如观察上限 999） | 留在本地，靠归档 + autostash 保护 |
| C 另案 | 补丁在依赖包（site-packages 如 hindsight_embed） | 投对应仓库，不在主仓库投递范围 |

用户特定定制投官方必被拒——官方没有那套环境。评估时诚实分层，别把 B 层混进 A 层 PR。

## 2. 上游状态预检（先查再动手）

```bash
cd <fork-clone>
git fetch origin main -q
git diff HEAD origin/main --stat -- <目标文件>     # 官方是否已改该文件
git log origin/main --oneline -3 -- <目标文件>      # 官方是否已修
gh issue list --repo <上游> --search "<错误码|症状>"  # 查重复 issue
```
- **issue 查 duplicate**：AI triage 常把新 issue 标记为更早 issue 的 duplicate（实测 #81169 → duplicate of #78975）——PR 要关联 canonical issue。
- 官方 main 对目标文件可能有无关新改动（如 lazy-deps）——rebase 前确认改动区域不重叠，冲突就小。

## 3. fork + clone（gh 2.95 实测坑）

```bash
# ❌ 会打印 help：布尔 flag 不接受 =true
gh repo fork <org>/<repo> --clone --remote=true

# ✅ 分步（clone fork 时 gh 自动配 upstream，勿再手动 git remote add upstream——会报 already exists，无害但多余）
gh repo fork <org>/<repo>
gh repo clone <你>/<repo>        # 放 Projects/ 下隔离，不污染运行实例
# upstream 已自动配置；从 upstream/main 建分支
git checkout -b fix/<描述> origin/main
```

## 4. 干净重放（最关键）

**本地 git diff 混着 B 层改动，不能直接提交。** 每 PR 独立分支，手动重放对应文件的干净版：
- 只重放目标文件的修复逻辑（对着本地补丁的语义，在最新 upstream 代码上重写）
- PR 分支上 `git status` 必须只含该 PR 的文件
- commit message / 注释 / PR body 全英文、通用描述，**零用户环境信息**（无路径/项目名/中文/用户名）——提交前 grep 复查

## 5. issue 占位

canonical + duplicate 都留言 "Working on a fix for this. Plan: ... Will open a PR shortly."（英文），避免别人同时开工。

## 6. 对齐官方已有模式

找同类 bug 的既有修复镜像其写法（实测：feishu audio 的 99992402 修复在 `_send_uploaded_file_message`，post 修复镜像它 → 维护者容易接受）。

## 7. 测试（Windows 实测）

- 系统 Python（本机 `AppData\Local\Programs\Python\Python312\python.exe`，skill 里旧的 Python311 路径不存在），user site 装 `pytest-xdist` `pytest-asyncio`（unset PYTHONPATH 再装，防 venv 污染）
- 跑法：`unset PYTHONPATH && export PYTHONPATH="$(pwd)" && python -m pytest <file> -n 0 --tb=short`（`-n 0` 覆盖 pyproject.toml 的 addopts）
- **mock 前先 grep 真实方法名**：适配器消息发送方法是 `send()` 不是 `send_message()`；`send()` 捕获异常返回 `SendResult(success=False, error=...)` 不 propagate——测试断言按真实行为写
- **回归对比法**（判断失败是回归还是平台固有）：`git stash -q` → 跑基线 → `git stash pop -q` → 对比失败数与失败名单。POSIX 权限位（umask/0o600）、symlink 测试在 Windows 必失败——基线一致即零回归
- 测试残留 `$tmp` 之类文件记得清理（污染检查）

## 8. 合并后收尾

- 本地 `hermes-local-patches.diff` 移除已合并文件的补丁（重新生成 diff）→ autostash 保护范围缩小
- Obsidian 补丁管理 README 更新投递状态
