# FCPXML 多轨/音频/HEVC 实测记录（2026-08-11）

《满级女总》51 集批量导入攻坚中，对达芬奇 21.0.2.4 FCPXML 导入能力的逐项实测记录。
配套 SKILL.md 正文「多轨与音频」「核心坑 11/15-21」章节。

## 多轨方案演进（试错路径，避免重复踩）

| 写法 | 实测结果 |
|---|---|
| `<sync><lane><asset-clip/></lane></sync>` | 导入"成功"但 V2 内容被丢弃（V1 只有 1 段） |
| `<sync><spine><asset-clip/></spine></sync>` | 导入"成功"但只留 1 帧（总时长=1帧） |
| **spine 内 clip 直接带 `lane="1"`** | ✅ V1+V2 都进（`GetTrackCount('video')=2`） |
| 音频 clip 直接放 spine（asset-clip + audioRole） | 导入成功但 A1=0 段 |
| **音频 clip 放 `<gap>` 里带 `lane="1"`** | ✅ A1 进轨（复刻达芬奇导出格式） |

关键认知：**sync/lane 包裹不是标准多轨写法**（FCPXML 1.8 DTD 里 `lane` 是 clip 的 `ao_attrs` 属性，不是元素）；`lane` 属性语义：0=父容器内（主轨），>0=向上叠加，<0=向下（负 lane 达芬奇不认，实测 lane=-1 导入失败）。

## ⚠️ 时间格式金标准（2026-08-11 二轮修正——最隐蔽的坑）

**浮点秒 duration 会让每个片段变成 1 帧**。用户导入第6集后一眼看穿"每个片段都只有一帧"——根因就是转换器生成 `duration="1.900000s"`（浮点），达芬奇解析成 1 帧。此前误以为"浮点也兼容"。

| 位置 | 正确格式 | 反例（失败） |
|---|---|---|
| clip/gap `duration` | `帧数/帧率`：`48/25s`、`3302/25s` | `1.900000s` → 每段 1 帧 |
| clip `offset` | 秒整数有理数：`0/1s`、`15/1s` | `0.000000s` → 只进第一段 |
| clip `start`（源入点） | 秒整数有理数：`0/1s`（对齐达芬奇导出） | 浮点有时可导但混用有理数时拒导 |
| asset `duration` | 秒有理数**向上取整**：`int(dur)+1/1s` | `round()` 截断导致 clip 时长超 asset → 整体拒导 |

达芬奇导出实测对照（权威模板）：
- 视频 clip：`<asset-clip tcFormat="NDF" offset="0/1s" start="0/1s" ... duration="15/1s" format="r1">` + `<adjust-transform scale="1 1" anchor="0 0" position="0 0"/>` 子元素
- 音频 clip（gap 内）：`offset="3600/1s" start="6675/1s" ... duration="3302/25s" lane="1"`（offset/start 是媒体池源起点魔法值，不是时间线位置）

## gap 重叠陷阱（早前误判为"clip 数量上限"）

早期测试"3 clip 音频进（A1=1）、5 clip 音频丢（A1=0）"被误判为 spine 数量限制。**真相：gap 的 offset 写死与视频重叠**。修复：gap offset 必须紧跟前面视频 clip 结束位置（不重叠）。用达芬奇导出模板 + gap offset=视频总长，**46 clip + 音频全进（V1=46, A1=47）**——数量不是限制。

## 素材隐藏（visible=false → enabled="0"）

剪映 segment 有 `visible` 字段（默认 true，缺失=可见）。隐藏素材转 FCPXML 时 clip 加 `enabled="0"`：
```xml
<asset-clip ... enabled="0" .../>
```
达芬奇侧 `clip.GetClipEnabled()` 返回 false 可验证。草稿6 实测 7 个隐藏素材（visible=false）全部生效（V3/V4 轨上 3+3+1）。

## 多视频轨 attribute 陷阱

剪映多个视频轨的 `attribute` 可能**全为 1**（草稿6 的 4 条视频轨全 attribute=1）——不能按 attribute 区分主/叠加轨。**必须按轨道顺序分配 lane**：第1条视频轨 lane=0（主轨），第2/3/4 条 lane=1/2/3。轨道 `flag=2` 是叠加轨类型标志，不是隐藏标志。

## 达芬奇导出 FCPXML 金标准（音频必须模仿）

用 API 造含音频时间线再导出，得到权威模板：

```python
items = mp.ImportMedia([wav_path, mp4_path])
tl = mp.CreateEmptyTimeline('导出测试')
mp.AppendToTimeline([items[0]])  # 视频
mp.AppendToTimeline([items[1]])  # 音频
tl.Export(r'export.fcpxml', 5)   # 格式5 = FCPXML
```

导出文件关键结构（对照用）：
- `<fcpxml version="1.9">`，`<!DOCTYPE fcpxml>` 无 DTD 路径
- 音频 asset：**无 format 属性**，带 `audioChannels="2" hasAudio="1" audioSources="1"`
- 视频 asset：带 `format` 引用；视频 clip 上也有 `format="r1"` 属性
- 音频 clip 在 gap 里：`<gap offset="15/1s" start="3600/1s"><asset-clip offset="3600/1s" start="6675/1s" lane="1"/></gap>`
- media-rep src：`file://localhost/Z:/%E9%A1%B9...`（百分号编码中文/空格，盘符冒号明文）

注意：导入自己导出的文件 A1=1 成功；手工生成的同样结构若 media-rep 中文**未编码**，音频 clip 被丢弃（A1=0）——URL 编码是音频能进轨的必要条件之一。

## file duration 规则（坑 15 实测细节）

`<asset><duration>` 必须 = 对应 clipitem 的 `out` 值，**不是素材真实总帧数**。
- 失败例：素材 6.06s（181帧@30fps），clip in=54 out=111，asset duration 写 181 → 导入失败
- 修复：asset duration = 111（= out）→ 成功
- 手写成功版验证：file duration 与 out 完全一致（100/100、75/75）
- 注：asset duration 与 clip duration 是两个概念——asset 声明素材总长（向上取整），clip 声明片段用时长（帧/25s）

## HEVC 素材（坑 16 实测细节）

剪映「美图视频消除」AI 产物是 HEVC 8K：`第6集陈1_美图视频消除.mp4` = h265 4320x7680@30fps。
- 草稿6 素材编码分布：hevc×17 / h264×28 / png×1
- **FCP7 XML 导入 HEVC 素材失败**（fcp7 是 2011 格式，导入器按 H.264 解析 HEVC 失败）
- **FCPXML 导入 HEVC 成功**（format 声明 4320x7680 实测 ✓）
- 结论：格式必须 FCPXML；不能为多轨换 FCP7（虽然 FCP7 的 `<track>` 多轨很可靠，但不支持 HEVC）

## 达芬奇项目切换陷阱（2026-08-11 实测）

API 连的是 GUI 当前打开的项目。用户切到别的项目（《犬子无双》）后，同一 FCPXML 从"23段全进"变成"每轨1段"——调试前必须确认当前项目：
```python
pm = resolve.GetProjectManager()
print(pm.GetCurrentProject().GetName())
projs = pm.GetProjectsInCurrentFolder()   # {1: '模板', 2: '《魔王》', ...}
pm.LoadProject('《满级女总》')            # 同名返回 None 不报错，先确认存在
```

## 其他实测细节

- `RelinkClips(mpi_list, timeline_items)` 配对签名返回 False——API 的 RelinkClips 实际签名是 `([MediaPoolItem], folderPath)`，只移动媒体池项位置；GUI「从媒体夹重新套底」在 API 无直接等价
- `GetItemListInTrack('video', 1)` 是达芬奇 21 正确 API；`GetItemsInTrack` 返回对象不支持切片（KeyError）
- 时间线对象是媒体池里 `Type=时间线` 的 clip，可被 `MoveClips` 移动（实测 move/move-back 成功）
- 项目「模板」空时间线导出只有 545 字节（含 `FFVideoFormatRateUndefined` format）
- 测试教训：**同名时间线残留会让 ImportTimelineFromFile 返回 None 且无报错**——排查"导入失败"先列时间线查重名，再怀疑格式
- 未解决：草稿6 完整版（61 asset + 46 主轨 + 11 叠加 + 2 音频 gap）仍整体拒导；去掉 HEVC 17 个后仍失败（46 asset）——**某个特定素材或 asset+gap 组合未定位**，排查中（二分法：素材数量/clip数量/format引用已排除）
