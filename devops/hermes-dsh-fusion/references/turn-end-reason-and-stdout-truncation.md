# 桥判定 P0 洞 + stdout 截断 + zstd 落盘机制（2026-08-19 实测）

> 本文是 hermes-dsh-fusion SKILL §坑 17/18/19 的展开版。三条规则合并写在一个文件，因为它们都从同一个根因——**桥把"DSH 说自己完成"和"DSH 真完成"混淆了**——展开。
>
> 主坑条目在 SKILL.md 里短引述；要落地代码（dsh_bridge.py 行号、状态映射表、续投决策树）查这里。

## §坑 17 · turn/end reason.kind P0 洞

### 现象
今天 r2（产物没落盘被当完成）+ r3（30 秒中断被当完成转述）两个事故，**共同根因**是 `scripts/dsh_bridge.py:451-453` 轮询判定只数"有没有 turn/end 事件"，不解析 `data.reason.kind`。

### DSH 源码确认的 reason.kind 值域
`completed` / `aborted` / `blocked` / `max-tokens` / `error` / `interrupted` / `disposed`

- `aborted` = 回合被主动中断
- `interrupted` = 会话在未收尾回合上被重新加载时系统补写的合成关闭（崩溃/进程被杀后重载）
- `max-tokens` = 输出截断，产物可能缺尾

### 桥三处必改（行号已核实）
1. `dsh_bridge.py:57-60` 状态常量加 `STATUS_INTERRUPTED = "interrupted"`
2. `dsh_bridge.py:451-453` 轮询判定从"数 turn/end 事件"改为解析 `data.reason.kind`，存 `end_kind` 变量
3. `dsh_bridge.py:307-309` BRIDGE_RESULT result dict 加 `turnEndReason` 字段；`format_trace` 和 `_emit` 的 `[状态]` 打印区分档位（"回合中断（reason=aborted/interrupted），产物不可信，走验收 FAIL 路径"）

### 状态映射表

| reason.kind | BRIDGE_RESULT.status | turnEndReason | 验收行为 |
|---|---|---|---|
| completed | done | completed | 走正常验收 gate |
| max-tokens | done | max-tokens | 数产物字数/镜数，截断=FAIL |
| aborted | interrupted | aborted | 走 FAIL 路径，产物不可信 |
| interrupted | interrupted | interrupted | 走 FAIL 路径（崩溃/重载，内存不可知） |
| error | error | error | 已有，重试或查工具权限 |
| blocked | done | blocked | 工具权限问题，**不续投**，排错后再派 |
| 缺失/未知 | done | unknown | 兼容旧事件，正常验收 |

### 续投决策树（叠加在 SKILL §坑 10 之上）

```
reason.kind 是什么？
├─ completed
│  ├─ 产物齐全 → 验收 gate 通过 → close
│  └─ 产物缺 → 同 route 续投「从 X 节继续」（DSH 上下文完好）
├─ aborted
│  ├─ 有部分产物 → 同 route 续投「补全剩余」（DSH 内存上下文还在）
│  └─ 无产物 → 同 route 续投「上一轮被中断，请重新执行任务」（force_new 也可）
├─ interrupted（崩溃/被杀重载）→ force_new=True 开干净新线，别续旧线
│   （崩溃前内存状态不可知，续投=猜上下文，污染风险 > 重做成本）
├─ max-tokens → 同 route 续投 + "上一轮输出被截断，从 X 节继续"
├─ blocked → 排查工具权限/preset 配置，**不续投**
└─ error → 同 route 续投「上一轮报错（reason=error），请重试或换策略」
```

### Hermes 验收 gate 必须独立于 BRIDGE_RESULT

`status=done` 只是触发器——之后**强制独立验产物文件**：

1. 产物文件存在
2. 字节数合理（坌子型22 镜 ≥ 5KB）
3. 内容完整（自查清单逐条 grep 验证）
4. 关键不可删词抽查（如「水光反衬/重半分/下颌线绷紧」必须出现）
5. 锁定项逐条核对（坌子三处拍板一字不差）

即使 `turnEndReason=completed` 也要独立验——**桥只负责"DSH 说自己完成"，产物对不对是 Hermes 的责任**。

---

## §坑 18 · DSH 长回答 stdout 截断规律

### 现象
桥返回的实时 stdout（DSH 在 turn 内的文本输出）在 Hermes 侧**稳定截到 1500-1700 字节**：

| 任务 | stdout_bytes_captured |
|---|---|
| mowang-polish-r2（DSH 跑了 183s） | ~3000+（多回合累计） |
| mowang-workflow-design 第 1 轮 | 1719 |
| mowang-workflow-design 第 2 轮 | 1488 |
| mowang-workflow-design 第 3 轮 | 2588 |
| mowang-workflow-design 第 4 轮（落盘成功） | 1488 |

> 单回合内 DSH 输出如果超过 ~1.5KB，Hermes 收到的 stdout 就会从中间切断——`stdout_bytes_omitted: 0` 说明不是有意 omit，是 stdout buffer 在 stdout_bytes_captured 阈值就被截了。

### 直接后果
**桥的 stdout ≠ DSH 完整产物**——只能当"过程"线索，不能当"答案"交付。

### 硬约束：何时必须强制落盘

满足以下**任一条件**就必须在任务书里写硬约束「必须调 write_file 把答案写到磁盘」：

- DSH 任务书回答预计 > 1500 字节（典型：5 节方案 / 长代码段 / 完整提示词成品 / 详细技术分析）
- 任务是"DSH 给方案/成品/答案"而非"DSH 改文件"（改文件任务产物在磁盘，不走 stdout）
- 用户明确要"看看 DSH 怎么想"（语义层面要拿到完整思考）

### 强制落盘姿势

**任务书末尾**必须写：

```markdown
**这次任务的硬约束**：必须调 write_file / create_file 工具把答案写到磁盘，
不能只在对话里说。

**文件路径**：`C:/.../目标文件.md`

**写完后再在对话里回报**：
- 文件路径 + 字节数（DSH 自带 Test-Path / Get-Item 验证）
- 内容要点回顾（前 N 条关键结论）
- 最终 JSON 摘要（changes/verification/leftovers 必须 message 字段非空）
```

DSH 收到后**必须真的调工具**，写完才允许结束 turn。

### 栈选择（产物文件路径）

| 场景 | 推荐路径 | 理由 |
|---|---|---|
| DSH 给方案/答案（不进 Vault） | `Temp/<任务线>_<日期>.md` | Hindsight 不入库，不污染 Vault |
| 坌子型润色任务（项目资产） | `<项目>/.dsh_polish/日期-场次.md` | 任务产出归属项目，坌子可直接打开 |
| DSH 维护 skill | skill 文件本身 | 唯一例外，按 SKILL §"Skill 共享与写权限纪律" |

**绝对避免** cwd 锚到 `skills/hermes-agent` 安装目录——沙箱写范围会把产物塞进系统资产目录。

### 接收侧：Hermes 怎么读

物理文件落盘后，Hermes 用 `read_file` 读——不走 stdout、不依赖 session.history API、不依赖 zstd。

```python
read_file(path="C:/Users/HMSJ/AppData/Local/Temp/mowang_workflow_ans.md")
```

全文拿到，无截断。

### 失败兜底

如果 DSH 写完报告"已落盘"但 read_file 拿不到：

1. 用 `terminal` 直接 `ls -la <路径>` 验证文件存在
2. 文件存在但字节数对不上 → 任务书再加约束"再写一遍确认"
3. 文件不存在 → DSH 没真调 write_file，**强约束下次任务书**

---

## §坑 19 · zstd 落盘机制——不能用字节数判 DSH 干活没

### DSH 源码确认的事实

DSH session 持久化是事件日志，append 走软 flush——**只有 turn/end（回合结束）+ 会话销毁才是强制 commit 点**。`session-projection-cache` 源码注释原话：mandatory write points = turn/end and session disposal。

**回合进行中的事件只缓存在内存视图**（`session.history` API 能实时读到），磁盘 `session.jsonl.zstd` 只有上次 commit 的内容 + header frame。

### 实测数据

| sessionId | DSH 干了什么 | zstd 压缩前 | zstd 解压后 |
|---|---|---|---|
| hermes-cfc1fd84 | 11 步推理（mowang-polish-r2） | 430541B | 167B（= session 头） |
| hermes-fc62c28f | 11+ 步推理 + 4 轮续投（workflow design） | 430541B | 167B |
| hermes-3cc13249 | turn 30s 被 abort | ~200B | 167B |

**430KB 压成 167B**——DSH zstd stream 用了高重复 dictionary 编码，**不是 bug，是设计**。

### 直接后果

1. **不能看 zstd 字节数判 DSH 干活没**——今天我因此断言"DSH 落盘模块坏了"被打回（用户纠正："我打断了"）
2. **`session.history` 在回合进行中也可能 events=0**——未 commit 不进 history 列表，**不是 RPC 接口坏了**
3. **判断 DSH 真活干了 = 看桥轨迹里的 `📥 任务:` 行**（user/message 进内存视图了）+ `tool/call` 事件序列
4. **等 DSH 干完一个完整 turn**，turn/end 触发 commit，**这时** zstd 才会有完整事件流

### 误判清单（千万别再说这些话）

- ❌ "zstd 只有 167B，DSH 落盘坏了"
- ❌ "session.history events=0，DSH 没干活 / RPC 接口坏了"
- ❌ "bridge status=done 但 zstd 没内容，DSH 没真完成"
- ❌ "DSH 整个 ~/.dsh/sessions/ 都只 1 行，持久化层挂了"

**正确说法**：

- ✅ "DSH 回合进行中，zstd 还没到强制 commit 点，等 turn/end"
- ✅ "判断 DSH 真干活 = 桥轨迹里的 user/message + tool/call 序列"
- ✅ "验收 gate 必须独立验产物文件存在 + 字节数 + 内容完整，不靠桥返回"

### 何时 zstd 才有完整数据

```python
import zstandard as zstd
# 等 DSH 完整 turn 结束（bridge 收到 turn/end 事件 + reason.kind=completed）
# 然后查 zstd：
with open('~/.dsh/sessions/<ws>/<sid>/session.jsonl.zstd', 'rb') as f:
    raw = zstd.ZstdDecompressor().decompress(f.read(), max_output_size=200*1024*1024)
# 此时 raw 应包含完整 NDJSON 事件流
```

但**通常不需要走 zstd 路径**——直接 `session.history` RPC（commit 后事件已落 history）更干净。除非要 dump 完整事件流做离线分析。

---

## 三条坑的共同根因（治理思路）

坑 17/18/19 是同一棵树的三个症状——**桥把"DSH 说自己完成"当成了"DSH 真完成"**：

- 坑 17 = 桥不读 reason.kind ＝ 信任 DSH 的 done 不看完成质量
- 坑 18 = stdout 截断 ＝ 信任 DSH 的对话输出当最终交付
- 坑 19 = zstd 字节数误导 ＝ 信任磁盘内容当会话真实状态

**治理原则**（记到 SKILL 主干 §"验收与归位"附近）：

> **Hermes 是验收者，不是转述者**。BRIDGE_RESULT 是 DSH 的"自评"，不是 Hermes 给用户的"交付"。任何 DSH 任务的最终交付**必须独立验产物文件**——存在性 + 字节数 + 内容完整性 + 锁定项 + 不可删词。Bridge 只决定"要不要触发验收"，不决定"产物对不对"。

### 给后续 task 模板的修正

原 SKILL 任务模板结尾要求 DSH 输出 `{changes, verification, leftovers}` JSON 行——**这条不变**。但加一条：

```markdown
【交付】产物落盘文件路径必须回报进 summary.changes，Hermes 验收时核对文件存在 + 字节数 + 内容。
【不允许】只用对话回复交付内容（stdout 会被截断，Hermes 拿不到完整答案）。
```

---

### 验收记录（本会话踩过的）

| 任务 | 第一次失败 | 第二次成功 | 关键修复 |
|---|---|---|---|
| mowang-polish-r2（润色） | stdout 给前 7 镜，22 镜后续丢；Hermes 没落盘 | （未走坑 18） | 必须落盘 |
| mowang-workflow-design 第 1-3 轮 | stdout 截断在第 1 节中段 | 第 4 轮：DSH 写文件 + 自验证字节数 | 坑 18 强制落盘姿势 |
| 落地 turn/end reason.kind | 没注意到 aborted 被当 done | DSH 自查源码 + 列行号 + 状态映射 | 坑 17 桥改法 |
| 验证 zstd 不是 bug | 误判"DSH 落盘坏了"被打回 | DSH 答：mandatory write points = turn/end + 销毁 | 坑 19 机制事实 |

---

## §坑 17 修复落地记录（2026-08-19 PM）

### 实际打的补丁（dsh_bridge.py 已落盘）

- **第 61-83 行**：新增 4 个常量 `STATUS_MAX_TOKENS` / `STATUS_INTERRUPTED` / `STATUS_ABORTED` / `STATUS_BLOCKED` + `_TURN_END_KIND_TO_STATUS` 映射表 + `_turn_end_kind()` 提取函数（从 `data.reason.kind` 安全取 kind，缺失/非字符串返 None）
- **第 253-261 行**：`format_trace` 的 turn/end 分支从 `d.get("stopReason", d.get("reason", ""))` 改为走真实 schema `data.reason.kind`（`reason.get("kind") if isinstance(reason, dict) else None`），旧 `stopReason` 保留兼容
- **第 481-494 行**：轮询循环里取 `end_kind = _turn_end_kind(e)`，break 条件从"见到 turn/end 就算成功"改为"`end_kind is not None or 见到 turn/end`"——reason 缺失也按 error 兜底
- **第 532-534 行**：`completed` 分支按 `_TURN_END_KIND_TO_STATUS.get(end_kind, STATUS_ERROR)` 映射状态，传 `turn_end_reason=end_kind`
- **第 349-379 行**：`_finish` 加 `turn_end_reason=None` 参数，日志 dict 也带字段
- **第 320-364 行**：`_emit` 加 `turn_end_reason` 参数，4 个新状态（max_tokens/interrupted/aborted/blocked）各补一行人读文案，BRIDGE_RESULT 增加 `turnEndReason` 字段

### 实测验证（修后跑一单轻量任务）

```
任务：只回 'pong' 一个词，别调任何工具
route：verify-p0-fix
结果：
  💬 pong
  ── 回合结束 (reason.kind=completed) ──
  [状态] 完成
  [turnEndReason] completed
  BRIDGE_RESULT {"status": "done", ..., "turnEndReason": "completed"}
```

**链路验证**：`reason.kind=completed` → `[状态] 完成` → `[turnEndReason] completed` → BRIDGE_RESULT 带字段。三处都有数据。

**未实测分支**：`aborted` / `interrupted` / `blocked` / `max_tokens` 四个状态需要 DSH 真正触发这些 turn/end 才能验——mock 注入事件是最稳妥的覆盖测试路径（参见下方验证脚本）。

### 验证脚本（`scripts/verify-turn-end-reason.py`）

不动桥代码，单测式验证映射完整性。覆盖 6 个 kind 值（含 `disposed`）和缺失/非字符串 reason 的兜底分支。Python 单元测试，无外部依赖。

```python
# 用法：python scripts/verify-turn-end-reason.py
# 退出码 0 = 全过；1 = 有失败
```

---

## §机制层卫生——DSH 任务不要绑定业务上下文（2026-08-19 PM 教训）

### 现象

本会话后续有一次「问问 DSH 怎么优化工作流程」的任务——**目标是通用 Hermes-DSH 协作机制**，但任务书里写满了坌子/叶子/魔王/伏妖记/十二硬规则/三处拍板等业务上下文。结果：

- 第一版方案文件全文坌子，DSH 把方案写成坌子场景特化版，机制层被业务污染
- 坌子/叶子根本不是本任务的当事人（管理员才是），引入业务上下文反而偏离目标
- 后续用户纠正"打通 hermes / DSH，和特定某个人没关系"——机制层必须脱离业务场景

### 教训（机制层铁律）

**派 DSH 的任务分两类**：

| 类型 | 范围 | 任务书应该怎么写 |
|---|---|---|
| 机制层（治理/流程/契约/P0 洞） | 通用、可跨任务复用 | **业务上下文 = 0**。任何"针对 X 场景的优化"都拒绝写入机制层 |
| 业务层（坌子润色 / 伏妖记审读 / 项目特定任务） | 项目专属 | 业务上下文全量注入（角色/场景/规则/拍板/不可删词清单） |

**判别口诀**：问「这是『机制怎么设计』还是『这个项目怎么拍』？」——前者业务清零，后者业务全量。

**反模式**：

- ❌ 任务书首段说"坌子魔王剧本有一场戏，坌子打回画面太干"——业务上下文把机制层任务污染成场景特化
- ❌ 任务书带"坌子 12 条硬规则"——除非机制层任务本来就要定义"硬规则区怎么写"，否则这些是坌子的偏好不是机制
- ✅ 任务书只说"DSH/Hermes 协作链路机制方案"——纯机制层，零业务上下文

---

## §预支结论陷阱——不要凭观察推"X 坏了"（2026-08-19 PM 再次踩坑）

### 现象

本会话曾断言 **"DSH 整个 ~/.dsh/sessions/ 都只 1 行，持久化层挂了"**——基于压缩前 430KB / 解压后 167B 的"压得太狠"观察。被打回后让 DSH 自查源码，**DSH 答：mandatory write points = turn/end + 会话销毁，这是设计不是 bug**。

### 教训

**判断 X 是否坏的三段式纪律**：

1. 观察事实（看 zstd 字节数 / 看 stdout / 看 log）— **这不是结论**
2. **机制事实核查**：让 X 自己答 / 查源码 / 查官方文档 / 让 X 跑测试
3. **基于机制事实下结论**——否则不下结论

### 反模式

- ❌ "zstd 只有 167B → 落盘坏了"（跳过步骤 2，凭压缩比推断）
- ❌ "session.history events=0 → RPC 接口坏了"（同上，commit未 commit）
- ❌ "stdout 只 1500B → 输出被吃了"（事实对但原因错——stdout 截断不是 DSH 输出问题，是 Hermes 接收侧问题）
- ❌ "bridge status=done 但产物没动 → DSH 撒谎"（跳过 2，DSH 可能真在做但产物在 stdout 被截）

### 正确姿势

观察 → "我看到 X" → "我**怀疑** Y，验证方法 Z" → 让 Z 跑出结果 → 结论

**没有验证的"X 坏了"不算结论**——只算猜测。猜测说出口 = 自找打回 + 把错误观察固化进 skill。