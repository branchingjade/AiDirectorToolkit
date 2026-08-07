---
name: windows-boot-repair
description: Repair unbootable Windows systems — rebuild ESP, recreate BCD, fix boot manager. Covers bcdboot pitfalls, Secure Boot workarounds, and manual BCD creation with bcdedit.
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [windows, boot, repair, esp, bcd, bcdboot, bcdedit, diskpart]
    category: devops
---

# Windows Boot Repair

修复无法启动的 Windows 系统——重建 ESP（EFI 系统分区）、修复 BCD、恢复引导。

## 触发条件

- 开机报 `Boot Device Not Found` / `No bootable device` / `0xc0000098` / `0xc000000f`
- BIOS 中启动项消失
- ESP 分区文件损坏、BCD 损坏
- 硬盘从其他电脑拆下后无法启动（原电脑上就已不能启动）

## 诊断流程

### 1. 确认分区结构

```bash
powershell -Command "Get-Disk | Format-Table -AutoSize"
powershell -Command "Get-Partition -DiskNumber X | Format-Table DiskNumber,PartitionNumber,DriveLetter,Size,Type,GptType"
```

ESP 特征：FAT32、100–500MB、GptType `{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}`。

### 2. 挂载 ESP 检查内容

```bash
echo 'select disk X
select partition Y
assign letter=Z
exit' | diskpart

# 检查引导文件是否存在
powershell -Command "Get-ChildItem Z:\EFI\Microsoft\Boot -Depth 1"
```

## 修复方法 A：bcdboot（优先尝试）

```bash
bcdboot C:\Windows /s Z: /f UEFI
```

**注意**：修复从其他电脑拆下的硬盘时，源路径应使用该硬盘上的 Windows（如 `D:\Windows`），不要用当前系统的 Windows。

### bcdboot 常见失败及原因

| 错误 | 含义 | 解决 |
|------|------|------|
| `WinVerifyTrust failed 0x80092003` | Secure Boot 签名验证失败 | 换手动方式（方法 B） |
| `Failed to validate boot manager checksum 0xc1` | 缺少 EFI_EX 引导文件，源 Windows 版本不支持当前安全启动策略 | 换手动方式（方法 B） |
| `尝试复制引导文件失败`（无详细错误） | 综合原因 | 加 `/v` 看详细日志后再判断 |

### 坑：不要混用不同 Windows 版本的引导文件

修复外来的系统盘时，`bootmgfw.efi` 等引导文件必须来自该盘自己的 `X:\Windows\Boot`，**不能用当前电脑的引导文件替代**。

不同 Windows 版本的 `bootmgfw.efi` 文件大小有明显差异（例如 Win10 ~1.6MB，Win11 ~3.1MB），混用会导致启动失败或安全启动拒绝。

## 修复方法 B：手动重建（bcdboot 失败时）

### 步骤 1：格式化 ESP

```bash
echo 'select disk X
select partition Y
format fs=fat32 quick
assign letter=Z
exit' | diskpart
```

### 步骤 2：从源系统复制引导文件

**关键**：从源 Windows（待修复系统）的 `Boot` 目录复制，不是当前系统。

```powershell
# 创建目录结构
New-Item -ItemType Directory -Path Z:\EFI\Boot -Force
New-Item -ItemType Directory -Path Z:\EFI\Microsoft\Boot -Force

# 核心引导文件
Copy-Item <SourceDrive>:\Windows\Boot\EFI\bootmgfw.efi Z:\EFI\Microsoft\Boot\ -Force
Copy-Item <SourceDrive>:\Windows\Boot\EFI\bootmgr.efi Z:\EFI\Microsoft\Boot\ -Force
Copy-Item <SourceDrive>:\Windows\Boot\EFI\bootmgfw.efi Z:\EFI\Boot\bootx64.efi -Force

# 其他引导资源（语言文件、内核调试 DLL 等）
robocopy "<SourceDrive>:\Windows\Boot\EFI" "Z:\EFI\Microsoft\Boot" *.efi *.dll *.stl *.p7b /S /R:1 /W:1
```

### 步骤 3：用 bcdedit 创建 BCD

```
bcdedit /createstore Z:\EFI\Microsoft\Boot\BCD
bcdedit /store Z:\EFI\Microsoft\Boot\BCD /create {bootmgr} /d "Windows Boot Manager"
bcdedit /store Z:\EFI\Microsoft\Boot\BCD /set {bootmgr} device partition=Z:

bcdedit /store Z:\EFI\Microsoft\Boot\BCD /create /d "Windows" /application osloader
# 返回一个 {GUID}，后续命令中用这个 GUID

bcdedit /store Z:\EFI\Microsoft\Boot\BCD /set {GUID} device partition=<SystemDrive>:
bcdedit /store Z:\EFI\Microsoft\Boot\BCD /set {GUID} osdevice partition=<SystemDrive>:
bcdedit /store Z:\EFI\Microsoft\Boot\BCD /set {GUID} path \Windows\system32\winload.efi
bcdedit /store Z:\EFI\Microsoft\Boot\BCD /set {GUID} systemroot \Windows
bcdedit /store Z:\EFI\Microsoft\Boot\BCD /displayorder {GUID} /addlast
bcdedit /store Z:\EFI\Microsoft\Boot\BCD /default {GUID}
```

BCD 内部用 GPT 分区 GUID 存储 device 引用，盘符只是创建时的临时寻址方式。硬盘装回原电脑后分区 GUID 不变，不受盘符变化影响。

### 步骤 4：验证

```
bcdedit /store Z:\EFI\Microsoft\Boot\BCD /enum
```

确认 `{bootmgr}` 的 device 指向 ESP、`{default}` 的 device/osdevice 指向系统分区、path 和 systemroot 正确。

### 步骤 5：移除盘符、装回原机

```
echo 'select disk X
select partition Y
remove letter=Z
exit' | diskpart
```

## 权限要求

Windows 上所有磁盘操作（diskpart、格式化、分配盘符、bcdboot、bcdedit /store）都需要**管理员权限**。

在 Hermes 中：**退出 → 右键以管理员身份运行**。Hermes terminal 继承进程权限，无法在会话中提权。

## 盘符冲突

常见问题：
- **幽灵盘符**：`Get-PSDrive` 显示盘符存在但 `Get-Volume` 找不到对应卷 → 旧映射残留，用 `Remove-PartitionAccessPath` 清理
- **盘符已被占用**：换未使用的盘符（Z:、Y:、W: 等）
- **格式化后盘符自动脱落**：需重新 `assign letter=`
