# NAS mihomo 代理: Docker build 时走代理

## 背景

UGOS NAS docker daemon 无法配置代理(no root), 但 build 过程中的 `git clone`/`npm install`/`pip install` 需要外网。mihomo 作为 NAS 本地代理解决此问题。

## 安装步骤

### 1. 下载 mihomo binary (aarch64)
```bash
# 本机下载, 通过 SFTP 传到 NAS
curl -sL -o mihomo.gz https://github.com/metacubex/mihomo/releases/download/v1.19.10/mihomo-linux-arm64-v1.19.10.gz
gunzip mihomo.gz && chmod +x mihomo
# SFTP put 到 /docker/tencentdb-memory/mihomo
```

### 2. 下载 GeoIP/GeoSite dat
```bash
curl -o GeoIP.dat https://cdn.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/country.dat
curl -o GeoSite.dat https://cdn.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geosite.dat
```

### 3. 配置文件
```yaml
mixed-port: 7890
allow-lan: true
bind-address: '*'
mode: rule
log-level: info
proxy-providers:
  sub:
    type: http
    url: "<subscription URL>"
    interval: 86400
    health-check: { enable: false }
rules:
  - GEOIP,CN,DIRECT
  - MATCH,Proxy
```

### 4. 启动
```bash
nohup ./mihomo -m -d /path/to/config/ > mihomo.log 2>&1 &
# -m = geodata mode (用 .dat 文件, 非 mmdb)
```

### 5. Docker build 使用代理
```bash
docker build \
  --build-arg HTTP_PROXY=http://192.168.1.2:7890 \
  --build-arg HTTPS_PROXY=http://192.168.1.2:7890 \
  -f Dockerfile.hermes -t image:tag .
```

## 关键坑

- **容器内 127.0.0.1 ≠ 宿主机**: Docker build 的 RUN 命令里 `127.0.0.1:7890` 指向容器自己。用宿主机 LAN IP `192.168.1.2:7890`
- **GeoIP.dat 格式**: mihomo `-m` mode 用 dat 格式(非 mmdb)。从 `cdn.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/` 下载的是 dat 格式
- **GeoSite.dat 需要正确来源**: `geosite.dat` 从 `MetaCubeX/meta-rules-dat` 下载; `GeoSite.mmdb` 格式不存在(404)
- **crontab 不可用**: UGOS HMSJadmin 无 crontab 权限。用 `restart: unless-stopped` + 手动启动
- **mihomo 配置里 health-check 会导致启动慢**: 首次启动时 health check 去 gstatic.com 超时, 关闭 `health-check: { enable: false }` 加速

## 验证
```bash
# 本地测试
curl -s -o /dev/null -w "%{http_code}" --max-time 8 -x http://127.0.0.1:7890 https://github.com/
# → 200

# Docker build 测试 (在 Dockerfile 的 RUN 里)
RUN curl -s -o /dev/null -w "%{http_code}" https://github.com/
# → 200 (通过 build-arg 传入的 proxy)
```

## 与 nas-docker-deploy 的关系

`nas-docker-deploy` 的 `hub.rat.dev` 镜像前缀方案适用于 FROM 基础镜像拉取(简单场景)。mihomo 代理适用于 build 过程中需要访问外网的复杂场景(多阶段构建、git clone、npm install 等)。两者互补。
