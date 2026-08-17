# 实战案例：director-aesthetic-card 瘦身手术（2026-08-07）

本次手术的完整实录——作为 skill-slimming 方法的验证样本与复用模板。

## 背景

- 症状：研习子代理多轮误报「知识库 SKILL.md 已达 100K 上限」；系统提示中 `director-aesthetic-card` 显示 `[SKILL_PRUNED]`（26,632 chars 被压缩剪裁）
- 真相排查：**知识库 SKILL.md 实际 31.8KB（健康）**；真正超限的是 `research/director-aesthetic-card/SKILL.md`——99,499 chars（196KB bytes，中文 3 字节/字符）
- 子代理误报机制：研习子代理 context 内置 director-aesthetic-card 指导，加载时被剪裁 → 它把「自己加载的 skill 不完整」误写成「知识库 SKILL.md 100K」——**先验证实际文件大小，别信转述**

## 量化（Step 2 实录）

```
总行数: 238，总字符: 99,262
① frontmatter+定位头: 383 chars       ← 保留
② 历轮实测记录(15-49): 15,310 chars   ← 移 rounds-log（每条已指向 references 地图，正文是重复摘要）
③ 适用+工作流(50-96): 34,340 chars    ← 保留
④ 编号坑(97-104): 19,828 chars        ← 移 pitfalls-log（㉟㊱㊲…㊿ 系列）
⑤ 卡片模板+纪律(105-125): 1,154 chars ← 保留
⑥ 深化变体(126-168): 10,450 chars     ← 保留
⑦ 参考登记(169-237): 17,797 chars     ← 移 reference-index（119 个来源地图逐行登记）
冗余可移: 52,935 chars（51KB）｜保留核心: 46,327 chars（45KB）
```

## 手术执行（Step 3 实录）

1. git 快照：`git commit -m "chore(skills): director-aesthetic-card 瘦身前快照（手术保护点）"`
2. 三块原文提取落盘 references/（零改写、逐字移动）：
   - `references/rounds-log.md`（30,639 bytes）
   - `references/pitfalls-log.md`（39,793 bytes）
   - `references/reference-index.md`（34,316 bytes）
3. SKILL.md 重写：保留核心 46KB + 三个一行指针；工作流加「第 0 步：写卡前必须先 skill_view 加载 pitfalls-log」
4. 结果：99,262 → 47,113 chars（-52%）

## 验证（Step 4 实录）

| 层 | 方法 | 结果 |
|---|---|---|
| ① 完整加载 | skill_view(name=...) | ✅ 47KB 全文返回，章节 7/7 在位，无剪裁 |
| ② 按需加载 | skill_view(file_path='references/pitfalls-log.md') | ✅ 39.8KB 坑库完整返回 |
| ③ 零丢失 | git show <快照>:SKILL.md 逐行 diff | ✅ 三块 0 行丢失、核心块 0 行丢失 |
| ④ 真实子代理 | leaf 子代理 skill_view 加载测试 | ✅ 通过（模拟下一轮研习实战） |
| 体积对照 | 手术前 99.5K chars → 47K chars；健康基线 AI电影编剧 15K | ✅ 同量级 |

## 关键坑（本案例特有）

1. **子代理误报**：报「知识库 100K」实际是它自己加载的 director-aesthetic-card 被剪裁——排查先 `find ... -name SKILL.md -size +80k` 全盘定位真凶
2. **bytes vs chars**：196KB bytes = 99K chars（CJK 3 bytes/char），enforced 上限是 chars（MAX_SKILL_CONTENT_CHARS=100,000）
3. **references 自动列出**：linked_files 自动列出全部 122 个 references 文件——119 行手动登记纯冗余
4. **坑可见性补偿**：坑库从「常驻上下文」变「必须 skill_view」——靠工作流第 0 步硬指令补偿，不是建议

## 可复用模板

后续任何 SKILL.md 膨胀手术照此执行：
1. 全盘 `find -size +80k` 定位真凶（不信子代理转述）
2. 章节边界量化三块（轮次日志/编号坑/参考登记）
3. git 快照 → 逐字移 references/ → 一行指针替换 → 工作流加第 0 步
4. 四层验证（完整加载/按需加载/逐行 diff/真实子代理）
