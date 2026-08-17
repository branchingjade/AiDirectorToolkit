# 剪映 draft_content.json 结构详解（2026-08 本机实测）

## 文件位置与加密判定

- 草稿根：`%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft\`
- 每个草稿一个目录（数字名或项目名），含 `draft_content.json`（时间线主文件）、`draft_meta_info.json`（元数据，同样可能加密）、`crypto_key_store.dat`（密钥文件）、`.backup/`、素材目录 `materials/video|audio|image/`
- **明文判定**：文件首字符为 `{` 即明文 JSON；否则是加密的 base64 乱码
- **加密回退候选**（按序尝试，取首个以 `{` 开头的）：
  1. `template.json`
  2. `template.json.bak`（实测 808KB，含完整时间线，是最可靠回退）
  3. `draft_content.json.bak`
  4. `template-2.tmp`
- 组合预设/复合片段会引用 `subdraft\<UUID>\draft_content.json`（subdraft 实测明文）
- 剪映内"保存为预设"产物：`...\User Data\Presets\Combination\Presets\<预设名>\preset_draft\draft_content.json`（**明文**，素材复制到 `Presets\Combination\Resources\`，hash 文件名）

## 顶层字段

```
fps: float（老草稿可能缺失 → 需从素材推断或默认 30）
duration: int（微秒）
canvas_config: {width, height, ratio, background}（如 720x1280 竖屏）
draft_type: "video"
version: int（如 360000）| new_version: str（如 "75.0.0"）
tracks: [...] | materials: {...} | keyframes / group_container / relationships
```

## materials 结构

键极多（ai_text_effects / audios / images / texts / stickers / videos / transitions / audio_fades / speeds / canvases / placeholders / ...），多数为空列表。**只有实际使用的类型有内容。**

### videos 元素（~80 键，关键字段）
```
id: str（UUID，segment.material_id 引用它）
path: str — 占位符相对路径，如 "##_draftpath_placeholder_0E685133-..._##/materials/video/46-1 1.1.mp4"
        占位符 = 草稿目录绝对路径；也可能是纯相对路径 "materials/video/xxx.mp4"
media_path / material_url / local_material_id: 常为空
duration: int（微秒）| width / height: int
material_name: str | type: "video" 或 "photo"（定格图！仍在 videos 列表里）
has_audio: bool | fps: 常为 None
```

### texts 元素（字幕/花字）
```
id: str | type: "subtitle"
content: str — **JSON 字符串**，解析后：
    { "text": "字幕正文", "styles": [{"fill":{...}, "font":{...}, "size": N, "strokes":[...], "range":...}] }
```

## tracks 结构

```
track: { type: "video"|"text"|"audio"|"filter"|"effect",
         attribute: 1 表示主视频轨（V1），其他视频轨 attribute 不同,
         name, segments: [...] }
segment 关键键：
  id: str | material_id: str（→ materials 查素材）
  source_timerange: {start, duration} — 素材入点/时长（微秒）
  target_timerange: {start, duration} — 时间线位置/时长（微秒）
  speed: float 或 None（None=1.0；变速段有值如 1.1/3.46）
  volume: float | reverse: bool | visible: bool
  clip: {alpha, flip, rotation, scale, transform} — 变换
  render_index / track_render_index / uniform_scale / hdr_settings / extra_material_refs
```

## 转换要点（写入 FCPXML 时）

- 时间格式：FCPXML 用有理数秒 `f"{us}/1000000s"`，避免帧数换算误差
- 素材 → `<asset id="aN" ...><media-rep kind="original-media" src="file:///绝对路径"/></asset>`（路径须 urllib.parse.quote 编码，Windows 反斜杠转正斜杠）
- 主视频轨（attribute==1）→ `<spine>`；叠加视频/音频/字幕 → `<sync><lane>...</lane></sync>`
- 变速：clip 内嵌 `<rate><value>N</value></rate>`（FCPXML 1.10 变速写法）
- 定格 photo：hasVideo="true" 当视频素材处理
- 字幕：SRT 输出（`hh:mm:ss,mmm` 时间戳，拖入达芬奇自动成字幕轨）比 FCPXML `<title>` 可靠
- 画布 720x1280 → format width/height；frameDuration = 1000000000//fps / 1000000000s
