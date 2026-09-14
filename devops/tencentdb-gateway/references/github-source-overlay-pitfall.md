# GitHub 源码覆盖 npm 包导致路由丢失（2026-08-27 实战）

## 问题

Docker build 时把 GitHub 仓库的 `src/` 目录 COPY 到 `node_modules/@tencentdb-agent-memory/memory-tencentdb/src`（覆盖 npm 安装的代码），会导致 **所有 v2 路由返回 404**。

## 根因

npm 包 `@tencentdb-agent-memory/memory-tencentdb@latest` 的运行时结构与 GitHub 源码仓库不同：
- npm 包有编译产物、依赖解析、类型声明等
- GitHub 源码是原始 TypeScript，需要编译
- 直接覆盖 src/ 后，server.ts 的 import 路径找不到正确模块

## 实测现象

```
curl -X POST http://127.0.0.1:8420/v2/atomic/query ...
→ {"error":"Not found: POST /v2/atomic/query"}

curl http://127.0.0.1:8420/health
→ {"status":"ok",...}  ← 只有 /health 能用
```

## 正确做法

**不要覆盖 node_modules**——要么改 CMD（env 覆盖 LLM 配置），要么改 base image：

```dockerfile
# ✅ 正确：用现有 prebuilt 镜像，只改启动参数
FROM tencentdb-gateway:2.0.0
# 不 COPY src/，不覆盖 node_modules
# 只改 env 传入新 LLM 配置

# ❌ 错误：COPY src/ over node_modules 会破坏路由
COPY src /opt/tdai-gateway/node_modules/@tencentdb-agent-memory/memory-tencentdb/src
```

## 已验证的修复路径

`tencentdb-gateway:2.0.0` 已经是 prebuilt all-in-one（3.16GB，含 Node 22 + npm 包 + Hermes + TDB Gateway），**不需要重新 build**——直接传 `MODEL_*` env 就能接入新 LLM：

```bash
docker run -d --name tdai-memory \
  -p 8420:8420 \
  --env-file /path/to/.env \
  -e MODEL_API_KEY="sk-..." \
  -e MODEL_BASE_URL="https://api.xiaomimimo.com/v1" \
  -e MODEL_NAME="mimo-v2.5" \
  -e MODEL_PROVIDER="custom" \
  tencentdb-gateway:2.0.0
```

## sed 替换截断长字符串

另一个关联坑：用 `sed -i "s/old/new/"` 编辑 .env 时，正则模式匹配可能截断长字符串（如 API key）：

```bash
# ❌ 会截断：old 模式含 \.\.\.（3 个点），new 也是 \.\.\.，实际写入被截断
sed -i "s/MODEL_API_KEY=sk-c5l\.\.\.ar16/MODEL_API_KEY=sk-c5l...ar16/" .env
# 结果：写入的是 sk-c5l...ar16（截断了！）

# ✅ 正确：整个替换或用精确字符串
sed -i 's/^MODEL_API_KEY=.*/MODEL_API_KEY=<完整key>/' .env
```

**验证**：编辑后 `cat .env | grep MODEL_API_KEY` 确认 key 长度 ≥ 30 字符（mimo key 通常 ~50 字符）。