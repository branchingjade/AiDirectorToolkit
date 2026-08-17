---
name: credential-auto-renewal
version: 1.0.0
description: "用 cron job 自动续期 OAuth token / 凭据的通用模式。覆盖飞书 lark-cli 及可扩展到其他平台。触发词：token 过期、自动续期、refresh token、OAuth 续期、lark-cli 自动续。"
---

# 凭据自动续期模式

任何带 refresh token 的 OAuth 凭据都可以用 cron job 实现自动续期。核心原则：**检查不是修复——必须真正触发 API 调用才能延长 token 有效期**。

## 通用模式

```
检查脚本（只读状态）→ 如果快过期 → 跑一个轻量 API 调用触发续期 → 报告结果
                                              ↓
                                      如果续期失败 → 提醒用户手动授权
```

**关键**：检查脚本只负责判断状态，修复步骤必须写在 cron job prompt 里（而不是指望用户看到提醒后手动操作）。

## 飞书 / lark-cli

### 续期原理

飞书 OAuth 的 refresh token 有固定有效期（首次授权后约 30 天），但**每次成功使用后有效期会自动延长**。

lark-cli 在执行任何 user 身份 API 调用时，如果发现 access token 已过期，会自动用 refresh token 换新 access token——这个动作同时也延长了 refresh token 的有效期。

### 触发续期的最简命令

```bash
lark-cli im +chat-list --as user --page-limit 1
```

⚠️ **2026-08-13 实测坑：`lark-cli whoami` 不触发刷新**（v1.0.82）。whoami 走本地缓存读取身份，tokenStatus 保持 needs_refresh 不变。必须用**真实 user API 调用**（如 `im +chat-list --as user --page-limit 1`，无额外 scope 要求）才会触发 refresh token 使用并延长有效期。实测：续期后 access token 从已过期→valid，refresh token 到期从 08-15 延长到 08-20（+5 天）。验证方式：`lark-cli auth status` 里 tokenStatus 变 valid、refreshExpiresAt 变新日期。

### 检测脚本

`check-lark-auth.py`（位于 `scripts/check-lark-auth.py`）通过 `lark-cli auth status` 读取 token 状态，判断剩余有效期。输出带 emoji 标记：
- `✅` = 正常，无需操作
- `⚠️` = 即将/已经过期，需要续期

### Cron job prompt 模板

```
每天检查飞书用户身份 OAuth token 是否快过期。如果快过期且 refresh token 还有效，自动触发续期；如果 refresh token 也已过期，提醒用户手动重新授权。

步骤：
1. 用 terminal 执行 python3 <path>/check-lark-auth.py
2. 读取脚本输出判断状态：
   - 如果输出包含 ✅（正常）→ 不发送任何消息，直接结束
   - 如果输出包含 ⚠️（即将过期或已过期）→ 继续步骤3
3. ⚠️ 情况下的自动续期尝试：
   - 执行 lark-cli im +chat-list --as user --page-limit 1（触发 refresh token 使用，延长有效期；⚠️ whoami 走本地缓存不触发刷新）
   - 如果成功 → 报告"Token 已自动续期成功 ✅"
   - 如果失败 → 提醒用户执行：lark-cli auth login --domain all --no-wait
4. 最终回复就是状态消息正文，正常时回复"正常"即可。
```

### 陷阱

- **检查不修陷阱**：只跑 `lark-cli auth status` 读取状态不会触发 refresh token 使用，token 照样过期。必须再跑一个真正调用飞书 API 的命令（如 `lark-cli im +chat-list --as user`）。这是最容易踩的坑——检查脚本输出"✅ 正常"，用户收到"正常"报告就放心了，实际上 token 从未被使用、从未被续期，等到 refresh token 本身过期才发现问题。
- **whoami 不触发刷新**：`lark-cli whoami` 走本地缓存，不算真实 API 调用。触发刷新必须用会真正打到飞书 API 的命令（`im +chat-list --as user` / `auth status` 后的任意 user 操作）。2026-08-13 实测确认。
- **Windows 下 Python 子进程调 lark-cli**：lark-cli 是 shell 包装脚本（`#!/bin/sh`），Python `subprocess.run(["lark-cli", ...])` 会报 WinError 193（不是有效 Win32 程序）。必须调真实入口：`node.exe node_modules/@larksuite/cli/scripts/run.js <args>`（node 与 run.js 都在 `~/AppData/Local/hermes/node/` 下）。check-lark-auth.py 已内置该逻辑。
- **refresh token 过期**：一旦 refresh token 本身过期，自动续期就失效了，只能重新走完整 OAuth 授权流程。所以 cron job 的频率要高于 refresh token 的有效期（推荐每天一次）。
- **验证数据**：实测 `lark-cli whoami` 触发续期后，refresh token 到期从 2026-07-24 延长到 2026-07-30（+6 天），证明只要实际使用 token 就会自动延长有效期。
- **cron 子进程环境**：lark-cli 的 auth 状态存在用户 home 目录下，cron 子进程能读到（如果是同一个用户运行的）。

### Cron job 审计清单

排查所有 cron job 时逐一过：

1. 这个 job 是只读报告还是实际做了修改？
2. 如果只读，是刻意设计（如版本简报）还是遗漏？
3. 检查脚本的"ACTION"提示会不会被 cron 实际执行，还是只是打印到 stdout 就没了？
