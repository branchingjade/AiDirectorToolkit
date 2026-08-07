---
name: clash-config
description: Clash Verge 分流配置管理——订阅分析、地区分组脚本、规则增强、API自检。触发词：clash、分流、代理规则、TUN、节点分组。
category: devops
---

# Clash Verge 分流配置管理

## 目录结构

所有配置在 `%APPDATA%/io.github.clash-verge-rev.clash-verge-rev/`：

```
profiles/
  profiles.yaml        ← 订阅列表，current 指向当前生效的订阅 UID
  {uid}.yaml           ← 远程订阅拉下来的完整配置（只读，别改）
  rFykVaWKjJzk.yaml    ← 规则增强（prepend/append/delete）
  m2G4h8rmcyl3.yaml    ← 全局扩展覆盖（merge YAML）
  sSm5lXS6fVKp.js      ← 全局扩展脚本（JS 修改 config 对象）
```

`verge.yaml` 中有 `verge_mixed_port`（HTTP 代理端口）和 `enable_external_controller` 等关键配置。

## 三种扩展方式对比

| 方式 | 文件 | 用途 | 会替换原配置？ |
|---|---|---|---|
| **Rules** | `rFykVaWKjJzk.yaml` | 增删规则 | ❌ 不替换，prepend/append/delete |
| **Merge** | `m2G4h8rmcyl3.yaml` | 深度合并 YAML | ❌ 合并（行为依赖版本，有风险） |
| **Script** | `sSm5lXS6fVKp.js` | JS 修改 config 对象 | ❌ 拿到完整 config 自由操作 |

**加固定规则 → 用 Rules（prepend/append）。需要动态逻辑（如按地区分组节点、正则匹配）→ 用 Script。**

## 操作流程

### 1. 分析当前配置

```bash
# 看当前用的是哪个订阅
cat "$APPDATA/io.github.clash-verge-rev.clash-verge-rev/profiles.yaml"

# 分析订阅配置结构（节点、代理组、规则）
# 节点在 proxies: 段，代理组在 proxy-groups: 段，规则在 rules: 段
# 文件路径: profiles/{uid}.yaml
```

### 2. 加分流规则（固定域名）

编辑 `profiles/rFykVaWKjJzk.yaml`：

```yaml
prepend:
    - DOMAIN-SUFFIX,elevenlabs.io,🌍 新加坡    # 前置，优先级最高
    - DOMAIN-SUFFIX,openai.com,🌍 日本

append:
    - DOMAIN-SUFFIX,some-cdn.com,DIRECT         # 追加到末尾

delete: []
```

- `prepend`：插在规则列表最前面，优先级高于订阅自带规则
- `append`：追加到末尾，可能被前面规则拦截
- `delete`：删除订阅自带的某条规则

规则类型：
- `DOMAIN-SUFFIX`：匹配域名及所有子域名（推荐，覆盖广）
- `DOMAIN`：仅精确匹配该域名
- `DOMAIN-KEYWORD`：域名包含关键字
- `IP-CIDR`：IP 段
- `GEOIP`：按地区 IP
- `MATCH`：兜底

### 3. 地区分组（Script）

编辑 `profiles/sSm5lXS6fVKp.js`，在 `main` 函数中：

1. 遍历 `config.proxies`，按节点名中的地区归类
2. 为每个地区创建 `url-test` 类型的 proxy-group
3. 注入到主组 `Thunder` 的 proxies 列表中
4. `groups.splice()` 插入到 proxy-groups

文件保存后 Clash Verge 自动重载。

### 4. API 自检

先确认 external controller 是否开启（`verge.yaml` → `enable_external_controller: true`）。端口通常是 `verge_mixed_port` 对应的 controller 端口（如 9097）。用 `Authorization: Bearer {secret}` 头。

```bash
# 检查规则
curl -s -H "Authorization: Bearer {secret}" http://127.0.0.1:{port}/rules

# 检查代理组
curl -s -H "Authorization: Bearer {secret}" http://127.0.0.1:{port}/group
```

Clash API 返回格式：`/rules` 返回 `{"rules": [...]}`，`/group` 返回 `{"proxies": [...]}`（数组，不是字典）。

### 5. 验证规则命中

```bash
# 发起实际请求，触发规则匹配
curl -sI https://目标域名

# 然后在 Clash Verge Connections 面板确认走的节点
# 或用 curl 验证网络可达性
```

## 常见问题

- **订阅更新 403**：token 过期，去机场后台重新获取 URL。与脚本/规则无关
- **地区分组不出现**：检查脚本是否有语法错误，节点名中的地区是否被正则匹配到
- **TUN 模式确认生效**：`curl --noproxy '*' https://www.google.com` 返回 200 即生效
- **API 返回 404**：路径可能不对，Mihomo 内核用 `/group` 而非 `/proxy-groups`
