# V3 Team Setup 实战（2026-08-27）

> 把团队成员 + 画像数据搬进 TDB 的完整流程

## 前置条件

- tdb-hub/tdb-core/tdb-proxy 已运行（健康端口 8125/8420/8096）
- `init-admin` 已跑过（admin user + default-team 已创建）
- admin `user_key` 已获取（写到 `/volume1/docker/tdai-memory/admin/user_key_admin.txt`）

## Step 1：建用户 + team member（用 admin key）

```python
# 每个成员用 admin user_key 调 /v3/meta/user/create
POST /v3/meta/user/create
Header: x-tdai-user-key: admin_key
Body: {
  "username": "yangxuan",
  "external_id": "ou_7c8f735ad66c252550f265bd392c5d3d",  # 飞书 open_id
  "auth_provider": "feishu",
  "display_name": "杨璇"
}
# → user_id = "usr-pj0ro7it6x"

# 加入 team
POST /v3/meta/team-member/add
Body: {
  "team_id": "team-pix2b9boys",
  "user_id": "usr-pj0ro7it6x",
  "role": "member"
}
```

**坑**：`team-member/add` 需要 caller 是 team admin（admin 默认是）。
admin 调用时 `ctx.userId = admin.user_id`，但 `assertCallerIsTeamAdmin` 要求 `getTeamMember(teamId, callerId)` 返回 role=admin——admin 在 team 成员表里必须有 role=admin 记录。

## Step 2：建 chat_memory assets（用成员自己的 key）

```python
# 每个成员用自己的 user_key
POST /v3/meta/asset/create
Header: x-tdai-user-key: <yangxuan's user_key>
Body: {
  "asset_id": "ast-xxx",
  "asset_type": "chat_memory",
  "name": "杨璇/协作备注/01",
  "description": "完整画像内容...",
  "team_id": "team-pix2b9boys",
  "owner_user_id": "usr-pj0ro7it6x",  # = caller 自己
  "source_type": "manual_import",
  "visibility": "team",
  "metadata_json": "{\"kind\":\"collab_note\",\"real_name\":\"杨璇\"}"
}
```

**不能用 admin key 给其他用户建 asset**——`assertCallerIsResourceOwner` 会拒绝。

## Step 3：查询（用 admin key）

```python
# 按 owner 过滤
POST /v3/meta/asset/list
Body: {
  "team_id": "team-pix2b9boys",
  "asset_type": "chat_memory",
  "owner_user_id": "usr-pj0ro7it6x"
}
# → 该成员的全部画像 assets
```

## Step 4：飞书身份 → TDB 身份映射

写到 `/volume1/docker/tdai-memory/admin/feishu_keymap.json`：
```json
{
  "yangxuan": {
    "open_id": "ou_7c8f735ad66c252550f265bd392c5d3d",
    "user_id": "usr-pj0ro7it6x",
    "user_key": "sk-mem-...",
    "key_id": "uky-pj0r6sgsl8"
  }
}
```

查询工具：`feishu_to_tdb.py --open-id <open_id>` → 返回该飞书用户的 TDB user_key。

## 已知限制

1. **system_admin 不能代替其他用户建 asset**——每个成员必须用自己的 user_key 调 asset/create
2. **chat-memory/import 需要 agent.owner = caller**——只能往自己的 agent 导入
3. **L1/L2/L3 pipeline 抽取需要 LLM + everyN 阈值**——推荐走路径 B（asset metadata 直接存内容）
4. **Hermes 对话流对 `sk-` 前缀做 mask**——admin user_key 真值只能从 NAS 文件读
