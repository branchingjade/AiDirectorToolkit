# 反向通道 v3「全表 source 缺失」根因诊断（2026-08-20）

> 现场：用户截图飞书出现两条 DSH 提问（hermes-fe1ffa2f、hermes-7956064e），
> Hermes 自首「hermes-7956064e 根本不在注册表里——所以监听器每次都走兜底分支」。
> 经排查：**121 条 session 全表无 source/owner**，整个 v3 反向通道路由机制全部退化成兜底分支。

## 现象

DSH 提问 → `events.mux` 推 `question/requested` → `scripts/dsh_mux_listener.py` 收帧
→ 查 `.hermes/dsh-registry.json` 找 session 的 `source`/`owner` → **字段不存在**
→ 走第 207-215 行兜底分支「无 source → cwd 判定桌面/飞书」→ 桌面场景只留痕不推送 / 飞书场景堆妖玉 DM

截图里两条提问都堆到了妖玉 DM；用户正确指出这是路由问题。

## 根因（三层证据链）

### 1. 监听器路由逻辑（dsh_mux_listener.py:174-215）

```python
def route_and_notify(sid, frame):
    session = find_session(sid)
    source = (session or {}).get("source", "")   # ← 注册表没 source
    owner  = (session or {}).get("owner", "")    # ← 注册表没 owner
    cwd    = (session or {}).get("cwd", "")
    ...
    if source == "feishu" and owner:     # ← 永远不命中
        ...
    if source == "feishu":               # ← 永远不命中
        ...
    if source == "desktop":              # ← 永远不命中
        ...
    # 兜底分支 ← 全部走这里
    if cwd and ("Documents/Hermes" in cwd.replace("\\", "/") or "Obsidian" in cwd):
        ...留痕不推送
    ok = feishu_send(FEISHU_BOT_DM, msg) # ← 堆妖玉 DM
```

### 2. 注册表全表统计（dsh-registry.json 实测）

```
总计 121 条 session
查找 hermes-7956064e: False
查找 hermes-fe1ffa2f: False
拥有 source 字段的 session: 0 条（全表无 source）
拥有 owner 字段的 session: 0 条（全表无 owner）
```

所有 session 都有 `route` 字段（任务的逻辑线 ID），但 `source`/`owner` 是「来源元数据」，
需要桥 CLI 显式传 `--source` `--owner` 才写入。

### 3. 协议层完整支持，但调用方全没传

**dsh_bridge.py 协议层**（设计完整）：
- `_new_entry(cwd, label, route="", source="", owner="")`（行 243-261）—— 接受并按需写入
- `run_task(cwd, task, label, route=None, ..., source="", owner="")`（行 435）—— 透传到 _new_entry
- CLI 参数解析（行 926-931）—— 支持 `--source <value>` `--owner <value>`

**调用方层**（全没传）：
- 桌面 / Web 直发起 → 没走桥 CLI，源字段无来源
- 飞书渠道派活 → 渠道入口没在 `run` 命令后追加 `--source feishu --owner <open_id>`
- DSH web UI 直发起 → 也没触发桥 CLI 注册

## 修复路径（C 已选定——2026-08-20 用户拍板）

### A 最小修复——监听器兜底更聪明 [否]

只动 `dsh_mux_listener.py` 的兜底分支。问题：cwd=Documents/Hermes 时被判定桌面，桌面
只留痕不推送——但用户从飞书看到了，说明判定失效。**用户结论：cwd 不可靠，砍掉 cwd 判定**。

### B 完整修复——所有渠道入口带 source/owner [否]

| 渠道入口 | 调桥时必须追加 | 写入注册表 |
|---|---|---|
| 桌面 / Web 直发起 | `--source desktop` | `source=desktop`，无 owner（妖玉本机） |
| 飞书 channel hub 派活 | `--source feishu --owner <发起人 open_id>` | `source=feishu`，`owner=ou_xxx` |
| Cron 触发 | `--source cron` | `source=cron`（cron 不提问，路由表无此分支） |
| DSH web UI 直发起 | **用户拍板：归 desktop 类，不需要回流** | 不登记 source/owner，走「未登记 → 默认留痕」 |

**用户否定 B 的关键论据**：「DSH web UI 直起的 session 跟 Hermes 桌面端一样，不需要回流飞书」。
→ B 路径全表回填 source 的复杂度没价值。

### C 选定——砍兜底 cwd 判定、默认桌面留痕（commit `2630cfc`）

把兜底分支从「cwd 判定」改成「未登记 session 默认桌面留痕，不推送」：

```python
# 旧（174-215）：
if cwd and ("Documents/Hermes" in cwd.replace("\\", "/") or "Obsidian" in cwd):
    ...留痕
ok = feishu_send(FEISHU_BOT_DM, msg)  # 堆妖玉 DM

# 新：
# 未登记会话（DSH web UI 直起 / 旧会话）→ 默认桌面留痕，不推送
log(f"[路由] 未登记会话 → 默认桌面留痕")
_mark_pending(sid, frame, text, options, target="desktop", source="unknown")
return True
```

**4 case 单测全过**（feishu+owner / feishu / desktop / 未登记），真实 mux 帧实测：
`hermes-84d606e3 (2026-08-20 10:04:36) → [路由] 未登记会话 → 默认桌面留痕` ✅

**遗留上游保险**（未做）：若飞书渠道起的 session 桥忘传 source，应该在 `dsh_bridge.py:934` CLI
入口加硬性 warn（cwd 是飞书相关路径但 source 空时退出报错），不该让监听器靠 cwd 猜。

## 实操清单

1. **看 mux listener 实际日志**（决定走哪条路径的关键证据）：
   ```bash
   tail -50 "$HERMES_HOME/.hermes/dsh-mux-listener.log"
   ```
   重点看两条 hermes-fe1ffa2f / hermes-7956064e 是不是被打了「无 source」标记。

2. **统计全表 source 缺失比**（诊断整体）：
   ```python
   import json
   data = json.load(open(".hermes/dsh-registry.json"))
   sessions = data["sessions"]
   no_source = [s for s in sessions if not s.get("source")]
   print(f"全表 {len(sessions)} 条，无 source: {len(no_source)} 条")
   # 输出 121/121 时 = 路由机制全表退化（本次确认）
   ```

3. **修复后查 zombie listener**（commit 后立即验证）：
   ```powershell
   Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
     Where-Object {$_.CommandLine -like '*dsh_mux_listener*'} |
     Select-Object ProcessId, CreationDate
   ```
   看 CreationDate 是 commit 时间之前（zombie）还是之后（新进程）。zombie 则 `Stop-Process -Id <PID> -Force`。
   详见 `references/dsh-mux-listener-zombie-pitfall.md`。

## 经验教训（写进 SKILL.md 的坑 21）

1. **协议层 ≠ 链路通**：支持参数和实际调用是两件事。注册表里 source 全空就是证据。
2. **全表诊断比单条诊断更准**：只看 hermes-7956064e 一条，会以为「只是这一条没注册」
   → 看到 121/121 才知道是「所有调用方都没传」的全局问题。
3. **兜底分支要带告警**：当前兜底只 `log()` 没告警，121 条全走兜底也没人发现。
   修复时应同时给兜底分支加「高频兜底=异常」告警（飞书推一次「DSH 反向通道疑似
   退化，source 字段全空」到开工群）。
4. **commit 后必查 zombie**：长驻进程不会自动 reload 代码，`--once` + `check_alive()`
   组合只检查进程存在性不看代码版本——commit 后进程 StartTime 早于 commit 时间
   = zombie，行为仍按旧代码走（坑 22）。

## 关联

- SKILL.md 坑 21（v3 全表退化）+ 坑 22（zombie listener）
- `scripts/dsh_mux_listener.py`（监听器本体）
- `scripts/dsh_bridge.py` 行 243-261 / 435 / 926-931（协议层源头）
- `.hermes/dsh-registry.json`（注册表，121 条全表无 source）
- 提交 d997158（反向通道 v3 落地）
- 提交 2630cfc（路径 C：未登记默认留痕，砍 cwd 兜底）
- `references/dsh-mux-listener-zombie-pitfall.md`（zombie 进程问题详解）