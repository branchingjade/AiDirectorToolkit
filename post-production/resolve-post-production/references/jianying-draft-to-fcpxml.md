# 剪映草稿 → 达芬奇 FCPXML 转换（2026-08-11 大版本修订：全量 51 集实测打通）

完整可运行转换器（用户工作区 git 仓库）：`C:\Users\HMSJ\Documents\Hermes\scripts\jianying2davinci.py`（2026-08-11 支持 `--no-audio` 纯视频 / `--audio-only` 纯音频输出，默认全量视频+音频）
批量导入：`batch_import_manlv.py`（转换→复制→清旧素材→导时间线→MoveClips 时间线对象）
验证脚本思路见 SKILL.md「FCPXML 导入兼容性」节。

## 剪映草稿文件结构（Windows）

草稿目录：`%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft\<草稿名>\`

- **`draft_content.json` 大部分是明文**，个别草稿加密（base64 乱码开头），此时用 **`template.json.bak` 明文备份**回退。回退优先级：`template.json` → `template.json.bak` → `draft_content.json.bak` → `template-2.tmp`
- 素材路径占位符：`##_draftpath_placeholder_XXX_##/materials/video/xxx.mp4` → 替换为草稿目录绝对路径
- 时间单位：**微秒（μs）**；**顶层 `fps: 50`（子帧精度）**——但**时间线仍输出 25fps**（`frameDuration="1/25s"`）+ **主轨缝合并**（见下），不要升 50fps 时间线（50fps 下 lane>0 clip offset 解析错位，V2 叠加轨跑到 2 倍位置——本会话 2026-08-11 实测，曾把第2集 V2 的 75.6s 片段错放到 151.3s）；`canvas_config.width/height` 给画布

## JSON 结构要点

- `materials.videos[]`：视频素材（含 type=photo 定格图）；`materials.audios[]`：音频素材（**type 可能是 `extract_music`/`music`**，必须归一化）
- `materials.texts[]`：字幕，`content` 是 JSON 字符串，`json.loads` 后取 `text`
- `tracks[]`：轨道，`type` ∈ video/text/audio/filter/effect；`segments[]` 每段有 `material_id`/`source_timerange`/`target_timerange`/`speed`/`visible`
- **多视频轨判定（重要修正）**：剪映多个视频轨的 `attribute` 可能**全为 1**（第6集 4 轨全 attribute=1）——**不能按 attribute 分类轨道，必须按轨道数组顺序分 lane**（第0条=主轨 lane=0，后续=叠加轨 lane=1/2/3）

## FCPXML 生成铁律（达芬奇 21 实测，缺一不可）

### 时间单位：25fps 时间线 + 主轨缝合并（本会话两轮试错后的最终定案）

0. **时间线 fps = 25（保持）**：剪映草稿顶层 `fps: 50`（子帧 20ms）是编辑精度，不是导出帧率。**不要升 50fps 时间线**——2026-08-11 实测：50fps 时间线下 lane>0 clip 的 offset 被达芬奇按 25fps 帧语义解析（50/25 倍错位），第2集 V2 叠加轨 2 个片段从正确的 75.6s/77.6s 错放到 151.3s/155.3s（2 倍位置）。**若直接 round 到 25fps 帧**（round(secs*25)），相邻片段会因剪映半帧位置（134.5/135.5）取整出 1 帧缝（第2集 9-10 处，用户目视「很多间隙」）。
1. **duration 必须写有理数**（帧数/25s），**禁止浮点秒**（4.000000s）——浮点秒被达芬奇解析成 **1 帧**（「每个片段只有一帧」的根因，用户两次抓出）。asset 的 duration 同理。
2. **offset/start 用 25fps 帧格式**：offset="{int(round(offset_secs*25))}/25s"；**主轨缝合并**（消 1 帧缝且不升 50fps）：生成时主轨按 offset 排序，off_f=round(secs*25)、dur_f=round(dur*25)，若 off_f > prev_end（缝）或 < prev_end（叠）都吸附为 prev_end，然后 prev_end = off_f + dur_f 接力 → 间隙 0 处。代价：片段位置最大偏移 4 帧（160ms，平均 1.2 帧），切换点肉眼不可见，可接受。
3. **asset duration 必须 ≥ clip 用时长**：向上取整 max(int(total_dur)+1, 1)，否则 clip 超出 asset 声明 → 导入失败。
4. **lane>0（叠加轨）clip 的 offset 也用 25fps 帧格式**——达芬奇 lane offset 只认 25fps 帧语义，微秒有理数/50fps 帧格式都会错位（见 SKILL.md 表）。

### 结构与属性

4. **format 必须有 name**：`<format id="r0" name="FFVideoFormatRateUndefined" frameDuration="1/25s" width="720" height="1280"/>`；**每素材独立 format**（混帧率共用 format 达芬奇崩溃）——但实测简单场景（单 format r0 全引用）可用，不强制每素材一个
5. **多轨 = clip 级 `lane` 属性**：主轨 clip 不写 lane（默认 0），叠加轨写 `lane="1"/"2"/"3"`。**不用 `<sync>/<lane>/<spine>` 元素**（达芬奇 21 实测丢弃/拒导）。lane 属性方案 V1+V2+V3+V4 全部导入成功
6. **隐藏素材 → `enabled="0"`**：segment `visible=false` → clip `enabled="0"`（第6集 7 个隐藏素材实测生效）
7. **变速 rate 必须带 timebase**：`<rate><value>0.9</value><timebase>25</timebase></rate>`（**timebase 必须与时间线 fps 一致=25**）——**不带 timebase 的 rate 片段不套底**（实测 1/36 vs 36/36）！这是变速+套底两全的唯一写法
8. **src URI 冒号保留**：`file://localhost/` + `quote(p, safe='/:')`（达芬奇导出用 `file://localhost/` + 中文百分号编码）
9. **asset 布尔必须 1/0**：`hasVideo="1"`、`hasAudio="1" audioChannels="2" audioSources="1"`——`"true"/"false"` 达芬奇静默丢素材。**视频素材 asset 用 `hasAudio="0" audioSources="0"`**（丢视频自带音频、只留剪映音频轨，第1集实测 A1=0 视频 52/52 正常——注意这与旧结论"hasAudio 必须为 1"相反，见音频节）
10. **spine 按 offset 排序**：同轨 clip offset 必须连续（不能重叠）；时间线名唯一（重名 → 返回 None 不报错）
11. **clip 需要 `tcFormat="NDF"` + `<adjust-transform scale="1 1" position="0 0" anchor="0 0"/>`**（达芬奇格式），否则解析异常只进第一段

- **所有 clip（视频主轨/叠加轨/音频）统一 25fps 帧格式 offset**（`offset="0/25s"`、`duration="1450/25s"`）——达芬奇 lane offset 只认 25fps 帧语义（微秒有理数会错位，50fps 时间线更会 2 倍错位，见上）。主轨缝合并见「时间单位」节。**变速 rate 的 timebase = 25**（与时间线 fps 一致），音频无变速。\n\n### 音频：正确格式 = asset-clip + audioRole 直接放 spine（2026-08-11 第1集实测 4 轨全进）

**`<gap>` 包裹音频 = 彻底否定**（达芬奇 FCPXML 导入器硬限制，A1=0；混录音频从未真正进入 A 轨）。**`<clip><audio>` 简例可但全集不稳定**（V1 27 段/A1=0）。**正确格式**（第1集 4 条音频轨全部实测导入）：

- **音频 clip = `<asset-clip>` 直接放 spine**，无 gap、无 lane、**带 `audioRole="dialogue"`**（mult_seg 验证的格式）：
  `<asset-clip tcFormat="NDF" offset="0/25s" start="4/25s" name="1.wav" ref="r54" enabled="1" duration="1450/25s" format="r0" audioRole="dialogue"/>`
- **视频素材 asset 用 `hasAudio="0" audioSources="0"`** → 视频自带音频不进入 A 轨（第1集实测 A1=0，视频 52/52 正常套底）。**推翻旧结论"hasAudio 必须为 1"**——`hasAudio="0"` 才是丢视频自带音频、只留剪映音频轨的正确写法
- 音频 clip 的 offset = 剪映音频轨 target start（无 lane，全部音频 clip 平铺 spine，达芬奇按 audioRole 自动分轨——第1集 A1 混录/A2 音效/A3 音乐/A4 音乐 与剪映 4 条音频轨一一对应）
- 音量：剪映 segment `volume`（线性增益）→ 达芬奇无直接 clip 属性可用，仅作记录不转换（或后续 audioRole 区分）

### 音频脱机（wav 头）——终态方案：用户 GUI 手动重链（2026-08-11 拍板）

**核心结论（用户拍板，勿再走 API 弯路）**：旧式 PCM 头 wav / 多 clip 共享 asset 的音频片段导入后可能脱机（`GetMediaPoolItem()=None`），**正解是用户 GUI「文件 → 从媒体夹重新套底」手动处理（一次全链上，用户亲自验证 3/3）**。**API 无对应方法**——RelinkClips 只重定位池项路径、ReplaceClip 不改变片段绑定、解锁四步（SetClipsLinked→Unlink→Relink→锁回）实测全 True 但片段仍 False。**不要试图 API 复刻，脱机音频直接交给用户手动链接。**

| 坑 | 症状 | 终态处理 |
|---|---|---|
| **旧式 PCM wav 头**（fmt_size=16 / audio_format=1） | 达芬奇媒体池建项但**标"离线 -"**，时间线片段 `GetMediaPoolItem()=None` | **首选：用户 GUI「文件 → 从媒体夹重新套底」**。备用批量修复：`fix_wav_headers.py` 重编码为 EXTENSIBLE（fmt=40/audio_format=65534）——**ffmpeg 必须加 `-write_bext 1`**（默认 `-c:a pcm_s24le` 输出仍是 fmt=16 假修复） |
| **多 clip 共享同一音频 asset**（同名素材切多段） | 同名合并后多 clip 引用同一 aid → 达芬奇不关联（池项=False） | **保持同名合并**（达芬奇只按文件建池项，拆独立 asset 反而导致片段无池项可链——走过弯路）；脱机交给用户 GUI 手动重链 |

**流程纪律（用户两次纠正）**：① 排查脱机**先确认媒体池里是原素材**——曾造 `_ext.wav` 副本并让转换器映射过去，导致媒体池没有原素材、用户 GUI 无从选原文件（"你都没把原素材放进去"）。转换器素材引用始终指向原素材，重编码只作为 NAS 批量修复不动转换器。② **重编码不是必需的**——用户 GUI 一次成功，不要过度工程化。③ 脱机音频手动处理是用户明确选择（"音频脱机的我后面手动处理"）。

- 音频素材收集：剪映 `materials.audios[]` type 是 `extract_music`/`music`/`sound`，path 可能是占位符或 `Resources/audioAlg/...`（算法生成音乐，ffprobe 过滤）

### 套底（relink）机制（本次会话最深的坑，全量 51 集重导多次）

**达芬奇 `ImportTimelineFromFile` 只在素材"不存在"时创建并链接媒体池项**。已存在的素材不被关联 → 时间线片段 `GetMediaPoolItem()=None`（无法调色/回批）。

完整流程（batch_import_manlv.py 实测 51 集全部套底成功）：
1. **当前夹设为 01素材/<集>**（素材自动创建到此，套底后素材目录结构正确）
2. **删除同名旧时间线**（`DeleteTimelines`）——必须先删时间线再删素材：残留时间线引用素材导致 DeleteClips 删不净
3. **清空该夹旧素材——必须循环 DeleteClips 直到 `GetClipList()` 为空（0 项）**，一次删不干净（达芬奇索引残留）
4. **删除操作后当前夹可能失效 → 必须重新 `SetCurrentFolder(ep_folder)`**（漏了这一步素材创建错位 → 片段不套底，第1集 1/52 的根因）
5. `ImportTimelineFromFile(fcpxml)` → 达芬奇创建素材+链接 = 套底
6. **`MoveClips([时间线对象], 00时间线)`**——时间线对象创建在当前夹（01素材/<集>），**必须移走**，否则下次导入时素材夹残留时间线对象 → 达芬奇看到"文件夹非空" → 素材不重建 → 不套底（这是全量重导反复失败的根因链最后一环）
7. 00时间线 清理：只删非「时间线」类型项

**⚠️ 套底验证必须在导入同一进程内做**：`GetMediaPoolItem()` **跨进程（新脚本/新连接）返回 None = 假象**，不是真未套底。本会话最大弯路：51 集反复重导其实一直成功，是跨进程验证脚本误判"未套底"导致。批量脚本在 `ImportTimelineFromFile` 后**立即同进程**查询并打印 `导入进程内套底: N/N`（如 37/37、52/52）。

**验证**：`c.GetMediaPoolItem()` 非 None = 套底成功；批量后逐集抽查 `GetItemListInTrack('video', 1)` 套底数。

## 已知边界

- 转场/滤镜/花字/特效不过去（跨软件固有）
- **复合片段（subdraft）渲染方案已落地**（2026-08-11 实测打通）：
  - 脚本 `C:\Users\HMSJ\Documents\Hermes\scripts\render_compounds.py`：解析草稿 `materials.drafts` → 子草稿 `subdraft/<id>/draft_content.json`（或内嵌 draft）→ **递归展开嵌套复合片段**（素材 path 空 → 深入嵌套 drafts 找叶子 segments）→ ffmpeg 逐段裁剪+变速（`setpts=PTS/speed` + `atempo`，concat demuxer 拼接）→ 产物 `NAS/01素材/<集>/video/<集>_复合片段N.mp4` + `rendered/compound_map_<集>.json`（material_id → 产物路径）
  - 转换器 `jianying2davinci.py` 自动加载 compound_map：素材 path 空时查映射引用渲染产物（第2集 37 段无空隙验证通过）
  - **嵌套陷阱**：子草稿素材可能嵌套多层（顶层 tracks 引用"复合片段1"素材 path 空，真实时间线在更深 drafts）；素材路径可能是占位符 `##_draftpath_placeholder_..._##/materials/video/<名>`（从占位符提取文件名 → 草稿本地 materials/ 找）
  - **云缓存素材**：部分集素材 path 指向 `D:/新建文件夹/JianyingPro Drafts/.cloud_cache_*/`（剪映云盘缓存）——未下载到本机则无法渲染（第14/17/21/24/38 集 + 第47集部分），需剪映打开该集同步后重跑
- **同名素材脱机**：剪映同一文件名多个 material_id（如 `1_美图视频消除.mp4` ×16）→ 达芬奇对同名 asset 去重改名 `name[xxx].ext` → 路径失配脱机。转换器按 `(name, kind)` 去重 asset（同名只输出一个 aid，所有 clip 复用）
- **png/jpeg 静帧脱机**：达芬奇导入静帧自动加 `[帧范围]` 后缀（`sdr[709-270733].png`）→ 文件不存在。`fix_offline.py` 扫描媒体池 File Path，脱机项在 NAS 同目录按基名匹配建副本（53/53 修复）
- 变速段带 timebase 后套底正常（见铁律 7；timebase 与时间线 fps 一致，25fps 时间线用 25）
- 加密草稿、坏素材（audioAlg 非 RIFF wav）用 ffprobe `media_readable()` 过滤跳过

## 验证脚本（scripts/dvr_import_test.py 思路）

导入后必须真实验证，不能只看返回值：
```python
tl = mp.ImportTimelineFromFile(fcpxml_path)
assert tl, '导入失败'
items = tl.GetItemListInTrack('video', 1)
assert items and len(items) > 0, '导入成功但素材未落轨'
# 套底验证：
linked = sum(1 for c in items if c.GetMediaPoolItem())
assert linked == len(items), f'未套底: {linked}/{len(items)}'
# 帧数验证（每段不能是 1 帧）：
d = items[0].GetEnd() - items[0].GetStart()
assert d > 1, f'duration 解析错误: {d} 帧'
```
