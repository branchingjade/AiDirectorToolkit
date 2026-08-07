---
name: github
description: "Complete GitHub workflow: auth, repos, issues, PRs, and code review via gh CLI or REST API."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Authentication, Repositories, Pull-Requests, Issues, Code-Review, CI/CD, Git, gh-cli]
    related_skills: [codebase-inspection]
---

# GitHub — Complete Workflow Guide

Everything you need to work with GitHub: authentication, repository management, issues, pull requests, and code review. Each section shows `gh` CLI first, then `git` + `curl` fallback.

## Prerequisites

### Auth Detection (use at the start of any GitHub workflow)

```bash
# Check what's available
git --version
gh --version 2>/dev/null || echo "gh not installed"
gh auth status 2>/dev/null || echo "gh not authenticated"
```

Load the shared env setup script (handles token extraction from multiple sources):

```bash
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github/scripts/gh-env.sh"
```

Or inline:

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

# Extract owner/repo from git remote
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 1. Authentication

### Option A: GitHub Personal Access Token (most portable)

1. Create token at **https://github.com/settings/tokens** with scopes: `repo`, `workflow`, `read:org`
2. Configure git to store it:

```bash
git config --global credential.helper store
git ls-remote https://github.com/<username>/<any-repo>.git
# Enter username + token (not password) when prompted
```

3. Set identity:

```bash
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

### Option B: SSH Key

```bash
ssh-keygen -t ed25519 -C "email@example.com" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub
# Add to https://github.com/settings/keys
ssh -T git@github.com
# Optional: auto-rewrite HTTPS to SSH
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

### Option C: gh CLI

```bash
gh auth login              # Interactive browser login
echo "TOKEN" | gh auth login --with-token  # Headless
gh auth setup-git          # Configure git credentials through gh
gh auth status             # Verify
```

### Using the API Without gh

```bash
export GITHUB_TOKEN="<token>"
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `git push` asks for password | GitHub disabled password auth — use token or SSH |
| `Permission to X denied` | Token lacks `repo` scope — regenerate |
| `ssh: Connection refused` | Try SSH over HTTPS port 443: add `Port 443` + `Hostname ssh.github.com` to `~/.ssh/config` |
| Multiple accounts | Use SSH with different keys per host alias in `~/.ssh/config` |

### Adding Scopes to gh CLI Token

When an operation fails with "This API operation needs the 'X' scope", add the missing scope:

```bash
gh auth refresh -h github.com -s delete_repo,user
```

**⚠️ Pitfall: device flow blocks the conversation if run in foreground.** The `gh auth refresh` device flow prints a one-time code and waits for the user to visit `https://github.com/login/device` and authorize. Running it in foreground freezes the terminal until either the user completes authorization or 60s timeout — the agent can't poll it and the user can't see the code in time.

**Correct approach: run as background process, poll for the code, tell the user:**

```bash
# 1. Start in background
terminal(command="gh auth refresh -h github.com -s delete_repo,user", background=true, notify_on_complete=true)

# 2. Poll for the one-time code
process(action="poll", session_id="proc_xxx")

# 3. Read the code from output, tell the user: "打开 https://github.com/login/device，输入 XXXX-XXXX"
# 4. Wait for the completion notification
```

Do NOT retry `gh auth refresh` in foreground — it will time out every time if the user isn't watching the terminal output in real time.

---

## 2. Repository Management

### Clone

```bash
git clone https://github.com/owner/repo-name.git
git clone --depth 1 https://github.com/owner/repo-name.git  # Shallow
gh repo clone owner/repo-name                                # With gh
```

### Create

```bash
gh repo create my-project --public --clone
gh repo create my-org/my-project --private --description "A tool" --license MIT
# From existing local dir:
cd /path/to/project && gh repo create my-project --source . --public --push
```

With curl:
```bash
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{"name":"my-project","private":false,"auto_init":true,"license_template":"mit"}'
```

### Rename

```bash
gh repo rename new-name --yes
```

API fallback (works even when `gh repo rename` isn't available):
```bash
gh api -X PATCH repos/$OWNER/$REPO -f name=new-name
```

After rename, update local remote immediately:
```bash
git remote set-url origin https://github.com/$OWNER/new-name.git
git remote -v  # verify
```

GitHub auto-redirects old URLs, but updating avoids future confusion.

**Post-rename cleanup checklist** (do ALL of these):
```bash
# 1. Update local git remote
git remote set-url origin https://github.com/$OWNER/new-name.git
git remote -v  # verify
```
- **Hermes memory**: search for old repo name with `memory` tool, replace any entries
- **External skill sources**: if old repo is a skill tap, update the URL in external-skill-sources config
- **Cron jobs / scripts**: check for hardcoded repo URLs
- **Local directory name**: rename to match new repo name (see pitfall below)

> **⚠️ Windows pitfall — directory rename locked**: When the current working directory is the repo being renamed, `mv` fails with "Device or resource busy" / "Permission denied". Workaround: copy then delete.
> ```bash
> cp -r /path/to/OldName /path/to/NewName && rm -rf /path/to/OldName
> ```
> Then switch your Hermes project to the new directory path.

### Fork

```bash
gh repo fork owner/repo-name --clone
gh repo sync $GH_USER/repo-name  # Keep fork in sync
```

### Settings & Configuration

```bash
gh repo edit --description "Updated" --visibility public
gh repo edit --enable-auto-merge
gh repo edit --add-topic "ml,python"
```

### Branch Protection

```bash
curl -s -X PUT -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \
  -d '{"required_status_checks":{"strict":true,"contexts":["ci/test"]},
       "required_pull_request_reviews":{"required_approving_review_count":1}}'
```

### Secrets (GitHub Actions)

```bash
gh secret set API_KEY --body "value"
gh secret list
gh secret delete API_KEY
# curl requires encryption with repo public key — see references/github-api-cheatsheet.md
```

### Releases

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release create v2.0.0-rc1 --draft --prerelease
gh release list
gh release download v1.0.0 --dir ./downloads
```

### GitHub Actions Workflows

```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID> --failed
gh workflow run ci.yml --ref main
```

### Gists

```bash
gh gist create script.py --public --desc "Useful script"
gh gist list
```

---

## 3. Issues

### View & Search

```bash
gh issue list --state open --label "bug"
gh issue list --assignee @me
gh issue list --search "authentication error" --state all
gh issue view 42
```

With curl:
```bash
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&per_page=20"
```

### Create

```bash
gh issue create \
  --title "Login redirect ignores ?next= parameter" \
  --body "## Description\n..." \
  --label "bug,backend" --assignee "username"
```

See `templates/bug-report.md` and `templates/feature-request.md` for body templates.

### Manage Labels, Assignment, Comments

```bash
gh issue edit 42 --add-label "priority:high,bug"
gh issue edit 42 --remove-label "needs-triage"
gh issue edit 42 --add-assignee @me
gh issue comment 42 --body "Investigated — root cause in auth middleware."
gh issue close 42 --reason "not planned"
gh issue reopen 42
```

### Triage Workflow

1. `gh issue list --label "needs-triage" --state open`
2. Read and categorize each issue
3. Apply labels and priority
4. Assign if owner is clear
5. Comment with triage notes if needed

### Bulk Operations

```bash
gh issue list --label "wontfix" --json number --jq '.[].number' | \
  xargs -I {} gh issue close {} --reason "not planned"
```

### Link Issues to PRs

Use `Closes #42` / `Fixes #42` / `Resolves #42` in PR body.

Create branch from issue:
```bash
gh issue develop 42 --checkout
```

---

## 4. Pull Requests

### Branch & Commit

```bash
git fetch origin && git checkout main && git pull origin main
git checkout -b feat/add-user-auth
# ... make changes ...
git add src/auth.py tests/test_auth.py
git commit -m "feat: add JWT-based user authentication"
```

Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `ci:`, `chore:`, `perf:`.
See `references/conventional-commits.md` for details.

### Push & Create PR

```bash
git push -u origin HEAD
gh pr create --title "feat: add JWT auth" --body "## Summary\n...\nCloses #42"
# Options: --draft, --reviewer user1,user2, --label "enhancement", --base develop
```

With curl:
```bash
BRANCH=$(git branch --show-current)
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{\"title\":\"feat: add JWT auth\",\"body\":\"Closes #42\",\"head\":\"$BRANCH\",\"base\":\"main\"}"
```

See `templates/pr-body-bugfix.md` and `templates/pr-body-feature.md` for PR body templates.

### Monitor CI

```bash
gh pr checks           # One-shot
gh pr checks --watch   # Poll until done
```

With curl:
```bash
SHA=$(git rev-parse HEAD)
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs
```

See `references/ci-troubleshooting.md` for CI failure diagnosis.

### Auto-Fix CI Failures

1. `gh run list --branch $(git branch --show-current)`
2. `gh run view <RUN_ID> --log-failed`
3. Fix code with `patch` / `write_file`
4. `git add . && git commit -m "fix: ..." && git push`
5. Re-check CI status
6. Repeat up to 3 times, then ask user

### Merge

```bash
gh pr merge --squash --delete-branch
gh pr merge --auto --squash --delete-branch  # Auto-merge when checks pass
```

---

## 5. Code Review

### Pre-Push Review (Local Changes)

```bash
git diff main...HEAD --stat        # Big picture
git diff main...HEAD               # Full diff
git diff main...HEAD -- src/auth.py  # Specific file
```

Check for common issues:
```bash
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME\|debugger"
git diff main...HEAD | grep -in "password\|secret\|api_key\|token.*=\|private_key"
```

### Review Output Format

```
## Code Review Summary

### Critical
- **src/auth.py:45** — SQL injection: user input passed directly to query.

### Warnings
- **src/models/user.py:23** — Password stored in plaintext.

### Suggestions
- **src/utils/helpers.py:8** — Duplicates logic in src/core/utils.py:34.

### Looks Good
- Clean separation of concerns in middleware layer
```

### PR Review on GitHub

```bash
gh pr view 123
gh pr diff 123
gh pr checkout 123     # Check out locally for full review
```

Leave inline comments:
```bash
# Via gh API
HEAD_SHA=$(gh pr view 123 --json headRefOid --jq '.headRefOid')
gh api repos/$OWNER/$REPO/pulls/123/comments --method POST \
  -f body="Use parameterized queries." -f path="src/auth.py" \
  -f commit_id="$HEAD_SHA" -f line=45 -f side="RIGHT"
```

Submit formal review:
```bash
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
gh pr review 123 --comment --body "Some suggestions, nothing blocking."
```

See `references/review-output-template.md` for the full review template.

### Review Checklist

- **Correctness:** Does it work? Edge cases handled? Error paths?
- **Security:** No hardcoded secrets, input validation, no SQL injection/XSS
- **Quality:** Clear naming, no unnecessary complexity, DRY
- **Testing:** New code paths tested? Happy path + error cases?
- **Performance:** No N+1 queries, appropriate caching, no blocking in async
- **Documentation:** Public APIs documented, non-obvious logic commented

---

## 6. Profile Page Customization

GitHub 个人主页由以下层级组成（从上到下）：

| 层级 | 说明 | 修改方式 |
|------|------|---------|
| 左侧个人信息栏 | 头像、Bio（160字）、公司/位置/链接 | Settings → Public profile |
| Profile README | `username/username` 仓库的 README.md，渲染在置顶仓库上方 | 创建同名仓库 |
| Pinned 仓库 | 手动置顶最多 6 个仓库 | 主页点 "Customize your pins"（⚠️ 无公开 API） |
| GitHub Pages | `username.github.io` 独立静态网站 | 创建对应仓库 |

### ⚠️ Pitfall 1：先出示例，不要直接动手改

GitHub 主页属于**对外展示页面**，用户的审美偏好无法预判。操作铁律：

1. **先说明结构** — 解释 GitHub 主页有哪些可定制的层级（用户可能不了解 profile README / Pinned / Pages 的区别）
2. **让用户选方向** — clarify 问风格/内容偏好
3. **先出预览，确认后再 push** — 用本地 HTML 文件模拟 GitHub 主页效果，用户点头了再动手
4. **不要未经确认就创建仓库并推送** — 事后删仓库需要 `delete_repo` scope，比创建麻烦得多

### 📋 标准工作流

```
1. 询问用户想装修哪些层级
2. 如果用户不确定 → 先解释 GitHub 主页原理（5层结构）
3. clarify 选风格/方向
4. 构建本地 HTML 预览（仿 GitHub 暗色主题），包含 Bio/置顶/贡献图等
5. 用户确认 → 执行修改
```

### 🔧 可程序化操作的命令

```bash
# 更新 Bio（需要 user scope，见 Section 1 的 gh auth refresh）
gh api -X PATCH user -f bio="新 Bio 内容（最多 160 字符）"

# Pinned 仓库
# ⚠️ GitHub 没有公开 API 可以设置置顶仓库（GraphQL 无对应 mutation）
# 只能在 GitHub 网页端操作：主页 → Customize your pins → 勾选仓库
```

### ⚠️ Pitfall 2：Pinned 仓库无 API

`pinnableItems` GraphQL 查询可以读取置顶列表，但没有对应的 mutation 可以写入。`gh repo`、REST API、GraphQL mutation 均不支持。唯一途径：用户手动在网页端操作。

---\n\n## Quick Reference

| Action | gh | git + curl |
|--------|-----|-----------|
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name` | `curl POST /user/repos` |
| Rename repo | `gh repo rename name` | `gh api -X PATCH repos/o/r -f name=n` |
| Fork | `gh repo fork o/r` | `curl POST /repos/o/r/forks` |
| List issues | `gh issue list` | `curl GET /repos/o/r/issues` |
| Create issue | `gh issue create ...` | `curl POST /repos/o/r/issues` |
| Create PR | `gh pr create ...` | `curl POST /repos/o/r/pulls` |
| View PR diff | `gh pr diff N` | `git diff main...HEAD` |
| Approve PR | `gh pr review N --approve` | `curl POST .../reviews` |
| Merge PR | `gh pr merge --squash` | `curl PUT .../pulls/N/merge` |
| Set secret | `gh secret set KEY` | `curl PUT .../actions/secrets/KEY` |
| Create release | `gh release create v1.0` | `curl POST .../releases` |
| Rerun CI | `gh run rerun ID` | `curl POST .../actions/runs/ID/rerun` |

## Support Files

- `scripts/gh-env.sh` — Auth detection and env setup script
- `references/github-api-cheatsheet.md` — Full API endpoint reference
- `references/github-profile-preview-template.html` — HTML 模板，本地预览 GitHub 主页效果
- `references/ci-troubleshooting.md` — CI failure diagnosis guide
- `references/conventional-commits.md` — Commit message format guide
- `references/review-output-template.md` — Review output template
- `templates/bug-report.md` — Issue body template for bugs
- `templates/feature-request.md` — Issue body template for features
- `templates/pr-body-bugfix.md` — PR body template for bug fixes
- `templates/pr-body-feature.md` — PR body template for features
