# WebBridge + Studio 调试工作流

> 用户需要看到设计过程，不能用无头浏览器替代。全部在用户真实 Chrome 中操作。

## 启动

```python
# 1. 起守护进程
subprocess.run([r"C:\Users\HMSJ\.kimi-webbridge\bin\kimi-webbridge.exe", "start"])

# 2. 起 HTTP 服务器（WebBridge 不支持 file:// 需扩展权限）
# terminal: cd .../ograf && python3 -m http.server 8888 &

# 3. 推到用户浏览器（带自动重载）
payload = {"action": "navigate", "args": {
    "url": "http://127.0.0.1:8888/studio.html?autoreload=1",
    "newTab": True, "group_title": "OGraf设计"},
    "session": "ograf-studio"}
```

`?autoreload=1` → 每 2 秒检测 `last-modified`，改源码自动刷新。

## 三种操作模式

### A. evaluate 实时注入（最快，用户即时看到）
```python
{"action":"evaluate","args":{"code":"setBG('light')"}}
{"action":"evaluate","args":{"code":"data.animDur=3;rPreview()"}}
```
**限制**：`<script>` 内 `let`/`const` 顶层变量是模块作用域，evaluate 无法直接访问。
**解法**：append 一个 script 标签暴露关键变量：
```javascript
var expose=document.createElement('script');
expose.textContent='window.DB=DB;window.data=data;window.rAll=rAll;';
document.body.appendChild(expose);
```

### B. 改源码自动重载（2 秒生效）
`patch`/`write_file` 改 `studio.html` → autoreload 自动刷新。适合加新功能、改结构、修语法错误。

### C. file:// 直开（备选）
需 Chrome 扩展设置中开启"允许访问文件网址"。HTTP 服务器方式更可靠。

## 截图验证

```python
{"action":"screenshot","args":{"format":"jpeg","quality":60}}
# 返回 path → vision_analyze 读图
```
截图存 `%TEMP%\kimi-webbridge-screenshots\`。用于留档和 Obsidian 参考文档。

## 排查 JS 语法错误

页面模板数为 0 说明 JS 静默失败：

```python
# 1. 验证源码括号平衡
python3 -c "
import re
c=open('studio.html').read()
m=re.search(r'<script>(.*)</script>',c,re.DOTALL)
s=m.group(1)
bc=s.count('{')-s.count('}')
pc=s.count('(')-s.count(')')
print(f'brace diff={bc}, paren diff={pc}')
"
# 2. Node 语法检查
python3 -c "
import re,subprocess,tempfile,os
c=open('studio.html').read()
m=re.search(r'<script>(.*?)</script>',c,re.DOTALL)
js='function _test(){\n'+m.group(1)+'\n}'
tf=tempfile.NamedTemporaryFile(mode='w',suffix='.js',delete=False)
tf.write(js);tf.close()
r=subprocess.run(['node','--check',tf.name],capture_output=True,text=True)
print(r.stderr[:500] if r.returncode else 'OK')
os.unlink(tf.name)
"

# 3. 清缓存重试
{"action":"evaluate","args":{"code":"localStorage.removeItem('ograf_studio_v3');location.reload()"}}
```

## 注意

- 不要用无头浏览器截图做视觉验证——用户看不到过程。
- snapshot `@e` ref 每次刷新会变，优先用 `evaluate` + CSS selector。
- `?fresh=` 等额外 query param 会破坏 autoreload 轮询——只用 `?autoreload=1`。
- 截图超时 → 降低 jpeg quality，或用 snapshot 替代。
- 用户关闭标签后 session 失效，需重新 navigate。
