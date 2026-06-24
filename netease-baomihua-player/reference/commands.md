# 命令参考文档

本文档详细描述 `bmh-cli.exe` 的所有命令、参数和返回格式。

---

## 命令总览

| 命令 | 用途 | 常用参数 |
|------|------|---------|
| `doctor` | 环境检测 | 无 |
| `start` | 启动爆米花 | 无 |
| `search` | 搜索媒体 | `--keyword`, `--page`, `--types` |
| `play` | 播放媒体 | `--media-type`, `--tmdb-id`, `--season`, `--episode`, `--source`, `--media-id` |
| `episodes` | 获取剧集信息 | `--tmdb-id`, `--source`, `--media-id` |

---

## 1. doctor - 环境检测

### 用途
检查爆米花客户端的安装状态、运行状态和服务可用性。

### 命令格式
```bash
bin\bmh-cli.exe --json doctor
```

### 参数
无参数

### 返回结构
```json
{
  "success": true,
  "data": {
    "installed": boolean,
    "running": boolean,
    "service_available": boolean,
    "service_port": number,
    "install_path": string,
    "version": string,
    "status": string
  }
}
```

### status 字段取值

| 值 | 含义 | 后续操作 |
|----|------|---------|
| `ready` | 服务就绪 | 继续执行其他命令 |
| `not_installed` | 未安装 | 提示用户安装 |
| `not_running` | 未运行 | 执行 start 命令启动 |
| `service_unavailable` | 服务不可用 | 等待或重启爆米花 |

### 示例

```bash
bin\bmh-cli.exe --json doctor
```

```json
{
  "success": true,
  "data": {
    "status": "ready",
    "installed": true,
    "running": true,
    "service_available": true,
    "service_port": 52020,
    "version": "1.2.0",
    "install_path": "C:\\Program Files\\Netease\\BaoMiHua\\BaoMiHua.exe"
  }
}
```

---

## 2. start - 启动爆米花

### 用途
以静默模式启动爆米花客户端（不弹出窗口），等待服务就绪。

### 命令格式
```bash
bin\bmh-cli.exe --json start
```

### 参数
无参数

### 行为说明
- 已运行：直接返回成功
- 未运行：静默启动并轮询 /health 等待就绪（最多 15 秒）
- 未安装：返回 `APP_NOT_INSTALLED` 错误

### 返回结构
```json
{
  "success": true,
  "data": {
    "message": string,
    "path": string
  }
}
```

### 示例

```bash
bin\bmh-cli.exe --json start
```

```json
{
  "success": true,
  "data": {
    "message": "BaoMiHua started successfully",
    "path": "C:\\Program Files\\Netease\\BaoMiHua\\BaoMiHua.exe"
  }
}
```

---

## 3. search - 搜索媒体

### 用途
在爆米花媒体库中搜索影视内容。若客户端未运行会自动启动。

### 命令格式
```bash
bin\bmh-cli.exe --json search --keyword "<关键词>" [--page N] [--page-size N] [--types "2,3"]
```

### 参数

| 参数 | 缩写 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|--------|------|
| `--keyword` | `-k` | string | ✅ | — | 搜索关键词（中英文均可） |
| `--page` | `-p` | int | ❌ | `1` | 页码 |
| `--page-size` | — | int | ❌ | `20` | 每页数量 |
| `--types` | `-t` | string | ❌ | `2,3` | 媒体类型，逗号分隔。`2`=电影，`3`=电视剧 |

### 返回结构
```json
{
  "success": true,
  "data": {
    "total_count": number,
    "count": number,
    "has_more": boolean,
    "next_page": number,
    "items": [
      {
        "media_id": string,
        "title": string,
        "media_type": number,
        "year": string,
        "poster_url": string,
        "source": number,
        "source_name": string,
        "tmdb_id": string
      }
    ]
  }
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `total_count` | 总结果数 |
| `count` | 当前页结果数 |
| `has_more` | 是否有下一页 |
| `next_page` | 下一页页码（无更多时为 0） |
| `items[].media_type` | `2` = 电影，`3` = 电视剧 |
| `items[].source` | 来源标识（`0`=媒体库, `1`=emby, `2`=jellyfin, `3`=fnos, `4`=zspace） |
| `items[].source_name` | 来源名称：`media_library` / `emby` / `jellyfin` / `fnos` / `zspace` |
| `items[].tmdb_id` | TMDB ID（仅媒体库来源有值，emby/jellyfin/fnos/zspace 为空） |

> **注意**：搜索会同时查询所有数据源（媒体库 + Emby + Jellyfin + Fnos + Zspace），结果合并返回。来自 emby/jellyfin/fnos/zspace 的结果，播放时需使用 `--source` + `--media-id`。

### 示例

```bash
bin\bmh-cli.exe --json search --keyword "星际穿越"
```

```json
{
  "success": true,
  "data": {
    "total_count": 2,
    "count": 2,
    "has_more": false,
    "next_page": 0,
    "items": [
      {
        "media_id": "157336",
        "title": "星际穿越",
        "media_type": 2,
        "year": "2014",
        "poster_url": "https://image.tmdb.org/...",
        "source": 0,
        "source_name": "media_library",
        "tmdb_id": "157336"
      },
      {
        "media_id": "emby_item_abc123",
        "title": "星际穿越",
        "media_type": 2,
        "year": "2014",
        "poster_url": "",
        "source": 1,
        "source_name": "emby",
        "tmdb_id": ""
      }
    ]
  }
}
```

**仅搜索电视剧**：
```bash
bin\bmh-cli.exe --json search --keyword "权力的游戏" --types "3"
```

**翻页**：
```bash
bin\bmh-cli.exe --json search --keyword "漫威" --page 2 --page-size 10
```

---

## 4. play - 播放媒体

### 用途
在爆米花中播放指定的影视内容。支持媒体库和 Emby/Jellyfin/Fnos/Zspace 多数据源。若客户端未运行会自动启动。

### 命令格式
```bash
# 媒体库电影
bin\bmh-cli.exe --json play --media-type 2 --tmdb-id "<TMDB_ID>"

# 媒体库电视剧指定季集
bin\bmh-cli.exe --json play --media-type 3 --tmdb-id "<TMDB_ID>" --season <N> --episode <N>

# Emby/Jellyfin/Fnos/Zspace 播放
bin\bmh-cli.exe --json play --media-type <2|3> --source <1|2|3|4> --media-id "<ITEM_ID>"
```

### 参数

| 参数 | 缩写 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `--media-type` | `-m` | int | ✅ | `2` = 电影，`3` = 电视剧 |
| `--tmdb-id` | `-i` | string | 媒体库时必填 | TMDB ID |
| `--season` | `-s` | int | 媒体库电视剧时必填 | 季号（从 1 开始） |
| `--episode` | `-e` | int | 媒体库电视剧时必填 | 集号（从 1 开始） |
| `--source` | — | int | Emby/Jellyfin/Fnos/Zspace 时必填 | `1`=emby, `2`=jellyfin, `3`=fnos, `4`=zspace |
| `--media-id` | — | string | Emby/Jellyfin/Fnos/Zspace 时必填 | 该源的 item ID |

### 参数规则

**媒体库播放**（`--source` 不填或为 0）：
- `--media-type` 只接受整数 `2` 或 `3`
- `--season` 和 `--episode` 必须同时提供或都不提供
- 电视剧（`--media-type 3`）必须指定 `--season` 和 `--episode`
- 电影（`--media-type 2`）不需要 `--season` 和 `--episode`

**Emby/Jellyfin/Fnos/Zspace 播放**（`--source` 为 1/2/3/4）：
- 必须提供 `--source` 和 `--media-id`
- 不需要 `--tmdb-id`、`--season`、`--episode`
- `--media-id` 来自 search 结果的 `media_id`（emby/jellyfin/fnos/zspace 来源）或 episodes 返回的 `episodes[].media_id`

### 返回结构
```json
{
  "success": true,
  "data": {
    "accepted": boolean,
    "mediaType": number,
    "tmdbId": string,
    "season": number,
    "episode": number
  }
}
```

### 示例

**播放电影**：
```bash
bin\bmh-cli.exe --json play --media-type 2 --tmdb-id "157336"
```

```json
{
  "success": true,
  "data": {
    "accepted": true,
    "mediaType": 2,
    "tmdbId": "157336",
    "season": 0,
    "episode": 0
  }
}
```

**播放电视剧**：
```bash
bin\bmh-cli.exe --json play --media-type 3 --tmdb-id "1399" --season 3 --episode 9
```

```json
{
  "success": true,
  "data": {
    "accepted": true,
    "mediaType": 3,
    "tmdbId": "1399",
    "season": 3,
    "episode": 9
  }
}
```

---

## 5. episodes - 获取剧集信息

### 用途
获取指定电视剧的季度和剧集信息，包括每季有哪些集、哪些集有可用资源。支持媒体库和 Emby/Jellyfin/Fnos/Zspace 多数据源。适合在播放电视剧前了解可用集数。若客户端未运行会自动启动。

### 命令格式
```bash
# 媒体库
bin\bmh-cli.exe --json episodes --tmdb-id "<TMDB_ID>"

# Emby/Jellyfin/Fnos/Zspace
bin\bmh-cli.exe --json episodes --source <1|2|3|4> --media-id "<SERIES_ID>"
```

### 参数

| 参数 | 缩写 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `--tmdb-id` | `-i` | string | 媒体库时必填 | 电视剧的 TMDB ID |
| `--source` | — | int | Emby/Jellyfin/Fnos/Zspace 时必填 | `1`=emby, `2`=jellyfin, `3`=fnos, `4`=zspace |
| `--media-id` | — | string | Emby/Jellyfin/Fnos/Zspace 时必填 | 电视剧的 series ID |

### 返回结构（媒体库）
```json
{
  "success": true,
  "data": {
    "tmdb_id": string,
    "name": string,
    "total_seasons": number,
    "only_one_season": boolean,
    "season_index_list": [number],
    "seasons": [
      {
        "index": number,
        "name": string,
        "short_name": string,
        "total_episodes": number,
        "available_episodes": number,
        "episodes": [
          {
            "index": number,
            "name": string,
            "has_source": boolean
          }
        ]
      }
    ]
  }
}
```

### 返回结构（Emby/Jellyfin/Fnos/Zspace）
```json
{
  "success": true,
  "data": {
    "source": string,
    "media_id": string,
    "name": string,
    "total_seasons": number,
    "only_one_season": boolean,
    "seasons": [
      {
        "index": number,
        "name": string,
        "short_name": string,
        "total_episodes": number,
        "available_episodes": number,
        "episodes": [
          {
            "index": number,
            "name": string,
            "media_id": string,
            "has_source": boolean
          }
        ]
      }
    ]
  }
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `source` | （Emby/Jellyfin/Fnos/Zspace 返回）来源名称：`emby` / `jellyfin` / `fnos` / `zspace` |
| `media_id` | （Emby/Jellyfin/Fnos/Zspace 返回）电视剧 series ID |
| `total_seasons` | 总季数 |
| `only_one_season` | 是否只有一季 |
| `season_index_list` | （媒体库返回）可用季号列表 |
| `seasons[].index` | 季号 |
| `seasons[].total_episodes` | 该季总集数 |
| `seasons[].available_episodes` | 该季有资源的集数 |
| `seasons[].episodes[].index` | 集号 |
| `seasons[].episodes[].name` | 集名 |
| `seasons[].episodes[].media_id` | （Emby/Jellyfin/Fnos/Zspace 返回）**该集的 item ID，直接用于 `play --source X --media-id`** |
| `seasons[].episodes[].has_source` | 该集是否有可播放资源 |

### 使用场景
1. **播放电视剧前**：先调用 `episodes` 查看哪些季和集有资源，再调用 `play` 播放
2. **用户未指定季集时**：查询后展示可用季集列表供用户选择
3. **检查资源可用性**：通过 `has_source` 字段判断哪些集可以播放

### 示例

```bash
bin\bmh-cli.exe --json episodes --tmdb-id "1399"
```

```json
{
  "success": true,
  "data": {
    "tmdb_id": "1399",
    "name": "权力的游戏",
    "total_seasons": 8,
    "only_one_season": false,
    "season_index_list": [1, 2, 3, 4, 5, 6, 7, 8],
    "seasons": [
      {
        "index": 1,
        "name": "第 1 季",
        "short_name": "S1",
        "total_episodes": 10,
        "available_episodes": 10,
        "episodes": [
          { "index": 1, "name": "凛冬将至", "has_source": true },
          { "index": 2, "name": "国王大道", "has_source": true }
        ]
      }
    ]
  }
}
```

---

## 通用规则

### JSON 输出模式
所有命令都必须带 `--json` 参数以获取 JSON 格式输出。

### 响应格式

**成功响应**：
```json
{
  "success": true,
  "data": { ... }
}
```

**失败响应**：
```json
{
  "success": false,
  "error": {
    "code": string,
    "message": string
  }
}
```

### 编码
- 输出编码：UTF-8
- 支持中文搜索和路径

### 性能

| 命令 | 预期耗时 |
|------|---------|
| doctor | < 200ms |
| start（已运行） | < 100ms |
| start（需启动） | 3-15s |
| search | 500ms-2s |
| play | 200ms-1s |
| episodes | 500ms-2s |
