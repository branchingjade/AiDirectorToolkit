# 坚果云 WebDAV 备份

## 凭据

- 地址: `https://dav.jianguoyun.com/dav/`
- 账号: 坚果云注册邮箱
- 密码: **应用密码**（非登录密码），在 坚果云设置 → 安全选项 → 第三方应用管理 中生成

凭据存于 `~/.hermes/.webdav-cred`（chmod 600）。

## 验证连接

```bash
curl -s -u "user@example.com:APP_PASSWORD" \
  -X PROPFIND -H "Depth: 1" \
  "https://dav.jianguoyun.com/dav/"
```

## 远程目录操作

```bash
# 创建目录
curl -u "user:pass" -X MKCOL "https://dav.jianguoyun.com/dav/DIRNAME/"
# 上传文件
curl -u "user:pass" -T local.tar.gz "https://dav.jianguoyun.com/dav/DIRNAME/file.tar.gz"
# 列出文件
curl -s -u "user:pass" -X PROPFIND -H "Depth: 1" "https://dav.jianguoyun.com/dav/DIRNAME/"
# 删除文件
curl -u "user:pass" -X DELETE "https://dav.jianguoyun.com/dav/DIRNAME/file.tar.gz"
```

## Pitfalls

- **URL 编码**：curl 不自动编码中文路径。目录/文件名用纯 ASCII，否则返回 HTTP 400。
- **MKCOL 幂等**：目录已存在时返回 405 Method Not Allowed，可在脚本中忽略。
- **上传返回码**：成功为 201（新建）或 204（覆盖）。
