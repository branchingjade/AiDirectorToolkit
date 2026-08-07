---
name: alist-setup
description: 在 Windows 上安装配置 alist，挂载百度网盘为 WebDAV。触发词：alist、百度网盘 WebDAV、alist 配置、挂载网盘。
---

# alist Windows 搭建

alist 是一个支持多存储后端的文件列表程序，可将百度网盘等云存储挂载为本地 WebDAV。

## 安装

```bash
# 获取最新版本号
VER=$(curl -sL "https://api.github.com/repos/AlistGo/alist/releases/latest" | grep -oP '"tag_name":\s*"\K[^"]+')

# 下载 Windows amd64 版本
curl -sL "https://github.com/AlistGo/alist/releases/download/$VER/alist-windows-amd64.zip" -o alist.zip
unzip -o alist.zip
```

推荐安装路径：`~/Documents/Hermes/tools/alist/`

## 初始化

```bash
cd <alist目录>
./alist.exe admin random
```

输出 admin 用户名和初始密码。**记下密码**——除非重置，否则不会再次显示。

默认端口：5244，WebDAV 路径：`/dav`

## 启动

```bash
./alist.exe server
```

验证：`curl -s http://localhost:5244/api/public/settings`

## 添加百度网盘存储

### 1. 获取 refresh token

百度网盘驱动需要 refresh token。获取方式：

① 打开百度 OAuth 授权页（`redirect_uri=oob` 方式）：
```
https://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id=hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf&redirect_uri=oob&scope=basic,netdisk
```
② 用户登录百度账号并授权  
③ 页面显示授权码（authorization code）  
④ 用授权码换 refresh token：

```bash
curl -s "https://openapi.baidu.com/oauth/2.0/token" \
  -d "grant_type=authorization_code" \
  -d "code=<授权码>" \
  -d "client_id=hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf" \
  -d "client_secret=YH2VpZcFJHYNnV6vLfHQXDBhcE7ZChyE" \
  -d "redirect_uri=oob"
```

返回的 `refresh_token` 即 alist 所需。

### 2. 通过 Web 管理页添加

访问 `http://localhost:5244/@manage` → 登录 → 存储 → 添加 → 选择"百度网盘"。

关键字段：

| 字段 | 值 | 说明 |
|------|-----|------|
| 显示文件夹名称 | `百度网盘` | 挂载路径，唯一 |
| 刷新令牌 | `<refresh_token>` | 必填 |
| 根文件夹路径 | `/` | 默认根目录 |
| 客户端ID | `hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf` | 默认即可 |
| 客户端密钥 | `YH2VpZcFJHYNnV6vLfHQXDBhcE7ZChyE` | 默认即可 |
| 自定义破解ua | `netdisk` | 默认即可 |
| 下载代理 | 302 重定向 | 直链下载用 |

其他字段保持默认，点击"添加"。

### 3. 通过 API 添加（推荐 Python，避免编码问题）

**必须用 Python `urllib` 而非 curl**——bash 中 curl 传中文字符（用户名、路径）会编码错误导致 API 拒绝。

```python
import json, urllib.request

# 登录
data = json.dumps({"username": "admin", "password": "<密码>"}).encode("utf-8")
req = urllib.request.Request("http://localhost:5244/api/auth/login", data=data,
    headers={"Content-Type": "application/json", "Accept": "application/json"})
token = json.loads(urllib.request.urlopen(req).read())["data"]["token"]

# 创建存储
storage = {
    "mount_path": "/百度网盘",
    "order": 0,
    "driver": "BaiduNetdisk",
    "cache_expiration": 30,
    "webdav_policy": "native_proxy",
    "web_proxy": False,
    "addition": json.dumps({
        "refresh_token": "<refresh_token>",
        "root_folder_path": "/",
        "order_by": "name", "order_direction": "asc",
        "download_api": "official",
        "client_id": "hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf",
        "client_secret": "YH2VpZcFJHYNnV6vLfHQXDBhcE7ZChyE",
        "custom_ua": "netdisk",
        "upload_thread": "3",
        "use_dynamic_upload_api": True,
        "custom_upload_part_size": 0
    })
}
req2 = urllib.request.Request("http://localhost:5244/api/admin/storage/create",
    data=json.dumps(storage).encode("utf-8"),
    headers={"Content-Type": "application/json", "Authorization": token})
print(json.loads(urllib.request.urlopen(req2).read()))
```

修改全局设置同理：
```python
# 关签名、开索引
api("/api/admin/setting/save", method="POST",
    body=[{"key": "sign_all", "value": "false"},
          {"key": "allow_indexed", "value": "true"}])
```

## ⚠️ Windows WebDAV 兼容性（关键步骤）

### WebDAV 策略必须改

默认策略 **"302 重定向"** 会导致 Windows 映射网络驱动器报 **"Method Not Allowed"**。

**每个存储**添加后必须将 WebDAV 策略改为 **"本地代理"**（native_proxy）：

- 管理后台 → 存储 → 编辑存储 → WebDAV 策略 → 选 "本地代理" → 保存
- 通过 API 创建时加 `"webdav_policy":"native_proxy"`

选项对照：

| 策略 | alist 选项 | API 值 | Windows 兼容 |
|------|-----------|--------|-------------|
| 302 重定向 | 默认 | `302_redirect` | ❌ Method Not Allowed |
| 使用代理地址 | — | `proxy` | ⚠️ 部分 |
| 本地代理 | ✅ 选这个 | `native` | ✅ 正常 |

### 启用 Windows WebClient Basic 认证

**以管理员身份运行 PowerShell**：

```powershell
Set-Service WebClient -StartupType Automatic
Start-Service WebClient
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\WebClient\Parameters' -Name 'BasicAuthLevel' -Value 2 -Type DWord -Force
```

- `BasicAuthLevel=2` 允许 HTTP Basic 认证（默认只允许 HTTPS）
- 必须管理员权限，普通终端报 `PermissionDenied`

## WebDAV 访问

- 地址：`http://localhost:5244/dav`
- 用户名：`admin`
- 密码：alist admin 密码（或在用户管理中创建专用 WebDAV 用户）
- Windows 挂载：映射网络驱动器 `http://localhost:5244/dav` 或 RaiDrive

## 开机自启

在 `C:\Users\<用户名>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\` 创建 `alist.vbs`：

```vbs
' alist WebDAV auto-start
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\<用户名>\Documents\Hermes\tools\alist"
WshShell.Run "C:\Users\<用户名>\Documents\Hermes\tools\alist\alist.exe server", 0, False
```

第 2 个参数 `0` = 隐藏窗口运行。

## Windows WebDAV 客户端替代方案

即使策略改为"本地代理"并配置了 BasicAuth，Windows 原生 WebDAV 映射仍可能失败（`GET /dav/` 返回 405）。**推荐 RaiDrive**（免费）：

1. 下载：https://www.raidrive.com/download
2. 添加 → NAS → WebDAV，填 localhost:5244，路径 `/dav`，alist 账号密码
3. 支持开机自动挂载，比 Windows 原生稳定

## 通过 alist WebDAV 做备份

将文件打包后直接 PUT 到 alist WebDAV，利用百度网盘做远端存储。

### Python tarfile（避免 MSYS tar 路径问题）

Windows 上 GNU tar（Git Bash 自带）会尝试自动转换 Windows 路径 → MSYS 路径，导致 `C:\Users\...` 被解析为 `C:Users...` 然后连接失败。**用 Python 内置 `tarfile` 替代**：

```python
import tarfile, gzip, os
from pathlib import Path

with gzip.open("archive.tar.gz", "wb") as gz:
    with tarfile.open(fileobj=gz, mode="w|") as tar:
        for root, dirs, files in os.walk(str(Path.home() / ".hermes")):
            rel = os.path.relpath(root, str(Path.home()))
            # os.walk 的 dirs 在原地修改可控制深度
            for name in files:
                fpath = os.path.join(root, name)
                arcname = os.path.join(rel, name).replace("\\", "/")
                tar.add(fpath, arcname=arcname)
```

### WebDAV PUT 上传（中文路径需 URL 编码）

alist 挂载的百度网盘路径含中文（如 `/百度网盘`），URL 中的中文必须 `urllib.parse.quote()` ：

```python
import urllib.request, urllib.parse, base64

base = f"http://localhost:5244/dav/{urllib.parse.quote('百度网盘')}"
url = f"{base}/archive.tar.gz"
auth = base64.b64encode(f"用户名:密码".encode()).decode()

req = urllib.request.Request(url, method="PUT")
req.add_header("Authorization", f"Basic {auth}")
with open("archive.tar.gz", "rb") as f:
    req.data = f.read()
with urllib.request.urlopen(req) as resp:
    print(f"HTTP {resp.status}")  # 201/204=成功
```

### 自动拉起 alist

备份脚本中检查并启动 alist（幂等）：

```python
import subprocess, time, urllib.request

ALIST_EXE = r"C:\Users\HMSJ\Documents\Hermes\tools\alist\alist.exe"
ALIST_DATA = r"C:\Users\HMSJ\Documents\Hermes\tools\alist\data"

# 检查是否运行
try:
    urllib.request.urlopen("http://localhost:5244/api/public/settings", timeout=5)
except:
    subprocess.Popen([ALIST_EXE, "server", "--data", ALIST_DATA],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(15):
        time.sleep(2)
        try:
            urllib.request.urlopen("http://localhost:5244/api/public/settings", timeout=5)
            break
        except:
            pass
```

## 陷阱

### WebDAV URL 中文路径编码

alist WebDAV 路径含中文时，URL 非 ASCII 部分必须 `urllib.parse.quote()`，否则 Python `urllib.request` 报 `'ascii' codec can't encode`：

```python
# ❌ 报错
url = "http://localhost:5244/dav/百度网盘/file.tar.gz"

# ✅ 正确
url = f"http://localhost:5244/dav/{urllib.parse.quote('百度网盘')}/file.tar.gz"
```

### bash/curl 传中文 → API 拒绝

在 bash 中用 curl 传中文 JSON（用户名如"妖玉"、挂载路径如"/百度网盘"）会编码错误，导致 `username or password is incorrect` 或 API 返回 HTML。**必须用 Python `urllib` + `encode("utf-8")` 做所有含中文的 API 调用。**

### WebDAV curl -u 中文 → 401（编码幽灵）

`curl -u 妖玉:密码` 在 MSYS/bash 中对中文用户名编码错误，始终返回 401——但 WebDAV 本身是好的。**验证用 explicit base64**：

```bash
curl -H "Authorization: Basic $(echo -n '妖玉:密码' | base64)" ...
```

**Windows 映射网络驱动器不受此影响**——Windows 凭据系统正确处理 UTF-8 Basic Auth。

### `admin set` 改密码后需重启 alist（v3.9.0+ 必须先停服）

**v3.9.0+ 必须先停止 alist 再运行 `admin set`**，否则命令尝试通过 API 清缓存时可能失败，且运行的 server 会锁定数据库文件：

```bash
# 1. 停服（用 PowerShell，避免 MSYS bash 中 taskkill 的 /F 路径转义问题）
powershell -Command "Stop-Process -Name alist -Force"
# 2. 删除 WAL 文件（避免读到脏数据）
rm -f data/data.db-wal data/data.db-shm
# 3. 重置密码
./alist.exe admin set <新密码> --data "<data目录>"
# 4. 重启
./alist.exe server --data "<data目录>"
```

`admin set` 更新 `x_users` 表的 `pwd_hash` 和 `salt` 列（SHA256+盐），**`password` 列始终为空**。不要被空的 `password` 列误导。

**⚠️ 命令输出"已更新"不代表真的写入了正确数据库——必须验证：**

```python
import sqlite3, os
data_dir = r"C:\Users\HMSJ\Documents\Hermes\tools\alist\data"
# 先删 WAL 确保读到最新提交的数据
for f in ["data.db-wal", "data.db-shm"]:
    p = os.path.join(data_dir, f)
    if os.path.exists(p): os.remove(p)
db = sqlite3.connect(os.path.join(data_dir, "data.db"))
db.execute("SELECT id, username, pwd_hash, salt FROM x_users").fetchall()
```

如果 username 或 pwd_hash 没变，说明 `admin set` 写入了错误的数据库——见下方 `db_file` 路径陷阱。

更新已有的存储（edit）时 `POST /api/admin/storage/save` 可能返回 HTML 而非 JSON，即使带了 `Accept: application/json`。但 `storage/create` 正常。更新存储推荐用浏览器管理后台而非 API。

### 百度 OAuth `redirect_uri=oob` 的授权码是一次性的

换取 token 后授权码即失效。refresh token 需妥善保存。

### alist v3 登录 API 路径

登录 API 是 `/api/auth/login`（不是 `/api/admin/login`），需同时带 `Content-Type: application/json` 和 `Accept: application/json`，否则返回 HTML。

### alist 管理页可能没有"获取令牌"按钮

v3.61.0 的百度网盘驱动表单可能不包含内置 OAuth 按钮，需手动走 OAuth 流程获取 token。

### curl 用 `curl.exe` 不要用 PowerShell 别名

PowerShell 中 `curl` 是 `Invoke-WebRequest` 的别名，行为不同。**必须用 `curl.exe`**。

### Windows WebDAV 302 重定向 → Method Not Allowed

默认策略 "302 重定向" 导致 Windows 映射网络驱动器失败。**添加存储后必须立即改为 "本地代理"**。这是最常见的配置遗漏。

### WebClient 服务配置需要管理员权限

`Set-Service` 和注册表 `HKLM` 修改必须以管理员身份运行 PowerShell，普通终端会报 `PermissionDenied`。

### `db_file` 路径陷阱：`data\\data.db` 创建嵌套目录

`config.json` 中的 `db_file` 是相对路径，以 config 文件所在目录为基准解析。如果设为 `"data\\data.db"`，实际解析为 `<data_dir>/data/data.db`（嵌套在 `data/data/` 子目录下），而非预期的 `<data_dir>/data.db`。

**后果**：`alist admin set` 命令看似成功（"admin user has been updated"），但写入的是错误的数据库文件。alist server 启动后也读取错误的数据库，导致：
- 存储列表为空（storage not found）
- 登录失败（username or password is incorrect）
- API 返回 `"failed get storage: storage not found; please add a storage first"`

**修复**：将 `db_file` 从 `"data\\\\data.db"` 改为 `"data.db"`，然后删除嵌套目录下的错误数据库：

```python
import json, os
config_path = r"C:\Users\HMSJ\Documents\Hermes\tools\alist\data\config.json"
with open(config_path) as f:
    config = f.read()
config = config.replace('"db_file": "data\\\\data.db"', '"db_file": "data.db"')
with open(config_path, "w") as f:
    f.write(config)
# 删除错误数据库
os.remove(r"C:\Users\HMSJ\Documents\Hermes\tools\alist\data\data\data.db")
```

**检测方法**：如果 `data/` 目录下同时存在 `data.db` 和 `data/data.db` 两个文件，且大小差异大（131KB vs 4KB），说明存在路径错误。另有 `~/Documents/Hermes/data/data.db` 也需检查。

### WAL 文件会隐藏数据库真实状态

SQLite WAL（Write-Ahead Logging）模式下，修改先写入 `data.db-wal`，不会立即合并到 `data.db`。**在 alist 运行时查询数据库可能看不到刚写入的变更**。

执行 `admin set` 后验证时，必须：
1. 先停掉 alist（让 WAL checkpoint 到主文件）
2. 或手动删除 WAL 文件强制从主文件读取

```bash
rm -f data/data.db-wal data/data.db-shm
```

如果不删 WAL，sqlite3 可能读到旧数据，误判 `admin set` 失败。

### 百度网盘驱动 `custom_ua` 字段名

alist 内部存储的字段名为 `custom_crack_ua`，但 API 传 `custom_ua` 也会被接受。UI 显示为"自定义破解ua"。

### taskkill 在 bash 中语法错误

`taskkill /F /IM alist.exe` 中 `/F` 被 MSYS bash 解析为 Unix 路径。改用 PowerShell：

```bash
powershell -Command "Stop-Process -Name alist -Force"
```

### 利用已登录浏览器操作 alist API

当用户浏览器已登录 alist，用 Kimi WebBridge 的 `evaluate()` 直接调 API，避免重复传密码：

```js
const token = localStorage.getItem('token');
await fetch('/api/fs/mkdir', {method:'POST', headers:{'Content-Type':'application/json','Authorization':token}, body:JSON.stringify({path:'/百度网盘/WebDAV'})});
```

重启 alist 后 token 失效（"token is invalidated"），需重新登录。

### 限制 WebDAV 只暴露子目录

百度网盘根目录文件杂乱时，创建专用文件夹并修改存储根路径：

1. 在百度网盘建 `WebDAV` 文件夹
2. 管理后台 → 存储 → 编辑 → 根文件夹路径 → `/` 改为 `/WebDAV`
3. 保存后 WebDAV 只显示该文件夹内容

### 备份脚本凭据漂移

备份脚本中硬编码的 alist 用户名/密码会随时间漂移（密码被修改后脚本不知道）。**401 错误不一定是服务挂了，先验证凭据是否有效**：

```python
import urllib.request, json
data = json.dumps({"username": "admin", "password": "<密码>"}).encode()
req = urllib.request.Request("http://localhost:5244/api/auth/login", data=data,
    headers={"Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req).read())
print(resp.get("code"), resp.get("message"))  # 200=成功, 400=密码错
```

如果 API 登录成功但 WebDAV 仍 401，检查：
1. 用户名是否含中文（curl/Basic Auth 编码问题——用 Python 发请求避免）
2. alist 是否在运行（`netstat -ano | grep ":5244"`）
3. 存储是否已挂载（`/api/admin/storage/list`）

### alist 重启后 WebBridge session 失效

用 Kimi WebBridge evaluate 调 alist API 时，`localStorage.getItem('token')` 取的 token 在 alist 重启后立即失效（"token is invalidated"）。需重新 navigate 登录页、填表、点击登录刷新 session。

### WebDAV 策略 API 值是 `native` 不是 `native_proxy`

通过 API 创建/更新存储时，`webdav_policy` 用 `"native"`（UI 显示为"本地代理"），不是 `"native_proxy"`。从 `/api/admin/storage/list` 返回的字段可验证正确值。
