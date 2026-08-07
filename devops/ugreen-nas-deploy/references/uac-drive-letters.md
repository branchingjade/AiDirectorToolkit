# Windows 管理员终端看不到用户映射的网络驱动器（UAC）——诊断与根治

2026-08 实测。症状："其他软件（资源管理器等）能读 Y/Z 盘，Hermes 终端读不到"。

## 症状

- `net use` 列表为空（或缺失目标盘）
- `Get-PSDrive -PSProvider FileSystem` 只有 C 盘
- 但普通（非提权）软件正常访问 Y:/Z:

## 根因

Hermes 终端进程以**管理员权限**运行（`IsInRole(Administrator)` = True）。
Windows UAC 默认不把普通用户会话的映射网络驱动器暴露给提权进程
（Linked Connections 未启用）。提权进程也没有用户会话的 SMB 凭据缓存
——`net view \\NAS` 报错误 5（拒绝访问）、`net use \\NAS\Share` 报错误 67
（找不到网络名），即使共享真实存在。

## 诊断链（实测顺序）

1. `net use` 空 → 别急着下结论
2. 注册表确认映射真实存在（用户会话里已映射）：
   ```powershell
   Get-ItemProperty 'HKCU:\Network\Y','HKCU:\Network\Z' -ErrorAction SilentlyContinue | Select PSChildName,RemotePath
   # Y -> \\Hmsj\hmsj_b   Z -> \\hmsj\HMSJ_A
   ```
3. 确认当前进程是提权状态：
   ```powershell
   ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole('Administrator')
   ```
4. 顺带注意：主机名（`\\Hmsj`）可能解析到 IPv6 公网地址而非局域网 IP。

## 根治：EnableLinkedConnections（实测成功）

管理员权限执行一次：

```powershell
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name 'EnableLinkedConnections' -Value 1 -Type DWord
# 验证：Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' | Select EnableLinkedConnections  → 1
```

**生效机制（关键）**：Windows 在**登录时**为管理员会话创建到用户会话的链接。
因此必须**注销并重新登录（或重启 Windows）**，已提升的现有进程不会即时变更
——改完立即 `Test-Path Z:\` 仍是 False 属预期，不要误判为失败。

重启后验证：

```powershell
Test-Path 'Y:\'; Test-Path 'Z:\'      # True True
Get-PSDrive -PSProvider FileSystem     # Y: Y:\ \\Hmsj\hmsj_b / Z: Z:\ \\hmsj\HMSJ_A
```

盘符映射记录在 `HKCU:\Network\<盘符>`，重启后自动重连（前提：映射时已保存凭据）。

## 兜底（SMB 重连失败时）

SMB 凭据与 SSH 凭据是两套体系（绿联 NAS 的 valid users 是中文名/组），
盘符重连失败时走 SFTP 直连 NAS：`~/Documents/Hermes/scripts/nas.py`
（`ls / get / put / rm`，密码内置），或 paramiko 模式直连
（SFTP 根 = 共享挂载点，`/HMSJ_A` = Z 盘、`/HMSJ_B` = Y 盘）。

## 一句话

管理员进程看不到用户盘符 → 注册表 EnableLinkedConnections=1 + 注销/重启；
SFTP 直连永远是可用的兜底。
