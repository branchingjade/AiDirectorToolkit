---
name: agent-tool-thread-safety
description: Hermes agent tool 跨线程上下文传递——threading.local() 在 tool handler 跑在 DaemonThreadPoolExecutor 时失效的模式 + 进程全局 dict / ContextVar / propagate_context 三种修复方案。Use when agent 调自定义 tool 时报"X not available (not in a X context)"但 set_client/set_context 是同一个进程里的另一个 thread。
category: devops
---

# Agent Tool 跨线程上下文传递

> **来源**：2026-09-01 飞书评论 agent 真实验证。
> Hermes 把 agent 跑在 `loop.run_in_executor(None, agent_runner)`，agent 调 tool 时 tool handler 又被 `DaemonThreadPoolExecutor` 派到**第三个 OS thread**。自定义 tool 用 `threading.local()` 存上下文（lark client / DB session / user identity 等）时，A thread set、B thread 读、C thread handler 用——B 存的东西 C 读不到。

## 何时加载

- agent 调用 tool 时 tool handler 返回 `X not available (not in a X context)` 类错误
- gateway.log / agent.log 看到 `Tool xxx returned error: ...`
- tool 的 `set_X()` 在 `plugins/.../feishu_comment.py` 类似位置被调用，但 tool handler 在另一个 thread 跑
- 同一个 tool 在 reply / creative agent 都报"不可用"，但 set_client 明显调用了
- 排查 Hermes toolset 注册（已 OK）、AIAgent enabled_toolsets（已 OK）、prefill 注入（已 OK）之后还挂——

## 不加载场景

- tool 不接受 set/get 上下文（如 pure function tool）→ 不查本 skill
- tool 用全局变量而不是 threading.local → 跨 thread 本来就 OK → 不查本 skill
- ContextVar-based tool 的 propagate 已坏 → 加载 `hermes-runtime-pitfalls` 排查 propagate_context_to_thread 链路

---

## 根因模型

Hermes agent 的 tool 调用有三层 thread 跨越：

```
main thread (gateway.process_event)
   ↓ asyncio loop.run_in_executor
worker thread A (_run_creative_agent / _run_comment_agent)
   ↓ set_client(client)  ← 在这里 set
   ↓ agent.run_conversation
   ↓ LLM 决定调 tool_name
worker thread B (DaemonThreadPoolExecutor 池里的某个 worker)
   ↓ tool handler _handle_xxx()
   ↓ client = get_client()  ← 在这里读
```

`threading.local()` 是 **per-thread storage**：A 写的东西 B 读不到。

`agent.tool_executor` 已知这个 issue，已实现 `propagate_context_to_thread()` 把 ContextVar 跨线程复制（`agent/tool_executor.py` line 1347/1526）——但**前提是 tool 自己用 ContextVar**，而旧工具普遍用 `threading.local()`，propagate 对它们无效。

---

## 诊断流程

看到 `Tool X returned error: X client not available (not in a X context)` 类报错：

1. **确认是 tool 自己的 set/get 机制**——grep tool 文件找 `set_client` / `get_client` / `_local` / `threading.local()`
2. **确认 handler 在哪个 thread 跑**——加 logger.info(`threading.get_ident()`) 看两次打印
3. **两次不一致** → 跨线程问题 → 走修复流程
4. **两次一致** → 不是跨线程问题 → 查别处（client 实例是否真的 set 了 None、是否 API 鉴权失败等）

**诊断口诀**：
- "X not available (not in a X context)" + tool 内部用了 `_local = threading.local()` = **跨线程** —— 100% 是这个 issue
- "X not available (not in a X context)" + tool 用 ContextVar = 检查 propagate_context_to_thread 调用链
- "X not available" + tool 用全局 = 检查 set_X 是否真的被调用

---

## 修复三选一

### A. 进程全局 dict + fallback（最快，1-2 行 patch）

适合：tool 数量少、调用方单一（同一事件只有一个 in-flight context）。

```python
# tools/feishu_doc_tool.py 改造前
_local = threading.local()

def set_client(client):
    _local.client = client

def get_client():
    return getattr(_local, "client", None)

# 改造后
_local_clients: dict = {}
_local_lock = threading.Lock()


def set_client(client):
    tid = threading.get_ident()
    with _local_lock:
        if client is None:
            _local_clients.pop(tid, None)
        else:
            _local_clients[tid] = client


def get_client():
    tid = threading.get_ident()
    with _local_lock:
        client = _local_clients.get(tid)
    if client is not None:
        return client
    # Fallback: any registered client
    with _local_lock:
        for c in _local_clients.values():
            if c is not None:
                return c
    return None
```

**风险**：fallback 在多 context 同时 in-flight 时会拿到错的 client（极端情况如并发评论事件多用户同时触发）。同事件单 in-flight 是有界的，**生产可用**。

### B. ContextVar（推荐未来方向）

适合：tool 数量多、想真正干净。

```python
# 顶部
from contextvars import ContextVar
_client_var: ContextVar = ContextVar("feishu_doc_client", default=None)


def set_client(client):
    _client_var.set(client)


def get_client():
    return _client_var.get()
```

**额外要求**：`agent.tool_executor` 已实现 `propagate_context_to_thread(target)`（`tools/thread_context.py` line 64）——ContextVar 自动随 `copy_context()` 复制到 worker thread，**handler 能直接读到**。

但 `set_client` 通常在 main/agent_runner 里调，**不在 turn context 里**——所以 ContextVar 也读不到。**真正的修复**是把 set_client 调用搬进 agent 主循环，让它在 turn context 生命周期内：

```python
# agent runner 里 (而不是 tool handler 之外)
with propagate_context_to_thread(_run_tool_call):
    _client_var.set(client)
    result = _run_tool_call(...)
```

### C. 关掉跨线程（最佳但侵入大）

如果 `set_client` 调用方接受同步执行 tool，可以把 `loop.run_in_executor(None, agent_runner, ...)` 改成同步调用——agent 跑在 main thread，set 和 handler 同一 thread。**代价**：阻塞 event loop，不适合有其他事件在等的场景。

---

## Hermes 现状（2026-09-01）

| Tool | 当前 set/get 机制 | 状态 | 修复 |
|---|---|---|---|
| `tools/feishu_doc_tool.py` | `threading.local()` | ✅ 已修（commit `470145c1a`） | 改进程全局 dict |
| `tools/feishu_drive_tool.py` | `threading.local()` | ✅ 已修（同 commit） | 改进程全局 dict |
| 其他 tool | 未审计 | ❓ | 跑一遍 grep `_local = threading.local()` 看 |

**审计命令**：

```bash
grep -rn "_local = threading.local()" ~/AppData/Local/hermes/hermes-agent/tools/
```

每个命中点都需要按 A 或 B 方案修。

---

## Pitfalls（避免重复犯）

- **不要在新 tool 里用 `threading.local()` 存跨线程需要的 context**——必须用 ContextVar + propagate_context
- **不要以为 "tool handler 在 set_client 那个 thread 跑"**——除非你确认 agent runner 是同步调用且不用 DaemonThreadPoolExecutor
- **不要把 set_X 放进 `finally: set_X(None)`**——这是 commit `403b94597`/`470145c1a` 前的错误设计：每次事件结束 set None 会让 in-flight 的 tool handler 拿不到 client。改成 finally 段 set None 必须在 handler **返回之后**（用 `loop.run_in_executor` 的 future.result 之后）
- **不要把"client"用 globals 全局**——多用户/多 tenant 场景会串

---

## 类级教训（值得记入MEMORY）

1. **`threading.local()` 在跨线程工具调用场景下天然失效**——agent runner / DaemonThreadPoolExecutor 是 Hermes 的标准三层 thread 拓扑（main → worker A → worker B），任何一层 set 的 thread-local 都不能跨到下一层。
2. **`agent.tool_executor.propagate_context_to_thread()` 只能传播 ContextVar**——不传播 `threading.local()`。新 tool 设计应该用 ContextVar + propagate，老 tool 改造需要 fallback 机制（dict / globals）。
3. **"X not available" 类报错的诊断顺序**——先看 tool 是 set/get 机制（threading.local / ContextVar / globals）→ 再看 handler 跨 thread 跑到哪个 worker → 再看 propagate 是否生效。

---

## 相关

- 修复 commit：`470145c1a fix(feishu-doc-tool): client lookup fails across DaemonThreadPoolExecutor`
- 诊断案例：见 Obsidian `Hermes运维/2026-08-31_飞书评论创作意图分流修复.md`（L3 层「feishu_doc/drive tool 跨线程 client 查找陷阱」章节）
- MEMORY 铁律：「飞书评论 agent 创作/回复分流铁律」内含「feishu_doc/drive tool 跨线程 client 查找陷阱」实战补充（2026-09-01）
- 关联 skill：`hermes-runtime-pitfalls`（运行时通用排查）