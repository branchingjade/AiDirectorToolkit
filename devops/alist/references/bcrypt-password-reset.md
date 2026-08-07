# alist 管理员密码重置 — bcrypt 直接写入

当 `alist admin set` 因 db_file 路径问题或 admin 已存在的 bug 无法写入密码时，
用 Python bcrypt 直接写 SQLite 数据库。

## 前置条件

```bash
pip install bcrypt
```

## 完整配方

```python
import bcrypt, sqlite3

DB_PATH = 'C:/Users/HMSJ/Documents/Hermes/tools/alist/data/data.db'
NEW_PASSWORD = 'Huan1120'

# 1. 生成 bcrypt hash（Go 兼容，rounds=10）
hash_str = bcrypt.hashpw(NEW_PASSWORD.encode(), bcrypt.gensalt(rounds=10)).decode()

# 2. 写入数据库
db = sqlite3.connect(DB_PATH)
db.execute('PRAGMA wal_checkpoint(TRUNCATE)')  # 合并 WAL
db.execute('UPDATE x_users SET password = ? WHERE username = ?', (hash_str, 'admin'))
db.commit()

# 3. 验证
for r in db.execute('SELECT username, length(password) FROM x_users WHERE username="admin"'):
    print(f'{r[0]}: pw_len={r[1]} (应为60)')

db.close()
```

## 注意事项

- **先停 alist server**：`powershell -Command "Stop-Process -Name alist -Force"`
- **确认数据库路径**：先用 `find .../alist -name "data.db"` 确认只有正确的那个
- **bcrypt rounds=10**：alist（Go）默认用 10 轮，与 Python bcrypt 兼容
- **hash 长度应为 60**：`$2b$10$...` 格式，验证时检查 `pw_len=60`
- **写入后立即删 WAL**：`rm -f data.db-wal data.db-shm`，避免 server 启动时读到旧状态

## 为什么不用 alist admin set

`alist admin set` 有以下已知问题（v3.61.0）：

1. **db_file 相对路径解析 bug**：`config.json` 中 `db_file: "data.db"` 被解析为相对于当前工作目录，而非 config.json 所在目录 → 可能在错误位置创建新 data.db
2. **admin 已存在时跳过写入**：日志显示 "admin user has been updated" 但数据库密码字段未变化
3. **即使改了 config.json 中 db_file 为绝对路径**，`admin set` 仍可能不写入（本会话实测确认）

直接写 SQLite 是唯一可靠的方式。
