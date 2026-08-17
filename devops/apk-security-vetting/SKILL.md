---
name: apk-security-vetting
description: 第三方APK安全检测：权限/SDK/端点/签名静态分析。触发词：检测安全、APK安全、信息截留。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [security, apk, android, 安全检测]
    related_skills: [windows-shell, hermes-remote-gateway]
---

# 第三方 APK/软件安全检测

## When to Use

用户下载第三方 Android APK（TV 客户端/工具）并要求"检测安全性/有没有信息被截留风险"、或推荐/对比第三方软件并要求确认"还在稳定维护"时用。流程：查项目维护状态 → 下载/传输 → 静态分析 → 分级报告。全程用证据说话（GitHub API 字段、解包结果），不凭印象。

## 一、项目维护状态核查（GitHub 源必做）

推荐/选型时不要信 README 和媒体稿，直接查 GitHub API：
```bash
curl -s https://api.github.com/repos/<owner>/<repo> | python3 -c "import json,sys; d=json.load(sys.stdin); print('stars:', d.get('stargazers_count'), '| archived:', d.get('archived'), '| pushed:', d.get('pushed_at'))"
```
- `pushed_at` 距今 >6 个月 = 停更风险。第三方客户端依赖平台 API，停更=随时失效——BBLL 17k star 因 2025-02 停更被淘汰，star 数救不了 API 失效
- `archived: true` = 归档，直接排除（blbl 案例）
- 原仓库可能被删/改名（xiaoyaocz/BBLL → xiaye13579/BBLL），顺着 fork/收集列表找继承者
- "还在稳定维护" = 近 1-3 个月有 release；**release 节奏比 star 数重要**；另看 release notes 判断更新是修 bug 还是加功能
- 权威候选清单：GitHub 上"xx-client-software-collection"类收集仓库（raw.githubusercontent 被墙时用 API readme 端点：`curl -sL -H "Accept: application/vnd.github.raw" https://api.github.com/repos/<owner>/<repo>/readme`）

## 二、下载与跨机传输

- GitHub release assets：`https://github.com/<owner>/<repo>/releases/download/<tag>/<file>`，curl -L 即可（本机 Clash TUN 自动走代理）
- 下载后校验文件头防下到 HTML 错误页：`head -c 4 file | xxd`，ZIP 应为 `50 4b 03 04`（PK\x03\x04）
- **U 盘/目标文件在另一台电脑**：B 机没开 SSH 时用 Tailscale Taildrop：`tailscale file cp <file> <Tailscale-IP>:`，接收方文件落在 Windows "下载"文件夹（部分版本在 Downloads\Tailscale 子目录）。⚠️ 445 端口开放≠能访问（net view 对 Tailscale IP 报错 1702），别在 SMB 上耗时间，直接 Taildrop
- 老设备兼容包判断：项目提供多 APK 时问清设备安卓版本，别默认全下

## 三、APK 静态分析（核心）

```bash
mkdir -p unpack && unzip -o -q <apk> -d unpack
python scripts/scan_apk.py <apk>   # 权限+SDK+端点一键扫
```

四个维度：

1. **权限**（AndroidManifest.xml）：AXML 字符串池是 **UTF-16 编码**，直接 regex 匹配不到——先 `data.replace(b'\x00', b'')` 去零再匹配 `android\.permission\.[A-Z_]+`。敏感权限：READ_CONTACTS/READ_SMS/RECORD_AUDIO/ACCESS_FINE_LOCATION/READ_PHONE_STATE/CAMERA。TV 客户端正常只需要 INTERNET/网络状态/WakeLock；REQUEST_INSTALL_PACKAGES=应用内更新（可接受）；WRITE_EXTERNAL_STORAGE 在老 targetSdk 正常。
2. **统计/广告 SDK**：dex 里搜 firebase/analytics/umeng/appcenter/mixpanel/talkingdata/getui/jpush/crashreport。⚠️ 必须带上下文判断，见误报表。
3. **网络端点**：从 dex 提取 URL 按域名归类：
   - 平台官方域（如 api.bilibili.com/passport.bilibili.com）= 正常，**登录凭据只发这里**
   - 作者服务器（更新检查/远程配置/跳广告 SponsorBlock）= 能看到 IP+视频 ID，看不到凭据
   - 第三方解析站（*jiexi*/player/?url=）= 灰色盗播接口，完全不可信，报告里明确建议禁用
   - 腾讯 X5 内核域（log.tbs.qq.com/tbsall.imtt.qq.com/debugx5.qq.com）= WebView 内核常规通信，正规大厂行为
4. **签名**：META-INF/*.RSA：
```bash
openssl pkcs7 -inform DER -in META-INF/CERT.RSA -print_certs | openssl x509 -noout -subject -dates
```
占位符签名（CN=1/O=1）说明发布随意但完整性没问题；同一项目签名前后变化=包被改过，警惕。

## 四、dex 关键词误报表（最重要，避免吓用户/漏报）

| 关键词 | 常见误报来源 | 真 SDK 特征 |
|---|---|---|
| adjust | Gson 反射错误文案 "adjust the access filter"、Media3 "Adjusting minDurationToRetainAfterDiscardMs" | com.adjust.sdk 类路径 |
| bugly | 腾讯 X5 内核自带（KEY_USE_BUGLY/bugly_switch.txt/bugly is forbiden）——X5 的崩溃开关，非 APP 主动集成 | com.tencent.bugly 独立集成 |
| mta | Media3 "smta: captureFrameRate"、dex 字符串池错位乱码 | com.tencent.stat 包名 |
| getui | B 站 API 方法名 getUgcSeasonFavoriteVideos/getUid | 个推 SDK 类路径 |
| tencent | X5 内核类路径 com.tencent.smtt（出现几百处正常） | — |
| firebase/umeng/appcenter | 很少误报，出现即视为真命中 | — |

判断标准：**看上下文里的类路径/完整字符串，不是看单词出现次数**。

## 五、报告结构（用户偏好：表格+证据+分级）

1. 传输链路安全（HTTPS / Taildrop WireGuard 端到端加密，明确"无截留风险"）
2. 权限清单（标注敏感项，对比两个以上候选时并排表格）
3. 数据收集结论（有无统计 SDK，逐项证据）
4. 登录凭据走向（关键结论：扫码登录走官方 passport，不经第三方）
5. ⚠️ 风险点分级（作者服务器/第三方服务各自能看到什么）
6. 使用建议（锁官方线路、禁用解析功能、扫码登录别输密码）

## 六、Windows 环境坑

- git-bash 的 `/tmp` 是 MSYS 虚拟路径，**Windows 原生 python 看不到**——跨工具共享文件用 `~/Downloads/...` 等 Windows 路径，脚本内也用绝对 Windows 路径
- git-bash 没有 `strings` 命令，用 python 读字节/grep -a 替代
- PowerShell 命令里的 `$_` 会被 bash 双引号吃掉——整条 PowerShell 命令用**单引号**包裹
- `wmic` 在 git-bash 输出乱码，查磁盘/U 盘用 `powershell -NoProfile -Command 'Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, DriveType, VolumeName | Format-Table -AutoSize'`
