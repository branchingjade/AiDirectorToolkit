# Windows ESP 修复（EFI 系统分区引导重建）

## 适用场景

- 原电脑无法启动，报 `Boot Device Not Found` / `0xc0000098` / `0xc000000f`
- 硬盘已拆下接到另一台 Windows 电脑当从盘
- ESP 分区本身还在（未删除），只是引导文件或 BCD 损坏
- 修完后装回原电脑启动

## 前置条件

**必须管理员权限。** Hermes 的 terminal 继承进程权限——退出 Hermes → 右键以管理员身份运行，重启后即可。验证：

```bash
powershell -Command "([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')"
```

## 诊断：确认 ESP 分区状态

```powershell
Get-Disk | Format-Table -AutoSize
Get-Partition -DiskNumber 1 | Format-Table DiskNumber,PartitionNumber,DriveLetter,Size,Type,GptType
```

ESP 的特征：`Type = System`，`GptType = {c12a7328-f81f-11d2-ba4b-00a0c93ec93b}`，100–500MB。

## 修复路径选择

优先走 bcdboot 路径（简单），失败后走手动路径。

### 路径 A：bcdboot（优先尝试）

```bat
diskpart
select disk 1
select partition 1
assign letter=S:
exit

bcdboot D:\Windows /s S: /f UEFI
```

成功输出：`Boot files successfully created.`

### bcdboot 常见失败及根因

| 错误码 | 现象 | 根因 |
|--------|------|------|
| `0x80092003` | `WinVerifyTrust failed` | 安全启动签名验证失败。当前电脑的 Secure Boot 策略拒绝外来盘上的引导文件 |
| `0xc1` | `bootmgfw_EX.efi not found` | 安全启动要求 EX 引导文件（`EFI_EX\` 目录），但目标 Windows 版本不提供（常见于 Win10 旧版） |
| `0xc1` | Failed to validate checksum | 同上，`BFSVC_USE_EX_BINS` 启用但源系统缺少 EX 文件 |

两个错误的根因相同：**当前电脑启用了安全启动，bcdboot 要求 EX 引导文件，但源 Windows 没有这些文件。**

> **关键教训**：不要切换到当前系统的引导文件来绕过签名验证——引导文件版本必须与目标 Windows 版本匹配。C 盘和 D 盘的 `bootmgfw.efi` 大小不同就是信号（Win11 ~3MB vs Win10 ~1.5MB）。

### 路径 B：手动重建（bcdboot 失败时）

**1. 格式化 ESP**

```bat
diskpart
select disk 1
select partition 1
format fs=fat32 quick label=ESP
assign letter=Y:
exit
```

**2. 从目标 Windows 复制引导文件（不是当前系统！）**

```powershell
# 创建目录结构
New-Item -ItemType Directory -Path Y:\EFI\Boot -Force
New-Item -ItemType Directory -Path Y:\EFI\Microsoft\Boot -Force

# 从目标系统的 Boot 目录复制（D: = 外来硬盘的系统分区）
Copy-Item D:\Windows\Boot\EFI\bootmgfw.efi Y:\EFI\Microsoft\Boot\ -Force
Copy-Item D:\Windows\Boot\EFI\bootmgr.efi Y:\EFI\Microsoft\Boot\ -Force
Copy-Item D:\Windows\Boot\EFI\bootmgfw.efi Y:\EFI\Boot\bootx64.efi -Force

# 复制语言文件夹和调试文件
robocopy "D:\Windows\Boot\EFI" "Y:\EFI\Microsoft\Boot" *.efi *.dll *.stl *.p7b /S /R:1 /W:1
robocopy "D:\Windows\Boot\Fonts" "Y:\EFI\Microsoft\Boot\Fonts" /E /R:1 /W:1
robocopy "D:\Windows\Boot\Resources" "Y:\EFI\Microsoft\Boot\Resources" /E /R:1 /W:1
```

**3. 创建并配置 BCD**

获取目标 Windows 分区的 GUID（用于 BCD）：
```powershell
Get-Partition -DiskNumber 1 -PartitionNumber 3 | Select Guid
```

```bash
# 创建 BCD 存储
bcdedit /createstore Y:\EFI\Microsoft\Boot\BCD

# 创建引导管理器
bcdedit /store Y:\EFI\Microsoft\Boot\BCD /create {bootmgr} /d "Windows Boot Manager"
bcdedit /store Y:\EFI\Microsoft\Boot\BCD /set {bootmgr} device partition=Y:
bcdedit /store Y:\EFI\Microsoft\Boot\BCD /set {bootmgr} path '\EFI\Microsoft\Boot\bootmgfw.efi'

# 创建 Windows OS Loader
bcdedit /store Y:\EFI\Microsoft\Boot\BCD /create /d "Windows" /application osloader
# → 返回 GUID {xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}

bcdedit /store Y:\EFI\Microsoft\Boot\BCD /set {返回的GUID} device partition=D:
bcdedit /store Y:\EFI\Microsoft\Boot\BCD /set {返回的GUID} osdevice partition=D:
bcdedit /store Y:\EFI\Microsoft\Boot\BCD /set {返回的GUID} path '\Windows\system32\winload.efi'
bcdedit /store Y:\EFI\Microsoft\Boot\BCD /set {返回的GUID} systemroot '\Windows'
bcdedit /store Y:\EFI\Microsoft\Boot\BCD /displayorder {返回的GUID} /addlast
bcdedit /store Y:\EFI\Microsoft\Boot\BCD /default {返回的GUID}
```

> **关键：** `systemroot` 和 `path` 的值必须用**单引号**括起来，否则 bash 会吃掉反斜杠。详见 [bcdedit 反斜杠陷阱](#bcdedit-反斜杠陷阱)。

**4. 验证 BCD**

```bash
bcdedit /store Y:\EFI\Microsoft\Boot\BCD /enum
```

确认输出中：
- `{bootmgr}` 有 `path \EFI\Microsoft\Boot\bootmgfw.efi`
- `{default}` 有 `path \Windows\system32\winload.efi`
- `systemroot \Windows`（带反斜杠）
- `device` 和 `osdevice` 都指向目标分区

**5. 清理盘符**

```bat
diskpart
select disk 1
select partition 1
remove letter=Y:
exit
```

## bcdedit 反斜杠陷阱

在 git-bash 中，`bcdedit /set` 的值如果有反斜杠（`\Windows\system32\winload.efi`），bash 会把 `\` 当作转义符吃掉：

```bash
# ❌ 反斜杠被吃掉 → path 变成 Windowssystem32winload.efi
bcdedit /store BCD /set {default} path \Windows\system32\winload.efi

# ❌ 双反斜杠在 bash 中也无效
bcdedit /store BCD /set {default} path \\Windows\\system32\\winload.efi

# ❌ cmd /c 同样不行
cmd /c "bcdedit /store BCD /set {default} path \Windows\system32\winload.efi"

# ✅ 单引号保护反斜杠
bcdedit /store BCD /set {default} path '\Windows\system32\winload.efi'
bcdedit /store BCD /set {default} systemroot '\Windows'
```

这个陷阱也影响 `{bootmgr}` 的 path 值（`\EFI\Microsoft\Boot\bootmgfw.efi`）。

## 验证清单（装回原电脑前）

- [ ] `bootmgfw.efi` 来自目标 Windows（不是当前系统）——检查文件大小是否与 `D:\Windows\Boot\EFI\bootmgfw.efi` 一致
- [ ] `bootx64.efi` 是 `bootmgfw.efi` 的副本（`Get-FileHash` 验证一致）
- [ ] BCD 中 `{bootmgr}` path = `\EFI\Microsoft\Boot\bootmgfw.efi`
- [ ] BCD 中 `{default}` path = `\Windows\system32\winload.efi`
- [ ] BCD 中 `systemroot` = `\Windows`（带反斜杠）
- [ ] 所有盘符已移除（`Get-CimInstance Win32_LogicalDisk` 只剩 C D E）

## 原理

ESP 不存用户数据，只存引导文件。BCD 中 `device partition=D:` 底层存储的是分区 GUID，不是盘符，所以装回原电脑后盘符变化不影响引导定位。

## 换机启动 vs 原机启动

- **装回原机**：以上步骤就够了，硬件环境没变
- **就在这台电脑启动**：还需要处理 AHCI/存储驱动兼容问题，换机成功率不是 100%
