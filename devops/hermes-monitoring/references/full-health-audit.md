# Hermes 全景健康度体检（multi-surface audit）

**触发场景**：用户问"检查 Hermes 健康度"/"我的 Hermes 现在怎么样"/"全面体检一下"。**和 Runtime Health Check（被动探测「这个服务活着吗」）不同**——这是**多 surface 并行扫**（进程/端口/cron/凭据/通道/系统/版本），输出**体检报告 + 优先级建议**。

**和 `hermes-maintenance/references/quick-health-check.md` 区别**：那个是修完某具体问题后的 6 步验证清单；这是用户主动问「整体状态」时的全景探针。

## 铁律：先看实际部署状态再下结论

**2026-08-20 用户两次纠正同主题**：排查/体检时**不要凭 commit 历史 / skill 文档 / 记忆推断当前跑什么**——会反复把已撤掉的旧组件当现状推理，全部错。

**第一步必跑**（看清谁在跑再推理）：
```bash
# 实际进程（不靠名字判断——「Hermes_DSH_Inbox_Watcher」名字是历史遗留，看 Task To Run 字段别看名字）
tasklist | grep -iE "python|node"

# 计划任务
schtasks /Query /FO LIST | grep -iE "Hermes_|DSH_"

# 实际监听端口
netstat -ano | grep LISTENING
```

排除法做完才下结论：列出现在跑的所有组件 → 各自做什么 → 哪个可能产生用户看到的行为 → 验证。

---

## 体检九面（按面扫，缺一面就漏一个坑）

### 1. 进程面（不只看 Python）

```bash
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.Name -match 'node.exe|python.exe' } | Select-Object Name,ProcessId,@{n='Cmd';e={[string]\$_.CommandLine}} | ConvertTo-Csv -NoTypeInformation"
```

**坑**：node.exe 数量通常比想象多（dashboard / open-design dev server / memos-console-web dev / DSH web 等），不是每个都该常驻。判断哪些该跑、哪些可收——按场景问用户。

### 2. 端口面（核心服务 + 默认执行引擎）

```bash
netstat -ano | grep LISTENING
```

**必查端口与含义**：

| 端口 | 服务 | 期望 | 体检判读 |
|------|------|------|---------|
| **8644** | gateway webhook 平台 | ON | 离线 = 飞书不通（致命） |
| **8642** | gateway API Server（OpenAI 兼容） | ON | 离线 = 外部 Web 应用无法接入 |
| **9120** | HermesDashboard（web 控制台） | ON | 计划任务 `HermesDashboard` Ready 但 9120 没监听 = 死状态 |
| 9119 | 远程 serve | 按需 | 不是 loopback-only 时强鉴权 |
| **8080** | DSH web（默认执行引擎） | ON | 离线 = DSH 任务全挂；用户日常靠它执行 |
| 9177 | Hindsight 记忆 daemon | ON | 离线 = 记忆写入静默失败 |
| 3000 / 5912/5915 / 7456 | open-design / dashboard dev 等 | 按需 | dev server 长期占内存 |

**⚠️ dashboard 9120 + gateway 8644 双进程纪律**（用户硬要求）：核心库改动后必须**双进程都重启**，只重启 gateway 不生效——dashboard 的进程是独立的 Node 服务，patch 后端不会自动加载。

### 3. Gateway 健康

```bash
curl -s -o /dev/null -w "8644: %{http_code} time=%{time_total}s\n" --max-time 3 http://127.0.0.1:8644/health
curl -s http://127.0.0.1:8644/health   # {"status":"ok","platform":"webhook"}
```

进一步验证飞书重连：grep gateway.log 的 `[Feishu] Connected` 时间戳（应新鲜）。

### 4. Cron 调度器（三个判据叠加）

**不能只看 `jobs.json` 的 last_run_at**——一个 job 跑过 ≠ 调度器健康。三件套：

1. **`cron/ticker_heartbeat` mtime**——cron scheduler 每次 tick 重写，<2 分钟前 = 调度器在跑
2. **`cron/ticker_last_success` mtime**——上次 tick 成功时刻
3. **`cron/jobs.json`**——所有 job enabled、last_run 在合理时间窗内

```bash
ls -lt "$LOCALAPPDATA/hermes/cron/" | head
```

体检判读：
- ticker_heartbeat 超 5 分钟未更新 = cron 死了（gateway 活着但 cron 没跑）
- jobs.json 大量 job `last_run` 都是几天前 = 调度器在跑但触发链断了（手动 run 验证）

### 5. 凭据池

```bash
cd "C:/Users/HMSJ/AppData/Local/hermes"
python -c "
import json
with open('auth.json') as f: a = json.load(f)
for p, entries in a['credential_pool'].items():
    for e in entries:
        print(f'  {p}: {e[\"label\"]} src={e[\"source\"]} status={e.get(\"last_status\")}')
"
```

体检判读：
- 所有 key 都 `source=env:XXX` → 真实 key 在 `$LOCALAPPDATA/hermes/.env`，不在 `~/.hermes/`
- `last_status=null` = 这把 key 还没被用过（不代表坏，但需要一次真实调用验证）
- `last_error_code` 非空 = 短期有失败，看 `last_error_reason` 判断是限流/认证/连接

### 6. 配置关键项

```bash
cd "C:/Users/HMSJ/AppData/Local/hermes"
python -c "
import yaml
with open('config.yaml') as f: c = yaml.safe_load(f)
def gv(d, k):
    cur = d
    for p in k.split('.'):
        cur = cur.get(p, {}) if isinstance(cur, dict) else None
        if cur is None: return '-'
    return cur if not isinstance(cur, (dict, list)) else '<nested>'
for k in ['model.default','memory.provider','tts.provider','stt.provider']:
    print(f'  {k} = {gv(c, k)}')
"
```

体检判读（按用户偏好）：
- `model.default` 是否与单一配置源原则一致（其它端点都指回这里）
- `memory.provider=memos` 配 Hindsight = 应有 daemon 在 9177 监听

### 7. 通道（按用户实际配的平台）

```bash
cat "$LOCALAPPDATA/hermes/channel_directory.json" | python -m json.tool
```

体检判读：每个平台的 DM/group/topic 数量、最近更新时间。

### 8. 系统面

```bash
# 磁盘
df -h C:/Users/HMSJ | tail -2

# .env 大小（异常膨胀 = 配错）
ls -la "$LOCALAPPDATA/hermes/.env"

# skills 数量
ls "$LOCALAPPDATA/hermes/skills" | wc -l

# 版本
cat "$LOCALAPPDATA/hermes/.update_check"
cat "$LOCALAPPDATA/hermes/.update_exit_code"
```

体检判读：
- C: 盘 < 50G 余量 = 提醒用户
- `behind=0` = 已最新；`behind>0` 但 `exit=0` = 上次 update 成功，但 git 落后
- skills > 100 个 = 提醒用户做库审计

### 9. 默认执行引擎（DSH）—— 用户日常靠它跑任务，容易被忽略

**DSH 完全独立于 Hermes**——重启 Hermes 不影响 DSH，反之亦然。但**用户记忆铁律：DSH 是默认执行引擎，必须纳管**。

```bash
# DSH 端口
curl -s -o /dev/null -w "8080: %{http_code} time=%{time_total}s\n" --max-time 8 http://127.0.0.1:8080/

# DSH 计划任务（按用户 8/24 升级流程）
schtasks /Query /FO LIST | grep -iE "DSH_MountOrphans|DSH_Restart" -A 5

# DSH 数据完整性（rc.2 升级后）
head -c 5 ~/.dsh/.credentials.yaml | od -An -c   # 不能是 BOM（357 273 277）
ls -la ~/.dsh/.credentials.yaml
```

体检判读（**8/24 用户拍板的 DSH 升级铁律**）：
- **8080 不在监听 = DSH 没起来**（web UI 跑在 3080 不等于引擎就绪）——这是体检最常漏的项
- **DSH_MountOrphans 状态应该是 `Disabled`**——升级流程第一步就是禁用它（避免挂载孤儿），不在禁用 = 不合规
- **`~/.dsh/.credentials.yaml` 必须无 BOM**（rc.2+ 加了 credential ref 严格正则，BOM/全角字符会让整个 plugin tree 加载失败）
- credentials.yaml 体积 < 500 字节 = 正常；> 500 = 可能有冗余配置

---

## 体检报告输出格式（推荐结构）

```
## 整体状态：🟢 健康 / 🟡 有提示 / 🔴 有故障

## [✅/⚠️/🔴] 核心进程
表格：服务 / 端口 / 状态 / 备注

## [⚠️] DSH（默认执行引擎）
- 进程在跑但 8080 没监听（致命/可忽略？）
- MountOrphans 状态不对
- ...

## ✅ Cron 调度（14 任务全启）
表格：类别 / 任务 / 状态

## ✅ 凭据池（N provider）
- xiaomi (XIAOMI_API_KEY) base=...
- ...

## ✅ 配置 / 通道 / 系统

## 🔧 建议动作（按优先级）
P1 - 最重要
P2 - 次要
P3 - 收尾
```

**关键纪律**：
- **每个 ⚠️ 必须给可执行建议**（不要只说"DSH 没在 8080"——说"跑 `pnpm dsh start` 或查计划任务"）
- **不要罗列无关项**（用户偏好：版本/工具升级汇报只挑高价值 top 2-4，不罗列 changelog）
- **明确哪些服务"按需"**——dashboard 9120 / dev server / open-design 3000 不一定该常驻，问用户

---

## 常见体检发现的真坑（实测）

### DSH 8080 静默离线
**症状**：用户报「DSH 任务失败」→ 体检发现 8080 没监听但 web UI（3080）在线
**根因**：DSH 升级后或重启失误，数据平面（8080）没起但 web UI 还在跑
**修复**：`pnpm dsh start` 或查 `DSH_Restart_V2` 计划任务

### HermesDashboard 计划任务 Ready 但 9120 不监听
**症状**：桌面 app 侧栏会话列表空白/老
**根因**：计划任务因某种原因未拉起，或上次崩溃没自动恢复（HermesDashboard 无 watchdog）
**修复**：`MSYS_NO_PATHCONV=1 schtasks /Run /TN "HermesDashboard"` 看是否起来

### Cron ticker_heartbeat 超时
**症状**：jobs.json 看起来正常（今天全跑过）但实际调度器挂了几小时
**根因**：gateway 进程在但 cron dispatcher 卡了（看 gateway.log 有无 cron 报错）
**修复**：先 `hermes gateway restart`，等下次 tick 验证 ticker_heartbeat 是否恢复

### 凭据池全是 `last_status=null`
**症状**：用户报「飞书发不出消息」
**根因**：key 从未被实际调用过——但 status 字段不验证 key 真假
**修复**：直接跑一次真实调用（lark-cli im send）才能确认 key 有效

### .env 文件 50KB+
**症状**：Hermes 启动变慢 / 配置冲突
**根因**：长期累积旧 key / 旧备份 / 旧注释
**修复**：按 `hermes-backup` 备份后瘦身；保留当前活跃 key + 必要覆盖项即可

### Windows 计划任务指向已归档脚本（DSH_Restart_V2 哑死，2026-09-07 实测）

**症状**：体检发现 DSH 8080 没监听、计划任务 `\DSH_Restart_V2` 状态 `Disabled` / `Last Result: -1`；但 `schtasks /query /fo LIST /v` 显示任务的 "Task To Run" 路径在 `scripts/_archive/...` 归档子目录里。

**根因**：DSH 启动器从 `restart_memos_fix.cmd`（memos 时代）迁移到 `restart_dsh_web.cmd`（harness 时代），但**计划任务注册时复制粘贴了 Task To Run 字段，没同步更新**——脚本物理位置早已搬到 `_archive/memos-hindsight-2026-08-27/`，但任务还在指。Disabled + Last Result -1 = 任务被卡住（找不到脚本路径就拒绝执行），永远自愈不了。

**判别三步**：
```bash
# 1. 任务实际指向
schtasks /query /tn "\DSH_Restart_V2" /fo LIST /v | grep "Task To Run"
# → "C:\Users\HMSJ\Documents\Hermes\scripts\restart_memos_fix.cmd"
# 2. 文件实际位置
find /c/Users/HMSJ/Documents/Hermes/scripts -name "restart_memos_fix*"
# → 出现在 _archive/ 子目录 = 已归档
# 3. 验证新启动器在场
ls /c/Users/HMSJ/Documents/Hermes/scripts/restart_dsh_web.cmd
# → 存在 = 有人搬走了旧脚本但忘了更新计划任务
```

**修复**：
```bash
# 1. 删旧任务
schtasks /delete /tn "\DSH_Restart_V2" /f
# 2. 建新任务指向当前启动器（参考 restart_dsh_web.cmd 内容：等 8080 释放 + tsx 拉 DSH web）
schtasks /create /tn "\DSH_Restart_V2" /tr "C:\Users\HMSJ\Documents\Hermes\scripts\restart_dsh_web.cmd" /sc once /st 00:00 /f
schtasks /run /tn "\DSH_Restart_V2"
# 3. 验证
curl -sS -o /dev/null -w "8080: HTTP %{http_code}\n" -m 5 http://127.0.0.1:8080/
# → 200 = 起来了；node.exe 进程应在 tasklist
```

**教训 / 通用判读**：体检时**计划任务不能只看 Last Result**（-1 也可能是设计性 disabled）；必须把 "Task To Run 路径" + "磁盘 ls 该路径" + "磁盘 ls 当前新启动器" 三件套对账，**任一对不上 = 调度链断**。这套模式适用于所有 Windows 计划任务守护类（DSH_Restart_V2 / DSH_Mux_Listener_Polling / Hermes_Hindsight_Daemon / cua-driver-serve 等）。

### NAS 服务 TCP 通但 HTTP 不响应（empty reply，2026-09-07 实测）

**症状**：NAS 端口（8125 / 8096 / 8420 / 8424）`/dev/tcp` 测试显示端口打开、`bash -c "echo > /dev/tcp/<ip>/<port>"` 返回 0；但 `curl http://<ip>:<port>/` 5 秒后报 `curl: (52) Empty reply from server`、`HTTP 000`。**裸 ping 也可能超时**（CGNAT 或防火墙禁 ICMP）。

**根因**：TCP 端口监听者在（内核 accept 队列没满），但**应用层 HTTP server 没在容器里响应**——常见模式是容器挂了（crashloop / OOM / 健康检查失败被 swarm/k8s 重启中）。TCP 层还活着只是因为 socket 还没被内核回收；HTTP 层已经无人接应答。

**判别三连**：
```bash
# 1. TCP 通（内核层）
timeout 3 bash -c "echo > /dev/tcp/<nas_ip>/<port>" && echo "✅ TCP" || echo "❌ TCP closed"
# 2. HTTP 不应（应用层）
curl -v http://<nas_ip>:<port>/health --max-time 5 2>&1 | grep -E "HTTP|Empty"
# → "Empty reply from server" = 应用挂了
# 3. 真实端点（很多 NAS 后端的 / 是空响应，必须查已知端点）
curl -sS -o /dev/null -w "/health → %{http_code}\n" http://<nas_ip>:<port>/health --max-time 5
# → 404 不一定是坏（健康检查走其他路径），关注 000 / connection refused / empty reply
```

**修复方向**：SSH 登 NAS（`ssh <nas_ip>` + `export PATH=/overlay/upper/usr/bin:$PATH`）→ `docker ps` 看容器状态 → `docker logs <container>` 看 crash 原因 → `docker restart <container>` 或修复 OOM/配置后自愈。**不要凭"TCP 通"判定服务健康**——TCP 通只是「端口没人 bind」的反面，不能证明应用在跑。

**判读口诀**：任何 NAS / 远程端口健康判读都走 `TCP 通? + HTTP 200? + 端点真活?` 三连，缺一不可。本机 NAS 上的 TDB 网关（8420）、飞书 OAuth 服务、各类容器后端都可能撞这模式。

### memory provider 真实端点识别（端点 ≠ 名字，2026-09-07 实测）

**症状**：体检查 `config.yaml` 显示 `memory.provider = openviking`，但 `curl https://api.vikingdb.cn-beijing.volces.com/health` 全 404——让人怀疑 provider 配置错了。**不是配错**，是 `memory.provider` 字段值不可信——历史上切过 provider（Hindsight → MemOS → OV → TDB）的用户，这里常常是历史残留名。

**真相**：每个 memory provider 插件自己声明端点（不一定来自 config.yaml 的字段）。要查**真实端点**得直接读插件源码：

```bash
# 1. 列当前装了哪些 memory provider 插件
ls "$LOCALAPPDATA/hermes/plugins/" | grep memory
# → memory_tencentdb / memory_hindsight / memory_memos / memory_openviking ...
# 2. 读客户端代码找端点
grep -nE "(BASE_URL|base_url|API_BASE|endpoint)\s*=" \
  "$LOCALAPPDATA/hermes/plugins/memory_<当前名>/client.py"
# → http://127.0.0.1:8420 = NAS TDB 网关（不是北京火山 OV）
# 3. 验证
curl -sS -o /dev/null -w "/health → %{http_code}\n" -m 5 \
  -H "X-API-Key: $KEY" -H "X-OpenViking-Account: $ACC" \
  https://api.vikingdb.cn-beijing.volces.com/health
# → 404 是正常的，OV 健康检查走资源查询，不走 /health
```

**教训**：体检时**别把 `memory.provider` 字段值当真理**——它是用户意图配置（"我希望用 X"），不是当前事实（"我实际在跑 X"）。真实端点要从插件源码 + 实际可访问性两端对账。**OpenViking 北京火山端点不提供 /health 端点**，所有 404 别误判为「OV 服务挂了」——直接用插件实际会调用的端点（POST /api/v1/search/search 等）验证。

详细 provider 切换/坑见 `hermes-memory-provider-selection` skill。

---

## 一键体检脚本（参考实现，未直接部署）

完整体检可直接跑 `python ~/AppData/Local/hermes/scripts/health_audit.py`（未实现，按本文件九面实现）。**不建议过度自动化**——用户偏好：检查+提醒型任务必须同时做"自动修"，但**全景体检的目的是发现真坑 + 让人判断优先级**，不是机械跑一遍就完。