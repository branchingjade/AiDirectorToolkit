---
name: jianying-draft-migration
description: 剪映草稿转达芬奇/PR 工程（FCPXML+SRT）。触发词：剪映导入达芬奇、剪映转PR、草稿迁移。
version: 1.0.0
author: hermes
license: MIT
category: post-production
metadata:
  hermes:
    tags: [post-production, davinci-resolve, jianying, fcpxml, video-editing]
    related_skills: [resolve-post-production]
---

# 剪映草稿 → 达芬奇/PR 工程迁移

剪映没有官方导出工程到其他 NLE 的通道（只能**导入** FCP/PR 工程，导出方向一直没做）。第三方工具（彩虹桥/LmBox）有 bug。**可行路径：直接解析剪映明文草稿 JSON，自写转换器生成 FCPXML**——剪映草稿除个别外均为明文 JSON，含完整时间线（剪辑点/字幕/音频）。

## When to Use

- 用户要把剪映里剪好的工程搬到达芬奇调色/精剪，或转到 PR/AE
- 触发词：剪映导入达芬奇、剪映转PR、剪映工程转换、草稿迁移、一键导入、剪映回批
- 彩虹桥等第三方工具失效/有 bug 时的自建替代方案

## 核心事实（本机实测 2026-08）

- 草稿位置：`%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft\<草稿名>\draft_content.json`
- **绝大多数草稿是明文 JSON**（本机 48 个草稿 47 个明文）；个别加密（剪映 6.0+ 特征）
- **加密草稿有明文备份**：按序尝试 `template.json` → `template.json.bak`（实测 808KB 完整时间线）→ `draft_content.json.bak` → `template-2.tmp`
- 素材路径用占位符 `##_draftpath_placeholder_XXX_##/materials/video/xxx.mp4`，**占位符 = 草稿目录本身**（须替换为绝对路径）
- 时间码单位：**微秒**（source_timerange=素材入点/时长，target_timerange=时间线位置/时长）
- 帧率：**顶层 `fps` 字段是硬指标——实测为 50**（《满级女总》51 集，子帧 20ms 精度）。**时间线必须输出 50fps**（`frameDuration="1/50s"`）+ **所有时间用微秒有理数** `{int(round(secs*1e6))}/1000000s`（子帧精度无损）——25fps 帧取整（`round(secs*25)/25s`）会因半帧位置产生 1 帧间隙（用户目视「很多间隙」抓出，2026-08-11 最终根因；2026-08-13 第5集起重导实证 50fps 微秒方案 0 间隙）。**⚠️ 早期方案「25fps + 主轨缝合并吸附」已废弃**（8-11 早中期产物；「50fps 会让 lane 错位」是误判，实为帧数/50s 写法的坑，微秒有理数无损）。**批量导入前必须 grep 转换器核查无 25fps 残留**（`frame_dur='1/25s'` / `round(secs*25)` / `timebase>25<` 任一命中 = 旧版，2026-08-13 实测转换器漂回 25fps 导致 5-51 集全错重导）。老草稿可能缺 fps 字段才需推断

## 数据结构速查

- `materials.videos/audios/images/texts/stickers`：id→素材对象（含 path/duration/width/height）
- `tracks[]`：type=video/text/audio/filter/effect；`segments[]` 每段含 material_id、source_timerange、target_timerange、speed、volume
- 字幕文本：texts 素材的 `content` 字段是 **JSON 字符串**，`json.loads(content)['text']` 取正文；`content['styles'][0]['size']` 取字号
- **photo 类型（定格图）也放在 materials.videos 里**，转换时按视频处理，否则定格片段丢
- 主视频轨判定：video 轨 `attribute==1`

## 转换器

正本：`C:\Users\HMSJ\Documents\Hermes\scripts\jianying2davinci.py`（git 归档，本 skill 不复制避免漂移）+ 一键入口 `jianying2davinci.bat`：

```bash
python jianying2davinci.py "草稿目录" [-o 输出.fcpxml] [--fps N] [--no-audio] [--no-text] [--no-srt]
```

产出：FCPXML 1.10（达芬奇 **File → Import → Timeline** 导入）+ 同名 `.srt`（达芬奇编辑页**直接拖入时间线上方自动生成字幕轨**，比 FCPXML title 可靠）。

## 坑（全部踩过，2026-08）

1. **占位符必须替换为草稿目录绝对路径**，且 draft_dir 必须 `os.path.abspath()`——否则 file:// URI 生成相对路径，达芬奇导入必脱机
2. **photo 素材 type 判断**：`mtype in ('video','photo')` 都要进资源收集
3. **字幕优先 SRT 路径**——达芬奇对 FCPXML title 元素支持一般，拖 SRT 最稳
4. **变速必须带 `<timebase>` 才套底**（2026-08-11 实测最关键发现）：`<rate><value>0.9</value><timebase>50</timebase></rate>`——**timebase 必须与时间线 fps 一致（50fps 时间线用 50）**。不带 timebase 的 rate 导致该片段不套底（实测第2集 18 个变速段：无 timebase 套底 1/36，加 timebase 后 36/36 且变速时长正确）。PR 端不支持（彩虹桥文档明说 PR 拿不到变速控件）
- **跨软件固有边界**（所有工具一致）：转场/滤镜/花字/美容/特效过不去，只保留剪辑点+素材入出点+字幕+音频；复合片段需先在剪映展开成扁平时间线
- **关键帧动画/轨道隐藏（2026-08-11 实测）**：《满级女总》51 集草稿 segment 里**无关键帧动画**（`clip.transform` 全是静态默认值）也无隐藏轨道（轨道 `flag=2` 是叠加轨标志，不是隐藏标志）。如后续项目有动画需增量开发——FCPXML motion 体系可表达简单变换关键帧，剪映 animate 字段与 FCP 不直接映射，属固有边界
- **变速必须带 `<timebase>` 才套底**（同上，与坑4一致）：`<rate><value>0.9</value><timebase>50</timebase></rate>`——timebase 与时间线 fps 一致（50fps 用 50）；不带 timebase 该段不套底（GetMediaPoolItem() 返回 None）
6. 达芬奇导入严格校验脱机素材——导入失败先查素材路径是否正确解析
7. 时间格式用 FCPXML 有理数秒 `N/1000000s`，别用帧数（避免 fps 换算误差）
8. **素材格式必须逐素材独立**：剪映素材常混用 24/30/48/60fps、720x1280/1080x1920，全指向单一 format 会崩；用 ffprobe 逐素材探测生成独立 format（fmt1 留画布默认，其余从 fmt2 起）
9. **FCPXML 布尔值只认 1/0**：`hasVideo="true"` 导致导入"成功"但空时间线（V1=0）——最隐蔽的坑
10. **media-rep src 冒号不能编码**：`file:///C%3A/...` 达芬奇不认（需 `safe='/:`），否则素材脱机
11. **多轨用 `lane` 属性，不用 `<sync>` 包裹**（2026-08-11 实测修正）：FCPXML 1.10 多轨正确写法是 spine 内 clip 直接带 `lane` 属性——`lane="0"`=主轨 V1、`lane="1"`=叠加轨 V2。`<sync>/<lane>` 包裹结构 V2 内容被达芬奇丢弃、`<sync>/<spine>` 只留 1 帧。**音频 clip 放 `<gap>` 里带 `lane="1"`**（达芬奇导出格式，实测 A1 成功）。详见「多轨与音频」节
12. **spine 内 title 有数量限制**（实测约 25-30 个超限拒绝）——字幕默认走 SRT
13. **剪映 audioAlg 产物可能损坏**：`*_human.wav` 等提取人声文件存在但 ffprobe 解析失败，达芬奇遇到即失败；素材可读性检查用 ffprobe（`-show_entries stream=codec_name`），不能只 `os.path.isfile`（转换器 `media_readable()` 已内置）
14. **GetClipProperty('Type') 返回中文**（「时间线」「视频 + 音频」），不能用 'Timeline' 判断；清理媒体夹时保留 Type 含「时间线」的对象，否则 DeleteClips 连坐删掉时间线对象
15. **file duration 必须等于 clipitem 的 out 值**（不是素材真实总长）：FCPXML `<asset><duration>` 写成素材总时长会导致导入失败，要写片段出点
16. **HEVC 素材边界**：草稿里可能有 HEVC（h265）8K 素材（如「美图视频消除」AI 产物 4320x7680，草稿6 有 17 个）——**FCP7 XML 导入 HEVC 失败，FCPXML 可以**（format 声明 4320x7680 实测 ✓）。所以格式必须选 FCPXML，不能为多轨换 FCP7
17. **drt/drp 无法外部生成**：达芬奇私有格式无公开规范，外部工具只能走 FCPXML/EDL/AAF 交换
18. **⚠️ 音频 gap 的 offset 不能与视频 clip 重叠**（2026-08-11 实测）：`<gap>` 的 offset 必须紧跟前面视频 clip 的结束位置（如视频总长后），否则音频丢失（A1=0）甚至整体拒导。早期误判为"spine 内 clip 超 4-5 个音频就丢"——真因是 gap offset 固定写死与视频重叠，不是数量。用达芬奇导出模板（gap offset=视频结束位）46 clip + 音频全进（A1=47）
19. **素材隐藏 = `visible:false` → clip `enabled="0"`**：剪映 segment 有 `visible` 字段（默认 true）；隐藏素材转成 FCPXML clip 的 `enabled="0"`，达芬奇 `GetClipEnabled()` 返回 false 可验证。草稿6 实测 7 个隐藏素材全部生效
20. **轨道隐藏 vs 叠加轨区分**：剪映轨道 `flag=2` 是**叠加轨标志**（V2+），不是隐藏标志；轨道级隐藏在这些草稿里未使用。多视频轨的 `attribute` 可能**全为 1**（草稿6 四轨全 attribute=1）——**不能按 attribute 分主/叠加轨，必须按轨道顺序分配 lane**（第1轨 lane=0，其余 lane=1/2/3...）
21. **达芬奇当前项目 ≠ 目标项目时导入行为异常**：脚本连上的是 GUI 当前打开的项目。若用户切到别的项目（如《犬子无双》），ImportTimelineFromFile 可能只进第一段/每段1帧。**调试前先 `GetProjectManager().GetCurrentProject().GetName()` 确认**；切项目用 `GetProjectsInCurrentFolder()` 列出 + `LoadProject('名')`（同名返回 None 不报错，先确认存在）
22. **批量导入触发达芬奇崩溃/弹窗卡死（2026-08-11 实测）**：全量连续导入 51 集时，某集（实测第23集）可能触发达芬奇**崩溃或弹窗**（旧式 PCM 头 wav 导入也曾在第1集触发弹窗）。症状：API 调用 `subprocess.run` 超时 300s（达芬奇在等 GUI 交互/已无响应）；**处理**：让用户点掉弹窗或重启达芬奇。**崩溃后恢复**：达芬奇重启后项目仍在（时间线不丢），但**媒体池状态可能损坏**——`ImportTimelineFromFile` 对任何 fcpxml 都返回 None（实测第5/6集都 None，而这两集此前导入成功）。恢复办法：重启达芬奇后**重新打开项目**（File→Open 或脚本 LoadProject），再试导入；仍 None 则需进一步检查媒体池。**批量导入中断后重跑**：`relink_all_episodes.py` 逐集跑，已完成集跳过会重复导入（脚本会删旧时间线重导），从失败集续跑即可
23. **单集导入失败（IMPORT_TL_FAIL）排查**：某集 fcpxml XML 合法、引用完整、素材在位，但 `ImportTimelineFromFile` 返回 None——先排除达芬奇状态损坏（用另一集 fcpxml 试导入，若也 None 则是达芬奇问题而非该集问题）；确认达芬奇正常后，对比该集与成功集的结构差异（asset 数量/同名合并/HEVC 素材）
24. **⚠️ 转换器版本漂移 → 用户要求「从第N集起重导」（2026-08-13 实测）**：8-11 定稿 50fps 微秒方案后，转换器曾漂回 25fps 旧版（`frame_dur='1/25s'`/`round(secs*25)`/timebase 25 残留）——第 1-4 集按定稿重导正确，5-51 集用旧版全带 1 帧间隙（用户目视抓出「从第五集开始后面都重新倒」）。**重导工作流**：①先 grep 转换器确认无 25fps 残留（`grep -nE "1/25s|/25s|fps = 25|round\(.*\* 25"`）②**扫描草稿目录核对 VALID_DIRS 与实际目录名**（见坑 25——剪映整理草稿后目录结构会变，硬编码名单必失效）③用 `batch_import_manlv.py <N> <M>` 批量重导（单遍法自动删旧时间线+清空素材夹）④导入进程内验证套底 N/N + 同进程查帧率=50、0 个 1 帧片段、0 主轨间隙（用户目视抓的正是这三项）。第5集实测：37/37 套底、50.0fps、0 间隙\n25. **草稿目录结构会变 → 批量脚本 VALID_DIRS 硬编码失效（2026-08-13 实测）**：剪映内整理草稿后，副本目录合并回主目录——`7 (1)`/`15 (1)`/`17 (1) (1)`/`33 (1)`/`37 (1)`/`44(1)`/`47 (1)` 全部消失，正片变为 `7`/`15`/`17`/`33`/`37`/`44`/`47`（主目录不再为空）。症状：`FAIL_CONVERT ✗ 草稿不存在: ...com.lveditor`（路径被截断，实际是目录名对不上）。**批量前必须先 `os.listdir(DRAFTS_ROOT)` 重建 VALID_DIRS**（`scan_jianying_drafts.py` 或内联扫描），不要信任上轮名单；`episode_of()` 正则从新目录名解析集数即可
26. **⚠️ 跨集同名素材冲突 → 大面积套底 0/N（2026-08-13 实测，新坑）**：剪映素材文件名高度重复——《满级女总》51 集跨集同名素材有 **44 组**（如 `3.mp4` 出现在 13 集、`7.mp4` 在 7 集、`9.mp4`/`12.mp4` 各 7 集）。达芬奇 `ImportTimelineFromFile` 按**媒体池全局文件名**判定"素材已存在"——素材先 `ImportMedia` 进池（或已在其他集的素材夹中）→ 新集导入时同名素材跳过创建也跳过关联 → 片段 0/N 套底。症状：`01素材/第N集` 夹内有素材（如 31 项），但时间线片段 `GetMediaPoolItem()` 全部 None。**区别于「素材不存在」（夹空）**——这里夹不空但片段仍不套底。**诊断**：跨集同名检查 `regex.*<asset[^>]*name="..." .* name`. fcpxml 提取全部素材名→`collections.Counter` 找多集共用名。**修复方向**（待验证）：asset `name` 加集数前缀（如 `第30集_26.1.1.mp4`）避免全局冲突；或先 `ImportMedia` 预导入到素材夹再导入时间线（8-11 放弃的两遍法，因"预导入不关联"但可先建立池项让新导入复用）
27. **⚠️ 批量连续导入时严格交替套底失败（2026-08-13 实测）**：严格 ✓✗✓✗✓✗ 模式——**手动跑同进程也复现**（29✓ 30✗ 31✓）。区别于 8-11 的"跨进程 1% 假象"：那是跨进程查返回 None，导入进程内都是 N/N；这次**导入进程内也交替 0/N**。最可能根因 = 坑 26（跨集同名素材冲突）：成功集导入后媒体池积累了该集素材（含通用短名如 `3.mp4`），下一集也有 `3.mp4` → 判定已存在→0/N；该集失败时素材未真正创建（副本复制到夹但不关联），再下一集的通用名在媒体池不存在 → 成功。**交替间隔随素材名分布变化**（34✗ 35✗ 两个连续失败打破了严格交替——它们的素材名覆盖了前两集的通用名）。**重启达芬奇后第一次导入成功**（媒体池缓存清空），连续导入后交替恢复。修复方向同坑 26——消除跨集同名。**用户 GUI 目视确认是最终判据**：API 0/N 可能同时包含真失败和假象混合，达芬奇 GUI 里片段非灰/非红=实际 OK
28. **collect_materials 必须递归 main_draft 的 drafts 嵌套**（2026-08-13 第38集实测）：子草稿 segment 引用的素材定义可能藏在**主草稿 combination draft 的内嵌 draft** 里——38 集三个复合片段素材（45C13C3D/C96B35C3/AF888DFD，均为 `is_copyright=true` AIGC 版权素材）在主草稿顶层 videos 没有、子草稿也没有，只在 `main_draft.materials.drafts[].draft` 嵌套层。原实现只对 main_draft 取顶层 videos/images/audios → 素材收集不到 → 「素材不可达」渲染失败。修复：收集逻辑抽成 `_collect_from(draft_obj, mats)`，对 main_draft 和 sub_draft 都递归嵌套 drafts
29. **素材名空但 path 含文件名 → resolve 兜底从 path 尾部提取**（2026-08-13 第38/47集实测）：AIGC 复合片段素材的 `name`/`material_name` 为空，path 指向云缓存 `D:/新建文件夹/JianyingPro Drafts/.cloud_cache_*/<集>/materials/video/<file>.mp4`（本地不存在），**真身在本地草稿 `<集>/materials/video/<file>.mp4`**（如 4a.mp4/6.mp4/06.mp4/王.mp4）。`resolve_source_path` 云缓存兜底原来只按 `mat['name']` 搜文件（空 → None → 渲染失败）；修复：name 为空时 `re.search(r'/materials/(video|image|audio)/([^/]+)$', p)` 从 path 尾部提取文件名，再按名在草稿树全搜（subdraft/ 与 materials/ 两棵树）
30. **嵌套引用主草稿复合片段 → expand_segments 按素材名在主草稿 drafts 展开**（2026-08-13 第17集实测）：复合片段 A 的子草稿里某 segment 引用**另一个复合片段素材**（如 name='复合片段1'、path 空），当前子草稿无对应嵌套 draft → 渲染「素材不可达」。修复：`expand_segments` 加 main_draft 参数，path 空且本地嵌套找不到时，在 `main_draft.materials.drafts` 里找 `inner.name == 素材名` 的 combination，`extract_subdraft` 展开其子草稿递归（17 集 draft7 name='15' 引 3C84D87B name='复合片段1' → 展开 6B9610E9 子草稿）。修复后 17 集 8/8 渲染成功、映射 5 条全齐
31. **渲染成功 ≠ 映射正确**（2026-08-13 第17集教训）：render_compounds 主流程映射逻辑是 `draft.name == 主草稿 path 空素材的 material_name`——draft name 为空/数字时匹配不上，**即使全部渲染成功 compound_map 也可能只有 1 条**（17 集曾 8/8 渲染成功但映射仅 1 条，5 个 path 空素材只映射 1 个）。转换器按 `mid in compound_map` 查，缺映射的素材时间线上仍缺。**重导前必须核对 `compound_map_<集>.json` 条数 == 主草稿 path 空素材数**（不一致先补映射再导，fix_compound_map.py 按 draft.name 匹配可复用）

## 多轨与音频（FCPXML lane 属性 + 达芬奇导出金标准，2026-08-11 实测）

**音频需求（用户拍板）**：只迁移剪映的 **audio 类型轨道**（混录音轨等）；**视频素材自带的声音直接丢弃**——视频 asset 不需要声明音频（`hasAudio` 处理简化），只有剪映 audio 轨的素材进音频轨。

多轨正确写法——spine 内 clip 直接带 `lane` 属性（不是 sync 包裹）。⚠️ 下方示例的 `<gap>` 包裹写法**已弃用**（gap 是达芬奇导入器硬限制，见「音频最终方案」），仅作 lane 结构对照：

```xml
<spine>
  <asset-clip name="a.mp4" ref="r2" offset="0/1s" start="0/1s" duration="15/1s" format="r1"/>
  <gap offset="15/1s" start="3600/1s" name="Gap" duration="3302/25s">
    <asset-clip name="混录.wav" ref="r3" offset="3600/1s" start="6675/1s" duration="3302/25s" lane="1"/>
  </gap>
</spine>
```

- 视频主轨不写 lane（=0）；叠加视频轨 `lane="1"`；**音频 clip 放 `<gap>` 里带 `lane="1"`**
- 音频 asset **不带 format 引用**，带 `audioChannels="2" hasAudio="1" audioSources="1"`
- 音频 asset-clip 的 `offset`=素材源起点（如 3600/1s），`start`=媒体池素材入点，与 gap 的 `offset`（时间线位置）不同
- media-rep src：`file://localhost/Z:/%E9%A1%B9...`——**中文/空格百分号编码、盘符冒号明文**（`urllib.parse.quote(path, safe='/: ')`）；未编码中文路径导致音频 clip 被丢弃
- **时间必须全用有理数**：clip/gap 的 `duration` 写 **微秒有理数**（`2840000/1000000s`）或 帧数/帧率（`142/50s`）；**`offset`/`start` 必须微秒有理数**（`"{int(round(secs*1e6))}/1000000s"`）——剪映 start 多为小数秒（1.9s/4.23s），**秒取整（`round(s)/1s`）产生时间线空隙/重叠**（实测 46/50 段非整数秒，主轨出现空隙用户一眼看穿）；**浮点秒（`4.000s`）会把每段解析成 1 帧**（时间线"成功"但每个片段都是 1 帧）——这是本会话最隐蔽的两个坑。**时间线 fps 必须是 50**（剪映 fps=50 子帧精度）：25fps 下即使帧精度（round(secs*25)/25s）仍会因半帧位置取整产生 1 帧间隙（用户目视"很多间隙"抓出，2026-08-11 最终根因）
- **⚠️ 音频 gap 是达芬奇 FCPXML 导入器的硬限制（2026-08-11 实测）**：`<gap>` 内音频 clip 在**视频 asset hasAudio=0（纯视频）时永远进不了时间线**（A1=0）；hasAudio=1 时只有视频素材自带音频进（A1 被视频音频占满），gap 混录仍不进。**结论：音频不要用 `<gap>` 包裹，用 asset-clip + `audioRole` 直接放 spine**（见「音频最终方案」）——简例与第1集全量均验证成功（A1-A4 与剪映一致），API 追加方案（CreateEmptyTimeline + AppendToTimeline）仅空时间线有效
- **音频最终方案（2026-08-11 会话终局，用户拍板）**：**视频+音频一体导入**（转换器默认输出，勿加 `--no-audio`）——剪映音频轨用 **asset-clip + `audioRole="dialogue"` 直接放 spine**（无 gap/lane），视频 asset `hasAudio="0"` 丢弃视频自带音频，实测第1集 A1-A4 四轨与剪映一致（混录/音乐/音效）。**脱机音频由用户 GUI 手动处理**——用户原话「音频脱机的我后面手动处理」「最后一步你别管了」。**不要在音频上过度工程化**（本会话教训：为修 A4 脱机反复折腾重编码/拆 asset/API 重链，被用户两次叫停；agent 一度加 `--no-audio` 纯视频导入被纠正——用户原话「单独填音频轨道，这不是之前测试过的吗」）。GUI 可靠路径（用户实测 1 次成功 3 段全链上）：达芬奇菜单 **文件 → 从媒体夹重新套底**——选中脱机音频片段 → 右键取消套底锁定 → 重新套底选媒体池项（**不指定文件**，选媒体池里的同名素材）→ 全部链上。API 无法复刻此操作：`SetClipsLinked(False)→UnlinkClips→RelinkClips(池项,文件夹)→SetClipsLinked(True)` 四步返回全 True 但 `GetMediaPoolItem()` 仍 None；`SetClipsLinked` 对未锁定片段返回 False（该片段本就没锁）。转换器 `--no-audio`（纯视频）/`--audio-only`（纯音频）参数仅作备用，不是默认方案
- **旧式 PCM wav 头（fmt_size=16）陷阱（2026-08-11 实测）**：达芬奇导入时对旧式标准 PCM 头 wav **不建立池项关联**（导入后音频片段脱机，即使文件存在且 ffprobe 正常、渲染有声）。EXTENSIBLE 头（fmt_size=40 / audio_format=65534）单 clip 正常。**ffmpeg 重编码默认仍输出 fmt=16**，须加 `-write_bext 1` 才输出 EXTENSIBLE（`ffmpeg -i in.wav -c:a pcm_s24le -write_bext 1 out.wav`）。但**重编码是绕远路**：多 clip 共享同一音频 asset（同一素材切成多段，如 1.wav×3）时无论什么头都脱机——达芬奇只按文件建 1 个池项，多个时间线片段引用同一池项不自动关联（视频多 clip 共享可 52/52，音频不行）。用户 GUI「从媒体夹重新套底」一次解决，无需重编码
- **asset 的 duration 用秒有理数且向上取整**（`int(dur)+1/1s`），必须 ≥ 该素材 clip 的用时长，否则整体拒导（clip 时长超出 asset 声明 → 导入失败）
- **验证方法**：用达芬奇 API 造一条视频+音频时间线（`CreateEmptyTimeline` + `AppendToTimeline`）→ `Export(fcpxml, 5)` → 拿到的导出文件就是金标准模板，直接对照

## 套底（Conform）——导入后必须验证片段是否关联媒体池项

**「未套底」≠「脱机」**：脱机=素材文件找不到（变灰/变红）；未套底=素材文件在媒体池好好的，但时间线片段 `GetMediaPoolItem()` 返回 None——无法调色/回批。**只验证"文件存在"会漏掉未套底**（本会话实测 51 集全踩）。

### 验证（必须查媒体池项，不能只看路径存在）
```python
tl = proj.GetTimelineByIndex(i)
for c in tl.GetItemListInTrack('video', 1):
    if c.GetMediaPoolItem() is None:
        print('未套底!', c.GetName())
```

### 根因
**ImportTimelineFromFile 不会自动 relink 到媒体池中已存在的素材**。素材先 ImportMedia 进池、再导时间线时，达芬奇跳过导入但也跳过关联 → 片段全未套底。反之素材不在池中时导入会自动创建并链接（100% 套底）。

### 清空池项单遍法（2026-08-11 最终确认，比两遍法更干净）
```
1. 删旧时间线（重名导入失败）
2. SetCurrentFolder(01素材/第N集)          ← 当前夹必须是素材夹
3. 循环清空该夹所有媒体池项直到 0 项（见下） ← 素材由导入自动重建
4. 再次 SetCurrentFolder(素材夹)（2026-08-11 最后确认的关键步骤）
5. ImportTimelineFromFile(fcpxml)           ← 素材不存在 → 达芬奇自动创建到当前夹 + 100% 套底
6. MoveClips(时间线对象, 00时间线)          ← 时间线对象是 Type=时间线 的 clip，导入时创建在素材夹，必须移走（否则下次导入素材夹残留时间线对象 → 素材不重建 → 不套底）
```

**⚠️ 删除素材后当前夹会失效**（2026-08-11 血泪教训）：`DeleteClips` 清空素材后，达芬奇内部会把当前夹重置（不再指向素材夹）。若在清空后直接导入，素材被创建到错误位置（根/00时间线），片段全部不套底——批量脚本最初 SetCurrentFolder 写在删除**之前**，第1集套底 1/52；把 SetCurrentFolder 移到循环清空**之后、导入之前**重置，第1集变 52/52。顺序铁律：**Set → 清空 → 再 Set → 导入**。
实测：清空 68 项 → 导入 → 自动创建 46 项（去重后）→ V1 50/50 全套底，素材正确落在 01素材/第N集，00时间线 无重复素材。**批量脚本最终采用此流程**（不再预 ImportMedia——预导入的素材不会被关联）。

**⚠️ 清空必须循环 DeleteClips 直到 GetClipList 为 0**：单次 `DeleteClips` 删不干净（素材被时间线引用时残留索引），残留 1 个旧素材项 → 导入时达芬奇认为素材"已存在" → 跳过创建也跳过关联 → 该集全片段不套底（实测：清到 0 则 37/37，清剩 1 则 1/37）。删除后 `time.sleep(1)` 再查。顺序上**先删时间线再删素材**（时间线引用素材时素材删不掉）。

### ⚠️ 套底验证必须在导入同一进程内（2026-08-11 最隐蔽的误报源）
达芬奇 API 的 `GetMediaPoolItem()` **跨进程会话查询会返回 None**——用另一个脚本（新进程）去查刚导入的时间线，全部片段显示"未套底"，但实际套底是成功的。本会话曾因此把"全部成功"误判为"全部失败"，来回全量重导 4 轮。
**正确验证**：在 `ImportTimelineFromFile` 的**同一脚本进程内**立即遍历查 `GetMediaPoolItem()`。批量脚本应把验证写进导入流程（导入后打印 `套底 N/N`），不要靠外部脚本二次验证。

**⚠️ 全量连续导入（51 集连跑）后跨进程查询全部显示 1% 套底，是达芬奇 API 假象，不是真失败**（2026-08-11 终局确认）：无论单遍/两遍/逐集重跑，全量跑完后跨进程查询都会显示每集只有 1 段套底；但导入进程内每集输出都是 N/N（如 52/52、37/37）。时间线内容实际完整（段数正确），套底在导入瞬间已建立。**判断批量结果只看每集脚本输出的"导入进程内套底 N/N"，跨进程/导出 FCPXML 验证均不可信**（达芬奇导出 FCPXML 也可能只导出 1 个 clip，属导出拍平 bug，不代表时间线丢内容）。用户实际关心的是达芬奇 GUI 里片段能否调色——API 查不到就请用户目视抽查（片段非灰/非红即可）。

### 两遍法修复（旧方案，已弃用）
```
1. 删旧时间线（重名导入失败）
2. SetCurrentFolder(01素材/第N集)   ← 当前夹必须是素材夹
3. ImportTimelineFromFile(fcpxml)
4. MoveClips(时间线对象, 00时间线文件夹)  ← 时间线对象是 Type=时间线 的 clip，可被 MoveClips 移动
5. 重跑 1-4 一遍（第一遍建立匹配关系只套底少数，第二遍全套底：实测 6/51 → 51/51）
```
- API 事实：`RelinkClips([MediaPoolItem], folderPath)` 只是移动媒体池项位置，不是时间线片段套底（配对签名返回 False）；GUI 的「从媒体夹重新套底」在 API 无直接对应
- 批量脚本：`C:\Users\HMSJ\Documents\Hermes\scripts\relink_manlv.py`（含 --skip= 参数，旧两遍法）；新批量入口 `batch_import_manlv.py`（清空池项单遍法）

### 时间线"空隙/黑块"的三种来源（2026-08-11 排查结论）
1. **offset 秒取整** → 主轨空隙（已修：帧精度，见「多轨与音频」节）
2. **叠加轨（V2+）天然空隙** → **正常现象**，不是 bug：剪映叠加轨本就只覆盖部分时间（草稿6 的 V2 只覆盖 13-67s），未覆盖区达芬奇显示黑色，剪映里同样存在
3. **复合片段/特效素材无法迁移** → 时间线留空：`material_name` 含「复合片段」或纯数字名（如"13"/"15"）且 **path 为空的素材**（剪映内部生成无源文件）FCPXML 无法表示。全 51 集实测 99 个（76 复合片段 + 23 特效），分布在 23 集（最多第32集 17 个）。**渲染管线已开发**（`render_compounds.py` 把子草稿 ffmpeg 渲染成 mp4 → 生成 `rendered/compound_map_<集>.json` → 转换器加载映射用渲染产物替代 path 空素材）。**⚠️ `scripts/rendered/` 目录是转换器运行依赖**（含 compound_map_*.json + 渲染 mp4）——2026-08-12 清理 scripts/ 时被误删（当调试产物），导致 94 个复合片段全部缺位。**清理 scripts/ 时必须排除 `rendered/` 子目录**。重新渲染：`python render_compounds.py <起集> <止集>`（需要子草稿素材在位——草稿目录 `subdraft/<uuid>/`；云缓存素材需剪映同步后才能渲染）。诊断缺位数：`python scan_jianying_drafts.py` 或内联扫描 path 空素材计数。这是固有边界，排查空隙先查该位置素材是否 path 为空

## 第三方工具对比（2026-08）

| 工具 | 问题 |
|---|---|
| 彩虹桥（LmBox，sockite.com） | 有 bug 用户实测不可用；高版本草稿需剪映内"保存为预设"绕加密（预设 draft_content.json 明文）；免费但不在会员计划不保证需求 |
| Jianying-CapCut2XML（GitHub Ersiter） | 素材路径占位符没处理（导入必脱机）、字幕全丢、素材重复计数 |

## 验证方式

- XML 合法性：`xml.dom.minidom.parse`
- 素材存在性：解析每个 media-rep src → `urllib.parse.unquote` → `os.path.isfile`
- SRT：按空行分块数 + 时间戳正则 `\d+$` / `-->`
- **套底验证（最重要）**：达芬奇导入后查每个片段 `GetMediaPoolItem()` 非 None——只验证文件存在会漏掉未套底（详见「套底（Conform）」节）。**必须在导入同一进程内查**：跨进程查询全部返回 None，是误报源（本会话曾因此误判全量失败重导 4 轮）
- **用户目视检查（本会话血泪教训）**：用户会逐集打开达芬奇时间线看——"每个片段只有一帧"（duration 浮点）、"时间线空白"（offset 秒取整）、"黑的地方"（叠加轨空隙/复合片段）。API 数据验证（段数/时长）**不足**，交付前必须自查：每段帧数非 1、主轨相邻段 offset 连续、变速段带 timebase 套底正常
- **⚠️ 验收标准分层（2026-08-13 用户拍板）：脱机可接受，视频内容必须一致**——用户原话「现在我可以接受脱机，但不能接受视频不一致」。含义：①套底 0/N（片段未关联池项）**不是阻塞项**，调色时可 GUI 手动套底；②时间线上的**内容**（段数/每段时长/顺序/复合片段补齐）必须与剪映草稿一致——缺段、1 帧片段、错位、复合片段留空都是必须修的硬伤。**内容一致性对账方法**：剪映草稿各视频轨段数（`tracks` type=video 的 segments 数列表）vs 达芬奇 V1-V5 各轨 `GetItemListInTrack('video', N)` 长度列表**逐轨相等**。⚠️ 只查 V1 会误报"缺段"——叠加轨的段在 V1 里不算（第8集剪映 [43,4] 达芬奇 V1=43 曾被误判缺 4 段，实际完全一致）。差值 = 复合片段/特效数 = 需渲染补齐的量
- **片段级帧数/间隙 API（2026-08-13 实测）**：`GetStartFrame()/GetEndFrame()` 是**时间线级** API；**片段（TimelineItem）级要用 `c.GetStart()/c.GetEnd()`**——`c.GetStartFrame()` 在达芬奇 21 报 `TypeError: 'NoneType' object is not callable`（方法不存在）。自查脚本：`s,e=c.GetStart(),c.GetEnd(); if e-s<=1: 1帧片段++`；主轨间隙：`if s>prev_end+1: gaps++; prev_end=max(prev_end,e)`；帧率 `tl.GetSetting('timelineFrameRate')` 应为 50
- 达芬奇自动化：**Studio 版（21.0.2.4 实测）有脚本 API 可全程自动化**——Python 3.12 + `fusionscript.dll`，连接前提：Resolve 运行中 + Preferences External Scripting = Local + 安装时勾选 Developer/Scripting。免费版无 Developer/Scripting 目录=无脚本 API。桥文件 `C:\Users\HMSJ\scripts_dvr\DaVinciResolveScript.py`；`GetItemListInTrack('video', 1)` 是达芬奇 21 的正确 API（`GetItemListInTimeline` 已废弃）。**⚠️ Python 3.12 直接 import 桥文件必失败**（内部 `spec_from_file_location` 对 `.dll` 返回 None）——正解配方见 `references/resolve-script-python312.md`（ExtensionFileLoader 显式加载 + scriptapp None 三层排查）

## References

- `references/resolve-script-python312.md` — Python 3.12 连接达芬奇脚本 API 的正解（fusionscript.dll ExtensionFileLoader 配方、错误症状、scriptapp None 三层排查）
- `references/compound-clip-rendering.md` — 复合片段渲染方案（子草稿解析、ffmpeg 配方、**2026-08-13 四个实测 bug 修复**：映射按 draft.name、collect_materials 递归 main_draft 嵌套 drafts、resolve_source_path 三种 path 形态+名空从 path 提取、expand_segments 嵌套引用展开；**渲染成功≠映射正确**校验；重渲染恢复流程）
- `references/draft-json-structure.md` — draft_content.json 字段详解（materials/tracks/segment 全键、加密回退、预设路径）
- `references/manlv-batch-import.md` — 《满级女总》51 集批量导入实战记录（media-root 素材迁移、草稿→集数映射、两遍法套底修复、达芬奇 API 关键事实、时长换算）
- `references/fcpxml-multitrack-audio-hevc.md` — FCPXML 多轨/音频/HEVC 实测记录（lane 属性写法、达芬奇导出金标准格式、**时间有理数规则（浮点→1帧）**、gap 重叠陷阱、素材隐藏 enabled=0、file duration 规则、FCP7 vs FCPXML 编码边界、达芬奇项目切换陷阱）

> 注：姊妹 skill `jianying-to-davinci`（user-owned）正文里"浮点 duration 兼容/音频走 spine"等表述已被本 skill 修正——以本 skill 为准。如需同步请 `hermes curator adopt jianying-to-davinci` 后前台编辑。
