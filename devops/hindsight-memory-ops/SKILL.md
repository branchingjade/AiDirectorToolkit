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
| 日志 | `~/.hindsight/profiles/hermes.log` | consolidation 进度（processed=N/M）、retain 记录、Document 列表（确认某会话是否 retain 的直接证据） |
| 数据库 | 嵌入式 pg0（PostgreSQL 18.1），**端口以 netstat + 进程身份实测为准** | ⚠️ 见下方陷阱；端口多次漂移（5433→8475→？），2026-08-13 实测 8475 已被百度网盘进程占用 |

## ⚠️ 端口漂移陷阱（2026-08-08 → 2026-08-13 二次修正）

早期记录 pg0 端口 5433/5434（双实例）；2026-08-08 实测漂移到 8475；**2026-08-13 实测 8475 已被百度网盘进程占用（baidunetdiskhost.exe）——pg0 真相库端口又漂了（instance.json 写 5433，实测无监听）**。**任何端口记录（包括标注「实测」的）都不可信——每次验证三连**：

1. `netstat -ano | grep LISTENING` 找候选端口
2. `powershell -NoProfile -Command "Get-Process -Id <PID> | Select-Object ProcessName, Path"` **确认 ProcessName=postgres 且 Path 含 .pg0 或 hindsight**——8475 的教训：百度网盘照样监听端口，psql 连它会报 `server closed the connection unexpectedly`
3. 再用 psql/API 验证；recall 全 0 → 先查 `/stats` 的 `total_nodes`，0 = 连错库

> 本机其他 postgres 勿连错（都不是 hindsight 真相库）：`C:\Program Files\PostgreSQL\13`（5432）、`C:\Program Files\Common Files\Reallusion\PostgreSQL`（11810）。

## 手动启动 API（验证时用）

> ⚠️ **0.20.0 起架构变更（2026-08-13 实证）**：`venv/Scripts/hindsight-api.exe` **已不存在**——daemon 由 provider 构造时 `_start_daemon` 线程自动拉起（`hindsight_embed.daemon_embed_manager`，python 包）。正常流程无需手动启动；手动启动 API 仅在验证 daemon 异常时兜底（旧版命令保留如下，若 exe 不存在则跳过此节，改查 provider 是否激活）。

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

## 验证结论存档（2026-08-07 → 08-08 定稿）

- recall 对飞书内容**已打通**：魔王六人分工 / 神域审讯 23 镜 / 收购谈判线（八千万债务局/九十三万定价/和平方案/强制回收）/ 魏宁馨导演身份均可召回
- **最终决策（2026-08-08 用户拍板）**：Obsidian `_hermes/项目记忆/` **已删除**（项目事实记忆全面改用 Hindsight），Obsidian 保留四类：会话路由.json/成员名单.json、11 人成员画像、创作成果（伏妖记/犬子无双/剧本库）、`_hermes/memory/` MEMORY.md 镜像
- consolidation 慢是 DeepSeek 单条 3~95s 所致（预期行为）；积压数字随 retain 持续上涨（129→297→119），不是故障信号；积压多轮后消化完成（297→12）recall 即恢复

## ⚠️ 删除 Obsidian 项目记忆的完整流程（2026-08-08 实测，只删目录是坑）

**只删 `_hermes/项目记忆/` 目录不彻底**——gateway 的飞书沉淀钩子 `record_project_memory()` 里有 `path.parent.mkdir(parents=True, exist_ok=True)`，下次有 PROJECT_MEMO 标记时会**自动重建目录**。必须同时停钩子，四处联动：

1. **停沉淀函数**：`hermes-agent/plugins/platforms/feishu/feishu_comment_collab.py` 的 `record_project_memory()` 开头加 `logger.info(...); return False`（保留签名防调用方 NameError），注释标明停用原因和恢复方法
2. **移除提示模板**：`feishu_comment.py` 和 `gateway/run.py` 里教 agent 输出 `PROJECT_MEMO: <事实>` 的 prompt 段落删除（否则 agent 白输出一行被丢弃）
3. **更新 Obsidian 引用**：`_hermes/记忆MOC.md`、`_hermes/飞书协作记忆MOC.md`、`MOC.md` 中项目记忆条目改为「→ Hindsight」说明
4. **同步补丁存档**：`~/Documents/Hermes/scripts/patches/` 下 `hermes-local-patches.diff`（git diff 重新生成）+ `feishu_comment_collab.py` 备份 + `reapply-patches.py` 头部注释更新

**验证**：临时目录打补丁后调用 `record_project_memory('测试','内容')` → 断言返回 False 且目录零文件。改完需重启 gateway 生效（`powershell Stop-Process` 杀 PID → `Start-ScheduledTask Hermes_Gateway`，**勿用 `hermes gateway status/start` CLI**——可能触发 update 恢复流程连带停 gateway）。

**cron 同步**：删项目记忆后，检查涉及它的 cron——`feishu-collab-health.py` 的项目记忆检查块要改为 no-op（否则误报「项目记忆为空」为 ⚠️ 待处理项），cron prompt 里的解读指引同步删除。

## ⚠️ Hindsight 停摆根因模式（2026-08-13 实测：update 依赖失败 → 静默停摆 22h+）

> 完整排查路径 + 修复命令 + 遗留问题见 `references/2026-08-13-outage-recovery.md`。

**症状**：daemon 空闲关闭后不再拉起，retain/recall 全停，无报错（provider best-effort 静默降级，用户无感知）。

**根因链**：`hermes update` 拉新代码后依赖安装失败（`uv pip install -e .` exit 2 → ZIP fallback → `Optional extras failed`）→ hindsight 系列包被移除 → 新 gateway 进程里 `_check_local_runtime()`（import hindsight / hindsight_embed.daemon_embed_manager / sentence_transformers）失败 → `is_available()`=False → provider 不加载 → daemon 不再拉起。

**诊断三步**：
1. `grep "Hindsight initialized" ~/AppData/Local/hermes/logs/agent.log | tail` —— 最后一条时间 = provider 最后一次成功构造（= 停摆起点）
2. `hermes memory status`（venv 内跑）—— Provider Status 显示 available/unavailable
3. venv 内 `python -c "import hindsight; from hindsight_embed import daemon_embed_manager; import sentence_transformers"` 复现 import

**修复**（依赖重装已验证成功，2026-08-13）：
```bash
source ~/AppData/Local/hermes/hermes-agent/venv/Scripts/activate
cd ~/AppData/Local/hermes/hermes-agent
uv pip install "hindsight-client==0.6.1" hindsight-all   # pyproject 锁 hindsight-client==0.6.1
```
- 版本：hindsight-client 0.6.1、hindsight-embed/hindsight-all 0.8.6（含 torch/sentence-transformers/pg0-embedded，体积大，装 2-5 分钟）
- ⚠️ `uv pip install --python /c/...` 的 MSYS 路径会被转坏（报 No virtual environment found）——先 `source venv/Scripts/activate` 再装
- **光装 hindsight 不够——还要两步**（2026-08-13 实测，漏了会卡在「依赖装好但 provider 仍不加载」）：
  1. `uv pip install "fastmcp[server]"`——hindsight 的 `hindsight_api/extensions/mcp.py` 在 import 链上 `from fastmcp import FastMCP`，缺 server extra 时整个 `import hindsight` 直接挂（报 "FastMCP server support is not installed"）
  2. **sitecustomize 修复 pywin32 .pth 问题**（见下方「uv venv shim 陷阱」→ pywintypes 链）——在 base python 用户 site 写 `sitecustomize.py` 注入 venv 的 win32/win32lib/pywin32_system32 路径 + `os.add_dll_directory`
- **验证修复生效**：curl POST `http://127.0.0.1:8642/v1/chat/completions`（api_server，需 `Authorization: Bearer $API_SERVER_KEY`）触发**新 agent 创建** → `grep "Memory provider" agent.log | tail` 应出现 `activated`。⚠️ 桌面会话 agent 走恢复路径**不激活 provider**（实测），api_server 新会话会——用 api 会话验证
- 重启 gateway：杀 `gateway run` 进程（`Stop-Process`）→ `Start-ScheduledTask Hermes_Gateway`；勿用 `hermes gateway status/start` CLI
- 数据无损：`~/.pg0/instances/hindsight-embed-hermes/` 保留旧库，daemon 起来直接连回（101 个 Document 都在）
- **daemon 保活（2026-08-13 追加）**：`~/AppData/Local/hermes/hindsight/config.json` 的 `idle_timeout` 默认 300s——空闲 5 分钟 daemon 自动关闭，且**已激活的 provider 不会自动重拉**（只有新 agent 创建才拉起）→ retain 又会断。改 `"idle_timeout": 0` 禁关闭（0 禁用），daemon 常驻

## ⚠️ daemon 停摆症状链 + watchdog 保活（2026-08-14 实测）

**症状**：`agent.log` 连续出现 `sync_turn failed: [Errno 36] Resource deadlock avoided`（死锁）+ `Failed to start daemon for profile 'hermes'`（拉起失败）→ **recall/retain 全失败，agent 无项目记忆注入**（文皓会话 14:00-14:20「失忆」实证：找内核全靠猜、反复被否）。注意 Errno 36 也可能是 daemon **冷启动中**（consolidation 积压 + embedding 同步阻塞事件循环 → recall 15.7s 慢返回），要结合进程/端口判断。

**根因**：`idle_timeout=0` 只挡空闲关闭，**挡不住 gateway 重启**——daemon 由 provider 构造时拉起，gateway 重启后旧 daemon 消失、新 provider 不自动拉，直到某个新会话激活才拉起。期间记忆服务静默停摆。

**修复（2026-08-14，治本双层）**：
1. **独立保活任务**：`scripts/hindsight_daemon_guard.py` + 计划任务 `Hermes_Hindsight_Daemon`（每 5 分钟，pythonw 无窗口）——daemon 生命周期与 gateway/provider **完全解耦**（gateway 重启不再带走记忆服务）；冷却 30 分钟防风暴，与 watchdog 共用 `state/hindsight_daemon_state.json` 天然互斥。
2. **watchdog 探针自愈 + 告警**：`gateway_watchdog.py` 的 `ensure_hindsight_daemon()` 从纯端口升级为 `hindsight_health()` 三态（ok=9177 监听+stats 2.5s 响应 / degraded=监听但无响应 / down=无监听）——**9177 监听 ≠ 可用**（事件循环阻塞时端口照听、recall 15.7s 实证）；degraded 连续 3 次（15 分钟）→ `kill_port_pid` 杀进程重启；拉起失败/卡死重启都发飞书 DM 告警（不再静默）。

**验证**：`python3 'C:/Users/HMSJ/AppData/Local/hermes/scripts/gateway_watchdog.py' --status` → `hindsight_daemon: ok`；guard 幂等（daemon 在跑则跳过）。Windows 原生路径必须用单引号（`~/` 会被 MSYS 转成 `C:\c\` 报错）。

## ⚠️ 恢复期多方抢拉 daemon（2026-08-17 实测：三方竞争 → 反复起死）

**触发**：gateway 死亡（或重启）后 daemon 连带死亡，恢复窗口内三个拉起源同时动作：①watchdog 探针（`ensure_hindsight_daemon`）②guard（`hindsight_daemon_guard.py`，每 5 分钟）③provider（`daemon_embed_manager`，agent 创建时 `_start_daemon`）——**guard 与 watchdog 有状态文件互斥，provider 不参与** → 双实例同时起 → 一个绑定 9177 成功、另一个报 `ERROR: [Errno 13] error while attempting to bind on address ('127.0.0.1', 9177)`（WSAEACCES，Windows 上端口被抢的表现），或锁文件 `[Errno 36] Resource deadlock avoided`（两个 `_ensure_started` 同进程并发加同一把锁）→ 全死。日志特征：hermes.log 有完整启动流程（DB 迁移 → Application startup complete）但绑定失败后 shutdown；或连日志都不写（启动早期即死）。观察信号：tasklist 里同时出现多个 pythonw（16-330MB）且 9177 无监听。

**⚠️ 补丁覆盖复核（2026-08-17）**：`grep "_pe_subsystem\|_find_gui_pythonw" venv/Lib/site-packages/hindsight_embed/daemon_embed_manager.py` 无输出 = **8-12 update 已覆盖黑窗口补丁**（site-packages 补丁每次 update 后都要重打，正本见 windows-shell skill `references/console-stub-rootcause.md`）。但**实测 venv pythonw（console stub）拉 daemon 依然可用**——shim 正常解析 venv 上下文（`venv/Scripts/pythonw.exe -c "import hindsight_api"` 通过，daemon 1.3GB 存活收到 recall/retain），stub 只影响黑窗口不影响功能。

**恢复标准动作（实测可靠，2026-08-17）**：别依赖 guard 手动触发——**guard 有 30 分钟冷却，冷却期内手动跑直接打印「冷却期内...跳过」**（状态 `state/hindsight_daemon_state.json` 的 `last_launch_at` 判定）。直接单实例拉起：

```bash
cd "$LOCALAPPDATA/hermes" && "$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/pythonw.exe" -m hindsight_api.main --daemon --idle-timeout 0
```

**验证链（缺一不可）**：`netstat -ano | grep 9177` LISTENING → gateway 到 9177 ESTABLISHED → `curl :9177/v1/default/banks/hermes/stats` 的 total_nodes 非 0 → hermes.log 尾部出现实时 `[RECALL hermes]`/`[BATCH_RETAIN_TASK]` 活动 → `hindsight_recall` 端到端命中。**daemon 启动加载 30-60s**（嵌入模型 1.3GB 内存），别在 40s 内下结论。

**gateway 死亡连带 daemon 死亡（修正 2026-08-14 的「解耦」表述）**：2026-08-14 guard 建成后「daemon 生命周期与 gateway 解耦」指的是**恢复手段解耦**（guard 独立拉起），不是**死亡隔离**——gateway 进程树一死，它拉起的老 daemon 照样死。所以 gateway 死亡后必须按本流程主动核 daemon，等 guard 每 5 分钟轮询（且有 30 分钟冷却）不可靠；watchdog 探针（`--status` 的 `hindsight_daemon` 字段）是快速判活入口。

## ⚠️ uv venv shim 陷阱（2026-08-13）

本机 venv 是 uv 管理的：`venv\Scripts\python.exe` 是 **shim**，实际 exec 到 `~/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe`（uv base python）。真 gateway 进程 = uv base python（命令行仍显示 venv 路径，靠 PYTHONPATH overlay 含 `venv/Lib/site-packages` 读包）。因此：

- **provider 是否可用取决于真 gateway 进程**（`netstat` 找 8644/8642 归属 PID → 看 ExecutablePath），不能只看命令行里是 venv 路径
- 模拟 gateway 环境测 import 时 **PYTHONPATH 必须含 `venv/Lib/site-packages`**，否则 ModuleNotFoundError 是误判（本会话曾因此复现失真）
- pg0 嵌入式 postgres **惰性启动**：daemon 未运行时无 postgres 进程、无端口可连（psql `server closed connection` = daemon 没跑，先起 daemon）
- **pywintypes 链（2026-08-13 实测，最深的坑）**：base python 只把 PYTHONPATH 里的 venv site-packages 当普通路径条目，**不处理其 .pth 文件** → pywin32 的 `pywin32.pth`（指向 win32、win32\lib、Pythonwin）不生效 → `win32/lib/pywintypes.py`（DLL 包装）和 `pywin32_system32/pywintypes311.dll` 都不可见 → import 链 `hindsight → hindsight_api.extensions.mcp → fastmcp[server] → mcp/os/win32/utilities → pywintypes` 断 → provider is_available=False。**shim 下正常、base python 下失败**是判定此坑的特征。修复：base python **用户 site**（`sitecustomize.py`）注入 venv 的 win32/win32lib/pywin32_system32 到 sys.path + `os.add_dll_directory(pywin32_system32)`（sitecustomize 对所有 uv base python 进程生效，无害）
- **MSYS 路径坑**：bash 里给 Windows 程序设 PYTHONPATH 用 `/c/...` 风格会被 MSYS 转坏成 `C:\c\...`（`python -c "import sys; print(sys.path)"` 里可见 `C:\c\` 前缀）→ 模拟环境必须用 Windows 原生路径（单引号包裹 `'C:\...'` 防转换），否则 import 全部 ModuleNotFoundError 是假象
- **psutil 读进程真实环境**（Windows 同用户）：`python -c "import psutil; print(psutil.Process(<pid>).environ().get('PYTHONPATH'))"`——拿真 gateway 进程的 PYTHONPATH/VIRTUAL_ENV，比猜环境可靠

## ⚠️ 2026-08-13 大故障：Hindsight 停摆 22h + 修复全流程（已实测闭环）

### 故障现象
daemon 8-12 11:15 空闲关闭后再没拉起，retain/recall 全断 22h+，`hermes memory status` 显示 provider available 但实际不工作（provider 未激活，agent.log 无 "Memory provider activated"）。

### 根因链（三层）
1. **8-12 `hermes update` 依赖安装失败**（`uv pip install -e .` exit 2 → 回退 ZIP）→ hindsight 全家桶丢失 → provider `_check_local_runtime()` 失败
2. **uv venv shim 机制**：`venv\Scripts\python.exe` 是 shim，gateway 实际由 **uv base python** 执行（`~/AppData/Roaming/uv/python/.../python.exe`，sys.prefix=uv 目录）——真 gateway 进程 ExecutablePath 显示 uv python 路径（netstat 8644 归属查 PID 确认）
3. **base python 不处理 venv site-packages 的 .pth**（PYTHONPATH 加的目录 .pth 不生效）→ pywin32 的 `win32/lib`（pywintypes.py 包装）+ DLL 目录没进 → `hindsight → hindsight_api.extensions.mcp → fastmcp(FastMCP) → mcp.os.win32.utilities → pywintypes` 链断 → is_available False

### 修复（按序执行）
```bash
# 1. 重装依赖（venv 内）
source ~/AppData/Local/hermes/hermes-agent/venv/Scripts/activate
cd ~/AppData/Local/hermes/hermes-agent && uv pip install "hindsight-client==0.6.1" hindsight-all
uv pip install "fastmcp[server]"   # hindsight 的 MCP 扩展依赖（关键！否则 import hindsight 报 FastMCP server support 未装）

# 2. sitecustomize.py（根治 .pth 问题）——base python 用户 site 自动加载
# 写入 C:\Users\HMSJ\AppData\Roaming\Python\Python311\site-packages\sitecustomize.py
# 内容：把 venv site-packages 的 win32、win32\lib、pywin32_system32 加 sys.path + os.add_dll_directory(pywin32_system32)

# 3. daemon 保活：config.json idle_timeout 300→0（不再空闲关闭）

# 4. 重启 gateway：杀 gateway 进程 → Start-ScheduledTask Hermes_Gateway
#    ⚠️ 杀进程会中断当前会话，桌面 app 自动重连

# 5. 验证（三层）
python -c "import pywintypes, fastmcp, hindsight; from hindsight_embed import daemon_embed_manager; print('OK')"
# gateway 同环境验证必须用 uv base python + 正确 Windows 路径 PYTHONPATH（bash 里 MSYS 会把 /c/ 错转成 C:\c\！用单引号 Windows 路径）
netstat -ano | grep 9177        # daemon 监听
grep "Memory provider" agent.log # provider 激活
grep "Document:" ~/.hindsight/profiles/hermes.log | tail  # retain 入库
```

### 验证陷阱
- **bash 模拟 gateway 环境时 MSYS 路径转换坑**：`PYTHONPATH=/c/Users/...` 传给 Windows 程序会变 `C:\c\Users\...`（sys.path 里可见）——必须用单引号包 Windows 原生路径
- **provider 激活的日志在 agent.log 的 "Memory provider 'hindsight' activated"**（不是 hermes.log）
- **is_available() 独立验证**：`python -c "from plugins.memory import load_memory_provider; mp=load_memory_provider('hindsight'); print(mp.is_available())"`
- **desktop 消息不记 gateway.log 的 inbound**（只有 feishu 记）——桌面 agent 的创建/激活只能看 agent.log
- **跨多次 gateway 重启的旧桌面会话可能不重新激活 provider**（恢复路径，8-13 实测 091320 会话 0 retain）；**gateway 重启后全新触达的会话正常激活**（92ce5b 实测）——旧会话不 retain 可接受，新会话正常
- **排障入口**：agent.log 的 "Memory provider activated"（有=激活）、hindsight-embed.log 的 "Daemon startup failed"（有=启动失败）、`hermes memory status`（provider available 不代表 agent 激活）

## 内容治理：成员画像类记录清理（2026-08-13 实测）

**治理原则（2026-08-13）**：成员「身份/偏好/习惯」类信息 → Obsidian `成员画像/*.md`（正本，三章节：沟通偏好/擅长领域/协作备注）；Hindsight 记忆库只留**项目事实**（团队分工/创作场景/运维事件）。画像类进记忆库 = 双写冗余 + recall 污染 + 单 bank 无隔离下的身份混淆（成员偏好可能被当成主人上下文注入）。

**画像类 vs 项目类判断特征**：
- 画像类（删）：身份年龄/学历/职业、文风偏好、命名习惯、分镜/格式要求、成员名字、档案归属映射、画像维护记录
- 项目类（留）：团队分工、具体创作场景（时间线事件）、cron 运维记录

**清理流程（实测）**：
1. 连真相库（端口先 netstat + 进程身份确认；psql.exe 在 `~/.pg0/installation/18.1.0/bin/psql.exe`）：`SELECT id, fact_type, text FROM memory_units WHERE fact_type='observation' AND (text LIKE '%成员名%' OR ...)`
2. 逐条出**精确清单**（id + 文本）供用户核对，区分画像类/项目类——不要批量盲删
3. `DELETE FROM memory_units WHERE id='<uuid>'` 逐条精确删 → `SELECT COUNT(*)` 验证 0 残留
4. 补齐画像文件缺口（画像正本可能比记忆库旧/少，如杨璇「21岁」条目）

**防复发决策（2026-08-13）**：改 gateway retain hook 机械分流**被否**——①hermes update 覆盖核心代码 ②画像/项目分类是判断力活，机械规则误判风险高（违反「机械/智能分工」铁律）③误判污染正本比记忆库冗余严重。方向 = **LLM 低频审计清理**（psql/recall 扫新入库候选 → LLM 逐条确认 → 脚本按 uuid 删）；根治需 Hindsight 支持 per-user bank（外部能力，不可控）。

**审计机制已落地（2026-08-13 执行）**：cron `2ad7b042825d`（每天 8:30，deliver=local 静默，LLM 判定，首次全量强制）+ 脚本 `~/AppData/Local/hermes/scripts/memory-audit-scan.py`（采集）/ `memory-audit-delete.py`（备份+删除+状态推进）。**关键端点事实**：列记忆用 `GET /v1/default/banks/{bank}/memories/list`；⚠️ `POST /v1/default/banks/{bank}/memories` 是 **retain 写入**端点（传 items 会写库，空 items 无害）；**无单条 delete API**（只有 clear 全清）→ 删除只能走 psql；PG 凭据在 `~/.pg0/instances/hindsight/instance.json`（hermes.env 只有 HINDSIGHT_API_* 键）。完整机制细节见 `references/memory-audit-mechanism.md`。

**首次执行结果（2026-08-13 实测闭环）**：全量 6530 条 → 候选 335 → **删 60 条画像类**（徐学环 30/杨璇 15/魏宁馨 5/全志越叶子苑津铭 7/陈星艳 2/档案映射 1，world 44+observation 16）→ 计数 6530→6470 实锤 + 备份 60/60 可恢复。275 条项目类保留；**6 条模糊项人工复核结论 = 零操作**（夹带的画像信息（叶子拆段/陈星艳口语化/施文皓懂技术等）画像文件 8-07 已全部覆盖——「宁留勿误删」判断正确）。cron agent 顺带自修脚本 3 bug：find_psql 适配 pg0 版本化目录（installation/<version>/bin/）、端口兜底改为 psql 报错即重试 5433、DELETE 命令标签解析取末位数字（int('DELETE 60') 曾崩）。

**instance.json port 决策（2026-08-13，不改）**：hindsight 实例写 5434、embed 实例写 5433、实际只有一个 PG 在 5433 监听——**port 字段是创建时期望值非运行实际值**（pg0 运行时动态分配，不回写文件）。改它 = 与 pg0 角力（下次 pg0 操作实例可能重写）+ 期望值本身不准（embed 也写 5433）。现状无影响（daemon 不依赖该字段、审计脚本有 fallback）→ **保持 fallback 逻辑，不手动改 instance.json**。

## ⚠️ daemon 未运行 → 会话「失忆」排查（2026-08-14 实测）

**现象**：飞书/桌面会话 agent 说「不记得 XX 项目」「翻不到之前的记录」、找内核全靠猜反复被否——**先查记忆服务，别只怪会话历史**。本次文皓「学习写歌」会话 14:00-14:20 全程无记忆注入（角色/主线/之前创作全丢），agent.log 实锤 `sync_turn failed: [Errno 36] Resource deadlock avoided` ×2 + `Failed to start daemon for profile 'hermes'`。

**根因模式**：Hindsight daemon **非常驻**——由 provider 激活时 `_start_daemon` 拉起；gateway 重启后旧会话继续消息若无新 agent 激活，daemon 不自动起 → recall/retain 静默失败（provider best-effort 降级，无报错），agent 表现「失忆」。

**诊断三步**：
1. `grep "Memory provider" ~/AppData/Local/hermes/logs/agent.log | tail`——找 `sync_turn failed: Errno 36`（死锁=daemon 冷启动/并发竞争）或 `Failed to start daemon`（daemon 压根没起）；同时看该时段的 `activated` 记录判定 provider 是否真在工作
2. `netstat -ano | grep 9177` + `Get-CimInstance Win32_Process` 看 PID 的 CreationDate——daemon 是否活着、何时被拉起（进程刚创建=冷启动期）
3. **数据层与服务层分开判**：`curl :9177/.../stats` 的 `total_nodes`（数据在不在）≠ recall 通不通（服务通不通）——本次 7153 节点全在，纯服务层故障；数据层验证用 Python urllib 发中文 recall（bash 中文 JSON 会被转义）

**冷启动加剧因素**：daemon 初始化（alembic migrations + embedding 模型加载）几十秒，期间 consolidation 积压（pending_consolidation=44+）同步跑 → DB pool 饱和（日志 `slow DB pool acquire`）+ `EVENT LOOP BLOCKED` → recall 15.7s 甚至 Errno 36。consolidation 消化完 recall 恢复 8-10s——**恢复后必须实测验证（Python recall 命中目标内容），别只看进程活着**。

**预防**：idle_timeout=0 已配（禁空闲关闭，8-13）；但 daemon 仍随 gateway 重启而消失——治本方案=watchdog（Hermes_Gateway_Watchdog 每 5 分钟查 8644）扩展加查 9177 拉起 daemon（2026-08-14 建议，未落地，用户拍板中）。

**相关**：8-13 停摆章节（依赖丢失→provider 不加载）与本次（daemon 未拉起→provider 加载但服务不可用）是两个不同根因，症状同为「recall 全停」，排查都从 agent.log 的 provider 记录入手。

## 陷阱速查

- **单 bank 无用户隔离**（2026-08-13 实证）：Hermes `sync_all()` 无条件同步所有渠道会话，飞书**成员**会话自动 retain 进 bank=hermes（日志 101 个 Document 中 17 个是成员会话，施文皓/全志越/苑津铭等）。成员偏好/项目版本与主人记忆混淆，recall 可能把成员内容当主人上下文注入。画像类清理流程见上方「内容治理」章节。config.yaml 的「仅妖玉可写」门禁只拦全局记忆（memory 工具），拦不住自动 retain 管线。诊断：`grep '^Document:' ~/.hindsight/profiles/hermes.log | sort | uniq -c` 列 Document 会话，再 state.db sessions 表按 id 反查 source/chat_type/user_id 对照成员名单.json

- recall 全 0 → 先查 stats.total_nodes，0 = 连错库（5434 vs 5433）
- **列记忆用 `GET /v1/default/banks/{bank}/memories/list`；⚠️ `POST /v1/default/banks/{bank}/memories` 是 retain 写入端点**（body 要 items 字段，传内容即写库）——2026-08-13 实测误用风险（空 items 无害，返回 usage 字段是写入特征）；**无单条 delete API**，删除只能走 psql（凭据 `~/.pg0/instances/hindsight/instance.json`，非 hermes.env）
- **端口观察澄清（2026-08-13）**：「8475 被百度网盘占用、5433 无监听」是 daemon 停摆期间 postgres 惰性关闭的假象；daemon 常驻修复后 **5433 回归监听**（instance.json 写 5434 有漂移，连接失败 fallback 5433）
- 手动启动 API → 必须 source hermes.env + export DATABASE_URL
- 中文 JSON body → 用 Python 发请求，别用 bash 内联
- 判定「未打通」前 → 确认 consolidation 已消化（observation 计数）且连对库
- **验证完成前不下定论、不删验证工具**（2026-08-08 用户纠正「等验证后在做决定」）：consolidation 积压期间 recall 搜不到≠未打通，此时删除验证 cron / 把「结论已定」写进记忆会被用户打回——先等消化完成跑实测，三种结果（打通/失败/待定）都拿到再定论。判断「打通」要用大 limit 查（默认只返回前 10 条，飞书内容实测排第 6/10 位，默认视图会漏）
