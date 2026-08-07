# lark-cli OAuth Token 生命周期

## 架构

```
Hermes adapter.py ──WebSocket/REST──► 飞书 API (bot身份)
     独立，不依赖 lark-cli

lark-cli ──OAuth user_access_token──► 飞书 API (用户身份)
     仅在需要「以用户身份」操作时使用
```

## Token 类型

| Token | 有效期 | 说明 |
|-------|--------|------|
| access_token | 2 小时 | 每次 API 调用自动刷新 |
| refresh_token | 7 天（个人版应用）| 由平台固定，不可配置 |

企业自建应用 refresh_token 为 30 天，个人版应用固定 7 天。

## 自动续期

lark-cli 在 access_token 过期后、下次 API 调用时自动用 refresh_token 续期。只要 7 天内至少调用一次 lark-cli，token 永不过期。`lark-cli auth status` 输出中：
- `tokenStatus: "valid"` — 正常
- `tokenStatus: "needs_refresh"` — 过期但可自动刷新
- `tokenStatus: "expired"` — refresh_token 也过期，需重新授权

## 手动重新授权

当 refresh_token 过期（7 天未使用）时：

```bash
# 1. 获取授权 URL（务必加 send_as_user scope）
lark-cli auth login --recommend --scope "im:message.send_as_user" --no-wait --json

# 2. 生成二维码
lark-cli auth qrcode "<verification_url>" -o qr.png

# 3. 用户扫码授权后
lark-cli auth login --device-code <device_code>
```

**关键：** `--recommend` 不包含 `im:message.send_as_user`，必须显式 `--scope`。

## 提醒机制

`scripts/check-lark-auth.py` 每天检查 token 状态：
- 过期前 24 小时 → 飞书 DM 提醒
- 已过期 → 飞书 DM 提醒重新授权
- 正常 → 静默

通过 cron job `d89acf50b8a2` 每天 9:00 执行。

## 安装

```bash
npm install -g @larksuite/cli
```

**不安装：** OpenClaw、lark-* skills、任何其他 OpenClaw 生态组件。Hermes 只用 lark-cli 做 OAuth。
