# Hindsight 记忆库内部结构与访问（2026-08-07 实测）

Hindsight 是 Hermes 的外部记忆 provider（`memory.provider=hindsight`，config.yaml）。记忆数据存**本地内嵌 PostgreSQL**，不是 `~/AppData/Local/hermes/hindsight/`（那里只有 config.json）。

## 存储位置与连接

| 项 | 值 |
|---|---|
| 数据库实例 | `~/.pg0/instances/hindsight-embed-hermes/`（内嵌 PG 18.1.0） |
| 实例配置 | `~/.pg0/instances/hindsight-embed-hermes/instance.json`（含端口/用户/密码） |
| 端口 | 5433（PG），9177（API daemon） |
| 用户/密码/库名 | `hindsight` / `hindsight` / `hindsight` |
| psql 路径 | `~/.pg0/installation/18.1.0/bin/psql.exe` |
| API daemon | `http://127.0.0.1:9177`（/health 探活，openapi.json 有全部端点） |
| 配置 | `~/AppData/Local/hermes/hindsight/config.json`（bank_id=hermes, recall_budget=mid, memory_mode=hybrid） |

psql 直连示例：
```bash
PGPASSWORD=hindsight ~/.pg0/installation/18.1.0/bin/psql.exe \
  -h 127.0.0.1 -p 5433 -U hindsight -d hindsight -c "SELECT ..."
```
⚠️ psql 不在 `installation/bin/`，在 `installation/18.1.0/bin/`（带版本号目录）。Windows 下 psql 输出中文表头乱码是编码问题，不影响数据读取。

## 核心表

- `memory_units`：记忆本体。关键列：`bank_id`、`text`、`fact_type`（experience/world/observation）、`tags`（`character varying[]`，有 GIN 索引）、`embedding`（vector(384)）、`metadata`（jsonb）、`mentioned_at`/`event_date`
- `banks`：bank 定义（当前只有 `hermes` 一个，含 mission/disposition/config jsonb）
- `documents`/`chunks`：记忆来源文档与分块
- `entities`/`entity_cooccurrences`：知识图谱实体
- `mental_models`：跨记忆综合模型
- `async_operations`/`audit_log`：后台 consolidation 任务与审计

## tag 现状（2026-08-07 实测）

- 956 条记忆，946 条有 tag，10 条无 tag
- **全部是系统自动打的会话追踪标签**：`session:20260807_xxx` / `parent:20260807_xxx`，共 10 个不同 tag
- **没有任何语义标签**（如 `project:伏妖记`、`type:偏好`）——语义标签层从未启用
- API 支持任意 tag 打标与通配符查询（`user:*`、`*-admin`），`hindsight_retain` 工具也接受 tags 参数

查 tag 分布：
```bash
# 按 tag 分组计数
SELECT tags, count(*) FROM memory_units WHERE bank_id='hermes' AND cardinality(tags)>0 GROUP BY tags ORDER BY count(*) DESC;
# 有/无 tag 统计
SELECT count(*) AS total, count(*) FILTER (WHERE cardinality(tags)>0) AS with_tags,
       count(*) FILTER (WHERE cardinality(tags)=0) AS no_tags FROM memory_units WHERE bank_id='hermes';
# 按事实类型统计
SELECT fact_type, count(*) FROM memory_units WHERE bank_id='hermes' GROUP BY fact_type;
```

## API 端点（记忆运维相关）

- `GET /health` — daemon 探活
- `GET /v1/default/banks/{bank_id}/tags?q=user:*&source=memories` — 列 tag（支持通配符）
- `GET /v1/default/banks/{bank_id}/memories/list` — 列记忆（分页+全文搜索+类型过滤）
- `POST /v1/default/banks/{bank_id}/memories/recall` — 语义检索 `{"query":"...","limit":N}`
- `GET /v1/default/banks/{bank_id}/stats` — 统计
- `GET /v1/default/banks/{bank_id}/export` — ⚠️ 只导出 bank 模板（配置/mental models/directives），**不是记忆内容导出**（返回 `{"version":"1"}` 15 字节）。备份记忆必须用 pg_dump 或 SQL 查询，不能用这个端点。

## 备份要点（2026-08-07 发现）

`backup-hermes-webdav.py` 打包范围是 `~/.hermes`（残留目录）+ Obsidian Vault + state.db 临时副本——**不含 `~/.pg0/`，记忆库 138MB 裸奔无云备份**。修复方向：
1. `pg_dump` 导出 memory_units 等表（PG 18.1，pg_dump 也在 `~/.pg0/installation/18.1.0/bin/`）
2. 或直接把 `~/.pg0/instances/hindsight-embed-hermes/` 加入打包（138MB，需注意 tar 打包时 PG 在运行，建议先停 daemon 或用 pg_dump 一致性快照）
