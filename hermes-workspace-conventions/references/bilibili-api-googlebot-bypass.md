# Bilibili API 反爬绕过：双 UA 策略

## 问题

Bilibili 对 API 请求有严格的反爬机制（风控校验 -352、非法访问 -401、验证码拦截），普通 `curl` 或程序化请求返回空或验证码页面。WBI 签名即使算法正确也大概率被拒。

## 方案：两种 UA 各司其职

| 数据 | API | UA | WBI |
|------|-----|-----|-----|
| 用户信息（昵称/头像/粉丝） | `x/web-interface/card?mid=` | Googlebot/2.1 | ❌ 不需要 |
| 视频列表（标题/播放量） | `x/space/arc/search?mid=&ps=8&pn=1&order=click` | BiliApp/1.0 Android | ❌ 不需要 |

**⚠️ 永不尝试 WBI 签名。** 正确实现后仍返回 -352/-403，根本不值得折腾。两个 UA 覆盖所有常用场景。

### 用户信息（Googlebot UA）

```python
import json, urllib.request

def get_bilibili_user(mid: int) -> dict:
    """用 Googlebot UA 获取 B站用户名片"""
    url = f"https://api.bilibili.com/x/web-interface/card?mid={mid}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Referer": "https://www.bilibili.com/",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    if data["code"] != 0:
        raise Exception(f"API 错误: {data.get('message')}")
    card = data["data"]["card"]
    return {
        "name": card["name"],
        "face": card["face"],       # 头像 URL
        "sign": card["sign"],       # 个人简介
        "fans": data["data"]["follower"],
        "videos": data["data"]["archive_count"],
    }
```

### 使用场景

- 飞书链接预览 OG 代理（本会话需求）
- B站 UP 主信息采集
- 任何需要程序化获取 B站用户数据的场景

### 视频列表（移动端 UA）

```python
import json, urllib.request, urllib.parse, time

UA = "BiliApp/1.0 Android"
HEADERS = {"User-Agent": UA, "Referer": "https://m.bilibili.com/"}

def get_top_videos(mid, count=8):
    """用移动端 UA 获取 UP 主热门视频（无需 WBI）"""
    params = urllib.parse.urlencode({"mid": mid, "ps": count, "pn": 1, "order": "click"})
    url = f"https://api.bilibili.com/x/space/arc/search?{params}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    if data.get("code") != 0:
        raise Exception(f"API 错误: {data.get('message')}")
    return [{
        "title": v["title"],
        "play": v["play"],
        "video_review": v.get("video_review", 0),
        "length": v["length"],
        "description": v.get("description", ""),
    } for v in data["data"]["list"]["vlist"]]
```

### 注意事项

- Googlebot UA + 移动端 UA 目前均有效（2026-07），未来可能被封
- 批量拉取时加 `sleep(0.4)` 避免触发频率限制
- `card` API 头像 URL 可能缺协议头，需自行补 `https:`
