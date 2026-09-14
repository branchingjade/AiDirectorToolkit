# TDB v3 飞书 open_id ↔ user_key 映射：项目级工具与流程

> 项目级资产。**主本在 NAS `/volume1/docker/tdai-memory/admin/`，本文件是 reference 镜像**。
> 跟着项目走，不进类级 skill 知识。改工具/数据 → 改 NAS 那个。

## 1. `feishu_to_tdb.py`（NAS 端映射查询器）

**位置**：`/volume1/docker/tdai-memory/admin/feishu_to_tdb.py`（mode 755）

**用途**：给飞书 sender `open_id` → 查 TDB `user_key`（用于 gateway 飞书 webhook hook 注入下游 ctx）。

**用法**：
```bash
# 列全部映射
python3 /volume1/docker/tdai-memory/admin/feishu_to_tdb.py --list

# open_id → user_key
python3 /volume1/docker/tdai-memory/admin/feishu_to_tdb.py --open-id "ou_7c8f735ad66c252550f265bd392c5d3d"
# → {"username": "yangxuan", "user_id": "usr-pj0ro7it6x", "user_key_masked": "sk-m***dVnQ", "user_key_full": "sk-mem...完整值", ...}

# username → user_key
python3 /volume1/docker/tdai-memory/admin/feishu_to_tdb.py --username housiyu

# 强制刷新缓存（NAS 文件改了后用）
python3 /volume1/docker/tdai-memory/admin/feishu_to_tdb.py --refresh --list
```

**实现要点**：
- 60 秒内存缓存（避免每次飞书消息都读 NAS 文件）
- 缓存 key = `KEYMAP_FILE` mtime + 内容 hash
- 找不到 open_id → `exit 1` + stderr（**不静默**——gateway hook 拿 None 应该早报错）

## 2. 映射表数据

**完整 mapping（含 user_key 明文）**：`/volume1/docker/tdai-memory/admin/feishu_keymap.json`（mode 600）

**公开 metadata（masked，写在 `meta_teams.metadata_json`）**：
- key：`feishu_user_key_map`
- 内容：`{username: {open_id, user_id, key_id, default}}` —— **不包含完整 user_key**
- 文件路径提示：`feishu_keymap_file` 字段指向完整文件

**典型使用流程**：
1. 飞书 sender 发消息，open_id 出现在 webhook payload
2. `feishu_to_tdb.py --open-id <open_id>` 查 user_key
3. 把 user_key 注入到 DSH/Hermes 调 TDB 的 `x-tdai-user-key` header
4. 消息 + 记忆自动归属到该 user

## 3. 改映射表的流程（新增/删除成员）

**新增成员**：
1. 飞书成员入群（open_id 由飞书提供）
2. `initAdminUser` 或 `user/create-with-key` 创建 TDB user（system_admin 用 key）
3. SQL 直接 INSERT 到 `meta_team_members`（参考 tencentdb-gateway skill 坑 17）
4. 改 `/volume1/docker/tdai-memory/admin/feishu_keymap.json` 加 `{username: {open_id, user_id, user_key, key_id, default}}`
5. 调一次 `feishu_to_tdb.py --list` 验证

**删除成员**：
1. SQLite：`UPDATE meta_user_keys SET status='revoked' WHERE user_id='usr-xxx'`（撤销所有 key）
2. SQLite：`UPDATE meta_team_members SET status='inactive' WHERE user_id='usr-xxx'`
3. `feishu_to_tdb.py --refresh --list` 确认不再返回

**更新 user_key**（rotate/泄露）：
1. 调 `user-key/revoke` + `user-key/create` 生成新 key
2. 改 `feishu_keymap.json` 的对应 username 的 user_key 字段
3. 通知所有引用此 key 的客户端（gateway / DSH / 自建后台）

## 4. TDB v3 user_key 端点

| 操作 | API 端点 | 备注 |
|---|---|---|
| 创建 | `POST /v3/meta/user-key/create` | body `{user_id, name, expires_at?}` |
| 列出 | `POST /v3/meta/user-key/list` | body `{user_id, limit, offset}` |
| 获取（脱敏）| `POST /v3/meta/user-key/get` | body `{key_id}` → 返回 key_prefix（**不是** 完整 key_value）|
| 撤销 | `POST /v3/meta/user-key/revoke` | body `{key_id}` |
| **完整 key_value** | **SQLite 直读** `meta_user_keys.key_value` | 即使 system_admin 也不返明文 |

## 5. 已知边界

- **user_key 不在 API 响应里**——`toPublicUserKey` 永远不返 `key_value`，只返 `key_prefix`（前 8 + *** + 后 4）
- **system_admin 调 team-member/* 报 403 "not a team member"**——见 tencentdb-gateway skill 坑 17
- **system_admin 调 team/list 报 400 "user_id or user_key is required"**——team/list 不是"列出我加入的 team"，是"按 user_id 查"
- **v3 没有 user.update 端点**——见 tencentdb-gateway skill 坑 15，改字段只能 SQL

## 6. 完整 onboarding 流程（飞书成员入项目）

```
[飞书] open_id 出现
   ↓
[TDB] user/create 创建账号（system_admin 走 init-admin-like 流程）
   ↓
[TDB] user-key/create 生成 user_key
   ↓
[SQL] INSERT meta_team_members（跳过 v3 API）
   ↓
[NAS] feishu_keymap.json 加 entry
   ↓
[gateway] 飞书 webhook hook 注入 user_key 到 DSH/Hermes 请求
   ↓
[验证] 飞书发条消息，看 TDB L0 记录 user_id=该成员
```