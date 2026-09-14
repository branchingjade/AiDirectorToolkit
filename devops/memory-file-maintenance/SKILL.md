---
name: memory-file-maintenance
description: 维护 MEMORY.md 等本地 memory 文本文件的精简/拆分/回滚 + 记忆后端切换（Hindsight → TDB 等）的会话级事实迁移。触发词：memory 优化、满了、备份、memory 切后端、记忆迁移。
version: 1.3.0
author: curator
license: MIT
metadata:
  hermes:
    tags: [devops, hermes, memory, maintenance, optimization, tdb-migration]
    related_skills: [hindsight-memory-ops, tencentdb-gateway, hermes-memory-provider-selection]
    changelog:
      - 1.3.0 (2026-09-03): 新增「写入前查重 SOP」(Step 2.5) + pitfall #8（写入不查重→MEMORY 自相矛盾）+ 自检清单加「重叠段数=0」+ 决策表加「重叠段合并去重」行——根因 8/28-9/3 OV/Hindsight 切换应激期反复注入 4 条重叠段（config.yaml 修改通道/OV memory provider 零 MCP 依赖/OV 切换完成矩阵/飞书评论创作润色工作流已固化），agent 写入时不检查 anchor 同主题段已存在就直接新建
      - 1.2.0 (2026-08-28): 决策表新增「不迁」一行（旧 provider 源数据 + 目标 provider 已有 LLM 精炼版）+ 新增 pitfall #7「垃圾记忆不需要」+ Phase 3 补「边际价值评估」前 5 步
      - 1.1.0 (2026-08-27): 新增「后端切换 + 记忆迁移」工作流（Hindsight export.jsonl → TDB capture 批量回灌）+ 「切后端/资产盘点时的穷尽搜索铁律」（用户两次纠正"nas 和本地都有备份"，避免单工具断言"已丢"）+ 升级 selfcheck 阈值
---

# Memory 文件维护

维护 Hermes 本地 memory 文本文件（默认 `~/AppData/Local/hermes/memories/MEMORY.md`，按 `§` 单独一行分隔条目）。memory 容量上限 16000 字符（66% 时工具开始拒写）→ 需要精简/拆分会话级事实到 skill 时的标准流程。

> **memory vs skill 分工**：
> - **memory = 用户事实源**（"谁是我 + 当前状态"）—— 跨会话必须保留，agent 自动 read 注入
> - **skill = 操作手册**（"这类任务怎么做"）—— 按需 load，skills/ 目录管理
> - **判断标准**：某条事实 agent 未来处理**哪类任务**时需要？纯操作类（如何测 cron、如何 debug ssh）→ **迁 skill**；agent 跨任务判断时需要（用户偏好、铁律）→ **留 memory**

## 触发词

memory 优化 / memory 满了 / memory 备份 / §段维护 / memory 回滚 / memory 拆分 / 迁到 skill / memory 自检 / MEMORY.md

## 何时用

- memory 容量快满（>90% 占用）需要瘦身
- 想把某条事实从 memory 迁到 skill（去重 + 减少 memory 噪音）
- 误操作需要回滚到上次备份
- 改完想验证关键铁律 NOT lost
- 跨 session 准备 memory 交接

## 标准流程（5 步，顺序不可错）

### 1. 备份（必做，**所有操作前**）

```bash
cp "$HERMES_MEMORY" "${HERMES_MEMORY}.bak-$(date +%Y%m%d)-pre-optimize"
```

**最低必要**：每次操作前**必做**。备份命名带日期+目的（pre-optimize / pre-slim / pre-cleanup），回滚用。

### 2. 决策：精简 vs 删除 vs 保留

**对每条 memory 问一遍**：

| 问题 | 动作 |
|------|------|
| 内容已在某 skill 里有详细版本（用 `skills_list` 查）？ | **删除**，memory 留 1-2 行指针即可 |
| 内容是配置文件/操作手册/事件档案？ | **删除**（迁 skill 或 docs） |
| 内容是跨任务的判断原则/用户偏好/可执行铁律？ | **精简**保留（保留核心，删历史细节/示例） |
| 内容是当前任务状态/一次性会话事实？ | **保留**（不缩，但确认是否真需要长期记忆） |
| 内容核心关键词是否已在 MEMORY.md 出现 ≥2 次（**重叠段**）？ | 🧹 **合并去重**——保留一条最新/最准确、删其余（见下方「写入前查重 SOP」） |
| 内容是**旧 provider 源数据**，**目标 provider 已有 LLM 精炼版**（OpenViking `resources/yaoyu-knowledge-base/*.md` 384 个 + `user/default/memories/` LLM 摘要 4,180 条）？ | **不迁**（见 pitfall #7「垃圾记忆不需要」） |

**错误倾向**：
- ❌ 看到长内容就精简——但如果是核心铁律（创作哲学、本地单独铁律），保留完整
- ❌ 想保留所有内容——但 memory 容量限制决定必须删除/迁
- ❌ 凭"感觉"分类——用 skills_list + 全文搜索验证"skill 里有没有"

### 3. 操作：段号文本锚点（**不用索引**）

**坑 #1**：MEMORY.md 用 `re.split(r"(?m)^§$", text)` 切段时，`parts[0]` 是文件开头（"安全红线..."），`parts[1]` 是**段 1**，**段号 N = parts[N]**（不是 parts[N-1]）。这是 2026-08-26 实测踩坑——多次操作累积位移后看 parts[i] 误以为是段 i。

**坑 #2**：用 `parts[idx]` 做删除索引会**位移错乱**——删 parts[5] 后，原 parts[6] 变成 parts[5]，再 `parts[5] = new_content` 会改错位置。

**正确做法**：用**段首文本作为锚点**，搜索定位 + patch 替换：

```python
# 锚点 = 段第一行前 30-50 字（足够唯一即可）
def replace_seg(text, anchor, new_content):
    idx = text.find(anchor)
    if idx < 0:
        return text, False
    seg_start = text.rfind("§\n\n", 0, idx)
    seg_end = text.find("\n§", idx)
    new_text = text[:seg_start] + new_content + "\n\n" + text[seg_end:]
    return new_text, True
```

或者直接用 Hermes 的 `patch` 工具（基于 unique substring 匹配）—— 更稳，无脚本位移风险。

### 4. 自检（每次改完必跑）

**检查清单**：
- ✅ 段数 < 目标（一般 ≤40 条）
- ✅ 占用率 < 60%（留 6000 字缓冲）
- ✅ 应删段全部 NOT found（用 grep 关键词）
- ✅ 应精简段都含精简版关键词
- ✅ 关键铁律全部 still present（cron / 浏览器 / 安全红线 / bot 边界 / 本地单独铁律 等）
- ✅ § 分隔符齐全（段数+1 = § 出现次数）
- ✅ 备份存在（可回滚）
- ✅ **重叠段数 = 0**：本批涉及的所有核心关键词 `grep -c` 均 ≤ 1（查重失败 = 写入时漏跑 Step 2.5）

参考 `scripts/memory_selfcheck.py`（基于 2026-08-26 实测自检脚本）。

### 5. 留档到 memory（如有跨会话教训）

- 操作类型、踩坑点、新技巧——**只留可执行原则**，不记录一次性的会话细节
- 例：本次留的 "memory 维护用段号文本锚点 + 每次 cp 备份 + 自检脚本验证"——下次会话需要时能立即想起
- 不留：本次具体删了哪几条（一次性事实，下次会变）

## 坑清单（2026-08-26 实测踩过）

- ❌ **用 parts 数组索引操作** → 索引位移错乱。**用段号文本锚点**
- ❌ **patch 不验证 anchor 唯一性** → 多段共用同一开头导致改错位置。**先 search 看 anchor 是否唯一，再 patch**
- ❌ **多次操作不重新校验** → 段号语义模糊。**每轮操作前 cp 备份 + 自检**
- ❌ **精简时只看长度** → 可能把核心铁律精简了。**先看是否在 skill 有更详细版**（用 skills_list + 搜索）
- ❌ **改完不验证关键铁律** → 误删核心条款。**自检脚本强制检查"cron / 浏览器 / 安全红线 / bot 边界 / 本地单独铁律"是否仍存在**
- ❌ **不备份就动手** → 误操作难回滚。**操作前 cp 一份 .bak-YYYYMMDD-pre-<目的> 命名**
- ❌ **看到「未迁移」就启动批量灌入脚本** → 用户原话「垃圾记忆不需要」（2026-08-28）：源数据（如 Hindsight 9,735 条 jsonl）里 55% 命中主题桶听起来很多，但**目标 provider 已有 LLM 精炼版**（OpenViking 384 md + 4,180 LLM 摘要），再灌只会触发 503 限流 + extraction 队列压力 + 召回噪音。**先评估「边际价值」再决定迁不迁**（详见下方 Phase 3 补充）：①目标 provider 5 个采样 query 召回 score ≥ 50% 且内容是 LLM 精炼版 → **停止**；②反之才进入 Phase 3 主流程
- ❌ **架构变更拍板=全量执行** →（2026-09-03 OV 退役 Obsidian 实战）：用户原话「OV 主写扩到所有项目」听上去是全团队切，但用户实际偏好**「一步步来」**——第一步轻量（铁律持久化+归档标记），第二步评估后启动（cron 改造/基础设施迁移/数据格式迁移）。详见 `hermes-runtime-pitfalls`「项目级重大决策节奏铁律」+「两步走标准动作」两条。
- ❌ **写入不查重 → MEMORY 自相矛盾/事实错误累积**（2026-09-03 清理实战确立）：注入新 memory 段前**必须 `grep -c "<核心关键词>" MEMORY.md`** 查 anchor 是否已存在。若已存在同主题段（hash 标题/事件描述/工具名）就**并入、替换或留指针**，绝不新增同内容。**这次踩坑**：8/28-9/3 OV/Hindsight/TDB 切换应激期，多会话反复注入 `config.yaml 修改通道` `OV memory provider 零 MCP 依赖` `2026-09-01 OV 切换+ MCP 退役完成` 三条重叠段——表面看「三条独立事件」实际同事实，每个 OV 切换会话各写一份，9/3 清理时发现这三条全在，段号 L99/L101/L105。**根因**：agent 写入时不检查 anchor，硬上「新建一段」而不去 merge 既有段。**修复**：每次写入前 grep + 决策表（并入/替换/留指针/新增），并把它加入自检清单。

---

## 写入前查重 SOP（Step 2.5，并入 Step 2 决策表）

> 任何写入新段前**必走**——和备份一样硬性。MEMORY.md § 段是 agent 自动 read 注入的，重复段 = 同一事实被算多次权重，污染判断。

### 决策表（写入前查重后选一项）

| grep 结果 | 动作 |
|-----------|------|
| 0 命中（核心关键词 grep 不到） | ✅ **新增**段，写新内容 |
| 1 命中（同主题段已存在，内容过时） | ✏️ **替换**——用 patch 工具原地改原段 |
| 1 命中（同主题段已存在，内容还准） | 🗑️ **取消新增**——新事实并入原段（patch 追加一行）或留指针到 .md |
| ≥2 命中（已有重复 = 当前已污染） | 🧹 **清理**——保留一条最新/最准确的、删其他重叠段、写新的元铁律 |

### 操作步骤（Python 脚本模板）

```python
# 写入前查重（5 行必跑）
import re
anchor = "OV memory provider"  # 新段核心 5-15 字关键词
text = open('MEMORY.md', 'r', encoding='utf-8').read()
hits = [m.start() for m in re.finditer(re.escape(anchor), text)]
print(f'anchor "{anchor}" hits: {len(hits)}')
for h in hits[:3]:
    print(f'  hit@{h}: {text[max(0,h-30):h+80]}')
```

**判断**：hits=0 → 新增；hits=1 且内容过时 → 替换；hits=1 且内容准 → 并入/留指针；hits≥2 → 清理优先。

### 自检清单新增项

- ✅ **重叠段数 = 0**：跑 `for kw in <本批写入的所有核心关键词>: grep -c "$kw" MEMORY.md` —— 每条应 ≤ 1（自身+1）。**发现 ≥2 → 立即合并/清理**

## 后端切换 + 记忆迁移（Hindsight → TDB 等）

> 任何"换记忆后端"任务都是**双轨**：① 本地 MEMORY.md 该不该瘦身 ② 旧后端的 export 怎么灌进新后端。**不要只切 provider 就跑**——会让历史知识全丢。

### 触发条件

- config.yaml 改 `memory.provider:`（hindsight ↔ memos ↔ tdai 等）
- 用户原话"切到 X 吧""还是用 X""考虑 X"——意味着从单边切换变成双轨迁移
- 旧后端 daemon 停了（hindsight.config.json auto_retain=false 等）但 export.jsonl 在

### 标准 7 步（顺序不可错）

```
Phase 1  备份与冻结（5min）
   cp memories/MEMORY.md → .archive/20260827-<主题>-pre/
   cp config.yaml → 同上
   cp ~/.hermes/hindsight/config.json → .archive/ (旧 provider 配置快照)

Phase 2  新 provider 协议层（30min）
   config.yaml 改 memory.provider
   .env 加新 provider 必需 env（如 TDB: MEMORY_TENCENTDB_GATEWAY_HOST/PORT）
   重启 gateway → probe 端到端能 retain + recall

Phase 3  旧数据迁移（1-2h，最重）
   改 migrate_hindsight_to_xxx.py: 旧 POST /product/add → 适配新 provider 的 capture 端点
   - TDB: POST http://<gateway>:<port>/capture body={user_content, assistant_content, session_key}
   - 旧 MemOS v1: POST /product/add body={user_id, mem_cube_id, memory_content, tags}
   - 分桶：按 fact_type (world/experience/observation) 用不同 session_key，避免单桶过载
   - 批量 100 条/批 + sleep 0.5s 防压垮
   - 先 dry-run → 再干跑
   验证：新 provider query 能召回

   ─── Phase 3 前置：「边际价值评估」（2026-08-28 新增） ───
   0. 先 grep 目标 provider 现状（5 个采样 query 覆盖核心项目 / 主题 / 角色 / 工具 / 决策）
      - 召回 score 平均 ≥ 50% + 内容是 LLM 精炼版（带决策摘要 + 路径标注）→ **停止**（源数据再灌=边际价值低，会触发 503 + extraction 队列压力 + 召回噪音）
      - 召回 score 平均 < 30% 或召回内容是源数据原文 → 才进入 Phase 3 主流程
   评估指标不是「文件数」，是「find() 召回命中率 + 召回内容是否直接可用」——「直接可用」= LLM 摘要 + 决策原文 + 路径标注，agent 不必再读源文件就能用

Phase 4  Vault 知识库迁移（1-2h）
   跑 sync_vault_md_to_<provider>.py 增量同步
   跑 upload_profiles_to_<provider>.py 上传成员画像
   验证：召回"成员画像""项目主文档"

Phase 5  MEMORY.md 精简（1.5h，根因处理）
   按上方「标准流程」执行精简（保留 / 迁 skill / 迁 provider L1 / 删）
   目标：≤80 条 / ≤10K chars（参考本会话实测 152→待精）
   grep 验证关键铁律仍在

Phase 6  旧后端彻底清理（10min）
   备份旧 config.json（即便已全 false，留档）
   MEMORY.md 加一行 HTML 注释 marker 标注封存事实
   写归档 README 写恢复路径
   禁用旧 daemon 保活（双路径：计划任务 + watchdog）

Phase 7  端到端验证（15min）
   新桌面会话发一条 → retain → recall 命中
   新飞书会话发一条 → retain → recall 命中
   监控 24h：provider log 无 ERROR
```

### ⚠️ 资产盘点铁律：穷尽搜索后才断言"已丢"（2026-08-27 用户两次纠正）

> 用户原话："memos 不是有备份吗"/"数据备份有的吧，nas 和本地应该都有"——我之前单工具探活后断言"MemOS 数据已丢"，被打回。

**错**：
```
ssh NAS "docker ps | grep memos"     # 0 条
echo "MemOS 数据已丢"
```

**对**——断言"已丢"前**至少搜这 5 个层级**：

| 层级 | 命令 |
|------|------|
| 1. NAS 容器 | `ssh hmsj.local "docker ps -a"` |
| 2. NAS 数据卷 | `ssh hmsj.local "docker volume ls"` |
| 3. NAS 路径 | `ssh hmsj.local "find /volume1 -maxdepth 4 -type f \( -name '*.sql' -o -name '*.dump' -o -name 'memos_*' -o -name '*pg_dump*' \) 2>/dev/null"` |
| 4. 本地路径 | `find ~ -maxdepth 6 -type f \( -name '*.sql' -o -name '*.dump' -o -name 'memos*' \) 2>/dev/null` |
| 5. 分析目录 | `ls 分析/memos-*/ 分析/*-cleanup-*/`（历史的迁移日志/目录） |

**实战教训**（2026-08-27 本会话）：
- 第一次只看了 NAS 容器 + 数据卷（2 层）→ 断言"MemOS 数据已丢" → 用户纠正
- 第二次加了 NAS 路径 + 本地路径 + 分析目录 → 发现 `memos-backup/memos-source-20260826.tar.gz` 是源码+配置备份（757KB / 454 文件），但**数据备份确实是 0**（无 pg_dump / qdrant snapshot / neo4j dump）
- **最终结论："数据已丢"这个判断本身没变，但理由必须基于 5 层穷尽搜索**——用户的纠正不是在否认结论，是在要求"理由要扎实"

### 跨场景推论（不仅限记忆）

任何"X 是没了吗"类问题，先穷尽搜索再断言。**至少 3 个独立来源**才下结论（grep 范围 / 时间范围 / 命名变体）。

## References

- `references/memory-layout.md` — MEMORY.md 文件结构（§ 分隔符、parts 索引、文件位置、容量规则）
- `scripts/memory_selfcheck.py` — 自检脚本（grep 关键词 + 段数 + 占用率 + 关键铁律 NOT lost 检查）
- `templates/backup_restore.sh` — 备份 + 回滚模板（含 cp 命名规范、diff 对比、验证清单）