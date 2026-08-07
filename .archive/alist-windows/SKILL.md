---
name: alist-windows
description: 在 Windows 上安装、配置 alist 文件列表服务器，挂载百度网盘等存储后端为 WebDAV。触发词：alist、WebDAV、百度网盘挂载、alist 配置。
version: 1.0.0
---

# alist Windows 配置

在 Windows 上安装 alist，挂载百度网盘等云存储为 WebDAV，含开机自启。

## 安装

```bash
mkdir -p ~/Documents/Hermes/tools/alist
cd ~/Documents/Hermes/tools/alist
# 获取最新版本号
VER=$(curl -sL https://api.github.com/repos/AlistGo/alist/releases/latest | grep -oP '"tag_name":\s*"\K[^"]+')
# 下载
curl -sL "https://github.com/AlistGo/alist/releases/download/$VER/alist-windows-amd64.zip" -o alist.zip
unzip -o alist.zip
```

## 初始化 & 管理密码

```bash
cd ~/Documents/Hermes/tools/alist
./alist.exe admin random          # 生成随机密码（首次）
./alist.exe admin set <新密码>    # 修改密码
```

管理后台：`http://localhost:5244/@manage`

## 添加百度网盘存储

### 1. 获取 refresh token

百度网盘的 alist 内置"获取令牌"按钮可能不显示。回退方案——手动 OAuth：

1. 打开：`https://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id=hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf&redirect_uri=oob&scope=basic,netdisk`
2. 登录百度账号授权
3. 复制授权码（类似 `xxxxxxxxxxxxxxxx`）
4. 兑换 refresh token：

```bash
curl -s "https://openapi.baidu.com/oauth/2.0/token?grant_type=authorization_code&code=<授权码>&client_id=hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf&client_secret=YH2VpZcFJHYNnV6vLfHQXDBhcE7ZChyE&redirect_uri=oob"
```

取返回的 `refresh_token`。

### 2. 创建存储（API 方式）

用 Python API 添加存储比浏览器填表更可靠（避免中文编码问题）：

```python
import json, urllib.request

# 登录获取 token
resp = api("/api/auth/login", method="POST", body={"username": "admin", "password": "xxx"})
token = resp["data"]["token"]

# 创建存储
storage = {
    "mount_path": "/百度网盘",
    "driver": "BaiduNetdisk",
    "webdav_policy": "native_proxy",  # 推荐"本地代理"
    "addition": json.dumps({
        "refresh_token": "<refresh_token>",
        "root_folder_path": "/",
        "download_api": "official",
        "client_id": "hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf",
        "client_secret": "YH2VpZcFJHYNnV6vLfHQXDBhcE7ZChyE",
        "custom_ua": "netdisk",
    })
}
api("/api/admin/storage/create", method="POST", body=storage)
```

## WebDAV 访问

### WebDAV 地址

`http://localhost:5244/dav`（带存储子路径如 `/dav/百度网盘/`）

### WebDAV 策略

| 策略 | 说明 |
|------|------|
| **本地代理**（推荐） | 内容直传，兼容性好 |
| 302 重定向 | 跳转到下载链接 |
| 使用代理地址 | 走代理 |

### Windows WebDAV 客户端

⚠️ Windows 原生 WebDAV 客户端（资源管理器映射）**不可用**。原因是：
- alist 对 `GET /dav/` 返回 405，Windows WebDAV 客户端将 GET 作为初始探测
- 中文用户名在 Windows 凭据管理中也有兼容问题

**推荐 RaiDrive**：https://www.raidrive.com/download（免费），填写：
- 地址：`localhost`，端口：`5244`，路径：`/dav`
- 账号密码即 alist 账号

### 测试 WebDAV

```bash
# ⚠️ curl -u 在 MSYS/bash 中对中文用户名编码有问题，用 base64
curl -s -o /dev/null -w "%{http_code}" -X PROPFIND "http://localhost:5244/dav/" \
  -H "Depth: 1" \
  -H "Authorization: Basic $(echo -n '用户名:密码' | base64)"
# 应返回 207
```

## 开机自启

创建 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\alist-server.vbs`：

```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\<user>\Documents\Hermes\tools\alist"
WshShell.Run "C:\Users\<user>\Documents\Hermes\tools\alist\alist.exe server", 0, False
```

## 数据库调试

当认证异常时需要检查密码哈希：

```python
import sqlite3
db = sqlite3.connect('data/data.db')
c = db.execute('SELECT id, username, pwd_hash, salt, disabled FROM x_users')
# 密码在 pwd_hash 列（SHA256+salt），非 password 列
```

## 陷阱

### curl -u 中文编码
在 MSYS/Git Bash 中 `curl -u 中文名:密码` 的 Basic Auth 编码会出错。**必须用 base64 手动编码**：`Authorization: Basic $(echo -n 'user:pass' | base64)`。

### 浏览器访问 /dav 返回 Method Not Allowed
**这不是 bug**。浏览器发 GET 请求，WebDAV 目录需要 PROPFIND。只有 WebDAV 客户端能正常访问。

### alist admin set 不立即生效
`alist admin set` 修改数据库后尝试通知运行中的服务器清除缓存。如果服务器未运行会报 `del_user_cache_online failed`——这是无害的警告，重启 alist 即可。

### 百度网盘 OAuth 回调
alist 内置的 OAuth 回调 (`redirect_uri=https://tool.nn.ci/...`) 在新版本可能不工作。用 `redirect_uri=oob` 手动获取授权码是最可靠的方式。

### WebDAV 根路径隔离
修改存储的 `root_folder_path` 可限制 WebDAV 只暴露特定子目录。先在百度网盘创建目标文件夹，再通过管理后台或 API 修改存储配置。
