# Python 备份脚本开发 — Windows 陷阱与模式

在 Windows 上用 Python 写 Hermes cron 备份脚本时的常见坑和正确模式。

## 为什么用 Python 而不是 bash

- Hermes cron 运行器不走 Git Bash 环境，`bash` 不一定在 PATH 中
- 加 bash 到 PATH 后重启 Hermes 也未必生效（cron 环境继承链不确定）
- Python 脚本无此依赖，更可靠

## 打包实现选择：`os.walk + tar.add` vs `subprocess GNU tar`

两种实现都跑得通，但行为不同：

| 实现 | 体积膨胀风险 | 权限错误处理 | 进度可见 | 推荐场景 |
|------|------------|------------|---------|---------|
| `os.walk` + `tar.add` 逐文件加 | 无（如果排除规则正确） | **整包中断**（Python 抛 PermissionError） | 差（只能拿到最终大小） | 需要精细 EXCLUDE_DIRS 控制的复杂项目 |
| `subprocess` GNU tar.exe | 无 | **跳过条目继续**（tar 退出码非0但部分包有效） | 中（tar 进度选项） | 大型工作区 / 容忍警告 |
| `Path.rglob("**/*")` + `tar.add` | ⚠️ **重复打包**（1935 文件 → 9326 条目，4× 膨胀） | 同上 | 差 | **绝不要用** |

**2026-08-24 实战教训**：`Documents/Hermes/scripts/backup-hermes-webdav.py` 用 `os.walk + tar.add`（不是 rglob），是 OK 的实现——但碰上 `.next/dev/lock` 这种 dev server 持有的文件句柄时，Python tarfile 直接抛 `PermissionError` 中断整包，**没有跳过选项**。如果改用 GNU tar.exe，同样情况会返回警告但继续打包（部分成功 vs 全部失败）。

**取舍**：
- 当前 `os.walk + tar.add` 实现保留，**但 EXCLUDE_DIRS 必须把 dev server 触及的所有派生目录全列上**（见下文 §EXCLUDE_DIRS 必查清单）
- 大型工作区（≥ 50GB）或 EXCLUDE 难以穷举时，建议改回 GNU tar.exe，让 PermissionError 降级为 warning

## MSYS2 路径转换

Git for Windows 的 GNU 工具（`tar.exe`, `bash.exe` 等）是 MSYS2 编译的，不接受 Windows 风格路径。
必须用 `to_msys()` 函数转换：
- 盘符 `C:` → `/c`
- 反斜杠 `\` → `/`
- 示例：`C:\Users\HMSJ\Documents` → `/c/Users/HMSJ/Documents`

## curl 上传模式

```python
CURL = "curl"  # Git for Windows 自带

# 创建远程目录（已存在则 405 忽略）
subprocess.run([
    CURL, "-s", "-u", auth, "-X", "MKCOL",
    f"{base_url}/", "-w", "  HTTP %{http_code}",
])

# 上传文件
result = subprocess.run([
    CURL, "-s", "-o", os.devnull, "-w", "%{http_code}",
    "-u", auth, "-T", str(archive),
    f"{base_url}/{remote_file}",
], capture_output=True, text=True)
if result.stdout.strip() in ("201", "204"):
    print("成功")
```

## Chrome CDP Profile 缓存排除

`chrome-cdp-profile` 是备份中体积最大的部分（~107M），其中可安全排除的缓存：

| 子目录 | 大小 | 说明 |
|--------|------|------|
| `optimization_guide_model_store/` | 43M | ML 模型，Chrome 自动重建 |
| `GrShaderCache/`, `ShaderCache/`, `GPUPersistentCache/` | ~10M | GPU 着色器缓存 |
| `Safe Browsing/` | 4.8M | 恶意网站 DB，自动更新 |
| `BrowserMetrics/`, `DeferredBrowserMetrics/` | ~4M | 统计数据 |
| 其他（`Crashpad/`, `extensions_crx_cache/` 等） | ~2M | 各类缓存 |

**保留 `Default/`**（~47M）含 cookie/登录态/扩展数据。如果不需要登录态持久化，可排除整个 `chrome-cdp-profile/`。

tar 排除写法：
```python
"--exclude=.hermes/chrome-cdp-profile/optimization_guide_model_store",
"--exclude=.hermes/chrome-cdp-profile/GrShaderCache",
# ... 或其他缓存目录
# 整个排除（不要登录态）：
"--exclude=.hermes/chrome-cdp-profile",
```

排除后效果：110M → 38M（保留 state.db + skills + Obsidian Vault + 配置）。

## Cron 超时

`no_agent: true` 脚本有 **120s 硬超时**。大体积上传可能超时，需：
- 严格控制打包体积（排除 chrome-cdp-profile 缓存后可从 110M 降到 38M）
- 如果上传慢，考虑增量备份而非全量快照

## EXCLUDE_DIRS 必查清单（2026-08-24 实战）

**根因规则**：备份用户数据，**不备可重装的程序本体**。dev server / 构建工具运行时持有的文件句柄会让 Python tarfile 整包中断——必须用 EXCLUDE_DIRS 把它们在源头排除。

**Windows + Node/Next/Rust/Python 项目必查**（任何 dev server 留过的痕迹）：

| 排除项 | 为什么 | 体积量级 |
|--------|-------|---------|
| `node_modules` | pnpm/npm/yarn 安装产物，`pnpm install` 重建 | 100MB ~ 数 GB |
| `.next` | Next.js 构建产物 + dev server 持有 `.next/dev/lock` | 100MB ~ 数 GB |
| `target` | Rust/cargo 构建产物 | 项目相关 |
| `dist` | Vite/Rollup 构建产物 | 项目相关 |
| `build` | 各种构建工具输出 | 项目相关 |
| `.turbo` | Turborepo 缓存 | 项目相关 |
| `.cache` | 各种工具缓存（gatsby/vite/eslint） | 项目相关 |
| `.parcel-cache` | Parcel 缓存 | 项目相关 |
| `__pycache__` | Python 字节码 | 小 |
| `.venv` / `venv` | Python 虚拟环境 | 大（500MB+） |
| `.pytest_cache` | pytest 缓存 | 小 |
| `.mypy_cache` | mypy 缓存 | 小 |
| `.gradle` / `build` | Java/Kotlin Gradle | 大 |
| `vendor` | Go/PHP 依赖（部分场景需保留） | 项目相关 |

**绝对不排除**（看似可重装但其实是项目产出）：

| 保留项 | 为什么不能排除 |
|--------|--------------|
| `.git` | git 历史是项目产出（commit/分支/tag），不可重建；131MB 量级值得保留 |
| `.gitignore` 跟踪的代码文件 | 用户已自己管理 |
| 任何 git tracked 文件 | `git checkout` 可恢复，但恢复后失去所有未提交修改——保留总没坏处 |

**审计方法**（改完 EXCLUDE_DIRS 必须实测，按用户偏好「不接受口头声称」）：

```python
import tarfile
with tarfile.open("backups/hermes-XXX.tar.gz", "r:gz") as tf:
    names = tf.getnames()

# 1. 应排除项 = 0
for bad in ["node_modules", ".next", "chrome-cdp-profile", "hermes-agent"]:
    count = sum(1 for n in names if f"/{bad}/" in n)
    print(f"[{'OK' if count == 0 else 'FAIL'}] {bad}: {count} 条目")

# 2. 应保留项 = 在
for good in [".git/HEAD", "scripts/backup-hermes-webdav.py"]:
    hit = any(n.endswith(good) for n in names)
    print(f"[{'OK' if hit else 'MISS'}] {good}")

# 3. 文件数对比：应该比改前少（排除生效）但不少于用户数据基线
print(f"总条目: {len(names)}")
```

**踩坑**：kill 一个后台跑着的 tarfile 备份会留半成品（100MB+ 损坏文件）在 backups/。跑测试时 kill 后必须 `rm -f` 清掉，否则下次脚本按保留策略判断时容易留垃圾。

## 多份备份脚本识别（同一台机器常见）

`backup-hermes-*.py` 可能有多份——精简版（LOCALAPPDATA）和全量版（Documents/Hermes/scripts）。**看日志签名**判断当前跑的哪份：

| 日志签名 | 脚本 | 打包内容 |
|---------|-----|---------|
| `[1/4] 打包 ... 打包完成: X MB (workspace=N文件, hermes=N文件)` | 全量版 | Documents/Hermes 工作区 + Hermes + Obsidian |
| `[1/4] 打包 ... 打包完成: X MB` (无 workspace=) | 精简版 | 仅 .hermes + state.db + Obsidian |
| `[Errno 13] Permission denied: '...'` | 全量版（Python tarfile） | 不会被精简版报（它走 GNU tar.exe） |

排查时第一件事 = `grep` 错误信息判断版本，再针对性修 EXCLUDE_DIRS 或 cron 任务参数。
