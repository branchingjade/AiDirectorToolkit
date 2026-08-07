# 消息详情面板通用模式（v1.3，channel-sessions 插件）

任何「列表 + 详情」类桌面插件（会话记录、任务历史、审批流）可复用本模式：点列表行，右侧同屏显示详情，不跳转。

## 后端 /messages 路由

```python
@router.get("/messages")
def get_session_messages(session_id: str, profile: str = "default", limit: int = 200) -> dict:
    from hermes_state import SessionDB
    db = SessionDB(db_path=<profile 的 state.db>, read_only=True)
    try:
        sid = db.resolve_session_id(session_id)          # 支持 id 前缀
        if not sid:
            return {"session_id": session_id, "messages": []}
        sid = db.resolve_resume_session_id(sid)          # 压缩续体投影到最新会话
        messages = db.get_messages(sid, limit=min(max(limit, 1), 500))
        # 瘦身：{id, role, content, timestamp, tool_name, tool_calls, active, compacted}
    finally:
        db.close()
```

要点：
- `resolve_resume_session_id` 必须调——压缩续体会把旧 id 投影到最新续体，不调会查空
- `get_messages` 返回 messages 表全字段（SELECT *），content 已解码；只取渲染需要的字段避免大字段进前端
- role 取值：user / assistant / tool / session_meta（元数据消息，前端隐藏）

## 前端三栏 + 选中管理

```
<div flex min-h-0 flex-1>
  <aside 左筛选 w-64 border-r>        ← 筛选区（可折叠分区）
  <div 中列表 w-[380px] border-r>     ← 列表 + 状态条
  <div 右详情 flex-1 min-w-0>        ← 详情（无选中时 EmptyState 引导）
</div>
```

- `selectedId` state；行点击 `setSelectedId(prev => prev === id ? null : id)`（toggle）
- `selected = all.find(s => s.id === selectedId)` —— 从最新列表数据取，标题/置顶状态随刷新更新，不存旧对象
- 行高亮：`active={selected && selected.id === s.id}` + `bg-(--ui-control-active-background)`
- 删除选中会话后：`if (selectedId === s.id) setSelectedId(null)`
- messagesQuery：`enabled: !!selected` + `refetchInterval: 30000`（会话列表 15s，消息 30s）

## 消息分角色渲染 + 折叠展开

```js
const LONG_MESSAGE_THRESHOLD = 600

function MessageItem({ m }) {
  if (m.role === 'session_meta') return null
  const content = (m.content || '').trim()
  const isTool = m.role === 'tool'
  const isLong = content.length > LONG_MESSAGE_THRESHOLD
  const [expanded, setExpanded] = useState(() => !isTool && !isLong)  // 惰性初始化

  if (isTool) {
    // 默认折叠一行：🔧 工具名 + 「展开详情（N字）」；展开才显示内容
    return <灰底小字块>{tool_name} {expanded ? '收起' : `展开详情（${content.length}字）`}
      {expanded && <pre-wrap>{content}</pre-wrap>}</灰底小字块>
  }
  const body = expanded ? content : content.slice(0, LONG_MESSAGE_THRESHOLD)
  // 用户：左「我」accent 底色；AI：左「AI」灰底；右侧气泡 pre-wrap
  // 长消息下方：「展开全文（共N字）」/「收起」
  // compacted 字段 → 「（此段已被压缩）」标注
}
```

折叠规则：
- 工具消息**默认折叠**（内容常为 skill 全文/搜索结果，防刷屏）
- 长消息（>600 字）**默认折叠**前 600 字，按钮展开
- `useState(() => ...)` 惰性初始化——每条消息独立折叠态（key 用 m.id）

## 详情头部（信息层次）

返回按钮（arrow-left）| 标题（truncate + pinned 图标）| 副行（对象名 · 平台 · N 条消息）| 右侧「完整打开」（host.navigate 跳完整页）+ 操作菜单（重命名/置顶/归档/删除复用列表行菜单）。

## 时间显示

- 列表行：相对时间 `fmtTime(ts)`（刚刚/X分钟前/X小时前/昨天/X天前/日期）
- 消息气泡：钟点 `fmtClock(ts)`（HH:mm）——列在头像旁竖排
- state.db 时间戳为秒级（`last_activity_at`/`started_at`/`timestamp`），`new Date(ts * 1000)`
