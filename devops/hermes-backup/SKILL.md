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

### 从本地备份 tar 恢复误删文件（2026-08-12 实测）

`backup-hermes-webdav.py` 除上传 WebDAV 外，**本地 `~/Documents/Hermes/backups/` 也保留最近 7 个 `hermes-<日期>_<时间>.tar.gz` 完整工作区快照**（含全部 untracked 文件）——误删正式工具/文件时先查这里，通常当天早上的包就有删除前的版本。

恢复步骤：
1. **选包**：`ls -la backups/` 找删除之前的包（cron 8:30 跑备份 → 删除发生在当天上午之后的，用当天 8:30 的包；跨天用最近一次）
2. **先确认文件在包内**：`tar -tzf <包> | grep 文件名`（列出即可，不一定要解压）
3. **提取**——⚠️ 用 Python tarfile 提取单文件，不要用 bash tar 解包：
   ```python
   import tarfile, os
   with tarfile.open(TAR, 'r:gz') as tf:
       data = tf.extractfile('workspace/scripts/xxx.py').read()
       open(os.path.join(DEST, 'xxx.py'), 'wb').write(data)
   ```
   - **bash `tar -xzf` 在 MSYS 下会坑**：`/tmp/backup-restore` 这类路径 bash 和 Python 各解释各的（bash 的 /tmp ≠ Python 的 /tmp），`-C` 目标目录报 "Cannot open"；直接用 Python 提取到 Windows 风格目标路径最稳。注意：Python tarfile 打包有 rglob 重复条目坑（见 Pitfalls），但**提取单文件 `extractfile()` 是另一回事，可靠**——两个坑不要混淆。
   - **个别备份包会损坏**（gzip: unexpected end of file / "Compressed file ended before end-of-stream marker"——打包时被中断或打包期间文件变化）：`tarfile.open` 报错就换相邻时间点的包，不要死磕一个包（实测 08:32 包坏、08:48 包完好）。
4. **验证恢复**：字节数对比（`wc -c`）+ `python -m py_compile` 语法检查
5. **防复发**：恢复的正式工具立即 `git add` 纳入追踪——被误删的根因往往是它们从未进过 git（untracked 文件在清理白名单里容易被漏掉）

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

## 跨设备迁移（新设备配置 Hermes）

用户在多台设备间迁移 Hermes 时（SteamOS/Mac/新 Windows），**只迁移跨平台通用资产，Windows 专属一律排除**（计划任务守护脚本 .ps1/.cmd/gateway_watchdog.py、STT local_command、Clash 代理、源码本地补丁、cron 内嵌 Windows 路径）。完整自包含迁移提示词模板（可整块粘贴给新设备 Hermes 执行）：`templates/hermes-migration-prompt.md`。

### 实际在用的 WebDAV 端点（2026-08-15 查证）

`backup-hermes-webdav.py` 当前走 **alist → 百度网盘**（不是坚果云）：

| 项 | 值 |
|---|---|
| Base URL | `http://<alist-host>:5244/dav/百度网盘/hermes-backup`（中文路径可写，或 URL 编码 `%E7%99%BE%E5%BA%A6%E7%BD%91%E7%9B%98`） |
| 用户名 | `妖玉` |
| 密码 | `Huan1120`（脚本内 base64 硬编码：`base64.b64encode("妖玉:Huan1120")`） |
| 局域网访问 | alist 监听 `0.0.0.0:5244`，同网设备用 `http://192.168.1.208:5244/...` |
| 跨网访问 | Tailscale `http://100.78.192.8:5244/...` |
| 备份文件 | `hermes-YYYY-MM-DD_HH-MM-SS.tar.gz`（保留最近 7 份） |

⚠️ 中文用户名 curl `-u` 在 MSYS 下 base64 编码错 → 401，必须 Python 预编码 Basic 头（见 Pitfalls）。新设备拉最新备份：先 LIST 目录解析文件名（grep `hermes-[0-9_-]+\.tar\.gz` 排序取尾），再 GET 下载。

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
