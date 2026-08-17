---
name: jianying-draft-recovery
description: 剪映草稿丢失/草稿列表为空/剪映打不开时诊断与恢复。触发词：修复剪映、剪映草稿丢了、草稿没了、草稿列表空、剪映草稿恢复。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  tags: [剪映, 草稿恢复, 数据诊断, post-production]
  related_skills: [jianying-to-davinci, jianying-draft-migration]
---

# 剪映草稿丢失诊断与恢复

## When to Use

用户说「修复剪映」「剪映草稿没了」「剪映打开草稿列表是空的」「草稿打不开/找不到了」。先诊断后恢复——**大多数情况下剪映本体没坏，是草稿被删/被移动**。不要急着卸载重装。

## 关键资产位置（先全部摸一遍）

- **草稿根目录**：`%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft\`——每集一个文件夹（含 `draft_content.json` + `materials/`）
- **草稿注册表**：`com.lveditor.draft\root_meta_info.json`——`draft_ids`/`all_draft_store` 为空 = 剪映认为没有草稿
- **剪映回收站**：`com.lveditor.draft\.recycle_bin\`——剪映内删除的草稿先进这里；清空后只剩 `root_meta_info.json`（空壳）
- **云草稿缓存**：`com.lveditor.draft\.cloud_cache_<uid>\`——云同步草稿的本地副本，结构=完整草稿（draft_content + materials + draft_cover.jpg），**可直接复制恢复**
- **草稿文件夹映射**：`User Data\Config\LocalDraftFolder\draft_folder_mappings.json` + `folder_meta_info.json`——`mappings`/`folders` 空 = 映射被清空
- **操作日志（诊断关键）**：`User Data\Log\draft_acion_watch.json`——每条 `create_draft`/`import_draft`/`move_draft_to_trash`/`delete_draft` 操作带 `time_nsec` 微秒时间戳，是还原「草稿怎么没的」的铁证

## 诊断流程

1. **确认剪映本体**：`tasklist | grep -i jianying` 查进程；主窗口 `Responding=True` 即正常；`User Data\Crash\` 有无今天的崩溃报告
2. **ls 草稿根目录**——草稿文件夹是否还在
3. **读 root_meta_info.json + LocalDraftFolder 映射**——是否被重写成空数组（删除后的正常副作用，不是文件损坏）
4. **读 draft_acion_watch.json**（核心步骤）：
   - 按类型计数：`grep -o '"type":"[^"]*"' <log> | sort | uniq -c | sort -rn`
   - 时间戳换算：`python3 -c "import datetime; print(datetime.datetime.fromtimestamp(<time_nsec>/1e6))"`
   - **同一秒内几十条 `move_draft_to_trash` + `delete_draft` = 全选→删除→清空回收站的批量操作**（人为误触），不是崩溃/更新 bug——崩溃不会产生上百条有序操作记录
5. **查两层回收站**：剪映 `.recycle_bin/` + Windows 回收站（`$Recycle.Bin` 下 `$I*` 元数据文件含原始路径，可解析确认有无草稿）

## 恢复路径（按成功率排序）

1. **云草稿缓存**：`.cloud_cache_<uid>/<草稿名>/` 结构完整 → 复制出来即为可用草稿（实测 4 集全恢复）
2. **转换产物备份**：之前跑过 `scripts/jianying2davinci.py` 的 `manlv_import/ep*.fcpxml + srt + manifest` 是时间线完整备份——fcpxml 51/51 + Z 盘素材在位 = 内容没丢，只是剪映草稿 JSON 没了
3. **磁盘恢复工具**（Recuva/DiskGenius）：草稿 JSON 只有 ~500KB，SSD 上删除后恢复成功率低，且**任何新写入都会覆盖**——要先评估再决定要不要备份动作在前

## 实测案例

2026-08-14《满级女总》51 集草稿批量删除：10:41:48 移入回收站 → 10:41:54-59 清空，全程 11 秒；剪映进程正常、无崩溃报告 → 判定误操作删除非 bug。51 集 fcpxml 全在 + 4 集云缓存（1/1(1)/6/51）幸存 → 损失可控。详见 `references/manlv-51ep-deletion-2026-08-14.md`

## 预防

- 剪映草稿的转换产物（fcpxml+srt）就是现成的定期备份机制——跑过转换的集永远有备份
- 剪映「彻底删除」= 移入 .recycle_bin 再清空，**不进 Windows 回收站**；云缓存只保同步过的集
- 用户确认恢复方案前，先做**零风险抢救**（复制云缓存/产物到安全目录），再谈恢复动作

## 坑

- `draft_acion_watch.json` 里同一草稿可能有多条记录（import → move → delete 各一条），计数先看全貌别急着下结论
- Windows 回收站 `$I` 元数据用 Python struct 解析（UTF-16LE 路径，偏移 24 起）；MSYS 路径下注意 `$` 转义
- `Crash\crash_post_reports\` 目录存在≠崩溃发生，内容为空是常态，别误判
