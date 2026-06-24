---
name: netease-baomihua-player
display_name: "网易爆米花播放器控制"
description: "通过 bmh-cli 命令行工具操作网易爆米花 Windows 客户端，支持搜索媒体库和播放影视内容。当用户提到：搜索影片、播放电影、播放电视剧、查找视频、网易爆米花、爆米花播放器、媒体库搜索、TMDB、看电影、看剧时使用。"
tags:
  - media-player
  - video-player
  - streaming
  - baomihua
  - netease
  - automation
  - cli-tool
  - 爆米花
  - 播放器
  - 网易爆米花
  - 影视搜索
  - 媒体库
metadata:
  version: "1.2.0"
  platform: "windows"
  category: "media-tools"
  author: "netease-baomihua"
  license: "MIT"
  language: "zh-CN"
  keywords:
    - "爆米花播放器"
    - "网易爆米花"
    - "BaoMiHua"
    - "media player"
    - "video player"
    - "影视搜索"
    - "播放电影"
    - "播放电视剧"
    - "TMDB"
    - "媒体库"
    - "网盘视频"
    - "命令行工具"
    - "自动化"
    - "Emby"
    - "Jellyfin"
    - "Fnos"
    - "Zspace"
    - "极空间"
  features:
    - "自动环境检测和爆米花启动"
    - "媒体库全文搜索（中英文）"
    - "支持电影和电视剧播放"
    - "指定季集播放电视剧"
    - "静默模式自动启动客户端"
    - "AES-128-ECB 本地安全通信"
    - "支持 Emby/Jellyfin/Fnos/Zspace 多数据源搜索"
    - "支持播放 Emby/Jellyfin/Fnos/Zspace 视频"
    - "支持获取 Emby/Jellyfin/Fnos/Zspace 电视剧季集信息"
  use_cases:
    - "搜索并播放电影"
    - "搜索并播放电视剧指定集"
    - "搜索并播放 Emby/Jellyfin/Zspace 中的影视内容"
    - "检查爆米花客户端运行状态"
    - "自动化影视播放流程"
  dependencies:
    - "网易爆米花客户端 (https://baomihua.163.com)"
  requirements:
    - "Windows 10/11 (x64)"
    - "网易爆米花已安装"
  performance:
    typical_latency: "< 500ms"
    success_rate: "> 95%"
---

# 网易爆米花播放器控制 Skill

本 skill 通过 `bmh-cli.exe` 命令行工具控制网易爆米花 Windows 客户端，支持环境检测、客户端启动、影视搜索和播放功能。

---

## 适用边界

这个 skill 只解决"通过 `bmh-cli.exe` 控制网易爆米花客户端"。

- 用户要搜索或播放影视内容：使用这个 skill
- 用户只是在问开发原理、接口设计、C++/C# 代码：优先做常规代码分析，不要硬套本 skill
- 用户既要操作客户端又要解释 CLI 行为：先按本 skill 完成操作，再补说明

---

## 目录结构

```
netease-baomihua-player/
├── SKILL.md              # 本文档
└── bin/
    └── bmh-cli.exe       # 爆米花 CLI 工具
```

---

## 前置条件

1. **操作系统**：Windows 10/11 (x64)
2. **依赖软件**：已安装网易爆米花客户端（从 https://baomihua.163.com 下载）
3. **CLI 工具**：`bin\bmh-cli.exe` 已包含在本 skill 中

---

## 默认工作方式

除非用户明确限制，否则始终按下面顺序执行：

1. 解析意图：搜索 / 播放 / 查看剧集 / 检查状态
2. 执行 `doctor` 确认客户端状态
3. 若未运行，执行 `start` 自动启动
4. 根据意图执行 `search`、`episodes` 或 `play`
5. 播放电视剧时，若用户未指定季集，先用 `episodes` 查询可用集数再让用户选择
6. 只使用真实 CLI 输出组织回复，不脑补结果

如果某一步缺少必要信息，优先通过 CLI 获取；只有 CLI 也无法消除歧义时才向用户确认。

---

## 使用模式识别

| 用户意图 | 触发关键词 | 执行工作流 |
|---------|-----------|-----------|
| 搜索影视 | "搜索XXX"、"找一下XXX"、"有没有XXX" | 工作流1：搜索媒体 |
| 播放影视 | "播放XXX"、"看XXX"、"放XXX" | 工作流2：搜索+播放 |
| 查看剧集 | "有哪些集"、"哪些季"、"剧集列表" | 工作流3：查看剧集信息 |
| 检查状态 | "爆米花是否运行"、"检查爆米花" | 单步：环境检测 |

---

## 核心工作流

### 工作流1：搜索媒体

**适用场景**：用户想搜索影视内容

**执行步骤**：

1. **环境检测**
   ```bash
   bin\bmh-cli.exe --json doctor
   ```
   - 检查返回的 `data.status` 字段
   - 若为 `ready`，继续下一步
   - 若为 `not_installed`，提示用户安装爆米花（https://baomihua.163.com）
   - 若为 `not_running`，执行 `bin\bmh-cli.exe --json start` 启动客户端
   - 若为 `service_unavailable`，提示用户等待 3-5 秒或重启爆米花

2. **执行搜索**
   ```bash
   bin\bmh-cli.exe --json search --keyword "用户提到的关键词"
   ```

3. **解析并展示结果**
   - 检查 `data.total_count` 获取总数
   - 遍历 `data.items` 数组展示：
     - 标题（title）
     - 类型（media_type）：`2` = 电影，`3` = 电视剧
     - 年份（year）
     - 来源（source_name）：`media_library` / `emby` / `jellyfin` / `fnos` / `zspace`
   - 搜索会同时查询所有数据源（媒体库 + Emby + Jellyfin + Fnos + Zspace），结果合并返回
   - 若 `data.has_more` 为 `true`，提示用户可翻页
   - **重要**：来自 emby/jellyfin/fnos/zspace 的结果，`media_id` 是该源的 item ID（非 TMDB ID），播放时需配合 `--source` 使用

**示例回复**：
```
🔍 为您找到 3 个与"星际穿越"相关的结果：

1. 🎬 星际穿越（2014）— 电影
2. 📺 星际迷航：发现号（2017）— 电视剧
3. 🎬 星际探索（2019）— 电影

需要播放哪一部？
```

---

### 工作流2：播放媒体

**适用场景**：用户想播放某个影视内容

**执行步骤**：

1. **环境检测**（同工作流1步骤1）

2. **确定播放目标**
   - 若用户直接提供了 TMDB ID 和类型，跳到步骤4
   - 否则先搜索：
     ```bash
     bin\bmh-cli.exe --json search --keyword "用户提到的影片名"
     ```

3. **确认播放条目**
   - 若搜索返回多个结果，使用 `ask_user_question` 让用户选择
   - 记录选中条目的 `media_type` 和 `tmdb_id`（若有）

4. **执行播放**
   ```bash
   # 媒体库电影
   bin\bmh-cli.exe --json play --media-type 2 --tmdb-id "550"

   # 媒体库电视剧（指定季集）
   bin\bmh-cli.exe --json play --media-type 3 --tmdb-id "1399" --season 1 --episode 1

   # Emby/Jellyfin/Fnos/Zspace 电影
   bin\bmh-cli.exe --json play --media-type 2 --source 1 --media-id "emby_item_abc123"

   # Emby/Jellyfin/Fnos/Zspace 电视剧（指定某集的 item ID）
   bin\bmh-cli.exe --json play --media-type 3 --source 1 --media-id "emby_episode_xyz"

   # 极空间（zspace）电影
   bin\bmh-cli.exe --json play --media-type 2 --source 4 --media-id "zspace_item_xxx"
   ```

5. **反馈结果**
   - 告知用户播放已开始
   - 显示播放的影片信息

**示例回复**：
```
▶️ 已开始播放电影《星际穿越》
```

```
▶️ 已开始播放电视剧《权力的游戏》第1季第1集
```

---

### 工作流3：查看剧集信息

**适用场景**：用户想知道电视剧有哪些季和集，或哪些集有可播放资源

**执行步骤**：

1. **环境检测**（同工作流1步骤1）

2. **确定目标电视剧**
   - 若用户提供了 TMDB ID，直接使用
   - 否则先搜索确定 TMDB ID

3. **获取剧集信息**
   ```bash
   bin\bmh-cli.exe --json episodes --tmdb-id "<TMDB_ID>"
   ```

4. **展示结果**
   - 列出所有季和可用集数
   - 标注哪些集有资源（`has_source: true`）
   - 如果用户想播放，直接调用 `play` 命令

**示例回复**：
```
📺《我独自升级》共 2 季：

第1季（12集，2集有资源）：
  ✅ 第1集 · 我就是你
  ✅ 第2集 · 如果我有那种力量
  ❌ 第3-9集 · 暂无资源
  ✅ 第10集 · 不够
  ❌ 第11-12集 · 暂无资源

需要播放哪一集？
```

---

## 命令参考

### doctor — 环境检测

检查爆米花客户端的安装和运行状态。

```bash
bin\bmh-cli.exe --json doctor
```

**返回字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | `ready` / `not_running` / `service_unavailable` / `not_installed` |
| `installed` | bool | 是否已安装 |
| `running` | bool | 进程是否在运行 |
| `service_available` | bool | HTTP 服务是否可用 |
| `service_port` | int | 服务端口号（可用时返回） |
| `version` | string | 客户端版本号（可用时返回） |
| `install_path` | string | 安装路径（已安装时返回） |

**返回示例**：
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

### start — 启动客户端

以静默模式启动爆米花客户端（不弹出窗口）。

```bash
bin\bmh-cli.exe --json start
```

- 若客户端已运行，直接返回成功
- 若未运行，自动启动并等待服务就绪（最多 15 秒）
- 若未安装，返回 `APP_NOT_INSTALLED` 错误

**返回示例**：
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

### search — 搜索媒体

在爆米花媒体库中搜索影视内容。

```bash
bin\bmh-cli.exe --json search --keyword "关键词" [--page N] [--page-size N] [--types "2,3"]
```

**参数**：

| 参数 | 缩写 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--keyword` | `-k` | ✅ | — | 搜索关键词（中英文均可） |
| `--page` | `-p` | ❌ | `1` | 页码 |
| `--page-size` | — | ❌ | `20` | 每页数量 |
| `--types` | `-t` | ❌ | `2,3` | 媒体类型筛选，逗号分隔。`2` = 电影，`3` = 电视剧 |

**返回字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_count` | int | 总结果数 |
| `count` | int | 当前页结果数 |
| `has_more` | bool | 是否有下一页 |
| `next_page` | int | 下一页页码（无更多时为 0） |
| `items[]` | array | 结果列表 |
| `items[].media_id` | string | 媒体 ID |
| `items[].title` | string | 标题 |
| `items[].media_type` | int | `2` = 电影，`3` = 电视剧 |
| `items[].year` | string | 上映年份 |
| `items[].poster_url` | string | 海报图片 URL |
| `items[].source` | int | 来源标识（`0`=媒体库, `1`=emby, `2`=jellyfin, `3`=fnos, `4`=zspace） |
| `items[].source_name` | string | 来源名称：`media_library` / `emby` / `jellyfin` / `fnos` / `zspace` |
| `items[].tmdb_id` | string | TMDB ID（仅媒体库来源有值，emby/jellyfin/fnos/zspace 为空） |

**返回示例**：
```json
{
  "success": true,
  "data": {
    "total_count": 3,
    "count": 3,
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

**注意事项**：
- 搜索会**同时查询所有数据源**（媒体库 + Emby + Jellyfin + Fnos + Zspace），结果合并返回
- 搜索会自动检测客户端状态，若未运行会自动启动
- 关键词支持中英文模糊匹配
- `--types "2"` 仅搜索电影，`--types "3"` 仅搜索电视剧
- 来自 emby/jellyfin/fnos/zspace 的结果，播放时需使用 `--source` + `--media-id`，而非 `--tmdb-id`

---

### play — 播放媒体

在爆米花中播放指定的影视内容。支持媒体库和 Emby/Jellyfin/Fnos/Zspace 多数据源。

```bash
# 媒体库播放
bin\bmh-cli.exe --json play --media-type <2|3> --tmdb-id "ID" [--season N] [--episode N]

# Emby/Jellyfin/Fnos/Zspace 播放
bin\bmh-cli.exe --json play --media-type <2|3> --source <1|2|3|4> --media-id "ITEM_ID"
```

**参数**：

| 参数 | 缩写 | 必填 | 说明 |
|------|------|------|------|
| `--media-type` | `-m` | ✅ | 媒体类型。`2` = 电影，`3` = 电视剧 |
| `--tmdb-id` | `-i` | 媒体库时必填 | TMDB ID（媒体库来源使用） |
| `--season` | `-s` | 媒体库电视剧时必填 | 季号（从 1 开始） |
| `--episode` | `-e` | 媒体库电视剧时必填 | 集号（从 1 开始） |
| `--source` | — | Emby/Jellyfin/Fnos/Zspace 时必填 | 数据源：`1`=emby, `2`=jellyfin, `3`=fnos, `4`=zspace |
| `--media-id` | — | Emby/Jellyfin/Fnos/Zspace 时必填 | 该源的 item ID |

**使用规则**：

**媒体库播放**（`--source` 不填或为 0）：
- 电影：`--media-type 2` + `--tmdb-id`
- 电视剧：`--media-type 3` + `--tmdb-id` + `--season` + `--episode`

**Emby/Jellyfin/Fnos/Zspace 播放**（`--source` 为 1/2/3/4）：
- 电影或电视剧：`--media-type` + `--source` + `--media-id`
- 不需要 `--tmdb-id`、`--season`、`--episode`
- `--media-id` 来自 search 结果中的 `media_id` 字段（emby/jellyfin/fnos/zspace 来源），或 episodes 结果中每集的 `media_id`

**返回示例**：
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

**注意事项**：
- 播放会自动检测客户端状态，若未运行会自动启动
- `accepted: true` 表示播放指令已被接受，客户端正在处理
- 如果媒体库中没有对应内容，返回 `MEDIA_NOT_FOUND` 错误
- Emby/Jellyfin/Fnos/Zspace 播放时，电视剧无需指定季集号，`--media-id` 直接指向某一集的 item ID

---

### episodes — 获取剧集信息

获取电视剧的季度和剧集信息，包括资源可用性。支持媒体库和 Emby/Jellyfin/Fnos/Zspace 多数据源。

```bash
# 媒体库
bin\bmh-cli.exe --json episodes --tmdb-id "<TMDB_ID>"

# Emby/Jellyfin/Fnos/Zspace
bin\bmh-cli.exe --json episodes --source <1|2|3|4> --media-id "<SERIES_ID>"
```

**参数**：

| 参数 | 缩写 | 必填 | 说明 |
|------|------|------|------|
| `--tmdb-id` | `-i` | 媒体库时必填 | 电视剧的 TMDB ID |
| `--source` | — | Emby/Jellyfin/Fnos/Zspace 时必填 | 数据源：`1`=emby, `2`=jellyfin, `3`=fnos, `4`=zspace |
| `--media-id` | — | Emby/Jellyfin/Fnos/Zspace 时必填 | 电视剧的 series ID |

**返回字段（媒体库）**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `tmdb_id` | string | TMDB ID |
| `name` | string | 剧名 |
| `total_seasons` | int | 总季数 |
| `only_one_season` | bool | 是否只有一季 |
| `season_index_list` | int[] | 可用季号列表 |
| `seasons[].index` | int | 季号 |
| `seasons[].total_episodes` | int | 该季总集数 |
| `seasons[].available_episodes` | int | 有资源的集数 |
| `seasons[].episodes[].index` | int | 集号 |
| `seasons[].episodes[].name` | string | 集名 |
| `seasons[].episodes[].has_source` | bool | 是否有可播放资源 |

**返回字段（Emby/Jellyfin/Fnos/Zspace）**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `source` | string | 来源名称：`emby` / `jellyfin` / `fnos` / `zspace` |
| `media_id` | string | 电视剧 series ID |
| `name` | string | 剧名 |
| `total_seasons` | int | 总季数 |
| `only_one_season` | bool | 是否只有一季 |
| `seasons[].index` | int | 季号 |
| `seasons[].total_episodes` | int | 该季总集数 |
| `seasons[].available_episodes` | int | 有资源的集数 |
| `seasons[].episodes[].index` | int | 集号 |
| `seasons[].episodes[].name` | string | 集名 |
| `seasons[].episodes[].media_id` | string | **该集的 item ID（用于 play 命令的 `--media-id`）** |
| `seasons[].episodes[].has_source` | bool | 是否有可播放资源 |

**注意事项**：
- 会自动检测客户端状态，若未运行会自动启动
- 媒体库来源：`has_source: true` 的集才能通过 `play --tmdb-id` 播放
- Emby/Jellyfin/Fnos/Zspace 来源：每集返回 `media_id`，可直接用于 `play --source X --media-id <media_id>` 播放
- 媒体库的 `tmdb_id` 可从 `search` 结果的 `media_id` 字段获取
- Emby/Jellyfin/Fnos/Zspace 的 `media-id` 可从 `search` 结果的 `media_id` 字段获取（对应来源的电视剧 item ID）

---

## 错误处理

所有命令返回统一 JSON 格式：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

### 错误码速查

| 错误码 | 含义 | 处理方式 |
|--------|------|---------|
| `APP_NOT_INSTALLED` | 爆米花未安装 | 提示用户从 https://baomihua.163.com 下载安装 |
| `APP_OFFLINE` | 客户端未运行且无法连接 | 执行 `start` 命令启动 |
| `SERVICE_UNAVAILABLE` | 服务不可用 | 等待 3-5 秒重试，或提示用户重启爆米花 |
| `START_TIMEOUT` | 启动超时（15秒内服务未就绪） | 提示用户手动启动爆米花 |
| `LAUNCH_FAILED` | 启动进程失败 | 检查安装路径是否正确 |
| `INVALID_PARAMS` | 参数错误 | 检查命令参数是否完整正确 |
| `MEDIA_NOT_FOUND` | 媒体未找到 | 检查 TMDB ID 是否正确，或媒体库中是否有该内容 |
| `UNAUTHORIZED` | 认证失败 | CLI 工具版本与客户端不匹配，需更新 |
| `TIMEOUT` | 请求超时 | 重试请求 |
| `BACKEND_ERROR` | 后端错误 | 重试或提示用户重启爆米花 |

---

## media_type 映射

`play --media-type` 只接受整数 `2`（电影）或 `3`（电视剧）。

| 用户表述 | media_type 值 |
|---------|--------------|
| 电影、影片、movie | `2` |
| 电视剧、剧集、美剧、日剧、韩剧、番剧、动漫、series、tv | `3` |

禁止：将字符串 `"movie"` / `"series"` 传给 `--media-type`，CLI 只接受整数。

---

## 播放前检查清单

执行 `play` 前逐条确认：

**媒体库播放**：
- [ ] `media_type` 是整数 `2` 或 `3`？
- [ ] `tmdb_id` 有值且来自可靠来源（搜索结果或用户明确提供）？
- [ ] 若为电视剧（`media_type=3`）：`--season` 和 `--episode` 都已填写？
- [ ] 客户端状态已确认为 `ready`？（若不确定，先执行 `doctor`）

**Emby/Jellyfin/Fnos/Zspace 播放**：
- [ ] `media_type` 是整数 `2` 或 `3`？
- [ ] `--source` 是 `1`（emby）、`2`（jellyfin）、`3`（fnos）或 `4`（zspace）？
- [ ] `--media-id` 有值且来自搜索结果的 `media_id` 或剧集查询的 `episodes[].media_id`？
- [ ] 客户端状态已确认为 `ready`？（若不确定，先执行 `doctor`）

---

## 实现要点

### 1. 命令执行
- 使用 `run_terminal_cmd` 工具执行命令
- 所有命令都带 `--json` 参数以获取结构化输出
- 命令路径使用 `bin\bmh-cli.exe`（Windows 反斜杠）

### 2. JSON 解析
- 所有命令返回统一格式：
  ```json
  {
    "success": true/false,
    "data": { ... },
    "error": { ... }
  }
  ```
- 必须先检查 `success` 字段再处理数据

### 3. 自动启动
- `search` 和 `play` 命令内置自动启动逻辑
- 若客户端未运行，会自动执行静默启动并等待服务就绪
- 无需手动先执行 `start`，但建议先 `doctor` 获取状态信息

### 4. 用户交互
- 使用 `ask_user_question` 工具让用户选择：
  - 搜索返回多个结果时选择条目
  - 电视剧未指定季集时询问
- 当搜索结果含 `poster_url` 时，可用 Markdown 图片增强展示

### 5. 友好反馈
- 将技术信息转化为用户友好的语言
- 根据 `media_type` 调整称呼：`2` 称"电影"，`3` 称"电视剧"
- 默认说"已开始播放《标题》"，不暴露内部参数和技术细节
- 只有在需要排障时才展示 `doctor` 的详细状态信息

---

## 用户可见话术

对用户回复时，不要暴露实现细节，优先使用自然表达。

优先使用：
- "已开始播放《星际穿越》"
- "已开始播放电视剧《权力的游戏》第1季第1集"
- "为您找到了 5 个与'漫威'相关的结果"

避免使用：
- "已向 HTTP Bridge 发送 play 请求"
- "TMDB ID 157336 的媒体已开始播放"
- "通过端口 52020 连接到爆米花服务"
- 在 `media_type=3` 时说"已播放电影"
- 在 `media_type=2` 时说"已播放电视剧"

---

## 注意事项

1. ⚠️ **始终使用 `--json` 参数**确保输出可解析
2. ⚠️ **先执行 `doctor`** 确认服务可用后再执行其他命令（推荐但非必须，search/play 内置自动启动）
3. ⚠️ **`--season` 和 `--episode` 必须成对**使用
4. ⚠️ **`media_type` 只接受整数** `2` 或 `3`
5. ⚠️ **Windows 环境**下使用反斜杠 `\` 作为路径分隔符
6. ⚠️ **不得伪造 CLI 输出**，必须使用真实执行结果
7. ⚠️ **不得假设客户端正在运行**，必须先验证状态

---

## 性能预期

| 操作 | 预期耗时 |
|------|---------|
| doctor | < 200ms（端口扫描） |
| start（已运行） | < 100ms |
| start（需启动） | 3-15s（等待服务就绪） |
| search | 500ms-2s |
| play | 200ms-1s |

---

## 示例对话

### 搜索影视

**用户**：帮我搜一下有没有星际穿越

**执行**：
```bash
bin\bmh-cli.exe --json doctor
bin\bmh-cli.exe --json search --keyword "星际穿越"
```

**回复**：
```
🔍 为您找到 2 个与"星际穿越"相关的结果：

1. 🎬 星际穿越（2014）— 电影（媒体库）
2. 🎬 星际穿越（2014）— 电影（Emby）

需要播放哪一个？
```

### 播放媒体库电影

**用户**：播放第一个

**执行**：
```bash
bin\bmh-cli.exe --json play --media-type 2 --tmdb-id "157336"
```

**回复**：
```
▶️ 已开始播放电影《星际穿越》
```

### 播放 Emby 电影

**用户**：播放 Emby 里的那个

**执行**：
```bash
bin\bmh-cli.exe --json play --media-type 2 --source 1 --media-id "emby_item_abc123"
```

**回复**：
```
▶️ 已开始播放电影《星际穿越》
```

### 播放电视剧指定集（媒体库）

**用户**：播放权力的游戏第三季第九集

**执行**：
```bash
bin\bmh-cli.exe --json doctor
bin\bmh-cli.exe --json search --keyword "权力的游戏"
bin\bmh-cli.exe --json play --media-type 3 --tmdb-id "1399" --season 3 --episode 9
```

**回复**：
```
▶️ 已开始播放电视剧《权力的游戏》第3季第9集
```

### 播放 Emby 电视剧（先查剧集再播放）

**用户**：播放 Emby 里的权力的游戏第一集

**执行**：
```bash
bin\bmh-cli.exe --json search --keyword "权力的游戏"
# 从搜索结果中找到 emby 来源的 media_id: "series_12345"
bin\bmh-cli.exe --json episodes --source 1 --media-id "series_12345"
# 从剧集信息中找到第1季第1集的 media_id: "ep_001"
bin\bmh-cli.exe --json play --media-type 3 --source 1 --media-id "ep_001"
```

**回复**：
```
▶️ 已开始播放电视剧《权力的游戏》第1季第1集
```

### 播放极空间（ZSpace）电影

**用户**：播放极空间里的星际穿越

**执行**：
```bash
bin\bmh-cli.exe --json search --keyword "星际穿越"
# 从搜索结果中找到 zspace 来源的 media_id: "zspace_item_xxx"
bin\bmh-cli.exe --json play --media-type 2 --source 4 --media-id "zspace_item_xxx"
```

**回复**：
```
▶️ 已开始播放电影《星际穿越》
```

---

## 约束

- 不得伪造 CLI 输出
- 不得假设客户端正在运行，必须先验证状态
- 不得将非 TMDB ID 传给 `--tmdb-id`
- 不得将 TMDB ID 传给 `--media-id`（`--media-id` 仅用于 emby/jellyfin/fnos/zspace 的 item ID）
- 不得将 emby/jellyfin/fnos/zspace 的 item ID 传给 `--tmdb-id`
- 未经用户明确要求，不修改用户配置
- media_type 必须传整数，不得传字符串
- `--source` 必须传整数 `1`、`2`、`3` 或 `4`（分别对应 emby、jellyfin、fnos、zspace）

---

## 技术规格

| 项目 | 说明 |
|------|------|
| CLI 工具 | bmh-cli.exe v1.2.0 |
| 通信协议 | HTTP (localhost) |
| 端口范围 | 52020-52029 |
| 认证方式 | AES-128-ECB (BaoMiHua-Auth-Code) |
| 输出格式 | JSON |
| 支持平台 | Windows 10/11 (x64) |

---

## 版本历史

### v1.2.0
- ✨ 新增极空间（Zspace）数据源支持：`--source 4` 用于 search / play / episodes
- ✨ 搜索同时查询媒体库 + Emby + Jellyfin + Fnos + Zspace 五类数据源
- 📦 包含 bmh-cli.exe v1.2.0

### v1.1.0
- ✨ 搜索支持多数据源：同时搜索媒体库 + Emby + Jellyfin + Fnos，结果合并返回
- ✨ 播放支持 Emby/Jellyfin/Fnos：新增 `--source` 和 `--media-id` 参数
- ✨ 剧集查询支持 Emby/Jellyfin/Fnos：获取季集信息，每集返回 `media_id` 供播放使用
- ✅ 搜索结果新增 `source_name` 和 `tmdb_id` 字段
- ✅ Emby/Jellyfin/Fnos 剧集返回每集的 `media_id`
- ⚡ 搜索并行查询所有数据源，总耗时 ≈ 最慢的那个源（而非串行累加）
- 📦 包含 bmh-cli.exe v1.1.0

### v1.0.0
- ✨ 初始版本
- ✅ 支持环境检测（doctor）
- ✅ 支持静默启动（start）
- ✅ 支持媒体搜索（search）
- ✅ 支持影视播放（play）
- ✅ 支持剧集查询（episodes）
- 📦 包含 bmh-cli.exe v1.0.0

---

## 许可与支持

本 skill 依赖网易爆米花客户端，使用前请确保已安装官方客户端。

- 官方网站：https://baomihua.163.com
- CLI 工具版本：1.2.0
- Skill 版本：1.2.0
