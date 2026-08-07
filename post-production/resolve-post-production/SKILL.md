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
