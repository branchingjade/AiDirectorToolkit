# 从坚果云迁移到百度网盘 WebDAV

当已配置 alist 将百度网盘挂载为本地 WebDAV 后，可将备份目标从坚果云切过来。

## 要改的文件

**`~/AppData/Local/hermes/scripts/backup-hermes-webdav.py`**

改动点：

| 行 | 当前（坚果云） | 改为（百度网盘 via alist） |
|----|---------------|--------------------------|
| `BASE_URL` | `https://dav.jianguoyun.com/dav/hermes-backup` | `http://localhost:5244/dav/%E7%99%BE%E5%BA%A6%E7%BD%91%E7%9B%98/hermes-backup` |
| `AUTH` | 从 `~/.hermes/.webdav-cred` 读取 | Python `base64.b64encode("妖玉:Huan1120".encode("utf-8"))` 预编码 |
| curl `-u` | `-u $AUTH` | `-H "Authorization: Basic $AUTH_B64"` |
| MKCOL | 按需创建远程目录 | 预先 MKCOL 或直接用（405 可忽略） |

## 认证方案（中文用户名）

curl 的 `-u` 参数在 bash/MSYS 环境对非 ASCII 字符 base64 编码不可靠（401）。

**正确方案——Python 预编码**：

```python
import base64

AUTH = "妖玉:Huan1120"
AUTH_B64 = base64.b64encode(AUTH.encode("utf-8")).decode("ascii")
AUTH_HEADER = f"Authorization: Basic {AUTH_B64}"

# curl 调用用 -H 替代 -u
run([CURL, "-s", "-H", AUTH_HEADER, "-T", archive, remote_url])
```

## 验证

```bash
BASE64AUTH=$(echo -n '妖玉:Huan1120' | base64)
curl -s -X PROPFIND "http://localhost:5244/dav/%E7%99%BE%E5%BA%A6%E7%BD%91%E7%9B%98/hermes-backup/" \
  -H "Depth: 1" -H "Authorization: Basic $BASE64AUTH" | grep displayname
```

## 前置条件

- alist 运行中（开机自启已配）
- 百度网盘 `WebDAV/hermes-backup/` 目录已创建
- 备份 cron job `7c3df411d075` 无需改动（脚本路径不变）
