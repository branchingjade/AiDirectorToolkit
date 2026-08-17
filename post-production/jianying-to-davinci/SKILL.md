---
name: jianying-to-davinci
description: 剪映草稿导入达芬奇时用。自写转换器+5个实测坑，达芬奇Studio 21已实测打通。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  tags: [剪映, 达芬奇, fcpxml, 工程转换, post-production]
  related_skills: [resolve-post-production]
---

# 剪映草稿 → 达芬奇导入（实测打通，2026-08-10）

## When to Use

用户想把剪映工程导入达芬奇（调色/精剪/套底），或排查剪映→达芬奇转换失败（空时间线/脱机/崩溃）。触发词：剪映导入达芬奇、剪映转达芬奇、剪映工程到达芬奇、彩虹桥不好用。

剪映没有官方导出到达芬奇的通道；彩虹桥等第三方工具有 bug。**自写转换器**读剪映明文草稿 JSON → 生成 FCPXML → 达芬奇 Import Timeline 导入。已在用户本机达芬奇 Studio 21.0.2.4 实测两个真实草稿全部通过（23 视频段/52 视频段，时长精确一致）。

## 核心资产

- 转换器：`C:\Users\HMSJ\Documents\Hermes\scripts\jianying2davinci.py`
- 一键入口：`C:\Users\HMSJ\Documents\Hermes\scripts\jianying2davinci.bat`
- 达芬奇脚本桥：`C:\Users\HMSJ\scripts_dvr\DaVinciResolveScript.py`（Python 3.12 兼容版，importlib 替代已废弃的 imp）

## 用法

```bash
python scripts/jianying2davinci.py "草稿目录" --name "达芬奇时间线名"
# 可选: --fps 30 强制帧率 | --with-text 字幕写进FCPXML(仅少量字幕) | --no-srt 不生成SRT
```

草稿目录默认在 `%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft\<草稿名>`

产物：`.fcpxml`（达芬奇 File → Import → Timeline）+ `.srt`（拖进编辑页自动生成字幕轨）。

## 剪映草稿结构要点

- **多数草稿是明文 JSON**（`draft_content.json`），个别加密（草稿 1 实测加密）
- **加密草稿有明文备份**：依次尝试 `template.json` / `template.json.bak` / `draft_content.json.bak` / `template-2.tmp`（转换器已自动回退）
- 素材路径两种形态：占位符 `##_draftpath_placeholder_XXX_##/materials/...`（→ 草稿目录绝对路径）或**纯相对路径** `materials/video/...`（→ 基于草稿目录）
- 时间单位：微秒（μs）；`source_timerange`=素材入出点，`target_timerange`=时间线位置
- 素材 type 需归一化：`photo`（定格图）→ video，`extract_music`/`music` → audio
- 素材实际帧率/分辨率**必须用 ffprobe 探测**——剪映素材常混用 24/30/48/60fps、720x1280/1080x1920，草稿 JSON 里 fps 字段常缺失

## 五个实测坑（达芬奇 21 表现，每条都是崩过/空时间线换来的）

1. **素材帧率混乱 → 达芬奇崩溃**：所有素材指向单一 format 会崩。必须每个素材按 ffprobe 真实帧率/分辨率生成**独立 format**，asset 引用各自 format。format id 从 fmt2 开始（fmt1 留给画布默认），避免 id 重复。
2. **`hasVideo="true"` → 素材全部不落轨（V1=0 空时间线）**：达芬奇 FCPXML 布尔值只认 `1`/`0`，`true`/`false` 导致导入"成功"但时间线为空、媒体池 0 片段。最隐蔽的坑。
3. **`file:///C%3A/` 冒号被编码 → 素材脱机**：media-rep src 的 `:` 和 `/` 必须保留（`urllib.parse.quote(path, safe='/:')`），`%3A` 达芬奇不认。
4. **`<sync>/<lane>` 结构 → 达芬奇拒绝导入**：音频轨不要用 sync 包裹。全部 clip（视频+音频）直接放 spine，**按 权重分组（视频0→音频1→title2）+ 组内 offset 排序**，避免同位置重叠（offset=0 的音频与首视频重叠会导致拒绝）。
5. **spine 内 title 数量限制（约 25-30 个）→ 超限拒绝**：字幕默认**不进 FCPXML，走 SRT**（达芬奇拖 SRT 自动生成字幕轨，无数量限制）。`--with-text` 可强制写入但仅适合少量字幕。

### 批量导入实战补充坑（《满级女总》51 集全量，2026-08-10）

6. **`GetClipProperty('Type')` 返回中文**（如「时间线」「视频 + 音频」），不能用 'Timeline' 判断——清理媒体夹时要保留 Type 含「时间线」的对象，否则 DeleteClips 会把时间线对象一起删掉（时间线本身是媒体池里 Type=时间线 的 clip）。
7. **剪映 audioAlg 目录的产物可能是损坏文件**（存在但 ffprobe 解析失败，如 `*_human.wav` 提取人声），达芬奇 ImportMedia/ImportTimelineFromFile 遇到即失败。素材可读性检查要用 **ffprobe 验证**（`-show_entries stream=codec_name`），不能只 `os.path.isfile`。转换器已内置 `media_readable()` 自动跳过坏素材；`copy_manifest.py` 复制时也会跳过。
8. **素材重映射到 NAS**：`--media-root <NAS根>` 把素材路径改为 `<根>/<video|audio|image>/<原名>`（按类型分子夹），`--copy-manifest` 输出 {原路径: 新路径} JSON 供批量复制。达芬奇导入素材用 `ImportMedia`（素材进当前媒体夹），时间线用 `ImportTimelineFromFile`（先 `SetCurrentFolder` 到目标夹）。
9. **达芬奇 ImportTimelineFromFile 会把时间线引用的素材复制一份到当前媒体夹**——批量导入后清理重复素材时要保留「时间线」类型对象。
10. **时长验证**：达芬奇时间线帧率取 `GetSetting('timelineFrameRate')`（可能是 30 而非草稿 fps），换算时长别用错帧率。

其他：project 名与达芬奇已有时间线重名会导入失败（`--name` 指定新名）；转场/滤镜/花字/特效**跨软件不过去**（固有边界，所有工具一致）；变速保留 rate 标签。

## 字幕批量导出（《满级女总》51 集实测，2026-08-13）

单独导字幕（不转达芬奇）：`python scripts/jianying_srt_export.py`——批量读全部草稿，只产 SRT（默认输出 `Z:\项目\《满级女总》\字幕\第N集.srt`，`--eps 1,3` 只导指定集）。

字幕提取的两个实测坑：

1. **`material_map` 必须收集 `materials.texts`**：字幕素材在 `materials.texts`（不在 videos/audios/images），不收集则 `build_srt` 全空（草稿 1 曾导出 0 条）。
2. **多条 text 轨 = 重复字幕层**：重识别/换版会遗留整层副本（第 10 集 61+32 双轨，轨 1 是后半段错位约 2.4s 的副本）。去重规则：**不同轨、同文本、起始时间差 <5s 视为重复层，只留最早一条；同轨重复（结巴/连说）是真实台词，保留**。多轨小段（1-3 段）是重点花字/台词，属于字幕保留。

## 达芬奇脚本 API 连接（Studio 专用，Python 3.12 实测）

免费版无脚本 API；Studio 需安装时勾选 Developer/Scripting（用户机器实测没勾，但 fusionscript.dll 在安装目录，可绕过）。

```python
import importlib.util, importlib.machinery, sys
sys.path.insert(0, r'C:\Users\HMSJ\scripts_dvr')  # 兼容版 DaVinciResolveScript.py
path = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
loader = importlib.machinery.ExtensionFileLoader('fusionscript', path)
spec = importlib.util.spec_from_loader('fusionscript', loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
sys.modules['fusionscript'] = mod
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp('Resolve')  # 前提: Resolve 运行中 + Preferences External Scripting = Local
```

用 **Python 3.12**（`%LOCALAPPDATA%\Programs\Python\Python312\python.exe`），3.11 venv 会段错误（ABI 不匹配）；3.12 也需要 importlib 替代 `imp`（3.12 已移除）。

### 导入并验证（真实链路）

```python
proj = resolve.GetProjectManager().GetCurrentProject()
mp = proj.GetMediaPool()
tl = mp.ImportTimelineFromFile(r'...\xxx.fcpxml')
# 关键: 必须查 V1 片段数，导入返回非 None ≠ 成功（可能空时间线）
v = tl.GetItemListInTrack('video', 1)   # 达芬奇21 API，非 GetItemListInTimeline
print(len(v) if v else 0)                # 应与草稿视频段数一致
```

- 清理测试时间线：`mp.DeleteTimelines([tl_list])`（在 MediaPool 上，不在 project 上）
- 重名时间线导入会返回 None——测试时每次用唯一 project 名

## 验证收尾清单

- [ ] XML 语法合法（xml.dom.minidom.parse）
- [ ] 所有 media-rep src 文件真实存在（占位符/相对路径都解析成绝对路径）
- [ ] spine 无 sync/lane；hasVideo/hasAudio 是 1/0；src 无 %3A
- [ ] 达芬奇导入后 V1 片段数 = 剪映草稿视频段数
- [ ] 时长一致（GetEndFrame - GetStartFrame）/ fps ≈ 草稿 duration
- [ ] 字幕 SRT 每块 `序号\n时间线 --> 时间线\n文本` 格式合法

## 已知边界

- 转场/滤镜/花字/特效不过去（跨软件固有）
- 字幕样式不进达芬奇（SRT 纯文本，可在达芬奇统一设置）
- 复合片段（combination）需先展开成扁平时间线
- 变速保留 rate 标签但达芬奇支持度有限
