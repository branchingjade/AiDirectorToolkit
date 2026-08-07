---
name: quduoduo-eagle-sync
description: "从曲多多(haifanwu.com)提取版权音乐元数据并同步到 Eagle。触发词：曲多多、haifanwu、版权音乐元数据、Eagle 批量标签。"
---

# 曲多多 → Eagle 元数据同步

## 前置条件
- Eagle 运行中（localhost:41595）
- Chrome CDP 运行中（localhost:9222），已登录 haifanwu.com（`chrome-cdp-profile`）

### 0. 登录检测（每次开始前）
页面始终显示"登录 / 注册"文字，**不能据此判断未登录**。用 JS 检测：
```js
// browser_console 执行
document.body.innerText.includes('个人会员') || document.body.innerText.includes('退出')
```
返回 `true` = 已登录。`false` = 需切有头模式让用户扫码，参考 `hermes-browser-cdp` skill。

## 流程

### 1. 定位 Eagle 中的曲目
```bash
# 先定位文件夹（用户会告知路径，如"项目/《犬子无双》/素材/音乐"）
curl -s http://localhost:41595/api/folder/list | python3 -c "...找文件夹名..."

# 列出文件夹内曲目
curl -s "http://localhost:41595/api/item/list?folders=<FOLDER_ID>" | python3 -c "...过滤曲多多..."
```

### 2. 提取元数据（核心）
**直接 URL 导航，不走 SPA 路由：**
```
browser_navigate → https://haifanwu.com/song-detail/<TRACK_ID>
browser_console → 提取 DOM 数据
```

**提取 JS（`document.body.innerText` 解析）：**
```js
(function(){
var text=document.body.innerText;
var lines=text.split('\n').map(l=>l.trim());
var infoIdx=lines.lastIndexOf('歌曲基本信息');
var bpm=text.match(/BPM:\s*(\d+)/);
var dur=text.match(/(\d{2}:\d{2})/);
var fields=['表演者','作词','作曲','歌词','所属专辑','所属曲库'];
var values={};
for(var j=infoIdx;j<Math.min(infoIdx+20,lines.length);j++){
  var l=lines[j];
  for(var f=0;f<fields.length;f++){
    if(l===fields[f]+'：'){
      var vals=[];
      for(var k=j+1;k<lines.length;k++){
        var nl=lines[k];
        if(nl==='查看专辑'||nl==='歌曲标签')break;
        if(nl.indexOf('：')>0)break;
        if(nl&&nl!=='-')vals.push(nl);
      }
      values[fields[f]]=vals.join('; ');
    }
  }
}
var sections={使用场景:[],流派:[],情绪:[],特征:[],器乐:[],速度:[],年代:[],调:[],关键词:[]};
var current=null;
for(var m=infoIdx;m<lines.length;m++){
  var line=lines[m];
  if(line==='我们的优势')break;
  if(sections.hasOwnProperty(line)){current=line;}
  else if(current&&line&&line!=='查看专辑'&&line!=='歌曲标签'){
    var isF=false;
    for(var n=0;n<fields.length;n++)if(line===fields[n]+'：')isF=true;
    if(!isF)sections[current].push(line);
  }
}
var tags={};
for(var s in sections)if(sections[s].length)tags[s]=sections[s].join('; ');
return JSON.stringify({bpm:bpm?bpm[1]:'',duration:dur?dur[1]:'',
  performer:values['表演者']||'',composer:values['作曲']||'',
  album:values['所属专辑']||'',libraries:values['所属曲库']||'',tags:tags});
})()
```

### 3. 回写 Eagle（必须用 Python，禁止 shell curl）
Shell curl 会破坏中文编码。用 `execute_code` + `urllib.request`：

```python
import json, urllib.request

payload = json.dumps({
    "id": eagle_id,
    "tags": ["曲多多","haifanwu","版权音乐"] + tag_list,
    "annotation": "曲目: ...\n曲多多ID: ...\n表演者: ...\n...",
    "url": f"https://haifanwu.com/#/song-detail/{track_id}"
}, ensure_ascii=False).encode('utf-8')

req = urllib.request.Request("http://localhost:41595/api/item/update",
    data=payload, headers={'Content-Type': 'application/json; charset=utf-8'})
```

### 4. 批量策略

**默认串行，不滥用子 agent：**
当前提取速度 ~2-3 秒/首，16 首串行 < 1 分钟。子 agent 有调度开销、可能失败、共享一个 CDP 会互相干扰。

| 曲目数 | 方案 |
|--------|------|
| ≤20 首 | 主线程串行 `browser_navigate` 循环 |
| 20-50 首 | 2 agent 并行 |
| 50+ 首 | 斟酌使用，优先考虑能否缩小范围 |

**写入始终用 `execute_code` 单脚本**（Python urllib），不用子 agent 拆散。

## 关键陷阱

1. **登录态检测**：页面始终显示"登录 / 注册"，不代表未登录。用 JS 检测 `document.body.innerText.includes('个人会员')`
2. **SPA 路由不可靠**：`$nuxt.$router.push` 多次调用后断连。用直接 URL 导航：`https://haifanwu.com/song-detail/ID`
3. **中文乱码**：shell curl 传中文必乱码。写 Eagle 必须用 Python `urllib.request`
4. **Eagle 文件夹树过大**：`/api/folder/list` 响应可能超 100k 字符。用管道 `curl | python3 -c` 流式过滤
5. **标签重复**：写入前检查已有 tags，避免重复追加
