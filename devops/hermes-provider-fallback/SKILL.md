---
name: hermes-provider-fallback
description: LLM provider 兜底链实战铁律——同链≠同凭据、psutil 环境验证、MiniMax 2056、attempt 3/3 失败判据；TDB/TencentDB 端点配置实战（env var 优先级、yaml 字段名错配、NAS 防火墙白名单）。
tags: [hermes, provider, fallback, minimax, psutil, env-validation, tdb, krolik, end-point-config]
whenToUse: 涉及 LLM provider 兜底链诊断、跨渠道凭据差异、MiniMax Token Plan 错误、agent.log attempt 失败排查、TDB/TencentDB pipeline LLM 端点配置、NAS 出网白名单验证、Hermes 输出流脱敏陷阱排查时。
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, provider, fallback, minimax, psutil, env-validation, tdb, krolik, end-point-config]
    related_skills: [hermes-maintenance, hermes-monitoring, hermes-agent, tencentdb-gateway]
    changelog:
      - 1.1.0 (2026-08-27): 新增「TDB/TencentDB LLM 端点配置实战铁律」——env var 优先级机制、yaml base_url vs baseUrl 字段名错配、NAS 防火墙白名单、Hermes 输出流脱敏陷阱、docker compose down+up 才能让 env 生效。
      - 1.0.0 (2026-08-27): 起源——2026-08-27 实测，多渠道兜底差异 + MiniMax 2056 错误排查。从 MEMORY.md「兜底链运行时真相」条迁出。
---

# Hermes Provider 兜底链实战铁律

> 完整 4 条实战教训，2026-08-27 飞书网关 vs 桌面 app 实测确立。
> 起源：从 MEMORY.md 第 22 条「兜底链运行时真相」迁出（MEMORY 精简 Phase 6）。
> 适用范围：任何涉及 LLM provider 兜底链诊断、跨渠道凭据差异、MiniMax Token Plan 错误的场景。

## 1. 同 config.yaml 兜底链 ≠ 同凭据

**现象**：同一份 `config.yaml` 的 `fallback_providers` 在不同渠道（飞书网关 vs 桌面 app）**实际凭据可能不同**。

**根因**：凭据按「进程启动时环境快照 + `$HERMES_HOME/.env`」解析，飞书网关（`gateway run` 重启后）与桌面 app（`serve` 随 app 启动长驻）**进程谱系不同**。

**实测**：
- 桌面 app 进程：内存里残留**早已消失的旧 `XIAOMI_API_KEY`** 仍可作为兜底（key 在 os.environ 里没被清理）
- 飞书网关进程：同变量悬空、兜底链中间两跳全废 = 等于裸奔

**判断某渠道兜底是否真实可用**：

```python
import psutil
proc = psutil.Process(<gateway_pid>)  # netstat 找 8644 归属 PID
env = proc.environ()
for key in ['MINIMAX_API_KEY', 'XIAOMI_API_KEY', 'GLM_API_KEY', 'DEEPSEEK_API_KEY']:
    val = env.get(key, '<missing>')
    print(f'{key}={val[:10] if val != "<missing>" else val}...')
```

⚠️ **不要信 `hermes auth list` 或 `config.yaml`** —— 那是配置文件层的视角。运行时实际进程环境才是真相。

## 2. MiniMax 错误码 2056 = Token Plan 用量封顶

**症状**：HTTP 200 响应，但 `choices=null`、`base_resp.status_code=2056`、`base_resp.status_msg="已升级 Token Plan 套餐或购买积分补充用量"`。

**陷阱**：HTTP 200 = "请求成功" ≠ "有内容"。前端/agent 看到 200 以为调用成功，但实际返回空 body。

**判断**：

```python
resp = client.chat(...)
if resp.get('choices') is None:
    base = resp.get('base_resp', {})
    if base.get('status_code') == 2056:
        # Token Plan 用量封顶
        ...
```

**缓解**：
- 启用 fallback model（mimo-v2.5 本机 LLM 不耗 token）
- 飞书评论 agent 配置成 fallback model（避免命中 MiniMax 2056）
- 主聊天模型保持 MiniMax，评论/批量任务用 fallback

## 3. 判断「没兜底」先看 attempt 3/3 失败

**陷阱**：观察 `fallback_active` 字段、log 的 "fallback to ..." 行——这些都是**过程信号**，不能作为最终判断。

**最终判定**：必须看 `attempt 3/3 failed`——三个 provider 都没回非空 response。

**判定序列**：
1. 看 `base_resp.status_code` 是否 2056（MiniMax 封顶）
2. 看 attempt count：1=主模型，2=第一个 fallback，3=第二个 fallback
3. 看每个 attempt 的 `choices` 是否 `null`
4. **三个都 null** → 兜底链真实失败
5. **某个非 null** → 兜底成功，看 log "fallback to X"

## 4. 凭据更新要走 `setx` + 重启进程

**陷阱**：`os.environ["KEY"] = new_value` 在**当前 Python 进程**生效，但 gateway 进程是另一个进程谱系。

**正确流程**（Windows）：
```powershell
setx MINIMAX_API_KEY "sk-new-key"
# 然后：powershell Stop-Process -Id <gateway_pid> -Force
# 然后：schtasks /Run /TN \Hermes_Gateway
```

**验证**：
```python
import psutil
proc = psutil.Process(<new_gateway_pid>)
print(proc.environ().get('MINIMAX_API_KEY', '<missing>')[:10])
```

⚠️ **不要信 `os.environ.get`** 在测试脚本里 —— 测试脚本是新进程，凭据从 .env 重读，跟 gateway 进程无关。

## 5. L1 端到端验证：4 个测试 case 必跑

测试场景（每次改 provider/fallback 配置后）：

| Case | 验证目标 |
|------|----------|
| 桌面 chat：MiniMax 主 | `attempt=1, choices!=null` |
| 桌面 chat：MiniMax 2056 触发 | `attempt=1 fail → attempt=2 fallback 成功` |
| 桌面 chat：MiniMax + mimo 双失败 | `attempt=3 fail → "all failed"` |
| 飞书网关：comment agent | 走的 fallback model（非 MiniMax），不触发 2056 |

## 验证清单（每次改 provider 后跑）

- [ ] `psutil` 读 gateway 进程 environ() 确认所有 key 都在
- [ ] `curl -X POST :8644/v1/chat/completions` trigger 新会话 → 看 agent.log 启动 attempt 序列
- [ ] 故意把主模型 key 改错 → 验证 fallback 真的接手
- [ ] 改回正确 key → 验证恢复
- [ ] 监控 5 分钟，看没有 `2056` 错误码（如有，fallback 配置可能漏了某个 model）

## 相关 skill

- `hermes-maintenance`：gateway 进程启停、wmic/psutil 跨平台诊断
- `hermes-monitoring`：cron 任务监控 + 网关健康检查
- `hermes-agent`：provider 抽象层、model 配置参考
## 6. TDB/TencentDB pipeline LLM 端点配置实战（2026-08-27 实战）

> 本节是上面 5 节的延伸，专门覆盖 **TDB memory-core 容器的 LLM 端点配置**——这是 L1 提炼 pipeline（mimo 抽取 episodic/persona/instruction）调用的端点，错配会直接导致 `extracted=0`。

### 6.1 三层配置优先级

TDB container 的 LLM 端点读取顺序（`/app/src/gateway/config.ts:451`）：

```ts
baseUrl: env("TDAI_LLM_BASE_URL") ?? str(llmConfig, "baseUrl") ?? "https://api.openai.com/v1"
```

| 优先级 | 来源 | 何时生效 |
|--------|------|----------|
| 1 | `TDAI_LLM_BASE_URL` 环境变量 | docker-compose `environment:` 块 |
| 2 | yaml `llm.baseUrl`（驼峰）| `config/tdai-gateway.yaml` |
| 3 | fallback `https://api.openai.com/v1` | 代码写死 |

**坑：yaml 字段名错配**（2026-08-27 实战）

yaml 写 `base_url: "https://api.xiaomimimo.com/v1"`（下划线），但代码读 `llmGroup["baseUrl"]`（驼峰）。`str()` 函数（`/app/src/config.ts:679`）**不做下划线↔驼峰转换**——只读 `src[key]` 直接查找。结果 yaml 解析失败 → fallback 到 `api.openai.com` → NAS 防火墙拦截 → L1 抽取 `extracted=0, stored=0`。

**修法**：env var 优先级最高，直接覆盖 yaml 字段名错配：

```yaml
# /home/HMSJadmin/tdb-v3/docker-compose.yml
services:
  memory-core:
    image: agentmemory/memory-core:latest
    environment:
      - TDAI_LLM_BASE_URL=https://api.xiaomimimo.com/v1
      - TDAI_LLM_API_KEY=***
      - TDAI_LLM_MODEL=mimo-v2.5
      - TDAI_LLM_PROVIDER=openai
```

⚠️ **yaml 字段名兼容需验证**：TDB v3 容器代码是否支持 `base_url`（下划线）→ 直接读 yaml 文件 + 搜 `str(llmConfig,` 看用了什么 key。

### 6.2 NAS 防火墙白名单（出网限制）

绿联 UGOS 走 iptables 路径拦截——但只拦特定域名：

| 域名 | 状态 | 用途 |
|------|------|------|
| `api.openai.com` | ❌ **拦截** | OpenAI 官方 |
| `api.xiaomimimo.com` | ✅ 通 | mimo |
| `api.siliconflow.cn` | ✅ 通 | bge-m3 embedding |
| `github.com` / `pypi.org` / `npmjs.com` | ✅ 通 | git/pip/npm |
| `registry-1.docker.io` / `registry.docker.io` | ❌ 拦截 | docker pull |
| `quay.io` / `doh.pub` | ✅ 通 | 镜像/DoH |

**验证端点不被拦截**：

```bash
# 在 NAS 上执行（不是本机！防火墙是 NAS 的）
ssh HMSJadmin@hmsj.local "curl -s -m 5 -X POST https://api.openai.com/v1/chat/completions -H 'Authorization: Bearer test' -d '{}' 2>&1 | head -1"
# 输出 "Connection timed out" → 被拦截
```

### 6.3 docker compose env var 必须 down + up 才生效

`docker compose stop/start` **不重读 .env / 不重读 compose.yml**——只重启进程，不重建容器环境。

**正确动作**：

```bash
cd /home/HMSJadmin/tdb-v3
docker compose down memory-core    # 删容器（env 不变，但 env 注入到容器进程）
docker compose up -d memory-core  # 重建容器（重新读 compose.yml environment 块）
```

⚠️ **端口冲突**：如果有多个 compose 占同一端口（比如 `tencentdb-gateway:2.0.0` 单容器版和 `memory-core` v3 三件套都想占 8420），`down + up` 会失败 `port is already allocated`——必须先 `down` 旧的，或改端口。

### 6.4 Hermes 输出流脱敏陷阱

所有 `sk-`-前缀字符串在 Hermes 工具输出时会被 mask（中间 30+ 字符 → `sk-mem...TfPz` 或 `sk-cwm...jx88`）。

**症状**：
- `.env` 里 `XIAOMI_API_KEY=***`（被脱敏显示）
- `docker inspect` 输出 env 也是脱敏版
- `docker exec <container> node -e 'console.log(process.env.LLM_API_KEY)'` 也是脱敏版
- 本机 `curl` 测试 `*** ` → "Invalid API Key"

**陷阱**：脱敏后 `docker-compose.yml` 里写的字面值就是这个脱敏字符串——**不是真实 key**！重启后 L1 调用 `Invalid API Key`。

**正确姿势**：
1. 在 hermes 桌面对话里直接说"把 mimo key 写到 NAS 的 tdb-core docker-compose"
2. 或手动 SSH 上去直接编辑文件（绕过 Hermes 输出流）
3. 或用 base64 编码贴 key，agent 解码后用 `printf` / `tee` 写文件

**验证 key 是否有效**（在 NAS 容器内直连）：

```bash
ssh HMSJadmin@hmsj.local "export PATH=/overlay/upper/usr/bin:/usr/bin:/bin && docker exec tdb-core node -e '
fetch(\"https://api.xiaomimimo.com/v1/chat/completions\", {
  method: \"POST\",
  headers: {\"Content-Type\":\"application/json\",\"Authorization\":\"Bearer \" + process.env.TDAI_LLM_API_KEY},
  body: JSON.stringify({model:\"mimo-v2.5\",messages:[{role:\"user\",content:\"hi\"}],max_tokens:20})
}).then(r => r.text()).then(t => console.log(t.substring(0,200)));
'"
```

如果输出 `{"error":{"code":"401","type":"invalid_key"}}` → key 无效（占位符或脱敏字符串）。

### 6.5 端到端 L1 验证流程

TDB LLM 端点修复后必须做的 4 步验证：

1. **端点正确性**（NAS 防火墙层）：
   ```bash
   docker logs tdb-core --tail 100 | grep -iE 'api.openai|api.xiaomi'
   ```
   - ✅ 只看到 mimo 相关 → 端点修对了
   - ❌ 看到 `api.openai.com` → 还在走 fallback

2. **LLM API Key 有效性**：
   ```bash
   docker logs tdb-core --tail 100 | grep -iE 'Invalid API Key|connect timeout'
   ```
   - ✅ 没有错误 → key 有效
   - ❌ "Invalid API Key" → key 是占位符，需用户更新
   - ❌ "Connect Timeout" → NAS 防火墙拦截

3. **L1 抽取结果**：
   ```bash
   docker logs tdb-core --tail 200 | grep -E 'L1 complete'
   ```
   - ✅ `extracted=N, stored=N` (N > 0) → 抽取成功
   - ❌ `extracted=0, stored=0` → 端点/key 仍有问题

4. **三 type 可查**（1-2h 后）：
   ```bash
   for t in episodic persona instruction; do
     curl -s -X POST http://192.168.1.2:8420/v2/atomic/query \
       -H 'Authorization: Bearer sk-mimo-key' \
       -H 'x-tdai-service-id: default' \
       -H 'Content-Type: application/json' \
       -d "{\"type\":\"$t\",\"limit\":1}" | python -c "import json,sys; d=json.loads(sys.stdin.read()); print('$t total:', d.get('data',{}).get('total',0))"
   done
   ```

## 相关 skill

- `tencentdb-gateway`：TDB Krolik v2/v3 协议端点、容器内代码定位（受保护不能改）
- `hermes-maintenance`：gateway 进程启停、wmic/psutil 跨平台诊断
- `hermes-monitoring`：cron 任务监控 + 网关健康检查
- `hermes-agent`：provider 抽象层、model 配置参考

## 支持文件

- `references/tdb-l1-endpoint-fix.md`：TDB L1 pipeline 端点修复完整实战案例（背景/排查/修复/验证/遗留，含完整时间线）
- `scripts/tdb_l1_diag.py`：一键诊断脚本（7 步端到端：health/env/yaml/防火墙/容器直连/L1 结果/诊断结论）

