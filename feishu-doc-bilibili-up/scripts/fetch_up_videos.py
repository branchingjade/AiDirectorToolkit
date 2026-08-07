"""
批量拉取 B站 UP主 视频数据（移动端 API，无需 WBI）
用法: python fetch_up_videos.py
输出: up_videos.json
"""
import json, time, urllib.request, urllib.parse, ssl

UA = "BiliApp/1.0 Android"
HEADERS = {"User-Agent": UA, "Referer": "https://m.bilibili.com/"}
ctx = ssl.create_default_context()

# 填入 UP 列表: [(mid, name), ...]
mids = [
    ("431169809", "示例UP主"),
]

results = {}
for mid, name in mids:
    print(f"{name}...", end=" ", flush=True)
    params = urllib.parse.urlencode({"mid": mid, "ps": 8, "pn": 1, "order": "click"})
    url = f"https://api.bilibili.com/x/space/arc/search?{params}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"ERR:{e}")
        continue
    if data.get("code") == 0:
        vlist = data["data"]["list"]["vlist"]
        results[mid] = [{"title": v["title"], "play": v["play"],
            "video_review": v.get("video_review", 0),
            "length": v["length"], "created": v["created"],
            "description": v.get("description", "")[:100]} for v in vlist]
        print(f"OK({len(vlist)})")
    else:
        print(f"FAIL:{data.get('code')}")
    time.sleep(0.4)

with open("up_videos.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"Done. {len(results)} UP主")
