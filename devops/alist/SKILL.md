---
name: alist
description: alist 安装、配置与故障排除——Windows 环境下将云存储挂载为本地 WebDAV。触发词：alist、WebDAV、百度网盘挂载、alist 配置。
---

# alist

Windows 下安装配置 alist，将百度网盘等云存储挂载为本地 WebDAV。

## 安装

```bash
# 下载最新版
mkdir -p ~/Documents/Hermes/tools/alist
cd ~/Documents/Hermes/tools/alist
curl -sL "https://api.github.com/repos/AlistGo/alist/releases/latest" | grep -oP '"tag_name":\s*"\K[^"]+'
# 下载 alist-windows-amd64.zip → 解压

# 初始化（获取管理员密码）
./alist.exe admin random
```

## 添加百度网盘存储

### 1. 获取 refresh token

百度 OAuth URL 格式：
```
https://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id=hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf&redirect_uri=oob&scope=basic,netdisk
```

用户在浏览器打开 → 登录百度账号 → 授权 → 获取 authorization code → 交换 refresh token：

```python
import json, urllib.request
# POST https://openapi.baidu.com/oauth/2.0/token
# grant_type=authorization_code, code=<授权码>, client_id=..., client_secret=..., redirect_uri=oob
# 返回 refresh_token
```

### 2. 添加存储（API 方式）

通过管理 API 添加，避免浏览器中文编码问题：

```python
# 登录 → POST /api/auth/login
# 创建 → POST /api/admin/storage/create
#   driver: "BaiduNetdisk"
#   mount_path: "/百度网盘"
#   webdav_policy: "native_proxy"
#   addition: JSON with refresh_token, root_folder_path, etc.
```

### 3. 设置根文件夹路径

通过 API 编辑存储，修改 `addition` 中的 `root_folder_path`：
- 默认 `"/"` → 暴露整个百度网盘根目录
- 改为 `"/WebDAV"` → 只暴露指定文件夹（需先在百度网盘创建该文件夹）

## WebDAV 策略 ⚠️

**Windows 原生 WebDAV 客户端必须用"本地代理"**，不能用"302 重定向"——Windows 发送 GET 探测 /dav/ 会被 405 拒绝。

推荐用 RaiDrive 替代 Windows 原生 WebDAV，兼容性更好。

## 开机自启

Startup 目录 `.vbs` 文件，静默启动：

```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\<user>\Documents\Hermes\tools\alist"
WshShell.Run "C:\Users\<user>\Documents\Hermes\tools\alist\alist.exe server", 0, False
```

放至 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\alist-server.vbs`。

## 管理员密码管理

```bash
# 查看当前管理员（⚠️ 不会显示密码——首次启动后密码以 hash 存储，不可逆）
./alist.exe admin
# 输出示例：
#   Admin user's username: 妖玉
#   The password can only be output at the first startup, and then stored as a hash value, which cannot be reversed

# 重置密码（直接写 config + 在线清缓存）
./alist.exe admin set <新密码>
```

**注意**：
- `alist.exe admin` **不会显示密码**，只显示用户名。首次启动后密码转为 hash 存储，无法反向解出。忘记密码只能 `admin set` 重置。
- `alist admin set` 修改 config.json 后会尝试通过 API 清缓存（需 server 正在运行）。如果 server 未运行，重启后生效。

## Kimi WebBridge 优先

当 alist 管理页面需要浏览器操作且涉及中文时，优先用 **Kimi WebBridge** 操作用户真实浏览器（已有登录态），而不是 Hermes CDP browser——后者对中文表单输入支持差（编码问题导致登录失败）。

### 安装（首次）

```powershell
# PowerShell 一键安装（自动下载 + 启动 daemon + 安装各 Agent skill）
irm https://cdn.kimi.com/webbridge/install.ps1 | iex
```

装完后在 Chrome 安装 Kimi WebBridge 扩展，使 `extension_connected` 变为 `true`。

### 状态检查

```bash
# 确认 daemon 运行 + 扩展已连接
~/.kimi-webbridge/bin/kimi-webbridge.exe status
# 关键字段：running=true, extension_connected=true
# 如果 extension_connected=false → 浏览器扩展未安装或未连接
```

### 页面操作

使用 Python urllib 发请求（避免 bash 中文编码问题）：

```python
import urllib.request, json

def wb(action, args=None, session='alist'):
    """发送 Kimi WebBridge 指令"""
    payload = json.dumps({'action': action, 'args': args or {}, 'session': session}).encode()
    req = urllib.request.Request('http://127.0.0.1:10086/command',
        data=payload, headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req).read())

# 导航到管理页
wb('navigate', {'url': 'http://localhost:5244/@manage', 'newTab': True})

# 获取页面快照（full=False 只返回可交互元素，full=True 返回全部内容）
snap = wb('snapshot', {'full': False})
# snap['data']['tree'] 包含可交互元素及其 ref ID（如 @e6）

# 导航到特定页面比 click 更可靠
wb('navigate', {'url': 'http://localhost:5244/@manage/storages'})  # 存储列表
wb('navigate', {'url': 'http://localhost:5244/@manage/users'})     # 用户列表
```

## 全局安全设置

```python
# 关签名（WebDAV 不需要）+ 开首页索引
api("/api/admin/setting/save", method="POST", body=[
    {"key": "sign_all", "value": "false"},
    {"key": "allow_indexed", "value": "true"}
])

# 禁用 guest 用户
api("/api/admin/user/save", method="POST", body={
    "id": guest_id, "username": "guest", "password": "",
    "base_path": "/", "role": 2, "disabled": True, "permission": 0
})
```

## 检测运行状态

**不要用 `tasklist` 或单次 `curl` 判断 alist 是否在运行**——两者都有假阴性：

- `tasklist /FI "IMAGENAME eq alist.exe"` 在 bash（MSYS/Git Bash）下编码乱码，进程存在时也可能显示乱码文本误导判断
- `curl -s http://localhost:5244` 偶尔返回 `000`（exit code 23），不代表服务挂了

**可靠检测方式**：

```bash
# 端口占用检测（最可靠）
netstat -ano | grep ":5244"
# 有 LISTENING 行 → 在运行；无输出 → 真挂了

# 多次 curl 确认（单次 000 可能是瞬态）
for i in 1 2 3; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5244; sleep 1; done
```

## 故障排查流程

百度网盘报 `errno: 20016` 时，按以下步骤排查：

### 1. 确认 token 本身是否有效

直接测试 access_token 是否能用（不要通过 alist）：

```python
import urllib.request, json, urllib.parse

# 用 refresh_token 换 access_token
data = {
    'grant_type': 'refresh_token',
    'refresh_token': '<你的RT>',
    'client_id': 'hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf',
    'client_secret': 'YH2VpZcFJHYNnV6vLfHQXDBhcE7ZChyE'
}
req = urllib.request.Request('https://openapi.baidu.com/oauth/2.0/token',
    data=urllib.parse.urlencode(data).encode(),
    headers={'Content-Type': 'application/x-www-form-urlencoded'})
resp = json.loads(urllib.request.urlopen(req).read())
at = resp['access_token']

# 测试百度 PCS API
url = f'https://pan.baidu.com/rest/2.0/xpan/nas?method=uinfo&access_token={at}'
print(json.loads(urllib.request.urlopen(url).read()))
```

如果这一步 errno=0，说明 token 有效，问题在 alist 端。

### 2. token 有效但 alist 报 20016 → 删掉重建存储

多次 API 更新 refresh_token 仍报 20016 的情况下，**直接删掉存储重建**——alist 内部可能缓存了旧状态：

```python
# 删除存储
POST /api/admin/storage/delete?id=<id>
# 用新的 refresh_token 重建
POST /api/admin/storage/create
```

**重建时必须用的 addition 字段：** `refresh_token`, `root_folder_path`, `client_id`, `client_secret`, `upload_thread`, `upload_api`。

### 3. token 无效 → 重新 OAuth 授权

⚠️ **关键：换到新 refresh_token 后不要手动测试它！** 百度 OAuth 机制是每次 refresh 返回新 RT，旧 RT 立即作废。手动测试会消费掉 alist 要用的 token，导致 token 链断裂。

正确做法：授权码 → 换 RT → **直接存入 alist，不测试**。

## 常见问题

### Windows WebDAV "Method Not Allowed"
- **原因**：Windows WebDAV 客户端发 GET 到 /dav/ 被 alist 拒绝（405）
- **解决**：存储 WebDAV 策略改为"本地代理"；或用 RaiDrive

### curl 登录 API 返回 400
- **原因**：bash 编码中文参数导致 JSON 损坏
- **解决**：用 Python urllib 发请求（UTF-8 编码可靠）

### alist admin set 改了密码但不生效

常见根因（按概率排序）：

1. **`db_file` 路径指向错误数据库**：`config.json` 中 `db_file` 为 `data\\data.db` 时，实际解析为 `<data>/data/data.db`（嵌套子目录），而非 `<data>/data.db`。`admin set` 命令更新了错误的数据库，alist server 也读取错误的数据库。修复：改为 `"data.db"`，删除 `data/data/` 下的错误 db 文件。

2. **v3.9.0+ 未先停服**：运行的 alist server 锁定数据库。必须先 `Stop-Process -Name alist -Force` 再执行 `admin set`。

3. **WAL 文件导致读到旧数据**：SQLite WAL 模式下修改先写 `data.db-wal`。验证前删除 WAL 文件（`rm -f data.db-wal data.db-shm`）或先停服让 checkpoint 触发。

4. **server 缓存了旧凭据**：重启 alist server 清内存缓存。

**完整修复流程**：
```bash
# 1. 停服
powershell -Command "Stop-Process -Name alist -Force"
# 2. 检查 db_file 配置 + 删 WAL
grep db_file data/config.json  # 应显示 "data.db" 不是 "data\\data.db"
rm -f data/data.db-wal data/data.db-shm
# 3. 重置
./alist.exe admin set <新密码> --data "./data"
# 4. 验证（必须）
python3 -c "
import sqlite3
db = sqlite3.connect('data/data.db')
db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
for r in db.execute('SELECT id, username FROM x_users'):
    print(r)
"
# 5. 重启
./alist.exe server --data "./data"
```

### 百度网盘存储报 errno 20016

#### 第一步：重新授权（常规流程）

- **原因**：百度 OAuth refresh token 过期或授权失效
- **现象**：存储状态显示 `errno: 20016, refer to https://pan.baidu.com/union/doc/`
- **解决**：重新走百度 OAuth 授权流程获取新的 refresh token，然后通过 API 更新存储的 `addition.refresh_token`

#### 第二步：DELETE + RECREATE（API 更新无效时）⚠️

如果按上述流程更新了 refresh_token 但存储仍报 20016，说明 alist 内部缓存了旧存储的异常状态，API update 无法清除。**必须删除存储并重建**：

```python
# 1. 登录 alist
data = json.dumps({'username': '妖玉', 'password': '<密码>'}).encode()
req = urllib.request.Request('http://localhost:5244/api/auth/login', data=data,
    headers={'Content-Type': 'application/json'})
token = json.loads(urllib.request.urlopen(req).read())['data']['token']

# 2. 删除旧存储
req = urllib.request.Request('http://localhost:5244/api/admin/storage/delete?id=<storage_id>',
    data=b'', headers={'Authorization': token})

# 3. 创建新存储（注意：refresh_token 必须是刚换的、未被使用过的）
new_storage = {
    'mount_path': '/百度网盘',
    'driver': 'BaiduNetdisk',
    'cache_expiration': 30,
    'webdav_policy': 'native_proxy',
    'addition': json.dumps({
        'refresh_token': '<刚换到的 refresh_token>',
        'root_folder_path': '/WebDAV',
        'client_id': 'hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf',
        'client_secret': 'YH2VpZcFJHYNnV6vLfHQXDBhcE7ZChyE',
        'upload_thread': '3',
        'upload_api': 'https://d.pcs.baidu.com'
    }, ensure_ascii=False)
}
req = urllib.request.Request('http://localhost:5244/api/admin/storage/create',
    data=json.dumps(new_storage).encode(),
    headers={'Authorization': token, 'Content-Type': 'application/json'})
resp = json.loads(urllib.request.urlopen(req).read())
# code=200 + message="success" → 存储状态变为 "work"
```

**关键点**：创建新存储时传入的 `refresh_token` **绝不能在此之前被手动使用过**（见下方 OAuth token 链一次性消耗），否则 alist 初始化时拿到的 access_token 无效，新存储也会报 20016。

### 百度 OAuth token 链一次性消耗 ⚠️

百度 OAuth 的关键特性：**每次用 refresh_token 换取 access_token，百度会同时返回一个新的 refresh_token，旧的立即作废。** 这意味着：

- 用授权码换到 refresh_token **后不要手动测试**（如用 access_token 调百度 API 验证）——一旦你手动调了 `/oauth/2.0/token?grant_type=refresh_token`，生成的 refresh_token 就被消耗了，保存到 alist 的是废 token
- 授权码也是单次使用，用过后失效
- **正确流程**：用户给授权码 → 换 refresh_token → **立刻存入 alist，不做任何验证**。alist 内部会自己用 refresh_token 换 access_token 并更新存储
- 如果测试了 token 导致链断裂，需要用户重新授权

## 参考脚本

- `references/baidu-oauth-recreate.md` — 百度 OAuth 授权 + alist 存储创建完整流程（含 DELETE + RECREATE）
- `references/bcrypt-password-reset.md` — bcrypt 直接写 SQLite 重置管理员密码（`admin set` 不生效时的可靠绕过）

## 陷阱

- **不要用 bash/curl 内联中文字段**——shell 编码问题导致 JSON 损坏，使用 Python urllib 或 WebBridge
- **Windows 原生 WebDAV 客户端兼容性差**——推荐 RaiDrive
- **修改密码前告知用户**——`alist admin set` 就地改密码，用户可能无法登录
- **storage/save API 需要传完整对象**——只传要改的字段会导致未传字段被清空。先 GET 当前存储对象，修改目标字段后完整 PUT 回去
- **不要在没有检测的情况下直接 `alist.exe server`**——如果已有实例在跑，新进程会因端口冲突退出（`bind: address already in use`），然后你看到 exit code 1 误以为是启动失败。先 `netstat -ano | grep ":5244"` 确认没有占用再启动
- **百度 OAuth 授权码和 refresh_token 都是一次性的**——换到 token 后立刻存入 alist，不要手动调用百度 API 验证 token 有效性，否则 token 被消耗，alist 拿到的是废的，只能重新授权
- **`config.json` 中 `db_file` 必须用绝对路径**——`alist admin` 系列命令将相对路径 `"data.db"` 解析为相对于**当前工作目录**而非 config.json 所在目录，导致修改错误的数据库文件。修复：`"db_file": "C:\\Users\\%USERNAME%\\Documents\\Hermes\\tools\\alist\\data\\data.db"`
- **`alist admin set` 对已存在的 admin 用户可能不写入数据库**——日志显示 "admin user has been updated" 但实际密码未变。怀疑 alist 的 upsert 逻辑有 bug（admin 已存在时跳过写入）。绕过方法：用 Python bcrypt 直接写 SQLite：`db.execute('UPDATE x_users SET password = ? WHERE username = ?', (bcrypt_hash, 'admin'))`
- **`alist admin`/`admin random` 会在错误位置创建 data.db**——由于 db_file 相对路径问题，这些命令可能在当前工作目录创建新的 data.db 而非修改正确的数据库。执行前确认 `pwd` 和 db_file 绝对路径
- **验证 `alist admin` 是否真正生效（铁律）**——`admin set/random` 输出 "admin user has been updated" **不代表数据库被改**。验证三步：
  1. `stat <data>/data.db` 看 Modify 时间戳——命令执行后没变 → 写到了错误数据库（db_file 路径/工作目录不对）
  2. `find <alist目录> -name "data.db"` 列出全部 db 文件（可能有根目录、data/、data/data/ 多个副本）——对比各库的 x_users/x_storages 表，找到真正在用的那个
  3. 直接读 SQLite 确认密码 hash：`SELECT id, username, length(password) FROM x_users`——admin 的 pw_len 应为 60（bcrypt），0 表示没写入。**不要只看命令日志，必须读库验证**
- **管理员用户名不一定是脚本里写的**——`alist admin` 输出 "Admin user's username" 才是权威。备份脚本/cron 里用户名写错（如写旧用户名 `妖玉` 实际是 `admin`）会导致登录 401、备份静默失败多天。排查 401 时先确认用户名和密码都对
- **WebDAV 自检脚本**：`scripts/webdav-check.py` — 一键检查：登录 → 存储列表 → PROPFIND 根/挂载路径 → 全局设置。改密码/修 db 后跑它验证全链路
