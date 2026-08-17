---
name: resolve-post-production
description: DaVinci Resolve MCP × Hermes 后期制作完整工作流——素材分析、调色评估、时间线管理。
version: 1.0.0
category: post-production
---

# DaVinci Resolve 后期制作（Hermes MCP 集成）

通过 Hermes 内置 MCP 客户端控制 DaVinci Resolve Studio，覆盖素材技术分析、调色评估、时间线管理、渲染等全部后期环节。

## 前置条件

- DaVinci Resolve **Studio**（免费版不支持脚本）
- Resolve 运行中，Preferences → External scripting → **Local**
- davinci-resolve-mcp 已安装并配置到 Hermes（见 references/hermes-mcp-config.md）
- FFprobe/FFmpeg 已安装（媒体分析需要）

## 核心工作流

### 1. 素材技术分析（调色决策辅助）

对时间线上所有素材做 quick 分析，提取编码/分辨率/色彩空间/位深/帧率等信息，用于判断调色管线需求。

```
media_analysis action=analyze_sequence
  depth=quick  （仅 ffprobe 元数据，约 2s/条）
  include_visuals=false
  include_transcription=false
  publish_metadata=false
  timed_markers=no
  sampling_mode=fixed  （首次运行需要设置默认值）
```

分析完成后用 Python 脚本提取聚合数据——见 `scripts/extract-technical-report.py`。

### 2. 调色状态评估

步骤：
1. 切到 Color 页面：`resolve_control action=open_page page=color`
2. 全域报告：`timeline_item_color action=grade_boundary_report`（首片段）
3. 采样多个片段：`probe_node_graph` 检查节点数/LUT/工具
4. 用 `gallery_stills action=grab_and_export` 在不同时间点抓帧，通过 vision_analyze 评估颜色一致性和 look 风格

### 3. 素材分辨率不足时的处理

当素材分辨率低于交付规格时，需做超分（super-resolution）。从快到慢三个层级：

| 方案 | 速度 | 质量 | 适用 |
|------|:----:|:----:|------|
| Resolve Super Scale（内置） | 快 | 一般 | 轻度放大，不想离开Resolve管线 |
| Real-ESRGAN / ComfyUI ESRGAN | 中 | 好 | 通用4x，GAN细节锐利 |
| ComfyUI 两阶段（SwinIR→ESRGAN→SD tile） | 慢 | 最佳 | 单帧/海报级质量需求 |

**Resolve Super Scale 说明**：Studio版项目设置中启用，选2x/4x。无缝集成但模型固定不可换，质量不如专用AI模型。

**外部超分工作流**：导出帧→ComfyUI超分→导回。Model选择、VRAM预算、时域一致性问题详见 ComfyUI skill 的 `references/upscale-model-guide.md`。

**关键原则**：
- 先超分再调色——超分模型在线性空间表现更好
- 视频逐帧超分需额外做时域平滑，否则会闪烁
- 扩散模型（DiffBIR）可能"发明"不存在的细节，电影修复应保守使用

### 4. 时间线结构探测

```
timeline action=set_current index=N  （切换到目标时间线）
timeline action=probe_timeline_structure include_clip_properties=true
timeline action=source_range_report merge=true  （获得唯一素材列表）
media_analysis action=coverage_report min_source_trust=medium  （已有分析状态）
```

## 调色 API 边界（重要）

**可直接控制**：
- CDL 值（Slope/Offset/Power/Saturation on existing node）
- LUT 套用/导出
- 版本管理、颜色组、Gallery 静帧

**只能作为不透明包应用**：
- DRX 导入（替换整个节点图，不是追加）
- 完整 grade copy

**完全不可脚本化**：
- 新建/删除/连接节点
- Lift/Gamma/Gain 轮值
- 曲线/Qualifier/Power Window/Tracker/Color Warper

## 调色分析产出格式

**用户偏好：图文报告，不是纯文字。** 纯文字调色分析易读性不足，需要视觉载体——生成 HTML 文件内嵌帧图像，在浏览器中打开。

### 帧采样 → HTML 报告工作流

```
1. 定位时间点：timeline_markers set_current_timecode → 场景首/中/尾 3+ 位置
2. 抓帧：gallery_stills grab_and_export cleanup=false folder_path=... format=jpg
3. 逐帧分析：vision_analyze 每帧问"色彩色调/冷暖/反差/饱和度/一致性"
4. 聚合对比：确认帧间是否有色温跳变
5. 生成 HTML：内嵌 base64 帧图像 + 分段分析（一致性/做得对/可精进/总体评价）
6. 给用户文件路径，用户自己打开
```

HTML 模板和生成脚本在 `references/color-report-template.html`。

HTML 模板和生成脚本在 `references/color-report-template.html`。8bit h264 素材的调色约束见 `references/8bit-grading-constraints.md`。

### 原则

- **只分析、评价、给方向，不主动操作。** 用户说了"不需要你操作"就停手。
- 分析先定位"有没有调色"（扫 V1 的 `tools` 字段找 HDR/LUT/工具痕迹），再评价"调得怎么样"
- 8bit h264 素材的调色天花板很低——暗部不提、压黑保中间调、冷调容易做、暖调容易爆

## 常见问题

### FCPXML 导入兼容性（剪映/外部工程 → 达芬奇，2026-08 实测达芬奇 21 Studio）

达芬奇 **File → Import → Timeline** 或脚本 `MediaPool.ImportTimelineFromFile()` 导入 FCPXML 时，以下陷阱全部实测踩过：

| 陷阱 | 症状 | 解法 |
|---|---|---|
| format 缺 `name` 属性 | 导入失败（返回 None） | format 必须带 `name="FFVideoFormat{W}x{H}p{fps}"` |
| 素材混帧率/分辨率却共用一个 format | **达芬奇崩溃**（segfault） | 每素材用 ffprobe 探测真实帧率/分辨率，独立 format |
| `<sync>/<lane>` 结构 | 导入失败 | 全部 clip 直接放 spine，不用 sync（达芬奇 21 实测拒绝）；**多轨用 clip 级 `lane` 属性**（主轨无 lane/叠加轨 lane="1""2"…） | 
| duration 写浮点秒 `4.000000s` | **每片段只有 1 帧**（用户目视检查抓出） | duration 必须有理数帧数 `帧数/25s`（asset 同理），**禁止浮点秒** |
| offset 秒取整 `offset="4/1s"` | 时间线出现**空隙/空白**（剪映 start 多非整数秒，round 误差 ±0.37s） | offset 帧精度 `offset="{int(round(secs*50))}/50s"`；start（源入点）同理 |
| **剪映工程 fps=50（子帧 20ms）** | 若直接 round 到 25fps 帧（`round(secs*25)`），相邻片段出现**多处 1 帧间隙**（25fps 无法表示剪映半帧位置 134.5/135.5 → 取整出缝） | **时间线仍用 25fps**（`frameDuration="1/25s"`），但主轨做**缝合并**：每段 `offset_f=round(secs*25)`、`dur_f=round(dur*25)`，若 `off_f > prev_end`（缝）或 `< prev_end`（叠）都吸附到 `prev_end`，`prev_end = off_f + dur_f` 接力 → 间隙 0 处。代价：片段位置最大偏移 4 帧（160ms，平均 1.2 帧，肉眼不可见）。**不要升 50fps 时间线**——实测 50fps 下 lane>0 clip 的 offset 解析错位（V2 叠加轨跑到 2 倍位置，如 75.6s→151.3s） | 
| 变速 rate 缺 timebase `<rate><value>0.9</value></rate>` | **片段不套底**（1/36），变速段无法调色 | `<rate><value>0.9</value><timebase>25</timebase></rate>`（timebase 必须与时间线 fps 一致=25；变速+套底两全，36/36） |
| asset duration < clip 用时长 | 导入失败 | asset duration 向上取整（int+1），必须 ≥ clip 时长 |
| 同名时间线已存在 | 返回 None 且**不报错** | 导入前 `DeleteTimelines` 删旧；测试残留时间线会阻断套底 |
| **同名素材**（同一文件名多个 material_id，剪映常见） | 达芬奇对同名 asset 去重改名 `name[xxx].ext` → 路径失配 → **脱机** | 转换器按 `(name, kind)` 去重 asset：同名只输出一个 asset，所有 clip 复用同一 aid（改名去重后 26 组同名 → 0 脱机） |
| **png/jpeg 静帧**（定格图素材） | 达芬奇导入时自动加 `[帧范围]` 后缀（如 `sdr[709-270733].png`）→ 文件不存在 → **脱机** | `fix_offline.py` 扫描媒体池 File Path，脱机文件在 NAS 同目录按基名匹配建副本（53/53 修复） |
| 音频 `<gap>` 包裹 | 音频轨全丢（A1=0） | gap 音频是达芬奇导入器硬限制；**正确格式 = `<asset-clip>` + `audioRole="dialogue"` 直接放 spine**（无 gap/lane，第1集 4 轨实测全进） |\n| **旧式 PCM wav 头**（fmt_size=16/audio_format=1，剪映旧音频） | 媒体池池项标"离线 -"、片段 GetMediaPoolItem()=None | **首选：用户 GUI「文件 → 从媒体夹重新套底」手动链接（一次全链上，2026-08-11 用户亲自验证；API 无对应方法——RelinkClips 只重定位池项路径、ReplaceClip/解锁四步均无法让片段链上池项，多次实测失败，勿再尝试 API 复刻）**。备用批量修复：`fix_wav_headers.py` 重编码为 EXTENSIBLE（fmt=40/audio_format=65534），**ffmpeg 必须加 `-write_bext 1`**（默认 `-c:a pcm_s24le` 输出仍是 fmt=16 假修复）；转换器素材引用保持原素材不绕路 |\n| 音频多 clip 共享同一 asset（同名素材切多段） | 音频片段不关联（池项=False） | **保持同名合并（达芬奇只按文件建池项）**，脱机音频交给用户 GUI「从媒体夹重新套底」手动处理——拆独立 asset 反而导致片段无池项可链（本会话走过弯路：拆名+解锁四步均失败，用户 GUI 一次成功） |
| spine 内 title 数量 ≥30 | 导入失败（≤25 通过） | 字幕默认走 SRT 拖入（达芬奇自动生成字幕轨），不进 FCPXML |
| `file:///C%3A/...`（冒号被 quote 编码） | "导入成功"但素材不落轨、媒体池空、时间线 0 片段 | URI 里冒号/斜杠必须保留：`urllib.parse.quote(p, safe='/:')` |
| `hasVideo="true"`/`hasAudio="true"` | **导入"成功"但素材全部不落轨**（V1=0，媒体池空，最隐蔽） | 布尔必须写 `1`/`0`：`hasVideo="1" hasAudio="0"`——达芬奇只认数字布尔，true/false 静默丢弃素材 |
| spine 内同 offset 重叠 clip（视频+音频都从 0 开始） | 导入失败 | 音频轨 clip 整体排视频之后（分组+组内按 offset 排序） |
| project 名与已有时间线重名 | 导入失败/返回旧时间线 | `--name` 指定唯一时间线名 |

**关键验证原则**：`ImportTimelineFromFile` 返回非 None **不等于导入成功**——必须检查 `tl.GetItemListInTrack('video', 1)` 片段数 > 0 且媒体池有素材。返回成功但 0 片段 = 素材路径/格式问题。

**FCPXML 结构要点**：spine 内元素必须时间有序；asset 的 `format` 引用各自真实格式；`hasVideo`/`hasAudio` **必须写 `1`/`0`**（实测 `"true"`/`"false"` 会导致素材全部不落轨 V1=0；**视频素材用 `hasAudio="0"` 即丢弃自带音频、只留剪映音频轨**）；时间单位用有理数帧 `"N/25s"`（25fps 时间线）；**时间线保持 25fps + 主轨缝合并**（剪映草稿顶层 `fps: 50` 子帧精度会出 1 帧间隙，但升 50fps 时间线会导致 lane>0 clip offset 错位——详见上表，勿再走 50fps 路线）；**音频 clip 用 25fps 帧格式 + audioRole 直接放 spine**（详见 references「音频」节）。

### 套底（relink）机制：ImportTimelineFromFile 只在素材"不存在"时创建+链接

**核心事实**：达芬奇导入 FCPXML 时间线时，素材已存在于媒体池 → **不建立关联**（时间线片段 `GetMediaPoolItem()=None`，无法调色/回批）。这是"为什么素材都在但没套底"的根因。

**可靠流程**（batch_import_manlv.py 全量 51 集验证）：
1. 当前夹 = `01素材/<集>`（素材自动创建到此，目录结构正确）
2. 先删同名旧时间线（残留时间线引用素材 → DeleteClips 删不净 → 阻断重建）
3. 清空该夹旧素材——**必须循环 DeleteClips 直到 GetClipList 为空（0 项）**，一次删不干净（达芬奇索引残留）
4. **删除操作后当前夹可能失效 → 必须重新 `SetCurrentFolder(ep_folder)`**（漏了这一步素材创建错位 → 片段不套底，1/52 的根因）
5. `ImportTimelineFromFile` → 达芬奇创建素材 + 链接 = 套底
6. **`MoveClips([时间线对象], 00时间线)`**——时间线对象创建在当前夹，**必须移走**，否则下次导入素材夹残留时间线对象 → 素材不重建 → 不套底（反复失败的根因链最后一环）

**⚠️ 套底验证必须在导入同一进程内做**：`GetMediaPoolItem()` **跨进程（新脚本连接）返回 None = 假象**，不是真未套底。批量脚本在 `ImportTimelineFromFile` 后立即同进程查询并打印 `导入进程内套底: N/N`——跨进程验证脚本会误判全部未套底（本会话最大弯路：51 集反复重导其实一直成功，是验证方式错了）。

**⚠️ 排查脱机时先确认媒体池里是原素材**（2026-08-11 用户纠正）：音频脱机排查时先造了重编码 `_ext.wav` 副本并让转换器映射过去，结果媒体池里**没有原素材**，用户 GUI 重新套底时无从选原文件（"你都没把原素材放进去"）。正确顺序：① 先确认导入的是原素材（转换器 media_root 映射不绕路）② **脱机音频终态方案 = 用户 GUI「文件 → 从媒体夹重新套底」手动链接（一次全链上，用户亲自验证；API 无对应方法，勿再尝试 RelinkClips/ReplaceClip/解锁四步复刻）** ③ 重编码（fix_wav_headers.py，注意 ffmpeg 需 `-write_bext 1`）只作备用批量修复，不改变转换器的素材引用。

验证：`c.GetMediaPoolItem()` 非 None = 套底成功。

详见 `references/jianying-draft-to-fcpxml.md`「套底（relink）机制」节。

### 达芬奇 Studio 脚本 API：Windows 外部连接（Python 3.12）

Studio 版但安装时未勾 Developer/Scripting 组件 → 无 `DaVinciResolveScript.py` 模块。解决：

1. 从 GitHub 镜像拉官方模块（如 `diop/davinci-resolve-api` 的 `Modules/DaVinciResolveScript.py`）
2. **Python 3.12 已移除 `imp` 模块**——官方模块会 ImportError，需打补丁改用 `importlib.util.spec_from_file_location`
3. fusionscript.dll 用 ExtensionFileLoader 加载（直接 spec_from_loader 会报 NoneType）：
   ```python
   loader = importlib.machinery.ExtensionFileLoader('fusionscript', r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll')
   spec = importlib.util.spec_from_loader('fusionscript', loader)
   mod = importlib.util.module_from_spec(spec); loader.exec_module(mod)
   sys.modules['fusionscript'] = mod
   ```
4. 需 `System.Scripting.Mode = 1`（Preferences → External scripting → Local，在 `%APPDATA%\Blackmagic Design\DaVinci Resolve\Preferences\config.dat` 可查）
5. 达芬奇 21 实测 Python 3.12 可连（3.11 也试过可行）；bash 里默认 python 是 Hermes venv 的，用系统 Python 3.12 更稳
6. 时间线管理 API：删除用 `MediaPool.DeleteTimelines([...])`（不是 project.DeleteTimeline，21 无此方法）；取片段用 `GetItemListInTrack('video', 1)`

完整剪映草稿 → FCPXML 转换器在用户工作区 `C:\Users\HMSJ\Documents\Hermes\scripts\jianying2davinci.py`（git 仓库），草稿结构逆向细节见 `references/jianying-draft-to-fcpxml.md`。**复合片段（嵌套剪辑）渲染方案**（render_compounds.py + compound_map 映射 + 云缓存素材边界）同见该文件「已知边界」节。

### 性能排障：Resolve 卡顿/丢帧

用户说"达芬奇很卡"或"修复达芬奇"→ **不要直接跳到 MCP**。"修复达芬奇"不等于 MCP 问题。先按以下顺序做系统级诊断：

1. GPU 显存分析（nvidia-smi — 8GB 卡 4K 需 4-6GB 空闲）
2. 后台 GPU 进程排查（Wallpaper Engine、Chrome、Steam 等关掉）
3. 驱动类型检查（Game Ready → 换 Studio 驱动）
4. Resolve 内代理模式/缓存优化（Proxy Mode → Half、DNxHR LB 缓存）
5. 笔记本散热降频检查

完整诊断清单见 `references/resolve-performance-troubleshooting.md`。

> **关键认知：MCP 是独立进程，不消耗 Resolve 的 GPU 资源。卡顿不是 MCP 导致的。**

### MCP 服务器更新

davinci-resolve-mcp 以本地源码方式运行（非 pip 安装）。更新步骤：

1. 克隆新版本到新目录（旧目录被进程占用）
2. 用与 `PYTHONHOME` 一致的 Python 版本创建 venv
3. `pip install -r requirements.txt` 后**再装 `anyio mcp`**（requirements 不完整）
4. `hermes config set` 改 command 路径；args 路径用 Python yaml.dump 直接写（hermes config set 的 args 有序列化 bug）
5. 重启 Hermes；`resolve_control get_version` 验证版本
6. 旧目录重启后可删除

### Fusion 标题/人名条构建

首选 **OGraf**——达芬奇通过 Fusion 内置 OGrafLoader（嵌入 CEF 浏览器引擎）原生支持，HTML/CSS/JS 完全控制设计，Inspector 面板原生拾色器/文本/滑块参数。官方文档在 `C:\ProgramData\...\Developer\OGraf HTML Templates\Documentation\`。

备选 **Fusion .setting + .drfx**——Lua 序列化的 Fusion 节点图，原生但编写繁琐。

**不可用**：Python API 直接赋值（值不持久化）、Lottie 手写 JSON（黑屏，无原生渲染器）、SVG 导入 Media Pool（不支持）、MCP fusion_comp 逐节点构建（每次返回 100KB+ JSON，低效）。

详见 `resolve-fusion-title-builder` skill。

**设计参考**：古装剧/年代剧的 name plate 和 lower thirds 视觉风格、字体、色彩和动画参考，覆盖中国古装剧（琅琊榜、长安十二时辰、大明王朝、知否）、日本时代剧（黑泽明七人の侍/用心棒/羅生門/乱/影武者、NHK大河ドラマ）、经典电影字幕（王家卫、张艺谋）和获奖片头序列（Saul Bass 纯真年代、Elastic 幕府将军），见 `references/period-drama-name-plate-references.md`。

**外部模板可用性**：年代剧/年代感人名条模板作为产品品类**在主流市场上不存在**（2026-07 全平台搜索：Mixkit/Envato/Motion Array/Gumroad/Videohive/Pixflow/YouTube）。最接近的是 TiKa-Studios "15 Cinematic Retro Film Titles"（€15，通用欧美复古标题，非中国年代剧美学）。正确路径是 OGraf 自定义设计。

**找帧资源**：研究标题设计时优先使用 movie-screencaps.com 的逐帧截图（前 5-10 帧通常包含完整标题序列），Bing 图片搜索（curl + grep murl 模式可在无浏览器时提取图片 URL）。

### hermes config set 的 args 序列化 bug
用 `hermes config set "mcp_servers.X.args" '["..."]'` 写入时，args 会被序列化为 JSON 字符串而非 YAML 列表。需要事后用 Python + yaml.dump 修复。详见 references/hermes-mcp-config.md。

### Gallery grab 权限
`grab_and_export` 需要 Color 页面 + Gallery 面板可见。如果返回 false，先确认 `resolve_control action=open_page page=color` 已执行。

### 视觉分析首次运行
首次 analyze 会弹出 `confirmation_required` 要求选择 sampling_mode。即使 `include_visuals=false` 也需要设一个默认值。推荐 `sampling_mode=adaptive_capped`。

### 调色版本保护
`ApplyGradeFromDRX` 替换整个节点图——始终先做 version snapshot：`timeline_item_color action=grade_version_snapshot`。
