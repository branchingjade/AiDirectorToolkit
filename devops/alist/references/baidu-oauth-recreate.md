# 百度 OAuth 授权 → alist 存储创建完整脚本

## 用户侧操作

1. 在浏览器打开 OAuth URL（用户已登录百度）：
   `https://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id=hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf&redirect_uri=oob&scope=basic,netdisk`

2. 授权后获得 authorization code，交给 agent

## Agent 侧操作

```python
import urllib.request, json, urllib.parse

CODE = '<用户提供的 authorization code>'
ALIST_USER = '妖玉'
ALIST_PASS = '<alist 管理员密码>'

# ── Step 1: 换 refresh_token ──
data = {
    'grant_type': 'authorization_code',
    'code': CODE,
    'client_id': 'hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf',
    'client_secret': 'YH2VpZcFJHYNnV6vLfHQXDBhcE7ZChyE',
    'redirect_uri': 'oob'
}
req = urllib.request.Request('https://openapi.baidu.com/oauth/2.0/token',
    data=urllib.parse.urlencode(data).encode(),
    headers={'Content-Type': 'application/x-www-form-urlencoded'})
resp = json.loads(urllib.request.urlopen(req).read())
REFRESH_TOKEN = resp['refresh_token']
# ⚠️ 不要用 access_token 做任何事——会消耗 refresh_token！

# ── Step 2: 登录 alist ──
data2 = json.dumps({'username': ALIST_USER, 'password': ALIST_PASS}).encode()
req2 = urllib.request.Request('http://localhost:5244/api/auth/login', data=data2,
    headers={'Content-Type': 'application/json'})
ALIST_TOKEN = json.loads(urllib.request.urlopen(req2).read())['data']['token']

# ── Step 3: 删除旧存储（如果存在且报错）──
# 先列出所有存储
req_list = urllib.request.Request('http://localhost:5244/api/admin/storage/list',
    headers={'Authorization': ALIST_TOKEN})
result = json.loads(urllib.request.urlopen(req_list).read())
storages = result.get('data', {}).get('content', [])
for s in storages:
    if s.get('driver') == 'BaiduNetdisk':
        req_del = urllib.request.Request(
            f'http://localhost:5244/api/admin/storage/delete?id={s["id"]}',
            data=b'', headers={'Authorization': ALIST_TOKEN})
        json.loads(urllib.request.urlopen(req_del).read())

# ── Step 4: 创建新存储 ──
new_storage = {
    'mount_path': '/百度网盘',
    'order': 0,
    'driver': 'BaiduNetdisk',
    'cache_expiration': 30,
    'status': '',
    'addition': json.dumps({
        'refresh_token': REFRESH_TOKEN,
        'root_folder_path': '/WebDAV',
        'client_id': 'hq9yQ9w9kR4YHj1kyYafLygVocobh7Sf',
        'client_secret': 'YH2VpZcFJHYNnV6vLfHQXDBhcE7ZChyE',
        'upload_thread': '3',
        'upload_api': 'https://d.pcs.baidu.com'
    }, ensure_ascii=False),
    'remark': '',
    'web_proxy': False,
    'webdav_policy': 'native_proxy',
    'down_proxy_url': '',
}
req_create = urllib.request.Request('http://localhost:5244/api/admin/storage/create',
    data=json.dumps(new_storage).encode(),
    headers={'Authorization': ALIST_TOKEN, 'Content-Type': 'application/json'})
resp_create = json.loads(urllib.request.urlopen(req_create).read())
print(f'创建: code={resp_create.get("code")} msg={resp_create.get("message","OK")}')

# ── Step 5: 验证 ──
req_verify = urllib.request.Request('http://localhost:5244/api/admin/storage/list',
    headers={'Authorization': ALIST_TOKEN})
data_v = json.loads(urllib.request.urlopen(req_verify).read())
for s in data_v.get('data',{}).get('content',[]):
    print(f'{s["mount_path"]}: {s.get("status","")}')
# 期望输出: /百度网盘: work
```

## 关键陷阱

1. **refresh_token 是一次性的**：换到后立即存 alist，不要手动调百度 API 验证，否则 token 被消耗
2. **API update 可能无效**：如果之前存储报过 20016，update 不一定清除缓存状态，必须 delete + create
3. **不要用 bash/curl 发 alist API**：中文用户名编码会损坏 JSON，用 Python urllib
4. **root_folder_path 必须存在**：指定的百度网盘目录需预先创建，否则 alist 初始化失败
