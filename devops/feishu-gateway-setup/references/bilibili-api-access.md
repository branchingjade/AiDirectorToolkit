# Bilibili API Access Patterns

Techniques for accessing Bilibili's public APIs without being blocked by anti-bot measures.

## Mobile UA Bypass (for space/arc/search)

Bilibili's `x/space/wbi/arc/search` endpoint requires WBI signing when accessed with desktop User-Agents, but **accepts requests with a mobile app User-Agent without WBI**:

```bash
curl -s \
  -H "User-Agent: BiliApp/1.0 Android" \
  -H "Referer: https://m.bilibili.com/" \
  "https://api.bilibili.com/x/space/arc/search?mid=431169809&ps=5&pn=1&order=click"
```

This works for fetching video lists by UP主 ID. Rate limit: add 0.3-0.5s sleep between calls for batch operations.

## Googlebot UA (for card API + HTML scraping)

The `x/web-interface/card` endpoint (user profile info) works with a Googlebot User-Agent:

```bash
curl -s \
  -H "User-Agent: Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" \
  -H "Referer: https://www.bilibili.com/" \
  "https://api.bilibili.com/x/web-interface/card?mid=431169809"
```

Returns: name, face (avatar), sign, follower count, archive count, level, official verification.

Also works for scraping the space page HTML to extract `<title>` and `<meta>` tags.

## WBI Signing (when UA bypass fails)

The WBI signing algorithm involves:
1. Fetch `img_key` and `sub_key` from `x/web-interface/nav` → `data.wbi_img`
2. Mix: concatenate keys → take even-indexed chars, then odd-indexed chars → take first 32 chars
3. Sign: sort params → urlencode → append mix_key → MD5 → add `w_rid` and `wts` to params

Current Python implementation (see `fetch_videos2.py`):
```python
concat = img_key + sub_key
even = [concat[i] for i in range(len(concat)) if i % 2 == 0]
odd = [concat[i] for i in range(len(concat)) if i % 2 == 1]
mix_key = "".join(even + odd)[:32]

wts = int(time.time())
params["wts"] = wts
query = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
w_rid = hashlib.md5((query + mix_key).encode()).hexdigest()
params["w_rid"] = w_rid
```

## Prioritized Strategy

1. Try **mobile UA** (`BiliApp/1.0 Android`) first — works for space/arc/search
2. Try **Googlebot UA** for card API and HTML scraping
3. Fall back to **WBI signing** as last resort

## Common Endpoints

| Endpoint | Purpose | Best UA |
|---|---|---|
| `x/web-interface/card?mid=` | User profile | Googlebot |
| `x/space/arc/search?mid=&ps=&pn=` | Video list | BiliApp mobile |
| `x/space/wbi/arc/search` | Video list (signed) | Desktop + WBI |
| `x/web-interface/nav` | Get WBI keys | Any |
