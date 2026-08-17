# channel-sessions 评论会话并入平台列表（2026-08-10 实测，用户三轮拍板最终形态）

把飞书文档评论会话（独立 AIAgent + JSON 文件，不进 state.db）并入 Hermes UI 平台列表的完整实现记录。

## 形态铁律（用户三次纠正确立，最终=独立平台）

演进三级，每级都被用户亲测后纠正：

1. **「飞书评论」独立 Tab 被否**：「不是这样，退回上一版，飞书评论放到平台里面即可」——不做独立 UI 面。
2. **合成记录 source=feishu 混入飞书平台列表再被否**：「评论会话独立，和飞书平级」——不并入飞书。
3. **✅ 最终形态 = 独立平台**：合成记录 `source="comment"`（`_COMMENT_SOURCE` 常量，单独定义不复用 `_FEISHU_SOURCE`），前端 `PLATFORM_LABELS.comment = "飞书评论"`——平台筛选栏自动多出「飞书评论」选项，与「飞书」平级、互不混入；列表行平台徽标显示「飞书评论」，类型徽标「评论」。

**教训**：给现有插件加旁路数据源，用户对「放哪」有明确心智——最终要的是**独立平台（平级）**，既不是独立 Tab（UI 面太重）也不是并入现有平台（混在一起）。别在方案 1/2 之间反复横跳，直接问用户平台维度怎么放。

## 背景：为什么需要插件后端直读

评论会话数据在 `Obsidian Vault/_hermes/评论会话/*.json`（含 `archive/` 归档子目录），
**不写 state.db** → 侧边栏「FEISHU」分类（读 list_sessions_rich）永远看不到。
要做成客户端可见，唯一路径是插件后端（plugin_api.py + service.py）直接读 JSON 目录。

## 后端实现（service.py）

### 目录定位

```python
_COMMENT_DIR_FALLBACKS = [
    Path(os.environ.get("HERMES_OBSIDIAN_VAULT", "")) / "_hermes" / "评论会话"
    if os.environ.get("HERMES_OBSIDIAN_VAULT") else None,
    Path.home() / "Documents/KnowledgeBase/Obsidian Vault" / "_hermes" / "评论会话",
    Path.home() / "Documents" / "KnowledgeBase" / "Obsidian Vault" / "_hermes" / "评论会话",
]
# 取首个存在的目录
```

与 `feishu_comment_collab.py` 的 `VAULT_ROOT` 逻辑保持一致（环境变量优先）。

### 合成 session 记录（list_sessions 合并）

```python
def _comment_sessions_as_rows(resolver, names):
    # 遍历 活跃目录 + archive/，每个 comment_*.json 合成一条：
    {
        "id": "comment:" + f.name,          # 前缀标记，get_messages 据此分流
        "source": "comment",                 # 独立平台（_COMMENT_SOURCE），与 feishu 平级——不是混入飞书！
        "user_id": oid, "user_name": 真名, "display_name": 真名,
        "title": "评论 · " + project,
        "chat_type": "comment",
        "message_count": len(msgs),
        "started_at": last_access, "last_activity_at": last_access,
        "archived": 归档标记, "pinned": 0, "is_active": False,
        "is_comment": True,                  # 前端只读防护 + 渲染分流的锚点
    }
# list_sessions 末尾：sessions.extend(_comment_sessions_as_rows(resolver, names))
# 常量：_COMMENT_SOURCE = "comment"（独立定义，不复用 _FEISHU_SOURCE）
```

### get_messages 分流

```python
if session_id.startswith("comment:"):
    file_name = session_id[len("comment:"):]
    data = get_comment_messages(file_name)   # 复用评论 JSON 读取
    return {"session_id": session_id, "messages": data["messages"], "has_more": False}
```

`get_comment_messages` 必须校验文件名（拒绝 `/`、`\` 防目录穿越），
活跃目录与 archive 都要找（`for archived in (False, True): folder = base/archive if archived else base`）。

### search_messages 覆盖评论

`search_messages` 循环完 state.db 后，若未满 limit 追加 `_search_comment_messages(q, ...)`：
扫评论 JSON 的 content 子串（不区分大小写），命中返回 `session_id: "comment:" + f.name` 供前端跳转。
⚠️ 注意缩进：追加逻辑在 profile 循环**之后**（模块级），别嵌进 finally/break 结构里（本会话 patch 曾把缩进搞坏）。

### 文件名解码（三个实测坑）

会话 key = `comment:{项目}:{open_id}`（**两个冒号**），percent-encode 后 `%` → `_pct_`：

```
comment_pct_3A_<编码项目>_pct_3Aou_xxx.json          # 活跃会话
comment_pct_3A_<编码项目>_pct_3Aou_xxx_20260808_115928.json  # 归档（追加时间戳）
```

正确解码（`_decode_comment_key`）：

```python
def _decode_comment_key(filename):
    if not filename.startswith("comment_") or not filename.endswith(".json"):
        return None
    body = filename[:-5]
    body = re.sub(r"_\d{8}_\d{6}$", "", body)          # ① 剥离归档时间戳
    decoded = unquote(body.replace("_pct_", "%"))       # ② _pct_ 还原 %
    parts = decoded.split(":")
    if len(parts) < 3 or parts[0] != "comment":
        return None
    return {"project": parts[1], "open_id": ":".join(parts[2:])}  # ③ 两冒号
```

**坑 1：不能切固定前缀**。早期实现 `filename[len("comment_pct_3A_"):]` 再解码——
前缀切掉后首个 `%` 标记残缺，项目名乱码（实测 `pct_E4��妖记`）。
**坑 2：不剥时间戳** → 归档会话 open_id 变成 `ou_xxx_20260808_115928`，真名反查失败。
**坑 3：key 是两个冒号**（`comment:项目:open_id`），`partition(":")` 只能拿第一个冒号，
必须 `split(":")` 后验证 parts[0]=="comment"、join 剩余段当 open_id。

### 消息三段解析（_parse_comment_message）

user 消息 = 完整 prompt 文本，逐行匹配前缀：

```python
for line in content.splitlines():
    if line.startswith('The user added a reply in "') or line.startswith('The user added a comment in "'):
        # 提取双引号内文档标题：find('in "')+4 到 rfind('"')
    elif line.startswith('Current user comment text: "'):
        comment = line[len(prefix):]  # 去尾部引号
    elif line.startswith('Original comment text: "'): ...
    elif line.startswith('Quoted content: "'): ...
```

注意：user 消息的 prompt 里还有 timeline（`[姓名] 文本` 行）、系统指令、Document link 等——
**不要整个展示**，只提取 doc/comment/original/quoted 四个字段。assistant 消息原样返回（纯 markdown）。

### 时间戳

JSON 里 `messages[]` 没有单条时间戳，只有顶层 `last_access`。
按消息序从 last_access 倒推（60s/条）模拟：

```python
ts = last_access - (len(msgs) - 1 - i) * 60 if last_access else None
```

### 真名反查

复用已有的 `NameResolver`（lark-cli 反查 + name_cache.json 7 天 TTL），
对每个会话的 open_id 反查 user_name——与渠道会话共用缓存，零新增成本。
（`_comment_sessions_as_rows` 里：`names` 已含本次反查结果则复用，否则 `resolver.resolve`。）

## 前端实现（index.jsx）

### marked 引入

SDK **没有 markdown 渲染能力**（grep 确认），方案 = npm 装 marked + esbuild bundle 打进 IIFE：

```bash
cd Projects/hermes-web-tools && npm install marked
./node_modules/.bin/esbuild channel-sessions-web/src/index.jsx \
  --bundle --format=iife --outfile=channel-sessions-web/dist/index.js --minify
```

源码顶部 `import { marked } from "marked";`（esbuild bundle 支持 IIFE 内 import）。

### mdRender（XSS 防御）

```js
function mdRender(text) {
  let html = marked.parse(text);
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<iframe[\s\S]*?<\/iframe>/gi, "")
    .replace(/\son\w+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "");
}
```

### 消息渲染（CommentMessageItem）

- user 消息：三段式 = 头部（「评论」标签 + 📄文档名 + 时间）+ 评论正文（mdRender）+ 引用原文块（border-l-2 引用样式）
- assistant 消息：整条 mdRender（纯 markdown 回复）
- 无结构化字段（doc/comment 都空）→ 退回全文渲染

### 并入列表（独立平台，不建 Tab）

- `MessageItem` 开头判断：`if (m.doc || m.comment || m.quoted || m.is_comment) return <CommentMessageItem m>`
  —— 评论消息直接复用详情栏，**不加 view state / 不加 Tab / 不加独立组件树**
- 会话对象识别加评论分支：`objectKey` → `comment:<user_id>`；`typeLabel` → 「评论」；`personKey` → `name:<真名>`
- **平台平级（最终形态）**：`PLATFORM_LABELS.comment = "飞书评论"`（不是「评论」）；平台筛选项从 `platformLabel(s.source)` 自动推导，source=comment 的记录自动成为独立筛选项，与「飞书」并列——**无需写死筛选逻辑**，只加标签映射即可

### 列表 UI 偏好（2026-08-10 用户拍板，渠道+评论通用）

- **排序下拉三档**（列表头部 select）：时间↓（默认）/ 时间↑ / 消息数；`localStorage` 持久化（key `cs-dash-sort`）；排序在归档沉底、置顶浮顶之后生效
- **日期分组分隔符**：列表按 `last_activity_at` 分组，组间插 sticky 吸顶条（`bg-muted/40 backdrop-blur-sm text-[10px]`），显示「标签 (数量)」
  - 标签规则（node 冒烟 9/9 通过）：`diffDays = Math.floor((now - ts) / 86400)`；`<1→今天`（含未来时区差归今天）、`<2→昨天`、`<3→前天`、`<7→一周前`、`<30→一月前`、`<365→一年前`、否则「更早」、无时间戳「未知」
  - 实现：`grouped` useMemo 按过滤后顺序遍历建组（Map 记组索引），渲染时 `grouped.map(g => Fragment(分隔条 + g.items.map(SessionRow)))`

### 只读防护（关键，评论会话没有 state.db 操作）

- SessionRow：`noOps = is_comment` → 隐藏 📌/🗄/✏️/🗑 四个管理按钮、批量 checkbox 不渲染
- 详情头部：`selected.is_comment ? null :` 包住 导出/重命名/置顶/归档/删除 全部按钮
- 批量选择：`toggleAll` 用 `filtered.filter(s => !s.is_comment)`（全选不含评论）；`allChecked` 同样过滤
- 原因：评论会话是 JSON 只读数据源，管理按钮打上去走 state.db 会报错

## 样式补类（style.css）

评论视图新增 className 需要手写补到 style.css（Tailwind 编译期扫描不覆盖插件 JS）：
`mt-1.5 / pl-2.5 / px-2.5 / rounded-md / disabled:opacity-50 / disabled:cursor-not-allowed / hover:text-amber-500 / hover:text-blue-400 / hover:text-destructive / hover:text-primary / hover:underline`

**markdown 内容样式 `.cs-md` 全套**（marked 输出的元素需要自己定义）：

```css
.cs-md { line-height: 1.65; font-size: 13px; word-break: break-word; }
.cs-md p { margin: 0.375em 0; }
.cs-md h1..h4 { font-weight: 600; ... }
.cs-md ul { list-style: disc; } .cs-md ol { list-style: decimal; }
.cs-md blockquote { border-left: 2px solid var(--color-border); padding-left: 0.75em; color: var(--color-muted-foreground); }
.cs-md code { font-family: ui-monospace, ...; background: color-mix(in srgb, var(--color-muted) 40%, transparent); }
.cs-md pre { background: ...; border-radius: 6px; padding: 0.6em 0.75em; overflow-x: auto; }
.cs-md table { border-collapse: collapse; display: block; overflow-x: auto; }
.cs-md th, .cs-md td { border: 1px solid var(--color-border); padding: 0.3em 0.55em; }
.cs-md a { color: var(--color-primary); }
.cs-md img { max-width: 100%; }
```

## 测试（pytest 36 例全过，含 8 个评论新增）

- **测试隔离坑**：`list_sessions` 测试若不 mock，`_comment_dir()` 会读到**真实评论目录**把真实会话混进断言（实测 4→8 崩）。必须在现有测试里 `monkeypatch.setattr(service, "_comment_dir", lambda: None)`；评论功能单独建临时目录测（`tmp_path / "评论会话"` + archive 子目录 + 手写 JSON fixture）
- 新增测试覆盖：文件名解码（活跃/归档剥时间戳/非法）、消息解析（全字段/纯文本）、list 合并（is_comment 记录字段/归档标记）、get_messages comment 分支、search 评论命中

## 类审计脚本 bug（实测，别踩）

skill 自带 `scripts/audit_plugin_classes.py` 有两个问题：

1. **`%LOCALAPPDATA%` 格式化占位 bug**：`Path(r"%LOCALAPPDATA%" % {"LOCALAPPDATA": ""})`
   报 `ValueError: unsupported format character 'O'`（`%` 后跟 `L` 不是合法格式符）。
2. **转义匹配易误报**：CSS 选择器里 `.gap-1\.5` / `.text-\[11px\]` / `.hover\:underline` 的
   Tailwind 转义形式与源码 className 直接比对会全 MISSING，需要先还原转义。

**可靠替代（实测可用）**：

```python
# 1. 提取 JSX 里所有 className（cn() 包裹的和裸字符串）
for m in re.finditer(r'className:\s*cn\(\s*"([^"]+)"', src):
    classes.update(m.group(1).split())
for m in re.finditer(r'className:\s*"([^"]+)"', src):
    classes.update(m.group(1).split())
# 2. 提取 CSS 选择器（style.css + web_dist assets/*.css）并还原转义
sels = set(re.findall(r'\.([a-zA-Z0-9_\\\[\]\.%\-:\/]+)', css_text))
norm = {s.replace('\\[','[').replace('\\]',']').replace('\\.','.').replace('\\:',':') for s in sels}
# 3. 比对
```

判断「某个类是否已补」的正确姿势：直接 grep style.css 是否含该类的转义形式
（如 `grep -c "mt-1\\\\.5" style.css`），别依赖审计脚本。

## 部署与生效

- **改 plugin_api.py / service.py 的生效目标按形态分（2026-08-10 实测修正）**：
  - Web Dashboard 形态（9120）：后端由 **HermesDashboard 计划任务进程**加载 → 必须重启 HermesDashboard
    （`Stop-Process -Id <9120 PID> -Force; Start-ScheduledTask HermesDashboard`，等 9120 监听）
  - **重启 gateway（8644）对 dashboard 插件后端无效**（实测先重启 gateway 仍旧代码，重启 9120 才生效）
  - gateway 与 dashboard 各自挂插件 API（日志 `Mounted plugin API routes`），用户实际访问走 9120
- **dist/index.js、style.css 是静态文件**：改完无需重启服务，浏览器**硬刷新（Ctrl+Shift+R）**即生效
- 正本仓库同步：源码在 `Projects/hermes-web-tools/channel-sessions-web/src/index.jsx`（esbuild 构建），
  部署位置 `~/AppData/Local/hermes/plugins/channel-sessions/dashboard/dist/`；
  后端正本 `Projects/channel-sessions/plugins/channel-sessions/dashboard/`——**两个仓库都要同步**，
  且 Projects/channel-sessions 的 service.py 可能比部署版旧（缺 is_active 等列），以部署版为基准改再同步回去。
