---
name: eagle
description: Eagle 本地 API 资产管理——浏览文件夹、搜索素材、管理标签。Eagle 是一款设计/素材管理工具，通过 localhost:41595 提供 REST API。
---

# Eagle API 资产管理

## 触发条件
用户提到 Eagle、素材库、在 Eagle 中查找/管理文件、Eagle 标签/文件夹操作。

## API 基础

- **端口**：`localhost:41595`
- **认证**：无需 token（token 在 `/api/application/info` 响应中可见，但所有端点无需认证即可调用）

### 核心端点

```bash
# 获取应用信息（版本、平台、偏好设置）
curl -s http://localhost:41595/api/application/info

# 按 ID 查素材元数据（ext/size/width/height/palettes/tags/annotation）——库盘未挂载时也能查到
curl -s "http://localhost:41595/api/item/info?id=<ITEM_ID>"

# 获取完整文件夹树（递归，包含 children）
curl -s http://localhost:41595/api/folder/list

# 列出文件夹内的项目
curl -s "http://localhost:41595/api/item/list?folders=<FOLDER_ID>"

# 按关键词搜索
curl -s "http://localhost:41595/api/item/list?keyword=<关键词>"

# 按扩展名筛选（限制 50 条）
curl -s "http://localhost:41595/api/item/list?ext=mp3&limit=50"
```

### 响应格式

```json
{
  "status": "success",
  "data": [
    {
      "id": "MQF4WH0AXL5YA",
      "name": "音乐",
      "children": [...],       // folder/list 才有
      "ext": "wav",
      "tags": [],
      "url": "",
      "folders": ["MQF4WH0AXL5YA"]
    }
  ]
}
```

## Eagle MCP vs REST API（分工明确）

| 操作 | 用哪个 | 原因 |
|------|--------|------|
| 查询文件夹内容 | `mcp_eagle_listItems(folders=...)` | REST `?folders=` 在 Eagle 4.0 返回 404 |
| 搜索关键词 | MCP 或 REST 均可 | 两个都正常工作 |
| 获取文件路径 | `mcp_eagle_getItemFilePath` | REST 没有这个端点 |
| 更新标签/注释 | REST `POST /api/item/update` | **MCP 没有 update 工具**，必须走 REST |
| 文件夹操作 | `mcp_eagle_createFolder` | REST `parent` 参数有坑 |

**写入操作始终用 `execute_code` + Python `urllib`**，不走 MCP。

**⚠ MCP 工具需要新会话才能生效**：`hermes mcp add eagle` 后必须 `/new` 重开。如果当前会话没有 `mcp_eagle_*` 工具，用下方 REST API 直调（Python `urllib`）降级。

## 关键陷阱

### 1. 中文编码：禁止 terminal + curl，必须 Python urllib

**🚫 禁止**：terminal 中用 `curl` 传中文 JSON。shell 管道编码转换会破坏 UTF-8，导致 Eagle 中文件夹名/标签变成乱码。

**✅ 正确**：用 `execute_code` + Python `urllib.request` 直连 API：

```python
import urllib.request, json

def api(method, path, data=None):
    url = f"http://localhost:41595{path}"
    if data:
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=payload, method=method,
            headers={'Content-Type': 'application/json; charset=utf-8'})
    else:
        req = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())
```

**例外**：`folder/list` 返回巨型树（可能 >100KB），用 `curl | python3 -c` 流式管道，不进入 execute_code。

### 2. execute_code 中文搜索需 URL 编码

`execute_code` 中的 `urllib.request` 对 URL 路径中的中文会抛 `UnicodeEncodeError: 'ascii' codec can't encode characters`：

```python
# ❌ 中文直接拼 URL → UnicodeEncodeError
items = api('GET', '/item/list?keyword=修复')

# ✅ URL 编码中文
import urllib.parse
kw = urllib.parse.quote('修复')
items = api('GET', f'/item/list?keyword={kw}')
```

### 3. 创建文件夹：用 `parent` 不是 `parentId`

```python
# ❌ parentId 不可靠——文件夹会被建到根目录
api('POST', '/folder/create', {'folderName': 'test', 'parentId': '<ID>'})

# ✅ parent 正确
api('POST', '/folder/create', {'folderName': 'test', 'parent': '<ID>'})
```

### 4. 导入文件：验证结果，不依赖树

`addFromPath(s)` 的 `folderId` 参数已验证可用。导入后立即用直接查询验证，不要依赖 `folder/list` 的树结构（有缓存延迟）：

```python
items = api('GET', f'/item/list?folders={folder_id}')
```

**⚠️ urllib 连 localhost:41595 必须绕过系统代理**（Windows 上系统代理会劫持 localhost 请求 → ConnectionRefused 10061）：
```python
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
with opener.open(req, timeout=30) as resp: ...
```

**⚠️ API 路径必须带 `/api` 前缀**：`/api/folder/list`、`/api/item/info`、`/api/item/addFromPaths`，漏掉 `/api` 返回 404。

批量导入：`POST /api/item/addFromPaths`，body `{"paths": [绝对路径...], "folderId": "..."}`，返回新素材 ID 列表。导入后逐条 `/api/item/info?id=...` 验证 name/ext/width/height/size。中文路径用 `ensure_ascii=False` 序列化 JSON。

### 4b. URL 远程导入（Eagle 4.0 关键坑，2026-08-12 实测）

**端点：`POST /api/item/addFromURL`**（`createFromURL`/`createFromPath` 在 4.0 已 404 废弃；`addFromPath` 400 参数不明不可靠）。

```js
// 浏览器前端直连（Access-Control-Allow-Origin: * 已开放）
fetch('http://localhost:41595/api/item/addFromURL', {
  method:'POST', headers:{'Content-Type':'text/plain'},  // 必须 text/plain！
  body: JSON.stringify({url:'http://192.168.1.2:8000/audio/114?download=1', name:'素材名', website:'来源', tags:['豆包TTS']})
})
```

四个坑（全部实测）：

1. **POST 必须 `Content-Type: text/plain`**——JSON content-type 会触发 CORS preflight（OPTIONS），Eagle **不响应 OPTIONS**（返回 404）→ 浏览器 `Failed to fetch`。text/plain 是简单请求，直接通过。服务端 curl 用 application/json 可以（无 CORS 参与），浏览器必须 text/plain。
2. **假成功**：下载 404 的 URL 也返回 `{"status":"success"}`——调试时必须用真实存在的 URL，导入后去 `item/list` 验证是否真入库，不能信响应。
3. **name/annotation/tags 参数不可靠**——Eagle 可能改写名称（115_xxx.wav 导入后显示为「铁门」），tags 可能不落。别依赖这些参数做查重。
4. **重复文件弹窗**：重复导入同文件时 Eagle UI 会弹窗（服务器端静默 success）。要「默认使用已存在文件不弹窗」，发送前查重：`GET /api/item/list?limit=5000` 拉全量，按 `item.size === 素材 size` 匹配（size 是可靠指纹，同素材必然命中），命中则跳过导入。



### 5. 文件夹树缓存延迟

`/api/folder/list` 返回的 `children` 可能不反映最近变更。始终用 `item/list?folders=<ID>` 验证。

### 6. 没有删除/移动端点

- `/folder/delete` → 404
- `/item/delete` → 404  
- `/item/move` → 404

出错的文件夹/文件只能让用户在 Eagle GUI 手动删除或拖动。

### 7. 获取文件真实路径（缩略图 API 技巧）

Eagle REST API 没有 `getItemFilePath`，但缩略图 API 暴露了目录：

```python
# 先获取 item 的 thumbnail URL
r = api('GET', '/item/thumbnail?id=<ITEM_ID>')
thumb_path = r['data']  # e.g. "Y:/HMSJ_B.library/images/XXX.info/file_thumbnail.png"
# 去掉 _thumbnail.png 即得文件所在目录
file_dir = thumb_path.rsplit('_thumbnail.png', 1)[0]
# 然后 ls 或直接拼接文件名
```

库路径模式：`<盘符>:/<库名>.library/images/<ITEM_ID>.info/<文件名>.<ext>`

### 8. 覆盖 Eagle 库文件

由于 API 不支持更新文件内容，要替换已导入文件的内容只能直接覆写磁盘文件：

```bash
cp "新文件路径" "Y:/库名.library/images/<ITEM_ID>.info/原文件名"
```

这不会破坏 Eagle 的元数据索引。完整流程见 `references/eagle-file-ops.md`。

### 9. 外部平台元数据：优先用 `window.__NUXT__` 直接取 JSON

曲多多等 Nuxt SPA 在 SSR 渲染时把数据注入 `window.__NUXT__.data[0].songDetail`。**
这是最干净的提取方式**——结构化 JSON，无需文本解析。
优于 DOM shortcut 和快照直读。一次 `browser_console` 调用拿到全部字段。

```javascript
// 首选：__NUXT__ 直接取
var sd = window.__NUXT__.data[0].songDetail;
// sd.bpm, sd.duration, sd.name, sd.composer, sd.performer
// sd.attribute → 分类标签树 [{typeName: "使用场景", child: [{tagName: "影视配乐"}, ...]}, ...]
```

`fetch()` 获取的 HTML 中 `__NUXT__` 数据分散为函数参数 `(false,"true",0,null,{...},...)`，无法从文本直接解析。必须通过 `browser_navigate` 让页面渲染后从 `window.__NUXT__` 读取。

### 10. CDP 浏览器会下载图片到 Eagle 自动导入

`browser_navigate` 加载页面时连带下载专辑封面图，Eagle 自动导入到库中。**处理前清空 `C:\Users\<用户>\Documents\eagle\` 目录**，处理中定期清理。Eagle API 不支持删除，已导入的图片需用户在 GUI 手动移除。

### 11. 禁止逐首重写脚本——用可复用模板

用户对此零容忍。批量写入 Eagle 时，**在 execute_code 中定义一个 `w()` 函数**，每首只传数据 dict，不要重写 urllib/json 样板。模板见 `references/batch-write-template.md`。

### 12. 库盘未挂载：API 元数据可用，但文件不可读

Eagle 库可能位于网络盘/外置盘（如 `Y:`）。盘未挂载时（`subst` 空、`net use` 空、`Get-PSDrive` 只剩 C:）：
- `/api/item/info?id=<ID>` 仍返回完整元数据（ext/size/width/height/palettes）——先查素材再决定下一步
- `/api/item/thumbnail` **只返回路径字符串**（`Y:/xxx.library/images/<ID>.info/xxx_thumbnail.png`），不返回图片字节——不能靠它验证盘可达性或读取文件
- Eagle 4.0 实测 `/api/item/export`（GET/POST 均 404 method not allowed）——没有导出端点可用
- 元数据中 `ext` 字段区分素材类型：`gif` 是动图（Eagle 中常见"动态封面"类素材），压缩/转换前必须确认——动图需逐帧处理，不能当静态图只处理第一帧（会丢动画）
- 文件操作（读取源文件/覆写）需用户先挂载盘或把文件复制到可达路径

**盘不可达的判定**（用户说"映射没问题"时也要实测）：`powershell Get-CimInstance Win32_LogicalDisk` 只列 C: + `Get-SmbMapping` 为空 + `subst` 空 → 映射确实不存在（UAC 提升/非提升进程也可能互相看不见映射，两级别都查一遍）。

**NAS 库的 SSH/SFTP 兜底（无需用户挂盘）**：库在 NAS 上时直接走 SSH/SFTP 绕开 SMB——绿联 NAS 的 SMB 用户与 SSH 用户是两套账户（SSH 的 HMSJadmin 常在 SMB 共享 `valid users` 之外，net use 报 67/1702 就别死磕）。关键路径要点见 `ugreen-nas-deploy` skill：SFTP 路径用共享名映射（`/HMSJ_B/...` 而非 `/volume1/...`），`sftp.stat` 报 Operation unsupported 但 `open/read/write` 正常，大文件用 `sftp.open(remote,'rb').read()`。写回用 SFTP 覆盖库文件即可，`metadata.json` 不用动，Eagle 自动重新索引。

## 写入操作（更新元数据）

### 更新文件标签/注释/URL

```bash
curl -X POST "http://localhost:41595/api/item/update" \
  -H "Content-Type: application/json" \
  -d '{"id":"<ITEM_ID>","tags":["版权音乐","曲多多"],"annotation":"曲目ID: 4776764\n来源: haifanwu.com","url":"https://haifanwu.com"}'
```

可写字段：`tags`（数组）、`annotation`（纯文本）、`url`（链接）。

无批处理端点，逐条 POST。

**⚠️ 禁止用 terminal + curl 传中文**：shell 管道的转义会破坏 UTF-8 编码，导致 Eagle 中所有中文变成乱码。批量写入时用 Python `urllib.request` 直连 API（在 `execute_code` 中），不使用 `terminal()` 中转。

### 从文件名提取元数据

Eagle 中版权音乐常见命名格式：
```
曲多多_<ID>_<英文名>.wav    # 曲多多/haifanwu.com
```

可从文件名提取 ID 和名称直接写入标签/注释，无需爬平台（参考 references/quduoduo.md）。

## 典型工作流

### 查找项目素材
1. 用 folder/list 获取完整树
2. 在 Python 中过滤目标文件夹名
3. 用文件夹 ID 调用 item/list

### 解读用户路径描述
用户说"项目-《犬子无双》音乐"意味着 Eagle 路径：`项目 → 《犬子无双》 → 素材 → 音乐`

### 批量查看文件
用 `curl ... | python3 -c` 管道，提取 name、ext、tags、url 字段即可。不要打印整个 JSON 对象。

### 同步外部平台元数据到 Eagle（强制执行前检查）

**⚠️ 执行前强制四步（任何批量操作必须先走）**：
1. **清空自动导入目录**：`C:\Users\HMSJ\Documents\eagle\`（防 browser_navigate 下载封面被 Eagle 捡走）
2. 用 `mcp_eagle_listItems(folders=...)` 列出目标文件，筛选待处理（无标签的跳过）
3. **先讲思路（方向级，非细节）、确认后再动手**
4. 第一首验证通过后，后面全部用同一套代码

确认后执行：

1. `browser_navigate` 到歌曲页 → `browser_console` 读 `window.__NUXT__.data[0].songDetail`（纯 JS 数据，不解析 DOM）
2. `execute_code` 用 `w()` 模板写入（见 `references/batch-write-template.md`）
3. 处理中定期清理自动导入目录

详细提取方法和字段说明见 `references/quduoduo.md`。
