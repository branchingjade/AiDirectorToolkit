# DSH 重装实战记录（2026-08-24）

## 根因
DSH 反复 crash（exit code 1），即使重装源码也不解决。真正原因是 **dsh-damage-pulse 插件读 corrupt session log 触发连锁故障**。

## 修复步骤
1. 从 `~/.dsh/profiles/web/package.json` 的 `dsh.profile.bundles` 列表中移除 `dsh-damage-pulse`
2. cordis.patch.yml 的 disable 块**不生效**（bundle 先于 patch 加载）
3. 移除 30+ 个 corrupt/test session 到 quarantine
4. 重启 DSH 后稳定运行

## 关键发现
- `dsh-damage-pulse` 启动时读所有 session log 做投影计算，遇到 corrupt session（seq gap）→ 连锁故障 → DSH 进程退出
- DSH background task wrapper exit（exit code 127/1）≠ DSH 死亡——看 netstat 端口判断
- depth-1 clone 后必须 `pnpm run build:lib` + `pnpm run build` 才能启动
- DSH 余额在启动阶段会持续消耗（投影计算）

## 遗留
- dsh-damage-pulse 已禁用（从 bundles 移除），需要修好 corrupt session 后恢复
- DSH 仍会定期自己重启（运行3+分钟后静默退出），可能是设计行为
- 3 个计划任务全 Disabled（DSH_MountOrphans / DSH_Mux_Listener_Polling / DSH_Restart_V2）
