# 曲多多（haifanwu.com）平台说明

## 平台身份

- haifanwu.com = 曲多多 = 嗨翻屋，同一平台
- Eagle 中版权音乐文件名格式：`曲多多_<数字ID>_<英文名>.wav`
- 平台用数字 ID 标识曲目（如 `4776764`）
- 站点是 **Nuxt 2.x SPA**，路由见 `window.$nuxt.$router.options.routes`

## 提取元数据：三种方案（按优先级排列）

### 🥇 首选：`window.__NUXT__` 直接取 JSON

### 核心入口

```javascript
window.__NUXT__.data[0].songDetail
```

### songDetail 字段

| 字段 | 类型 | 示例 |
|------|------|------|
| `name` | string | `"Hearthside Lullaby"` |
| `bpm` | number | `172` |
| `duration` | string | `"02:19"` |
| `composer` | string[] | `["Alonso"]` |
| `performer` | string[] | `["Alonso"]` |
| `albumName` | string | `"Glow"` |
| `poets` | string | 作词人 |
| `labelGroup` | string | 厂牌 |

### attribute 标签树

`songDetail.attribute` 是分类标签数组，每个元素：

```javascript
{
  typeName: "使用场景",       // 分类名
  child: [
    { tagName: "影视配乐" },
    { tagName: "影视配乐:冒险片" }  // 层级用冒号分隔
  ]
}
```

分类包括：使用场景、流派、情绪、特征、器乐、速度、年代、调、国家/地区、关键词 等。

### 一行提取

```javascript
// browser_console 中运行，直接拿到所有数据
(function(){var sd=window.__NUXT__.data[0].songDetail;
var tags=['曲多多','haifanwu','版权音乐'];
if(sd.bpm)tags.push('BPM:'+sd.bpm);
if(sd.attribute)for(var a=0;a<sd.attribute.length;a++){
var cat=sd.attribute[a];
if(cat.child)for(var c=0;c<cat.child.length;c++)tags.push(cat.child[c].tagName);
}
return JSON.stringify({name:sd.name,bpm:sd.bpm,duration:sd.duration,
composer:sd.composer,performer:sd.performer,album:sd.albumName,
poets:sd.poets,tags:tags});})()
```

**注意**：browser_console 有长度限制，如果表达式太长报 `SyntaxError: Unexpected end of input`，只提取关键字段，写入逻辑放 execute_code 中。

### 🥈 降级：DOM innerText（`__NUXT__` 不可用时）

如果页面未走 SSR（如 SPA 模式、已登录态），`window.__NUXT__` 可能为 undefined。此时降级为 DOM 查询：

```javascript
var h=document.querySelectorAll('h3');var info=null;
for(var i=0;i<h.length;i++){if(h[i].textContent==='歌曲基本信息'){info=h[i].parentElement;break;}}
if(!info)return'NF';
return info.innerText;  // 全文，需后续解析
```

### 批量提取流程

1. `browser_navigate` 到任意歌曲页（建立 origin）
2. `browser_console` 运行上面的提取 JS，拿到结构化数据
3. `execute_code` 用 `w()` 模板写入 Eagle（见 `references/batch-write-template.md`）
4. **下一首直接用 `browser_navigate`** 跳转，重复步骤 2-3

#### 执行策略

| 规模 | 策略 |
|------|------|
| ≤5 首 | 串行，每首 navigate + console + write |
| 6-20 首 | 串行即可，每首 ~2 秒，总计 <1 分钟 |
| >20 首 | `delegate_task` 分 3-4 个子 agent，每 agent 5-6 首 |

#### 代码分离原则

- **browser_console**：只提取 `__NUXT__` 数据，返回 JSON。不要在里面写 Eagle（表达式太长会报错）
- **execute_code**：承担写入逻辑，用 `w()` 模板函数一次性定义，每首只传数据 dict
- **禁止**在 browser_console 中拼接 annotation 字符串——放 execute_code 里做

### 🔴 browser_navigate 会下载封面图到 Eagle

CDP 浏览器加载歌曲页时自动下载专辑封面图，Eagle 自动导入到库中。**处理前必须清空自动导入目录**：

```python
import os, glob, shutil
d = "C:/Users/HMSJ/Documents/eagle"
for f in glob.glob(os.path.join(d, "*.*")):
    try: os.remove(f)
    except: pass
```

已导入 Eagle 的图片只能用户在 GUI 手动删除（API 无删除端点）。

### 回写 Eagle

**禁止在 browser_console 中写 Eagle**——表达式太长会报错。统一用 `execute_code` + 模板函数。模板见 `references/batch-write-template.md`。

## 不可行的方式（已验证）

| 方式 | 结果 |
|------|------|
| `curl` API 直调 | 阿里云 WAF 返回 JS 挑战页 |
| URL hash 路由 | SPA 不识别 |
| `fetch()` 同源调用 | 从首页调用返回 SPA 壳；从歌曲页调用能拿到 SSR HTML 但 `__NUXT__` 数据按函数参数分散无法直接提取 |
| 快照文字 / DOM innerText 解析 | 低效且不可靠，`__NUXT__` 才是权威数据源 |

**注意**：`browser_navigate` 到完整 SSR URL（`/song-detail/<ID>`）是可行的——这走服务端渲染，不是 hash/query 路由。
