# 飞书应用迁移完整清单

从旧飞书应用切换到新应用（如商店应用 → 企业自建应用）的完整步骤和常见陷阱。

## 触发条件

- 更换飞书 App ID / App Secret
- 从商店应用迁移到企业自建应用（或反过来）
- 更换飞书企业租户（新应用在新企业下）

## 完整步骤

### 1. 更新 lark-cli 配置

```bash
echo "<新app_secret>" | lark-cli config init --app-id <新app_id> --app-secret-stdin --brand feishu --force-init
```

### 2. 更新 Hermes .env

在 `~/.hermes/.env` 中更新：
```
FEISHU_APP_ID=<新app_id>
FEISHU_APP_SECRET=<新app_secret>
FEISHU_CONNECTION_MODE=websocket
FEISHU_GROUP_POLICY=open
```

⚠️ `.env` 是受保护文件，用 terminal echo 追加：
```bash
echo "FEISHU_APP_ID=..." >> "$HOME/AppData/Local/hermes/.env"
```

### 3. 绑定身份

```bash
lark-cli config bind --identity bot-only
```

⚠️ `bot-only` 会锁定 strict-mode 为 bot，此后 auth login 会报 `failed_precondition`。

### 4. 解除 strict-mode（仅 bot-only bind 需要）

```bash
lark-cli config strict-mode off
```

### 5. User OAuth 授权

```bash
lark-cli auth login --recommend --scope "im:message.send_as_user" --no-wait --json
```

生成二维码 → 用户扫码 → 轮询 device_code 完成登录。

⚠️ 每次 auth login 的新 device_code 不能缓存，过期（10分钟）需重新发起。

### 6. 在开发者后台开通 Bot 权限

**https://open.feishu.cn/app/<app_id>/permission**

企业自建应用直接勾选，无需审核。需开通的关键 scope：

**消息与群聊**：`im:message`, `im:message:readonly`, `im:message:group_msg:get_as_user`, `im:message.p2p_msg:get_as_user`, `im:message.send_as_user`, `im:chat:read`, `im:chat:update`, `im:chat.members:read`, `im:chat.members:write_only`, `im:chat:moderation:read`, `im:chat:moderation:write_only`

**云文档**：`drive:drive.metadata:readonly`, `drive:file:download`, `drive:file:upload`, `docx:document:readonly`, `docx:document:create`, `docs:document.content:read`, `docs:document:export`, `sheets:spreadsheet:read`, `sheets:spreadsheet:create`, `slides:presentation:read`, `slides:presentation:create`

**通讯录**：`contact:user.base:readonly`, `contact:user:search`

**日历/会议/任务**：`calendar:calendar:readonly`, `vc:meeting.search:read`, `vc:record:readonly`, `task:task:read`, `task:task:write`, `task:tasklist:read`

**审批/知识库/多维表格**：`approval:instance:read`, `wiki:space:read`, `wiki:node:read`, `wiki:node:create`, `base:table:read`, `base:record:read`, `base:app:read`

### 7. 验证

```bash
lark-cli auth status --json --verify
```

检查 bot 和 user 都是 `ready`，user token 是 `valid`。

### 8. 启用 Hermes Gateway

```bash
hermes config set platforms.feishu.enabled true
hermes gateway restart
```

验证连接：
```bash
grep "feishu connected" "$(dirname "$(hermes config path)")/logs/gateway.log" | tail -1
```

### 9. 重新设置 Home Channel

在飞书 DM 里发 `/sethome`。

### 10. 更新 Cron Job 投递目标 ⚠️ 容易漏

切换应用后 user openId 会变化，导致 DM 的 `oc_` chat_id 也变化。

**步骤**：

1. 找到新应用的 DM chat_id：
```bash
lark-cli --as bot im +messages-send --user-id <新openId> --text "test" --json
```
从响应的 `data.chat_id` 获取新的 `oc_xxx`。

2. 列出所有 cron job：
```bash
# 在 Hermes 会话中用 cronjob action=list
```

3. 逐个更新 deliver 目标：
```bash
# 在 Hermes 会话中用 cronjob action=update，deliver=feishu:oc_新chat_id
```

⚠️ 即使 cron job 看起来 deliver 到群聊 `oc_xxx`，群聊 ID 不变，但如果之前用旧 bot 发的，新 bot 可能不在群里（报 `[230002] Bot/User can NOT be out of the chat`）。需要把新 bot 拉进群。

## 企业自建应用 vs 商店应用

| | 商店应用 | 企业自建应用 |
|---|---|---|
| 使用范围 | 跨企业/多租户 | 仅创建它的企业租户 |
| 权限开通 | 敏感权限需飞书官方审核 | 管理员直接勾选，无需审核 |
| 权限池 | 受限 | 更大（通讯录批量读、部门管理等） |
| API 限额 | custom bot 5 QPS / 100 QPM | 同左，custom bot 硬限制不变 |
| 发布流程 | 需商店审核 | 管理员安装即可 |

## 常见陷阱

1. **只更新了 lark-cli 没更新 .env** → gateway 用旧凭据，lark-cli 用新凭据，行为不一致
2. **bot-only bind 后直接 auth login** → strict-mode 锁定，报 `failed_precondition`
3. **换了应用忘记 /sethome** → gateway 不知道 home channel，不发消息
4. **cron job deliver 目标没更新** → 推送发到旧 DM，用户收不到（`Bot/User can NOT be out of the chat`）
5. **新 bot 没进群** → 群聊 cron 投递失败，错误码 230002
6. **device_code 过期** → 10 分钟有效期，过期需重新 `--no-wait` 获取新链接
7. **`hermes config set` 用 `&&` 连写导致并发冲突** → 多个 config set 用 `&&` 串联时可能触发 `PermissionError: [WinError 5] 拒绝访问。`（config.yaml 文件锁冲突）。分开执行，每个 set 单独一个 terminal 调用。
