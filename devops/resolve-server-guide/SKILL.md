---
name: resolve-server-guide
version: 1.0.1
description: DaVinci Resolve 项目库服务器使用手册。触发词：达芬奇服务器、项目库、resolvedbkey。
tags: [davinci-resolve, postgresql, NAS, collaboration]
---

# DaVinci Resolve 项目库服务器使用手册

## 架构概览

```
工作站 (DESKTOP-3QUJG43)          NAS (192.168.1.2)
┌─────────────────────┐    ┌─────────────────────────┐
│ DaVinci Resolve     │    │ davinci-pg (PG 13)      │
│  dblist.conf        │───▶│  port 5432              │
│  .resolvedbkey      │    │  db=HMSJ, user=resolve   │
│  ProjectServer.cfg  │    │  davinci-pg-backup       │
└─────────────────────┘    │  (每日02:00 pg_dump)     │
                           └─────────────────────────┘
Y:\密钥\（网络共享盘）
├── HMSJ.resolvedbkey    ← 当前有效密钥
├── B.resolvedbkey.old   ← 旧密钥（已归档）
└── HMSJhmsj.local.resolve.backup  ← 数据库备份
```

## 一、NAS 服务端

### 1.1 容器管理

```bash
# SSH 登录 NAS
ssh HMSJadmin@hmsj.local

# 查看状态
docker ps --filter name=davinci

# 重启
cd /volume1/docker/davinci-resolve && docker compose restart

# 健康检查
docker exec davinci-pg pg_isready -U resolve -d HMSJ

# 查看日志
docker logs davinci-pg --tail 50
```

### 1.2 数据库信息

| 项 | 值 |
|---|---|
| IP | 192.168.1.2（静态） |
| 端口 | 5432 |
| 数据库名 | HMSJ |
| 用户名 | resolve |
| 密码 | NAS .env 文件 PG_PASSWORD 字段（勿写入文档） |
| Compose 路径 | /volume1/docker/davinci-resolve/ |
| 数据卷 | davinci-resolve_pgdata |
| 备份 | davinci-pg-backup 容器，每日 02:00 pg_dump -Fc，保留 14 天 |

### 1.3 备份与恢复

```bash
# 手动备份
docker exec davinci-pg-backup pg_dump -U resolve -Fc HMSJ > /backups/manual_$(date +%Y%m%d).dump

# 恢复（⚠ 会覆盖当前数据）
docker exec -i davinci-pg pg_restore -U resolve -d HMSJ --clean --if-exists < backup.dump
```

## 二、工作站客户端

### 2.1 连接配置文件

| 文件 | 路径 | 作用 |
|---|---|---|
| dblist.conf | `%APPDATA%\Blackmagic Design\DaVinci Resolve\Preferences\dblist.conf` | 数据库连接列表 |
| ProjectServer.cfg | `%APPDATA%\Blackmagic Design\DaVinci Resolve Project Server\Preferences\ProjectServer.cfg` | 协作服务器网卡绑定 |
| activedb.conf | `%APPDATA%\Blackmagic Design\DaVinci Resolve\Preferences\activedb.conf` | 当前激活的数据库 |

### 2.2 dblist.conf 格式

```
Local Database:<本地路径>:::::DISK
HMSJhmsj.local:hmsj.local:resolve*:<NAS密码>:HMSJ:QPSQL
```

- `HMSJhmsj.local` = 显示名（Resolve UI 里看到的）
- `hmsj.local` = 实际连接地址（走 mDNS 解析到 192.168.1.2）
- `resolve*` = 用户名（* 表示使用密码认证）
- `HMSJ` = 数据库名
- `QPSQL` = PostgreSQL 驱动

### 2.3 密钥文件（resolvedbkey）

**位置**：`Y:\密钥\`（网络共享盘 \\\\Hmsj\hmsj_b）

**格式**（XML）：
```xml
<?xml version="1.0" ?>
<DBAccessKey>
  <hostIPAddress>hmsj.local</hostIPAddress>
  <dbName>HMSJ</dbName>
  <dbUsername>resolve</dbUsername>
  <dbPassword>见NAS .env文件PG_PASSWORD字段</dbPassword>
</DBAccessKey>
```

**导入方式**：Resolve → 文件 → 导入密钥（Import Key）→ 选择 .resolvedbkey 文件

### 2.4 ProjectServer.cfg

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Database_Sharing_Network_Configuration_V1>
  <SharingNetworkInterface>192.168.1.208</SharingNetworkInterface>
</Database_Sharing_Network_Configuration_V1>
```

`SharingNetworkInterface` 必须填本机真实 LAN IP（非 VPN/Tailscale 虚拟网卡）。

## 三、多机协作

### 3.1 协作开关

数据库级：`SM_Project.IsCollaborationEnabled`（控制项目数据库共享）
实时级：`SM_Project.IsLiveCollaborationEnabled`（控制实时协作同步）

```sql
-- 查看所有项目协作状态
SELECT "ProjectName","IsCollaborationEnabled","IsLiveCollaborationEnabled" FROM "SM_Project";

-- 关闭实时协作
UPDATE "SM_Project" SET "IsLiveCollaborationEnabled" = false;
```

### 3.2 协作者注册表

```sql
-- 查看已注册的协作机器
SELECT "Name","ClientAddr","SysId" FROM "Sm2SysIdEntry";

-- 删除死记录
DELETE FROM "Sm2SysIdEntry" WHERE "SysId" = '<SysId>';
```

### 3.3 项目协作者列表

每个项目的 `AllSysIds` 列存储了该项目关联的所有协作机器 ID（逗号分隔）。

```sql
-- 查看某项目的协作者
SELECT "ProjectName","AllSysIds" FROM "SM_Project" WHERE "ProjectName" = '《满级女总》';

-- 删除某个协作者
UPDATE "SM_Project" SET "AllSysIds" = replace("AllSysIds", '<死ID>,', '') WHERE "ProjectName" = '<项目名>';
```

### 3.4 项目锁管理

每个项目有一个 `LockId` 字段（存储持有锁的机器 SysId）。死机器持有锁会导致"项目正在使用中"弹窗。

```sql
-- 查看所有项目的锁状态
SELECT "ProjectName","LockId","SysId" FROM "SM_Project";

-- 强制释放死机器的锁（将 LockId 改为当前机器或清空）
UPDATE "SM_Project" SET "LockId" = '' WHERE "LockId" = '<死机器SysId>';

-- 或将锁转移给当前机器（SysId 从 Sm2SysIdEntry 查本机条目）
UPDATE "SM_Project" SET "LockId" = '<本机SysId>' WHERE "LockId" = '<死机器SysId>';
```

**注意**：`SM_Session` 表无 LockId 列，锁只在 `SM_Project` 层。

### 3.5 "无法与协作者沟通"完整修复（2026-08-20 实测）

**报错日志特征**（`%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\logs\LogArchive\ResolveDebug_*.txt`）：
```
SyManager.Network | ERROR | Failed connecting to collaborator DESKTOP-XXX (88aeddb448f2) on IP 192.168.1.3 port 50059
```

**机制**：某项目开了实时协作（`IsLiveCollaborationEnabled=t`）+ `AllSysIds` 含该死机器 ID → 本机打开项目时主动连协作者 50059 端口 → 不通即报错。

**关键判据：机器是否还活着连库**（决定"删了会不会复发"）：
```sql
-- 连接来源 + 对应 Resolve 机器（application_name 格式 Resolve_<SysId>）
SELECT client_addr, application_name FROM pg_stat_activity WHERE application_name LIKE 'Resolve_%';
```
- 若死机器**还在线连库**（client_addr 命中）：它每次连接都会把注册写回 `Sm2SysIdEntry`——**单删注册会复发**，必须让那台机器退出 Resolve / 关协作，或接受"配合关协作后删一次即可"
- 机器识别用 **SysId 不用 IP**（工作站 DHCP 会漂，IP 不可靠；SysId 来自 `Sm2SysIdEntry.SysId` / ARP MAC）

**完整三步（缺一不可）**：
```sql
-- ① 删协作注册表死记录
DELETE FROM "Sm2SysIdEntry" WHERE "SysId" = '<死SysId>';
-- ② 关项目实时协作 + 清活跃协作者列表（否则本机仍会主动连）
UPDATE "SM_Project" SET "IsLiveCollaborationEnabled" = false, "SysIds" = '' WHERE "ProjectName" = '<项目名>';
-- ③ 从 AllSysIds 移除死 ID（保留其它历史 ID）
UPDATE "SM_Project" SET "AllSysIds" = regexp_replace("AllSysIds", '(^|,)<死SysId>(,|$)', '\1', 'g') WHERE "ProjectName" = '<项目名>';
```

**铁律**：改库前**本机 Resolve 必须完全退出**（运行中会缓存并在退出时写回，覆盖修改——实测 PID 还在跑时改无效）。改完重启 Resolve 验证；若还想用协作，需先修好死机器的 50059（防火墙放行 / 重开协作）。

### 3.6 协作防火墙放行（Windows 工作站，2026-08-20 实测）

Resolve 多用户协作的端口需求：**TCP 5432**（连 NAS 库，出站默认放行）+ **TCP 50059**（工作站之间点对点协作同步，**入站需放行**——每台参与协作的机器都要允许别人连自己的 50059）+ UDP 5353（mDNS 发现）。

**放行命令**（在目标工作站以**管理员**身份运行，任选其一）：
```powershell
# PowerShell（管理员）
New-NetFirewallRule -DisplayName "DaVinci Resolve Collab 50059" -Direction Inbound -Protocol TCP -LocalPort 50059 -Action Allow -Profile Private,Domain
```
```cmd
:: CMD（管理员）
netsh advfirewall firewall add rule name="DaVinci Resolve Collab 50059" dir=in action=allow protocol=TCP localport=50059 profile=private,domain
```

**验证**：
```powershell
Get-NetFirewallRule -DisplayName "DaVinci Resolve Collab 50059" | Select-Object DisplayName, Enabled, Direction, Action
netstat -ano | findstr 50059   # 需该机 Resolve 已启用协作后才会监听
```

**放行后配套**：① 该机 Resolve 项目管理器 → 项目右键 → Collaboration → **Enable Multi-User Collaboration**（若服务器侧已关过协作需重新启用）；② 所有工作站连同一个库（HMSJ@192.168.1.2:5432）；③ 若放行后仍不通，查该机 `netstat -ano | findstr 50059` 是否在监听 + 双方 mDNS 是否可达。不参与协作则无需放行，保持协作关闭即无报错。

## 四、日常维护

### 4.1 NAS IP 变更后必做

NAS IP 变更后需要同步修改**六个位置**：

1. `dblist.conf` — 改连接地址（或用 hmsj.local 域名免改）
2. `ProjectServer.cfg` — 改 SharingNetworkInterface（本机侧，与 NAS IP 无关）
3. `HMSJ.resolvedbkey` — 改 hostIPAddress（或用域名免改）
4. DB `Sm2SysIdEntry` — 清旧 IP 的死记录
5. DB `SM_Project.AllSysIds` — 清旧机器 ID
6. DB `SM_Project.LockId` — 清死机器的项目锁

**建议**：全程用 `hmsj.local` 域名而非 IP，NAS IP 变更时只需改 hosts 文件。

### 4.2 定期检查

```bash
# NAS 侧：检查容器健康
docker ps --filter name=davinci --format '{{.Names}} {{.Status}}'

# 工作站侧：检查连接
# Resolve → 项目管理器 → 看能否看到 HMSJ 项目库
```

### 4.3 数据库清理

```sql
-- 查看数据库大小
SELECT pg_size_pretty(pg_database_size('HMSJ'));

-- 查看各表大小
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;
```

## 五、故障速查

| 症状 | 检查 | 修复 |
|---|---|---|
| "无法与协作者沟通" | 五层排查（见下） | 逐层清理旧 IP |
| "项目正在使用中"（要求 .3 关闭项目） | `SM_Project.LockId` 查谁锁着 | 清死机器 LockId（见3.4） |
| 项目库连接超时 | `pg_isready` + 端口监听 | 重启容器 / 检查防火墙 |
| 素材脱机 | 素材路径变更 | 重新链接媒体 |
| 协作冲突 | Sm2SysIdEntry 重复记录 | 删除重复条目 |

**"无法与协作者沟通"五层排查**：dblist.conf → Sm2SysIdEntry → SM_Project.AllSysIds → ProjectServer.cfg → resolvedbkey。详见本 skill 第四节「日常维护」。

**"项目正在使用中"排查流程**：
1. `SELECT "ProjectName","LockId" FROM "SM_Project"` — 看谁锁着
2. `SELECT "Name","SysId" FROM "Sm2SysIdEntry"` — 确认锁持有者是否是死机器
3. `UPDATE "SM_Project" SET "LockId" = '' WHERE "LockId" = '<死SysId>'` — 强制释放
4. 重启 Resolve
