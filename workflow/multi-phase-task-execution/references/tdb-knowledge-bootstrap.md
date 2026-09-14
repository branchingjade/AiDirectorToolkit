# TDB Knowledge Bootstrap — Session Reference

Concrete recipe from the 2026-08-27 KB migration (Phase 1-7, 1h18min, 9722 Hindsight records + 541 Vault md + 12 profiles migrated to TDB).

## End-to-end shape

```
Phase 1  Backup MEMORY/USER/config/hindsight-config → .archive/<date>-<topic>/
Phase 2  config.yaml provider switch (sed, not patch) + DSH archive to scripts/_archive + Projects/_archive
Phase 3  Knowledge pump: Vault (sync_vault_md) + Hindsight (migrate_hindsight, 4-worker concurrent) + Profiles
Phase 4  Recall script: plugin-primary + HTTP-fallback dual-path
Phase 5  Verify against L0 conversation directly (L1 pipeline async, slow)
Phase 6  MEMORY.md auto-slim: keep exec-iron-rules, move 易变/临时 to skill or TDB L1
Phase 7  Stop daemon (kill PID + schtasks /Disable) + watchdog gate already in place + final verify
```

## Theme buckets (session_key pattern)

8 whitelist themes — replace per project but the structure is reusable:

```
vault-<theme>-<hash8>          # e.g. vault-creation-3f9e21ab
hindsight-<theme>-<hash8>      # e.g. hindsight-fuyaoji-7c2b50dd
profile-<name>-<hash8>         # e.g. profile-yangxuan-2a1c8d44
session-<sessionId>            # historical, leave alone
```

Hash is `hashlib.md5(...).hexdigest()[:8]` — stable, no time component (key stability = recall idempotency).

## Concurrent worker pattern

For batch jobs >1000 items / >5min, do not serialize. Split into N workers:

```python
# In the migration script
ap.add_argument("--offset", type=int, default=0)
ap.add_argument("--limit", type=int, default=0)
# ...
total = len(items)
if args.offset or args.limit:
    start = args.offset
    end = args.offset + args.limit if args.limit else total
    items = items[start:end]
```

Then launch N workers in background (each on disjoint offset range):

```bash
# In conversation flow — use terminal(background=true, notify_on_complete=true), NOT nohup
python migrate.py --offset 0 --limit 2430
python migrate.py --offset 2430 --limit 2430
python migrate.py --offset 4860 --limit 2430
python migrate.py --offset 7290 --limit 2432
```

Mistakes hit in this session (so you don't repeat them):
- **Slice logic bug**: first version was `items = items[args.offset : args.offset + (args.limit or len(items))]` which used up `args.limit` before slicing. Correct: `items = items[start:end]` where `end = offset + limit if limit else total`.
- **Duplicate write**: launching workers twice (old + new) doubled the first segment. Workers must own a disjoint range AND only one worker per range.
- **`time.sleep(0.2)` × N = serializing in disguise**: drop to `0.05` and use HTTP connection pooling.

## MEMORY.md auto-slim rules

Apply to any MEMORY.md past 16K chars (memory_char_limit default). Categories:

| Category | Action | Examples |
|---|---|---|
| 可执行铁律 / 全局偏好 | **保留** | 安全红线, cron 设计铁律, 浏览器铁律, bot 角色边界 |
| Skill 已有详细版 | **删** (skill 是单一正本) | skill 大小机制 (skill-management 覆盖), cron 调度策略 (cron-ops 覆盖) |
| 易变项目状态 | **迁 TDB L1** | DeepSeek 实测模型, DSH plugin 改名, TDB 默认 instance |
| 临时 debug 笔记 / 个人小工具 | **删** | 项目级 hermes-mem-agent 修复, MB 字符统计, prompt 评分, PC Mac 同步 |
| 重复条目 | **删旧留新** | MiMo vision 重复条目 |

Validate before commit: `for kw in "<铁律 1>" "<铁律 2>" ...; do grep -c "$kw" MEMORY.md; done` — every key iron-rule must still grep ≥1.

## Skill protection awareness

Skills `hermes-dsh-fusion` / `tencentdb-gateway` / `hindsight-memory-ops` / `feishu-outage-recovery` were loaded in the KB migration session but are user-owned (`created_by=None`). Even when their content is clearly outdated (e.g. tencentdb-gateway still describes v2 standalone while v3 three-piece is running), don't patch them in a `multi-phase-task-execution` run. Recommend `hermes curator adopt <name>` in the final report and move on.

## End-of-phase verification checklist

For each phase:

- [ ] Independent probe confirms success (not just process exit 0)
- [ ] Kanban card updated with `actual_min`
- [ ] Git commit with structured Chinese message
- [ ] Critical files snapshotted before destructive mutations
- [ ] No mid-phase decision questions to user

Final-phase extra:

- [ ] All `DSH_*` / `<old-system>` scheduled tasks Disabled
- [ ] Daemon process killed (verify port not LISTENING)
- [ ] Watchdog gate already in place (e.g. `HINDSIGHT_ENABLED=1` opt-in)
- [ ] Recovery path written to `archive/<date>-<topic>/README.md`