# 列表类插件的多条件筛选模型 + 会话对象键设计

来源：channel-sessions 插件 v1.2（用户三轮迭代后的最终形态）。任何「列表 + 分类 + 管理」类插件可复用。

## 筛选器模型（五维 AND 叠加）

```js
const DEFAULT_FILTERS = { platform: 'all', person: 'all', status: 'all', type: 'all', query: '' }
```

- 每个维度**独立单选**（内部再点取消），**跨维度 AND 叠加**——用户明确否定了单选导航（一次只能选一个维度）
- 每个维度的可选项由数据推导并带计数：`buildFilterOptions(all) → {platforms, persons, groups, localCount, statuses, types}`
- 匹配函数单一出口：

```js
function matchesAll(s, f) {
  if (f.platform !== 'all' && (s.source || 'unknown') !== f.platform) return false
  if (f.person !== 'all') {
    if (f.person === 'local') { if (objectKey(s) !== 'local') return false }
    else if (objectKey(s) !== f.person) return false
  }
  if (f.status === 'pinned' && !s.pinned) return false
  if (f.status === 'archived' && !s.archived) return false
  if (f.type !== 'all' && chatTypeKey(s) !== f.type) return false
  const q = f.query.trim().toLowerCase()
  if (q) { /* hay = [title, user_name, user_id, display_name, source, chat_id, objectLabel].join(' ').toLowerCase() */ }
  return true
}
```

## 失效筛选自动回退（必做）

数据刷新后（删除会话/平台消失），持久化的选中项可能已不存在 → 悬空筛选让列表永远为空。用 useMemo 校验：

```js
const validFilters = useMemo(() => {
  const f = { ...filters }
  if (f.platform !== 'all' && !options.platforms.some(p => p.key === f.platform)) f.platform = 'all'
  if (f.person !== 'all' && f.person !== 'local' && ![...options.persons, ...options.groups].some(o => o.key === f.person)) f.person = 'all'
  if (f.person === 'local' && !options.localCount) f.person = 'all'
  if (f.type !== 'all' && !options.types.some(t => t.key === f.type)) f.type = 'all'
  return f
}, [filters, options])
```

## 会话对象键（跨平台归一）

平台无关的会话「对象」标识——私聊人 / 群 / 话题 / 本地，全部会话可归组、可筛选：

```js
function objectKey(s) {
  if (s.source === 'desktop' || s.source === 'cli' || s.source === 'tui') return 'local'
  if (s.source === 'feishu') {
    return s.chat_type === 'group' ? `group:${s.chat_id || 'g'}` : `person:${s.user_id || 'u'}`
  }
  if (s.chat_type === 'group' || s.chat_type === 'chat') return `group:${s.chat_id || 'g'}`
  if (s.chat_type === 'topic' || s.chat_type === 'thread') return `topic:${s.chat_id || 'g'}:${s.thread_id || 't'}`
  return `person:${s.user_id || 'u'}`
}

function objectLabel(s) {
  if (本地) return '本地会话'
  if (群) return display_name 非空且非 oc_ 开头 ? display_name : `${platformLabel(s.source)}群`
  if (话题) return display_name 或 `${platformLabel(s.source)}话题`
  return s.user_name || userFallback(s)   // 私聊
}

function userFallback(s) {  // 各平台 ID 语义不同，无法反查时的可读形态
  if (!uid) return '(未知会话人)'
  if (ou_/on_ 开头) return '飞书用户'
  if (/^\d+$/) return `用户 ${uid.slice(-4)}`
  if (len > 10) return `${uid.slice(0,8)}…`
  return uid
}
```

## UI 组织（双栏）

- **左栏**（w-64）：搜索框 + 四个筛选区（平台 chips / 会话人列表 / 状态 chips / 类型 chips）。会话人区分「会话人」「群聊 / 频道」「本地会话」三个子组；对象项=首字色块 + 名称 + 计数，选中高亮 `bg-(--ui-control-active-background)`
- **右栏**：顶部一条当前组合描述（`activeParts.join(' · ')` + 会话数 + 一键清除），下面列表
- 每行：状态点（置顶/归档）| 标题 + 类型徽标 | 副行（对象名 · 预览）| 右侧 消息数 + 相对时间 + 操作菜单

## UI 状态记忆

```js
const [filters, setFilters] = useState(() => ({ ...DEFAULT_FILTERS, ...apiStorage.get(UI_STORAGE_KEY, {}) }))
const saveFilters = patch => setFilters(prev => {
  const next = { ...prev, ...patch }
  apiStorage.set(UI_STORAGE_KEY, next)
  return next
})
```

## 冒烟测试（不启动 UI）

`node -e` 截取 import 之后到组件定义前的纯函数段，`new Function(...)` 执行并返回函数引用，构造假数据验证 objectKey/objectLabel/buildFilterOptions/matchesAll 的组合场景（平台×人、平台×类型、搜索）。改逻辑后必跑。
