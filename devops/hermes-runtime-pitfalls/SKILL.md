---
name: hermes-runtime-pitfalls
description: Hermes 运行时踩坑档案库——MEMORY.md 精简后沉淀的操作日志/排查教训/工具怪癖。Use when 排查/诊断/OpenViking/MiMo/工具怪癖/边角工具/记忆体系异常。
category: devops
---

# Hermes Runtime Pitfalls

> **来源**：从 `~/.hermes/memories/MEMORY.md` 精简迁出（2026-08-28）。
> MEMORY.md 只留"运行时铁律 + 关键事实"，所有"操作日志/踩坑档案/工具怪癖/一次性经验"按需加载本 skill。

## 何时加载

- 排查/诊断 Hermes 异常（agent.log 401、Memory provider 假活等）
- 接 OpenViking / Hindsight / MiMo / TDB / 飞书 等工具的初始化/排错
- 用户问「setup X / 接 X / 用 X」类模糊指令
- 涉及 viking:// 路径、remember / add_resource / write 语义选择
- 命名规范冲突（hermes-memory vs default serviceId）

## 不加载场景

- 创作任务、剧本审读、提示词优化 → 加载妖玉影视系列 skill
- 用户核心偏好/全局铁律 → 在 MEMORY.md 已注入，无需加载
- 通用工具调用（git/terminal/file）→ 直接做，不查本 skill

---

## 分类索引

| 分类 | 条数 | 触发场景 |
|---|---|---|
| 记忆/Hindsight/OpenViking 运维 | 17 | 记忆/排查/迁移/MCP（新增 3 条 9/03：`add_resource wait=true` 超时真相 + 异步 abstract + 新旧版 recall 权威判定） |
| 工具/API/平台怪癖 | 5 | MiMo/MCP/voice_clone/输入法 |
| MEMORY/Skill 维护方法论 | 1 | 维护 MEMORY.md 时参考 |
| 边角工具/一次性经验 | 3 | macOS/ADC/线稿化 |

## References

- `references/ov-saas-smoke-test.md` — OV SaaS 端到端冒烟测试完整流程 + 一键脚本（auth → temp_upload → resources → search），3 分钟跑完。Use when 切换/排查 OV 写盘链路。
- `references/project-ov-overview.md` — 项目级 OV 总览落地工作流（README + 00-12 结构 + 验证矩阵 + 关键词命中策略 + 与飞书/Obsidian 的边界）。Use when 用户要求"整理 X 项目总览/进度到 OV"。
- `references/feishu-ov-write-protocol.md` — 飞书侧 OV 写盘契约 v1：open_id→username→namespace 路由、runtime env 切换、`POST /api/v1/content/write` 端点、401 调试矩阵。Use when 改造飞书侧写盘脚本/OCR/评论 capture/OCR adapter 任一类写盘链路。

---


## 记忆/Hindsight/OpenViking 运维

### 兜底链运行时真相（2026-08-27 实测）：①同一份 config.yaml 的 fallback_providers 全渠道同链≠全渠道同凭据——凭据按「进程启动时环境快照 

兜底链运行时真相（2026-08-27 实测）：①同一份 config.yaml 的 fallback_providers 全渠道同链≠全渠道同凭据——凭据按「进程启动时环境快照 + $HERMES_HOME/.env」解析，飞书网关与桌面 app 进程谱系不同。②判断某渠道兜底是否真实可用：psutil 读目标网关进程 environ() 逐 key 核对，不能只看 hermes auth list / config.yaml。③MiniMax 错误码 2056=Token Plan 用量封顶，藏在 HTTP 200 响应体 base_resp 里且 choices=null——「请求成功」不等于「有内容」。④判断「没兜底」先看 attempt 3/3 失败。
### 归档前先备份铁律（2026-08-27 Memos/Hindsight 清退实战）：用户清退类操作前必须先把所有目标移到 `scripts/_archive/<日期>-<主题>/`

归档前先备份铁律（2026-08-27 Memos/Hindsight 清退实战）：用户清退类操作前必须先把所有目标移到 `scripts/_archive/<日期>-<主题>/`，git 自动识别 rename（R）保留历史。删的文件留下完整目录快照，git history 可考古。**清退=删除** vs **归档=移动**——只要能归档就不直接删。
### SUPERSEDED 横幅铁律（2026-08-27 分析文档标注）：当某个知识资产已被新方案替代但内容仍有方法论价值时，在文档最顶部加 `> ⚠️ SUPERSEDED BY <

SUPERSEDED 横幅铁律（2026-08-27 分析文档标注）：当某个知识资产已被新方案替代但内容仍有方法论价值时，在文档最顶部加 `> ⚠️ SUPERSEDED BY <新方案> (<日期>): 当前已统一使用 <新方案>，本文档保留供考古/方法论参考，**不要按本文档的配置/端口/协议实施**`。**不删内容只加横幅**——保留考古价值的同时防止误用。hindsight_export.jsonl 等二进制数据文件跳过横幅。
### TDB 默认 instance 是 `default` 而非 hermes-memory（2026-08-27 TDB 实战）：TDB pipeline (`pipeline-v2

TDB 默认 instance 是 `default` 而非 hermes-memory（2026-08-27 TDB 实战）：TDB pipeline (`pipeline-v2`) 默认写入 serviceId=`default`。`hermes-memory` / `hermes` 这些是 Hindsight/MemOS v1 时代的命名残留——TDB 里存在但数据为空。**新接 TDB 的 agent 默认 serviceId 用 `default`**，不要被历史命名带跑偏。
### Hermes 记忆提供方诊断铁律（2026-08-28 端到端实测确立）：**agent.log 的 `Memory provider 'X' activated` ≠ 记忆在工作

Hermes 记忆提供方诊断铁律（2026-08-28 端到端实测确立）：**agent.log 的 `Memory provider 'X' activated` ≠ 记忆在工作**——provider 每次新 agent 都打印一次，可能背后 100% 在重试 401。正确判定路径：activated 行后 30 秒内 grep `AuthenticationError|HTTPError|sync_turn failed`，错误数 ≥ activated 数 ×2 = 假活。脚本 `~/AppData/Local/hermes/skills/devops/hermes-memory-provider-selection/scripts/memory_provider_health.py` 10 秒出结论（WORKING/DEGRADED/BROKEN + key 健康度 + http probe）。**OpenViking 双模式架构**：本地 server 模式（127.0.0.1:1933，viking:// 文件系统）+ SaaS 模式（火山引擎 api.vikingdb.cn-beijing.volces.com/openviking）。SaaS 端点路径前缀是 `/api/v1/`，不是 `/v1/`。MCP `viking_*` 工具只服务本地 server 模式，**SaaS 配 viking_* 必然 not connected 是预期不是 bug**——别拿这个当 provider 故障的证据。SaaS 真鉴权端点：`/api/v1/admin/accounts` `/api/v1/search/find` `/api/v1/fs/ls`；`/api/v1/system/status` 不鉴权——可用作"服务活否"探测。
### HERMES 排查/验证铁律 (2026-08-28 OpenViking MCP 实战确立): ①「setup X / 接 X / 用 X」类模糊指令, 第一轮必须 grill 

HERMES 排查/验证铁律 (2026-08-28 OpenViking MCP 实战确立): ①「setup X / 接 X / 用 X」类模糊指令, 第一轮必须 grill 三选项 (切换内置 / 加 MCP / 仅了解), 不替用户猜. ②config.yaml 已有 `provider: X` 不能默认为「正在切换中」, 可能是历史试验残留 — 先 grep 现状再决定动不动. ③看到 config 已配 + 用户说「X 通了 / 早就接上了」时立刻 grep `mcp list` / `config dump` 看真实状态, 不在错路上继续调. ④`hermes mcp test X` 报「✓ Connected」是乐观假象 — 只验 TCP 通 + 读 cache/mcp_schema_cache.json 的旧缓存, 不真发鉴权请求, 必须真发 initialize/list_tools 才是真验证. ⑤token / base64 类敏感信息粘贴到对话时 Hermes 输出会 mask (中间变 `***`), 但实际 config 文件里的 token 可能是完整版 — 用 grep -c 数长度确认, 别被显示截断误导. ⑥mcp SDK 1.29.1 的 streamablehttp_client 传 `read_timeout_seconds=int` 会触发 `int.total_seconds` bug, 不传 timeout 参数避开. ⑦OpenViking 云服务 MCP 鉴权: `Bearer <完整 base64 'account.user.credential'>` + `Accept: application/json, text/event-stream` + `mcp-protocol-version: 2025-11-25`.
### 模糊指令「setup X / 接 X / 用 X」第一轮必须 grill 三选项 (切换内置 / 加 MCP / 仅了解), 不替用户默认走最复杂路径(2026-08-28 实测:

### 凭据访问红线：agent 不要试图 base64 解码 Authorization / X-API-Key header

**场景**（2026-09-08 Kimi WebBridge 团队手册覆盖实战）：想给某个 OV 端点发 HTTP 请求上传资源，但 `viking_add_resource` 长轮询 timeout——直觉是先 curl 直连 `https://api.vikingdb.cn-beijing.volces.com/openviking/api/v1/resources`，**手贱开始 `grep -E "Authorization: Bearer \w+"` 解 base64**。

**根因**：我看到 config.yaml 里 mcp_servers.ov-mcp-server 的 `Authorization: Bearer ***`（被 Hermes 输出流 mask）就推断"我能拿到完整 base64 key 然后自填 header"——但：

1. config.yaml 文件里可能是完整 key（显示截断 ≠ 文件截断）
2. **任何"我自己起 HTTP 请求调凭据"的路径都让 agent 绕过 Hermes plugin 的凭据管理机制**——plugin 原本设计成把 OAuth token / SecretRef / API key 全程封装在 Hermes 进程内不暴露给 agent
3. 哪怕真的能拿到 key 调通，agent 也把"凭据访问"扩散到 N 个调用点，未来 plugin 升级（rotation、refresher）会全断

**铁律**：**永远不要 base64 解码 Authorization / X-API-Key 之类的敏感 header，也不要再发明自己的 HTTP 调用绕过 plugin**。要发请求就走 `viking_add_resource` / `viking_remember` / `viking_search` 等 viking_* 工具——它们自己注入凭据。要排查连通性 `viking_search("test")` 验证 recall——也是 plugin 自己走的。**agent 永远是消费者，不是凭据 owner**。

**类级教训（涉及所有凭据敏感场景）**：

- ❌ 看到 `Authorization: Bearer ***` 就想"我自己能解"——碰了就是碰红线
- ❌ curl 自填 Authorization 绕过 plugin——plugin 凭据 rotation 后 agent 全断
- ❌ 在 SDK / CLI 里硬编码任何 secret——违反 12-factor
- ✅ 永远通过 Hermes plugin 暴露的 viking_* 工具——plugin 负责凭据管理
- ✅ 排查 plugin 不可用：`hermes tools list` / `viking_search` 健康检查 / 看 plugin 日志——不碰凭据

### OV `viking_add_resource` target URI 路径层级与最终落地 URI 偏差（2026-09-08 实测）

**症状**：调 `viking_add_resource(to="viking://resources/_team-handbook/browser-capabilities.md", url=<local_md>, wait=true)` → 长 poll timeout 误判失败。再调 `wait=false` → `{"status":"added", "root_uri":"viking://resources/_team-handbook/browser-capabilities.md/browser-capabilities-handbook.md"}`——**root_uri 跟 target 末尾 `browser-capabilities.md` 不一致**。

**实测对照**：

| target URI | 最终 root_uri | 备注 |
|---|---|---|
| `viking://resources/_team-handbook/browser-capabilities.md` | `viking://resources/_team-handbook/browser-capabilities.md/browser-capabilities-handbook.md` | target 是单层，最终变 2 层（用本地 md 文件名） |
| `viking://resources/_team-handbook/browser-capabilities.md/browser-capabilities.md` | `viking://resources/_team-handbook/browser-capabilities.md/browser-capabilities-handbook.md` | target 是 2 层，最终**还是 2 层但名字变了** |
| `viking://resources/_team-handbook/memory-handbook.md/记忆使用手册团队公用v2/附录_D6_记忆卡修正与激进清理SOP.md` | `viking://resources/_team-handbook/memory-handbook.md/记忆使用手册团队公用v2/附录_D6_记忆卡修正与激进清理SOP.md/appendix-d6-memory-cleanup-sop.md` | target 是文件，最终变「target/本地文件名」 |

**根因**：OV 后端规范化——`target` 当**目录前缀**，最终 URI = `<target>`（如 target 是文件 URI 也视为目录前缀） + `<本地 md 文件名>.md`。**target 不影响最终文件名**。

**判定**：

- target **必须以 `/` 结尾或本身是文件 URI 含 .md**——否则 400 INVALID_URI（与 8/31 实测的「to 不能指向目录」不冲突——8/31 是 `to=viking://resources/_test/` 末尾斜杠无文件名，现在 target 是文件 URI OK）
- **target 末尾 `xxx.md` 是给 OV 当"放这里"的目录提示**，最终文件名 = 本地 md 文件名
- **功能等价**：target 路径偏差不影响 recall——`viking_search` 按关键词命中，跟具体 URI 后缀无关

**实战范式**：target URI 就写「希望它在的目录」就行，别纠结最终文件名——`viking_search` 命中即落地验证。

### `viking_forget` 工具能力边界（2026-09-08 实战踩坑）

**工具描述明确**：可以删除**精确 URI 的 memory file**。**不接受**：

- ❌ 目录删除（`viking://user/default/memories/events/2026/09/` 末尾斜杠 = 目录 = 拒绝）
- ❌ 批量删除（数组 URI = 拒绝）
- ❌ resources 删除（`viking://resources/...` — 即使是单个 .md）
- ❌ skills 删除（`viking://resources/skills/...`）
- ❌ sessions 删除（`viking://user/default/sessions/...`）
- ❌ generated summaries 删除
- ❌ broad deletes（glob/正则）

**支持的唯一形态**：`viking_forget(uri="viking://user/default/memories/<...>/<name>.md")` 单张精确 URI。

**批量清理 N 张卡 = N 次 `viking_forget` 单调**——不能用循环 hack 试图「绕过」（提交数组 URI 会整批拒，导致 0 张删除且 0 张成功状态可见）。**逐张 forget 时先 grep 该路径下有哪些 .md**——避免漏删。

**激进版记忆卡清理工作流**（用户拍板 + 团队手册附录 D.6 沉淀）：

1. **前置审计**：`viking_read level=full` 拿目标卡完整内容，**逐条 bullet** grep 整个 OV 看覆盖源——覆盖的可以激进删，未覆盖的留指针
2. **列代价清单**给用户拍板：哪些有效事实会被牺牲，哪些是被覆盖的牺牲无影响
3. 用户拍板后执行：
   - `viking_forget(uri=<每张精确 URI>)` 逐张删（**N 张 = N 次调用**）
   - `viking_remember(content=精炼事实)` 提新事实（OV 自动 retain 到 entities/events/preferences）
   - `viking_add_resource(to=..., wait=false)` 上传新卡到公共空间（如需要团队覆盖）
4. **验证 checklist**：
   - `viking_browse list` 确认被删 URI 从目录消失
   - `viking_search` 双向 query（错描述不召回 + 新事实召回）
   - `viking_read level=full` 新卡 URI 拿得到完整内容

### Windows 用户 PATH 注册铁律（2026-09-08 实战）

**场景**：装了一个 CLI 工具（如 `kimi-webbridge.exe`）想直接 `kimi-webbridge status` 跑（不写全路径）。

**正确流程**（用户级、不需 admin）：

```powershell
# 写 ps1 文件，不要在 bash heredoc 里写 $_ 之类的 PS 变量（bash 会吃）
$ps1 = "$env:TEMP\path-setup.ps1"
@'
$bin = 'C:\Users\<user>\.kimi-webbridge\bin'
$cur = [Environment]::GetEnvironmentVariable('Path','User')
$paths = $cur -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
if ($paths -contains $bin) { Write-Host '[skip] already on PATH'; exit 0 }
$new = ($cur + ';' + $bin).Trim(';')
[Environment]::SetEnvironmentVariable('Path', $new, 'User')
'@ | Set-Content -Path $ps1 -Encoding UTF8

# 再用 powershell -File 调（不是 inline -Command）
powershell -NoProfile -ExecutionPolicy Bypass -File $ps1
```

**关键陷阱**：

1. **`bash heredoc 里写 `$_` / `$env:USERPROFILE`**——bash 把 `$_` 当空字符串、把 `$env:USERPROFILE` 当普通文本——结果是 PS 收到 `:USERPROFILE\.kimi-webbridge\bin`（少了 `$env` 前缀）报路径找不到。**永远写 ps1 文件再 `powershell -File` 调**
2. **`SetEnvironmentVariable` 不即时刷新当前 shell**——新开 PowerShell/cmd 才会读到新 PATH。当前 shell 立即验证会 false negative。验证方法是新开进程。
3. **`Get-Command xxx -ErrorAction SilentlyContinue`** 默认不识别 .cmd / .bat 类型——必须加 `-CommandType Application` 才走 PATH 查找。但实际**裸跑 `xxx` 是可以成功的**——`Get-Command` 默认行为误导。
4. **顺手加 `Documents/Hermes/scripts/` 到 PATH** 让所有 scripts/ 下 .py / .cmd 都能裸跑——一次注册长期受益。

### SDK + CLI 共用 transport 的复用模式（2026-09-08 Kimi WebBridge 实战）

**场景**：同一个底层 daemon 有两种接入方式——agent 调 SDK（`KimiWebBridge` 类）、用户手跑 CLI（`kimiwb diagnose/exec`）。**两份代码不能各自实现 HTTP/curl/temp 文件逻辑**——出 bug 时两份不同步修。

**正确目录组织**：

```
kimi_webbridge/                      # Python SDK 包（agent 用）
├── __init__.py                      # KimiWebBridge 类 + 模块函数
└── _transport.py                    # HTTP + curl.exe + temp file + lazy daemon

scripts/
└── kimi_webbridge.py                # CLI（argparse + 调 _transport）
```

**关键设计**：

- **`_transport.py` 是单文件 stdlib 模块**，提供 `find_bin / is_alive / start_daemon / ensure_daemon / send_command(action, args, session)` 5 个函数 + `DaemonNotRunning` 异常
- SDK `__init__.py` 用 `from ._transport import ...` 拿这些函数，包成 `KimiWebBridge` 类
- CLI `scripts/kimi_webbridge.py` 也用 `from kimi_webbridge._transport import ...`，自己 argparse 写 diagnose/restart/exec 子命令
- **任何 HTTP/curl 行为修改 = 改 `_transport.py`**——SDK + CLI 自动同步

**类级教训**：底层工具链 = 单一 source of truth，不要在 CLI / SDK / 第三方包各写一份"类似但微妙不同"的实现。**`import` 而不是 `copy-paste`**。
### OpenViking `remember` 工具语义纠正（2026-08-28 端到端实测确立）：`target_uri` 只是初始提示，**不是写入路径**。OpenViking

OpenViking `remember` 工具语义纠正（2026-08-28 端到端实测确立）：`target_uri` 只是初始提示，**不是写入路径**。OpenViking 后台 LLM 自动按主题分类到 `viking://user/default/memories/{entities|events|preferences}/` 子目录（共 995+ entries 实测），不保留原 URI 结构。**评估迁移价值的指标不是文件数，是 find() 召回命中率 + 召回内容是否直接可用**（实测 query "伏妖记 三幕结构" 命中 61%，内容是 LLM 摘要+决策摘要，agent 可直接用）。同类内容会被自动去重但有延迟（同一事件拆成多个 md 是 LLM 重复提取的副作用）。
### OpenViking MCP 写入陷阱（2026-08-28 实测）：大批量 `remember` 写入触发 OpenViking 服务 503 限流，**HTTP 503 ≠ 写

OpenViking MCP 写入陷阱（2026-08-28 实测）：大批量 `remember` 写入触发 OpenViking 服务 503 限流，**HTTP 503 ≠ 写入失败**——SDK 重试可能表面成功但实际写入延迟到后台 extraction 队列（实测 32 个文件等了 1 小时才生成完整目录树）。`written=N` 计数仅代表请求发送成功，不等于 OpenViking 已落地。验证真实状态必须 `list(uri, recursive=True)` 看目录树，不能信脚本报告。大量记忆迁入时宁可单批 ≤ 20 条 + 间隔 30s（避免压垮后端队列），Hindsight 9722 条全量迁预计 4+ 小时且 extraction 队列可能崩——评估表明 32 个代表文件已覆盖工作流，全量迁移边际价值低。

### OpenViking `ov CLI add-resource` vs `temp_upload` 端点差异（2026-08-31 实测）：**锁错误路径是客户端 bug，不是服务端问题**

`ov` CLI 0.4.17.dev0 的 `add-resource` 命令实测报 `[PROCESSING_ERROR] Parse error: encrypted write lock error: lock I/O error: failed to create lock token at /local/_system/temp/.encrypt_stage/...`——**这个 `/local/_system/temp/` 是客户端本地的临时目录**，不是服务端。CLI 实现要在客户端生成加密锁文件，本机环境问题导致失败。**真服务端的健康探测**：直接 `curl https://api.vikingdb.cn-beijing.volces.com/openviking/health` 返回 `{"status":"ok","healthy":true,"auth_mode":"api_key"}`——服务端完全正常。**判断根因**：①看到 `/local/` 路径前缀的锁错误 → 客户端 bug 不是服务端；②看到 `5xx HTTP` → 服务端问题；③看到 `4xx MissingParameter` → 请求构造问题（如缺 `to` 字段）；④看到 `4xx AuthenticationError` → API key 拷错（base64 多了一段/少了一段）。

`temp_upload` 端点（`POST /api/v1/resources/temp_upload`）是绕过 ov CLI 锁 bug 的官方路径，需要 multipart 字段：`file`（二进制）、`to`（目标 viking:// URI）。MCP `add_resource` 工具就是这个流程的封装——它会返回一次性 `upload_url?token=...` 让客户端 POST。但实测发现**走 HTTP 直 curl `temp_upload` 会返 401**，因为缺 token；MCP 工具内部有 init 拿 token 的隐藏协议（路径未公开），目前外部脚本无法绕过 init 步骤。**当前唯一可靠的写入路径是 MCP `add_resource` 工具**——但实际验证服务端没存（`list` 报 NOT_FOUND），所以**当前（2026-08-31）OV SaaS 写入事实上不稳定**，先暂停 cron 自动同步避免污染队列。

### OpenViking SaaS HTTP API 完整协议（2026-09-01 端到端实测确立，已替代 8/31「客户端 bug」判断）

> ⚠️ **SUPERSEDED BY** `OpenViking SaaS HTTP API 完整协议 (2026-09-01)`: 8/31 的"OV 写盘 = 客户端实现 bug"判断已**彻底反转**——服务端 v0.4.14.5 的 HTTP API 实测**完整可用**，写盘端到端跑通。当时盲探 10+ 路径全 404 是**没找对协议**，不是服务端问题。本节是当前权威方案，旧节仅作考古参考。

**核心结论**：OV SaaS 写盘走 **HTTP 直连 `api.vikingdb.cn-beijing.volces.com/openviking`**，**不走 MCP `add_resource`/`remember`**（这些 MCP 工具的 schema 当前有 bug，跑不通）。

**鉴权 header（最容易搞错的）**：
```bash
curl -H "X-API-Key: $OPENVIKING_API_KEY" \
     -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
     -H "X-OpenViking-User: $OPENVIKING_USER" \
     "$OPENVIKING_ENDPOINT/..."
```
**不是** `Authorization: Bearer ...`。SaaS 模式用 API key + tenant header 三件套。GET `/health` 不鉴权即可探测服务活否。

**完整写盘协议（两步流程，必走）**：

```bash
# Step 1: temp_upload 拿 temp_file_id（multipart，不是 JSON）
TEMP_ID=$(curl -sS -X POST \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: $OPENVIKING_USER" \
  -F "file=@$(cygpath -w /tmp/file.md)" \    # ⚠️ Windows 路径必须 cygpath
  "$OPENVIKING_ENDPOINT/api/v1/resources/temp_upload" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["temp_file_id"])')

# Step 2: resources POST 带 temp_file_id 触发 ingest
curl -sS -X POST \
  -H "X-API-Key: $OPENVIKING_API_KEY" \
  -H "X-OpenViking-Account: $OPENVIKING_ACCOUNT" \
  -H "X-OpenViking-User: $OPENVIKING_USER" \
  -H "Content-Type: application/json" \
  -d "{\"temp_file_id\":\"$TEMP_ID\",\"to\":\"viking://resources/_test/foo.md\"}" \
  "$OPENVIKING_ENDPOINT/api/v1/resources"
```

**关键陷阱**（必读）：

| 陷阱 | 表现 | 解 |
|---|---|---|
| `to` 指向目录 | 400 INVALID_URI `to must target resource content` | 必须指向具体文件 URI（含 `.md` 后缀），不能是 `viking://resources/_test/` |
| `to` 指向 `viking://user/...` | 400 INVALID_URI | resources 端点**只能写 `viking://resources/`**，写 user memory 走 session/commit 流程 |
| `to` 带 `url` 字段直传 | 400 extra_forbidden | resources POST schema 严格模式不接受直传 URL，必须先 temp_upload |
| curl `-F file=@/tmp/...` MSYS 路径 | curl: Failed to open/read local data from file | 必须 `cygpath -w /tmp/...` 转 Windows 路径（**这条 8/31 已踩过但本会话复现，永久铁律**） |
| /api/v1/health | 404 | 用 `/health`，不鉴权，返回 `{healthy, version, auth_mode, role}` |
| Authorization: Bearer $KEY | 401 AuthenticationError | 改用 `X-API-Key` header |

**端点表（v0.4.14.5 实际挂载的路由）**：

| Method | Path | 用途 |
|---|---|---|
| GET | `/health` | 健康探测（不鉴权） |
| POST | `/api/v1/resources/temp_upload` | multipart 上传拿 temp_file_id |
| POST | `/api/v1/resources` | 用 temp_file_id 触发 ingest |
| GET | `/api/v1/fs/ls?uri=...` | 列目录 |
| POST | `/api/v1/content/write` | 写已有文件内容（要求文件已存在） |
| GET | `/api/v1/content/{read,abstract,overview}` | L0/L1/L2 读取 |
| POST | `/api/v1/search/{find,search,grep,glob}` | 语义/上下文/正则/glob 检索 |
| POST | `/api/v1/sessions/{id}/messages` | session 追加消息 |
| POST | `/api/v1/sessions/{id}/commit` | session 归档 + 提取记忆（**这是写 user memory 的真路径**） |

**验证端到端走通的最小测试**（2026-09-01 实测）：

1. GET `/health` → 200，role=admin
2. POST temp_upload → 200 + temp_file_id
3. POST resources with temp_file_id → 200 + file_id
4. 等 3-5 秒后 POST `/api/v1/search/search` → 200 + score≥0.5 命中刚写入的内容

**为什么 8/31 没走通**：①鉴权 header 用了 Bearer 而非 X-API-Key → 401 误判为"客户端问题"；②盲探的 `/v1/resources` 路径不存在（实际是 `/api/v1/resources`）；③ `to` 字段值带目录而非文件 → INVALID_URI 误判为"请求构造问题"；④ multipart 路径用 MSYS 格式 → "Local path does not exist" 误判为"客户端 bug"。三层盲探错误叠加才得出"服务端不可用"结论，**错的是 agent 不是服务端**。

### `mcp__ov_mcp_server__remember` schema mismatch（2026-09-01 实测）——SaaS 模式下 MCP 写入工具不可用

**症状**：调用 `mcp__ov_mcp_server__remember(messages=[{"role": "user", "content": "..."}])` → `MCPError: invalid params: validating "arguments": validating root: validating /properties/messages: validating /properties/messages/items: required: missing properties: ["role" "content"]`——schema 校验反复报缺字段，但参数已提供。

**根因**：当前 MCP 客户端构造的 messages 参数结构与服务端 schema 校验器不匹配。MCP SDK 1.29.1 序列化时把 `content` 嵌套错误，服务端 Pydantic 严格模式直接拒。

**判定**：MCP 写入工具当前**不可用**。任何写盘需求**直接走 HTTP 端点**（见上节），不要试 MCP `remember`/`add_resource`。MCP **只用于读侧**（`health`/`search`/`find`/`read`/`list`）——读侧 schema 正确可用。

### config.yaml 安全护栏：`memory.provider` 是 security-sensitive 字段，agent 不能写

**症状**（2026-09-01 实测）：`patch`/`write_file` 工具直接编辑 `~/AppData/Local/hermes/config.yaml` 报错：`Refusing to write to Hermes config file: ... Agent cannot modify security-sensitive configuration. Edit ~/.hermes/config.yaml directly or use 'hermes config' instead.`

**适用范围**：`.env` 文件**不在护栏内**（agent 可写）；`config.yaml` 的多数字段**也在护栏内**（`memory.provider`、`providers`、API key 等）。

**正确流程**（用户拍板后）：
1. agent 写/改 `.env`（OPENVIKING_* 5 行等）
2. agent 列出要改的 `config.yaml` 行号 + 旧值/新值，**不直接动 config.yaml**
3. 用户自己在编辑器里改 config.yaml
4. agent `grep` 验证改动生效（mtime + 实际值）

**不要尝试**：`hermes config set ...` CLI、`sudo -E bash -c`、删除护栏标记等绕过手段——都是死路，用户拍板的"先做再说"也不适用于 config.yaml 这种 agent 写会被拒的字段。**真正的"按你判断推进"指的是：别 grill 用户要 key、别 grill 用户决定 endpoint 端口——但 .env 写入和 config.yaml 改动是两件事，后者必须用户亲手改**。

### Memory provider 切换工作流（memory.provider 字段）

新会话自动激活的前提：① `.env` OPENVIKING_* 5 行已就位；② `config.yaml` 第 405 行 `provider: openviking`（你手动改）；③ 重启 gateway 或开新会话触发 `agent_init` 加载 provider。

**判定 provider 真活**：agent.log 看到 `Memory provider 'openviking' activated` 后 30 秒内 grep `AuthenticationError|HTTPError|sync_turn failed`——0 错误 = 真活；≥ activated 数 × 2 错误 = 假活（已激活但鉴权失败）。脚本 `~/AppData/Local/hermes/skills/devops/hermes-memory-provider-selection/scripts/memory_provider_health.py` 10 秒出结论。

### OV MCP `add_resource` 超时 vs `wait=false`（2026-09-03 实测确立）

**症状**：调 `viking_add_resource(to=..., instruction=..., reason=..., wait=true)` 上传 7K-15K+ 字符的 markdown 文档 → **反复** 返回 `error: "The read operation timed out"`。但文档实际**已经入队**——随后 `viking_browse` 能列出该文件，只是 abstract 显示 "Directory abstract is not ready"。

**根因**：`wait=true` 模式下 OV MCP wrapper 同步等 L0/L1 语义索引完成（生成 L1 摘要需 LLM 调一次），大文件耗时长 + MCP 通道 read timeout 默认窗口撞上。**文件已写入 OV，只是 abstract 没生成完**。

**修法（默认行为）**：**所有 `add_resource` 调用 `wait=false`**，返回 `{"status": "added", "root_uri": "...", "message": "Resource queued for processing"}` 即视为成功。摘要异步生成（后台 LLM 队列跑）——10-30 秒后 `viking_browse` 才会看到完整 abstract，OV 在生成期会显示 `Directory abstract is not ready`，**这是预期不是失败**。

**验证模式（批量上传 N 个文件后）**：

```bash
sleep 15  # 异步索引冷启动
viking_browse path=viking://resources/<dir>/  # 列出全部，看哪些还显示 "not ready"
sleep 25  # 再等一轮
viking_search query=<核心关键词>  # recall 命中即验证成功，无需等 abstract ready
```

**判定矩阵**：

| 现象 | 含义 | 应对 |
|---|---|---|
| `add_resource wait=true` timeout | 文件已入队，abstract 还在生成 | 改 `wait=false`，不要重传 |
| `viking_browse` 显示 "Directory abstract is not ready" | OV 后台 LLM 还没跑完该文件的 L0/L1 | 等 15-30s 再 browse，或直接 `viking_search` 验证（搜索不依赖 abstract） |
| `viking_search` recall 命中 score≥0.5 | 文件实质已落地 | ✅ 任务完成，无需等 abstract |
| `viking_search` recall 不命中 | 真未落地或语义化失败 | `viking_browse` 看文件是否存在；存在则是 LLM 摘要失败（罕见），不存在是上传失败 |

**批量实战技巧**：多个文件不要并发 `add_resource`（OV 后台队列可能拥塞）。**串行小批**（≤4 个/批）+ 每批后 `sleep 10-15` 让摘要跟上，是最稳的节奏。

### OV `viking_search` 同时命中新旧版记忆时如何判断权威（2026-09-03 实测确立）

**症状**：用户要求整理某项目总览到 OV，新建 `viking://resources/projects/<项目>/` 目录落地了新版。但 `viking_search` 召回时旧版 OV 实体卡（`viking://user/default/memories/entities/...`）和新版资源（`viking://resources/...`）**同时命中**，旧版分数甚至可能高于新版（因为旧版更短、信息密度更高）。

**根因**：OV 的 recall 排序靠"语义相似度"而非"权威性"。旧版实体卡短小精悍，新版资源文档信息密度相对低（虽然更新但更长），**信息密度 = 召回分数**是 OV 的默认行为。

**判定铁律**：

1. **新正本台账决定权威**——任何项目总览必须在 `viking://resources/<dir>/README.md`（或 `00-项目元数据.md`）顶部明确写**新正本的 URL/token 和"以新正本为准"的硬声明**
2. **`viking_search` 同时召回新旧时**，靠"信息密度"取舍会偏旧版——agent 必须读 README 顶部台账判断，不靠分数
3. **旧版降权靠"完整覆盖"而非"加过期标记"**——新版写得越完整越精确，旧版的相对分数自然下降（语义相似但关键词更专）。**"加过期标记"实际效果有限**（OV 不会按标记降权），别指望单一标记操作
4. **关键词命中策略**：新版的关键词必须用**当前正本的角色名/术语**——`viking_search("伏妖记 素鸢 暮云亭")` 命中新版；`viking_search("伏妖记 镜妖 陆老邪")` 命中旧版。让两个版本在不同 query 路径下不打架

**踩坑教训**：用户拍板"旧版少许参考价值" → 我一开始想给每张旧实体卡加"过期标记"——实际验证 OV `viking_remember`/`update` **不能修改存量卡内容**（只能新增或 viking_forget 删除）。**真正的降权手段按效果递增排**：
1. **写新版 README + 元数据顶部权威台账**——让 recall 时关键词走新正本路径（效果有限）
2. **给新版加更专更全的关键词命中**——让新版分数自然超过旧版
3. **加一条"过期说明事件卡"**——关键词密集 + 指向新版 README（实战有效，把新版排在首位）
4. **批量 `viking_forget` 旧版重复卡 + 留一张 viking_remember 快照卡**——**最彻底**（2026-09-03 伏妖记实战：删 60+ 张旧版重复卡后，旧版关键词 recall 完全压制，搜索"伏妖记 镜妖 陆老邪"只有新版事件卡 + 旧版快照卡 + 新版文档）

**类级教训**：当你被要求"整理某项目总览到 OV"且该项目存在多版本历史时，必须**第一步就确认"以哪份为正本"**——不要默认最新版，不要默认飞书最新版，不要默认最近编辑的版本。**用户拍板才算**。

### 项目级 OV 总览目录组织模式（2026-09-03 实战确立）

**场景**：用户要求"整理 X 项目总览、进度等，放到 OpenViking"——这是 OV 上**项目级长期资产**的标准化组织模式，跨会话召回用，不是一次性任务。

**目录结构（推荐）**：

```
viking://resources/projects/<项目名>/
├── README.md                           # 总览入口（最关键，必建）
├── 00-项目元数据.md                    # 单页可读入口
├── 03-故事线.md / 02-人物小传.md       # 分领域拆文档
├── ...按需扩展
└── README-过期记忆索引.md              # 旧版记忆降权说明（如适用）
```

**关键铁律**：

1. **README.md 是单点入口**——所有外部引用都指向 README。必须在顶部明确：①权威正本位置（飞书 token / URL）②旧版状态（淘汰/参考）③OV 内子文档指针 ④版本演进时间线
2. **00-项目元数据.md** = 单页可读版 README（用户能一页看完核心信息）。两文件内容有重叠但定位不同：README 给 agent recall 命中的首屏，元数据给人/agent 系统性查阅
3. **子文档按"信息维度"切分**（不是按场次切分）：核心设定/人物小传/故事线/分场大纲/场景美学/配乐声音/创作方法论/进度时间线/创作复盘/决策留档/OpenItems——每个维度独立文档，可单独 recall
4. **子文档数量上限**：项目级总览一般 12-15 份文档。每个文档 5-20KB 区间。超过 20 份会稀释 recall 命中率
5. **每个文档顶部必含元信息**——片长/版本号/正本位置/负责人/创作阶段——agent 单看一个文档也能立刻定位

**OV 摘要完整度差异**（同一项目不同文档对比验证）：

- 7-9K 字符文档：1-3 分钟 abstract ready
- 10-15K+ 字符文档：5-10 分钟 abstract ready
- 20K+ 字符文档：> 10 分钟，甚至部分章节 abstract 延迟到 30 分钟+

**实战技巧**：大项目批量上传 10+ 文档时，按"重要性倒序"上传（README + 元数据先传 → 子文档后传），保证最关键的文档先入队先 abstract，后传的子文档 recall 暂时走内容级匹配。

**与飞书/Obsidian 的关系**（用户拍板分工的范本）：

| 层级 | 工具 | 角色 |
|---|---|---|
| 权威源 | 飞书文档 | 唯一权威正本，所有创作以飞书为准 |
| 项目总览入口 | OV `resources/projects/<项目>/` | agent 召回中枢、跨会话共享 |
| 本地 git 归档 | Obsidian（可退役或保留） | 历史溯源、可选只读 |

### 项目级 OV 总览落地验证矩阵（2026-09-03 实战）

**落地后必跑的 5 项验证**：

| 验证项 | 命令 | 通过标准 |
|---|---|---|
| 目录树可见 | `viking_browse path=viking://resources/projects/<项目>/` | 列出所有上传的文档（abstract 可能 is not ready） |
| 关键词召回命中新版 | `viking_search("项目名 + 新版核心关键词")` | 命中 `viking://resources/projects/...` 的文档，score ≥ 0.45 |
| 关键词召回压制旧版 | `viking_search("项目名 + 旧版核心关键词")` | 新版事件卡/总览 rank 1-2，score ≥ 旧版事件卡 |
| 过期说明召回（agent 自行判断）| `viking_search("项目名 + 已过期/淘汰")` | 命中过期说明事件卡 |
| git 提交（如有 Obsidian 同步）| `git -C <repo> log --oneline` | 看到归档 commit |

**关键词命中策略（决定 recall 排序）**：

- **新版关键词**：当前正本的角色名 + 术语（伏妖记 → 金翅鸟/素鸢/暮云亭/依依/沈秋澜/青舟渡/澄阳观）
- **旧版关键词**：被淘汰的角色名 + 术语（伏妖记 → 镜妖/陆老邪/莲儿/花莲/茅草屋看家）
- **新版关键词命中新版** + **旧版关键词命中旧版** = 两个版本在不同 query 路径下不打架，让 agent 自己判断权威（靠 README 顶部台账）
- **不要试图单一关键词召回同时命中新旧**——会触发 recall 排序混乱

**实战案例**（2026-09-03 伏妖记项目）：

| 查询 | rank 1 | rank 2 | rank 3 |
|---|---|---|---|
| `伏妖记 金翅鸟素鸢 暮云亭 澄阳观 依依` | 新版事件卡（0.52） | 新版核心设定（0.512） | 旧版实体卡（0.512） |
| `伏妖记 镜妖 莲儿 陆老邪` | 旧版事件卡（0.586） | 旧版事件卡（0.582） | 旧版偏好卡（0.571） |
| `Obsidian 退役 写入 伏妖记` | 退役铁律卡（0.691） | 旧版同步事件（0.558） | 旧版同步事件（0.556） |

新版关键词路径下，新版占据前 2；旧版关键词路径下，旧版压制——但都靠 agent 读 README 顶部台账判断权威。

### Observing 项目文档 = 飞书正本切换时的"权威判定"铁律（2026-09-03）

**症状**：用户拍板"以新的剧本和项目文档为准"——旧版（飞书 + OV）已淘汰，少许参考价值。**但"新的"具体指哪个 token？必须当场向用户拍板，不能 agent 推断。**

**踩坑教训**：

- 9/3 第一轮我**自己去看 OV 事件卡**，找到 `viking://user/default/memories/events/2026/08/28/伏妖记当前文档状态确认.md` —— 信息是「EsMD/NSZK 双正本」——**这是旧版 v2.1.4，已淘汰**
- 我据此写 OV 总览 → 完全错了：把所有"金翅鸟素鸢/暮云亭/依依/沈秋澜"当成新设计，但用户其实已经在 9/2 完成了剧本大重做（这些已经是 9/3 之前的"新"）
- 用户**直接 @ 两个飞书文档 URL** 拍板"以这两个为准"——我才意识到必须先问用户

**铁律**：任何"整理项目总览/文档现状到 OV"类任务，**第一步**必须：

1. 向用户**直接拍板**当前正本的 token/URL（不要看 OV 旧事件卡推断）
2. 拍板后才能开始"权威源 → OV 总览入口"的对齐工作
3. 旧版来源只能用于"对比说明"，**不能**作为新版文档的引用源

**类级教训**：当用户拍板"以 X 为准"时，agent 不能**主动**从 OV/记忆库里推断"X 是哪个版本"——必须让用户**显式给**。MEMORY 里看到的"X"和用户当下指的"X"不一定是同一个东西**（版本已迭代多次）。

### 项目级 OV 总览 vs 一次性任务归档的边界

**项目级总览**（推荐用 `viking://resources/projects/`）：
- 跨会话长期资产、用户/团队多次访问
- 含权威正本台账、版本演进、决策留档
- 文档结构稳定（README + 00-12 标准化）
- 触发更新：正本 revision 推进 / 用户主动更新指令

**一次性任务归档**（用 `viking://resources/_archive/<日期>-<主题>/` 或 `viking://resources/<任务名>/`）：
- 单次任务产出（爬虫结果、批量分析报告）
- 一次性阅读、不需要跨会话维护
- 无版本演进、无决策留档需求
- 触发更新：极少（如有补充数据集）

**判断口诀**：

| 信号 | 归类 |
|------|------|
| 用户原话"放到 X 项目 / 整理项目总览" | 项目级总览 |
| 用户原话"归档 / 存档 / 留档" | 一次性任务归档 |
| 含"权威正本/版本演进/决策留档"关键词 | 项目级总览 |
| 含"本次产出/分析报告"关键词 | 一次性任务归档 |
| 用户后续会话会主动 viking_search 项目名 | 项目级总览 |

**混用风险**：把一次性任务归档到 `projects/<项目>/` 会稀释项目总览的 recall 精度；把项目级总览放到 `_archive/` 会让用户后续访问困难。

### 项目级 OV 总览与 Obsidian 写入的边界（2026-09-03 拍板）

**场景**：项目级 OV 总览落地后，用户拍板**退役 Obsidian 写入**（只读不写）——这是知识架构层面的重大转变。

**新分工**：

| 角色 | 工具 |
|---|---|
| 唯一权威正本 | 飞书文档 |
| 项目总览/记忆/召回中枢 | OpenViking `resources/projects/<项目>/` |
| 本地 git 归档（**只读**） | Obsidian（仅历史溯源，不再写入） |
| 跨平台多端同步 | OpenViking 直连 |

**Obsidian 写入退役铁律**：

1. **标记只读归档**：在 Obsidian 项目目录加 `_归档说明.md`，声明状态（"只读归档"+新新内容走 OV）
3. **git 提交归档标记**：`git commit -m "归档(<项目>): 退役Obsidian写入，标记为只读归档，OV主写"`
4. **OV 写铁律持久化**：`viking_remember` category=pattern 内容 = "凡涉及 X 项目的新内容只走 OV"——recall 排序首位，下次会话自动看到
5. **更新 OV README 顶部**：加"Obsidian 写入已退役"声明 + Obsidian 归档路径链接

**撤销/调整边界**（用户改主意时）：
- 用户说"Obsidian 重新启用" → 改 Obsidian `_归档说明.md` 内容 + OV README 顶部声明 + 更新 pattern 记忆
- 其他项目（犬子无双/手心人等）保持原状——只退役单一项目，不一刀切

**陷阱**：

- ❌ **一刀切所有项目**：用户拍板"退役 Obsidian 写入"可能只是某一个项目（如伏妖记），不是所有项目
- ❌ **删 Obsidian 内容**：只标记只读，不删内容（保留 git 历史）
- ❌ **未提交 git 就标记**：标记前必须 git 提交，确保 git 历史可回溯
- ❌ **OV README 没标权威**：如果 README 没写"以 OV 为项目总览入口"，agent 下次会话仍可能误用 Obsidian

**类级教训**：当用户拍板"X 项目退役某系统"类决策时，必须**先确认范围**（是 X 项目，还是所有项目），再执行——避免误扩大化。

### MCP `add_resource` multipart token 实测样本（2026-08-31）：短时效 + 端到端未走通

**token 实证**（MCP `add_resource(path=<Windows本地路径>)` 真实返回）：
```
Local file detected. Upload it with a multipart/form-data POST (field name "file") to:
  https://api.vikingdb.cn-beijing.volces.com/openviking/api/v1/resources/temp_upload?token=ywOVma
The URL's token authorizes the upload (no API key needed). Expires in ~10 minutes (2026-08-31T06:47:43Z).
```

**关键约束**：
- token 6 字符短串（`ywOVma` 格式），非 API key。
- **有效窗口 ≈10 分钟**（本次观察：`06:37:43Z → 06:47:43Z` UTC）。
- 字段名 `file`（multipart），不是 `content`/`data`/`blob`。
- 推断的完整链路：`add_resource(path)` → 拿 `upload_url?token=...` → POST multipart（10 分钟内）→ 拿 `temp_file_id` → 再调 `add_resource({temp_file_id})` 触发 ingest。

**为什么没走完**：
- 拿到 token 后才意识到 10 分钟窗口极短，单步操作可能已过期。
- 完整 ingest 验证仍是开放问题——火山引擎不文档化 multipart 字段细则，盲探风险高。
- **下次触发**：必须在拿到 token 后立刻连续执行 POST + 第二次 add_resource，不要分多轮跨窗口。

**结论**：MCP 拿 token URL 这步**已验证存在**；POST 上传 + ingest 端到端**未实测**。**报告官网时如实标注"multipart URL 已确认存在，完整 ingest 未实测"**——不要写"已走通"或"未走通"两面话，只说已确认的部分。

### 用户判定 vs agent 推断（2026-08-31 实战教训）：**用户说"X 服务正常"时不要凭错误信息推翻——先验证 health 端点，再判定责任方**

agent 看到 `[PROCESSING_ERROR]` 错误信息就推断"服务端挂了"，连续几轮坚持这个错误判断，但用户始终说"OV 云服务正常"。教训：**用户对自有服务的健康判断通常基于实际使用经验，比** **agent 从单次错误信息里推断更可靠**。遇到矛盾时：

1. **先 curl 服务 health 端点**确认服务端活没活（OpenViking: `/health`，不鉴权，返回 `{healthy, version, auth_mode}`）
2. **再看错误信息里的路径前缀**判定责任方（`/local/` = 客户端；`/api/...` = 服务端；`5xx` = 服务端；`4xx` = 请求构造或鉴权）
3. **不要从单一错误信息外推到「服务端挂了」**——服务挂的判定需要至少 3 个独立证据（health fail + 多端点 fail + 用户复述错误一致）
4. **不要把"我用 CLI 失败"等同于"服务不可用"**——客户端工具 bug 和服务端可用性是两回事

反面案例：本会话浪费 4+ 轮在「服务端挂了」的判断上，每次都被用户的"OV 正常"打断，最终发现服务端完全健康，错误是 `ov` CLI 客户端的本地锁文件生成 bug。**用户拍板"服务正常"时，第一轮就该验证 health 端点，而不是继续在客户端层面 debug。**

## 工具/API/平台怪癖

### MiMo-v2.5 vision 支持：用 OpenAI 标准 image_url 格式，base64 data URI 嵌套在 image_url.url 里。{"type":"

MiMo-v2.5 vision 支持：用 OpenAI 标准 image_url 格式，base64 data URI 嵌套在 image_url.url 里。{"type":"image"} 或裸 image 字段不行。image_tokens≈2040,3-8 秒/图。完整模型列表含 mimo-v2.5-asr/tts/tts-voiceclone/tts-voicedesign。封口原则:查不出≠不存在,vision 类需求实测 OpenAI 标准格式确认,不能凭直觉否定。
### 用户对 MiMo key 在聊天中粘贴说"没事,你配置进行就行"(2026-08-26)。不要主动 rotate,不要过度反应要求安全操作,按用户判断执行。MemOS Krolik

用户对 MiMo key 在聊天中粘贴说"没事,你配置进行就行"(2026-08-26)。不要主动 rotate,不要过度反应要求安全操作,按用户判断执行。MemOS Krolik 凭据授权码也适用同样规则。
### MCP/LSP 通讯:能 TCP 直连就直连(localhost)。"装客户端"不是银弹。

MCP/LSP 通讯:能 TCP 直连就直连(localhost)。"装客户端"不是银弹。
### 汉字输入法:选 CrazyDave 14键,设置选词 8。

汉字输入法:选 CrazyDave 14键,设置选词 8。
### MCP/voice_clone.py:模仿我的笑声不完美(差一截)但仍可用。

MCP/voice_clone.py:模仿我的笑声不完美(差一截)但仍可用。

## 浏览器工具集 / Chrome DevTools Protocol（2026-09-03 实战确立）

### 浏览器工具集口径校正：MEMORY 里"完整 browser_navigate 等十余项工具集"是过期描述

**症状**：用户说"用你内置的浏览器"——agent 凭 MEMORY 里某次会话记录的"完整浏览器工具集"臆断有 `browser_navigate` / `browser_click` 等工具，**实际 system prompt 注入的工具列表里没有这套**。本机实测可用的浏览器相关工具只有：

| 工具 | 能力 | 限制 |
|------|------|------|
| `desktop_preview` / `drive_preview` | 预览面板 + 操控当前页 | 只操控用户在看的 tab；agent 看不到实时页面（除非读 preview.read） |
| `computer_use` | 桌面 UI 操控（CUA driver） | 后台 first delivery，可不抢用户焦点；截图+坐标点击 |
| `web_search` / `web_extract` | 搜索/抓内容（ddgs 后端 或 Exa 兜底） | ddgs 后端要装 `ddgs` 包到 hermes-agent venv：`uv pip install --python <venv>/Scripts/python.exe ddgs` |
| `web_fetch` | 兜底 HTTP 抓取 | — |
| `browser_use` / chrome-devtools MCP | 高级浏览器自动化 | **chrome-devtools MCP 默认 `enabled: false`，要 `hermes config set mcp_servers.chrome-devtools.enabled true`**；MCP 工具要新会话才注入 |

**铁律**：用户说"用你内置的浏览器"时，**先用 `tool_search` 查 capability**，确认有再调用，别凭 MEMORY 臆断。

### Chrome DevTools Protocol 直连实战范式（绕开 MCP 加载不全）

**场景**：chrome-devtools MCP 启用了但本会话 toolset snapshot 没注入；或者用户已经启了一个 Chrome 在 9222/9014 等远程调试端口。

**完整工作流**（无需任何 MCP / 插件，Python 直连）：

1. **探测 ws endpoint**：
```python
import requests
ws_url = requests.get('http://127.0.0.1:9014/json/version').json()['webSocketDebuggerUrl']
# ws://127.0.0.1:9014/devtools/browser/<UUID>
```

2. **建立 ws（带 id 计数器管理多调用）**：
```python
import websocket, json, time
ws = websocket.create_connection(ws_url, timeout=10)
ws.settimeout(30)
id_counter = 0
def call(method, params=None, session_id=None):
    global id_counter
    id_counter += 1
    msg = {'id': id_counter, 'method': method, 'params': params or {}}
    if session_id:
        msg['sessionId'] = session_id
    ws.send(json.dumps(msg))
    while True:
        r = json.loads(ws.recv())
        if r.get('id') == id_counter:
            return r.get('result', {})
```

3. **创建 + 附着 tab + 执行 JS**：
```python
# 创 tab
tid = call('Target.createTarget', {'url': 'https://example.com'})['targetId']
# 附着（flatten=True 合并 event）
sid = call('Target.attachToTarget', {'targetId': tid, 'flatten': True})['sessionId']
time.sleep(3)  # 等加载
# 拿 DOM
title = call('Runtime.evaluate',
    {'expression': 'document.title', 'returnByValue': True},
    session_id=sid)['result']['value']
```

4. **拿 img src / innerText 批量**（IIFE 包裹防变量复用冲突）：
```python
EXPR = '''
(() => {
    const all = document.querySelectorAll('img');
    const cos = [];
    for (let i = 0; i < all.length; i++) {
        for (const s of [all[i].src, all[i].currentSrc,
                          all[i].getAttribute('data-original'),
                          all[i].dataset.src]) {
            if (s && s.indexOf('cos.ap-beijing') >= 0 && !cos.includes(s)) cos.push(s);
        }
    }
    return JSON.stringify(cos.slice(0, 5));
})()
'''
urls = json.loads(call('Runtime.evaluate',
    {'expression': EXPR, 'returnByValue': True},
    session_id=sid)['result']['value'])
```

**两个实战陷阱**：

- **`Runtime.evaluate` 变量跨调用复用**——同一 sessionId 下 `imgs` 这种变量名会报 `SyntaxError: Identifier 'imgs' has already been declared`。**永远用 IIFE 包裹** `(() => { const imgs = ...; return ...; })()`
- **`Page.navigate` 之后立即 `Runtime.evaluate` 会拿到旧 DOM**——必须 `time.sleep(2-5)` 等加载完（看页面复杂度），尤其是 SPA

5. **批量抓图直链后 curl 下载**（CDN 上的图直接 urllib 即可）：
```python
import urllib.request, os
for i, u in enumerate(urls):
    fn = f'imgs/故宫_{i}.png'
    req = urllib.request.Request(u, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://digicol.dpm.org.cn/'  # 关键：referer
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        with open(fn, 'wb') as f:
            f.write(r.read())
```

**故宫数字文物库 cos CDN 真品图范式**（已在伏妖记美术考据实战验证）：
- URL 模式：`https://shuziwenwu-1259446244.cos.ap-beijing.myqcloud.com/relic/<uuid>/<file>.png`
- 列表页直接 `Runtime.evaluate` 拿 cos URL 列表 → curl 下载（不需要登录）
- Referer header **必须**写 `https://digicol.dpm.org.cn/`，否则可能 403/404

### Chrome 远程调试模式启动（Windows 本机 + 自己的登录态）

**问题**：默认 Chrome 启了 inspect server（`chrome://inspect/#remote-debugging`，端口如 12812）但**不是 remote-debugging 协议**——`browser_navigate` / CDP MCP / 直连 ws 都连不上。

**修法**：**重启 Chrome** 加 remote-debugging 参数：
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" \
  --user-data-dir="C:\Users\<user>\AppData\Local\Google\Chrome\User Data" \
  --remote-debugging-port=9014 \
  --remote-allow-origins=* \
  --no-first-run \
  about:blank
```

**关键细节**：

1. **`--user-data-dir` 必须是主 Chrome 的 profile 路径**——直接复用登录态
2. **`--remote-debugging-port` 任意可用端口**（9014 / 9222 / 9229 都行）——避开 9222（hermes 内置独立无痕 Chrome 占着）
3. **`--remote-allow-origins=*` 必须**——否则 ws 会被 Chrome 403
4. **`--no-first-run` 避免首启弹窗**

**Single-instance 冲突解法**：Chrome 默认 user-data-dir 有 Singleton Lock，正在跑的主 Chrome 实例会让新启实例退化为空 user-data-dir，导致**新 Chrome 没登录态**。两种解法：

- **方法 A（推荐）**：用 `mklink /D <link> <real_dir>` 做目录 junction，让 agent 启的实例直接读写主 profile
  ```bash
  cmd /c mklink /D "C:\Users\HMSJ\AppData\Local\hermes\cache\chrome-agent-profile\User Data" \
       "C:\Users\HMSJ\AppData\Local\Google\Chrome\User Data"
  # 然后 --user-data-dir=C:\Users\HMSJ\AppData\Local\hermes\cache\chrome-agent-profile\User Data
  ```
  **登录态直接复用** + 单实例 lock 由主 Chrome 持有，新 Chrome 是同一 profile 视图
- **方法 B**：kill 主 Chrome 后再用新参数启（破坏性，慎用）
- **方法 C**：复制 user-data-dir 到独立目录——但 cookie / Local State 不全 = 没登录态

**判定已起 Chrome 用的端口**：
```bash
netstat -ano | grep "LISTENING" | awk '{print $2}' | awk -F':' '{print $NF}' | sort -u
# 或 netstat -ano | grep ":<port>"
```

`/json/version` 返回 200 + 看到 `webSocketDebuggerUrl` = 该端口是 remote-debugging 协议端口；
只有 inspect 服务（端口如 12812）无 HTTP 响应——`curl /json/version` 返回空但 `curl` exit 0。

### Chrome DevTools 路径速查（哪个端口是 remote-debugging）

| 端口 | 谁在用 | 怎么验证 |
|------|--------|----------|
| 9222 | Hermes 独立无痕 Chrome（chrome-cdp-profile）| `curl http://127.0.0.1:9222/json/version` → 200 + `webSocketDebuggerUrl` |
| 12812 | Edge inspect 服务（chrome://inspect/#remote-debugging 显示的 Server）| `curl http://127.0.0.1:12812/json/version` 返回空但 exit 0 = ws only |
| 9014 / 9229 / 其他 | 你手动启的 Chrome（加了 `--remote-debugging-port`）| 同 9222 验证法 |

**踩坑教训**：Edge 的"inspect Server running at 12812"**不是**remote-debugging 协议端口——是 Edge 内置的 DevTools UI service。chrome-devtools MCP 连不上 12812。

## MEMORY/Skill 维护方法论

### MEMORY 维护铁律（2026-08-26 实战教训）：①memory 应该装"可执行铁律 + 关键事实"，不该装"配置/操作手册/事件档案"——这些迁到 skill 或 doc

MEMORY 维护铁律（2026-08-26 实战教训）：①memory 应该装"可执行铁律 + 关键事实"，不该装"配置/操作手册/事件档案"——这些迁到 skill 或 docs；②memory 操作必须用段号文本锚点（search+patch），不要用 parts 数组索引；③每次操作前先 cp 一份 .bak 备份；④改完跑自检脚本（grep 关键词、验证结构、确认关键铁律 NOT lost）；⑤精简某条前先看："这段内容 skill 里有没有更详细的版本？"——有则删，无则保留精简版。

## 边角工具/一次性经验

### OS X 装机/卸载/不认设备/X11/WindowServer/dev dir/diskutil/EFI NVRAM/PRAM reset/RAM 排错/HFS+/APFS/Re

OS X 装机/卸载/不认设备/X11/WindowServer/dev dir/diskutil/EFI NVRAM/PRAM reset/RAM 排错/HFS+/APFS/ReFS/ext4 恢复/superblock 等:Claude 不应直接指挥(macOS CLI 误操作不可逆)。如确需动作,先让我用本机 Terminal 跑,核对了你再敲车。
### 实景照片线稿化(在描线风格表 + Procreate 笔刷)两次,均拿到四颗星。

实景照片线稿化(在描线风格表 + Procreate 笔刷)两次,均拿到四颗星。
### 用 ADC 抓大文件字节(100-500MB)统计独特 MD5,1M 速率够用。

用 ADC 抓大文件字节(100-500MB)统计独特 MD5,1M 速率够用。

---

## 工具/服务彻底卸载铁律（2026-09-11 DSH 清理实战扩展）

### 删磁盘 ≠ 删行为铁律：`.hermes.md` 与 MEMORY 是行为契约，不能在"全删 X"指令里顺手删

**症状**：用户说"电脑上所有 DSH 的都要删掉"——agent 顺手把 `~/.dsh/` 删了、计划任务删了、bridge 脚本删了，**也**想顺手把 `.hermes.md` 第 10 行 "执行引擎默认 DSH" 这条铁律段和 MEMORY 里同源条目删了——这是越权。行为铁律改了，**未来所有 agent 会话**的默认行为都跟着变，agent 不能凭单次"全删"指令单方面决策。

**铁律**：

1. **行为契约类资产（`.hermes.md` / MEMORY.md / `~/.hermes/memories/*.md` / OV behavior pattern 实体）永远不与磁盘清理混在一起执行**——磁盘清理完单独列"待拍板尾巴"返回给用户拍板。
2. **"全删 X"的语义默认是"删 X 的所有磁盘痕迹"**，不包含"删描述 X 是什么的所有文档"。这是两种 action，要分开问。
3. **MEMORY 里描述 X 的条目，删 X 后要主动提一句"MEMORY 那条要不要同步删"**，但**等用户拍板**——MEMORY 描述可能对未来 agent 还有用（"X 不在了"本身就是事实）。
4. **`.hermes.md` 行为铁律段的删除 = 改 agent 默认行为**——必须用户显式说"删掉那条铁律"才能动。

**反模式**：

- ❌ "用户说全删 = 顺手把行为铁律段也删了，反正 DSH 不在了那条也没用"——**没用 ≠ 应该删**，契约清理是契约清理
- ❌ "把 MEMORY 那条同步删了保持一致性"——**MEMORY 不与磁盘同步**，MEMORY 是 user-facing 知识库，不是系统配置
- ❌ 把"删 DSH"的执行报告写成"已删 DSH 全部"——必须区分"磁盘已删"和"行为铁律已删（待拍板）"

**正面案例**（2026-09-11 DSH 清理）：用户拍板"清理 DSH" → 删磁盘；用户拍板"电脑上所有 dsh 都要删掉" → 删磁盘 + 删计划任务 + 删 Hermes 侧 bridge 脚本；**最后明确列 `~/.hermes.md` 第 10 行 DSH 铁律段 + MEMORY 同源条目 = 待拍板尾巴**，等用户回来核一遍再动。

### `~/.agentsanywhere/<tool>-bridge-*` 是 Hermes 桥，不是目标工具的目录（同名陷阱）

**症状**：清理 DSH 时看到 `~/.agentsanywhere/dsh-bridge-next/` 目录，名字含 `dsh` ——直觉是 DSH 的产物应该删。**但它是 Hermes 的 agentsanywhere 桥插件的部署目录**，跟 DSH 的 `~/.dsh/agents-anywhere/` 是**完全不同的两套东西**，只是名字撞了。删了 = Hermes agentsanywhere 桥功能挂。

**判定铁律**：

1. **清理任何工具前，先 `ls -la` 看路径是软链、目录还是文件**——同名不代表同源
2. **`~/.agentsanywhere/X-bridge-*` 形态是 Hermes 的桥（user_install/部署位）**，不是源工具的一部分。`~/.dsh/agents-anywhere/` 才是 DSH 自己的
3. **判断方法**：看父目录。父目录是 `~/.agentsanywhere/` = Hermes 桥插件；父目录是 `~/.dsh/` = 目标工具本体
4. **`agents-anywhere` 字样在两个工具的目录树里都可能出现**——**Hermes 侧 = bridge 部署位**，**目标工具侧 = source tree 子目录**。同名巧合，机制不同

**反模式**：

- ❌ 看到 `dsh-bridge-next` 字样就当 DSH 资产删
- ❌ 不查父目录就推论归属
- ❌ 清理后没验证 Hermes 桥功能是否还在

**正面验证**（DSH 清理实战）：保留 `~/.agentsanywhere/dsh-bridge-next/` 后跑 `ls` + 读 `connector-settings.json` + 检查 `logs/` 内容——确认它是 Hermes 桥的 connector 配置目录，110B 文件 + logs 目录，与 DSH 主目录 `~/.dsh/` 完全独立。

### 清理类任务"扩展边界"的拍板节奏（2026-09-11 DSH 实战确立）

**症状**：用户清理任务经常**逐步扩边界**——"清 ~/.dsh" → "电脑上所有 dsh 都要删掉"。每轮扩展都有新一层（计划任务、注册表、服务、bridge 脚本、skill 索引、行为铁律、MEMORY）。**替用户决策每层"算不算属于所有" = 越权**。

**正确工作流（每轮扩展边界时）**：

1. **全量盘点当前边界**——并行 5-10 个 grep/ls 查所有候选位置（磁盘/计划任务/PATH/注册表/启动项/Program Files/用户家目录/全盘 1-3 层）
2. **分类列代价清单**——按"必删/可删/保留/B2 类边界争议"分组
3. **把所有 B2 类（边界争议）单独列给用户拍板**，不要替用户拍板：
   - "B2 = X 是 Hermes 桥还是 DSH 桥？"（带 `ls` 证据）
   - "B1 = 删磁盘还是含行为铁律段？"（带 `.hermes.md` 行号 + MEMORY 段落引用）
4. **执行时**严格按用户拍板的边界，**不替用户扩大也不替用户缩小**
5. **每层拍板完报告**——明确"已删"vs"待拍板"两个状态，不混淆

**反模式**：

- ❌ 用户说"清理 DSH"，agent 直接列"DSH 全机器清单：12 项"→ 全删——这是把"清理 DSH 主目录"擅自扩成"全机器卸载"
- ❌ 用户说"全删"，agent 区分"激进/保守"两个选项让用户拍板——**已经明示全删了不该再问"激进还是保守"**，除非有明确的"行为契约"边界争议
- ❌ 边界拍板问题用 `clarify` 工具弹窗——MEMORY 已固化：clarify 弹窗用户看不见，必须**打字发 markdown 选项**

**节奏口诀**：

> 看到"全部/所有" → 不动手 → 先全量盘点 + 列边界争议 + 等拍板 → 拍板后**一刀切**不重问

### 软链反向：清理工具时先查 `~/.X/skills` 等软链避免破坏宿主

**症状**：DSH 主目录 `~/.dsh/skills` 是软链 → `~/.hermes/skills/`。删 `~/.dsh/skills` = 删软链本身（无害），**但删 `~/.dsh/` 时如果连带删软链指向的源** = Hermes skills 跟着挂。

**判定**：

- `ls -la` 看 `skills` 行第一个字符是 `l` = 软链
- `readlink -f ~/.X/skills` 看真实目标，**目标不在 `~/.X/` 树内** = 跨宿主软链
- 删父目录时**软链本身可以一起删**（无害），但**绝对不能 rm -rf 到软链目标路径**

**陷阱**：跨宿主软链 = 双删风险。清理 X 时如果 agent 自动展开软链到目标路径 rm = 误删宿主。**操作原则**：`rm -rf ~/.X/` 删除 X 主目录时软链本身会被一起删（`rm -rf` 不跟随软链进入目标），但**之后任何"清理残留"或"遍历目录"的脚本都可能误入软链目标**。

## 飞书 / lark-cli 写入铁律（2026-09-03 实战扩展）

### `+media-insert` 返回 ok:true ≠ 图片真的渲染出来了

**症状**：跑完 `lark-cli docs +media-insert --doc X --file ./fig.jpg`，返回 `{"ok":true,"data":{"block_id":"...","file_token":"..."}}`，以为插入成功。**几小时或一天后用户打开 doc 发现图都裂了**——fetch XML 里图块还在，但 file_token 失效。

**根因**：飞书 img block 的 file_token 有独立生命周期（实测约 24h）。bot identity 生成的 token 失效概率更高，user identity 相对稳定但仍有失效窗口。**client SDK 不会告诉你"这张图明天会失效"**——它只说"现在创建成功"。

**铁律**：插入图后**必走视觉验证**，不要等用户来问"图呢？"。

**验证流程**：
1. `docs +fetch --doc X --scope full --detail full --format pretty` → 找 `<img ... name="...">` 节点确认 DOM 存在
2. 用 `vision_analyze` 拉回每张图（拼 `/file/<file_token>` URL 给 vision_analyze 读）
3. **重点关注"新插入的图"和"doc 末尾位置"**——失效最容易出现在末尾新追加的图块

**反面教训**：本次会话我跑 18 次 `+media-insert` 全部 code=0 就宣告"18 张图嵌入完成"，用户问"图呢？"才暴露 9 张新有效图 + 9 张失效旧图。**视觉验证不可省**。

### `+media-preview` 404 ≠ doc 里的图坏了

`docs +media-preview` 走的是 Drive token 路径（独立存储），docx 内嵌 img block 的 file_token **不在这个路径下**——`media-preview` 拉 docx inline 图会返 404。

**正确渲染验证**：
- ✅ 用 `vision_analyze` 直接读 `src=` URL（拼 `/file/<token>` 或走 internal CDN）
- ✅ 或者让用户打开 doc 截图——飞书客户端有内部 endpoint 拿 inline 图
- ❌ 不要靠 `media-preview` 判断"图坏了没"

### `lark-cli` 路径必须 cwd-相对

**症状**：`--file C:/path/to/file.jpg` → `unsafe file path: --file must be a relative path within the current directory`。多个命令都触发：`+media-insert`、`+media-upload`、`+update --content @path`、`drive +download --output`。

**铁律**：
- `--file`/`--output` 都用 `./relative/path`（以 cwd 为基准）
- **不要传绝对路径** `C:/...` 或 `/tmp/...`
- 路径带 `@` 前缀（如 `--content @./file.md`）也走同样规则
- 如要传多文件路径，先 `cd <目录>` 再传 `./文件名`

**批量处理时**：把要用的图片复制到 cwd 下的子目录（如 `./_imgs/`），用 `shutil.copy()` 而非直接传原路径。

### img block schema 直连 raw API

**当 `+media-insert` 不可用/失效时**，绕开它直接 POST 飞书 OpenAPI 创建 img block：

```
POST /open-apis/docx/v1/documents/<doc_id>/blocks/<root_block_id>/children
Body: {"children": [{"block_type": 27, "image": {"token": "<file_token>", "width": 1200, "height": 1600}}]}
Params: {"document_revision_id": -1}
```

**关键**：
- parent 用 root block id（=document_id 自身），不要用任何子 block id
- `block_type=27` 是 image block
- image 字段名是 `token` 不是 `file_token`（lark-cli `+media-insert` 内部转换后是这个）
- `width`/`height` 必填，否则 invalid param（错误码 1770001）

**file_token 来源**：
- `lark-cli drive +upload --file ./X.jpg` 拿到永久 token（Drive 资源池）
- `lark-cli docs +media-upload --file ./X.jpg --parent-type docx_image --parent-node <root_block>` 拿到 doc internal token（用于 inline block）
- 两种 token 走不同 endpoint：Drive 上传的不一定能直接 inline 到 docx——必须先 `+media-insert` 流程或 `+media-upload` 到 doc parent

### 中文文件名 URL encode

公开图源 URL 含中文文件名时（commons、博物馆下载链接等），必须 `urllib.parse.quote`：

```python
import urllib.parse
url = f'https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote("江帆楼阁图.jpg")}'
# → https://commons.wikimedia.org/wiki/Special:FilePath/%E6%B1%9F%E5%B8%86%E6%A5%BC%E9%96%A3%E5%9B%BE.jpg
```

**反例**：直接拼字符串 `f'https://.../江帆楼阁图.jpg'`——requests/urllib 在 MSYS/Cygwin 环境下会被 glob 展开或 URL 截断，401/404 假象。

### 中国文物图源的特殊抓取路径

中文语境下要找古代器物/书画/壁画参考图，三个公开渠道比 WikiCommons 通用搜索更可靠：

**1. WikiCommons `Special:FilePath` 直链探测**

```python
import urllib.request, urllib.parse
def head(url):
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.url
    except Exception as e:
        return None, str(e)

# HEAD 探测（不下载）文件存在性
files = ['越王勾践剑.jpg', '江帆楼阁图.jpg', '江帆樓閣圖.jpg']
for fn in files:
    u = f'https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(fn)}'
    s, real = head(u)
    if s == 200:
        print(real.split('?')[0])  # 清掉 utm 参数
```

**已知坑**：
- 中文名图常**只有仿/摹本**——例如 commons 的 `江帆楼阁图.jpg` 是后仿本，不是台北故宫藏真迹。**必须用 vision_analyze 看图确认是不是真迹**，不能信文件名
- `Garuda_cliff_in_Tirumala.jpg` 文件名像金翅鸟，**实际是印度天然山崖**——典型 commons 误导
- 数字敦煌 (`ip.e-dunhuang.com`) 的 `oss.e-dunhuang.com/dha-media/thumbnail/.../{uuid}.webp` 缩略图路径**必须带 empower token**，裸路径 415；详情页要登录才能拿全分辨率
- 故宫数字文物库 (`digicol.dpm.org.cn`) 缩略图 CDN 是 `shuziwenwu-1259446244.cos.ap-beijing.myqcloud.com/relic/...`——**直链可下**，referer 留空也 OK，但视觉验证必走（避免像 commons 那种仿本）

**2. DDGS images 反查（命中率高于 text 搜索 5-10x）**

```python
# install: uv pip install --python <hermes-venv>/Scripts/python.exe ddgs
from ddgs import DDGS
with DDGS() as ddgs:
    for img in ddgs.images("敦煌莫高窟359窟藻井金翅鸟", max_results=15):
        print(img.get("image"), "|", img.get("title")[:50])
```

**为什么 text search 找不到图**：百度/知乎/zhihu column 里的高清扫描图**没有 alt-text、没有正规文件名**，text 搜索命中后看搜索结果无用。**images search 直接命中图源 URL**，命中率显著高于 text search。

**3. 多 tab 并发抓 cos CDN（CDP 直连）**

如果页面有 `shuziwenwu-*.cos.ap-beijing.myqcloud.com` 这种 CDN，**不需要登录**，但 page-by-page 太慢。用 CDP ws 多 tab 并发（详见本 skill「Chrome DevTools Protocol 直连实战范式」节）：

```python
# 在故宫数字文物库搜"剑"后，Runtime.evaluate 拿全部 cos URL
EXPR = '''
(() => {
    const all = document.querySelectorAll('img');
    const cos = [];
    for (let i = 0; i < all.length; i++) {
        for (const s of [all[i].src, all[i].currentSrc,
                          all[i].getAttribute('data-original'),
                          all[i].dataset.src]) {
            if (s && s.indexOf('cos.ap-beijing') >= 0 && !cos.includes(s)) cos.push(s);
        }
    }
    return JSON.stringify(cos);
})()  // ⚠️ 必须 IIFE 包裹 — 同 sessionId 跨调用变量名会冲突
'''
```

**然后 curl 批量下载**：

```python
for u in cos_urls:
    req = urllib.request.Request(u, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://digicol.dpm.org.cn/'  # 关键：故宫 cos CDN 强制 referer
    })
    urllib.request.urlopen(req, timeout=15).read()  # → 本地保存
```

**视觉验证必做**：commons 文件名误导率极高——任何抓到的图，**用 vision_analyze 看一眼再嵌入 doc**，caption 必须注明"WikiCommons 来源仿/摹本"或"真迹"。

---

## 维护规则

- 新增条目：先在 MEMORY.md 临时记录，验证落地 1 周后确认是"铁律"还是"档案"，铁律留 MEMORY、档案迁本 skill
- 删除条目：先 grep 确认没有引用方（skills / cron / docs）
- 分类调整：触发场景变了就调整分类（不要为了分类而分类）

## 与 MEMORY.md 的边界

- MEMORY.md：每次会话必读 = agent 默认行为约束
- 本 skill：按需加载 = 特定场景的踩坑档案/工具怪癖

---

# 跨类铁律（agent 写盘 / 排障 / 自我描述类根因，2026-09-03 实战确立）

## 写入工具的"verified: true ≠ 实际写盘"铁律（patch/write_file 全家桶）

**症状**：`patch` 工具回执 `verified: true` 后 mtime 完全没动，grep 关键锚点也找不到。同会话内 `write_file` 全量写的新文件真实落地，但 `patch` 增量改的一行都没生效。**`verified` 是工具自报 = 进程内 parse 成功 ≠ 磁盘 IO 成功**。

**铁律三件套**（任一文件改动前后必跑）：

```bash
# 1. 写之前：记基线
stat -c '%Y %s %n' <file>  # mtime + size
grep <独有锚点> <file>     # 不存在则 grep 不到

# 2. 写之后：验证
stat -c '%Y %s %n' <file>  # mtime 变了
grep <独有锚点> <file>     # 命中
wc -c <file>               # size 变了

# 3. 不信信源的话：用 terminal + heredoc 或 Python 路径重写
# （patch verified 但 mtime 没动 → 立刻切路径，不要再 retry patch）
```

**批量改动（≥3 文件）收尾额外加**：

```bash
git status --short                                # 声称改的文件数 == modified 数
for f in <claimed_files>; do
  grep <独有锚点> "$f"                              # 每个文件 grep 唯一锚点
  stat -c '%Y %n' "$f"                              # mtime 不晚于声称 patch 时间
done
```

**任何不对齐 = 整个会话声称交付的 0% 是真交付**。铁律 1/2/3 都满足才算写盘成功。

**类级教训**：同根家族——`memory` 写入磁盘必须 grep 验证、`user_report`（"我改了 X"）必须 disk verify、agent 自我描述（"已固化"）必须 grep 验证。**工具/agent 的 self-report 不是现实**——磁盘 mtime + grep 才是。

---

## 工程排障两步铁律（2026-09-03 飞书端任务拍板扩展）

**任何工程排障 / 代码改写 / 配置文件修改任务，动手前必并行两步**：

### Step 1：`viking_search` 看 OV 沉淀

```python
# 飞书评论任务搜索示例
viking_search("飞书评论 软提示 全文档")
viking_search("feishu_comment session 持久化")
# 看是否已有"已拍板"结论
```

**为什么**：MEMORY/OV 里的"已拍板"结论可能没真正落地到代码（2026-08-28+ 反复出现的"已固化幻觉"模式）。先查沉淀 = 知道根因有没有前人诊断过，避免重新设计。

### Step 2：飞书端必 `skill_view(name='hermes-feishu-internals')`（2026-09-03 拍板"飞书端都走"）

**触发条件**：用户提到任何飞书侧技术问题 / 工程任务 / 排障 / 配置。

**覆盖范围**（按 SKILL.md 索引）：
- 评论 agent 事件链 / 访问控制 / 软提示陷阱 / 意图路由漏词 / 冷暴力兜底
- 群聊 require_mention 排查（姊妹篇：`feishu-gateway-setup`）
- 侧边栏会话显示 + state.db 持久化
- 健康度检查脚本

**不重叠**：
- 网关/配置层（lark-cli、.env、FEISHU_ALLOWED_USERS、port、restart、home_channel）→ `feishu-gateway-setup`
- 多用户协作业务规则（成员名单、角色、复盘）→ `feishu-multi-user-collab`（user-owned）
- 创作工作流（润色/三关/多方案）→ `feishu-comment-creative`（user-owned）

**共同点**：OV / skill / 官方 README 有方案而 agent 重新设计 = 浪费 token 还不一定对。**不查直接干**是工程排障最大的浪费。

---

## MEMORY 满载的"最小必要更新"模式（2026-09-03 实战）

**症状**：MEMORY 99% 满（15,998/16,000），新写一条铁律时 `add` 报超限。**正确做法不是"缩短新内容"，而是"先 remove 旧段腾空间，再 add 合并版新段"**。

### 模式三步

1. **先 grep anchor 查重**（避免新建一条和旧段重叠的内容）——本 skill 已有"用户陈述已做 → disk verify 优先"那条元铁律
2. **`remove` 旧段（精确 old_text 锚点）腾字符**——>100 字符的边际能腾出来
3. **`add` 合并版新段**——把旧段 + 新教训合成一条更精炼的版本，不是凭空新写

### 反模式

- ❌ **跳过 remove 反复 add**——`memory` 工具会反复报超限（"would put memory at 16,123 chars"），浪费 5+ 轮
- ❌ **只 add 不 remove 假装"不重要可以不删"**——MEMORY 满载是事实，必须腾空间
- ❌ **写超长新段不被合并**——400 字符的新段应该并进 200 字符的旧段，而不是独立

### 写盘验证同 3 件套（自检）

```bash
grep <新段独有锚点> MEMORY.md  # 必须命中
stat -c '%Y %s %n' MEMORY.md   # mtime 更新
```

**类级教训**：MEMORY 精简不是"少写"，是"该迁到 skill 的迁 skill、该合并的合并、该删的删"——保证每段都是当下必读的"铁律"，不是历史档案。`hermes-runtime-pitfalls` 本身就是这个模式的产物（2026-08-28 第一次精简）。

---

## 飞书评论 agent / AIAgent 集成踩坑（2026-08-31 实战 + 2026-09-04 实战扩展）

### AIAgent 没有 `skills=` 参数——skill 内容必须走 `system_message`（2026-08-31 飞书评论实战确立 + 2026-09-03 实战修正参数名）

**症状**：想把一个 skill（如 `feishu-comment-creative`）的内容自动注入到某次 agent 调用的 system prompt 里，但 `AIAgent.__init__()` 参数表里**没有 `skills=` 这个参数**。`enabled_toolsets` 只管工具开关，`skip_memory`/`skip_context_files` 只管上下文过滤——都没法加载 skill 内容。

**根因**：`run_agent.py` 的 `AIAgent` 设计时就没考虑"为单次调用注入一个 skill"的需求，`skills` 是 hub 级别的启动配置（不是 per-call 参数）。

**修法**：用 `system_message` 参数（不是 `prefill_messages`！见下方 ⚠️ 修正）——直接传 `str` 进 `AIAgent.run_conversation(user_message, system_message=...)` 或 `AIAgent(..., system_message=...)`。system_message 是真透传，内容直接进 system prompt 槽位。

**实战范本（`feishu_comment.py::_run_creative_agent`，2026-09-03 实战）**：
```python
prefill_system = _CREATIVE_AGENT_SYSTEM + "\n\n" + skill_text
agent = AIAgent(
    ...,
    system_message=prefilled_system,         # ← 关键：用 system_message 不是 prefill_messages
    enabled_toolsets=["feishu_doc", "feishu_drive"],
    max_iterations=25,
)
result = agent.run_conversation(
    prompt,                                    # ← 第一个位置参数是 user_message
    system_message=prefilled_system,         # ← 也可在这里传
    conversation_history=history or None,
)
```

**自动同步特性**：system_message 是运行时加载（每次 `_run_creative_agent` 都从磁盘读 SKILL.md），所以改 skill 文件下次触发立即生效，不需要重启 skill 索引也不需要重新发布。

**限制**：单次 system_message 总长建议 < 8K 字符——超长会挤掉 LLM 实际 system prompt 槽位，模型可能忽略 skill 工作流。本会话实测 2682 chars（含 system 硬要求 + skill 1523 chars）正常。

**⚠️ 修正（2026-09-03 实战踩坑）**：`AIAgent.run_conversation` 的真实签名是 `run_conversation(user_message, system_message=None, conversation_history=None, ...)`，**没有 `prefill_messages` 参数**。如果传 `prefill_messages=...` 会抛 `TypeError: run_conversation() got an unexpected keyword argument 'prefill_messages'`。本 skill 之前的修法描述错误——现已按真实签名修正。**任何 agent 集成代码看到"prefill_messages 注入 skill"的说法都先 `inspect.signature` 实际代码确认参数名**，别按旧描述写。

### Python `if/else` 分支初始化变量 + 后续统一引用 → `UnboundLocalError`（2026-08-31 飞书评论实战确立）

**症状**：在主流程末尾新增一行 `is_creative = func(a, b, c)`，其中 `b` 和 `c` 只在 `if local: ... else: ...` 分支的 `local` 分支里初始化。运行到 `else` 分支时抛 `UnboundLocalError: cannot access local variable 'X' where it is not associated with a value`——主流程全挂。

**根因**：Python 是编译期决定变量作用域。`func` 引用了 `b`/`c`，编译器把整个函数里的 `b`/`c` 标记为"local"，即使某个分支从未 `b = ""` 也没用——运行时仍抛 `UnboundLocalError`，**不是 `NameError`**。编译期不报错，运行期才炸，且炸的是独立路径不是开发路径（端到端测试才能发现）。

**修法**：用 `locals().get(name, "") or ""` 兜底——既兼容 `None` 又兼容"未绑定"两种状态：
```python
is_creative = _detect_creative_intent(
    current_text,
    locals().get("target_text", "") or "",  # only set for local comments
    locals().get("root_text", "") or "",    # only set for local comments
)
```

**类级教训**：在 `if A / else B` 分支后**新增引用任一分支变量的代码**，必须用 `locals().get()` 兜底，而不是直接引用。直接引用看起来"应该没事"（分支里都有初始化），但只在一个分支里有就够炸了。**端到端测试是唯一能发现这种 bug 的手段**——单跑那个分支测不出来。

### 飞书评论 agent 创作/回复分流：reply agent 不能做创作任务（2026-08-31 实战确立）

**症状**：用户在飞书文档评论里说「润色这三句」/「重写这段」/「节奏更紧」/「做出合理改动」，bot 回复「读不到文档内容。我只能基于引用片段润色这三句话……」——基于片段敷衍，不读全文，不出多方案。

**根因**：默认 `_run_comment_agent` 是为**回复型任务**设计的（quote-anchor、thread timeline、`skip_context_files=True`、`skip_memory=True`）。LLM 在该路径偷懒——`_COMMON_INSTRUCTIONS` 里的 "If the quoted content is not enough, use feishu_doc_read to read nearby context" 是**建议**不是要求，LLM 会跳过直接基于片段输出。

**修法（机制层修复，不是 patch）**：关键词路由分流——`_detect_creative_intent(*texts)` 命中 → `_run_creative_agent(prompt, client, session_key)` 复用 AIAgent 但 `prefill_messages` 注入 skill 全文 + `_CREATIVE_AGENT_SYSTEM` 硬要求（先调 `feishu_doc_read` 才能输出、不许说"读不到"）+ `max_iterations=25`。

**19 组触发词正则**（命中即路由到 creative agent）：
润色、打磨、重写、改.{0,6}(这场|这段|这句|这场戏|对白|台词)、优化.{0,6}(对白|台词|剧本|场景|分镜|画面|动作)、(调整|改).{0,4}(节奏|结构|人物|口吻|情绪|语气)、做出合理改动、(补|加).{0,4}(一句|一段|几场|场戏)、(改写|改写为|改写成)、换个写法、(试试|换一个).{0,6}(写法|版本|方案|路子)、(再来|重做).{0,6}(一版|一下|一次)、(怎么写|怎么改|怎么调)、(更好|更紧凑|更利落|更准|更狠|更冷|更顺).{0,4}(点|些|一点|一些)?、(再|更).{0,6}(紧|慢|狠|准|冷|利落|紧凑|克制|激烈).{0,6}(点|些|一点|一些)?、(节奏|人物|口吻|语气).{0,6}(更|再|要).{0,6}(紧|狠|准|冷|克制|激烈|稳|硬)。

**为什么不能"加一行 Creative work 章节"贴 `_COMMON_INSTRUCTIONS`？** 因为 `_COMMON_INSTRUCTIONS` 对 reply agent 和 creative agent 都生效——给 reply agent 加创作规则会污染它本身的回复逻辑；给 creative agent 加"建议读全文"又不构成硬要求。**结构上：reply agent `skip_context_files=True` + `skip_memory=True`，注定拿不到创作所需的全场景上下文**——必须独立 agent + 强 prefill 才能锁住工作流。

**验证（端到端实测）**：用户发「润色白双双扶房顶那三句对白要看得更紧更利落」→ bot 路由到 `_run_creative_agent` → agent 真调 `feishu_doc_read`（即使读不到也走完 skill 流程）→ 输出三个完整方案 A/B/C + plain text 对比表 + 改动说明。飞书 comment_id 已存在验证回复真发出去了。

**完整修复 commit 参考**：`fix(feishu-comment): creative/reply 路由分流`（589538288），含根因 + 设计选择 + 端到端验证 + 调试教训四节。

### bot 创作任务"贴原文/上下文不足" 兜底 = 创作决策外包，违反 skill 铁律（2026-09-04 飞书端任务实战确立）

**症状**：用户让 bot 在飞书文档评论里润色/改写/续写某段——bot 实际**有文档管理权限**（MEMORY 8/28 实战：str_replace 32 处修改成功 + revision 推进），但 bot 回复"上下文不足，请贴原文"或"在文档正文 @bot 重发"——**这等于把创作决策外包给用户**，违反 `feishu-comment-creative` skill 的铁律："必须出 2-3 个完整方案让用户挑，不许问'你倾向哪个方向'"。

**根因（两层）**：

1. **历史错误答案污染**：bot 历史回复里有过"上下文不足"的话——LLM 在新会话里看到这条 history，**直接复制粘贴旧答案**（典型"省力"模式：LLM 学会"问问题比出答案安全"）。即便系统提示里写"必须调 feishu_doc_read 读全文"，LLM 也会偷懒先问一句。
2. **没"用权限"能力**：agent 工具集里有 `feishu_doc_read` / `feishu_doc_update` / `feishu_doc_insert_block` / `feishu_doc_delete_block`（包装 lark-cli docs +update），但**默认 system 提示不要求 agent 真调**——agent 倾向"不调"（调失败会被 LLM 记为错过；不调能安全输出 1 版"上下文不足"）。

**修法（双层防御）**：

**Layer 1：stale history 过滤**——`_run_creative_agent` 加载 session history 后，**过滤掉**含"不可用"/"not available"/"调不通"/"上下文不足"等关键词的 assistant 消息。**让 LLM 不被旧错误答案传染**。

```python
# feishu_comment.py
STALE_KEYWORDS = ("不可用", "not available", "调不通", "上下文不足", "doc_read 不可用")
filtered = [m for m in history
            if not (m.get("role") == "assistant"
                    and any(kw in (m.get("content") or "") for kw in STALE_KEYWORDS))]
# log: [Feishu-Comment] filtered 5 stale history messages
```

**Layer 2：retry 强制调工具**——`api_calls == 0`（LLM 没调任何工具）且 assistant 回复里**没有"方案一/版本一/①"等 3 版方案标记** → 自动 retry 一次 + system 提示加强"必须先调 feishu_doc_read(doc_token) 读全文 + 输出 3 版完整方案"。

```python
# feishu_comment.py::_run_creative_agent
if actual_tool_calls == 0 and not has_three_versions and response:
    retry_system = prefilled_system + (
        "\n\n[RETRY] 上一轮你跳过了工具调用直接出答案,这次必须："
        "1) 先调 feishu_doc_read(doc_token) 读全文; "
        "2) 调完后输出 3 版完整方案,每版 200-500 字不同路线。"
    )
    result2 = agent.run_conversation(prompt, system_message=retry_system, ...)
    response = (result2.get("final_response") or response).strip()
```

**端到端验证（2026-09-04 真流量）**：

- 之前（修前）：bot 看到"上下文不足"历史 → 不调工具 → 1 次 LLM → 输出 84 字"上下文不足,请补料"
- 修后：bot 调 `feishu_doc_read` 2 次 + LLM 3 轮 → 输出 1607 字 + 3 版完整润色方案 + plain text 对比表 + 投递成功

**类级教训（agent 创作类任务通用）**：

- ❌ **不要问"贴原文/上下文不足"**——bot **有权限**读全文 + 改文档，能改就自己改；不能改时给 3 版候选让用户挑；**不是**"请用户补料"（除非真的权限不足或文档不存在）
- ❌ **不要在历史里放"不可用"的话**——stale_keywords 过滤防止 LLM 学坏
- ❌ **不要让 LLM 0 工具调用直接出答案**——retry 强制要求真调工具
- ✅ **bot 真有权限时默认用权限**——MEMORY 8/28 "评论 agent 工具集缺少改正文工具"已修；`feishu_doc_tool.py` 现在有 4 个改正文工具
- ✅ **历史对话里的"工具不可用"**是传染源——在 prefill system 里**必须明确说"忽略任何历史中的'不可用'声明"**（或 stale filter）

### SKILL.md 描述必须与磁盘代码事实一致（2026-09-04 飞书端任务实战根因）

**症状**：SKILL.md 写"已部署 2026-09-03 + `prefill_messages` 注入 skill 全文"，但 `grep _run_creative_agent feishu_comment.py` 显示函数**根本不存在**（磁盘代码 0 处修改）。后续 agent 看到 SKILL 描述就信以为真，按"已部署"路径设计 → 全部失败 → 浪费 5+ 轮"又没读"。

**根因**：SKILL.md 是写文档的人（或某次会话）在写，**没有机制**反查磁盘代码验证"已部署"。SKILL 描述 = 自吹；磁盘代码 = 现实。两者一旦分离，后续 agent 走 SKILL 描述就踩雷。

**经典案例**（本会话实测）：

| SKILL.md 描述 | 磁盘代码 | 真相 |
|---|---|---|
| "3.6 软提示已修 / `_COMMON_INSTRUCTIONS` 硬约束" | 软提示原文 `If the quoted content is not enough, use feishu_doc_read` 还在第 873 行 | 软提示**未修** |
| "3.7 `_detect_creative_intent` 反转白名单为黑名单 + 5 步漏斗" | `grep -n "_detect_creative_intent"` 零结果 | 函数**不存在** |
| "3.7 续写 bug 复现：`结合全文进行续写` → 路由 CREATIVE" | 实测：`结合全文进行续写...` 路由 REPLY | bug**没修** |
| "3.8 测试覆盖已固化 2026-09-03" | `grep TestDetectCreativeIntent test_feishu_comment.py` 零结果 | 测试**不存在** |
| "注入机制：`prefill_messages` 参数透传 SKILL 全文" | `AIAgent.run_conversation` 真实签名**没有** `prefill_messages` 参数 | 描述**错** |

**修法（agent 自查流程）**：

1. **任何引用 SKILL.md "已部署/已修" 描述前，先 grep 磁盘**：
   ```bash
   grep -n "<SKILL 提到的函数/变量>" <SKILL 提到的文件>
   # 零结果 = 描述与现实不符
   ```
2. **patch 任何 SKILL.md 后必须重启被描述的进程**——agent 自己 patch 完 SKILL.md，**不算部署**；进程加载新代码才算
3. **SKILL.md 的 `已部署 YYYY-MM-DD` 标注必须贴**真实 patch commit / file mtime——不靠"我记得我部署了"
4. **重写 SKILL.md 不只是改文档**——"已部署"的描述不能基于"我打算改"，必须基于 `git log` 或 `stat -c %Y` 的文件 mtime

**类级教训**（agent 自我描述类根因）：

- ❌ **不要让 SKILL.md 自吹"已部署"**——SKILL 是契约，磁盘代码是现实，两者必须对得上
- ❌ **不要把"我的代码会这么做"写进 SKILL.md**——只写"磁盘上代码实际会这么做"
- ✅ **任何"已部署" / "已修" / "已实现"描述必须有 file mtime 或 commit SHA 标注**——agent 自检时 `stat -c '%Y %n' <file>` 验证
- ✅ **patch 完 SKILL.md 立即 `grep <独有锚点> <file>` 确认落盘**——3 件套铁律同 patch 工具

### 创作类任务必须先查知识库再设计（2026-09-04 飞书端任务实战教训）

**症状**：用户让 bot 润色飞书文档评论，bot 假定"短剧剧本格式"（`△ 动作` + `切镜头` 三字标记 + 角色名+台词），结果用户拍板"**是电影剧本格式，翻翻知识库**"——知识库《国内标准剧本格式行业规范带跟脚》明确写"电影剧本正文**不标转场**、**不写镜号**、场次标题用 `第N场 地点 空间 日 内外`、对白用 `人名：（状态）台词` 不加引号"。

**根因**：agent 拍脑袋假定格式，没 `viking_search` / `skill_view('yaoyu-film-knowledge-base')` 查知识库。**MEMORY 8/08 5 创作 skill "知识库先行"铁律**——任何创作类任务第一步必查知识库，但 agent 直接跳到"想当然"。

**修法（创作类任务两步铁律）**：

```python
# Step 1: viking_search 查知识库
viking_search(query="<任务关键词> 格式 规范")

# Step 2: skill_view 加载相关 skill
skill_view(name="<相关创作 skill>")
# 例：创作类任务 → ai-movie-screenwriter / ai-movie-director / feishu-comment-creative

# Step 3: 从知识库中**精确摘录**格式规则（不是"我大概记得"）
# 例：知识库《国内标准剧本格式》第 4.2 节"场次标题"

# Step 4: 把规则写进 prefill system message（注入 LLM context）
```

**反面案例**（本会话）：

- 我加 SKILL 输出格式要求时，**凭 MEMORY 里"短剧分镜输出要求"那条记忆**写 `△ 切镜头`
- 用户："是电影剧本格式，翻翻知识库"
- 我才 `viking_search` 找到《国内标准剧本格式》第 4.2-4.6 节——**完全不同的格式规范**
- 修 SKILL.md：把 `△ 切镜头` 改成 `第N场 地点 空间 日 内外` + `人名：（状态）台词`

**类级教训（创作类任务通用）**：

- ❌ **不要凭 MEMORY/印象设计**——MEMORY 里的偏好是"用户当时的需求"，不一定是"现在要做的任务类型"
- ❌ **不要假定"短剧 vs 电影 vs 短片"格式**——每种格式规则不同（短剧有 △ 切镜头，电影没有；电影有画外音/闪回标记，短剧没有）
- ✅ **查知识库先于设计**——任何创作类任务（润色/审读/续写/扩写/格式调整），第一步 `viking_search("<格式/规范/范本>")`
- ✅ **知识库答案写进 prefill system**——LLM 不会自动查知识库，必须把查到的规范注入到 system_message
- ✅ **format 不确定时 grill 用户**——"这是电影/短剧/短片哪种格式？有参考吗？"——3 个选项秒答，胜过拍脑袋错路径


### feishu_doc/drive tool 跨线程 client 查找陷阱（2026-09-01 实战根因修复——三个串行坑中最难发现的一层）

**症状**：bot 挂 OK reaction、agent 真尝试调 `feishu_doc_read`（gateway.log 看到 `tool feishu_doc_read`），但 handler 返回 `Toolfeishu_doc_read returned error: Feishu client not available (not in a Feishu comment context)`。所有"工具不可用，无法读取文档全文"的退化报告——`fix(feishu-comment): creative/reply 路由分流`commit 之后还反复出现——根因都在这里。

**不是**：①toolset 没注册 `feishu_doc`（检查过，注册了）；②prefill 没注入 skill（注入成功 2682 chars）；③ACL 被拒（Access granted 日志存在）；④LLM 偷懒不调（LLM **真调了**，是 handler 找不到 client 报错）。**真实根因**：跨线程。

链路：
```
主线程 (gateway.handle_drive_comment_event)
  ↓ asyncio loop
worker thread A (loop.run_in_executor 调度 _run_creative_agent)
  ↓ set_doc_client(client) 存到 A._local.client      ← _local = threading.local()
  ↓ agent.run_conversation
  ↓ LLM 决定调 feishu_doc_read
worker thread C (DaemonThreadPoolExecutor —— agent.tool_executor)   ← OS thread 完全不同的 C
  ↓ handler _handle_feishu_doc_read
  ↓ client = get_client() 查 C._local.client → 没有 → 报错
```

`agent.tool_executor` 已用 `propagate_context_to_thread()` 传播 ContextVar，但 `set_client` 调用不在 turn context 里所以传不到 handler 端。

**临时方案（已落 commit `fix(feishu-doc-tool): client lookup fails across DaemonThreadPoolExecutor`，470145c1a）**：把 `tools/feishu_doc_tool.py` 和 `tools/feishu_drive_tool.py` 的 `_local = threading.local()` 改成进程全局 `dict[thread_ident] = client`，加锁，`get_client` 先查本 thread 找不到则 fallback 到任何已注册 client（同一事件通常只有一个 in-flight client，fallback 歧义有界）。

**根治方案**（未来 follow-up）：把这两个工具的 client 存改成 `ContextVar`，并在 agent 主循环 turn context 里调 `set_client`——这样 `propagate_context_to_thread()` 会自动传播，不需要 fallback。改动面超出本次故障响应范围。

**诊断口诀（必记）**：bot 挂 OK reaction 但不回复 + gateway.log 看到 `[Feishu-Comment] ========== handle_drive_comment_event START` 后突然断 + 上一行是 `Toolfeishu_doc_read returned error: Feishu client not available (not in a Feishu comment context)` + 创作意图命中 `Intent detected as CREATIVE` —— **一定是这个跨线程陷阱**，三层叠加坑（LLM 偷懒 → 变量未绑定 UnboundLocalError → 跨线程 client 查不到）最后一层。

**类级教训**：凡是用 `threading.local()` 存 handler 端需要的资源（lark client、DB connection、用户身份……），且 handler 由独立线程池执行（`DaemonThreadPoolExecutor` / `concurrent.futures.ThreadPoolExecutor`）——一定会在生产路径上爆。`threading.local()` 只能管住**同 thread 内** set/get，跨 OS thread 就是空的。跨线程要么用进程全局 + 锁 + fallback，要么用 ContextVar + `propagate_context_to_thread()`，要么就**别跨**（agent 主流程调 handler，不要 pool）。
