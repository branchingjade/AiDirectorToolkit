# TDB L1 Pipeline 端点配置实战案例（2026-08-27）

> 本文件是 `hermes-provider-fallback` skill 的实战案例，完整记录了一次端点错配 → 定位 →修复 →验证 →遗留的全过程。
> 引用：上层 SKILL.md 第 6 节「TDB/TencentDB pipeline LLM 端点配置实战」。

## 背景

TDB 三件套（tdb-core/hub/proxy）跑在 NAS（hmsj.local）。L1 pipeline 在 tdb-core 容器里跑，调用外部 LLM 提炼 L0 conversation 到 episodic/persona/instruction。

## 症状

灌入 9722 条 Hindsight + 541 条 Vault + 11 份 Profiles 后，TDB L0 conversation 涨到 28894 行，但 L1 永远 `extracted=0, stored=0`。

```bash
docker logs tdb-core --tail 100 | grep -E 'L1 complete'
# INFO  [tdai-gateway] [pipeline-factory] [l1] L1 complete: extracted=0, stored=0 (1 group(s))

docker logs tdb-core --tail 100 | grep -iE 'error|fail'
# ERROR [standalone-runner] run() failed: Cannot connect to API: Connect Timeout Error
#   (attempted address: api.openai.com:443, timeout: 10000ms)
# ERROR [l1-extractor] LLM extraction failed
```

**根因信号**：`api.openai.com:443` —— 我们配的明明是 mimo（`api.xiaomimimo.com`），为什么 L1 走的是 openai？

## 排查过程

### 第 1 步：看容器 env

```bash
ssh HMSJadmin@hmsj.local "docker inspect tdb-core --format '{{json .Config.Env}}'"
```

发现 `tdb-core` 容器**完全没有** `TDAI_LLM_*` 环境变量，只挂了 volumes。

### 第 2 步：读容器代码

```bash
ssh HMSJadmin@hmsj.local "docker exec tdb-core sh -c 'sed -n \"440,475p\" /app/src/gateway/config.ts'"
```

```ts
baseUrl: env("TDAI_LLM_BASE_URL") ?? str(llmConfig, "baseUrl") ?? "https://api.openai.com/v1",
apiKey: env("T...EY") ?? str(llmConfig, "apiKey") ?? "",
model: env("TDAI_LLM_MODEL") ?? str(llmConfig, "model") ?? "gpt-4o",
```

**优先级链**：
1. env var（缺 → fallback）
2. yaml `llm.baseUrl`（驼峰）
3. fallback `api.openai.com`

### 第 3 步：读 yaml

```bash
ssh HMSJadmin@hmsj.local "docker exec tdb-core sh -c 'cat /data/config/tdai-gateway.yaml'"
```

```yaml
llm:
  provider: "custom"
  base_url: "https://api.xiaomimimo.com/v1"   # ⚠️ 下划线
  api_key: "sk-cwm...jx88"                      # ⚠️ 脱敏占位符
  model: "mimo-v2.5"
```

yaml 写 `base_url`（下划线），但代码读 `llmGroup["baseUrl"]`（驼峰）—— **`str()` 函数不做下划线↔驼峰转换**（`/app/src/config.ts:679` 直接 `src[key]`）。

**结果**：`str(llmConfig, "baseUrl")` 返回 undefined → fallback 到 `api.openai.com` → NAS防火墙拦截 → `extracted=0`。

### 第 4 步：验证 NAS 防火墙

```bash
ssh HMSJadmin@hmsj.local "curl -m 5 https://api.openai.com/v1/chat/completions"
# Connection timed out   ← 防火墙拦截

ssh HMSJadmin@hmsj.local "curl -m 5 https://api.xiaomimimo.com/v1/chat/completions"
# （不报错，可达）   ← 防火墙放行
```

## 修复动作

`/home/HMSJadmin/tdb-v3/docker-compose.yml` 加 env vars（绕过 yaml 字段名错配）：

```yaml
services:
  memory-core:
    image: agentmemory/memory-core:latest
    container_name: tdb-core
    volumes:
      - ./config/tdai-gateway.yaml:/data/config/tdai-gateway.yaml
      - core-data:/data/tdai-memory
    environment:                          # ← 新增
      - TDAI_LLM_BASE_URL=https://api.xiaomimimo.com/v1
      - TDAI_LLM_API_KEY=***
      - TDAI_LLM_MODEL=mimo-v2.5
      - TDAI_LLM_PROVIDER=openai
```

```bash
cd /home/HMSJadmin/tdb-v3
docker compose down memory-core
docker compose up -d memory-core
sleep 15
curl -s http://192.168.1.2:8420/health
# {"status":"ok",...}
```

## 验证

### 端点修复成功

```bash
docker logs tdb-core --tail 50 | grep -iE 'api\.'
# 不再出现 api.openai.com  ← ✅ 端点修对
docker logs tdb-core --tail 50 | grep -iE 'error'
# Invalid API Key          ← ✅ 现在是 key 问题，不是端点问题
```

### Key 是脱敏占位符

⚠️ **关键陷阱**：compose 文件里 `TDAI_LLM_API_KEY=***` 是 Hermes 输出流脱敏显示的占位符。`docker inspect` / `process.env.LLM_API_KEY` 都看不到真实值。

```bash
# 在容器内直连测试
docker exec tdb-core node -e '
fetch("https://api.xiaomimimo.com/v1/chat/completions", {
  method: "POST",
  headers: {"Content-Type":"application/json", "Authorization":"Bearer " + process.env.TDAI_LLM_API_KEY},
  body: JSON.stringify({model:"mimo-v2.5", messages:[{role:"user",content:"hi"}], max_tokens:20})
}).then(r => r.text()).then(t => console.log(t.substring(0,200)))'
# {"error":{"message":"Invalid API Key","code":"401","type":"invalid_key"}}
```

**结论**：key 是脱敏占位符，不是真实值。

## 遗留：用户需手动更新 key

**方案 A**：在 hermes 桌面对话里直接说"把 mimo key 写到 NAS 的 tdb-core docker-compose"——但 key 在对话里也会被脱敏。

**方案 B**：手动 SSH 上去直接编辑：

```bash
ssh HMSJadmin@hmsj.local "vi /home/HMSJadmin/tdb-v3/docker-compose.yml"
# 改 TDAI_LLM_API_KEY=*** → TDAI_LLM_API_KEY=sk-真实key
# 保存后重启
cd /home/HMSJadmin/tdb-v3 && docker compose down memory-core && docker compose up -d memory-core
```

**方案 C**：用 base64 编码贴 key，agent 解码后 `tee` 写文件。

## 时间线

- 21:33 Phase 1 备份冻结
- 21:35 Phase 2 TDB 切换 + DSH 归档（commit `8021856`）
- 21:50 Phase 3+4 知识库灌入 + 双路 recall（commit `cd4932a`）
- 22:40 Phase 6 MEMORY 精简（commit `9432750`）
- 22:50 Phase 7 Hindsight 停用 + 收尾
- 22:55 Phase 10 L1 端点诊断 → 发现 openai.com
- 23:00 Phase 11 端点修复（env var 覆盖）→ 端点 OK，key 待更新

## 关键经验总结

1. **优先用 env var**（不用 yaml）——env var 字段名是代码直接读的，不会被 yaml 命名风格错配影响
2. **docker compose down + up** 才能让 env 生效（不是 stop/start）
3. **NAS 防火墙**只拦特定域名，验证 LLM 端点**必须先在 NAS 上 curl**——本机通不代表 NAS 通
4. **Hermes 输出流脱敏**所有 `sk-`-前缀字符串——key 显示出来一定是脱敏版，真实值要走非对话通道