# NAS SSH 重启后 PATH 丢失 docker（2026-08-27 实战）

## 问题

绿联 NAS 的 Docker 装在 overlay filesystem（`/overlay/upper/usr/bin/docker`），不在标准 PATH 里。SSH 重启后，`.bashrc`/`.profile` 可能不包含此路径，导致 `docker: command not found`。

## 实测表现

```bash
ssh HMSJadmin@hmsj.local 'docker ps'
# → bash: docker: command not found
```

## 根因

HMSJadmin 的 PATH：`/usr/local/bin:/usr/bin:/bin:/usr/games`——**不包含 `/overlay/upper/usr/bin`**。

`/etc/profile.d/` 下有 `common-env.sh`（加了 `$HOME/bin`），但**没有 docker 路径**。SSH session 的 PATH 由 login shell 的 profile 文件决定，重启后 profile 重新 source，但 docker 路径不在任何 profile 文件里。

## 修复

```bash
# 每次 SSH session 开始前加 PATH
ssh HMSJadmin@hmsj.local 'export PATH=/overlay/upper/usr/bin:$PATH && docker ps'
```

或在 SSH 连接前设 shell 变量（MSYS bash）：
```bash
export REMOTE_PWD='export PATH=/overlay/upper/usr/bin:$PATH && cd /volume1/docker && '
ssh HMSJadmin@hmsj.local "$REMOTE_PWD docker ps"
```

## 验证

```bash
ssh HMSJadmin@hmsj.local 'export PATH=/overlay/upper/usr/bin:$PATH && docker --version'
# → Docker version 26.1.0, build 9714adc
```

## 注意

- 这只影响 SSH 命令行——**容器内部有自己的完整 PATH**（含 npm/node），不影响容器运行
- `docker compose up` 不受此影响——docker daemon 已经在跑，只是 CLI 路径问题
- 所有涉及 `docker` 命令的 SSH 操作**必须**先加 PATH
