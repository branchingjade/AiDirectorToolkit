# 并行会话推单文件到技能正本仓库的边界条件（2026-08-07 实测）

场景：技能正本仓库（`~/AppData/Local/hermes/skills/` → AiDirectorToolkit）被并行会话重构为
精简结构（远端 master 只保留 `devops/` + `妖玉影视/`），但**本地 master 可能仍 tracked 了
不在远端的技能**（如 hermes-workspace-conventions——本地有、远端无）。

## 坑：cherry-pick 推单文件撞 add/delete 冲突

用「临时分支 + cherry-pick」推自己的单文件提交时，若该文件/目录在 `origin/master` 不存在：

```
git checkout -b tmp-push-<名> origin/master
git cherry-pick <自己的commit>   # → add/delete 冲突（远端没有这个文件，本地在改它）
git push origin tmp-push-<名>:master  # → "Everything up-to-date"（没有新提交可推，cherry-pick 停在冲突态）
```

cherry-pick 停在冲突状态但 grep `<<<<<<<` 计数为 0（add/delete 型冲突无标记行），
`git status` 显示 `Unmerged paths`——容易误判。

## 正确姿势

1. **推送前先确认文件在远端存在**：
   ```bash
   git ls-tree origin/master --name-only   # 看远端目录结构
   git log --oneline origin/master -- <路径>   # 远端历史是否出现过该文件
   ```
2. **远端无此目录 = 该技能不在正本仓库范围**（本地 tracked 可能是历史残留或并行会话的
   本地实验）——**本地 commit 已持久化即够，不要推**。强行推送会把整个目录引入正本，
   违背仓库精简方向（且文件不在远端时 cherry-pick/merge 必然冲突）。
3. 中止冲突现场并还原并行会话改动：
   ```bash
   git cherry-pick --abort
   git checkout master
   git branch -D tmp-push-<名>
   git stash pop    # 还原 push 前 stash 的并行会话未提交改动
   ```

## 判定口诀

`git ls-tree origin/master --name-only` 有该目录 → 走 tmp-push 流程推送；
没有 → 本地 commit 即收尾，不推。

## 坑2：tmp 分支上 `git checkout master -- <文件>` 取到旧版（2026-08-10 实测）

走 tmp-push 流程时，用 `git checkout master -- <文件>` 把改动带上 tmp 分支——**若该改动只在工作树、未 commit 到本地 master，checkout 取的是 master 上已提交的旧版**，push 后远端是旧内容，且 push 报告成功（无冲突、fast-forward 正常），不易察觉。

实测案例：impeccable SKILL.md 加「先查库」路由句——工作树已改但未 commit，`git checkout master -- impeccable/SKILL.md` 把旧版带上 tmp 分支推送，远端 11623 字节无新句；`git show origin/master:<文件> | grep 新标记` 返回 0 才暴露。修复：本地 master 先 commit 该文件 → 重建 tmp 分支 → `git checkout master -- <文件>` → push → 复验。

**铁律**：
1. **先 commit 到本地 master，再进 tmp 分支取文件**——checkout 只能取已提交内容
2. **push 后必须复验远端内容**（`git show origin/master:<文件> | grep <新标记>` 或 Python 读字节数），不能信 push 的 success 输出——本次 push 报告成功但内容是旧的
3. 复验失败时：本地 master 补 commit → 重走 tmp-push（远端多一个旧 commit 无害，新的 fast-forward 覆盖）

## 判定口诀（补充）

tmp 分支上取文件用 `git checkout master --` 前，先 `git log master -1 -- <文件>` 确认本地 master 已含该改动；未 commit 就 `git add` + `git commit` 到 master 再继续。
