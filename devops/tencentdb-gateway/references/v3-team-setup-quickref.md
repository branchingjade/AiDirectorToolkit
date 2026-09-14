## 8. 团队用户/画像/资产设置（2026-08-27 实战）

> 详细流程：`references/v3-team-setup.md`

### 8.1 关键约束

**system_admin ≠ team admin ≠ asset owner**——三者不能互换：
- system_admin 能建用户/建 team，但**不能代替其他用户建 asset**（`assertCallerIsResourceOwner` 严格校验 caller == owner_user_id）
- 每个成员必须用自己的 user_key 调 `asset/create`
- admin user_key 获取方式：SSH 读 NAS 文件 `/volume1/docker/tdai-memory/admin/user_key_admin.txt`（Hermes 流会 mask）

### 8.2 资产创建 API

```
POST /v3/meta/asset/create
Header: x-tdai-user-key: <成员 user_key>
Body: {
  "asset_id": "ast-xxx",        // 必填 UUID
  "asset_type": "chat_memory",
  "name": "施文皓/擅长领域/01",
  "description": "完整画像内容...",
  "team_id": "team-pix2b9boys",
  "owner_user_id": "<成员自己的 user_id>",  // 必填 = caller
  "source_type": "manual_import",
  "visibility": "team",  // team级可见
  "status": "approved",
  "metadata_json": "{\"kind\":\"expertise\",\"real_name\":\"施文皓\",\"username\":\"shiyuhao\"}"
}
```

### 8.3 按成员过滤查询

```
POST /v3/meta/asset/list
Body: {"team_id":"...","asset_type":"chat_memory","owner_user_id":"<user_id>","limit":50}
→ 该成员的全部画像 assets，description 包含完整内容
```

### 8.4 L0/L2/L3 自动抽取（可选，路径 A）

**路径 B（推荐）**：asset metadata 直接存内容，不依赖 pipeline，`description` 字段就是完整画像。

**路径 A（可选进阶）**：`chat-memory/import` → pipeline 抽 L1（需真 LLM key + everyN 阈值）。
- 限制：agent.owner 必须 = caller
- L1 需要 `/data/config/tdai-gateway.yaml` 里的 `llm.api_key` 是真 mimo key
- 默认 everyNConversations=5，单条导入不够触发

### 8.5 脚本位置

| 脚本 | 用途 | 位置 |
|---|---|---|
| `feishu_to_tdb.py` | 飞书 open_id → user_key 查询器 | NAS `/volume1/docker/tdai-memory/admin/feishu_to_tdb.py` |
| `member_profile_lookup.py` | 按 username/open_id/kind 查画像 | NAS `/volume1/docker/tdai-memory/admin/member_profile_lookup.py` |
| `migrate_vault_profile_to_team.py` | Vault 画像批量迁移 | 本地 `scripts/migrate_vault_profile_to_team.py` |
