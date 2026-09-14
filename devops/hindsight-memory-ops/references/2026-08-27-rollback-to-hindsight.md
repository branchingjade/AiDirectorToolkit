# 回滚：外部记忆从 TencentDB(TDB) 换回 Hindsight（2026-08-27 实测闭环）

用户诉求原话：「先把外部记忆改回 hindsight+obsidian 那套用着，后面 TDB 确认能用在切换 TDB」。
即**临时回滚，保留 TDB 配置随时切回**。本文是完整动作 + 本次踩到的 4 个真坑。

Hindsight 版本：**0.9.2**（hindsight-all / hindsight-client / hindsight-embed / hindsight-api-slim）。
本文所有命令在 Windows + git-bash + uv venv 下实测通过。

---

## 0. 回滚 ≠ 拆卸：只改一行 provider

```bash
cd ~/AppData/Local/hermes
cp config.yaml config-pre-hindsight-rollback-<日期>.yaml   # 先备份
```

`config.yaml` 的 `memory:` 段：

```yaml
# 回滚前（TDB）
  provider: memory_tencentdb
  env:
    MEMORY_TENCENTDB_GATEWAY_HOST: 192.168.1.2
    MEMORY_TENCENTDB_GATEWAY_PORT: '8420'
  tencentdb_gateway_host: 192.168.1.2
  tencentdb_gateway_port: 8420

# 回滚后（Hindsight）
  provider: hindsight
```

**TDB 的 `memory_tencentdb` 插件目录和 NAS 服务都不动**——用户明说「后面 TDB 确认能用再切」，切回去就是把这段改回来。
验证：`hermes memory status` → `Provider: hindsight` + `Status: available ✓` + 插件列表里 `hindsight ← active`。

Obsidian 那套**不需要任何动作**：项目资产写 Obsidian 目录 + git 归档，本来就不依赖 memory provider。

---

## 坑 1（最重要）：0.9.x 起 daemon 必须用 embed CLI 启动

旧文档（本 skill 的 8-13 / 8-17 章节）教的 `pythonw -m hindsight_api.main --daemon --idle-timeout 0` 在 0.9.2 上**必挂**：

```
ValueError: LLM API key is required. Set HINDSIGHT_API_LLM_API_KEY environment variable.
```

因为 key 存在 `~/.hindsight/profiles/hermes.env`，而**只有 `hindsight-embed` CLI 会加载 profile env**，裸 `python -m hindsight_api.main` 不会。

正确启动/停止/查状态（`-p hermes` 是 profile 名，对应 `~/.hindsight/profiles/hermes.env`）：

```bash
cd ~/AppData/Local/hermes
hermes-agent/venv/Scripts/hindsight-embed.exe -p hermes daemon start
hermes-agent/venv/Scripts/hindsight-embed.exe -p hermes daemon status
hermes-agent/venv/Scripts/hindsight-embed.exe -p hermes daemon stop
```

- **没有 `daemon restart` 子命令**（只有 start/stop/status/logs）——重启 = stop → sleep 15 → start
- 裸跑 `hindsight-embed.exe` 不带子命令 = 打印 help 后 exit 1（别误以为是崩溃）
- 启动需 **60~100 秒**（alembic migrations + bge embedding + cross-encoder 加载），别在 40s 内下结论
- 起来后：`daemon status` 显示 `✓ Daemon Running (hermes @ :9177)`，`curl -o /dev/null -w "%{http_code}" http://127.0.0.1:9177/health` = 200
- `daemon stop` 可能抛 `SystemError: <class 'OSError'> returned a result with an exception set`（`_kill_process` 的 `os.kill(pid,0)` 在 Windows 上的已知噪音）——**不影响停止结果**，随后 start 正常

### 连带修复：守护脚本 `hindsight_daemon_guard.py` 的 launch() 是坏的

计划任务 `Hermes_Hindsight_Daemon`（每 5 分钟）跑的 `~/AppData/Local/hermes/scripts/hindsight_daemon_guard.py`，其 `launch()` 用的就是上面那条会崩的旧命令 —— **任务启用了也拉不起来，且静默**（Popen 不等结果）。

已改为：

```python
PROFILE = os.environ.get("HINDSIGHT_PROFILE", "hermes")
...
def launch() -> bool:
    embed_cli = os.path.join(HERMES_HOME, "hermes-agent", "venv", "Scripts", "hindsight-embed.exe")
    subprocess.Popen([embed_cli, "-p", PROFILE, "daemon", "start"],
                     cwd=HERMES_HOME, creationflags=subprocess.CREATE_NO_WINDOW)
```

启用任务：`schtasks /Change /TN "Hermes_Hindsight_Daemon" /ENABLE`
**验证守护真能自愈**（不要只看 Status: Ready）：`daemon stop` → 跑 `python "C:/Users/HMSJ/AppData/Local/hermes/scripts/hindsight_daemon_guard.py" --force` → 等 100s → `daemon status` 应 Running。

> 注意任务的 `Task To Run` 指向 `~/AppData/Local/hermes/scripts/` 那份，**不是** `~/Documents/Hermes/scripts/_archive/` 的归档副本。改错文件等于没改（归档副本只是备份，不必同步）。

---

## 坑 2：0.9.x 的 retain API 端点/字段全变了

三次 4xx 才摸对，**先查 openapi.json 再动手，别照旧文档拼 URL**：

```bash
curl -sS http://127.0.0.1:9177/openapi.json -o "$LOCALAPPDATA/Temp/hs-api.json"
python -c "
import json; d=json.load(open(r'C:/Users/HMSJ/AppData/Local/Temp/hs-api.json',encoding='utf-8'))
for p,v in d['paths'].items():
    if 'memor' in p: print(','.join(m.upper() for m in v), p)
"
```

| 操作 | 端点 | 方法 |
|---|---|---|
| retain 写入 | `/v1/default/banks/{bank}/memories` | POST |
| recall 检索 | `/v1/default/banks/{bank}/memories/recall` | POST |
| 列举 | `/v1/default/banks/{bank}/memories/list?limit=N` | GET |
| 删除单条 | `/v1/default/banks/{bank}/memories/{id}` | ~~无~~（只有 observations 级 DELETE） |

- `POST /memories/retain` → **405**（该路径不存在，retain 就是 `POST /memories` 本身）
- body 用 `{"content": "..."}` → **422**，日志 `Unknown parameters ignored: [content]`
- 正确 body（`RetainRequest.items[] → MemoryItem.content` 必填）：
  ```json
  {"items": [{"content": "要记的事实"}], "async": false}
  ```
- 成功返回 `{"success": true, "items_count": 1, "usage": {...}}`

---

## 坑 3（本次真 bug）：recall 能通 ≠ 记忆能用 —— 必须双向测

**症状**：recall 一切正常（读出伏妖记/魔王/山神设定等历史记忆），但 retain 一律 **HTTP 500**。

**根因**：`~/.hindsight/profiles/hermes.env` 里的 **DeepSeek key 已失效**。
`hermes.log` 实证：
```
Auth error (HTTP 401) ... 'Authentication Fails, Your api key: ****c576 is invalid'
RuntimeError: Fact extraction failed: 1/1 chunks failed
```
`auth.json` 的凭据池同样标记：`deepseek → last_status: exhausted, last_error_code: 401`。

**为什么单测 recall 会漏掉**：
- recall = 纯本地向量/BM25 检索，**不调 LLM** → key 废了照样绿
- retain = 需要 LLM 抽取事实 → key 废了必挂

> **铁律：验证 Hindsight 可用性必须 retain + recall 双向测。**
> 只测 recall 就交差 = 用户第二天写记忆静默失败。本 skill 旧章节全是 recall 验证流程，这是缺口。

**修复（换 LLM，用户拍板 mimo-v2.5）—— 三处必须同步，漏一处 provider 自拉 daemon 时 key 为空**：

| # | 文件 | 改什么 |
|---|---|---|
| 1 | `~/.hindsight/profiles/hermes.env` | `HINDSIGHT_API_LLM_API_KEY` / `_MODEL=mimo-v2.5` / `_BASE_URL=https://api.xiaomimimo.com/v1`（`_PROVIDER` 保持 `openai`，OpenAI 兼容） |
| 2 | `~/AppData/Local/hermes/hindsight/config.json` | `llm_model` / `llm_base_url`（`llm_provider` 保持 `openai_compatible`） |
| 3 | `~/AppData/Local/hermes/.env` | 追加 `HINDSIGHT_LLM_API_KEY=<key>` —— plugin 走 `get_secret("HINDSIGHT_LLM_API_KEY")` 取 key，**config.json 不存 key** |

改完必须 stop→start daemon 才生效。每份改前 `cp` 一份 `.bak-<日期>-<原因>`。

**换 key 前先测哪个 key 是活的**（本机 `.env` 里的候选批量打一发 `/chat/completions`）：
```python
# minimax → 404（base_url 现为 https://api.minimaxi.com/anthropic，非 OpenAI 格式）
# xiaomi  → 200 choices OK   https://api.xiaomimimo.com/v1  mimo-v2.5
# glm     → 200 choices OK   https://open.bigmodel.cn/api/coding/paas/v4  glm-4.5-flash
```

---

## 坑 4：随机标记串验不了写入（用 list 而非 recall 收尾）

写入验证时给内容打 `ROLLBACK-VERIFY-<timestamp>` 标记，然后 recall 该标记 → **命中 False**。
不是没写进去 —— 随机数字串无语义，embedding/BM25 匹配不到。

**正确收尾**：`GET /memories/list?limit=15` 看最新条目 + `total`：
```
total: 9974          ← 历史数据完好
[HIT] 2026-08-27 外部记忆从 TencentDB 回滚到 Hindsight。
[HIT] DeepSeek key 已失效（401），导致 Hindsight 的 LLM 改用 mimo-v2.5（小米）。
[HIT] 守护脚本 launch() 改走 hindsight-embed CLI。
```
retain 会把一条输入**拆成多条事实**（本次 1 条 → 4 条），list 里能看到拆分结果 = 抽取链路真通。

---

## 重装依赖（本次 `hindsight_api` 模块曾整体缺失）

```bash
cd ~/AppData/Local/hermes/hermes-agent
python -m pip install 'hindsight-all==0.9.2'     # 装齐 api-slim/client/embed
python -c "import hindsight_api; print('ok')"
```

**副作用要主动报给用户**（本次实测降级）：
- `mcp 2.0.0 → 1.29.1`
- `onnxruntime 1.27.0 → 1.20.1`
- `boto3` 换版本

`hermes --version` / `hermes memory status` 均正常，但 MCP 相关功能未逐项回归。若之后 MCP 服务器连不上，根因在此。
⚠️ `hermes tools` 会进**交互式向导**（问 Nous Portal 登录）→ 前台跑会超时卡住，别用它做冒烟测试。

---

## 完整验证清单（回滚收尾，缺一不可）

1. `hermes memory status` → `Provider: hindsight` / `available ✓` / `hindsight ← active`
2. `daemon status` → `✓ Daemon Running (hermes @ :9177)`；`netstat -ano | grep ':9177' | grep LISTENING` **只有一个 PID**（多实例会互抢 9177）
3. `curl /health` → 200
4. **retain**：`POST /memories` with `{"items":[{"content":"..."}]}` → `success: true`
5. **recall**：POST `/memories/recall` 用**有语义的历史关键词**（如项目名）→ 能读出旧记忆
6. **list**：`GET /memories/list?limit=15` → `total` 量级正常（本次 9974）+ 新写入的事实在库顶
7. 守护自愈：stop daemon → 跑 guard `--force` → 100s 后 Running

---

## 本次杂项

- `hindsight-embed` 的 `hermes.log` 里 `[WORKER_STATS]` 每 30s 一条是正常心跳，不是故障
- 数据目录 `~/.hindsight`（24M）+ pg0 库 `~/.pg0/instances/hindsight-embed-hermes` 停用期间完好，回滚零数据损失
- MSYS 路径坑复现：`python ~/Documents/...` 会被转成 `C:\c\Users\...` 报 No such file —— 给原生程序传路径用 `"C:/Users/..."` 正斜杠形式
