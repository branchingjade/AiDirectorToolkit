# NAS mihomo MMDB 鸡蛋问题（2026-08-27 实战）

## 问题

mihomo 启动时需要 MMDB（GeoIP 数据库）供 `GEOIP,CN,DIRECT` 规则，但 MMDB 需要从外网下载，而 mihomo 是唯一能代理外网的工具——**死循环**。

## 实测现象

```
time="..." level=info msg="Start initial configuration in progress"
time="..." level=warning msg="MMDB invalid, remove and download"
# 等待60秒...
time="..." level=error msg="can't initial GeoIP: can't download MMDB: context deadline exceeded"
time="..." level=fatal msg="Parse config error: load GeoIP dns fallback filter error"
```

## 解法

config.yaml 中禁用 GEOIP 规则，注释掉 GEOIP 行：

```yaml
rules:
  # - 'GEOIP,CN,DIRECT'   # ← 注释掉：需要 MMDB
  - MATCH,Proxy           # ← 保留：所有流量走代理
```

同时加：
```yaml
geo-auto-update: false
```

## 已验证的节点状态

NAS 上的 mihomo proxies 文件（`/volume1/docker/tencentdb-memory/proxies/`）中的节点**2026-08-26 11:31 创建**——机场订阅更新后旧节点全部失效。即使 config 正确、MMDB 也有，**代理连不上**是因为节点过期。

需要：
1. 获取最新机场订阅 URL
2. 用新订阅更新 proxies 文件
3. 重启 mihomo
4. 验证 `curl -x http://127.0.0.1:7890 https://github.com/ -o /dev/null -w "%{http_code}"` → 200
