# Python 备份脚本开发 — Windows 陷阱与模式

在 Windows 上用 Python 写 Hermes cron 备份脚本时的常见坑和正确模式。

## 为什么用 Python 而不是 bash

- Hermes cron 运行器不走 Git Bash 环境，`bash` 不一定在 PATH 中
- 加 bash 到 PATH 后重启 Hermes 也未必生效（cron 环境继承链不确定）
- Python 脚本无此依赖，更可靠

## 正确模式：subprocess 调用 GNU tar

**不要**用 Python `tarfile` 模块的 `rglob("*")` 遍历目录逐个 `tar.add()`。
实测会导致文件重复打包：1935 个不同文件 → 9326 个 tar 条目，体积膨胀 4 倍。

**正确做法：** `subprocess` 调用 Git for Windows 自带的 GNU tar.exe：

```python
import subprocess
from pathlib import Path

HOME = Path.home()
TAR = r"C:\Program Files\Git\usr\bin\tar.exe"

def to_msys(p: Path) -> str:
    """C:\Users\HMSJ\... -> /c/Users/HMSJ/..."""
    s = str(p.resolve())
    if len(s) > 1 and s[1] == ":":
        s = "/" + s[0].lower() + s[2:].replace(chr(92), "/")
    return s

subprocess.run([
    TAR, "-czf", to_msys(ARCHIVE),
    "-C", to_msys(HOME),
    "--exclude=.hermes/logs",
    "--exclude=.hermes/cache",
    "--exclude=*.log",
    "--exclude=*.tmp",
    "--exclude=.hermes/.webdav-cred",
    "--exclude=.obsidian",
    ".hermes",
    "AppData/Local/hermes/state.db",
    "Documents/KnowledgeBase/Obsidian Vault",
], check=True)
```

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
