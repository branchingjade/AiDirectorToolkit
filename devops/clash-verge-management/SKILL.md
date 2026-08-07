---
name: clash-verge-management
description: Clash Verge 代理配置管理——定位配置文件、分流规则增删、节点分组脚本、API自检。触发词：Clash、clash、分流、代理规则、节点分组、TUN模式。
---

# Clash Verge 配置管理

## 配置文件位置

所有配置文件在 `%APPDATA%/io.github.clash-verge-rev.clash-verge-rev/` 下：

| 文件 | 作用 |
|---|---|
| `profiles.yaml` | 订阅列表和增强配置关联 |
| `verge.yaml` | Clash Verge 自身设置（端口、TUN等） |
| `profiles/<uid>.yaml` | 远程订阅内容（规则、节点、代理组） |
| `profiles/Merge.yaml` | 全局 Merge 增强 |
| `profiles/<uid>.yaml`（Rules类型） | 单订阅规则增强（prepend/append/delete） |
| `profiles/<uid>.js`（Script类型） | 单订阅脚本增强（JS操作config对象） |

profiles.yaml 中 `current` 字段指向当前激活的订阅。

## 三种增强方式对比

| | Rules（规则增强） | Merge（合并增强） | Script（脚本增强） |
|---|---|---|---|
| **作用** | 增删改规则 | 深度合并YAML字段 | JS操作整个config对象 |
| **是否替换原规则** | 否——prepend前置、append追加、delete删除 | 可能覆盖（依赖版本行为） | 完全由脚本控制 |
| **典型场景** | 加固定分流规则 | 改DNS、端口等全局字段 | 动态创建代理组、条件判断 |
| **复杂度** | ★☆☆ | ★★☆ | ★★★ |

**铁律：加分流规则用 Rules，不要用 Merge。** Merge 的行为在不同版本间不一致，可能意外覆盖订阅内容。

## 添加分流规则

编辑 Rules 文件（如 `rFykVaWKjJzk.yaml`）：

```yaml
prepend:
    - DOMAIN-SUFFIX,elevenlabs.io,🌍 新加坡
    - DOMAIN-KEYWORD,openai,Thunder
append:
    - DOMAIN-SUFFIX,some-cdn.com,DIRECT
delete:
    - DOMAIN-SUFFIX,unwanted.com
```

- `prepend`：前置，优先级最高，确保不被订阅规则拦截
- `append`：追加到规则列表末尾
- `delete`：删除订阅中的特定规则

规则类型：`DOMAIN-SUFFIX`（匹配子域名）、`DOMAIN`（精确匹配）、`DOMAIN-KEYWORD`（关键词）、`IP-CIDR`、`GEOIP`、`MATCH`。

**修改后 Clash Verge 自动检测文件变化并重载核心配置，无需手动更新订阅。**

## 创建地区分组（Script）

当需要按地区拆分节点为独立代理组时，用 Script：

```javascript
function main(config, profileName) {
  const regionMap = {};
  for (const p of config['proxies'] || []) {
    const match = p.name.match(/[\u4e00-\u9fff]+/);
    if (match) {
      const region = match[0];
      if (!regionMap[region]) regionMap[region] = [];
      regionMap[region].push(p.name);
    }
  }
  const regionGroups = Object.keys(regionMap).sort().map(region => ({
    name: `🌍 ${region}`,
    type: 'url-test',
    proxies: regionMap[region],
    url: 'http://www.gstatic.com/generate_204',
    interval: 86400
  }));
  // 注入到 Thunder 主组
  const thunder = config['proxy-groups'].find(g => g.name === 'Thunder');
  const regionKeys = regionGroups.map(g => g.name);
  const autoIdx = thunder.proxies.indexOf('自动选择');
  thunder.proxies.splice(autoIdx >= 0 ? autoIdx : thunder.proxies.length, 0, ...regionKeys);
  // 插入到 proxy-groups 列表
  const tIdx = config['proxy-groups'].findIndex(g => g.name === 'Thunder');
  config['proxy-groups'].splice(tIdx + 1, 0, ...regionGroups);
  return config;
}
```

完整示例见 `references/region-group-script.js`。

## API 自检

Clash 外部控制器默认关闭（`verge.yaml` 中 `enable_external_controller: false`）。开启后可通过 REST API 验证配置：

```bash
# 端口和密钥在 verge.yaml 中，或在 Clash Verge 设置中查看
curl -s -H "Authorization: Bearer <secret>" http://127.0.0.1:<port>/group
curl -s -H "Authorization: Bearer <secret>" http://127.0.0.1:<port>/rules
```

Mihomo 内核 API 路径与标准 Clash 不同：用 `/group` 而非 `/proxies`。

## TUN 模式验证

```bash
# 验证 TUN 是否生效——不设代理的情况下访问被墙站点
curl -s --noproxy '*' https://www.google.com -o /dev/null -w "%{http_code}"
# 返回 200 → TUN 生效
```

## 常见问题

- **订阅更新 403**：订阅 URL 中 token 过期（有效期通常1小时），去机场后台重新获取 URL
- **脚本修改后不生效**：Clash Verge 监听文件变化自动重载，通常无需手动操作；如未生效，切一下 profile 再切回来
- **Merge vs Rules 混淆**：绝对不要在 Merge 文件中写 rules，用 Rules 类型文件
