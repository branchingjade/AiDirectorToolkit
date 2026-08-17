# 实测案例：《满级女总》51 集草稿批量删除（2026-08-14）

## 症状

用户：「修复剪映」。无更多上下文——先诊断后问。

## 调查路径（按实际执行顺序）

1. **进程检查**：`tasklist | grep -i jianying` → 11 个 JianyingPro.exe 进程在跑，主窗口「剪映专业版」`Responding=True` → 剪映本体没坏。
2. **草稿目录**：`com.lveditor.draft/` 只剩 `root_meta_info.json` + `.cloud_cache_<uid>/` + `.recycle_bin/`——51 集草稿文件夹全空。
3. **注册表**：`root_meta_info.json` 显示 `draft_ids: 2` 但 `all_draft_store: []`——剪映认为草稿列表空。
4. **映射配置**：`Config/LocalDraftFolder/draft_folder_mappings.json` 和 `folder_meta_info.json` 的 mappings/folders 均为空数组，timestamp `2026-08-14T10:41:56`——10:41 被重写。
5. **操作日志（破案关键）**：`Log/draft_acion_watch.json`（82KB，10:41 最后修改）：
   - 类型计数：58 `delete_draft` + 55 `move_draft_to_trash` + 53 `import_draft` + 7 `rename_draft` + 2 `create_draft`
   - move 时间戳：55 条全部 `08-14 10:41:48`（同一秒）
   - delete 时间戳：58 条全部 `08-14 10:41:54-59`（6 秒内）
   - → **11 秒内批量「移入回收站 + 清空回收站」= 全选删除操作**，非崩溃（崩溃不会产生 113 条有序操作记录）
6. **回收站排查**：剪映 `.recycle_bin/` 只剩 root_meta_info.json（空壳）；Windows 回收站 `$I*` 元数据解析只有零星 mp4/md（无草稿）——剪映彻底删除不进 Windows 回收站。
7. **恢复资产盘点**：
   - `scripts/manlv_import/` 51 个 fcpxml + 50 个 srt + manifest（8月13 转换产物，时间线完整备份）
   - Z 盘 `01素材/` 素材完整（抽查第5集 30 文件在位）
   - `.cloud_cache_<uid>/` 4 集完整草稿：`1`（521KB）、`1 (1)`（595KB）、`6`（437KB）、`51`（200KB），均含 draft_content + materials + draft_cover
   - 缺：ep01.srt（当时没生成，可重新导）

## 零风险抢救（先做，不等用户确认）

把云缓存 4 集复制到 `Documents/Hermes/剪映草稿恢复备份/`（1.8GB）——防止剪映后续清缓存二次丢失。用户确认前不动剪映目录本身。

## 判定

人为批量删除（误触全选→删除→清空回收站），非剪映 bug、非崩溃。剪映 11.2.0.14339，10.5.0.13988 旧版本目录残留无关。

## 恢复方案（给用户的三个选项）

- **A. fcpxml 反向重建剪映草稿**：51 集 fcpxml → 剪映草稿 JSON（需写反向转换器，工作量大，兼容度待实测）
- **B. 继续用达芬奇**（推荐）：8月13 已导入达芬奇，fcpxml+srt+素材都在，剪映草稿 JSON 只是编辑源文件
- **C. 磁盘恢复**：JSON 小文件 + SSD + 已写入备份 → 成功率低

## 可复用要点

- `draft_acion_watch.json` 是剪映草稿操作的全量审计日志，诊断「草稿怎么没的」第一优先级
- 时间戳 `time_nsec` 是微秒：`datetime.fromtimestamp(ns/1e6)`
- 批量操作特征：同秒内几十条相同 type 记录
- 云缓存目录名 = 草稿名（`1`、`1 (1)`），非草稿 ID——按名称对应
