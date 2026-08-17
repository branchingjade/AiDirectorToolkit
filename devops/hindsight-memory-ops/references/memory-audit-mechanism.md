# 记忆库画像类审计机制（2026-08-13 建成，已实测）

治理目标：Hindsight 记忆库（bank=hermes）里成员画像类记录（身份/偏好/习惯）是双写冗余 + recall 污染源——正本是 Obsidian `成员画像/*.md`。本机制 = LLM 低频审计 + 脚本机械执行（「机械/智能分工」铁律：判断力活留 LLM）。

## 组件

| 组件 | 位置 | 作用 |
|------|------|------|
| 采集脚本 | `~/AppData/Local/hermes/scripts/memory-audit-scan.py` | 拉全量 → 成员名预筛 → 输出候选（增量直出 stdout / 全量写文件） |
| 删除脚本 | `~/AppData/Local/hermes/scripts/memory-audit-delete.py` | 备份 → psql 删 → 推进审计状态。`--ids "u1,u2"` 或 `--mark-only` |
| 状态文件 | 同目录 `memory-audit-state.json` | `{last_audit_at, full_scan_done, updated_at}` |
| 审计 cron | `2ad7b042825d`（每天 8:30，deliver=local，toolsets=[terminal,file]） | script=scan；LLM 判定 + terminal 调 delete |

## Daemon HTTP API（实测端点）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/v1/default/banks/{bank}/memories/list?limit=&offset=` | **GET** | 列记忆，分页（limit≤200 实测可行）。返回 items[]：id/text/fact_type/date/**metadata.user_name**/tags。排序 mentioned_at DESC。**无时间窗口参数**——要本地按 date 过滤 |
| `/v1/default/banks/{bank}/memories/recall` | POST | recall（body: query/types/budget/max_tokens） |
| `/v1/default/banks/{bank}/memories` | POST | ⚠️ **retain 写入端点**（body 需要 items 字段，传内容=写库）。**别拿它当 list 用**——本会话曾误试，幸好空 items 无害。返回 usage 字段是写入响应特征 |
| `/v1/default/banks/{bank}/memories/{memory_id}` | — | 只有 get；**无单条 delete**（只有 clear_bank_memories 全清）→ 删除必须走 psql |

- 客户端 `hindsight_client.Hindsight`（venv）封装全部端点，但审计脚本用 stdlib urllib 直调 HTTP（无 venv 依赖，cron agent 任何 python 都能跑）

## PG 直连（删除路径）

- **凭据源**：`~/.pg0/instances/hindsight/instance.json`（pg0 实例配置：port/username/password/database/installation_dir）。`~/.hindsight/profiles/hermes.env` **没有** PG 凭据（只有 HINDSIGHT_API_* 键）
- psql.exe：`<installation_dir>/bin/psql.exe`（`~/.pg0/installation/18.1.0/bin/psql.exe`）
- 调用：`subprocess [psql.exe, -h, 127.0.0.1, -p, port, -U, user, -d, db, -tA, -c, sql]` + env PGPASSWORD
- ⚠️ instance.json 的 port 可能漂移（写 5434，实测 5433 监听）——先试 instance.json 值，失败 fallback 5433
- 表 `memory_units`：id uuid / bank_id / fact_type (observation|experience|world) / text / embedding vector(384) / metadata jsonb / tags / created_at / date
- 全库量级：memory_units 6527 行（Document 层仅 101——unit 层远多）

## 预筛设计（踩坑教训）

- **宽特征词预筛是错的**：第一版用 毕业/专业/岁/职业/偏好/习惯/喜欢/不喜欢/要求/风格/身份… → 命中 **1230/6527**（19%）——"要求/喜欢/身份"在项目文本（运维/创作/评论）里泛滥，候选淹没 LLM
- **正确预筛 = 只匹配成员名**（画像类必要不充分条件：画像必然关于某个成员）：命中 335 条（~5%），LLM 终审兜底
- 成员名来源：Obsidian `成员画像/` 目录文件名（排除 _模板/成员画像/历史协作者观察）
- 主用户（妖玉）偏好不在审计范围（归全局 MEMORY/USER，且无成员名不会进候选）——正好天然排除

## 状态推进机制（防漏审）

- **scan 不推进状态，delete 推进**（`last_audit_at=now`）——agent 挂掉时下轮重复输出同一批 → 重复审计幂等无害，不漏审
- **`full_scan_done` 标记**：缺失时强制全量模式（`today.day==1 or not full_scan_done`）——防止首次全量被状态推进跳过（本会话 mark-only 测试差点把存量 335 条候选永久屏蔽，靠此标记兜住）
- 全量模式候选写 `memory-audit-candidates-YYYYMMDD.json`（335 条约 163KB），stdout 只出统计+路径，agent 分批 read_file（每批 ≤80 条）——一次性注入 prompt 会截断
- 每次审计完**必须**调 delete（有删传 --ids，无删 --mark-only）——否则状态不前移、下轮重复审计

## 判定规则（cron prompt 内核）

- **删（画像类）**：成员名 + 属性词（是/毕业于/岁/名字/偏好/习惯/擅长/喜欢/不喜欢/讨厌/要求/性格/审美/文风/职业/身份）描述"成员是谁、喜欢什么、怎么沟通"——持久属性陈述
- **留（项目类）**：成员做的事——创作进展/剧本/分镜/评论/运维修复/gateway 问题/UI 评估/团队分工/文档操作/cron 记录/OAuth 过期。特征：动作/事件，主语是成员但内容是项目
- **模糊→留**（宁留勿误删：漏删=冗余，误删不可逆；正本在画像文件）

## 其他设计决策

- **monitor_script 模式不适配审计**：monitor 的 hash 静默语义是"输出不变才静默"，审计是"有候选才跑"——输出从"有候选"变"无候选"也算变化，必然空跑一次触发。**普通 cron + deliver=local 更干净**（静默存档，脚本报错仍有告警）
- 删除前备份：`Obsidian Vault/_hermes/记忆审计/backup-YYYYMMDD-HHMMSS.json`（id+text+fact_type+created_at 全量），可恢复
- 删除幂等：DELETE WHERE id IN (...)，已删 uuid 报 0 行不影响
- 频次权衡（用户问过"每月会不会影响项目""每天呢"）：删除范围严格限定画像类（项目类永不删）、PG 行级操作与 retain/consolidation 并发无锁冲突、8:30 空闲时段、资源可忽略 → 每天可行。最终每天 + 每月 1 日全量深度兜底

## 验证

- 首次全量：`rm memory-audit-state.json && python memory-audit-scan.py`（应出 mode=full + 候选文件）
- 状态推进：`python memory-audit-delete.py --mark-only` → 状态文件出现 last_audit_at + full_scan_done=true
- 端到端：cronjob action=run 手动触发 → 结果回会话过目 → 确认后自动跑

## 首次执行实录（2026-08-13，已实测闭环）

**结果**：全量 6530 条 → 候选 335 → 删 60（徐学环 30/杨璇 15/魏宁馨 5/全志越叶子苑津铭 7/陈星艳 2/档案映射 1；world 44+observation 16）→ 计数 6530→6470 实锤；备份 `Obsidian Vault/_hermes/记忆审计/backup-20260813-121439.json` 60/60；275 项目类保留；6 条模糊项复核 = **零操作**（夹带画像信息早已在画像文件，8-07 归位时已覆盖——验证了「宁留勿误删」决策正确）。

**cron agent 自修 3 bug（脚本维护要点，人工写脚本时注意）**：
1. **pg0 版本化安装布局**：psql.exe 在 `installation/18.1.0/bin/` 不是 `installation/bin/`——find_psql 要扫 `installation/*/bin/psql.exe` 取最新版本目录
2. **端口兜底时机**：instance.json port（5434）连接被拒时 psql 返回 returncode≠0（不是 Python 异常）——fallback 条件要 `returncode!=0 且 port≠5433` 时重试，不能只 catch Python 异常
3. **psql -tA 输出解析**：DELETE 的输出是命令标签 `DELETE 60` 不是纯数字——`int(stdout)` 会崩（`int('DELETE 60')`），要 `split()[1]` 取末位数字；SELECT 输出才是纯行

**instance.json port 字段分析（决策：不改）**：
- 事实：hindsight 实例写 5434、hindsight-embed-hermes 实例写 5433、实际只有一个 PG 进程监听 5433
- 结论：port 字段是**创建时期望值**，pg0 运行时动态分配实际端口且**不回写文件**——字段本来就不可靠（双实例期望端口还重叠）
- 改的代价：pg0 是权威管理方，下次操作实例可能重写文件；期望值本身不准，手改是「与 pg0 角力」；当前无影响（daemon 不用它、脚本有 fallback）
- 保持：脚本 fallback（先试 instance.json 值 → psql 报错重试 5433）；将来 pg0 重建实例文件会重新生成
