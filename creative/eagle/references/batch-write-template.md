# 批量写入 Eagle 模板

## 使用方法

在 `execute_code` 中定义一次 `w()` 函数，然后每首只传数据 dict 调用。**禁止逐首重写 urllib/json 样板**。

```python
import urllib.request, json

def w(track_id, eagle_id, name, meta):
    """写一首歌的标签和注释到 Eagle。
    meta: {fields: {key:val,...}, tags: "tag1; tag2", tag_text: "分类详情"}
    """
    tags = ["曲多多", "haifanwu", "版权音乐"]
    tags += [t for t in meta.get("tags", "").split("; ") if t]
    
    ann = f"曲目: {name}\n曲多多ID: {track_id}\n"
    ann += "\n".join([f"{k}: {v}" for k, v in meta.get("fields", {}).items() if v])
    ann += "\n\n" + meta.get("tag_text", "")
    
    payload = json.dumps({
        "id": eagle_id,
        "tags": tags[:100],
        "annotation": ann,
        "url": f"https://haifanwu.com/song-detail/{track_id}"
    }, ensure_ascii=False).encode('utf-8')
    
    req = urllib.request.Request(
        "http://localhost:41595/api/item/update",
        data=payload,
        method='POST',
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )
    return json.loads(urllib.request.urlopen(req).read()).get('status')
```

## 调用示例

```python
r = w("2240059", "MQXEWNJ5R0WJ4", "秋意浓", {
    "fields": {"BPM": "78", "时长": "01:05", "表演者": "丁湘花音乐", "作曲": "丁湘花音乐"},
    "tags": "BPM:78; 中国风; 古风; 影视配乐; 游戏; 悲伤(Sad); 大气",
    "tag_text": "使用场景: 影视配乐; 游戏\n流派: 中国风; 古风\n情绪: 悲伤(Sad)\n特征: 大气"
})
print(f"秋意浓: {r}")
```

## 注意事项

- `tags` 是分号分隔字符串，`w()` 会自动拆分并加上基础标签
- `fields` 直接映射为注释行（"key: value"格式）
- `tag_text` 是注释的分类详情部分，原样追加
- tags 数组上限 100 个（Eagle 限制）
- 中文必须 `ensure_ascii=False`
