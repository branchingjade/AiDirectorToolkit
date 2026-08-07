# SSH 远程部署模式

通过 paramiko SSH 连接到远程 Linux 主机（NAS、VPS 等），上传文件并部署服务。

## 核心模式

### 1. 连接与探测

```python
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)
```

### 2. 文件传输（base64 编码，绕过 shell 转义）

SFTP 在部分 NAS 上有权限问题（如绿联 UGOS）。可靠替代：base64 编码文件内容，通过 `exec_command` 写入。

```python
import base64
with open(local_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
ssh.exec_command(f'echo {b64} | base64 -d > {remote_path}')
```

**注意**：heredoc（`cat > file << EOF`）在 execute_code 沙箱中有中文转义问题，base64 更安全。

### 3. Docker 部署（国内网络受限时）

Docker Hub 被墙时，用镜像站拉取再 tag：

```bash
docker pull hub.rat.dev/library/python:3.12-slim
docker tag hub.rat.dev/library/python:3.12-slim python:3.12-slim
docker compose up -d --build
```

镜像站列表（按需测试连通性）：`hub.rat.dev`、`docker.m.daocloud.io`、`docker.nju.edu.cn`。

### 4. 开机自启

**Docker 容器**：`restart: unless-stopped` + Docker daemon 自启即可。
**裸进程**：systemd user service + `loginctl enable-linger`（需 sudo）。

## 常见陷阱

| 陷阱 | 解决 |
|------|------|
| SFTP put 报 No such file | 改 base64 + exec_command |
| NAS 上 pip 不可用 | `python3 -m venv venv` 创建隔离环境 |
| `sudo -S` 被 Hermes 拦截 | 安全机制，无法绕过；让用户手动执行 |
| Docker pull 超时 | 用 `hub.rat.dev` 等镜像站 |
| Clash TUN fake-ip 拦内网流量 | 用真实局域网 IP（192.168.x.x）而非 mDNS 域名 |
