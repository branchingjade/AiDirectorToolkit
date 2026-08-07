---
name: hermes-backup
description: >
  将 Hermes 配置、技能、记忆、会话数据及 Obsidian Vault 备份到云存储（坚果云/OneDrive 等）。
  以 robocopy 增量同步为核心，覆盖 config/skills/memories/cron/state.db/Obsidian Vault。
  Trigger when: user asks to backup Hermes, migrate Hermes data, set up cloud sync,
  recover from lost data, or any mention of "备份" + Hermes.
---

# Hermes 云备份

将 Hermes 所有持久化数据备份到云存储目录，使用 robocopy 增量同步，只传输变化部分。

## 备份内容

| 数据 | 路径 | 说明 |
|------|------|------|
| Hermes 配置/技能/记忆/cron | `~/AppData/Local/hermes/` | 真实 HERMES_HOME（Windows） |
| 会话数据库 | `~/AppData/Local/hermes/state.db` | 468MB 级，压缩后 ~190MB |
| 工作区 | `~/Documents/Hermes/` | 含 git 历史，是用户的代码/创作产出 |
| Obsidian Vault | `~/Documents/KnowledgeBase/Obsidian Vault/` | Hermes 相关笔记 |
| Hindsight 记忆库 | `~/.pg0/instances/hindsight-embed-hermes/` | 内嵌 PostgreSQL（138MB 级，956+ 条记忆）——⚠️ **2026-08-07 实测不在任何备份脚本范围内**：`backup-hermes-webdav.py` 打包的是 `~/.hermes`（残留）+ Obsidian Vault + state.db，漏掉 `~/.pg0/`。修复方向：pg_dump 导出（连接方式见 `references/hindsight-memory-db.md`）或直接打包 `~/.pg0/`。 |

> **⚠️ `~/.hermes` 是残留目录，不是备份对象**（2026-08-04 实测）：Windows 上真实 HERMES_HOME 在 `~/AppData/Local/hermes`，`~/.hermes` 只有 21 字节占位 config.yaml、0 字节 state.db 和旧 .env。曾有一个备份脚本打包 `~/.hermes`，"成功"跑了 3.6MB（其中 3.5MB 是临时音频）——**备份脚本路径写对不等于备份有效**，必须抽查包内容验证范围。

**排除：** 工作区侧 `backups/`、`tools/`、`data/`、`.hermes/`、`.worktrees/`；Hermes 侧 `hermes-agent/`（3GB 源码）、`node/`、`lsp/`、`bin/`、`logs/`、`cache/`、`audio_cache/`、`checkpoints/`、`state-snapshots/`、`pets/`、`chrome-cdp-profile/`、`.curator_backups/`；文件级 `state.db-wal`、`*.log`、`*.lock`、`.temp_audio_b64.txt`。

## 步骤

### 1. 确认云盘路径

坚果云同步目录在 Nutstore SQLite 数据库中：
```
~/AppData/Roaming/Nutstore/db1/nutstore.db → sndconfig* 表 → localAbsPath
```
默认路径：`~/Nutstore/1/我的坚果云`

对其他云盘（OneDrive/Dropbox），直接用已知路径即可。

### 2. 运行备份脚本

直接执行技能自带的备份脚本：
```bash
bash "$(dirname "$(skill_view name='hermes-backup' file_path='scripts/backup-hermes.sh')")/scripts/backup-hermes.sh"
```
或将脚本复制到本地运行：
```bash
cp "$SKILL_DIR/scripts/backup-hermes.sh" ~/Documents/Hermes/scripts/
bash ~/Documents/Hermes/scripts/backup-hermes.sh
```

或手动 robocopy：
```bash
MSYS_NO_PATHCONV=1 robocopy \
  "$(cygpath -w ~/.hermes)" \
  "$(cygpath -w ~/Nutstore/1/我的坚果云/Hermes备份/.hermes)" \
  /MIR /NP /NDL /NFL /R:2 /W:3 \
  /XD logs cache __pycache__ .git \
  /XF "*.log" "*.tmp" "*.lock"
```

脚本自动处理增量同步和备份验证。

### 3. 设置定时备份（可选）

用 cronjob 每天自动备份：
```
cronjob action=create schedule="0 3 * * *" prompt="运行 backup-hermes.sh 脚本备份 Hermes 数据"
```

## 恢复

从云端恢复只需反向复制：
```bash
cp -r ~/Nutstore/1/我的坚果云/Hermes备份/.hermes ~/
cp ~/Nutstore/1/我的坚果云/Hermes备份/AppData/state.db ~/AppData/Local/hermes/
```

## Mode B — WebDAV 直传（curl）

适用于无本地同步文件夹的场景（如只用 WebDAV 密钥连接坚果云）。
凭据存放在 `~/.hermes/.webdav-cred`（chmod 600）：

```
WEBDAV_USER="branchingjade@qq.com"
WEBDAV_PASS="<应用密码>"
```

**Windows 推荐 Python 版**（`backup-hermes-webdav.py`），避免 bash-on-PATH 问题：
1. 用 Python `tarfile` 打包（2026-08-04 改版已修复重复打包问题——单层 `tar.add(fpath, arcname=...)` 逐个文件加，不用 `Path.rglob` 再遍历）
2. urllib PUT 上传（`urllib.request.Request(url, method="PUT")` + Basic auth，`req.data = f.read()`）
3. 本地保留最近 7 个备份

**分包设计（百度网盘 PUT 上限实测）**：单次 WebDAV PUT 阈值在 **202~338MB 之间**（145MB/202MB 成功，338MB 报 `errno: 10` → HTTP 405）。因此：
- 主包（工作区+配置，git 瘦身后 ~57MB）每天上传
- `state.db`（468MB 原始 → ~193MB 压缩）**独立分包上传**，只每周日（`datetime.now().weekday() == 6`）或 `--full` 参数手动强制
- 分包让每个文件都在成功阈值内，也避免主包膨胀

**git 历史瘦身直接缩小备份**（2026-08-04 实测）：工作区主包体积大头是 `.git`——曾经误提交的 alist.exe(110MB)/alist.zip(42MB) blob 永远留在历史里。用 `git filter-repo --force --path <路径> --invert-paths` 抹掉后 `.git` 从 114MB→25MB，主包从 145.8MB→56.7MB。**操作前必须 `cp -r .git .git.bak` 备份，且注意 filter-repo 会删除工作树所有 untracked 文件（先挪走需要的）**；无 remote 的本地仓库重写历史安全。

手动运行：
```bash
python3 ~/AppData/Local/hermes/scripts/backup-hermes-webdav.py            # 日常精简
python3 ~/AppData/Local/hermes/scripts/backup-hermes-webdav.py --full     # 强制含 state.db
```

设置定时备份（no_agent 模式）：
```
cronjob action=create schedule="0 8 * * *" name="Hermes WebDAV 备份"
  script="backup-hermes-webdav.py" no_agent=true deliver="origin"
```

也可以使用 bash 版（`backup-hermes-webdav.sh`），但需要确保 `bash` 在 Windows PATH 中（见 Pitfalls）。

详见 `references/webdav-nutstore.md`、`references/python-backup-pitfalls.md` 和 `references/baidu-webdav-migration.md`。

## Pitfalls

- **备份范围必须实测验证，不能只看脚本路径**：脚本"运行成功"≠备份有效。曾有一个 webdav 备份脚本打包 `~/.hermes` 残留目录，天天报"✅ 备份完成 5.0 MB"（其中 3.5MB 是临时音频），工作区仓库和真实 Hermes 数据全部漏备，用户以为有云备份实际是裸奔。**验证方法**：`tar -tzf <backup>.tar.gz | head` 抽查关键文件（`.env`、`memories/MEMORY.md`、`cron/jobs.json`、`workspace/.git/HEAD`）是否在包内；`du -sh` 对比打包前后预期体积；确认该排除的（`state.db` 日常、`tools/alist`、`hermes-agent/`）不在包内。
- **百度网盘 WebDAV 单次 PUT 上限 ~202-338MB**：超过阈值返回 `errno: 10`（百度 API 层拒绝，alist 表现为 HTTP 405，alist 日志 `failed put ... errno: 10`）。大文件（如 468MB 的 state.db）必须**压缩后独立分包上传**，或分卷。alist 百度网盘驱动日志位置：`tools/alist/data/log/log.log`。
- **`~/.hermes` ≠ 真实 HERMES_HOME**：Windows 上 `~/.hermes` 是残留（占位 config.yaml、0 字节 state.db），真实数据在 `~/AppData/Local/hermes`（4.3GB 级）。写备份/迁移脚本前先 `hermes config path` 确认，不要抄旧脚本里的路径假设。
- **Windows cron `.sh` 脚本：bash 必须在 PATH 中**：Hermes cron 运行器不走 Git Bash 环境。**推荐：改写为 Python 脚本**，调用 GNU tar（`C:\Program Files\Git\usr\bin\tar.exe`）打包、curl 上传，避免 bash 依赖。备选：将 `C:\Program Files\Git\bin` 加到用户 PATH 后重启 Hermes，但实测此方案不一定生效（cron 环境继承链不确定）。
- **Python `Path.rglob` 打包陷阱**：用 `tarfile` 遍历目录逐个 `tar.add()` 会导致文件重复打包（实测 1935 个不同文件 → 9326 个 tar 条目，体积膨胀 4 倍）。**正确做法**：用 `subprocess` 调用 GNU tar.exe 打包。
- **MSYS2 二进制路径格式（脚本内部）**：Git for Windows 的 GNU 工具（`tar.exe` 等）不接受 Windows 风格路径（`C:\\Users\\...`）。`subprocess` 调用时需转换为 MSYS 格式：`/c/Users/...`（`s.replace(chr(92), '/')`，盘符 `C:` → `/c`）。
- **MSYS 路径传递给 `python3` 时被错误转换**：在 `terminal()` 中执行 `python3 "/c/Users/..."` 时，MSYS 会将路径转换为 `C:\c\Users\...`（多余 `\c` 前缀），导致文件找不到。**正确做法**：使用正斜杠 Windows 风格路径 `"C:/Users/..."` 或 `python3 "C:/Users/..."`，MSYS 不会对含盘符的正斜杠路径做转换。`~/...` 展开也安全（bash 在传给 Python 前完成展开）。
- **Cron 脚本 120s 超时**：`no_agent: true` 脚本有 120s 硬超时。大体积备份（>200MB 上传）可能超时，需控制体积。
- **Cron job 脚本路径**：`script` 参数解析到 `~/AppData/Local/hermes/scripts/<文件名>`，不是 skill 目录。
- **robocopy 在 git-bash/MSYS 下路径转换**：必须设置 `MSYS_NO_PATHCONV=1` 并用 `cygpath -w` 转为 Windows 路径，否则 `/MIR` 等参数会被错误转换
- **robocopy 返回码**：1-7 均为成功（1=有文件复制，0=无变化），不要用 `set -e`，需手动检查 `$? -le 7`
- **WebDAV 中文路径**：curl 不自动 URL-encode，目录名用纯 ASCII 避免 400 错误
- **WebDAV 中文用户名认证**：curl `-u "中文:密码"` 在 bash/MSYS 环境 base64 编码错误 → 401。**正确做法**：Python 里 `base64.b64encode("用户名:密码".encode("utf-8"))`，curl 用 `-H "Authorization: Basic <b64>"` 替代 `-u`。
- **State.db 并发冲突**：备份期间 Hermes 运行中 state.db 被写入时 tar 报 `file changed as we read it`。重试通常成功，或挑空闲时段跑。
