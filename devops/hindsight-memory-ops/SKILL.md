---
name: hindsight-memory-ops
description: Hindsight 记忆运维：recall 验证、双实例陷阱。触发词：hindsight、记忆验证。
---

# Hindsight Memory Ops

Hindsight 是 Hermes 的外部记忆后端（memory.provider=hindsight，本地嵌入式）。本 skill 覆盖：recall 验证工作流、consolidation 进度检查、pg0 数据库直查、已知陷阱。凡涉及「Hindsight 能不能召回 X / 记忆积压 / 飞书内容入库」的任务先读本 skill。

## 架构事实（本机实测 2026-08-07）

| 组件 | 位置/端口 | 说明 |
|------|-----------|------|
| API 服务 | `hindsight-api.exe`（venv/Scripts/），端口 9177 | 空闲 300s 自动关闭，无活跃会话时 9177 不监听 |
| Hermes 侧配置 | `~/AppData/Local/hermes/hindsight/config.json` | recall_types="observation"、recall_budget="mid"、bank_id="hermes" |
| 环境配置 | `~/.hindsight/profiles/hermes.env` | LLM key/model/API_PORT（source 后直接可用） |
| 日志 | `~/.hindsight/profiles/hermes.log` | consolidation 进度（processed=N/M）、retain 记录 |
| 数据库 | 嵌入式 pg0（PostgreSQL 18.1），**两个实例** | ⚠️ 见下方陷阱 |

## ⚠️ 双实例陷阱（最重要，先读）

本机存在两个 pg0 PostgreSQL 实例：

| 实例 | 端口 | 内容 | 谁在用 |
|------|------|------|--------|
| `hindsight` | 5434 | **空库（0 节点）** | hindsight-api 不设 DATABASE_URL 时的默认连接 |
| `hindsight-embed-hermes` | 5433 | **真实数据**（2026-08-07：2117 节点/27 文档/721 observations） | hindsight-embed daemon |

**后果**：手动启动 `hindsight-api.exe` 不设 `HINDSIGHT_API_DATABASE_URL` → 连到 5434 空库 → recall 全部返回 0 结果 = 假性「0 召回」。2026-08-07 验证曾因此误判「飞书内容未打通」，实际是连错库。**任何 recall 全 0 的结果，先查 `/stats` 的 `total_nodes`：0 就是连错库，不是内容缺失。**

## 手动启动 API（验证时用）

```bash
cd ~/AppData/Local/hermes/hermes-agent/venv/Scripts/
set -a && source ~/.hindsight/profiles/hermes.env && set +a
export HINDSIGHT_API_DATABASE_URL="postgresql://hindsight:hindsight@127.0.0.1:5433/hindsight"
./hindsight-api.exe --port 9177 --idle-timeout 900
```

- 必须 source hermes.env，否则缺 `HINDSIGHT_API_LLM_API_KEY` 直接 ValueError 退出（traceback 里会明说）
- 必须显式 export DATABASE_URL 指向 5433；凭据 `hindsight/hindsight` 可从 `~/.pg0/instances/hindsight-embed-hermes/instance.json` 的 username/password/database 字段核验
- 模型加载慢（bge-small embeddings + cross-encoder reranker），等 30~60s 端口才监听，`netstat -ano | grep 9177` 确认
- 用完 kill 手动进程；Hermes gateway 会按需自拉 daemon（`--daemon` 模式在 Windows 下日志会丢失，优先用前台 background 模式）

## Recall 验证工作流

1. **查消化进度**：`grep -E "processed=" ~/.hindsight/profiles/hermes.log | tail -5`（如 processed=34/69 → 该批次还剩 35 条）
2. **查 bank 统计**：`curl http://127.0.0.1:9177/v1/default/banks/hermes/stats` → `total_nodes` / `total_observations` / `pending_consolidation`（total_nodes=0 → 连错库，回到双实例陷阱）
3. **调 recall API**：POST `/v1/default/banks/{bank_id}/memories/recall`，body：
   ```json
   {"query": "关键词", "types": ["observation"], "budget": "high", "max_tokens": 8192}
   ```
   - types 缺省 = world+experience（不含 observation）；要全查传 `["world","experience","observation"]`
   - **中文查询词必须用 Python urllib/requests 发**（bash 里中文 JSON 被转义 → HTTP 400 "error parsing the body"），或 write_file 落盘 JSON 再 `curl -d @file`
4. **判定**：搜到目标内容 → 打通；全 0 → 先排除双实例陷阱，再看 consolidation 积压是否未消化（observation 类型才代表已提炼）

## 数据库直查（绕过 recall 验证数据层）

```python
import psycopg2
conn = psycopg2.connect(host='127.0.0.1', port=5433, user='hindsight', password='hindsight', dbname='hindsight')
# 表 memory_units：text 存事实，fact_type ∈ (world/experience/observation)
# SELECT fact_type, COUNT(*) FROM memory_units GROUP BY fact_type
# SELECT COUNT(*) FROM memory_units WHERE text LIKE '%关键词%'   ← 数据层是否已有内容
# consolidated_at 字段 = 消化时间（NULL=未消化）
```

- **数据层有 ≠ recall 能召回**：召回还依赖 embedding/BM25/排序，占比少 + 时间衰减的内容会被排到后面（飞书内容实测排在 6~36 位，被伏妖记等大占比桌面内容挤占）
- observation = 已 consolidation 提炼；world/experience = 原始事实
- 完整可复用脚本见 `scripts/recall_check.py`（启动 API → 多查询 recall → 标记飞书/桌面）

## 验证结论存档（2026-08-07）

- recall 对飞书内容**已打通**：魔王六人分工 / 神域审讯 23 镜 / 收购谈判线（八千万债务局/九十三万定价/和平方案/强制回收）/ 魏宁馨导演身份均可召回
- Obsidian `_hermes/` 项目记忆可降级为 git 归档（保留不删；新会话内容仍在积压队列时归档是低成本保险）
- consolidation 慢是 DeepSeek 单条 3~95s 所致（预期行为）；积压数字随 retain 持续上涨（129→297），不是故障信号

## 陷阱速查

- recall 全 0 → 先查 stats.total_nodes，0 = 连错库（5434 vs 5433）
- 手动启动 API → 必须 source hermes.env + export DATABASE_URL
- 中文 JSON body → 用 Python 发请求，别用 bash 内联
- 判定「未打通」前 → 确认 consolidation 已消化（observation 计数）且连对库
