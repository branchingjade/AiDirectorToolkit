# 复合片段渲染方案（2026-08-11 实测打通）

## 背景

复合片段素材特征：`material_name` 含「复合片段」、`path` 为空、有 `extra_material_refs`。FCPXML 无法直接表示 → 转换器跳过 → 时间线留空（用户看到"黑的地方"）。

## 关键发现：子草稿数据可解析、源文件是真实文件

- `materials.drafts[].draft` 内嵌子草稿完整时间线（tracks/segments：material_id + source_timerange + speed）
- 子草稿独立文件：`<草稿目录>/subdraft/<uuid>/draft_content.json`——**uuid 从 `draft_config_path: subdraft/<uuid>/sub_draft_config.json` 取，不是 `combination_id`！**（草稿2 实测 combination_id=6C6A0374 但目录是 821CCD74-…）
- 子草稿 `materials.videos` 里素材的 `path` 是真实文件：`C:/Users/HMSJ/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft/<N>/materials/video/<原名>.mp4`（material_name 与草稿本地素材同名，如 2.14.1.mp4）
- 注意：草稿目录名可能是 `7 (1)` 这种带括号的，路径拼接不要丢

## 渲染配方（第2集 2.84s 复合片段实测 → 2.94s mp4 成功）

子草稿 segments 例：
- seg1: speed=0.8 src_start=3.48s src_dur=0.83s → 时间线 1.04s
- seg2: speed=0.9 src_start=4.40s src_dur=1.62s → 时间线 1.80s

逐段 ffmpeg（变速用 setpts + atempo）：

```bash
ffmpeg -y -v error -ss 3.48 -t 0.83 -i "<src>" -filter:v "setpts=PTS/0.8" -af "atempo=0.8" -r 25 -c:v libx264 -preset fast -c:a aac rendered/seg1.mp4
ffmpeg -y -v error -ss 4.40 -t 1.62 -i "<src>" -filter:v "setpts=PTS/0.9" -af "atempo=0.9" -r 25 -c:v libx264 -preset fast -c:a aac rendered/seg2.mp4
```

concat（**git-bash/MSYS 坑**：进程替换 `<(echo ...)` 不可用；concat 文件里必须写**绝对路径**，相对路径会解析成 `rendered/rendered/...` 直接失败）：

```
# concat.txt（每行一个 file 指令，绝对路径）
file 'C:/Users/HMSJ/Documents/Hermes/scripts/rendered/seg1.mp4'
file 'C:/Users/HMSJ/Documents/Hermes/scripts/rendered/seg2.mp4'

ffmpeg -y -v error -f concat -safe 0 -i concat.txt -c copy rendered/compound_<name>.mp4
```

## 转换器接入点

检测 `material_name` 含「复合片段」且 path 空 → 解析 `materials.drafts` → 逐段 ffmpeg 渲染成普通 mp4（建议命名 `<集>_compound_<N>.mp4`）→ 转换器把该 segment 引用渲染产物（按普通素材处理）。

## 范围与边界

- 全 51 集 76 个复合片段（第32集 17 个最多；草稿14 有 44 段的复杂复合——逐段变速/裁剪拼接可行，但内部转场/特效会丢，属固有边界）
- 23 个纯数字名素材（"13"/"15"）是特效/贴纸，path 空且无子草稿 → **无法渲染，仍留空**
- 渲染耗时：单片段秒级（libx264 fast preset），全量可控
- 关联 SKILL.md：空隙来源 #3「复合片段/特效素材 → 时间线留空」一节（2026-08-11 更新）

## ⚠️ render_compounds.py 三个实测 bug 修复（2026-08-13 重渲染 94 个复合片段时发现）

### Bug 1：映射逻辑把所有素材 id 指到最后一个产物（最严重）

旧代码把渲染产物赋值给**所有** path 空素材：`for v in ...: mapping[v['id']] = out` → 多复合片段集全部指向最后一个产物（实测第32集 17 个素材全映射到 `32集_复合片段10.mp4`）。

**正确映射键 = `draft.name`**：`materials.drafts[].draft.name`（如"复合片段8"）与主草稿 path 空素材的 `material_name` 一一对应。同名同 duration 的多个素材（同一复合片段多次使用，如"复合片段8"×4）共享同一产物——这是**正确行为**，不是重复。修复后第32集 17/17 精确匹配。独立的修复脚本 `scripts/fix_compound_map.py`（按 name 重建映射，产物已渲染时不必重渲染）。

### Bug 2：collect_materials 只收集子草稿素材 → 45C13C3D 素材不可达

子草稿 segments 可能引用**主草稿**定义的素材（8-11 遇过 45C13C3D，13 集复发）。`collect_materials(sub_draft)` 必须加 `main_draft` 参数**先合并主草稿 materials** 再递归嵌套 drafts：`collect_materials(sub_draft, main_draft)`。

**⚠️ 2026-08-13 加深（第38集）**：只合并 main_draft **顶层** videos/images/audios 仍不够——素材定义可能藏在**主草稿 combination draft 的内嵌 draft** 层（38 集三个 AIGC 复合片段素材 45C13C3D/C96B35C3/AF888DFD，顶层/子草稿都没有，只在 `main_draft.materials.drafts[].draft` 嵌套）。终版实现：抽 `_collect_from(draft_obj, mats)`，对 main_draft 和 sub_draft **都**递归嵌套 drafts。

### Bug 3：resolve_source_path 三种未覆盖的 path 形态

子草稿素材 path 除占位符形态外还有：

1. **嵌套子草稿素材目录**：`##_draftpath_placeholder_..._##/subdraft/<uuid>/materials/<sub>/<name>`（第14/17集实测）——真实文件在 `<草稿>/subdraft/<uuid>/materials/video/<name>`，按 uuid+name 拼接
2. **目录形态 path**：`.../subdraft/<uuid>/materials`（结尾无文件名，第14集实测）——按 `material_name` 在 `subdraft/<uuid>/materials` 下 os.walk 全搜
3. **云缓存路径**：`D:/新建文件夹/JianyingPro Drafts/.cloud_cache_<id>/...`（本地不存在）——检测 `.cloud_cache` 或 `not os.path.exists(p)` 后，按文件名在草稿树（subdraft/ + materials/）os.walk 兜底

**⚠️ 2026-08-13 补充（第38/47集）**：AIGC 复合片段素材的 `name`/`material_name` 常为**空**——按 name 搜直接 None → 渲染失败。修复：name 为空时 `re.search(r'/materials/(video|image|audio)/([^/]+)$', p)` 从 path 尾部提取文件名（4a.mp4/6.mp4/06.mp4/王.mp4 等），再按名全搜。真身在本地草稿 `<集>/materials/video/<file>`（云缓存路径本身不存在）。

修复后第14集（260MB 大复合片段）、第17集（2→6 成功）、第38集（0→3）、第47集（0→5）均渲染成功。

### Bug 4：嵌套引用主草稿复合片段 → expand_segments 展开（2026-08-13 第17集）

复合片段 A 的子草稿里某 segment 引用**另一个复合片段素材**（name='复合片段1'、path 空），当前子草稿无对应嵌套 draft → 「素材不可达」。修复：`expand_segments` 加 main_draft 参数，path 空且本地嵌套找不到时，在 `main_draft.materials.drafts` 找 `inner.name == 素材名` 的 combination，`extract_subdraft` 展开其子草稿递归（17 集 draft7 name='15' 引 3C84D87B name='复合片段1' → 展开 6B9610E9 子草稿）。修复后 17 集 8/8 渲染成功、映射 5 条全齐。

### ⚠️ 渲染成功 ≠ 映射正确（2026-08-13 第17集教训）

主流程映射逻辑 `draft.name == 主草稿 path 空素材的 material_name`——draft name 为空/数字时匹配不上，**即使全部渲染成功 compound_map 也可能只有 1 条**（17 集 8/8 渲染成功但映射仅 1 条，5 个 path 空素材只映射 1 个）。转换器按 `mid in compound_map` 查，缺映射的素材时间线上仍缺。**重导前核对 `compound_map_<集>.json` 条数 == 主草稿 path 空素材数**。

### 重渲染流程（rendered/ 被误删后的恢复）

```
python render_compounds.py <起集> <止集>    # 渲染 + 生成 rendered/compound_map_<集>.json
python fix_compound_map.py 1 51             # 若映射仍乱（旧产物已渲染），只重建映射 json
# 转换器自动加载 rendered/compound_map_<集>.json（路径：脚本同目录 rendered/）
# 验证：转换后 grep fcpxml 应出现 "<集>集_复合片段N.mp4" 引用
```
