# turn/end reason.kind + stdout 截断 + zstd 落盘机制（2026-08-19 已修复版）

> 本文是 hermes-dsh-fusion SKILL §坑 17/18/19 的展开版。三条规则合并在一个文件，因为它们都从同一个根因——**桥把"DSH 说自己完成"和"DSH 真完成"混淆了**——展开。
>
> 主坑条目在 SKILL.md 里短引述；要落地代码（状态映射表、续投决策树）查这里，**以本文件 + SKILL §17 为权威**，代码 `_TURN_END_KIND_TO_STATUS` 是单一事实来源（DB 真源）。
>
> 旧版本（修复前草案）已废弃——本文件**对齐 2026-08-19 DSH 视角审查的发现**：旧版 `blocked→done` / `缺失→done` / `aborted 有产物就续投` 是错的，会导致 P0 复发。

---

## §坑 17 · turn/end reason.kind P0 洞（**已修复**）

### 现象（修复前）

今天 r2（产物没落盘被当完成）+ r3（30 秒中断被当完成转述）两个事故，**共同根因**是 `scripts/dsh_bridge.py` 轮询判定只数"有没有 turn/end 事件"，不解析 `data.reason.kind`——`aborted` / `interrupted` / `max-tokens` / `error` 也被报 done。

### DSH 源码确认的 reason.kind 值域

`completed` / `aborted` / `blocked` / `max-tokens` / `error` / `interrupted`

（`disposed` 是会话级销毁事件，不进 turn/end，本节不涉及。）

| kind | 含义 |
|---|---|
| `completed` | 正常完成 |
| `aborted` | 回合被主动中断（含 user / parent / hook / legacy 等取消来源）|
| `interrupted` | 崩溃/进程被杀后重载的合成关闭 |
| `max-tokens` | 输出达到 token 上限，产物可能缺尾 |
| `error` | 回合失败（payload 含 LlmFailure: code + status）|
| `blocked` | 回合被阻断（工具权限等）|

### 修复后状态映射表（**唯一权威**——代码 `_TURN_END_KIND_TO_STATUS` 是 DB 真源）

| reason.kind | BRIDGE_RESULT.status | turnEndReason | 验收行为 |
|---|---|---|---|
| `completed` | `done` | `completed` | 走正常验收 gate |
| `max-tokens` | `max_tokens` | `max-tokens` | 数产物字数/镜数，截断=FAIL |
| `aborted` | `aborted` | `aborted` | **不自动重试**——可能是有意中止，等人工确认 |
| `interrupted` | `interrupted` | `interrupted` | 续投一次失败则 `force_new` 开干净新线（崩溃前内存状态不可知）|
| `error` | `error` | `error` | 瞬时类重试，结构性错误上报 |
| `blocked` | `blocked` | `blocked` | 排查工具权限/preset，**不续投** |
| 缺失/未知 | `error` | `error` | 兜底，事件不可信按最坏处理 |
| 无 turn/end | `timeout` | （字段不存在）| 会话保留可续，**不带 turnEndReason** |

**重要**：旧版本（草案）写的 `blocked→done` / `缺失→done` / `aborted 有产物就续投` 是错的——执行者照旧版走会复发 P0。

### 修复后桥改法（实际代码行号）

```python
# scripts/dsh_bridge.py 第 61-65 行：状态常量
STATUS_MAX_TOKENS = "max_tokens"
STATUS_INTERRUPTED = "interrupted"
STATUS_ABORTED = "aborted"
STATUS_BLOCKED = "blocked"

# 第 69-76 行：映射表
_TURN_END_KIND_TO_STATUS = {
    "completed": STATUS_DONE,
    "max-tokens": STATUS_MAX_TOKENS,
    "interrupted": STATUS_INTERRUPTED,
    "aborted": STATUS_ABORTED,
    "blocked": STATUS_BLOCKED,
    "error": STATUS_ERROR,
}

# 第 79-87 行：reason.kind 提取
def _turn_end_kind(event):
    """从 turn/end 事件 data.reason 里取 kind；缺失/非字符串返回 None。"""
    try:
        d = event["event"]["data"]
        reason = d.get("reason") or {}
        kind = reason.get("kind")
        return kind if isinstance(kind, str) else None
    except Exception:
        return None

# 第 501-512 行：轮询判定
# 取首个 turn/end 的 kind，break；缺 kind 也置 completed（由映射兜底）
# 第 549-553 行：收尾分支按 end_kind 映射状态
# 第 365-389 行：_finish 接 turn_end_reason 透传到日志和 BRIDGE_RESULT
```

**注意**：文档不写死行号——行号会随代码改动漂移（DSH 审查发现的 minor S2）。以函数/变量名为锚。

### 修复后续投决策树

```
reason.kind 是什么？
├─ completed
│  ├─ 产物齐全 → 验收 gate 通过 → close
│  └─ 产物缺 → 同 route 续投「从 X 节继续」
├─ interrupted（崩溃/被杀重载）
│  ├─ 续投一次 → 失败 → force_new=True 开干净新线
│  └─ 续投一次 → 成功 → 同上 completed 分支
├─ aborted → 不自动重试，等人工确认
├─ max_tokens → 同 route 续投「从 X 节继续」（产物可能部分可用）
├─ blocked → 排查工具权限/preset，**不续投**
├─ error → 瞬时类（网络/busy）自动重试同 route；结构性错误上报
└─ 缺失/未知 → 不续投（按最坏情况）
```

**重要**：旧版写的 `aborted 有部分产物 → 同 route 续投补全` 是错的——`aborted` 含 user 取消来源，无条件续投会让用户取消被吞。

### Hermes 验收 gate 必须独立于 BRIDGE_RESULT

`status=done` 只是触发器——之后**强制独立验产物文件**：

1. 产物文件存在
2. 字节数合理（坌子型22 镜 ≥ 5KB）
3. 内容完整（自查清单逐条 grep 验证）
4. 关键不可删词抽查（如「水光反衬/重半分/下颌线绷紧」必须出现）

**`turnEndReason` 非 completed 时直接判 verified_failed**——即使产物文件存在也不当交付物，可抢救到 `partial/`目录保留。

**当前状态**（2026-08-19）：验收 gate 是 skill 文本规则，**Hermes 端无消费代码**——落地靠 LLM 每次读 skill 执行，非程序化保证。后续工作要做 `scripts/verify_bridge_result.py` 或桌面插件钩子程序化实现。

---

## §坑 18 · DSH 长回答 stdout 截断规律

桥返回的实时 stdout（DSH 在 turn 内的文本输出）在 Hermes 侧**稳定截到 1500-1700 字节**（`stdout_bytes_captured: 1488/1719/2588` 三次实测），DSH 长回答的后半段全丢。**桥的 stdout ≠ DSH 完整产物**——只能当"过程"线索，不能当"答案"交付。

### 硬约束（何时必须强制落盘）

- DSH 任务书回答预计 > 1500 字节（典型：5 节方案 / 长代码段 / 完整提示词成品）

### 解决姿势

**强制 DSH 调 write_file 工具写到指定路径**——任务书里明确写"完成后必须调 write_file 落盘 `Temp/xxx.md`，对话里可重复摘要但全文必须在文件里"。

落盘验证三件套：
1. 路径存在 + 可读
2. 字节数 ≥ 契约下限
3. sentinel 清单 grep 命中（关键字符串）

---

## §坑 19 · zstd 落盘机制——不能用字节数判 DSH 干活没

DSH session 持久化是事件日志，append 走软 flush——**只有 turn/end（回合结束）+ 会话销毁才是强制 commit 点**（`session-projection-cache` 源码注释：mandatory write points = turn/end and session disposal）。回合进行中的事件**只缓存在内存视图**（`session.history` API 能实时读到），磁盘 `session.jsonl.zstd` 只有上次 commit 的内容 + header frame。

**判据禁用 zstd 字节数**——167B 是正常强制落盘点。**改用物理文件三件套**（§18 末尾）。

### `turnEndReason` 不出现的可能原因

- 还在 turn 进行中（zstd 只有 167B，正常）
- turn/end reason 字段缺失（事件不可信，桥兜底 error）
- 桥旧版本（修复前）——升级 Hermes 到最新 bridge

---

## 单测覆盖（程序化保证）

**两层测试**（**只测纯函数不够**——DSH 审查 M1 critical 实测教训）：

1. **`scripts/test_dsh_bridge_p0.py`（18 项纯函数断言）**：
   - `_turn_end_kind` 提取 10 用例（含 reason 缺失/非 dict/kind 缺失/非字符串 4 个边界）
   - `_TURN_END_KIND_TO_STATUS` 映射 8 断言（含 unknown/None 走 error 兜底）
   - 6 个状态常量存在性
   - **不够**：只测纯函数，P0修的核心行为（轮询判定 + 收尾分支）完全没被测——回退代码测试照样全绿

2. **`scripts/test_dsh_bridge_p0_e2e.py`（7 项端到端轮询单测）**——`test_dsh_bridge_p0.py` 的姐妹文件，必须同时跑：
   - S1 aborted → `status=aborted` + `turnEndReason=aborted`
   - S2 completed → `status=done` + `turnEndReason=completed`
   - S3 无 turn/end → `status=timeout` + 无 `turnEndReason` 字段
   - S4 多 turn/end 取首个 kind
   - S5 防回归断言（常量 + 映射表 + 函数齐全）
   - S6 interrupted → `status=interrupted` + `turnEndReason=interrupted`
   - S7 旧实现反证：旧逻辑 aborted→status=done（错）——证明测试能抓回归

   **跑法**：`python scripts/test_dsh_bridge_p0_e2e.py`（退出码 0 = 全过）。**跑这个脚本就是 M1 critical 的真正闭合证明**。

**端到端测试的关键技巧**（2026-08-19 实测，坑 4 个）：

1. **monkeypatch 必须改 `br.__dict__['rpc']`，不能改 `br.rpc`**——`run_task` 内部是裸调 `rpc(...)`，走 module global namespace；改 attribute 不会触发裸调用。`assert br.__dict__['rpc'] is fake_rpc` 硬保证 monkeypatch 生效。

2. **stateful fake 不依赖队列深度**——run_task 轮询 `session.history` 的次数不确定，队列 pop 模式会在第 5+ 次调用返回空事件流导致假 timeout。改用 `hist_call_count = [0]` 状态计数：第 1 次返回空（base_evs，让 `last_seq=0`），第 2+ 次返回带 turn/end 的事件流。

3. **`base_evs` 必须返回空 events**——`run_task` 第 481 行 `last_seq = max(seq in base_evs)`，如果 base_evs 含带 seq=N 的 turn/end，后续 `cur_new = [e for e in evs if seq > N]` 永远过滤掉 turn/end → 永久 timeout。

4. **DSH RPC 真实 schema（fake 必须返回解包后形态）**——`workspace.create` 返回 `val["workspace"]["workspaceId"]`（嵌套一层）；`session.history` 返回 `val["events"]`；`session.create` 返回 `val["sessionId"]`。**不要包 result 包装**——桥代码里的 `rpc(...).["xxx"]` 是直接索引，fake 返回 `{"result": {...}}` 会让 `["xxx"]` 抛 KeyError。

5. **`run_task` 不返回值**——所有信息走 stdout 末尾的 `BRIDGE_RESULT {json}` 行。测试用 `contextlib.redirect_stdout(buf)` + `buf.getvalue()` 取 BRIDGE_RESULT JSON。

**升级验证纪律**（DSH schema 变化后跑这套端到端测试）：

DSH schema `TurnEndReasonMap` 是 merge-extensible（types.ts 注释：plugins extend it by merging variants）——升级 DSH 后可能加新 kind。桥 `.get(end_kind, STATUS_ERROR)` 对未知 kind 兜底 error 是**安全方向**（宁报错不假 done）。

**风险**：若改 kind 命名（如 `max-tokens → maxTokens`）会静默 error。**DSH 升级后必须跑**：
1. `python scripts/test_dsh_bridge_p0.py` 退出码 0（纯函数）
2. `python scripts/test_dsh_bridge_p0_e2e.py` 退出码 0（端到端）
3. 派一单 hello 级任务，看 BRIDGE_RESULT 末尾 JSON 含 `turnEndReason=completed`



---

## §坑 20 · F3 turnEndError 细分透传（2026-08-19 落地）

**为什么需要**：§17 决策树要求 `error` 状态区分"瞬时"（重试）和"结构性"（上报）——但 DSH `reason.error` 携带 `code`（`RATE_LIMIT` / `AUTH_FAILED` / `NO_ADAPTER` 等 LlmFailure 共享分类法）和 `status`（HTTP 状态码）。**旧实现把这些都丢了**——`error` 字符串一刀切，验收端无法决断。

**桥改法**（`scripts/dsh_bridge.py`，F3 修复）：

- `_turn_end_error(event)`：从 `data.reason.error` 提取 `code`（str）/ `status`（int）/ `retryable`（bool），缺失字段跳过
- `run_task` 轮询：`end_error` 与 `end_kind` 同步提取（取首个 turn/end）
- `_finish/_emit`：加 `turn_end_error` 参数 + 透传到 BRIDGE_RESULT（仅 error 状态有值）
- _emit `status == STATUS_ERROR` 分支人读文案：`回合失败（reason.kind=error, code={code}）` —— code 可读

**BRIDGE_RESULT 新增字段**：`turnEndError`（仅 reason.kind=error 且事件含 error 字段时存在）

```python
# 验收端用法
br = json.loads(stdout['BRIDGE_RESULT {...}'])
if br.get('turnEndError', {}).get('retryable'):
    retry()  # 瞬时错（rate_limit / busy / network）
else:
    raise PermanentError(br['turnEndError'])  # 结构性错（auth_failed / no_adapter）
```

**实测**：`reason.kind=error + error.code=RATE_LIMIT + status=429 + retryable=true` →
```
BRIDGE_RESULT {..., "turnEndReason": "error",
                     "turnEndError": {"code": "RATE_LIMIT", "status": 429, "retryable": true}}
```

---

## §坑 21 · Hermes 端验收 gate = verify_bridge_result.py（2026-08-19 落地）

**为什么需要**：§17 验收契约（"Hermes 端验收 gate 必须独立于 BRIDGE_RESULT"）原本只是 skill 文本规则，靠 LLM 每次读 skill 行为执行——**非程序化保证**。**verify_bridge_result.py** 把这套规则沉淀为可执行脚本 + 11 项单测。

**三状态机**（最重要的设计——不是两态）：

| 状态 | 触发条件 | 退出码 | 含义 |
|---|---|---|---|
| `verified` | status=done + turnEndReason=completed + 物理文件三件套通过（或未指定 artifact）| 0 | 可交付 |
| `verified_failed` | 任何 errors（status 非 done/timeout / turnEndReason 非 completed / 文件检查失败）| 2 | 抢救到 partial/，不当交付物 |
| **`pending`** | status=timeout **或** 旧产物（无 turnEndReason 字段）**或** DSH 升级未知名 kind + 文件三件套通过 | 3 | **需人工审查**——不直接 fail |

**为什么要有 pending 第三态**：
- `status=timeout` 可能只是 DSH 还在跑或桥轮询到 deadline——**不能直接判 fail**
- 旧产物（修复前生成）没有 `turnEndReason` 字段——**直接 fail 会让历史日志全部失效**——但也不能直接 pass——**人工审查兜底**
- DSH 升级添加新 kind——桥 `.get(unknown, STATUS_ERROR)` 兜底成 error，但**升级保护**要 pending 让人类看一眼

**物理文件三件套**（独立于 BRIDGE_RESULT）：

1. **路径存在**（os.path.getsize 不抛 FileNotFoundError）
2. **字节数 ≥ 契约下限**（`--min-bytes`，未指定则跳过）
3. **sentinel 清单 grep 命中**（`--sentinel` 可多次指定，未指定则跳过）

**turnEndReason 兜底逻辑**（DSH 升级保护）：

```python
KNOWN_REASONS = {"completed", "aborted", "blocked", "error", "max-tokens", "interrupted"}
reason = br.get("turnEndReason")
if reason is None:
    # 旧产物 / 字段缺失 → pending 兜底
elif reason not in KNOWN_REASONS:
    # DSH 升级未知 kind → pending 兜底
elif reason != "completed":
    # 已知但非 completed → verified_failed + 提示抢救到 partial/
```

**用法**：

```bash
# 命令行
python scripts/verify_bridge_result.py '<br_json>' \
    --artifact path/to/product.md \
    --min-bytes 5000 \
    --sentinel '关键内容' \
    --sentinel '另一关键内容' \
    --json

# stdin
echo '{"status":"done","turnEndReason":"completed",...}' \
    | python scripts/verify_bridge_result.py --artifact p.md --json

# 11 项单测
python scripts/test_verify_bridge_result.py  # 退出码 0 = 全过
```

**调用时机**（Hermes 端默认行为）：DSH 任务走桥 `run` 完成后，Hermes 跑 verify_bridge_result.py 验证（如需）。**作为 CLI 工具单独用**——不是桥的一部分，**DSH 不知道**它的存在。

**DSH 升级保护完整套**（§17 / §20 / §21 组合）：

```
DSH 升级后跑：
  1. python scripts/test_dsh_bridge_p0.py          # 纯函数 18 项
  2. python scripts/test_dsh_bridge_p0_e2e.py       # 端到端 7 项
  3. python scripts/test_verify_bridge_result.py   # 验收 gate 11 项
  4. 派一单 hello 级任务，看 BRIDGE_RESULT 末尾 JSON：
     - 含 turnEndReason=completed（§17 新增字段）
     - 若 error 状态含 turnEndError={code,status,retryable}（§20 新增字段）
  5. 跑 verify_bridge_result.py 验证 hello 任务的产物（§21 三状态机）
```

---

## §坑 22 · 单一任务书三层契约（2026-08-19 沉淀）

DSH 任务书要同时表达**三层契约**，Hermes 验证只看这三层：

```
【契约 1】产物层
  - 产物路径（Hermes 注入，不让 DSH 选）
  - 最小字节数（防 DSH 偷懒写半截）
  - sentinel 文本清单（防 DSH 删关键词）

【契约 2】时机层
  - 何时必须重做（status=aborted/interrupted/error/blocked）
  - 何时可以续投（status=timeout + 文件齐）
  - 何时直接交付（status=done + turnEndReason=completed + 文件齐）

【契约 3】守卫层
  - 12 条硬规则（坌子型 / 通用型）逐条不能破
  - 三处拍板 / 锁定项必须保留
  - 知识库招式的"边界句"——什么能引用、什么不能照抄
```

**为什么需要**：单契约（只说"做完"、"完成"、"对"）= DSH 自由发挥空间大 = 容易复发 P0 类事故（删词、超界、误解）。三层契约 = 静态产物 + 动态时机 + 守卫约束 = 验收可程序化。

**写任务书时落地姿势**（Hermes 装任务文本模板）：

```markdown
【背景】<项目 + 上一版诊断 + 本次只许删 X 不许动 Y>

【任务】<具体任务>

【产物契约】
- 路径：cwd/.hermes_dsh/<route>.md（固定名，DSH 覆盖）
- 最小字节：5000
- 必含 sentinel：["关键内容 A", "关键内容 B"]
- 关键不可删词：["水光反衬", "重半分", "下颌线绷紧"]

【时机契约】
- 续投条件：status=timeout 且文件齐 → pending 人工审
- 重做条件：status=aborted/interrupted → 续投一次失败则 force_new
- 上报条件：status=error 且 sentinel 缺席 → 不重试

【守卫契约】
- 硬规则 12 条（编号）
- 锁定项：[白眯眼 B 路 / 萧耳朵红保留 / 林我爸不补]
- 知识库招式边界：哪条引用 / 哪条不能照抄
```

**Hermes 收到产物后**先跑 `verify_bridge_result.py` 走三状态机——pass 才接产物；fail 直接报错给用户（不静默让 DSH 改）。---

## 文档行号漂移警告

本文档/SKILL.md 不写死 `dsh_bridge.py` 行号——行号会随代码改动漂移（DSH 审查发现的 minor S2）。以函数名（`_turn_end_kind`、`_finish`、`_emit`）和变量名（`STATUS_MAX_TOKENS`、`_TURN_END_KIND_TO_STATUS`）为锚。代码真源以 `dsh_bridge.py` 为准。

---

*最后修订：2026-08-19 DSH 视角审查后重写——对齐 SKILL §17 落地版，修复旧版 P0 复发风险*