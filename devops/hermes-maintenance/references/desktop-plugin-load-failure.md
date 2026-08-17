# 桌面端 runtime 插件加载失败排查（completion-sound 缺陷，2026-08-12 实测）

上游 issue：https://github.com/NousResearch/hermes-agent/issues/83918（open，未修）
本机补充证据：issuecomment-5274984230

## 症状

desktop.log（`$LOCALAPPDATA/hermes/logs/desktop.log`，注意无时间戳——用文件 mtime + 错误行号位置判断新旧）：

```
[hermes] [renderer console:main] [plugins] runtime load failed (ops-panel) SyntaxError: Unexpected token ']' (file:///C:/Users/HMSJ/AppData/Local/hermes/hermes-agent/apps/desktop/release/win-unpacked/resources/app.asar/dist/assets/completion-sound-BFZKOsFC.js:3)
[hermes] [renderer console:main] [error-boundary:contrib:plugin:channel-sessions:channel-sessions:page-channel-sessions] TypeError: t is not a function
[hermes] [renderer crash:main] ... t is not a function
```

- ops-panel 型：import 阶段失败（SyntaxError 指向 completion-sound）
- channel-sessions 型：加载成功但渲染崩（TypeError，React 堆栈顶部是 `at ChannelSessionsPage (blob:file:///<uuid>:757:23)`——blob 上下文证实插件跑在 rewriteSpecifiers 后的 Blob 模块里）
- 上游 issue 报的是 `Invalid or unexpected token`（不同构建不同 token，行号恒为 :3）

## 30 秒判定

1. `grep "runtime load failed" desktop.log` —— 有 → 桌面端插件加载失败
2. 分清端：桌面端（`desktop-plugins/<id>/plugin.js`）vs 网页端（9120 `/api/dashboard/plugins` 正常 = 网页端 OK）
3. 对照上游 issue #83918 —— 症状一致直接进入「等上游/重启验证」轨道，别在插件代码上浪费时间

## 排查证据链（全绿结论如何得出）

| 检查 | 方法 | 结果（本机） |
|---|---|---|
| chunk 语法 | `node --check <asar.unpacked路径/completion-sound-*.js>` | ✓ 通过（146KB、2 行、rolldown ESM）|
| 依赖完整性 | python 递归提取 `from"./xxx"` import → 逐个查文件存在 | ✓ 70 个直接依赖 / 75 模块递归零缺失 |
| 插件 import | grep 4 个 desktop-plugins 的 import —— 全部仅 `@hermes/plugin-sdk`/`react*` | ✓ 干净，非插件问题 |
| 页面崩溃点 | 崩在 `blob:...:757`（useLangT 的 t 是箭头函数）→ TypeError 是 SDK 组件未就绪的连带症状 | 非 useLangT 问题 |
| 网页端对照 | 9120 加载同款插件正常 | 问题特定于桌面端渲染进程 |
| 模拟容器读取 | python 从 asar offset=0 读 size 字节 → node --check | 报 `Invalid or unexpected token` :1（≠ 实际 :3）→ 排除简单 offset=0 假设 |

结论：磁盘文件全绿 + 上游 issue 症状一致 = 运行时读取缺陷（渲染进程 Blob import 场景对 unpacked chunk 的解析失败，读到非磁盘内容——文件 2 行却报 :3）。

## asar 文件解析（python，避坑版）

asar 头是 pickle 序列化：`[4B:4][4B:size][4B:size-4][4B:size-8][JSON @16]` —— **JSON 在偏移 16，长度 = 偏移 12 处的 uint32 LE**（实测 106824）。

```python
import struct, json
with open(asar_path, 'rb') as f:
    f.seek(16)
    header = json.loads(f.read(jsize_from_offset12).decode('utf-8'))

def walk(node, path=''):
    if 'files' in node:
        for n, sub in node['files'].items():
            yield from walk(sub, f"{path}/{n}")
    else:
        yield path, node
# walk 入口传 header（不是 header['files']——顶层无 'files' 键会整块当文件 yield 1 条）
```

- 文件节点 `{"size","offset"}` = 容器内数据；`{"size","unpacked":true,"integrity"}` = **数据在 `app.asar.unpacked/` 同相对路径，容器内无 offset**
- 找 unpacked 规则：`apps/desktop/package.json` 的 build 段 `asarUnpack`（本机 `["**/*.node","**/prebuilds/**","dist/**"]` → 全 dist 387 文件解包）
- npx `@electron/asar extract-file` 在 Windows 有路径解析坑（ENOENT 找错目录）——优先 python 手解析

## 坑

- **node 正则 exec 循环必须复用同一实例**：`while((m = re().exec(src)))` 每次迭代新建正则 → lastIndex 重置 → 死循环 OOM（本会话实测 node 爆堆）。用 `matchAll` 或实例化一次。
- **MSYS 传 Windows 路径给 node -e 会丢反斜杠**：`require('C:\Users\...')` 变量展开后变 `C:Users...`——写死正斜杠 `C:/Users/...`。
- desktop.log 无时间戳：判断错误新旧 = 文件 mtime + 错误行号是否在尾部（行号接近总行数 = 最近）。
- 桌面会话（含 agent terminal 链）挂在 backend 进程树里（Hermes.exe → serve backend → bash → ...）——排查进程树时 `Get-CimInstance` 按 ParentProcessId 逐层看。

## 处置

- 重启桌面 app（⌘K → Reload desktop plugins 或完全重启）——疑似启动时序问题，重启可能自愈（未证实）
- 临时用 9120 网页端（channel-sessions/ops-panel 网页版功能完整）
- 给上游 issue 补证据（已补：文件合法、依赖齐全、网页端正常、:3 指向读到非磁盘内容）
- 上游修复后：`hermes update` + 重构建桌面 app（`cd apps/desktop && npm run pack`）
