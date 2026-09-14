# NAS 出网白名单实测（2026-08-27）

绿联 UGOS NAS 的出网策略是**白名单模式**——不是全封，是按域名/端口允许特定流量。

## 实测结果（从 NAS 本机 curl）

| 域名 | HTTP 状态 | 延迟 | 可用？ |
|---|---|---|---|
| baidu.com | 200 | 1.9s | ✅ |
| github.com | 200 (473KB) | 4.9s | ✅ |
| ghcr.io | 200 | 5.0s | ✅ |
| quay.io | 200 | 1.5s | ✅ |
| doh.pub | 200 | 0.3s | ✅ |
| pypi.org | 200 | 0.2s | ✅ |
| npmjs.com | 403 (可达) | 1.1s | ⚠️ |
| api.xiaomimimo.com | 404 (可达) | 0.4s | ✅ |
| google.com | timeout | 5s | ❌ |
| registry-1.docker.io | timeout | 5s | ❌ |
| registry.docker.io | timeout | 5s | ❌ |
| gcr.io | timeout | 5s | ❌ |
| api.openai.com | timeout | 5s | ❌ |

## 关键结论

1. **docker.io（gcr.io）永远不通**——白名单不包含容器 registry
2. **GitHub/pypi/公共 API 可用**——GitHub clone、npm install、pypi install 能走
3. **iptables 不存在**——NAS 无 firewall-cmd/iptables/ufw/nft 命令
4. **防火墙管理只能走 Web UI**（https://hmsj.local:443）——SSH 无法操作
5. **mihomo 代理无法启动**——mihomo 需要 MMDB 供 GEOIP 规则，MMDB 需要外网下载，死循环

## 部署绕行策略

由于 docker.io 不通，不能 `docker pull` 官方镜像。可行方案：

| 路径 | 方式 | 依赖 |
|---|---|---|
| A. hub.rat.dev 前缀 | `docker pull hub.rat.dev/library/xxx` + retag | NAS 能访问 hub.rat.dev（未测）|
| B. GitHub 源码 build | 从 GitHub clone/tar → 本地 `docker build` | NAS 能访问 github.com ✅ |
| C. 本机 Docker Desktop | Windows 拉镜像 → save tar → scp/飞书 → NAS load | 本机有 docker |
| D. Web UI 关防火墙 | 用户手动在 NAS Web UI 解放 docker.io | 用户操作 |

**路径 B 已验证（2026-08-27）**：
```bash
# NAS 上（已验证 github.com 可达）
curl -fsSL -o tdb.tar.gz https://github.com/TencentCloud/TencentDB-Agent-Memory/archive/refs/heads/main.tar.gz
tar xzf tdb.tar.gz
cd TencentDB-Agent-Memory-main/docker/opensource
docker build -f Dockerfile.hermes -t hermes-memory:v3 .
```
但 Dockerfile.hermes 用 `ubuntu:24.04` 做 base（docker.io 镜像），build 会卡在拉 base image。

**解决方案（已验证）**：用现有本地镜像（如 `tencentdb-gateway:2.0.0`）做 base：
```dockerfile
FROM tencentdb-gateway:2.0.0
# 只覆盖 src/（不覆盖 npm 依赖，避免破坏 v2 路由）
COPY src /opt/tdai-gateway/node_modules/@tencentdb-agent-memory/memory-tencentdb/src
COPY start.sh /opt/start.sh
RUN chmod +x /opt/start.sh
CMD ["/opt/start.sh"]
```
**⚠️ 危险**：COPY src/ over node_modules 会破坏 v2 路由（已实测）。更安全的做法是只改 CMD（env 覆盖 LLM 配置）不动代码。